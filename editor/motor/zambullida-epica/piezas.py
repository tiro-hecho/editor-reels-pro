NOMBRE = 'Tu nombre'  # nombre que sale en el chat
# Piezas del vídeo de webs: teléfono, pantallas, cuadro, tarjetas. Salen de vd.py (primera versión del guion).
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mc import *
from obj import *
from estilos import marco

BLA, CREMA_T, ORO = (255, 255, 255), (246, 236, 214), (250, 204, 90)
VERDE = (37, 190, 104)
ENT = cb(.2, .9, .3, 1)
SALE = cb(.6, 0, .15, 1)
def pop(ta, dur=.24, e=1.):
    return lambda t: max(.001, ENT(cl((t - ta) / dur))) * e


# ---------- objetos
PW, PH_ = 520, 1060
def _pantalla(fondo):
    return Image.new('RGBA', ((PW - 44) * R_, (PH_ - 44) * R_), fondo + (255,))


def movil(pant):
    """Teléfono con la pantalla que se le pase."""
    im = lienzo(PW, PH_)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, PW * R_ - 1, PH_ * R_ - 1), 66 * R_, fill=(18, 18, 20, 255))
    d.rounded_rectangle((3 * R_, 3 * R_, (PW - 3) * R_, (PH_ - 3) * R_), 64 * R_, outline=(96, 96, 104, 255), width=3 * R_)
    m = Image.new('L', pant.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, pant.width - 1, pant.height - 1), 48 * R_, fill=255)
    im.paste(pant, (22 * R_, 22 * R_), m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle(((PW / 2 - 66) * R_, 40 * R_, (PW / 2 + 66) * R_, 72 * R_), 16 * R_, fill=(18, 18, 20, 255))
    return con_sombra(im, des=30, op=.42)


def _web_generica(col=(120, 128, 150), titulo='Bienvenidos'):
    p = _pantalla((246, 246, 244))
    d = ImageDraw.Draw(p)
    W_ = p.width
    d.rectangle((0, 0, W_, 150 * R_), fill=(232, 232, 230, 255))
    d.rounded_rectangle((36 * R_, 98 * R_, 170 * R_, 124 * R_), 10 * R_, fill=(170, 170, 174, 255))
    d.rectangle((0, 150 * R_, W_, 520 * R_), fill=col + (255,))
    d.text((W_ / 2, 335 * R_), titulo, font=F(58 * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    for y, w in ((560, 380), (600, 410), (640, 300), (700, 400), (740, 340), (780, 390), (840, 260)):
        d.rounded_rectangle((36 * R_, y * R_, (36 + w) * R_, (y + 16) * R_), 8 * R_, fill=(196, 196, 196, 255))
    return p


def _web_cargando():
    p = _web_generica(col=(170, 174, 186), titulo='')
    a = np.array(p).astype(np.float32)
    a[..., :3] = a[..., :3] * .55 + 110
    p = Image.fromarray(a.clip(0, 255).astype(np.uint8), 'RGBA')
    d = ImageDraw.Draw(p)
    x0, x1, y = 70 * R_, p.width - 70 * R_, 720 * R_
    d.rounded_rectangle((x0, y, x1, y + 16 * R_), 8 * R_, fill=(150, 150, 150, 255))
    d.rounded_rectangle((x0, y, x0 + (x1 - x0) * .14, y + 16 * R_), 8 * R_, fill=ROJO + (255,))
    return p


def _web_buena():
    p = _pantalla((250, 250, 248))
    d = ImageDraw.Draw(p)
    W_ = p.width
    d.rectangle((0, 0, W_, 520 * R_), fill=AZUL + (255,))
    d.text((W_ / 2, 240 * R_), 'Te atiendo', font=F(62 * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    d.text((W_ / 2, 320 * R_), 'hoy mismo', font=F(62 * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    d.rounded_rectangle((70 * R_, 600 * R_, W_ - 70 * R_, 730 * R_), 32 * R_, fill=VERDE + (255,))
    d.text((W_ / 2, 665 * R_), 'Llamar', font=F(60 * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    for y, w in ((790, 340), (830, 300)):
        d.rounded_rectangle((70 * R_, y * R_, (70 + w) * R_, (y + 16) * R_), 8 * R_, fill=(196, 196, 196, 255))
    return p


def _chat():
    p = _pantalla((236, 229, 216))
    d = ImageDraw.Draw(p)
    d.rectangle((0, 0, p.width, 118 * R_), fill=(26, 40, 62, 255))
    d.ellipse((30 * R_, 62 * R_, 78 * R_, 110 * R_), fill=(214, 214, 214, 255))
    d.text((96 * R_, 86 * R_), NOMBRE, font=F(38 * R_, 1), fill=(255, 255, 255, 255), anchor='lm')
    return p


def plaza(w, h, col=(255, 255, 255), rr=30):
    im = lienzo(w, h)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w * R_ - 1, h * R_ - 1), rr * R_, fill=col + (255,))
    return im


def chip_cero():
    im = plaza(330, 300)
    d = ImageDraw.Draw(im)
    d.text((165 * R_, 118 * R_), '0', font=F(190 * R_, 1), fill=ROJO + (255,), anchor='mm')
    d.text((165 * R_, 248 * R_), 'llamadas', font=F(52 * R_, 1), fill=TINTA + (255,), anchor='mm')
    return con_sombra(im, des=18, op=.5)


def num_med(n, fondo=TINTA, r=135):
    im = lienzo(2 * r, 2 * r)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 4 * r - 1, 4 * r - 1), fill=fondo + (255,))
    d.text((2 * r, int(2 * r * .97)), n, font=F(int(r * 1.15) * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    return con_sombra(im)


def spinner(r=74, col=(40, 40, 44)):
    t = 2 * r * R_
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    x, y = xs - t / 2, ys - t / 2
    d = np.hypot(x, y)
    th = (np.arctan2(y, x) + math.pi) / (2 * math.pi)
    al = np.clip((r * R_ - d) + .5, 0, 1) * np.clip((d - (r - 16) * R_) + .5, 0, 1) * th
    a = np.dstack([np.full((t, t), col[0]), np.full((t, t), col[1]), np.full((t, t), col[2]), al * 255])
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def check(r=46, fondo=VERDE):
    im = lienzo(2 * r, 2 * r)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, 4 * r - 1, 4 * r - 1), fill=fondo + (255,))
    d.line(pp([(r * .52, r * 1.04), (r * .88, r * 1.42), (r * 1.5, r * .68)]), fill=(255, 255, 255, 255), width=int(r * .36 * R_ / 2), joint='curve')
    return im


def persona(col=TINTA):
    im = lienzo(190, 310)
    d = ImageDraw.Draw(im)
    d.ellipse((50 * R_, 0, 140 * R_, 90 * R_), fill=col + (255,))
    d.rounded_rectangle((12 * R_, 104 * R_, 178 * R_, 310 * R_), 62 * R_, fill=col + (255,))
    return im


def web_bonita(w, h):
    """Una web preciosa sin nada que decir: degradado, formas y líneas vacías."""
    W_, H_ = w * R_, h * R_
    ys, xs = np.mgrid[0:H_, 0:W_].astype(np.float32)
    u, v = xs / W_, ys / H_
    a = np.dstack([235 - 130 * v + 20 * u, 96 + 40 * u + 70 * v, 142 + 90 * v])
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    d.ellipse((W_ * .52, H_ * .08, W_ * .94, H_ * .72), fill=(255, 214, 150, 170))
    d.ellipse((W_ * .1, H_ * .42, W_ * .46, H_ * 1.02), fill=(120, 210, 230, 140))
    d.rectangle((0, 0, W_, 42 * R_), fill=(255, 255, 255, 215))
    for i in range(4):
        d.rounded_rectangle((W_ - (86 * (i + 1)) * R_, 16 * R_, W_ - (86 * i + 26) * R_, 26 * R_), 5 * R_, fill=(160, 160, 170, 255))
    for y, l in ((.32, .36), (.4, .28)):
        d.rounded_rectangle((36 * R_, H_ * y, 36 * R_ + W_ * l, H_ * y + 16 * R_), 8 * R_, fill=(255, 255, 255, 230))
    return im


def cuadro(w=760, h=500):
    m = marco(w + 88, h + 88)
    m.paste(web_bonita(w, h), (44 * R_, 44 * R_))
    return con_sombra(m, des=26, op=.5)


def pastilla(txt, tam=56, col=TINTA, fg=(255, 255, 255)):
    w = int(ancho(txt, tam)) + 76
    h = int(tam * 1.7)
    im = plaza(w, h, col, rr=h // 2)
    s = sprite_txt(txt, tam, 1, fg)
    im.alpha_composite(s, ((im.width - s.width) // 2, int((im.height - s.height) * .5)))
    return con_sombra(im, des=12, op=.4)


def cabeza_web():
    im = lienzo(420, 330)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6 * R_, 6 * R_, 414 * R_, 324 * R_), 22 * R_, fill=(248, 247, 243, 255))
    d.rounded_rectangle((6 * R_, 6 * R_, 414 * R_, 72 * R_), 22 * R_, fill=(60, 66, 84, 255))
    d.rectangle((6 * R_, 50 * R_, 414 * R_, 72 * R_), fill=(60, 66, 84, 255))
    for i, c in enumerate(((236, 84, 72), (240, 190, 70), (90, 190, 110))):
        d.ellipse(((32 + i * 34) * R_, 30 * R_, (54 + i * 34) * R_, 52 * R_), fill=c + (255,))
    d.rectangle((40 * R_, 100 * R_, 380 * R_, 190 * R_), fill=AZUL + (255,))
    for y, w in ((215, 300), (245, 340), (275, 220)):
        d.rounded_rectangle((40 * R_, y * R_, (40 + w) * R_, (y + 14) * R_), 7 * R_, fill=(190, 190, 186, 255))
    return con_sombra(im, des=14, op=.45)


def mini_web(i):
    cols = ((28, 104, 230), (226, 44, 40), (20, 20, 20), (37, 150, 104), (240, 170, 40), (120, 70, 190))
    c = cols[i % len(cols)]
    im = plaza(120, 150, (250, 250, 248), rr=12)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 120 * R_, 22 * R_), 12 * R_, fill=(70, 74, 88, 255))
    d.rectangle((10 * R_, 32 * R_, 110 * R_, 86 * R_), fill=c + (255,))
    for y, w in ((98, 92), (114, 70), (130, 84)):
        d.rounded_rectangle((12 * R_, y * R_, (12 + w) * R_, (y + 7) * R_), 3 * R_, fill=(190, 190, 186, 255))
    return im


def estrella_oro(r=66, col=(245, 180, 30)):
    im = lienzo(2 * r, 2 * r)
    pts = []
    for i in range(10):
        q = r * (1 if i % 2 == 0 else .46)
        a = -math.pi / 2 + i * math.pi / 5
        pts.append(((r + q * math.cos(a)) * R_, (r + q * math.sin(a)) * R_))
    ImageDraw.Draw(im).polygon(pts, fill=col + (255,))
    return im


def tarjeta_resena():
    im = plaza(880, 400, (255, 255, 255), rr=34)
    d = ImageDraw.Draw(im)
    for i in range(5):
        e = estrella_oro(r=30)
        im.alpha_composite(e, ((56 + i * 66) * R_, 46 * R_))
    for y, tx in ((150, '«He visto un aumento'), (216, 'del 45 % en las solicitudes'), (282, 'de presupuesto.»')):
        s = sprite_txt(tx, 58, 1, TINTA)
        im.alpha_composite(s, (48 * R_, y * R_))
    return con_sombra(im, des=26, op=.32)


def aro(r=330, g=9, col=(255, 255, 255)):
    t = (2 * r + 8) * R_
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    d = np.hypot(xs - t / 2, ys - t / 2)
    al = np.clip((r * R_ - d) + .5, 0, 1) * np.clip((d - (r - g) * R_) + .5, 0, 1)
    a = np.dstack([np.full((t, t), col[0]), np.full((t, t), col[1]), np.full((t, t), col[2]), al * 255])
    return Image.fromarray(a.astype(np.uint8), 'RGBA')


def globo_chat(txt, azul=False, tam=44, w=430):
    h = int(tam * 2.1)
    c = (34, 130, 246) if azul else (255, 255, 255)
    im = plaza(w, h, c, rr=26)
    s = sprite_txt(txt, tam, 1, (255, 255, 255) if azul else TINTA)
    x = (im.width - s.width) // 2 if azul else 90 * R_
    im.alpha_composite(s, (x, (im.height - s.height) // 2))
    if not azul:
        k = check(r=26)
        im.alpha_composite(k, (22 * R_, (im.height - k.height) // 2))
    return con_sombra(im, des=8, dx=4, dy=7, op=.22)


