# REFERENCIA del VSL de Tiro Hecho (horizontal). No es un motor genérico: Claude lo adapta a cada vídeo.
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'comun')); from rutas import *
# Subtítulos v4: Helvetica Neue Medium en minúscula, interlineado -1 px, sin fondos ni sombras,
# color neutro que se adapta píxel a píxel al fondo. Movimientos sutiles y fluidos que se alternan:
#   fundido  — cada palabra aparece subiendo 10 px desde un desenfoque leve
#   mascara  — la línea entera sube desde detrás de una línea invisible
#   suave    — el bloque entra escalando de 0,96 a 1 con fundido
#   letras   — (de vez en cuando) las letras suben una a una
import re, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import gfx as G
from subs3 import pega, hn

TAM = 66; INTER = TAM - 1     # interlineado -1 px
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_io(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x * x * x

BL = []; cur = []
for w in G.Wd:
    if cur and (len(cur) >= 4 or w[0] - cur[-1][1] > 0.35 or re.search(r"[.,?!…]$", cur[-1][2])):
        BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
ORDEN = ["fundido", "mascara", "suave", "fundido", "letras", "mascara", "suave", "fundido", "mascara", "letras"]
for i, b in enumerate(BL):
    t1 = b[-1][1] + 0.3
    if i + 1 < len(BL): t1 = min(t1, BL[i + 1][0][0] - 0.04)
    BL[i] = dict(t0=b[0][0] - 0.06, t1=t1, w=[(x[0] - 0.06, re.sub(r"[.,…¿?¡!]+", "", x[2]).lower()) for x in b], estilo=ORDEN[i % len(ORDEN)])

F = hn("bold", TAM); TRK = -0.065 * TAM; ESP = int(TAM * 0.20)
def largo(w): return F.getlength(w) + TRK * max(0, len(w) - 1)
def lineas(ws):
    anchos = [largo(w) for _, w in ws]; tot = sum(anchos) + ESP * (len(ws) - 1)
    if len(ws) >= 3 and tot > 760:   # dos líneas equilibradas
        mejor = min(range(1, len(ws)), key=lambda k: abs(sum(anchos[:k]) - sum(anchos[k:])))
        return [ws[:mejor], ws[mejor:]]
    return [ws]

CACHE = {}
def img_txt(txt):
    if txt not in CACHE:
        im = Image.new("RGBA", (int(largo(txt)) + 20, int(TAM * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 5
        for k, ch in enumerate(txt):   # tracking negativo: letras muy juntas
            d.text((x, int(TAM * 0.68)), ch, font=F, fill=(255, 255, 255), anchor="lm")
            x += F.getlength(ch) + (F.getlength(txt[k:k + 2]) - F.getlength(txt[k]) - F.getlength(txt[k + 1]) if k + 1 < len(txt) else 0) + TRK
        CACHE[txt] = im
    return CACHE[txt]
def alfa(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im

def dibuja(fr, t, y_base=800):
    b = next((b for b in BL if b["t0"] <= t < b["t1"]), None)
    if not b: return
    sal = 1 - ease((t - (b["t1"] - 0.12)) / 0.12)
    ls = lineas(b["w"]); n = len(ls)
    y0 = y_base - (n * INTER) // 2
    est = b["estilo"]
    if est == "suave":
        p = ease((t - b["t0"]) / 0.32); s = 0.96 + 0.04 * p
    for li, ln in enumerate(ls):
        anchos = [largo(w) for _, w in ln]; tot = sum(anchos) + ESP * (len(ln) - 1)
        x = (G.W - tot) / 2; cy = y0 + li * INTER + INTER // 2
        if est == "mascara":  # la línea sube desde detrás de su propia base
            p = ease_io((t - ln[0][0]) / 0.36)
            if p <= 0: continue
            txt = " ".join(w for _, w in ln); im = img_txt(txt); h = im.height
            dy = int(h * (1 - p)); vis = im.crop((0, 0, im.width, h - dy)) if h - dy > 0 else None
            if vis: pega(fr, alfa(vis, sal), x - 5, cy - h / 2 + dy)
            continue
        if est == "suave":
            if p <= 0: continue
            txt = " ".join(w for _, w in ln); im = img_txt(txt)
            im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
            pega(fr, alfa(im2, p * sal), x - 5 + (im.width - im2.width) / 2, cy - im2.height / 2)
            continue
        for (w0, w), aw in zip(ln, anchos):
            if est == "letras":
                cx = x
                for k, ch in enumerate(w):
                    p = ease((t - w0 - k * 0.022) / 0.26)
                    cw = F.getlength(w[:k + 1]) - F.getlength(w[:k]) + TRK
                    if p > 0:
                        im = img_txt(ch); pega(fr, alfa(im, p * sal), cx - 5, cy - im.height / 2 + 22 * (1 - p))
                    cx += cw
            else:  # fundido
                p = ease((t - w0) / 0.24)
                if p > 0:
                    im = img_txt(w)
                    if p < 1: im = im.filter(ImageFilter.GaussianBlur(3 * (1 - p)))
                    pega(fr, alfa(im, p * sal), x - 5, cy - im.height / 2 + 10 * (1 - p))
            x += aw + ESP

def eventos_sonido():
    return [(b["t0"], "letras") for b in BL if b["estilo"] == "letras"]
