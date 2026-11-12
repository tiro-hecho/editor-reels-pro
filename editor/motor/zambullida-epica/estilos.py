# Piezas de los estilos Earn Edits y Alborná (salen de como-si-fuese-mia/mia.py).
import json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mc import *
from obj import *

RND = np.random.default_rng(7)
def grano(tam, fuerza): return RND.normal(0, fuerza, tam)
_yq, _xq = np.mgrid[0:H // 2, 0:W // 2].astype(np.float32)


def pared():
    w, h = 1600, 2600
    base = np.zeros((h, w, 3), np.float32)
    ruido = RND.normal(0, 1, (h, w // 4)).astype(np.float32)
    ruido = np.asarray(Image.fromarray(((ruido + 3) * 40).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5)), np.float32) / 255 - .5
    plancha = 150
    x = np.arange(w)
    tonos = RND.uniform(.86, 1.1, w // plancha + 2)[x // plancha]
    jun = 1 - .55 * np.exp(-(((x % plancha) - plancha / 2) / 2.2) ** 2 * 0 - ((x % plancha) / 2.5) ** 2)
    v = (tonos * jun)[None, :] * (1 + ruido * .55)
    for i, c in enumerate((104, 62, 34)): base[..., i] = v * c
    # zócalo
    y0 = int(h * .73)
    base[y0:] *= .62
    base[y0 - 8:y0 + 8] *= .35
    base[y0 + 8:y0 + 26] *= 1.5
    # luz de foco arriba y caída a los lados
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    foco = np.exp(-(((xs - w / 2) / (w * .36)) ** 2 + ((ys - h * .42) / (h * .36)) ** 2))
    base *= (.3 + 1.05 * foco)[..., None]
    base += grano(base.shape, 3.5)
    im = Image.fromarray(base.clip(0, 255).astype(np.uint8)).convert('RGBA')
    return im.filter(ImageFilter.GaussianBlur(1.6))


def corazon_pts(cx, cy, s):
    pts = []
    for u in np.linspace(0, 2 * math.pi, 90):
        x = 16 * math.sin(u) ** 3
        y = -(13 * math.cos(u) - 5 * math.cos(2 * u) - 2 * math.cos(3 * u) - math.cos(4 * u))
        pts.append((cx + x * s, cy + y * s))
    return pts


def txt_metal(txt, tam, claro=False):
    """Letra metálica con degradado por altura: el «faux metallic» del tutorial."""
    s = sprite_txt(txt, tam, 1, (255, 255, 255))
    h = s.height
    ys = np.linspace(0, 1, h)
    if claro:
        col = np.array((255, 248, 226))[None, :] * np.ones((h, 1))
    else:
        col = np.stack([np.interp(ys, (0, .34, .5, .62, 1), (a, b, c, d, e)) for a, b, c, d, e in zip((255, 250, 210), (216, 172, 92), (132, 86, 36), (250, 224, 150), (176, 124, 56))], 1)
    a = np.array(s)
    a[..., :3] = col[:, None, :].astype(np.uint8)
    return Image.fromarray(a, 'RGBA')


def marco(w, h):
    im = lienzo(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w * R_, h * R_), fill=(112, 76, 34, 255))
    d.rectangle((16 * R_, 16 * R_, (w - 16) * R_, (h - 16) * R_), fill=(204, 160, 84, 255))
    d.rectangle((30 * R_, 30 * R_, (w - 30) * R_, (h - 30) * R_), fill=(86, 54, 24, 255))
    d.rectangle((44 * R_, 44 * R_, (w - 44) * R_, (h - 44) * R_), fill=(16, 14, 14, 255))
    return im


def red_luz(R=330, res=1.5):
    t = int((2 * R + 8) * res)
    c = t / 2
    r = np.random.default_rng(11)
    ang, rad = r.uniform(0, 2 * math.pi, 120), R * res * .96 * np.sqrt(r.uniform(0, 1, 120))
    pts = np.stack([c + rad * np.cos(ang), c + rad * np.sin(ang)], 1)
    im = Image.new('L', (t, t), 0)
    d = ImageDraw.Draw(im)
    for i in range(len(pts)):
        ds = np.hypot(*(pts - pts[i]).T)
        for j in np.argsort(ds)[1:4]:
            d.line((*pts[i], *pts[j]), fill=190, width=2)
    for x, y in pts:
        q = r.uniform(3, 7)
        d.ellipse((x - q, y - q, x + q, y + q), fill=255)
    glow = np.asarray(im.filter(ImageFilter.GaussianBlur(9)), np.float32) / 255
    nit = np.asarray(im, np.float32) / 255
    v = np.clip(nit + glow * 1.2, 0, 1)
    # fondo azul de disco con borde
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    dd = np.hypot(xs - c, ys - c)
    disco = np.clip(R * res - dd + .5, 0, 1)
    azul = .22 + .28 * (1 - dd / (R * res))
    rgb = np.dstack([(v * 150 + azul * 12), (v * 215 + azul * 70), (v * 255 + azul * 200)])
    out = np.dstack([rgb.clip(0, 255), disco * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def mitad(im, lado):
    a = np.array(im)
    w = a.shape[1]
    if lado == 'der': a[:, :w // 2, 3] = 0
    else: a[:, w // 2:, 3] = 0
    return Image.fromarray(a, 'RGBA')


def foto_circulo():
    im = Image.open('foto_circulo.png')  # foto de la persona, cuadrada de 400 px.convert('RGB')
    # sin el aro de Instagram: círculo interior
    c = 200; r = 176
    im = im.crop((c - r, c - r, c + r, c + r)).resize((r * 4, r * 4), Image.LANCZOS)
    t = r * 4
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    dd = np.hypot(xs - t / 2, ys - t / 2)
    al = np.clip(t / 2 - dd + .5, 0, 1) * 255
    a = np.dstack([np.asarray(im), al]).astype(np.uint8)
    out = Image.fromarray(a, 'RGBA')
    d = ImageDraw.Draw(out)
    d.ellipse((5, 5, t - 5, t - 5), outline=(255, 255, 255, 255), width=14)
    return out


class Liquido:
    def __init__(s, bolas, ini=-1, fin=1e9):
        s.bolas, s.ini, s.fin = bolas, ini, fin

    def dibuja(s, lienzo_, t, c):
        if not (s.ini <= t < s.fin): return
        f = np.zeros((H // 2, W // 2), np.float32)
        brillo = np.zeros_like(f)
        for x, y, z, r in s.bolas(t):
            prof = z - c[2] + ZOOM
            if prof < 40 or r < .5: continue
            k = ZOOM / prof
            sx = (W / 2 + (x - c[0]) * k) / 2; sy = (H / 2 + (y - c[1]) * k) / 2
            rr = r * k / 2
            d2 = (_xq - sx) ** 2 + (_yq - sy) ** 2 + 1
            f += rr * rr / d2
            brillo += np.exp(-((_xq - sx + rr * .34) ** 2 + (_yq - sy + rr * .38) ** 2) / (rr * rr * .16))
        dentro = np.clip((f - .96) / .08, 0, 1)
        h = np.sqrt(np.clip(1 - 1 / np.maximum(f, 1e-3), 0, 1))
        col = np.zeros(f.shape + (3,), np.float32)
        for i, (a, b) in enumerate(((16, 196), (84, 236), (214, 255))):
            col[..., i] = a + (b - a) * h ** 1.25
        col += brillo[..., None] * 75
        halo = np.clip(f, 0, 1) ** 1.6 * .62
        al = np.maximum(dentro, halo)
        rgb = np.where(dentro[..., None] > .01, col, np.array((46, 130, 255), np.float32))
        im = Image.fromarray(np.dstack([rgb, al * 255]).clip(0, 255).astype(np.uint8), 'RGBA').resize((W, H), Image.BILINEAR)
        lienzo_.alpha_composite(im)


def letras(txt, tam, origen, cx, cy, t0, paso=.022, peso=1, color=(255, 255, 255), ini=-1, fin=1e9):
    capas = []
    f = F(tam, peso)
    tot = ancho(txt, tam, peso)
    x0 = cx - tot / 2
    S = cb(.3, 0, .15, 1)
    for i, ch in enumerate(txt):
        if ch == ' ': continue
        sp = sprite_txt(ch, tam, peso, color, track=0)
        x = x0 + f.getlength(txt[:i + 1]) - f.getlength(ch) - .045 * tam * i
        ta = t0 + i * paso
        capas.append(Capa(sp, (origen[0] + x - 4, origen[1] + cy - tam * .62, origen[2]), ancla=(0, 0), ini=ini, fin=fin,
                          op=lambda t, a=ta: S(cl((t - a) / .14)), dxy=lambda t, a=ta: (0, 14 * (1 - S(cl((t - a) / .22))))))
    return capas
