# Objetos de otros vídeos reutilizados: tienda, buscador, megáfono, web atractiva, curvas y destellos.
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from mc import *
from obj import *
from piezas import *


def tienda(rotulo='TU WEB', fachada=(26, 58, 140)):
    w, h = 820, 700
    im = lienzo(w, h)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 90 * R_, w * R_, h * R_), fill=fachada + (255,))
    d.rectangle((0, 0, w * R_, 110 * R_), fill=tuple(int(c * .7) for c in fachada) + (255,))
    d.text((w, 56 * R_), rotulo, font=F(78 * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    n = 11
    for i in range(n):
        c = ROJO if i % 2 == 0 else (250, 248, 240)
        x0, x1 = i * w / n, (i + 1) * w / n
        d.polygon(pp([(x0, 112), (x1, 112), (x1 + 8 * (i - 5), 214), (x0 + 8 * (i - 6), 214)]), fill=c + (255,))
        d.pieslice(((x0 + 8 * (i - 6)) * R_, 196 * R_, (x1 + 8 * (i - 5)) * R_, 236 * R_), 0, 180, fill=c + (255,))
    # escaparates encendidos
    for x0, x1 in ((46, 300), (520, 774)):
        d.rectangle((x0 * R_, 260 * R_, x1 * R_, 610 * R_), fill=(255, 226, 150, 255), outline=(250, 248, 240, 255), width=5 * R_)
        for k in range(3):
            cx = x0 + (x1 - x0) * (k + .5) / 3
            d.rounded_rectangle(((cx - 28) * R_, 470 * R_, (cx + 28) * R_, 600 * R_), 8 * R_, fill=((226, 48, 44), (34, 110, 226), (37, 150, 104))[k] + (255,))
    # puerta
    d.rectangle((340 * R_, 270 * R_, 480 * R_, h * R_), fill=(255, 240, 200, 255), outline=(250, 248, 240, 255), width=5 * R_)
    d.ellipse((452 * R_, 470 * R_, 470 * R_, 488 * R_), fill=(90, 70, 40, 255))
    return con_sombra(im, des=24, op=.32)


def barra_busqueda():
    im = plaza(620, 110, (255, 255, 255), rr=55)
    d = ImageDraw.Draw(im)
    d.ellipse((34 * R_, 30 * R_, 76 * R_, 72 * R_), outline=(90, 90, 96, 255), width=7 * R_ // 2)
    d.line((70 * R_, 66 * R_, 88 * R_, 84 * R_), fill=(90, 90, 96, 255), width=7 * R_ // 2)
    s = sprite_txt('tu negocio cerca de mí', 44, 0, (60, 60, 64))
    im.alpha_composite(s, (108 * R_, (im.height - s.height) // 2))
    return con_sombra(im, des=14, op=.3)


def megafono():
    im = lienzo(460, 330)
    d = ImageDraw.Draw(im)
    d.polygon(pp([(40, 130), (150, 130), (420, 20), (420, 310), (150, 210), (40, 210)]), fill=ROJO + (255,))
    d.rounded_rectangle((26 * R_, 118 * R_, 66 * R_, 222 * R_), 12 * R_, fill=(30, 30, 34, 255))
    d.polygon(pp([(120, 210), (172, 210), (190, 300), (140, 310)]), fill=(30, 30, 34, 255))
    d.ellipse((396 * R_, 16 * R_, 446 * R_, 314 * R_), fill=(246, 236, 214, 255))
    d.polygon(pp([(150, 130), (420, 20), (420, 70), (150, 160)]), fill=(250, 110, 96, 255))
    return con_sombra(im, des=14, op=.3)


def video_movil():
    im = lienzo(230, 400)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 230 * R_ - 1, 400 * R_ - 1), 36 * R_, fill=(20, 20, 24, 255))
    d.rounded_rectangle((12 * R_, 14 * R_, 218 * R_, 386 * R_), 26 * R_, fill=(244, 92, 110, 255))
    d.ellipse((60 * R_, 145 * R_, 170 * R_, 255 * R_), fill=(255, 255, 255, 255))
    d.polygon(pp([(98, 170), (98, 230), (146, 200)]), fill=(244, 92, 110, 255))
    return con_sombra(im, des=14, op=.3)


def web_atractiva():
    w, h = 860, 660
    W_, H_ = w * R_, h * R_
    ys, xs = np.mgrid[0:H_, 0:W_].astype(np.float32)
    u, v = xs / W_, ys / H_
    a = np.dstack([18 + 70 * u + 30 * v, 22 + 40 * v, 60 + 120 * u + 40 * v])
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    d.ellipse((W_ * .55, -H_ * .15, W_ * 1.15, H_ * .75), fill=(255, 120, 90, 150))
    d.ellipse((W_ * .68, H_ * .2, W_ * 1.05, H_ * .75), fill=(255, 210, 110, 190))
    d.text((52 * R_, 44 * R_), 'tu marca', font=F(36 * R_, 1), fill=(255, 255, 255, 255))
    for i, t_ in enumerate(('Servicios', 'Casos', 'Contacto')):
        d.text(((430 + i * 138) * R_, 50 * R_), t_, font=F(26 * R_, 0), fill=(240, 240, 248, 255))
    d.text((52 * R_, 150 * R_), 'Lo que vendes,', font=F(78 * R_, 1), fill=(255, 255, 255, 255))
    d.text((52 * R_, 240 * R_), 'claro y a la', font=F(78 * R_, 1), fill=(255, 255, 255, 255))
    d.text((52 * R_, 330 * R_), 'primera.', font=F(78 * R_, 1), fill=(255, 255, 255, 255))
    d.rounded_rectangle((52 * R_, 450 * R_, 340 * R_, 540 * R_), 45 * R_, fill=VERDE + (255,))
    d.text((196 * R_, 495 * R_), 'Llamar ahora', font=F(38 * R_, 1), fill=(255, 255, 255, 255), anchor='mm')
    d.text((52 * R_, 575 * R_), '★★★★★', font=F(32 * R_, 1), fill=(250, 200, 40, 255))
    # esquinas
    m = Image.new('L', (W_, H_), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, W_ - 1, H_ - 1), 26 * R_, fill=255)
    im.putalpha(m)
    return con_sombra(im, des=26, op=.4)


def calle(col=TINTA):
    im = lienzo(2600, 10)
    ImageDraw.Draw(im).rectangle((0, 0, 2600 * R_, 10 * R_), fill=col + (255,))
    return im


def suave(pts, n=14):
    """Curva Catmull-Rom cerrada que pasa por los puntos."""
    out = []
    m = len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[(i - 1) % m], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for k in range(n):
            u = k / n
            q = []
            for a in range(2):
                q.append(.5 * (2 * p1[a] + (-p0[a] + p2[a]) * u + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * u ** 2 + (-p0[a] + 3 * p1[a] - 3 * p2[a] + p3[a]) * u ** 3))
            out.append(tuple(q))
    return out


def mota(r=10, col=(255, 220, 170)):
    t = 2 * r * 2
    ys, xs = np.mgrid[0:t, 0:t].astype(np.float32)
    a = np.clip(1 - np.hypot(xs - t / 2, ys - t / 2) / (t / 2), 0, 1) ** 2
    return Image.fromarray(np.dstack([np.full((t, t), col[0]), np.full((t, t), col[1]), np.full((t, t), col[2]), a * 255]).astype(np.uint8), 'RGBA')


def destello(tam=900, col=(255, 240, 200)):
    ys, xs = np.mgrid[0:tam, 0:tam].astype(np.float32)
    x, y = xs - tam / 2, ys - tam / 2
    d = np.hypot(x, y) / (tam / 2)
    a = np.exp(-(d / .16) ** 2) * .9 + np.exp(-(np.abs(y) / 4) ** 2) * np.exp(-(np.abs(x) / (tam * .38)) ** 2) * .85 + np.exp(-(d / .5) ** 2) * .18
    return Image.fromarray(np.dstack([np.full((tam, tam), col[0]), np.full((tam, tam), col[1]), np.full((tam, tam), col[2]), a.clip(0, 1) * 255]).astype(np.uint8), 'RGBA')


NOTA_C = (255, 214, 64)
def nota(tam=300, col=NOTA_C, texto=None, sombra=True):
    """Nota adhesiva: banda de pegamento arriba y la parte de abajo un poco levantada."""
    t = tam * R_
    ys = np.linspace(0, 1, t)[:, None]
    k = 1.03 - .09 * ys ** 2 + .05 * (ys < .16)
    a = np.ones((t, t, 3), np.float32) * np.array(col, np.float32) * k[..., None]
    a += np.random.default_rng(tam).normal(0, 1.6, (t, t, 1))
    im = Image.fromarray(a.clip(0, 255).astype(np.uint8)).convert('RGBA')
    return con_sombra(im, dx=8, dy=20, des=18, op=.32) if sombra else im
