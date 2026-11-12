import os
# Motor de «cámara continua»: curvas, capas 2.5D, texto y objetos. Sale de camara-continua/cc.py.
import math
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
ZOOM = 1500.0
OBT = 0.5


# ---------- curvas (cubic-bezier, lo mismo que tocar la influencia en el editor de gráficos)
def cb(x1, y1, x2, y2):
    def f(u):
        u = max(0., min(1., u))
        a, b = 0., 1.
        for _ in range(18):
            m = (a + b) / 2
            x = 3 * (1 - m) ** 2 * m * x1 + 3 * (1 - m) * m ** 2 * x2 + m ** 3
            if x < u: a = m
            else: b = m
        m = (a + b) / 2
        return 3 * (1 - m) ** 2 * m * y1 + 3 * (1 - m) * m ** 2 * y2 + m ** 3
    return f


CAE = cb(.05, .85, .18, 1)     # arranca muy rápido y cae despacio
LATIGO = cb(.72, 0, .16, 1)    # latigazo con pico marcado y cola larga
EMPUJE = cb(.62, 0, .2, 1)
SUAVE = cb(.25, .1, .25, 1)


def pico(e):
    """Fracción de la curva donde la velocidad es máxima: ahí va el corte."""
    xs = np.linspace(0, 1, 400)
    ys = np.array([e(x) for x in xs])
    return float(xs[int(np.argmax(np.gradient(ys)))])


def cl(x): return max(0., min(1., x))


# ---------- capas
def mipmaps(img, res):
    out = [(res, img)]
    while out[-1][0] > .3 and min(out[-1][1].size) > 8:
        r, i = out[-1]
        out.append((r / 2, i.resize((max(1, i.width // 2), max(1, i.height // 2)), Image.BOX)))
    return out


class Capa:
    def __init__(s, img, pos, ancla=None, res=2., ini=-1, fin=1e9, rot=None, esc=None, op=None, dxy=None,
                 clip=None, clipinv=None, liso=False):
        s.mips = mipmaps(img, res)
        s.w, s.h = img.width / res, img.height / res
        s.a = ancla if ancla else (s.w / 2, s.h / 2)
        s.pos, s.ini, s.fin, s.rot, s.esc, s.op, s.dxy = pos, ini, fin, rot, esc, op, dxy
        s.clip, s.clipinv = clip, clipinv
        s.filtro = Image.BILINEAR if liso else Image.BICUBIC

    def dibuja(s, lienzo, t, c):
        if not (s.ini <= t < s.fin): return
        op = s.op(t) if s.op else 1.
        if op <= .003: return
        x, y, z = s.pos(t) if callable(s.pos) else s.pos
        if s.dxy:
            dx, dy = s.dxy(t); x += dx; y += dy
        prof = z - c[2] + ZOOM
        if prof < 40: return
        k = ZOOM / prof
        sx = (W / 2 + (x - c[0]) * k); sy = (H / 2 + (y - c[1]) * k)
        ee = (s.esc(t) if callable(s.esc) else s.esc) if s.esc else 1.
        ex, ey = ee if isinstance(ee, tuple) else (ee, ee)
        kx, ky = k * ex, k * ey
        if kx < .002 or ky < .002: return
        res, img = s.mips[0]
        for r, i in s.mips:
            if r >= max(kx, ky): res, img = r, i
        ang = math.radians(s.rot(t)) if s.rot else 0.
        ca, sa = math.cos(ang), math.sin(ang)
        # esquinas en pantalla
        cs = []
        for px, py in ((0, 0), (s.w, 0), (s.w, s.h), (0, s.h)):
            qx, qy = (px - s.a[0]) * kx, (py - s.a[1]) * ky
            cs.append((sx + qx * ca - qy * sa, sy + qx * sa + qy * ca))
        x0 = max(0, int(math.floor(min(p[0] for p in cs))) - 1); x1 = min(W, int(math.ceil(max(p[0] for p in cs))) + 1)
        y0 = max(0, int(math.floor(min(p[1] for p in cs))) - 1); y1 = min(H, int(math.ceil(max(p[1] for p in cs))) + 1)
        if x1 <= x0 or y1 <= y0: return
        # de pantalla a textura
        a = ca / kx * res; b = sa / kx * res
        d = -sa / ky * res; e = ca / ky * res
        ox = x0 + .5 - sx; oy = y0 + .5 - sy
        cc = (ox * a + oy * b) + s.a[0] * res - .5 * 0
        ff = (ox * d + oy * e) + s.a[1] * res - .5 * 0
        tmp = img.transform((x1 - x0, y1 - y0), Image.AFFINE, (a, b, cc, d, e, ff), s.filtro)
        if op < .997 or s.clip or s.clipinv:
            al = tmp.getchannel('A')
            if op < .997: al = al.point(lambda v, o=op: int(v * o))
            for fn, inv in ((s.clip, False), (s.clipinv, True)):
                if not fn: continue
                r = fn(t)
                if r is None: continue
                rx0 = W / 2 + (r[0] - c[0]) * k - x0; ry0 = H / 2 + (r[1] - c[1]) * k - y0
                rx1 = W / 2 + (r[2] - c[0]) * k - x0; ry1 = H / 2 + (r[3] - c[1]) * k - y0
                dr = ImageDraw.Draw(al)
                if inv:
                    if rx1 > rx0 and ry1 > ry0: dr.rectangle((rx0, ry0, rx1, ry1), fill=0)
                else:
                    mk = Image.new('L', al.size, 0)
                    if rx1 > rx0 and ry1 > ry0: ImageDraw.Draw(mk).rectangle((rx0, ry0, rx1, ry1), fill=255)
                    al = ImageChops.multiply(al, mk)
            tmp.putalpha(al)
        lienzo.alpha_composite(tmp, dest=(x0, y0))


# ---------- texto Helvetica con letras muy juntas
_F = {}
def F(tam, peso=1):
    k = (tam, peso)
    if k not in _F:
        # Helvetica si el ordenador la tiene; si no, Inter (libre, va en editor/assets/fuentes)
        try: _F[k] = ImageFont.truetype('HelveticaNeue.ttc', tam, index=peso)
        except OSError:
            f = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'assets', 'fuentes', 'Inter[opsz,wght].ttf'), tam)
            try: f.set_variation_by_name('Bold' if peso else 'Regular')
            except Exception: pass
            _F[k] = f
    return _F[k]


def ancho(txt, tam, peso=1, track=-.045):
    return F(tam, peso).getlength(txt) + track * tam * max(0, len(txt) - 1)


def sprite_txt(txt, tam, peso=1, color=(255, 255, 255), track=-.045, res=2):
    f = F(tam * res, peso)
    w = int(ancho(txt, tam, peso, track) * res) + 8 * res
    asc, desc = f.getmetrics()
    h = asc + desc + 4 * res
    al = Image.new('L', (w, h), 0)
    dr = ImageDraw.Draw(al)
    for i, ch in enumerate(txt):
        x = f.getlength(txt[:i + 1]) - f.getlength(ch) + track * tam * res * i
        dr.text((x + 4 * res, 2 * res), ch, font=f, fill=255)
    im = Image.new('RGBA', (w, h), color + (0,))
    im.putalpha(al)
    return im


def bloque(lineas, origen, cx=0, cy=0, interlin=1.0, ini=-1, fin=1e9, dy=46, durw=.22, clip=None, clipinv=None, fijo=False):
    """Líneas de palabras centradas; cada palabra entra subiendo y con fundido al decirse
    (el selector de rango del tutorial: por palabras, rampa, suavizado alto 30 / bajo 70)."""
    capas = []
    alto = sum(l['tam'] * interlin for l in lineas)
    y = cy - alto / 2
    S = cb(.3, 0, .15, 1)
    for l in lineas:
        tam, peso, col = l['tam'], l.get('peso', 1), l.get('color', (255, 255, 255))
        pal = l['pal']
        esp = tam * .235
        tot = sum(ancho(p[0], tam, peso) for p in pal) + esp * (len(pal) - 1)
        x = cx - tot / 2
        for txt, tp in pal:
            sp = sprite_txt(txt, tam, peso, col)
            px, py, pz = origen
            pos = (px + x - 4, py + y - tam * .12, pz)
            kw = {}
            if not fijo:
                kw['op'] = lambda t, a=tp: S(cl((t - a) / durw))
                kw['dxy'] = lambda t, a=tp, d=dy: (0, d * (1 - S(cl((t - a) / (durw * 1.5)))))
            capas.append(Capa(sp, pos, ancla=(0, 0), ini=ini, fin=fin, clip=clip, clipinv=clipinv, **kw))
            x += ancho(txt, tam, peso) + esp
        y += tam * interlin
    return capas


# ---------- objetos
def estrella(n=5, ro=600, ri=130, rnd_o=1., rnd_i=2., color=(0, 0, 0), des=4., tam=1500):
    """La polystar del tutorial: radio interior 130, exterior 600, redondez interior 200 y exterior 100."""
    ss = 2
    im = Image.new('L', (tam * ss, tam * ss), 0)
    dr = ImageDraw.Draw(im)
    pts = []
    N = 2 * n
    seg = 2 * math.pi / N
    v = []
    for i in range(N):
        r = ro if i % 2 == 0 else ri
        a = -math.pi / 2 + i * seg
        rn = rnd_o if i % 2 == 0 else rnd_i
        tl = rn * r * seg * .5
        px, py = r * math.cos(a), r * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        v.append((px, py, tx * tl, ty * tl))
    for i in range(N):
        p0 = v[i]; p1 = v[(i + 1) % N]
        c0 = (p0[0] + p0[2], p0[1] + p0[3]); c1 = (p1[0] - p1[2], p1[1] - p1[3])
        for u in np.linspace(0, 1, 40, endpoint=False):
            x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * c0[0] + 3 * (1 - u) * u ** 2 * c1[0] + u ** 3 * p1[0]
            y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * c0[1] + 3 * (1 - u) * u ** 2 * c1[1] + u ** 3 * p1[1]
            pts.append(((x + tam / 2) * ss, (y + tam / 2) * ss))
    dr.polygon(pts, fill=255)
    im = im.resize((tam, tam), Image.LANCZOS)
    if des: im = im.filter(ImageFilter.GaussianBlur(des))
    out = Image.new('RGBA', im.size, color + (0,))
    out.putalpha(im)
    return out


def capsula(L, R, base, res=1.):
    """Pastilla brillante sombreada con normales reales."""
    w, h = int((L + 2 * R + 8) * res), int((2 * R + 8) * res)
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    x = xs / res - (L / 2 + R + 4); y = ys / res - (R + 4)
    qx = np.clip(x, -L / 2, L / 2)
    dx, dy = x - qx, y
    d = np.hypot(dx, dy)
    al = np.clip((R - d) * res + .5, 0, 1)
    dn = np.minimum(d / R, .999)
    nx, ny = dx / R, dy / R
    nx, ny = np.clip(nx, -1, 1), np.clip(ny, -1, 1)
    nz = np.sqrt(np.maximum(1 - nx ** 2 - ny ** 2, 0))
    lx, ly, lz = -.32, -.62, .72
    dif = np.clip(nx * lx + ny * ly + nz * lz, 0, 1)
    hx, hy, hz = lx, ly, lz + 1
    n_ = math.sqrt(hx * hx + hy * hy + hz * hz)
    spec = np.clip((nx * hx + ny * hy + nz * hz) / n_, 0, 1)
    b = np.array(base, np.float32) / 255
    col = np.stack([b[i] * (.28 + .86 * dif) for i in range(3)], -1)
    # luz de rebote abajo y brillo
    reb = np.clip(ny, 0, 1) ** 3 * (1 - nz) * .55
    for i in range(3): col[..., i] += (b[i] * .8 + .12) * reb
    col += (spec ** 60)[..., None] * .95 + (spec ** 12)[..., None] * .16
    # banda de reflejo larga, como de softbox
    banda = np.exp(-((y / R + .55) / .1) ** 2) * (np.abs(x) < (L / 2 + R * .3)) * .16
    col += banda[..., None]
    rgba = np.dstack([np.clip(col, 0, 1) * 255, al * 255]).astype(np.uint8)
    return Image.fromarray(rgba, 'RGBA')


def _sombreado(h, res, luz=(-.42, -.62, .66), fuerza=1.):
    gy, gx = np.gradient(h)
    nx, ny = -gx * fuerza * res, -gy * fuerza * res
    nz = np.ones_like(nx)
    n = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    nx, ny, nz = nx / n, ny / n, nz / n
    dif = np.clip(nx * luz[0] + ny * luz[1] + nz * luz[2], 0, 1)
    hx, hy, hz = luz[0], luz[1], luz[2] + 1
    k = math.sqrt(hx * hx + hy * hy + hz * hz)
    sp = np.clip((nx * hx + ny * hy + nz * hz) / k, 0, 1)
    return nx, ny, nz, dif, sp


def aspirina(R=240, res=1.5):
    t = int((2 * R + 8) * res)
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    x = xs / res - (R + 4); y = ys / res - (R + 4)
    r = np.hypot(x, y)
    al = np.clip((R - r) * res + .5, 0, 1)
    u = np.clip(r / R, 0, 1)
    h = np.where(u < .8, 1., np.sqrt(np.maximum(1 - ((u - .8) / .2) ** 2, 0))) * 34
    h += np.where(u < .8, (1 - (u / .8) ** 2) * 10, 0)
    h -= 13 * np.exp(-(x / 7) ** 2) * (u < .9)
    nx, ny, nz, dif, sp = _sombreado(h, 1 / res, fuerza=1.)
    v = .46 + .6 * dif + .1 * sp ** 40
    grano = np.random.default_rng(3).normal(0, .006, v.shape)
    v = np.clip(v + grano, 0, 1)
    col = np.dstack([v * .99, v * .985, v * .97])
    return Image.fromarray(np.dstack([col * 255, al * 255]).astype(np.uint8), 'RGBA')


def moneda(R=330, res=1.5):
    """Moneda en relieve a partir de un mapa de alturas: canto estriado, aro y € en el centro."""
    t = int((2 * R + 8) * res)
    c = t / 2
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    x = xs - c; y = ys - c
    r = np.hypot(x, y) / res
    th = np.arctan2(y, x)
    al = np.clip((R - r) * res + .5, 0, 1)
    u = r / R
    # capas de altura
    h = np.zeros_like(u)
    h += np.where(u > .86, 30., 0.)                         # aro exterior
    h += np.where(u > .86, 4 * np.sin(th * 150), 0.)        # estrías
    h += np.where((u > .70) & (u < .73), 7., 0.)            # filete interior
    # € y texto del aro en relieve
    capa = Image.new('L', (t, t), 0)
    dr = ImageDraw.Draw(capa)
    f = F(int(R * .98 * res), 1)
    b = dr.textbbox((0, 0), '€', font=f)
    dr.text((c - (b[0] + b[2]) / 2, c - (b[1] + b[3]) / 2), '€', font=f, fill=255)
    lema = '  SIN ATAJOS  ·  SIN ATAJOS  ·  SIN ATAJOS  ·'
    ft = F(int(R * .092 * res), 1)
    ra = R * .785 * res
    tot = sum(ft.getlength(ch) * 1.14 for ch in lema)
    ang0 = -math.pi / 2
    acum = 0.
    for ch in lema:
        adv = ft.getlength(ch) * 1.14
        a = ang0 + (acum + adv / 2) / tot * 2 * math.pi
        acum += adv
        if ch == ' ': continue
        tc = Image.new('L', (int(R * .3 * res), int(R * .3 * res)), 0)
        ImageDraw.Draw(tc).text((tc.width / 2, tc.height / 2), ch, font=ft, fill=255, anchor='mm')
        tc = tc.rotate(-math.degrees(a + math.pi / 2), Image.BICUBIC)
        capa.paste(255, (int(c + ra * math.cos(a) - tc.width / 2), int(c + ra * math.sin(a) - tc.height / 2)), tc)
    rel = np.asarray(capa.filter(ImageFilter.GaussianBlur(2.2 * res)), np.float32) / 255
    h += rel * 15
    for eje in (0, 1):                                      # suavizado para que el relieve no sea un escalón
        h = (np.roll(h, 1, eje) + h + np.roll(h, -1, eje)) / 3
        h = (np.roll(h, 2, eje) + h + np.roll(h, -2, eje)) / 3
    h += np.where(u > .97, -(u - .97) / .03 * 18, 0)
    nx, ny, nz, dif, sp = _sombreado(h, 1, fuerza=.55)
    # plata: mapa de reflejos sencillo + reflejo anisótropo que da sensación de metal
    aniso = .5 + .5 * np.cos(th * 2 + 1.1)
    v = .30 + .50 * dif + .26 * aniso * (u < .86) + .75 * sp ** 26
    v = np.clip(v, 0, 1)
    col = np.dstack([v * .985, v, v * 1.0])
    return Image.fromarray(np.dstack([np.clip(col, 0, 1) * 255, al * 255]).astype(np.uint8), 'RGBA')


def rejilla(tam=1500, paso=66):
    ss = 2
    im = Image.new('L', (tam * ss, tam * ss), 0)
    dr = ImageDraw.Draw(im)
    for i in range(0, tam, paso):
        for j in range(0, tam, paso):
            x, y = i * ss, j * ss
            dr.line((x - 7, y, x + 7, y), fill=255, width=2)
            dr.line((x, y - 7, x, y + 7), fill=255, width=2)
    im = im.resize((tam, tam), Image.LANCZOS)
    ys, xs = np.mgrid[0:tam, 0:tam].astype(np.float32)
    r = np.hypot(xs - tam / 2, ys - tam / 2) / (tam / 2)
    fade = np.clip(1 - (r - .25) / .55, 0, 1) ** 1.4
    a = np.asarray(im, np.float32) * fade * .55
    out = Image.new('RGBA', (tam, tam), (40, 40, 40, 0))
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def caja(w, h, grosor=5, color=(0, 0, 0), trazos=True, res=2):
    im = Image.new('RGBA', (int((w + grosor) * res), int((h + grosor) * res)), color + (0,))
    dr = ImageDraw.Draw(im)
    g = grosor * res
    x0, y0, x1, y1 = g / 2, g / 2, im.width - g / 2, im.height - g / 2
    if not trazos:
        dr.rectangle((x0, y0, x1, y1), outline=color + (255,), width=g)
        return im
    pt, hu = 24 * res, 15 * res
    def linea(a, b):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int((L + hu) / (pt + hu)))
        pasoL = (L - pt) / max(1, n - 1) if n > 1 else 0
        for i in range(n):
            s0 = i * pasoL; s1 = s0 + pt
            dr.line((a[0] + (b[0] - a[0]) * s0 / L, a[1] + (b[1] - a[1]) * s0 / L,
                     a[0] + (b[0] - a[0]) * s1 / L, a[1] + (b[1] - a[1]) * s1 / L), fill=color + (255,), width=g)
    linea((x0, y0), (x1, y0)); linea((x1, y0), (x1, y1)); linea((x1, y1), (x0, y1)); linea((x0, y1), (x0, y0))
    return im


def cursor(alto=86, res=2):
    pts = [(0, 0), (0, 72), (19, 54), (33, 86), (47, 80), (33, 49), (58, 47)]
    k = alto / 86 * res
    im = Image.new('RGBA', (int(70 * k) + 12, int(96 * k) + 12), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    P_ = [(x * k + 6, y * k + 6) for x, y in pts]
    dr.polygon(P_, fill=(8, 8, 8, 255), outline=(255, 255, 255, 255))
    dr.line(P_ + [P_[0]], fill=(255, 255, 255, 255), width=int(2.4 * res), joint='curve')
    return im


def trazo(res=1):
    """Trazo grueso afilado en las puntas (taper 100), como el del tutorial."""
    ss = 2
    im = Image.new('L', (1800 * ss, 1100 * ss), 0)
    dr = ImageDraw.Draw(im)
    p0, p1, p2, p3 = (-80, 900), (480, -150), (1250, 1200), (1880, 180)
    prev = None
    for u in np.linspace(0, 1, 500):
        x = (1 - u) ** 3 * p0[0] + 3 * (1 - u) ** 2 * u * p1[0] + 3 * (1 - u) * u ** 2 * p2[0] + u ** 3 * p3[0]
        y = (1 - u) ** 3 * p0[1] + 3 * (1 - u) ** 2 * u * p1[1] + 3 * (1 - u) * u ** 2 * p2[1] + u ** 3 * p3[1]
        r = 88 * math.sin(math.pi * u) ** .75 + 1
        dr.ellipse(((x - r) * ss, (y - r) * ss, (x + r) * ss, (y + r) * ss), fill=255)
    im = im.resize((1800, 1100), Image.LANCZOS)
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    out.putalpha(im)
    return out


_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)
_DIST = np.hypot(_xx - W / 2 + .5, _yy - H / 2 + .5)
R_MAX = float(_DIST.max()) + 6


# ---------- aberración cromática solo hacia los bordes (máscara en resta con calado grande)
_rr = np.hypot((_xx - W / 2) / (W * .52), (_yy - H / 2) / (H * .47))
_MASC = np.clip((_rr - .35) / .55, 0, 1)[..., None].astype(np.float32)


def aberracion(a):
    im = Image.fromarray(a)
    R, G, B = im.split()
    k = .0052
    def zoom(c, z):
        return c.transform((W, H), Image.AFFINE, (1 / z, 0, W / 2 * (1 - 1 / z), 0, 1 / z, H / 2 * (1 - 1 / z)), Image.BILINEAR)
    bz = np.array(zoom(B, 1 - k))
    mx, my = int(W / 2 * k) + 2, int(H / 2 * k) + 2         # el canal encogido no llega al borde: sin esto sale una línea amarilla
    bz[:my] = bz[my]; bz[-my:] = bz[-my - 1]; bz[:, :mx] = bz[:, [mx]]; bz[:, -mx:] = bz[:, [-mx - 1]]
    b = np.dstack([np.asarray(zoom(R, 1 + k)), np.asarray(G), bz]).astype(np.float32)
    return (a * (1 - _MASC) + b * _MASC).astype(np.uint8)


