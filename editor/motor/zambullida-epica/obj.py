# Objetos del estilo Simply Put: medallones, figuras, fondos. Sale de wd40/wd.py.
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mc import *

CREMA = (247, 242, 231)
TINTA = (16, 16, 16)
ROJO, AZUL, AMARILLO = (226, 44, 40), (28, 104, 230), (250, 200, 40)


# ---------- objetos
R_ = 2
def lienzo(w, h): return Image.new('RGBA', (w * R_, h * R_), (0, 0, 0, 0))
def pp(l): return [(x * R_, y * R_) for x, y in l]

def con_sombra(im, res=2, dx=14, dy=24, des=22, op=.3):
    pad = int(60 * res)
    out = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new('L', out.size, 0)
    a.paste(im.getchannel('A'), (pad + int(dx * res), pad + int(dy * res)))
    a = a.filter(ImageFilter.GaussianBlur(des * res)).point(lambda v: int(v * op))
    s = Image.new('RGBA', out.size, (0, 0, 0, 0)); s.putalpha(a)
    out.alpha_composite(s)
    out.alpha_composite(im, (pad, pad))
    return out


def medallon(r=170, fondo=TINTA, marca=(255, 255, 255)):
    im = lienzo(2 * r, 2 * r)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 4 * r - 1, 4 * r - 1), fill=fondo + (255,))
    q = r * .36 * R_
    g = int(r * .17 * R_)
    c = 2 * r
    d.line((c - q, c - q, c + q, c + q), fill=marca + (255,), width=g)
    d.line((c - q, c + q, c + q, c - q), fill=marca + (255,), width=g)
    return con_sombra(im.resize(im.size, Image.LANCZOS))


def lata(w=340, h=820, res=2):
    """Bote de spray dibujado, con volumen de cilindro."""
    W_, H_ = w * res, (h + 170) * res
    im = Image.new('RGB', (W_, H_), (30, 30, 34))
    d = ImageDraw.Draw(im)
    top = 170 * res
    y0, y1, y2 = top + 60 * res, top + 470 * res, top + 690 * res
    d.rectangle((0, top, W_, y0), fill=(190, 192, 198))
    d.rectangle((0, y0, W_, y1), fill=(18, 78, 178))
    d.rectangle((0, y1, W_, y2), fill=AMARILLO)
    d.rectangle((0, y2, W_, H_), fill=(18, 78, 178))
    f1, f2 = F(int(w * .46 * res), 1), F(int(w * .25 * res), 1)
    d.text((W_ / 2, y0 + 210 * res), '40', font=f1, fill=(255, 255, 255), anchor='mm')
    d.text((W_ / 2, y1 + 110 * res), 'WD', font=f2, fill=(18, 40, 90), anchor='mm')
    a = np.asarray(im, np.float32)
    xs = (np.arange(W_) - W_ / 2) / (W_ / 2)
    nz = np.sqrt(np.clip(1 - xs ** 2, 0, 1))
    luz = (.32 + .82 * nz)[None, :, None]
    bri = (np.exp(-((xs + .46) / .09) ** 2) * 80 + np.exp(-((xs - .62) / .05) ** 2) * 26)[None, :, None]
    a = a * luz + bri
    # alfa: cuerpo con hombros redondeados, tapón y cánula
    al = Image.new('L', (W_ * 2, H_ * 2), 0)
    da = ImageDraw.Draw(al)
    da.rounded_rectangle((0, (top - 24 * res) * 2, W_ * 2 - 1, H_ * 2 - 1), 56 * res * 2, fill=255)
    cap = Image.new('L', al.size, 0)
    dc = ImageDraw.Draw(cap)
    dc.rounded_rectangle((W_ * .32 * 2, (top - 96 * res) * 2, W_ * .68 * 2, (top - 10 * res) * 2), 18 * res * 2, fill=255)
    dc.rectangle((W_ * .46 * 2, (top - 150 * res) * 2, W_ * .54 * 2, (top - 90 * res) * 2), fill=255)
    al = al.resize((W_, H_), Image.LANCZOS); cap = cap.resize((W_, H_), Image.LANCZOS)
    ca = np.asarray(cap, np.float32)[..., None] / 255
    a = a * (1 - ca) + np.array((214, 40, 36), np.float32) * ca
    alfa = np.maximum(np.asarray(al, np.float32), ca[..., 0] * 255)
    return Image.fromarray(np.dstack([a, alfa]).clip(0, 255).astype(np.uint8), 'RGBA')


def misil(w=190, h=1040, res=1.5):
    W_, H_ = int(w * res), int(h * res)
    ys, xs = np.mgrid[0:H_, 0:W_].astype(np.float32)
    v = ys / H_
    # ojiva: el radio crece en el primer 30 %
    rad = np.where(v < .3, np.sqrt(np.clip(v / .3, 0, 1)) * .72, .72)
    u = (xs - W_ / 2) / (W_ / 2)
    cuerpo = np.abs(u) <= rad
    nu = np.clip(u / np.maximum(rad, .01), -1, 1)
    sh = .35 + .85 * np.sqrt(np.clip(1 - nu ** 2, 0, 1))
    col = np.dstack([sh * 226, sh * 228, sh * 232])
    banda = ((v > .34) & (v < .39)) | ((v > .78) & (v < .82))
    col[banda] = np.dstack([sh * ROJO[0], sh * ROJO[1], sh * ROJO[2]])[banda]
    al = Image.fromarray((cuerpo * 255).astype(np.uint8))
    d = ImageDraw.Draw(al)
    d.polygon([(0, H_ - 1), (W_ * .14, H_ * .78), (W_ * .2, H_ * .95), (W_ * .2, H_ - 1)], fill=255)
    d.polygon([(W_ - 1, H_ - 1), (W_ * .86, H_ * .78), (W_ * .8, H_ * .95), (W_ * .8, H_ - 1)], fill=255)
    al = al.filter(ImageFilter.GaussianBlur(1))
    return Image.fromarray(np.dstack([col, np.asarray(al, np.float32)]).clip(0, 255).astype(np.uint8), 'RGBA')


def desenfoca(im, r, op=1.):
    """Desenfoque sin halo oscuro: premultiplica antes y despremultiplica después."""
    a = np.asarray(im, np.float32) / 255
    al = a[..., 3:]
    pre = np.dstack([a[..., :3] * al, al])
    ca = [np.asarray(Image.fromarray((pre[..., i] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), np.float32) / 255 for i in range(4)]
    alpha = np.maximum(ca[3], 1e-3)
    rgb = np.dstack([np.clip(ca[i] / alpha, 0, 1) for i in range(3)])
    return Image.fromarray((np.dstack([rgb, ca[3] * op]) * 255).astype(np.uint8), 'RGBA')


TRAJE, SOLAPA = (34, 40, 58), (50, 57, 80)
def cuerpo():
    im = lienzo(660, 980)
    d = ImageDraw.Draw(im)
    d.polygon(pp([(212, 560), (322, 560), (312, 900), (222, 900)]), fill=TRAJE + (255,))
    d.polygon(pp([(338, 560), (448, 560), (438, 900), (348, 900)]), fill=TRAJE + (255,))
    d.rounded_rectangle((200 * R_, 888 * R_, 322 * R_, 930 * R_), 16 * R_, fill=(14, 14, 16, 255))
    d.rounded_rectangle((338 * R_, 888 * R_, 460 * R_, 930 * R_), 16 * R_, fill=(14, 14, 16, 255))
    d.polygon(pp([(142, 118), (250, 82), (410, 82), (518, 118), (482, 590), (178, 590)]), fill=TRAJE + (255,))
    d.rectangle((292 * R_, 40 * R_, 368 * R_, 110 * R_), fill=(226, 184, 150, 255))
    d.polygon(pp([(262, 82), (398, 82), (330, 340)]), fill=(245, 243, 236, 255))
    d.polygon(pp([(312, 96), (348, 96), (340, 130), (362, 300), (330, 342), (298, 300), (320, 130)]), fill=ROJO + (255,))
    d.polygon(pp([(250, 82), (262, 82), (330, 342), (300, 410), (216, 180)]), fill=SOLAPA + (255,))
    d.polygon(pp([(410, 82), (398, 82), (330, 342), (360, 410), (444, 180)]), fill=SOLAPA + (255,))
    # brazos pegados al cuerpo
    for x0, x1, x2, x3 in ((142, 58, 98, 200), (518, 602, 562, 460)):
        d.polygon(pp([(x0, 118), (x1, 480), (x2, 500), (x3, 200)]), fill=TRAJE + (255,))
        d.ellipse(((x1 + x2) / 2 * R_ - 34 * R_, 490 * R_ - 34 * R_, (x1 + x2) / 2 * R_ + 34 * R_, 490 * R_ + 34 * R_), fill=(226, 184, 150, 255))
    return im


def cabeza_papel():
    im = lienzo(250, 300)
    d = ImageDraw.Draw(im)
    d.rectangle((6 * R_, 6 * R_, 244 * R_, 294 * R_), fill=(244, 241, 232, 255))
    d.text((125 * R_, 150 * R_), '?', font=F(200 * R_, 1), fill=TINTA + (255,), anchor='mm')
    return im.rotate(-3, Image.BICUBIC, expand=True)


def socio(tono=True):
    """Figura en gris con la cabeza de papel: el personaje del tutorial."""
    c = cuerpo(); h = cabeza_papel()
    out = Image.new('RGBA', (c.width, c.height + h.height - 90), (0, 0, 0, 0))
    out.alpha_composite(c, (0, h.height - 90))
    out.alpha_composite(h, (c.width // 2 - h.width // 2, 0))
    a = np.array(out).astype(np.float32)
    lum = (a[..., 0] * .3 + a[..., 1] * .59 + a[..., 2] * .11) / 255
    n = np.random.default_rng(5).normal(0, .045, lum.shape)
    v = (np.clip(.16 + lum ** .85 * 1.05 + n, 0, 1) * 255)
    return Image.fromarray(np.dstack([v, v, v, a[..., 3]]).clip(0, 255).astype(np.uint8), 'RGBA')


def silueta_negra():
    c = cuerpo()
    out = Image.new('RGBA', (c.width, c.height + 240), (0, 0, 0, 0))
    out.alpha_composite(c, (0, 240))
    d = ImageDraw.Draw(out)
    d.ellipse((c.width / 2 - 170, 0, c.width / 2 + 170, 380), fill=(0, 0, 0, 255))
    negro = Image.new('RGBA', out.size, TINTA + (0,))
    negro.putalpha(out.getchannel('A'))
    return negro


def casa():
    im = lienzo(520, 560)
    d = ImageDraw.Draw(im)
    d.polygon(pp([(0, 240), (260, 0), (520, 240), (470, 240), (470, 560), (50, 560), (50, 240)]), fill=TINTA + (255,))
    d.rectangle((210 * R_, 360 * R_, 310 * R_, 560 * R_), fill=CREMA + (255,))
    return im


def billete(s=1):
    w, h = 520, 230
    im = Image.new('RGB', (w * 2, h * 2), (150, 182, 146))
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, w * 2 - 15, h * 2 - 15), outline=(52, 92, 66), width=8)
    d.rectangle((34, 34, w * 2 - 35, h * 2 - 35), outline=(92, 130, 100), width=3)
    d.ellipse((w - 130, h - 150, w + 130, h + 150), fill=(120, 158, 122), outline=(52, 92, 66), width=6)
    d.text((w, h), '$', font=F(190, 1), fill=(44, 84, 58), anchor='mm')
    for x, y, a in ((110, 96, 'la'), (w * 2 - 110, h * 2 - 96, 'rb')):
        d.text((x, y), '100', font=F(62, 1), fill=(44, 84, 58), anchor='mm')
    a = np.asarray(im, np.float32) + np.random.default_rng(s).normal(0, 3, (h * 2, w * 2, 1))
    return con_sombra(Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA'), des=12, op=.25)


def bloque_(w, h, col):
    im = lienzo(w, h)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * R_ - 1, h * R_ - 1), 18 * R_, fill=col + (255,))
    return im


# ---------- fondos
def fondo_oscuro():
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot((xs - W / 2) / (W * .7), (ys - H * .45) / (H * .62))
    v = 10 + 40 * np.clip(1 - d, 0, 1) ** 1.6 + np.random.default_rng(1).normal(0, 1.6, (H, W))
    return Image.fromarray(np.dstack([v, v, v * 1.02]).clip(0, 255).astype(np.uint8)).convert('RGBA')


