# EJEMPLO del estilo zambullida-epica (anuncio de 54 s para negocios de una región), a 60 fps. Es la plantilla:
# cambia textos, fotos, región y escenas por las del vídeo nuevo; lo que se reutiliza es el lenguaje, no las escenas.
# Necesita: voz/voz.wav + voz/tiempos.json (tiempos.py), foto_persona.jpg y fotos/sitio1.jpg, fotos/sitio2.jpg.
# Con todo lo aprendido:
# formas con rebote (Apple), reloj y carretera en perspectiva y páginas que se pasan (Time is money), cuadro en sala de madera
# (Earn Edits), esferas líquidas y foto partida (Alborná), caja con cursor y latigazos en el pico (cámara continua),
# cuadrícula y objetos (Simply Put), tienda que se llena (venta-tienda), luz y destellos (historia-escénica).
#
#   python3 vf.py hoja 1.0,2.5 salida.jpg [columnas]
#   python3 vf.py render carpeta
import json, math, os, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from mc import *
from mc import _DIST
from obj import *
from estilos import pared, marco, txt_metal, letras, Liquido, red_luz, mitad
from piezas import *
from piezas import _web_generica, _chat, _pantalla
from kit import *
REGION, PUEBLO = 'tu región', 'tu pueblo'  # textos del ejemplo: cámbialos (el mapa se dibuja con el polígono de geo)

FPS = 60
GRIS = (236, 236, 239)
VERDEW = (37, 190, 104)
BLA = (255, 255, 255)
ROJ2 = (255, 66, 58)

D = json.load(open('voz/tiempos.json'))
DUR, P = D['dur'], D['frases']
INI = [f['ini'] for f in P]
FIN = [f['fin'] for f in P]
def T(i, j): return P[i]['pal'][j]['ini']


def lin(tam, pal, peso=1, color=TINTA):
    tot = sum(ancho(p[0], tam, peso) for p in pal) + tam * .235 * (len(pal) - 1)
    if tot > 868: print('ANCHO', [p[0] for p in pal], int(tot), file=sys.stderr)
    return dict(tam=tam, peso=peso, color=color, pal=pal)


# ---------- cámara
MOV = []
def mov(t0, t1, d, e): MOV.append((t0, t1, d, e))
_p = pico(LATIGO)
def latigo(tc, dur=1.0, d=(0, 2000, 0)):
    t0 = tc - _p * dur
    mov(t0, t0 + dur, d, LATIGO)
    return t0, t0 + dur
def lento(a, b, dz=120): mov(a, b, (0, 0, dz * 2.4), SUAVE)

mov(0, 1.2, (0, 0, 600), CAE)
lento(1.2, INI[1] - .1, 80)
mov(INI[1] - .1, INI[1] + .8, (0, 0, 200), EMPUJE)
TC = {}
def corte(n, i, **k):
    TC[n] = INI[i] - .04
    return latigo(TC[n], **k)
PORT = []
def zambulle(n, i, dx=0, dy=0, dz=1150, dur=.42):
    # La cámara se mete dentro del objeto hasta que llena el plano, y la escena nueva se abre desde dentro.
    tc = TC[n] = INI[i] - .04
    mov(tc - dur, tc, (dx, dy, dz), cb(.7, 0, .95, .55))
    mov(tc, tc + .0005, (0, 0, -dz - 520), lambda u: u)
    mov(tc, tc + .62, (0, 0, 520), CAE)
    PORT.append(tc)
    return tc - dur, tc + .62
LZ = zambulle('z', 1)
LA = zambulle('a', 2, 0, 230); lento(LA[1] - .3, INI[4] - .35, 110)
LB = zambulle('b', 4, 0, 120); lento(LB[1] - .3, INI[5] - .35, 120)
LC = zambulle('c', 5, 0, 200); mov(INI[6] - .2, INI[6] + .65, (900, 0, -160), EMPUJE)
LD = corte('d', 7); lento(LD[1] - .3, INI[9] - .35, 170)     # gira al salir
LE = corte('e', 9); lento(LE[1] - .3, INI[10] - .35, 120)
LF = corte('f', 10); mov(LF[1] - .35, INI[11] - .3, (0, -520, 620), SUAVE)   # por la carretera
LG = corte('g', 11); lento(LG[1] - .3, INI[13] - .3, 200)
LH = zambulle('h', 13, 0, 190, dur=.24); lento(LH[1] - .3, INI[14] - .3, 160)
LI = corte('i', 14); lento(LI[1] - .3, INI[15] - .3, 260)
LJ = zambulle('j', 15, 0, -130); lento(LJ[1] - .3, INI[16] - .3, 90)     # vuelve la música
LK = corte('k', 16); lento(LK[1] - .3, INI[18] - .3, 90)
LL = zambulle('l', 18, 0, 130); mov(LL[1] - .3, DUR, (0, 0, -90), lambda u: u)


def cam0(t):
    c = [0., 0., -600.]
    for t0, t1, d, e in MOV:
        k = e(cl((t - t0) / (t1 - t0)))
        for i in range(3): c[i] += d[i] * k
    return c


BEATS = []
def cam(t):
    # Encima de la trayectoria: pulso de cámara en mano y un golpe en cada palabra fuerte. Todo vuelve a cero.
    c = cam0(t)
    c[0] += 15 * math.sin(1.27 * t) + 7 * math.sin(2.9 * t + 1)
    c[1] += 13 * math.sin(1.03 * t + 2) + 6 * math.sin(3.3 * t)
    c[2] += 26 * math.sin(.8 * t)
    for tb, a in BEATS:
        u = t - tb
        if 0 < u < 1.1:
            c[2] += 120 * a * math.exp(-4.5 * u) * math.sin(11 * u)
            c[0] += 13 * a * math.exp(-8 * u) * math.sin(61 * u)
            c[1] += 16 * a * math.exp(-8 * u) * math.sin(47 * u + 1)
    return c


def rest(t): return tuple(cam0(t))


def _seg(t, L, tc, ang):
    u = (t - L[0]) / (L[1] - L[0])
    if u <= 0 or u >= 1: return 0.
    k = LATIGO(u)
    return ang * k if t < tc else ang * (k - 1)


def giro(t):
    g = _seg(t, LE, TC['e'], 90) + _seg(t, LG, TC['g'], -90) + _seg(t, LK, TC['k'], 90)
    g += .8 * math.sin(t * 1.15)      # el giro leve que cose todo (Apple)
    for tb, a in BEATS:
        u = t - tb
        if 0 < u < .7: g += 1.3 * a * math.exp(-6 * u) * math.sin(17 * u)
    return g


def desenfoque(t):
    r = 0.
    for tc, a, m in ((INI[3] - .03, .1, 10), (INI[8] - .04, .1, 12), (INI[12] - .04, .1, 10), (INI[17] - .04, .1, 9)):
        r = max(r, m * max(0, 1 - abs(t - tc) / a))
    return r


ENT = cb(.2, .9, .3, 1)
SALE = cb(.6, 0, .15, 1)
def pop(ta, dur=.24, e=1.):
    return lambda t: max(.001, ENT(cl((t - ta) / dur))) * e
def muelle(u):
    """El rebote de la expresión de Apple: pasa de largo y vuelve."""
    u = max(0., u)
    return 1 - math.exp(-6 * u) * math.cos(9 * u)


# ---------- formas que se transforman (Apple)
def pega(lz, im, x0, y0):
    # Pega recortando lo que cae fuera; si queda entero fuera de cuadro, no hace nada.
    if x0 >= W or y0 >= H or -x0 >= im.width or -y0 >= im.height: return
    lz.alpha_composite(im, (max(0, x0), max(0, y0)), (max(0, -x0), max(0, -y0)))


class Pildora:
    """Forma redondeada cuyo ancho y alto siguen un muelle: de punto a círculo y de círculo a píldora."""
    def __init__(s, pos, ancho_f, alto_f, col, ini=-1, fin=1e9, sombra=True):
        s.pos, s.a, s.h, s.col, s.ini, s.fin, s.sombra = pos, ancho_f, alto_f, col, ini, fin, sombra

    def dibuja(s, lz, t, c):
        if not (s.ini <= t < s.fin): return
        x, y, z = s.pos(t) if callable(s.pos) else s.pos
        prof = z - c[2] + ZOOM
        if prof < 40: return
        k = ZOOM / prof
        w, h = max(0, s.a(t) * k), max(0, s.h(t) * k)
        if w < 2 or h < 2: return
        sx, sy = W / 2 + (x - c[0]) * k, H / 2 + (y - c[1]) * k
        pad = int(46 * k)
        iw, ih = int(w) + 2 * pad, int(h) + 2 * pad
        m = Image.new('L', (iw * 2, ih * 2), 0)
        ImageDraw.Draw(m).rounded_rectangle((pad * 2, pad * 2, (pad + w) * 2, (pad + h) * 2), min(w, h), fill=255)
        m = m.resize((iw, ih), Image.BOX)
        x0, y0 = int(sx - w / 2) - pad, int(sy - h / 2) - pad
        if s.sombra and k < 1.8:
            so = Image.new('RGBA', (iw, ih), (0, 0, 0, 0))
            so.putalpha(m.point(lambda v: int(v * .22)).filter(ImageFilter.GaussianBlur(14 * k)))
            pega(lz, so, x0, y0 + int(10 * k))
        im = Image.new('RGBA', (iw, ih), s.col + (0,))
        im.putalpha(m)
        pega(lz, im, x0, y0)


def pildora_txt(S_, pos, ta, w_fin, h, col, txt, tam, colt=BLA, tb=None, fin=1e9, ini=None, peso=1):
    """Punto → círculo → píldora, y el texto cae dentro cuando se abre."""
    ini = ta - .05 if ini is None else ini
    tb = ta + .22 if tb is None else tb
    px, py, pz = pos
    def an(t):
        c0 = h * muelle((t - ta) / .5)
        hunde = 1 - .12 * max(0, 1 - abs(t - tb + .05) / .06)   # el botón se hunde justo antes de abrirse
        return c0 * hunde if t < tb else h + (w_fin - h) * muelle((t - tb) / .5)
    S_.append(Pildora(pos, an, lambda t: h * muelle((t - ta) / .5), col, ini=ini, fin=fin))
    sp = sprite_txt(txt, tam, peso, colt)
    rec = lambda t: (px - an(t) / 2, py - h, px + an(t) / 2, py + h)
    Se = cb(.3, 0, .15, 1)
    S_.append(Capa(sp, (px, py - tam * .04, pz), res=2, ini=tb, fin=fin, clip=rec, op=lambda t: Se(cl((t - tb - .04) / .12)),
                   dxy=lambda t: (0, 22 * (1 - Se(cl((t - tb - .04) / .2))))))


class FotoMorf:
    """La foto pasa de círculo a rectángulo con muelle, recortando la imagen sin deformarla."""
    def __init__(s, im, pos, ta, tb, r0, w1, h1, fin=1e9):
        s.im = im.convert('RGB'); s.pos, s.ta, s.tb, s.r0, s.w1, s.h1, s.fin = pos, ta, tb, r0, w1, h1, fin

    def dibuja(s, lz, t, c):
        if not (s.ta - .02 <= t < s.fin): return
        x, y, z = s.pos
        k = ZOOM / max(40, z - c[2] + ZOOM)
        e0 = muelle((t - s.ta) / .5)
        u = muelle((t - s.tb) / .55) if t > s.tb else 0
        d0 = 2 * s.r0 * e0
        w = (d0 + (s.w1 - d0) * u) * k
        h = (d0 + (s.h1 - d0) * u) * k
        if w < 2: return
        rr = (min(w, h) / 2) * (1 - cl(u) * .9)
        iw, ih = int(w), int(h)
        ia = s.im.width / s.im.height
        esc_ = max(s.w1 * k / s.im.width, s.h1 * k / s.im.height) * 1.02
        fw, fh = int(s.im.width * esc_), int(s.im.height * esc_)
        g = s.im.resize((fw, fh), Image.BILINEAR)
        # centrado en la persona, no en el centro de la foto
        cx, cy = fw * .68, fh * .42
        cx = min(max(cx, iw / 2), fw - iw / 2); cy = min(max(cy, ih / 2), fh - ih / 2)
        rec = g.crop((int(cx - iw / 2), int(cy - ih / 2), int(cx - iw / 2) + iw, int(cy - ih / 2) + ih)).convert('RGBA')
        m = Image.new('L', (iw * 2, ih * 2), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, iw * 2 - 1, ih * 2 - 1), rr * 2, fill=255)
        rec.putalpha(m.resize((iw, ih), Image.BOX))
        sx, sy = W / 2 + (x - c[0]) * k, H / 2 + (y - c[1]) * k
        x0, y0 = int(sx - iw / 2), int(sy - ih / 2)
        pega(lz, rec, x0, y0)


class HojaCurl:
    """Nota cuya esquina se levanta y se pasa como una página (el CC Page Turn del tutorial)."""
    def __init__(s, hoja, reverso, pos, L, ta, dur=.55, ini=-1, fin=1e9, vivo=False):
        s.h, s.r, s.pos, s.L, s.ta, s.dur, s.ini, s.fin, s.vivo = hoja, reverso, pos, L, ta, dur, ini, fin, vivo

    def dibuja(s, lz, t, c):
        if not (s.ini <= t < s.fin): return
        if s.vivo:      # el wiggle del tutorial
            p = .1 + .05 * math.sin(t * 5.3) + .03 * math.sin(t * 11.1 + 1)
        else:
            p = cb(.5, 0, .4, 1)(cl((t - s.ta) / s.dur))
        if p >= 1: return
        x, y, z = s.pos
        k = ZOOM / max(40, z - c[2] + ZOOM)
        L = int(s.L * k)
        if L < 4: return
        if L > 1100:      # dentro de la zambullida la nota ya llena el plano: sin pliegue, que a este tamaño tarda minutos
            if s.vivo:
                sx, sy, r_ = W / 2 + (x - c[0]) * k, H / 2 + (y - c[1]) * k, s.h.width / L
                lz.alpha_composite(s.h.transform((W, H), Image.AFFINE, (r_, 0, -(sx - L / 2) * r_, 0, r_, -(sy - L / 2) * r_), Image.BILINEAR))
            return
        h = s.h.resize((L, L), Image.BILINEAR)
        d_ = 2 * L * p * 1.02
        cc = 2 * L - d_
        m = Image.new('L', (L, L), 0)
        di = ImageDraw.Draw(m)
        if d_ <= L:
            rem = [(0, 0), (L, 0), (L, L - d_), (L - d_, L), (0, L)]
            mas = [(L, L - d_), (L, L), (L - d_, L)]
        else:
            rem = [(0, 0), (cc, 0), (0, cc)]
            mas = [(cc, 0), (L, 0), (L, L), (0, L), (0, cc)]
        di.polygon(rem, fill=255)
        out = Image.new('RGBA', (L * 3, L * 3), (0, 0, 0, 0))
        o = L
        im = h.copy(); im.putalpha(ImageChops.multiply(h.getchannel('A'), m))
        out.alpha_composite(im, (o, o))
        ref = []
        for a, b in mas:       # la solapa va curvada: se acorta hacia el pliegue en vez de abrirse entera
            e_ = (a + b - cc) / 2
            ref.append((a - e_ * 1.42 + o, b - e_ * 1.42 + o))
        if d_ > 2:
            q_ = 1 - cl((p - .6) / .32)
            caja = Image.new('L', out.size, 0)      # la solapa nunca se sale de la nota
            ImageDraw.Draw(caja).rectangle((o, o, o + L - 1, o + L - 1), fill=255)
            so = Image.new('L', out.size, 0)
            ImageDraw.Draw(so).polygon([(a + 5, b + 8) for a, b in ref], fill=90)
            sh = Image.new('RGBA', out.size, (0, 0, 0, 0))
            sh.putalpha(ImageChops.multiply(so.filter(ImageFilter.GaussianBlur(9)), caja).point(lambda v: int(v * q_)))
            out.alpha_composite(sh)
            fo = Image.new('L', out.size, 0)
            ImageDraw.Draw(fo).polygon(ref, fill=255)
            cara = Image.new('RGBA', out.size, s.r + (0,)); cara.putalpha(ImageChops.multiply(fo, caja).point(lambda v: int(v * q_)))
            out.alpha_composite(cara)
        sx, sy = W / 2 + (x - c[0]) * k, H / 2 + (y - c[1]) * k
        x0, y0 = int(sx - L * 1.5), int(sy - L * 1.5)
        if x0 >= W or y0 >= H: return
        pega(lz, out, x0, y0)


# ---------- móvil en 3D con pantalla viva
SW, SH = PW - 44, PH_ - 44
_ry_, _rx_ = np.mgrid[0:SH, 0:SW * 3].astype(np.float32)
_BANDA = np.exp(-(((_rx_ + _ry_ * .42 - SW * 1.5) / 74) ** 2)) * .34 + np.exp(-(((_rx_ + _ry_ * .42 - SW * 1.9) / 22) ** 2)) * .22
_BANDA = Image.fromarray((_BANDA * 255).astype(np.uint8))
def _cuerpo_movil():
    S2 = 2
    w, h = PW * S2, PH_ * S2
    g = np.zeros((h, w, 3), np.float32)
    u = np.linspace(0, 1, w)[None, :, None]
    bl_ = np.exp(-((u - .08) / .1) ** 2) + np.exp(-((u - .9) / .08) ** 2) * .8
    g += 62 + bl_ * 165 * np.array((1, 1.02, 1.08))[None, None, :]
    im = Image.fromarray(g.clip(0, 255).astype(np.uint8)).convert('RGBA')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 70 * S2, fill=255)
    im.putalpha(m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((7 * S2, 7 * S2, w - 7 * S2, h - 7 * S2), 64 * S2, fill=(6, 6, 8, 255))
    return im.resize((PW, PH_), Image.BOX), m.resize((PW, PH_), Image.BOX)
_MBODY, _MMAS = _cuerpo_movil()
_SM = Image.new('L', (SW * 2, SH * 2), 0); ImageDraw.Draw(_SM).rounded_rectangle((0, 0, SW * 2 - 1, SH * 2 - 1), 96, fill=255); _SM = _SM.resize((SW, SH), Image.BOX)
_ISLA = Image.new('RGBA', (SW * 2, SH * 2), (0, 0, 0, 0))
_d = ImageDraw.Draw(_ISLA); _d.rounded_rectangle((SW - 136, 28, SW + 136, 92), 32, fill=(4, 4, 6, 255)); _d.ellipse((SW + 74, 44, SW + 106, 76), fill=(22, 26, 46, 255)); _d.ellipse((SW + 84, 52, SW + 94, 62), fill=(70, 90, 150, 255))
_ISLA = _ISLA.resize((SW, SH), Image.BOX)
def _persp(dst, src):
    A, b = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
        b += [u, v]
    return tuple(np.linalg.solve(np.array(A, float), np.array(b, float)))
class Movil3D:
    def __init__(s, pant, pos, esc, yaw, pitch=lambda t: 0, roll=lambda t: 0, ini=-1, fin=1e9, sombra=.42, tinte=None):
        s.pant, s.pos, s.esc, s.yaw, s.pitch, s.roll, s.ini, s.fin, s.sombra, s.tinte = pant, pos, esc, yaw, pitch, roll, ini, fin, sombra, tinte
    def _esq(s, e, cy, sy, cp, sp, cr, sr, dz):
        o = []
        for x, y in ((-PW / 2, -PH_ / 2), (PW / 2, -PH_ / 2), (PW / 2, PH_ / 2), (-PW / 2, PH_ / 2)):
            x2, z2 = x * cy + dz * sy, -x * sy + dz * cy
            y2, z3 = y * cp - z2 * sp, y * sp + z2 * cp
            x3, y3 = x2 * cr - y2 * sr, x2 * sr + y2 * cr
            f = 2300 / (2300 + z3)
            o.append((x3 * e * f, y3 * e * f))
        return o
    def dibuja(s, lz, t, c):
        if not (s.ini <= t < s.fin): return
        x, y, z = s.pos
        k = ZOOM / max(40, z - c[2] + ZOOM)
        e = k * (s.esc(t) if callable(s.esc) else s.esc)
        if e < .02: return
        if e > 2.4: e = 2.4       # dentro de una zambullida no hace falta más
        ya, pi_, ro = (math.radians(q(t)) for q in (s.yaw, s.pitch, s.roll))
        tr = (math.cos(ya), math.sin(ya), math.cos(pi_), math.sin(pi_), math.cos(ro), math.sin(ro))
        fr = s._esq(e, *tr, 0)
        fo = _MBODY.copy()
        sc = s.pant(t).convert('RGBA')
        of = int(SW * (.95 - .22 * ya * 2.5 + .10 * math.sin(t * .8)))
        ba = _BANDA.crop((of, 0, of + SW, SH))
        lu = Image.new('RGBA', (SW, SH), (255, 255, 255, 0)); lu.putalpha(ba)
        sc.alpha_composite(lu); sc.alpha_composite(_ISLA)
        fo.paste(sc, (22, 22), _SM)
        if s.tinte: fo = s.tinte(fo)
        ats = [s._esq(e, *tr, -(q + 1) * 11) for q in range(3)] if abs(ya) + abs(pi_) > .03 else []
        xs = [p[0] for l in [fr] + ats for p in l]; ys = [p[1] for l in [fr] + ats for p in l]
        x0, y0 = int(min(xs)) - 2, int(min(ys)) - 2
        cw, ch = int(max(xs)) - x0 + 3, int(max(ys)) - y0 + 3
        if cw > 2600 or ch > 3200: return
        sx, sy = W / 2 + (x - c[0]) * k, H / 2 + (y - c[1]) * k
        src = [(0, 0), (PW, 0), (PW, PH_), (0, PH_)]
        out = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        for n_, l in enumerate(reversed(ats)):
            co = _persp([(a - x0, b - y0) for a, b in l], src)
            m = _MMAS.transform((cw, ch), Image.PERSPECTIVE, co, Image.BILINEAR)
            g_ = 70 + n_ * 26
            cap = Image.new('RGBA', (cw, ch), (g_, g_, g_ + 6, 0)); cap.putalpha(m); out.alpha_composite(cap)
        co = _persp([(a - x0, b - y0) for a, b in fr], src)
        out.alpha_composite(fo.transform((cw, ch), Image.PERSPECTIVE, co, Image.BICUBIC))
        px, py = int(sx + x0), int(sy + y0)
        if s.sombra and e < 1.6:
            so = out.getchannel('A').resize((max(1, cw // 4), max(1, ch // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9)).resize((cw, ch), Image.BILINEAR).point(lambda v: int(v * s.sombra))
            sh_ = Image.new('RGBA', (cw, ch), (0, 0, 0, 0)); sh_.putalpha(so)
            pega(lz, sh_, px + int(ya * -40 + 18), py + 34)
        pega(lz, out, px, py)


# ---------- pantallas vivas
def _dos(w, h, col):
    return Image.new('RGBA', (w * 2, h * 2), col + (255,))
def _tira_busqueda():
    # resultados que hacen scroll
    H_ = 1900
    im = _dos(SW, H_, (255, 255, 255)); d = ImageDraw.Draw(im)
    x0, w_ = 24, SW - 48
    d.rounded_rectangle((x0 * 2, 16, (x0 + w_) * 2, 560), 36, fill=(232, 238, 228, 255))
    for a, b, c_, e_ in ((0, 180, 900, 90), (200, 0, 620, 560), (0, 420, 900, 330), (620, 0, 380, 560)):
        d.line((x0 * 2 + a, 16 + b, x0 * 2 + c_, 16 + e_), fill=(255, 255, 255, 255), width=18)
    for px, py in ((180, 180), (470, 300), (720, 150)):
        d.ellipse((x0 * 2 + px - 26, py - 26, x0 * 2 + px + 26, py + 26), fill=(226, 54, 48, 255)); d.polygon([(x0 * 2 + px - 20, py + 14), (x0 * 2 + px + 20, py + 14), (x0 * 2 + px, py + 58)], fill=(226, 54, 48, 255)); d.ellipse((x0 * 2 + px - 9, py - 9, x0 * 2 + px + 9, py + 9), fill=(255, 255, 255, 255))
    y = 600
    cols = [(52, 120, 220), (230, 150, 50), (60, 170, 110), (170, 80, 190), (40, 150, 170), (220, 90, 90), (90, 110, 130), (200, 170, 60)]
    for i, tx in enumerate(('tu competidor', 'otro competidor', 'otro más', 'y otro más', 'tu competidor', 'otro competidor', 'otro más', 'y otro más')):
        d.rounded_rectangle((x0 * 2, y, x0 * 2 + 180, y + 180), 28, fill=cols[i] + (255,))
        d.text((x0 * 2 + 210, y + 6), tx, font=F(50, 1), fill=(24, 84, 196, 255))
        for q in range(5):
            cx_, cy_ = x0 * 2 + 226 + q * 42, y + 92
            d.polygon([(cx_ + 18 * math.cos(a_ * math.pi / 5 - math.pi / 2) * (1 if a_ % 2 == 0 else .45), cy_ + 18 * math.sin(a_ * math.pi / 5 - math.pi / 2) * (1 if a_ % 2 == 0 else .45)) for a_ in range(10)], fill=(245, 170, 30, 255))
        d.rounded_rectangle((x0 * 2 + 210, y + 128, x0 * 2 + 700, y + 148), 10, fill=(214, 214, 214, 255))
        d.rounded_rectangle((x0 * 2 + 210, y + 162, x0 * 2 + 560, y + 180), 9, fill=(228, 228, 228, 255))
        y += 236
    return im.resize((SW, H_), Image.BOX)
_TIRA = _tira_busqueda()
_HDRB = _dos(SW, 170, (255, 255, 255)); _d = ImageDraw.Draw(_HDRB)
_d.text((62, 30), '9:41', font=F(40, 1), fill=(20, 20, 22, 255))
_d.rounded_rectangle((SW * 2 - 110, 36, SW * 2 - 52, 66), 8, outline=(20, 20, 22, 255), width=4); _d.rectangle((SW * 2 - 104, 42, SW * 2 - 70, 60), fill=(20, 20, 22, 255))
_d.rounded_rectangle((36, 150, SW * 2 - 36, 300), 75, fill=(241, 243, 246, 255))
_d.ellipse((70, 196, 118, 244), outline=(90, 90, 96, 255), width=7); _d.line((110, 236, 130, 258), fill=(90, 90, 96, 255), width=8)
_HDRB = _HDRB.resize((SW, 170), Image.BOX)
_QUERY = 'lo que vendes, cerca'
def pant_busca(t):
    p = Image.new('RGBA', (SW, SH), (255, 255, 255, 255))
    t0, t1 = T(5, 3), T(5, 7)
    u = cl((t - t1 - .02) / .12)
    if u > 0:
        sc = cb(.5, 0, .2, 1)(cl((t - t1) / (T(5, 8) - t1 + .2))) * 620
        p.alpha_composite(_TIRA, (0, 170), (0, int(sc), SW, min(_TIRA.height, int(sc) + SH - 170)))
        if u < 1: p = Image.blend(Image.new('RGBA', (SW, SH), (255, 255, 255, 255)), p, u)
    p.alpha_composite(_HDRB)
    d = ImageDraw.Draw(p)
    n = int(len(_QUERY) * cl((t - t0) / (t1 - t0)))
    d.text((78, 113), _QUERY[:n], font=F(33, 0), fill=(30, 30, 34, 255), anchor='lm')
    if int(t * 6) % 2 == 0 and t < t1:
        wx = 80 + (F(33, 0).getlength(_QUERY[:n]))
        d.line((wx, 94, wx, 132), fill=(30, 110, 240, 255), width=3)
    return p
_rv = None
def grieta_(tam=SW):
    im = Image.new('RGBA', (SW * 2, SH * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); g_ = np.random.default_rng(4)
    for i in range(13):
        a = i / 13 * 6.28 + g_.uniform(-.2, .2); x, y = SW * .9, SH * .9; p = [(x, y)]
        for q in range(7):
            a += g_.uniform(-.35, .35); r_ = g_.uniform(50, 140); x += r_ * math.cos(a); y += r_ * math.sin(a); p.append((x, y))
        d.line(p, fill=(255, 255, 255, 210), width=3); d.line([(a_ + 3, b_ + 3) for a_, b_ in p], fill=(20, 20, 20, 170), width=2)
    return im.resize((SW, SH), Image.BOX)
_GR = grieta_()
def pant_vieja(t):
    global _rv
    if _rv is None: _rv = gris_(red_vieja().resize((SW, SH), Image.BOX), .55, .86)
    p = _rv.copy()
    if t >= T(7, 7): p.alpha_composite(_GR)
    return p
_av = Image.open('foto_persona.jpg').convert('RGB')
_av = _av.crop((int(_av.width * .60), int(_av.height * .20), int(_av.width * .60) + int(_av.height * .17), int(_av.height * .37))).resize((68, 68), Image.BILINEAR)
_am = Image.new('L', (136, 136), 0); ImageDraw.Draw(_am).ellipse((0, 0, 135, 135), fill=255); _am = _am.resize((68, 68), Image.BOX)
def _fondo_chat():
    p = _dos(SW, SH, (11, 20, 24)); d = ImageDraw.Draw(p)
    g_ = np.random.default_rng(9)
    for q in range(90):
        x, y, r = g_.uniform(0, SW * 2), g_.uniform(260, SH * 2), g_.uniform(8, 22)
        d.ellipse((x - r, y - r, x + r, y + r), outline=(22, 34, 38, 255), width=4)
    d.rectangle((0, 0, SW * 2, 260), fill=(26, 38, 44, 255))
    d.text((200, 150), NOMBRE, font=F(50, 1), fill=(240, 244, 246, 255), anchor='lm')
    d.text((200, 208), 'en línea', font=F(32, 0), fill=(70, 210, 140, 255), anchor='lm')
    d.rounded_rectangle((28, SH * 2 - 130, SW * 2 - 150, SH * 2 - 34), 48, fill=(32, 44, 51, 255))
    d.ellipse((SW * 2 - 130, SH * 2 - 130, SW * 2 - 34, SH * 2 - 34), fill=(37, 190, 104, 255))
    p = p.resize((SW, SH), Image.BOX)
    p.paste(_av, (22, 44), _am)
    return p
_FCH = _fondo_chat()
def _burbuja(txt, tam, col, colt, ancho_=None):
    wt = F(tam * 2, 1).getlength(txt)
    w_ = int(wt / 2) + 56
    if w_ > SW - 40: print('ANCHO burbuja', txt, w_, file=sys.stderr)
    im = Image.new('RGBA', (w_ * 2, (tam + 44) * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w_ * 2 - 1, (tam + 44) * 2 - 1), 44, fill=col + (255,))
    d.text((w_, tam + 44), txt, font=F(tam * 2, 1), fill=colt + (255,), anchor='mm')
    return im.resize((w_, tam + 44), Image.BOX)
_BUR = [(_burbuja('¿me echas una mano?', 40, (0, 110, 88), (255, 255, 255)), 'd', T(18, 4), 190), (_burbuja('claro, te contesto yo', 40, (38, 52, 60), (255, 255, 255)), 'i', T(18, 6), 305), (_burbuja('cuéntame tu negocio', 40, (38, 52, 60), (255, 255, 255)), 'i', T(18, 8), 420)]
def pant_chat(t):
    p = _FCH.copy()
    Se = cb(.2, .9, .3, 1)
    for im, lado, ta, y in _BUR:
        if lado == 'i' and ta - .45 <= t < ta:      # escribiendo...
            bx = Image.new('RGBA', (108, 58), (0, 0, 0, 0)); d = ImageDraw.Draw(bx); d.rounded_rectangle((0, 0, 107, 57), 22, fill=(38, 52, 60, 255))
            for q in range(3):
                d.ellipse((24 + q * 22, 25 - 7 * abs(math.sin(t * 9 + q)), 36 + q * 22, 37 - 7 * abs(math.sin(t * 9 + q))), fill=(170, 186, 194, 255))
            p.alpha_composite(bx, (22, y))
        if t >= ta:
            u = Se(cl((t - ta) / .22))
            e_ = .7 + .3 * u
            f = im.resize((max(1, int(im.width * e_)), max(1, int(im.height * e_))), Image.BILINEAR)
            x = SW - 22 - f.width if lado == 'd' else 22
            p.alpha_composite(f, (x, y + int((1 - u) * 26)))
    return p


# ---------- objetos
def esfera_reloj(R=430):
    im = lienzo(2 * R, 2 * R)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 4 * R - 1, 4 * R - 1), fill=(20, 20, 22, 255))
    d.ellipse((22 * R_, 22 * R_, (2 * R - 22) * R_, (2 * R - 22) * R_), fill=(250, 250, 248, 255))
    for i in range(60):
        a = i * math.pi / 30
        r0, g = (.84, 9) if i % 5 == 0 else (.91, 3)
        d.line(((R + R * r0 * math.cos(a)) * R_, (R + R * r0 * math.sin(a)) * R_, (R + R * .94 * math.cos(a)) * R_, (R + R * .94 * math.sin(a)) * R_), fill=(20, 20, 22, 255), width=g * R_)
    for i in range(1, 13):
        a = i * math.pi / 6 - math.pi / 2
        d.text(((R + R * .72 * math.cos(a)) * R_, (R + R * .72 * math.sin(a)) * R_), str(i), font=F(int(R * .15) * R_, 1), fill=(20, 20, 22, 255), anchor='mm')
    return con_sombra(im, des=26, op=.34)


def moneda_oro(R=430):
    im = lienzo(2 * R, 2 * R)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 4 * R - 1, 4 * R - 1), fill=(176, 122, 26, 255))
    d.ellipse((20 * R_, 20 * R_, (2 * R - 20) * R_, (2 * R - 20) * R_), fill=(247, 196, 66, 255))
    d.ellipse((70 * R_, 70 * R_, (2 * R - 70) * R_, (2 * R - 70) * R_), fill=(230, 168, 44, 255))
    d.ellipse((84 * R_, 84 * R_, (2 * R - 84) * R_, (2 * R - 84) * R_), fill=(250, 208, 84, 255))
    d.text((R * R_ + 8, R * R_ + 8), '€', font=F(int(R * 1.05) * R_, 1), fill=(176, 122, 26, 255), anchor='mm')
    d.text((R * R_, R * R_), '€', font=F(int(R * 1.05) * R_, 1), fill=(120, 80, 14, 255), anchor='mm')
    return con_sombra(im, des=26, op=.34)


def aguja(l, g, col=(20, 20, 22)):
    im = lienzo(g + 8, l + 60)
    ImageDraw.Draw(im).rounded_rectangle((4 * R_, 0, (g + 4) * R_, (l + 60) * R_), g * R_, fill=col + (255,))
    return im


def carretera_p(w=1500, h=2000):
    """Carretera negra que serpentea hasta el fondo, con raya central: perspectiva hecha a mano."""
    im = Image.new('L', (w * 2, h * 2), 0)
    raya = Image.new('L', (w * 2, h * 2), 0)
    dr, dl = ImageDraw.Draw(im), ImageDraw.Draw(raya)
    izq, der = [], []
    ctr = []
    for k in range(240):
        v = k / 239                 # 0 abajo (cerca), 1 arriba (lejos)
        y = h * (1 - v) * 2
        an = (640 * (1 - v) ** 1.7 + 12) * 2
        x = (w / 2 + (1 - v) ** .3 * 0 + 430 * math.sin(v * 8.2) * (1 - v * .7)) * 2
        izq.append((x - an / 2, y)); der.append((x + an / 2, y)); ctr.append((x, y, an))
    dr.polygon(izq + der[::-1], fill=255)
    for k in range(0, 234, 10):
        (a, b, n1), (c, e, n2) = ctr[k], ctr[k + 5]
        dl.line((a, b, c, e), fill=255, width=max(2, int(n1 * .018)))
    m = np.asarray(im.resize((w, h), Image.BOX), np.float32)
    r = np.asarray(raya.resize((w, h), Image.BOX), np.float32)[..., None] / 255
    col = np.zeros((h, w, 3), np.float32) + 22
    col = col * (1 - r) + 240 * r
    return Image.fromarray(np.dstack([col, m]).astype(np.uint8), 'RGBA')


def bandera():
    im = lienzo(170, 240)
    d = ImageDraw.Draw(im)
    d.rectangle((8 * R_, 0, 18 * R_, 240 * R_), fill=(20, 20, 22, 255))
    d.polygon(pp([(18, 6), (160, 44), (18, 86)]), fill=ROJO + (255,))
    return im


def marcador(txt):
    im = plaza(150, 76, (255, 255, 255), rr=38)
    s_ = sprite_txt(txt, 38, 1, TINTA)
    im.alpha_composite(s_, ((im.width - s_.width) // 2, (im.height - s_.height) // 2))
    return con_sombra(im, des=10, op=.3)


def telarana(tam=720):
    im = Image.new('L', (tam, tam), 0)
    d = ImageDraw.Draw(im)
    for i in range(9):
        a = i * math.pi / 16
        d.line((0, 0, tam * math.cos(a), tam * math.sin(a)), fill=210, width=2)
    for r in (120, 220, 330, 440, 560):
        p = [(r * math.cos(i * math.pi / 16) * (1 + .03 * (-1) ** i), r * math.sin(i * math.pi / 16) * (1 + .03 * (-1) ** i)) for i in range(9)]
        d.line(p, fill=170, width=2)
    o = Image.new('RGBA', (tam, tam), (240, 240, 240, 0))
    o.putalpha(im)
    return o


def gris_(im, f=.75, luz=.7):
    a = np.array(im).astype(np.float32)
    g = a[..., :3].mean(-1, keepdims=True)
    a[..., :3] = (a[..., :3] * (1 - f) + g * f) * luz
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')


def cuadro_viejo():
    w, h = 720, 500
    im = plaza(w, h, (238, 232, 214), rr=4)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w * R_, 66 * R_), fill=(104, 118, 150, 255))
    d.text((28 * R_, 33 * R_), 'BIENVENIDOS A NUESTRA WEB', font=F(30 * R_, 1), fill=(255, 255, 255, 255), anchor='lm')
    d.rectangle((36 * R_, 96 * R_, 330 * R_, 300 * R_), fill=(176, 176, 170, 255))
    d.line((36 * R_, 96 * R_, 330 * R_, 300 * R_), fill=(130, 130, 124, 255), width=4)
    d.line((36 * R_, 300 * R_, 330 * R_, 96 * R_), fill=(130, 130, 124, 255), width=4)
    d.text((360 * R_, 110 * R_), 'NOVEDADES', font=F(36 * R_, 1), fill=(100, 70, 60, 255))
    d.text((360 * R_, 164 * R_), 'Hace 6 años', font=F(30 * R_, 0), fill=(120, 110, 100, 255))
    for y in (216, 250, 284):
        d.rectangle((360 * R_, y * R_, 672 * R_, (y + 12) * R_), fill=(186, 180, 166, 255))
    d.rectangle((36 * R_, 340 * R_, 672 * R_, 460 * R_), fill=(214, 206, 188, 255))
    d.text((354 * R_, 400 * R_), 'EN CONSTRUCCIÓN', font=F(44 * R_, 1), fill=(150, 100, 60, 255), anchor='mm')
    m = marco(w + 88, h + 88)
    m.paste(im, (44 * R_, 44 * R_))
    return con_sombra(m, des=26, op=.5)


def red_vieja():
    p = _pantalla((250, 250, 248))
    d = ImageDraw.Draw(p)
    W_ = p.width
    d.ellipse((36 * R_, 110 * R_, 136 * R_, 210 * R_), fill=(196, 196, 196, 255))
    d.text((156 * R_, 142 * R_), 'tu negocio', font=F(36 * R_, 1), fill=(40, 40, 40, 255))
    d.text((156 * R_, 184 * R_), 'última publicación: hace 2 años', font=F(20 * R_, 0), fill=(150, 150, 150, 255))
    for j in range(5):
        for i in range(3):
            x, y = 16 + i * 148, 260 + j * 148
            d.rectangle((x * R_, y * R_, (x + 140) * R_, (y + 140) * R_), fill=(226, 226, 222, 255) if (i + j * 3) < 4 else (244, 244, 242, 255))
    return p


def pantalla_busca():
    p = _pantalla((252, 252, 250))
    d = ImageDraw.Draw(p)
    W_ = p.width
    d.rounded_rectangle((26 * R_, 110 * R_, W_ - 26 * R_, 182 * R_), 36 * R_, outline=(180, 180, 184, 255), width=3 * R_)
    d.ellipse((50 * R_, 128 * R_, 82 * R_, 160 * R_), outline=(100, 100, 104, 255), width=5)
    d.text((98 * R_, 146 * R_), 'lo que vendes, cerca', font=F(30 * R_, 0), fill=(60, 60, 64, 255), anchor='lm')
    for j, (tx, co) in enumerate((('tu competidor', (26, 96, 210)), ('otro competidor', (26, 96, 210)), ('otro más', (26, 96, 210)))):
        y = 226 + j * 180
        d.text((30 * R_, y * R_), tx, font=F(40 * R_, 1), fill=co + (255,))
        for q, w_ in ((62, 380), (92, 330), (122, 260)):
            d.rounded_rectangle((30 * R_, (y + q) * R_, (30 + w_) * R_, (y + q + 12) * R_), 6 * R_, fill=(200, 200, 196, 255))
    return p


# ---------- fondos
OSCURO = fondo_oscuro()
CLARO = Image.new('RGBA', (W, H), CREMA + (255,))
GRISB = Image.new('RGBA', (W, H), GRIS + (255,))
SALA = Image.new('RGBA', (W, H), (26, 16, 10, 255))
_rej = rejilla(tam=1500, paso=66)
S = {k: [] for k in 'ZABCDEFGHIJKL'}
S['C2'] = []
SO = socio()
_chr = Image.open('foto_persona.jpg')
_mw = [mini_web(i) for i in range(6)]
_tn = tienda('TU NEGOCIO')
_tc = tienda('COMPETIDOR', (150, 26, 30))
_pn = persona()
_mo = mota(r=7, col=(236, 228, 210))

def bl(k, lineas, o, cy, a, b, **kw):
    S[k].extend(bloque(lineas, o, cy=cy, ini=a, fin=b, **kw))


# ===== A: la región. Punto que se abre en píldora; tiendas; reloj hacia atrás
sa = rest(LA[0] - .01)
S['A'].append(Capa(_rej, (sa[0], sa[1], sa[2]), res=1, liso=True, ini=TC['z'], fin=TC['a'] + .02, op=lambda t: .6))
_er, _ag1, _ag2 = esfera_reloj(), aguja(290, 16), aguja(370, 8, ROJO)
_tcl = INI[1] - .06
_tflip = TC['a'] - .6
_fi = lambda t: math.pi * 3 * cb(.3, 0, .15, 1)(cl((t - _tflip) / .52))      # el reloj es una moneda: da vuelta y media
def _esc_cara(t):
    e = max(.001, muelle((t - _tcl) / .55)) * .92
    return (max(.001, math.cos(_fi(t)) * e), e)
def _esc_cruz(t): return (max(.001, -math.cos(_fi(t)) * .92), .92)
_can = lienzo(860, 860); ImageDraw.Draw(_can).ellipse((0, 0, 860 * R_ - 1, 860 * R_ - 1), fill=(150, 100, 18, 255))
for d_ in np.linspace(-34, 34, 9):
    S['A'].append(Capa(_can, (sa[0], sa[1] + 230, sa[2]), res=2, ini=_tflip, fin=TC['a'] + .02, esc=lambda t: (max(.001, abs(math.cos(_fi(t))) * .92), .92), dxy=lambda t, q=float(d_): (q * math.sin(_fi(t)), 0)))
S['A'].append(Capa(_er, (sa[0], sa[1] + 230, sa[2]), res=2, ini=_tcl, fin=TC['a'] + .02, esc=_esc_cara))
S['A'].append(Capa(moneda_oro(), (sa[0], sa[1] + 230, sa[2]), res=2, ini=_tflip, fin=TC['a'] + .02, esc=_esc_cruz))
_rtime = lambda t: -(t - _tcl) ** 2 * 460
S['A'].append(Capa(_ag1, (sa[0], sa[1] + 230, sa[2]), res=2, ancla=(13, 320), ini=_tcl + .08, fin=_tflip, rot=lambda t: _rtime(t) * .083 + 40))
S['A'].append(Capa(_ag2, (sa[0], sa[1] + 230, sa[2]), res=2, ancla=(7, 400), ini=_tcl + .08, fin=_tflip, rot=lambda t: _rtime(t) + 200))
for k in range(11):
    a = T(1, 5) + (T(1, 7) - T(1, 5) + .2) * k / 10
    b = T(1, 5) + (T(1, 7) - T(1, 5) + .2) * (k + 1) / 10 if k < 10 else TC['a'] + .02
    S['A'].append(Capa(sprite_txt(str(2026 - k), 196, 1, ROJO if k == 10 else TINTA), (sa[0], sa[1] - 440, sa[2]), res=2, ini=a, fin=b))
bl('A', [lin(72, [('con el mismo marketing', T(1, 0))], 0)], sa, -640, INI[1] - .05, TC['a'] + .02)

# ===== Z: En la región. Globo que gira y baja hasta el mapa, con negocios que aparecen
# Contornos dibujados a mano con coordenadas (longitud, latitud).
_MUNDO = [
 [(-9,37),(-9.5,38.7),(-8.8,42),(-9,43.2),(-1.8,43.4),(-1.2,46),(-4.6,48.4),(-1.6,48.7),(1.5,50.9),(4,52),(8,54),(8.5,57),(10.5,57.7),(10.5,54),(14,54),(19,54.5),(21,57),(24,59.4),(30,60),(23,60),(21,61),(21.5,63),(25,65.5),(22,65.8),(17.5,62),(18.5,60),(16.5,56.5),(13,55.5),(11,58.5),(8,58),(5,59),(5,62),(12,65.5),(18,69.5),(25,71),(31,70),(41,67),(34,65),(38,64.5),(44,68),(54,68.5),(68,68.5),(73,72),(105,77),(140,73),(180,69),(180,62),(163,60),(156,52),(155,59),(142,59),(135,54),(141,48),(130,42.5),(127,39),(129,35),(126,34.5),(125,39),(121,40),(118,38.5),(122,37),(119,34),(122,30),(118,24),(110,21),(106,19),(109,13),(105,9),(100,13),(104,2),(101,3),(98,8),(98,16),(94,17),(91,22),(86,20),(80,15),(80,10),(77,8),(73,18),(72,21),(67,25),(57,25.5),(59,22),(52,16),(43,12.5),(39,21),(34.5,28),(35,32),(36,36.5),(30,36.3),(27,37),(26,40),(23,40.5),(24,38),(22.5,36.5),(19.5,40.5),(13.5,45.5),(12.4,44),(16,41.5),(18.4,40),(16,38),(15.7,40),(10.5,43),(8,44),(3,43.2),(3.2,41.8),(0,40),(-.5,38.3),(-2.2,36.7),(-5.4,36.1)],
 [(-5.9,35.8),(-1,35),(10,37.3),(11,33.5),(20,32),(20,31),(32,31.2),(34.5,28),(37,21),(43,12),(51,12),(40,-3),(39,-10),(40.5,-15),(35,-24),(32,-29),(26,-34),(18.5,-34),(15,-27),(12,-17),(13.5,-8),(9,-1),(9,4),(4,6),(-4,5),(-8,4.5),(-13,8.5),(-17,14.5),(-16,20),(-13,27.5),(-9.5,31),(-6.5,34)],
 [(-168,65),(-156,71),(-128,70),(-95,69),(-85,69),(-82,64),(-92,58),(-82,52),(-78,58),(-78,62),(-65,60),(-56,52),(-66,50),(-61,46),(-70,43),(-74,40),(-76,35),(-81,31),(-80,25),(-83,29),(-90,29.5),(-97,26),(-97,20),(-91,18),(-87,21),(-88,16),(-83,15),(-81,9),(-78,8.5),(-85,10),(-96,16),(-105,20),(-110,23),(-114,30),(-117,33),(-124,40),(-124,48),(-134,58),(-150,60),(-165,55)],
 [(-78,8),(-72,12),(-62,10.5),(-52,5),(-50,0),(-35,-6),(-39,-15),(-41,-22),(-48,-26),(-56,-35),(-65,-41),(-68,-52),(-75,-50),(-73,-37),(-70,-18),(-81,-5),(-79,1)],
 [(-5.5,50),(1.5,51.2),(1.7,52.8),(-1,55),(-2,57.6),(-5,58.6),(-6,56),(-3,54),(-5,52)], [(-10,52),(-6,52),(-6,55),(-10,54.5)], [(-24,65.5),(-14,66),(-14,64.5),(-22,63.5)], [(-55,82),(-25,83),(-20,72),(-43,60),(-53,66)]]
_CANT = [(-4.51,43.39),(-4.39,43.39),(-4.29,43.39),(-4.15,43.42),(-4.04,43.44),(-3.93,43.47),(-3.79,43.49),(-3.73,43.46),(-3.60,43.50),(-3.52,43.49),(-3.44,43.45),(-3.41,43.41),(-3.30,43.40),(-3.22,43.38),(-3.15,43.35),(-3.19,43.29),(-3.27,43.24),(-3.37,43.20),(-3.42,43.13),(-3.60,43.06),(-3.75,43.00),(-3.88,42.95),(-3.95,42.84),(-3.75,42.76),(-4.02,42.77),(-4.15,42.82),(-4.35,42.87),(-4.40,42.97),(-4.48,43.02),(-4.72,43.02),(-4.85,43.10),(-4.85,43.20),(-4.60,43.28)]
_IBE = [(-8.4,43.37),(-7.87,43.77),(-7.04,43.54),(-5.85,43.66),(-5.66,43.55),(-5.1,43.47),(-4.75,43.42),(-4.51,43.39),(-4.39,43.39),(-4.29,43.39),(-4.15,43.42),(-4.04,43.44),(-3.93,43.47),(-3.79,43.49),(-3.73,43.46),(-3.60,43.50),(-3.52,43.49),(-3.44,43.45),(-3.41,43.41),(-3.30,43.40),(-3.22,43.38),(-3.03,43.38),(-2.75,43.45),(-2.2,43.3),(-1.98,43.32),(-1.79,43.37),(-1,43),(0,42.7),(.7,42.7),(1.7,42.5),(3.17,42.43),(3.32,42.32),(2.17,41.38),(1.25,41.1),(.87,40.7),(-.03,39.98),(-.33,39.46),(.23,38.73),(-.48,38.35),(-.7,37.63),(-.98,37.6),(-2.19,36.73),(-2.46,36.84),(-4.42,36.72),(-5.35,36.14),(-5.6,36.01),(-6.29,36.53),(-6.95,37.2),(-7.4,37.19),(-7.5,37.6),(-7,38.2),(-7.3,39.4),(-6.9,40.3),(-6.6,41.3),(-6.2,41.6),(-6.7,41.95),(-8.1,41.85),(-8.85,42.1),(-9.27,42.9)]
_POR = [(-7.4,37.19),(-8.99,37.02),(-8.9,38.4),(-9.5,38.75),(-9.07,39.6),(-8.69,41.15),(-8.85,42.1),(-8.1,41.85),(-6.7,41.95),(-6.2,41.6),(-6.6,41.3),(-6.9,40.3),(-7.3,39.4),(-7,38.2),(-7.5,37.6)]
_FRA = [(-1.79,43.37),(-1.2,46),(-4.6,48.4),(-1.6,48.7),(1.5,50.9),(7,49),(7.5,44),(3,43.2),(3.17,42.43),(1.7,42.5),(.7,42.7),(0,42.7),(-1,43)]
_mk = Image.new('L', (1440, 720), 0); _dk = ImageDraw.Draw(_mk)
for pol in _MUNDO: _dk.polygon([((a + 180) * 4, (90 - b) * 4) for a, b in pol], fill=255)
_mk = np.asarray(_mk)
_pun = []
for la in np.arange(-78, 84, 2.1):
    for lo in np.arange(-180, 180, 2.1 / max(.2, math.cos(math.radians(la)))):
        if _mk[int((90 - la) * 4) % 720, int((lo + 180) * 4) % 1440]: _pun.append((math.radians(lo), math.radians(la)))
_pun = np.array(_pun)
_rs = np.random.default_rng(3).uniform(0, 1, (90, 3))
sz = rest(LZ[0] - .01)
_tmap_ = 1.02
_RE, _ZO = cb(.6, 0, .2, 1), cb(.15, .7, .2, 1)
def _vista(t):
    u = cl(t / .85); e = _ZO(u)
    R = 500 * (37000 / 500) ** _RE(cl((t - .16) / .9))
    return R, -105 + (-4 + 105) * e, 15 + (43.14 - 15) * e
def _proy(lo, la, lo0, la0):
    lo, la, lo0, la0 = np.radians(lo), np.radians(la), math.radians(lo0), math.radians(la0)
    d = lo - lo0
    return np.cos(la) * np.sin(d), math.cos(la0) * np.sin(la) - math.sin(la0) * np.cos(la) * np.cos(d), math.sin(la0) * np.sin(la) + math.cos(la0) * np.cos(la) * np.cos(d)
_CY = 90
def geo(lo, la, t):
    R, lo0, la0 = _vista(t)
    x, y, _ = _proy(lo, la, lo0, la0)
    return sz[0] + R * float(x), sz[1] + _CY - R * float(y), sz[2]
class Globo:
    def dibuja(s, lz, t, c):
        R0, lo0, la0 = _vista(t)
        k = ZOOM / max(40, sz[2] - c[2] + ZOOM)
        R = R0 * k
        cx, cy = W / 2 + (sz[0] - c[0]) * k, H / 2 + (sz[1] + _CY - c[1]) * k
        d0 = ImageDraw.Draw(lz)
        if R < 2600:      # estrellas y atmósfera, solo desde lejos
            for a, b, q in _rs:
                d0.ellipse((a * W, b * H, a * W + 1 + q * 2.6, b * H + 1 + q * 2.6), fill=(150, 170, 220, 255))
            for q in range(10, 0, -1):
                r = R * (1 + q * .022)
                d0.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(10 + 5 * (10 - q), 18 + 10 * (10 - q), 40 + 20 * (10 - q), 255))
            d0.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(10, 16, 36, 255))
        else:
            d0.rectangle((0, 0, W, H), fill=(9, 15, 32, 255))
        v_ = cl((R - 1300) / 900)       # de puntos a mapa
        if v_ < 1:
            x, y, z = _proy(np.degrees(_pun[:, 0]), np.degrees(_pun[:, 1]), lo0, la0)
            vis = (z > .02) & (np.abs(x * R + cx - W / 2) < W * .6) & (np.abs(cy - y * R - H / 2) < H * .6)
            r_ = max(1.3, R * .0052)
            for px, py, pz in zip((cx + x[vis] * R).tolist(), (cy - y[vis] * R).tolist(), z[vis].tolist()):
                ll = (1 - v_) * (.35 + .65 * pz)
                d0.ellipse((px - r_, py - r_, px + r_, py + r_), fill=(int(70 * ll + 10), int(135 * ll + 16), int(255 * ll + 36), 255))
        if v_ > 0:
            G = Image.new('RGB', (W * 2, H * 2), (9, 15, 32) if R >= 2600 else (10, 16, 36))
            dg = ImageDraw.Draw(G)
            def pol(l):
                x, y, _ = _proy(np.array([p[0] for p in l], float), np.array([p[1] for p in l], float), lo0, la0)
                return list(zip(((cx + x * R) * 2).tolist(), ((cy - y * R) * 2).tolist()))
            e_ = lambda a, b: tuple(int(p * v_ + q * (1 - v_)) for p, q in zip(a, b))
            ba = (10, 16, 36)
            for l in (_POR, _FRA): dg.polygon(pol(l), fill=e_((24, 32, 56), ba))
            pi = pol(_IBE); dg.polygon(pi, fill=e_((30, 44, 86), ba)); dg.line(pi + pi[:1], fill=e_((110, 155, 250), ba), width=5)
            q_ = cl((R - 5000) / 9000)
            pc = pol(_CANT)
            for q in range(8, 0, -1):        # canto: la región se levanta del mapa
                dg.polygon([(a, b + q * 7 * q_) for a, b in pc], fill=tuple(int(x_ * q_ + y_ * (1 - q_)) for x_, y_ in zip((120 + q * 3, 80 + q * 2, 20), (30, 44, 86))))
            dg.polygon(pc, fill=tuple(int(a * q_ + b * (1 - q_)) for a, b in zip((250, 200, 84), e_((60, 86, 150), ba))))
            dg.line(pc + pc[:1], fill=tuple(int(a * q_ + b * (1 - q_)) for a, b in zip((255, 240, 190), e_((120, 165, 255), ba))), width=9)
            M_ = G.resize((W, H), Image.BOX).convert('RGBA')
            if R < 2600:
                m_ = Image.new('L', (W, H), 0); ImageDraw.Draw(m_).ellipse((cx - R, cy - R, cx + R, cy + R), fill=255)
                lz.paste(M_, (0, 0), m_.point(lambda p: int(p * v_)))
            else:
                lz.paste(M_, (0, 0))
S['Z'].append(Globo())
for tx_, lo_, la_, tm_ in (('Asturias', -4.72, 42.86, 38), ('Castilla y León', -4.05, 42.50, 38), ('País Vasco', -3.25, 42.98, 38)):
    S['Z'].append(Capa(sprite_txt(tx_, tm_, 0, (170, 195, 245)), lambda t, a=lo_, b=la_: geo(a, b, t), res=2, ini=_tmap_ - .1, fin=TC['z'] + .02, op=lambda t: .75 * cl((t - _tmap_ + .1) / .25)))
_tn2 = tienda('TU NEGOCIO')
_tmap = 1.02
_sitios = [(-3.81, 43.43), (-4.06, 43.33), (-3.27, 43.33), (-3.55, 43.38), (-4.10, 43.03), (-4.60, 43.17), (-4.38, 43.35), (-3.80, 43.20)]
for i, (lo, la) in enumerate(_sitios):
    ta = T(0, 3) - .06 + i * .08
    S['Z'].append(Capa(_tn2, lambda t, a=lo, b=la: geo(a, b, t), res=2, ini=ta, fin=TC['z'] + .02, esc=pop(ta, .24, .115)))
pildora_txt(S['Z'], (sz[0], sz[1] - 300, sz[2]), T(0, 1) - .03, 600, 150, AZUL, REGION, 100, tb=T(0, 1) + .14, fin=TC['z'] + .02)
bl('Z', [lin(84, [('hay negocios', T(0, 2))], 0, BLA), lin(150, [('buenísimos', T(0, 4))], 1, (250, 204, 90))], sz, -610, -1, TC['z'] + .02)

# ===== B: tú has mejorado: píldoras con rebote
sb = rest(LB[0] - .01)
bl('B', [lin(92, [('tú', T(2, 0))], 0), lin(142, [('has mejorado', T(2, 1))], 1)], sb, -420, TC['a'], FIN[2] + .15)
bl('B', [lin(70, [('has cambiado', T(3, 0))], 0)], sb, -560, FIN[2] + .15, TC['b'] + .02)
_tmar = T(2, 1) - .08
def _an_m(t): return 110 + 820 * muelle((t - _tmar) / .55)
class Corchetes:
    # dos corchetes redondeados que se separan, abriendo el marco alrededor del texto
    def dibuja(s, lz, t, c):
        if not (TC['a'] <= t < FIN[2] + .15): return
        k = ZOOM / max(40, sb[2] - c[2] + ZOOM)
        w, h = _an_m(t) * k, 330 * k
        cx, cy = W / 2 + (sb[0] - c[0]) * k, H / 2 + (sb[1] - 420 - c[1]) * k
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        g = max(4, int(8 * k)); rr = int(46 * k); br = int(150 * k)
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
        col = (16, 16, 16, 255)
        d.arc((x0, y0, x0 + 2 * rr, y0 + 2 * rr), 180, 270, fill=col, width=g); d.arc((x0, y1 - 2 * rr, x0 + 2 * rr, y1), 90, 180, fill=col, width=g)
        d.arc((x1 - 2 * rr, y0, x1, y0 + 2 * rr), 270, 360, fill=col, width=g); d.arc((x1 - 2 * rr, y1 - 2 * rr, x1, y1), 0, 90, fill=col, width=g)
        d.line((x0, y0 + rr, x0, y1 - rr), fill=col, width=g); d.line((x1 - g, y0 + rr, x1 - g, y1 - rr), fill=col, width=g)
        d.line((x0 + rr, y0, x0 + br, y0), fill=col, width=g); d.line((x0 + rr, y1 - g, x0 + br, y1 - g), fill=col, width=g)
        d.line((x1 - br, y0, x1 - rr, y0), fill=col, width=g); d.line((x1 - br, y1 - g, x1 - rr, y1 - g), fill=col, width=g)
        lz.alpha_composite(im)
S['B'].append(Corchetes())
for i, (tx, j, col) in enumerate((('el local', 3, AZUL), ('el equipo', 5, (20, 20, 22)), ('lo que vendes', 7, VERDEW))):
    ta = T(3, j) - .05
    pildora_txt(S['B'], (sb[0], sb[1] - 300 + i * 210, sb[2]), ta, 700, 160, col, tx, 92, fin=TC['b'] + .02, ini=max(TC['a'], ta - .05))

# ===== C2: tu marketing sigue igual: notas que se pasan y debajo siempre lo mismo
sc0 = rest(LC[0] - .01)
def nota_igual(tam=660):
    n = nota(tam=tam, sombra=False)
    d = ImageDraw.Draw(n)
    d.text((tam, int(tam * .9)), 'igual', font=F(int(tam * .3) * R_, 1), fill=(30, 30, 30, 255), anchor='mm')
    d.text((tam, int(tam * 1.32)), 'que el primer día', font=F(int(tam * .082) * R_, 0), fill=(60, 60, 60, 255), anchor='mm')
    return n
_ni = nota_igual()
_L = 660
_tnota = (T(4, 3), T(4, 4) + .1, T(4, 7))
def tiza(txt, tam):
    # palabra escrita a tiza y tachada, como las del tutorial
    sp = sprite_txt(txt, tam, 1, (232, 232, 228))
    a = np.array(sp).astype(np.float32)
    r_ = np.random.default_rng(len(txt) * tam)
    ruido = np.asarray(Image.fromarray(r_.uniform(0, 255, (a.shape[0] // 3 + 1, a.shape[1] // 3 + 1)).astype(np.uint8)).resize((a.shape[1], a.shape[0]), Image.BILINEAR), np.float32) / 255
    a[..., 3] *= np.clip(ruido * 2.2 - .25, .15, 1)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(im)
    w_, h_ = im.size
    for q in range(3):
        y0 = h_ * (.42 + q * .06)
        p_ = [(x, y0 + r_.uniform(-7, 7) + (x / w_ - .5) * -h_ * .22) for x in range(0, w_, 26)]
        d.line(p_, fill=(240, 240, 236, 235), width=7)
    return im
_tiz = [('2019', 150, -340, -1000, -8, T(4, 1)), ('2021', 190, 330, -360, 7, T(4, 2)), ('2023', 140, -390, 640, -6, T(4, 3)), ('2025', 170, 340, 740, 8, T(4, 4))]
for tx, tam, x, y, r, ta in _tiz:
    S['C2'].append(Capa(tiza(tx, tam), (sc0[0] + x, sc0[1] + y + 200, sc0[2] + 90), res=2, ini=TC['b'], fin=TC['c'] + .02, rot=lambda t, q=r: q, op=lambda t, a=ta: .75 * cl((t - a) / .12)))
S['C2'].append(HojaCurl(_ni, (255, 236, 150), (sc0[0], sc0[1] + 200, sc0[2]), _L, 0, ini=TC['b'], fin=TC['c'] + .02, vivo=True))
for q in (2, 1, 0):
    S['C2'].append(HojaCurl(_ni, (255, 236, 150), (sc0[0], sc0[1] + 200, sc0[2]), _L, _tnota[q], ini=TC['b'], fin=TC['c'] + .02))
bl('C2', [lin(76, [('y tu marketing', T(4, 1))], 0, BLA), lin(120, [('sigue igual', T(4, 3))], 1, (255, 214, 64))], sc0, -520, TC['b'], TC['c'] + .02)

# ===== C: el móvil: no te encuentra; el cliente se va al competidor
sc = rest(INI[6] - .22)
sc2 = rest(LD[0] - .01)
S['C'].append(Capa(_rej, (sc[0] + 450, sc[1] + 100, sc[2]), res=1, liso=True, ini=TC['c'], fin=TC['d'] + .02, esc=1.6))
S['C'].append(Movil3D(pant_busca, (sc[0], sc[1] + 330, sc[2]), lambda t: .94 * min(1.05, max(.02, muelle((t - TC['c'] - .05) / .55))), lambda t: 32 * math.exp(-4 * max(0, t - TC['c'])) + 7 * math.sin(t * 1.3), lambda t: 5 * math.sin(t * .9 + 1) + 4, lambda t: -2 + 1.5 * math.sin(t * .7), ini=TC['c'], fin=TC['d'] + .02))
_tno = T(5, 8)
S['C'].append(Capa(pastilla('tú no apareces', 56, ROJO), (sc[0], sc[1] + 620, sc[2] - 40), res=2, ini=_tno, fin=TC['d'] + .02, rot=lambda t: -3, esc=pop(_tno, .2)))
bl('C', [lin(72, [('el que te busca en el móvil', T(5, 1))], 0), lin(122, [('no te encuentra', T(5, 8))], 1, ROJO)], sc, -520, TC['c'], INI[6] + .3)
S['C'].append(Capa(_tc, (sc2[0] + 60, sc2[1] + 200, sc2[2]), res=2, ini=TC['c'], fin=TC['d'] + .02, esc=.8))
_ys = sc2[1] + 200 + 280
S['C'].append(Capa(calle(), (sc2[0] + 760, _ys + 10, sc2[2]), res=2, ini=TC['c'], fin=TC['d'] + .02))
for i in range(5):
    ta = INI[6] + i * .34
    def _pp(t, a=ta, g=i):
        u = cl((t - a) / 1.0)
        return (sc2[0] - 720 + (720 + 60) * u, _ys - 70 - abs(math.sin((t - a) * 10 + g)) * 12, sc2[2] - 30)
    S['C'].append(Capa(_pn, _pp, res=2, ini=ta, fin=ta + 1.02, esc=.46, rot=lambda t, a=ta, g=i: 5 * math.sin((t - a) * 10 + g)))
bl('C', [lin(72, [('y el cliente', T(6, 1))], 0), lin(120, [('se lo lleva', T(6, 3))], 1), lin(120, [('tu competidor', T(6, 7))], 1, ROJO)], sc2, -560, INI[6] + .3, TC['d'] + .02)

# ===== D: la sala de madera: lo descuidado colgado en la pared
sd = rest(LE[0] - .01)
S['D'].append(Capa(pared(), (sd[0], sd[1], sd[2] + 1500), res=1, esc=3.1, liso=True, ini=TC['d'], fin=TC['e'] + .02))
_cv = cuadro_viejo()
_tw = T(7, 5)
_tred = T(7, 2)
S['D'].append(Movil3D(pant_vieja, (sd[0] - 230, sd[1] + 140, sd[2] - 20), pop(_tred, .3, .72), lambda t: 24 + 6 * math.sin(t * 1.1), lambda t: 6 + 3 * math.sin(t * .8), lambda t: -6 + 1.5 * math.sin(t * 1.4), ini=TC['d'], fin=INI[8] - .03))
S['D'].append(Capa(_cv, (sd[0] + 115, sd[1] + 80, sd[2] - 50), res=2, ini=_tw, fin=TC['e'] + .02, esc=pop(_tw, .28, .8), rot=lambda t: 4 + 1.3 * math.sin(t * 2.2) + 15 * math.exp(-1.3 * max(0, t - T(8, 0))) * math.sin(6 * max(0, t - T(8, 0)))))
_tel = T(7, 7)
S['D'].append(Capa(telarana(), (sd[0] - 470, sd[1] - 210, sd[2] - 70), res=1, ancla=(0, 0), esc=lambda t: max(.001, muelle((t - _tel) / .5)) * .85, ini=_tel, fin=TC['e'] + .02, liso=True, op=lambda t: .7))
_r = np.random.default_rng(31)
for i in range(26):
    x, y0, dl = _r.uniform(-520, 520), _r.uniform(-500, 300), _r.uniform(0, 1.8)
    ta = _tel + dl * .6
    S['D'].append(Capa(_mo, lambda t, a=x, b=y0, q=ta: (sd[0] + a + 14 * math.sin((t - q) * 2), sd[1] + b + 90 * (t - q), sd[2] - 100), res=1, ini=ta, fin=TC['e'] + .02, esc=_r.uniform(.7, 1.9), liso=True, op=lambda t, q=ta: .7 * cl((t - q) / .3)))
_tfig = INI[8] - .03
S['D'].append(Capa(SO, (sd[0] - 230, sd[1] + 590, sd[2] - 60), res=2, ini=_tfig, fin=TC['e'] + .02, esc=pop(_tfig, .3, .78), rot=lambda t: 1.3 * math.sin(t * 1.8)))
bl('D', [lin(66, [('si tus redes sociales y tu web', T(7, 0))], 0, (246, 236, 214)), lin(102, [('están descuidadas', T(7, 6))], 1, (250, 204, 90))], sd, -620, TC['d'], INI[8] - .03, dy=26)
bl('D', [lin(66, [('el cliente piensa que', T(8, 0))], 0, (246, 236, 214)), lin(100, [('tu servicio también', T(8, 4))], 1, (250, 204, 90))], sd, -620, INI[8] - .03, TC['e'] + .02, dy=26)

# ===== E: silencio. Me llamo …: la foto se abre
se = rest(LF[0] - .01)
_tm = T(9, 2) - .1
S['E'] += letras('me llamo', 96, se, 0, -640, T(9, 0), paso=.03, ini=TC['e'], fin=TC['f'] + .02)
S['E'] += letras(NOMBRE.upper() if len(NOMBRE) < 8 else NOMBRE.split()[0], 240, se, 0, -470, T(9, 2) - .04, paso=.05, ini=TC['e'], fin=TC['f'] + .02)
S['E'].append(FotoMorf(_chr, (se[0], se[1] + 240, se[2]), T(9, 0) - .02, _tm + .12, 200, 800, 880, fin=TC['f'] + .02))
_d_ = destello(col=(255, 245, 225))
S['E'].append(Capa(_d_, (se[0] + 230, se[1] - 170, se[2] - 40), res=1, ini=_tm + .1, fin=_tm + .55, liso=True, esc=lambda t: 1.2 * cl(1 - abs(t - _tm - .3) / .22) + .01))
S['E'].append(Capa(sprite_txt('charla en tu ciudad', 38, 0, (210, 210, 210)), (se[0], se[1] + 700, se[2]), res=2, ini=_tm + .4, fin=TC['f'] + .02, op=lambda t: cl((t - _tm - .4) / .2)))

# ===== F: cuatro años por una carretera que sube hasta la bandera
sf = rest(LF[1] - .36)
sf2 = rest(LG[0] - .01)
_cr = carretera_p()
_ry0 = sf[1] + 240
S['F'].append(Capa(_cr, (sf[0], _ry0 + 120, sf[2]), res=1, ini=TC['f'], fin=TC['g'] + .02, esc=1.0, liso=True))
_ban = bandera()
_rc = _ry0 + 120              # centro del dibujo de la carretera
def _road(v): return (sf[0] + 430 * math.sin(v * 8.2) * (1 - v * .7), _rc + 1000 - 2000 * v)
_bx, _by = _road(.985)
S['F'].append(Capa(_ban, (_bx + 8, _by + 26, sf[2] - 20), res=2, ini=TC['f'], fin=TC['g'] + .02, esc=pop(T(10, 11), .3, .9), ancla=(13, 240)))
for v, tx, ta in ((.14, 'año 1', T(10, 1)), (.4, 'año 2', T(10, 3)), (.63, 'año 3', T(10, 5)), (.84, 'año 4', T(10, 7))):
    mx, my = _road(v)
    S['F'].append(Capa(marcador(tx), (mx, my, sf[2] - 30), res=2, ini=ta, fin=TC['g'] + .02, esc=pop(ta, .22, 1.0)))
_pin = lienzo(84, 84); ImageDraw.Draw(_pin).ellipse((0, 0, 84 * R_ - 1, 84 * R_ - 1), fill=(255, 255, 255, 255)); ImageDraw.Draw(_pin).ellipse((14 * R_, 14 * R_, 70 * R_, 70 * R_), fill=ROJO + (255,))
_vr = lambda t: .03 + .95 * cb(.4, .1, .5, 1)(cl((t - T(10, 0)) / (T(10, 11) - T(10, 0))))
for q_ in (.05, .035, .02, 0):
    S['F'].append(Capa(_pin, lambda t, q=q_: (_road(max(0, _vr(t) - q))[0], _road(max(0, _vr(t) - q))[1], sf[2] - 40), res=2, ini=TC['f'], fin=TC['g'] + .02, esc=1 - q_ * 9, op=lambda t, q=q_: 1 - q * 14))
_pf = plaza(960, 400, GRIS, rr=40)
S['F'].append(Capa(_pf, lambda t: (cam(t)[0], cam(t)[1] - 545, cam(t)[2]), res=2, ini=TC['f'], fin=TC['g'] + .02, op=lambda t: .96))
S['F'].append(Capa(sprite_txt('más de 4 años', 130, 1, TINTA), lambda t: (cam(t)[0], cam(t)[1] - 640, cam(t)[2]), res=2, ini=T(10, 1), fin=TC['g'] + .02, op=lambda t: cl((t - T(10, 1)) / .14)))
S['F'].append(Capa(sprite_txt('marketing digital', 76, 0, TINTA), lambda t: (cam(t)[0], cam(t)[1] - 515, cam(t)[2]), res=2, ini=T(10, 6), fin=TC['g'] + .02, op=lambda t: cl((t - T(10, 6)) / .14)))
S['F'].append(Capa(sprite_txt('para negocios de ' + REGION, 62, 0, TINTA), lambda t: (cam(t)[0], cam(t)[1] - 430, cam(t)[2]), res=2, ini=T(10, 8), fin=TC['g'] + .02, op=lambda t: cl((t - T(10, 8)) / .14)))

# ===== G: oficina, sin equipo y como si fueran míos: esferas que se funden
sg = rest(LH[0] - .01)
_tof = T(11, 1)
class FotoPan:
    # La oficina de verdad a pantalla completa: se abre en círculo y la cámara recorre la sala.
    def __init__(s):
        s.f = [Image.open('fotos/sitio2.jpg').convert('RGB'), Image.open('fotos/sitio1.jpg').convert('RGB')]
        g = np.ones((H, 1), np.float32); y_ = np.arange(H, dtype=np.float32)
        g[:, 0] = 1 - .42 * np.exp(-(y_ / 460) ** 2) - .62 * np.exp(-((H - y_) / 640) ** 2)
        s.os = Image.fromarray((g * 255).astype(np.uint8)).resize((W, H))
    def dibuja(s, lz, t, c):
        if not (_tof - .04 <= t < INI[12] - .03): return
        two = t >= _tswap
        im = s.f[1 if two else 0]
        u = cl((t - (_tswap if two else _tof - .04)) / ((INI[12] - _tswap) if two else (_tswap - _tof + .04)))
        z_ = 1.05 + .14 * u
        e = im.height / H / z_
        x0 = (1420 + 240 * u if two else 620 + 380 * u) + c[0] * .15
        y0 = (im.height - H * e) / 2 + (c[1] - sg[1]) * .1
        f = im.transform((W, H), Image.AFFINE, (e, 0, x0, 0, e, y0), Image.BILINEAR)
        f = ImageChops.multiply(f, Image.merge('RGB', (s.os, s.os, s.os)))
        r = 1250 * muelle((t - _tof + .04) / .5)
        if r < 1200:
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
            lz.paste(f, (0, 0), m)
        else:
            lz.paste(f, (0, 0))
_tswap = T(11, 3) - .02
S['G'].append(FotoPan())
pildora_txt(S['G'], (sg[0], sg[1] - 540, sg[2]), _tof, 760, 140, AZUL, 'oficina en ' + REGION, 72, fin=INI[12] - .03, ini=TC['g'])
_tse = T(11, 4)
for i in range(5):
    x = (i - 2) * 200
    S['G'].append(Capa(SO, (sg[0] + x, sg[1] + 700, sg[2] + 30), res=2, ini=TC['g'], fin=INI[12] - .03, esc=.3, op=lambda t, g=i: 1 if g == 2 else 1 - cl((t - _tse - abs(g - 2) * .06) / .2)))
S['G'].append(Capa(sprite_txt(PUEBLO, 50, 0, BLA), (sg[0], sg[1] - 430, sg[2]), res=2, ini=_tof + .25, fin=INI[12] - .03, op=lambda t: cl((t - _tof - .25) / .14)))
bl('G', [lin(160, [('sin equipo', _tse)], 1, BLA)], sg, 330, TC['g'], INI[12] - .03, durw=.1)
_tu = T(12, 6)
UNE = cb(.6, 0, .2, 1)
_orb = ((-240, -20, 0), (240, -20, 1), (-240, 400, 2), (240, 400, 3))
_ord = [T(12, 0) + i * .22 for i in range(4)]
def _bolas(t):
    u = UNE(cl((t - _tu) / .6))
    return [(sg[0] + x * (1 - u), sg[1] + 190 + (y - 190) * (1 - u), sg[2], 112 * ENT(cl((t - _ord[i]) / .24)) * (1 + u * .3)) for x, y, i in _orb]
S['G'].append(Liquido(_bolas, ini=INI[12] - .04, fin=TC['h'] + .02))
for (x, y, i), w_ in zip(_orb, ('web', 'redes', 'anuncios', 'google')):
    S['G'].extend(bloque([lin(58, [(w_, _ord[i])], 1, BLA)], sg, cx=x, cy=y + 160, ini=INI[12] - .04, fin=_tu + .1, dy=18))
_tfm = T(12, 9) - .02
S['G'].append(FotoMorf(_chr, (sg[0], sg[1] + 190, sg[2]), _tfm, 1e9, 215, 430, 430, fin=TC['h'] + .02))
bl('G', [lin(66, [('trabajando el marketing', T(12, 0))], 0, BLA), lin(106, [('como si fueran', T(12, 6))], 1, BLA), lin(190, [('míos', T(12, 9))], 1, (116, 176, 255))], sg, -540, INI[12] - .03, TC['h'] + .02, interlin=1.0)

# ===== H: la prueba: la cuadrícula de negocios
sh = rest(LI[0] - .01)
S['H'].append(Capa(_rej, (sh[0], sh[1] + 200, sh[2]), res=1, liso=True, ini=TC['h'], fin=TC['i'] + .02))
_or = np.random.default_rng(6).permutation(54)
for n, i in enumerate(_or):
    x, y = (i % 6 - 2.5) * 148, -190 + (i // 6) * 182
    ta = INI[13] + .1 + n * (FIN[13] - INI[13] - .3) / 54
    S['H'].append(Capa(_mw[int(i) % 6], (sh[0] + x, sh[1] + y, sh[2]), res=2, ini=TC['h'], fin=TC['i'] + .02, esc=pop(ta, .2, 1.0)))
for k in range(31):
    a = T(13, 2) + (FIN[13] - T(13, 2)) * k / 30
    b = T(13, 2) + (FIN[13] - T(13, 2)) * (k + 1) / 30 if k < 30 else TC['i'] + .02
    S['H'].append(Capa(sprite_txt(f'+{k * 10}', 230, 1, TINTA), (sh[0], sh[1] - 560, sh[2]), res=2, ini=a, fin=b))
S['H'].append(Capa(sprite_txt('negocios', 80, 0, TINTA), (sh[0], sh[1] - 410, sh[2]), res=2, ini=T(13, 7), fin=TC['i'] + .02, op=lambda t: cl((t - T(13, 7)) / .14)))

# ===== I: 25 años y una promesa: casi a oscuras, con latido
si = rest(LJ[0] - .01)
_m25 = txt_metal('25', 600)
S['I'].append(Capa(_m25, (si[0], si[1] - 130, si[2]), res=2, ini=TC['i'], fin=TC['j'] + .02, esc=lambda t: 1 + .1 * cl((t - T(14, 2)) / 2.6) + 2.6 * (1 - cb(.1, .85, .2, 1)(cl((t - T(14, 2)) / .17))), op=lambda t: cl((t - T(14, 2) + .02) / .05)))
S['I'].append(Capa(sprite_txt('años', 110, 0, BLA), (si[0], si[1] + 230, si[2]), res=2, ini=T(14, 3), fin=TC['j'] + .02, op=lambda t: cl((t - T(14, 3)) / .14)))
bl('I', [lin(78, [('me he prometido', T(14, 4))], 0, BLA), lin(146, [('una cosa', T(14, 7))], 1, (250, 204, 90))], si, 470, TC['i'], TC['j'] + .02)

# ===== J: el golpe. La tienda se llena
sj = rest(LK[0] - .01)
S['J'].append(Capa(_rej, (sj[0], sj[1] + 80, sj[2]), res=1, liso=True, ini=TC['j'], fin=TC['k'] + .02, esc=1.3))
S['J'].append(Capa(_tn, (sj[0], sj[1] + 220, sj[2]), res=2, ini=TC['j'], fin=TC['k'] + .02, esc=.92))
_y2 = sj[1] + 220 + 322
S['J'].append(Capa(calle(), (sj[0], _y2, sj[2]), res=2, ini=TC['j'], fin=TC['k'] + .02))
for i in range(30):
    ta = TC['j'] + .15 + i * .085
    lado = -1 if i % 2 else 1
    def _pj(t, a=ta, l=lado, g=i):
        u = cl((t - a) / 1.05)
        return (sj[0] + l * 740 * (1 - u), _y2 - 72 - abs(math.sin((t - a) * 11 + g)) * 13, sj[2] - 30)
    S['J'].append(Capa(_pn, _pj, res=2, ini=ta, fin=ta + 1.07, esc=.48, rot=lambda t, a=ta, g=i: 5 * math.sin((t - a) * 11 + g)))
bl('J', [lin(70, [('ayudar a los negocios', T(15, 0))], 0), lin(112, [('a conseguir', T(15, 4))], 1), lin(150, [('más clientes', T(15, 6))], 1, VERDEW)], sj, -560, TC['j'], TC['k'] + .02, interlin=1.04)

# ===== K: la promesa: gris Apple, píldoras con su tic y estrellas
sk = rest(LL[0] - .01)
_fil = [('sin ampliar el equipo', T(16, 1), AZUL), ('ni el volumen', T(16, 5), (20, 20, 22)), ('sin empeorar el servicio', T(17, 2), VERDEW)]
for i, (tx, ta, col) in enumerate(_fil):
    y = -330 + i * 230
    pildora_txt(S['K'], (sk[0], sk[1] + y, sk[2]), ta - .04, 800, 170, col, tx, 66, fin=TC['l'] + .02, ini=max(TC['k'], ta - .1))
_es = estrella_oro()
for i in range(5):
    ta = T(17, 4) + i * .08
    S['K'].append(Capa(_es, (sk[0] + (i - 2) * 150, sk[1] + 400, sk[2]), res=2, ini=TC['k'], fin=TC['l'] + .02, esc=lambda t, a=ta: max(.001, muelle((t - a) / .4))))
S['K'].append(Capa(sprite_txt('5,0 en Google · 25 opiniones', 58, 1, TINTA), (sk[0], sk[1] + 510, sk[2]), res=2, ini=T(17, 4) + .3, fin=TC['l'] + .02, op=lambda t: cl((t - T(17, 4) - .3) / .14), dxy=lambda t: (0, 20 * (1 - cl((t - T(17, 4) - .3) / .2)))))

# ===== L: flecha que se abre en botón y chat que se llena
sl = rest(DUR)
_ty = T(18, 4)
S['L'].append(Movil3D(pant_chat, (sl[0], sl[1] - 40, sl[2]), lambda t: max(.02, muelle((t - TC['l'] - .05) / .55)) * .82, lambda t: 58 * math.exp(-3.4 * max(0, t - TC['l'])) + 8 * math.sin(t * 1.15), lambda t: 5 + 3 * math.sin(t * .85), lambda t: 1.2 * math.sin(t * .6), ini=TC['l'], sombra=.6))
S['L'].extend(bloque([lin(72, [('haz clic abajo', T(18, 0))], 0, BLA), lin(120, [('y escríbeme', T(18, 4))], 1, BLA)], sl, cy=-640, ini=TC['l'], interlin=1.06))
_tb = T(18, 8)
pildora_txt(S['L'], (sl[0], sl[1] + 400, sl[2]), T(18, 7), 840, 170, VERDEW, 'mi WhatsApp personal', 76, tb=_tb)
_fl = lienzo(120, 140)
ImageDraw.Draw(_fl).polygon(pp([(40, 0), (80, 0), (80, 80), (118, 80), (60, 138), (2, 80), (40, 80)]), fill=(255, 255, 255, 255))
S['L'].append(Capa(_fl, lambda t: (sl[0], sl[1] + 560 + 18 * math.sin(t * 9), sl[2]), res=2, ini=T(18, 1), esc=pop(T(18, 1), .24, .8)))

# palabra gigante detrás, desenfocada, para que cada fondo tenga profundidad
def gigante(k, txt, s_, col, idx=0, dy=-120, v=-70, t0=0):
    sp = sprite_txt(txt, 620, 1, col, res=1).filter(ImageFilter.GaussianBlur(3))
    S[k].insert(idx, Capa(sp, (s_[0], s_[1] + dy, s_[2] + 420), res=1, liso=True, dxy=lambda t: (360 + v * (t - t0), 0)))
_gr, _cr_ = (224, 224, 229), (232, 224, 208)
for k_, tx_, s_, c_, i_, t_ in (('A', REGION.upper(), sa, _gr, 0, 0), ('B', 'MEJOR', sb, _gr, 0, 6), ('C2', 'IGUAL', sc0, (36, 36, 40), 0, 11), ('C', 'INVISIBLE', sc2, _cr_, 0, 15), ('D', 'DESCUIDADO', sd, (44, 26, 14), 1, 21),
                                ('F', '4 AÑOS', sf, _gr, 0, 29), ('G', 'COMO MÍOS', sg, (32, 34, 44), 0, 34), ('H', '+300', sh, _cr_, 0, 39), ('J', 'CLIENTES', sj, _cr_, 0, 44), ('K', 'PROMESA', sk, _gr, 0, 48), ('L', 'WHATSAPP', sl, (34, 34, 38), 0, 52)):
    gigante(k_, tx_, s_, c_, i_, t0=t_)

ESC = [(-1, TC['z'], 'Z', Image.new('RGBA', (W, H), (6, 8, 16, 255))), (TC['z'], TC['a'], 'A', GRISB), (TC['a'], TC['b'], 'B', GRISB), (TC['b'], TC['c'], 'C2', OSCURO), (TC['c'], TC['d'], 'C', CLARO), (TC['d'], TC['e'], 'D', SALA),
       (TC['e'], TC['f'], 'E', OSCURO), (TC['f'], TC['g'], 'F', GRISB), (TC['g'], TC['h'], 'G', OSCURO), (TC['h'], TC['i'], 'H', CLARO), (TC['i'], TC['j'], 'I', OSCURO),
       (TC['j'], TC['k'], 'J', CLARO), (TC['k'], TC['l'], 'K', GRISB), (TC['l'], 1e9, 'L', OSCURO)]


# ---------- capa de efectos: lo que hace que parezca una película
OSCURAS = {'Z', 'C2', 'D', 'E', 'G', 'I', 'L'}
def _disco(r, col, op):
    p = 40
    im = Image.new('RGBA', (2 * r + 2 * p, 2 * r + 2 * p), col + (0,))
    a_ = Image.new('L', im.size, 0); ImageDraw.Draw(a_).ellipse((p, p, p + 2 * r, p + 2 * r), fill=int(255 * op))
    im.putalpha(a_.filter(ImageFilter.GaussianBlur(r * .16 + 3)))
    return im
_rb = np.random.default_rng(12)
_BOK = [(float(_rb.uniform(0, 1400)), float(_rb.uniform(0, 2300)), float(_rb.uniform(1.1, 2.6)), int(_rb.integers(34, 130))) for _ in range(9)]
_BOSC = [_disco(r, (255, 226, 180), .13) for *_, r in _BOK]
_BCLA = [_disco(r, (255, 255, 255), .34) for *_, r in _BOK]
def bokeh(lz, t, c, k):
    # motas fuera de foco en primer término: con el paralaje se nota el 3D
    sp = _BOSC if k in OSCURAS else _BCLA
    for (x, y, par, r), im in zip(_BOK, sp):
        px = (x - c[0] * par + 40 * math.sin(t * .4 + x)) % 1400 - 160 - r
        py = (y - c[1] * par - 22 * t * par) % 2300 - 190 - r
        pega(lz, im, int(px), int(py))


def escena(t):
    c = cam(t)
    for a, b, k, base in ESC:
        if a <= t < b:
            lz = base.copy()
            for q in S[k]: q.dibuja(lz, t, c)
            bokeh(lz, t, c, k)
            return lz.convert('RGB')


_IRIS = cb(.5, 0, .2, 1)
FX = []       # (t0, tipo, x, y, col, fuerza)
_rg = np.random.default_rng(77)
_CH = _rg.uniform(0, 6.283, 90), _rg.uniform(.25, 1, 90), _rg.uniform(.55, 1, 90)
def efectos(im, t):
    d = ImageDraw.Draw(im)
    for t0, tipo, x, y, col, a in FX:
        u = t - t0
        if tipo == 'onda' and 0 <= u < .6:
            r = (450 if a < .5 else 90) + 900 * a * (1 - (1 - u / .6) ** 3); q = (1 - u / .6) ** 2
            bl_ = tuple(int(255 * .0 + c_ * q + (im.getpixel((min(1079, max(0, int(x))), min(1919, max(0, int(y)))))[j]) * (1 - q)) for j, c_ in enumerate(col))
            d.ellipse((x - r, y - r, x + r, y + r), outline=bl_, width=max(2, int(16 * q)))
        if tipo == 'chispas' and 0 <= u < .85:
            for an, vel, vid in zip(*_CH):
                if u > vid * .85: continue
                dist = 1250 * a * vel * (1 - math.exp(-3.4 * u)) / 3.4 * 3
                px, py = x + dist * math.cos(an), y + dist * math.sin(an) + 260 * u * u
                l_ = 46 * vel * a * math.exp(-3.4 * u) + 3
                d.line((px, py, px - l_ * math.cos(an), py - l_ * math.sin(an)), fill=col, width=3 if vel > .6 else 2)


def dibuja(t):
    tc = next((p for p in PORT if p - .1 <= t < p + .17), None)
    if tc is not None:
        im = escena(min(t, tc - .002))
        nu = escena(max(t, tc + .002))
        r = 1180 * _IRIS((t - tc + .1) / .27)
        m = Image.new('L', (W, H), 0)
        ImageDraw.Draw(m).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
        im.paste(nu, (0, 0), m.filter(ImageFilter.GaussianBlur(4)))
    else:
        im = escena(t)
    efectos(im, t)
    g = giro(t)
    if abs(g) > .05:
        th = math.radians(g)
        z = abs(math.cos(th)) + (H / W) * abs(math.sin(th)) + .01
        ca, sa_ = math.cos(th) / z, math.sin(th) / z
        im = im.transform((W, H), Image.AFFINE, (ca, -sa_, W / 2 - ca * W / 2 + sa_ * H / 2, sa_, ca, H / 2 - sa_ * W / 2 - ca * H / 2), Image.BILINEAR)
    r = desenfoque(t)
    if r > .4: im = im.filter(ImageFilter.GaussianBlur(r))
    return im


_yy2, _xx2 = np.mgrid[0:H, 0:W].astype(np.float32)
_LEAK = np.exp(-(((_xx2 - W * .8) / (W * .65)) ** 2 + ((_yy2 - H * .3) / (H * .5)) ** 2))[..., None] * np.array((255, 170, 90), np.float32)
CORTES = tuple(TC.values())


_ys_, _xs_ = np.mgrid[0:240, 0:135].astype(np.float32)
FLASH = []
def _sube(a): return np.asarray(Image.fromarray(a.clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
def post(im, t):
    k = next((q for a, b, q, _ in ESC if a <= t < b), 'L')
    if k in OSCURAS:
        s_ = Image.fromarray(im.astype(np.uint8)).resize((270, 480), Image.BILINEAR).point(lambda v: max(0, v - 195) * 2.6)
        bl_ = np.asarray(s_.filter(ImageFilter.GaussianBlur(13)), np.float32)       # el brillo se abre
        pq = s_.resize((135, 240), Image.BILINEAR).filter(ImageFilter.GaussianBlur(2.2))
        cx, cy = 67 + 14 * math.sin(t * .7), 42 + 10 * math.sin(t * .5)
        ra = np.zeros((240, 135, 3), np.float32)
        for i_ in range(1, 13):                                                    # rayos de luz que salen de lo brillante
            z = 1 + i_ * .055
            ra += np.asarray(pq.transform((135, 240), Image.AFFINE, (1 / z, 0, cx * (1 - 1 / z), 0, 1 / z, cy * (1 - 1 / z)), Image.BILINEAR), np.float32) * (1 - i_ / 13)
        ra = np.asarray(Image.fromarray((ra * .1).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.5)), np.float32)
        ad = _sube(bl_) * .3 + _sube(ra) * .8
        im = 255 - (255 - im) * (255 - ad.clip(0, 250)) / 255
    else:
        # luz suave que barre el fondo
        lx, ly = 67 + 60 * math.sin(t * .63), 120 + 110 * math.sin(t * .41 + 1)
        m_ = np.exp(-(((_xs_ - lx) / 62) ** 2 + ((_ys_ - ly) / 110) ** 2))
        im = im * (.925 + .085 * _sube(m_[..., None].repeat(3, 2) * 255) / 255)
    if k == 'D':     # parpadea la luz de la sala
        fl = 1.
        for tf_ in (T(7, 7), T(7, 7) + .14, T(8, 0) + .05, T(8, 4), T(8, 4) + .1):
            fl = min(fl, 1 - .5 * cl(1 - abs(t - tf_) / .05))
        im = im * fl
    for t0, a in FLASH:
        if 0 <= t - t0 < .4: im = im + 255 * a * math.exp(-11 * (t - t0))
    return im


def fotograma(i):
    t = i / FPS
    a, b = cam(t), cam(t + OBT / FPS)
    v = math.hypot(a[0] - b[0], a[1] - b[1]) + abs(a[2] - b[2]) * .5
    if any(L[0] <= t < L[1] for L in (LE, LG, LK)): v = v * 2 + 10
    n = int(max(3, min(26, math.ceil(v / 4) + 1)))
    if any(p - .45 <= t < p + .3 for p in PORT): n = min(n, 10)
    suma = None
    for j in range(n):
        q = np.asarray(dibuja(t + (j + .5) / n * OBT / FPS), np.uint16)
        suma = q if suma is None else suma + q
    im = aberracion((suma / n).astype(np.uint8)).astype(np.float32)
    im = post(im, t)
    k = max(0., 1 - min(abs(t - c) for c in CORTES) / .13)
    if k > 0: im = 255 - (255 - im) * (1 - _LEAK * k * .0026)
    return im.clip(0, 255).astype(np.uint8)


# ---------- golpes, chispas, ondas y flashes (también mandan en la mezcla)
_tland = _tflip + .5
BEATS.extend([(_tmap, 1.3), (T(0, 4), .8), (_tcl, .7), (_tland, 1.3), (T(2, 1), 1.0), (T(3, 3), .55), (T(3, 5), .55), (T(3, 7), .55), (_tnota[0], .55), (_tnota[1], .55), (_tnota[2], .55),
              (T(5, 8), 1.3), (T(6, 3), .5), (T(6, 7), 1.0), (T(7, 6), 1.0), (T(7, 7), .8), (T(8, 4), 1.1), (T(9, 2), 1.4), (T(10, 1), 1.0), (T(10, 11), .9), (T(11, 1), .5), (T(11, 4), 1.5),
              (_tu, .8), (_tfm, 1.4), (T(13, 2), .5), (T(13, 7), 1.4), (T(14, 2), 2.0), (T(14, 7), 1.0), (TC['j'] + .02, 2.3), (T(15, 6), 1.5), (T(16, 1), .7), (T(16, 5), .7), (T(17, 2), .8), (T(17, 4), .5), (T(18, 4), .7), (T(18, 8), 1.3)])
_DOR, _BL_ = (255, 205, 90), (255, 255, 255)
for t_, x_, y_, c_, a_ in ((_tmap, 540, 1050, _DOR, 1.), (_tland, 540, 1190, _DOR, 1.), (T(9, 2), 540, 1190, _DOR, .7), (T(10, 11), 540, 340, ROJO, .6), (_tfm, 540, 1150, (120, 190, 255), 1.), (T(13, 7), 540, 420, AZUL, .8), (T(14, 2), 540, 830, _DOR, 1.2), (TC['j'] + .02, 540, 960, VERDEW, 1.2), (T(15, 6), 540, 460, VERDEW, 1.), (T(17, 4), 540, 1390, _DOR, .7), (T(18, 8), 540, 1360, VERDEW, .8)):
    FX.append((t_, 'chispas', x_, y_, c_, a_))
    FX.append((t_, 'onda', x_, y_, c_, min(a_, 1.)))
FLASH.extend([(_tmap, .2), (T(9, 2), .25), (T(14, 2), .45), (TC['j'], .7), (_tland, .12), (_tfm, .22)])

if __name__ == '__main__':
    NF = int(round(DUR * FPS))
    json.dump({'TC': TC, 'P': INI, 'F': FIN, 'dur': DUR, 'T': {f'{i}_{j}': T(i, j) for i in range(len(P)) for j in range(len(P[i]['pal']))},
               'tnota': list(_tnota), 'ord': _ord, 'tu': _tu, 'tfm': _tfm, 'tm': _tm, 'tcl': _tcl, 'tflip': _tflip, 'tland': _tland, 'beats': BEATS, 'port': PORT, 'tmap': _tmap, 'tswap': _tswap, 'tof': _tof}, open('cortes.json', 'w'))
    print(f'dur {DUR} nf {NF} cortes ' + ' '.join(f'{k}{v:.2f}' for k, v in TC.items()), file=sys.stderr)
    if sys.argv[1] == 'hoja':
        ts = [float(x) for x in sys.argv[2].split(',')]
        cols = int(sys.argv[4]) if len(sys.argv) > 4 else 8
        tw, th = 270, 480
        rows = math.ceil(len(ts) / cols)
        Sh = Image.new('RGB', (cols * tw, rows * th), (70, 70, 70))
        dr = ImageDraw.Draw(Sh)
        import time
        t0 = time.time()
        for k, t in enumerate(ts):
            f = Image.fromarray(fotograma(int(round(t * FPS)))).resize((tw - 4, th - 4), Image.LANCZOS)
            Sh.paste(f, ((k % cols) * tw + 2, (k // cols) * th + 2))
            dr.text(((k % cols) * tw + 8, (k // cols) * th + 8), f'{t:.2f}', fill=(255, 0, 200))
        Sh.save(sys.argv[3], quality=85)
        print(f'{(time.time() - t0) / len(ts):.2f} s/fot', file=sys.stderr)
    else:
        carp = sys.argv[2]
        os.makedirs(carp, exist_ok=True)
        for i in range(NF):
            p = f'{carp}/{i:05d}.png'
            if os.path.exists(p): continue
            Image.fromarray(fotograma(i)).save(p + '.tmp.png', compress_level=1)
            os.rename(p + '.tmp.png', p)
            if i % 60 == 0: print(i, NF, flush=True)
