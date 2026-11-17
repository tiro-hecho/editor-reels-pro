# -*- coding: utf-8 -*-
# v3 «como la ref»: pegatinas 3D (emoji Apple) con rebote y flotación, tarjetas polaroid en cascada,
# objeto que cae sobre la palabra, billetes volando, inversión de color en una transición. Sin temblor, rayos ni chispas.
import os, sys, math, random, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1, v2
from v1 import W, H, FPS, CUT, wt, ease, eio, F, HNM, HNB, paste_c, cara, NF
from v2 import spring, letras, palabra, zoomblur, recorta
from rutas_estilo import ICONOS as IC
random.seed(3)
_cache = {}
def ico(n, size):
    k = (n, size)
    if k not in _cache:
        im = Image.open(os.path.join(IC, n + ".png")).convert("RGBA"); s = size / max(im.size)
        im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        # sombra suave de contacto (muy ligera, sin borde)
        pad = 40; c = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].point(lambda v: int(v * 0.30)))
        c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (pad, pad + 14)); c.alpha_composite(im, (pad, pad))
        _cache[k] = c
    return _cache[k]

def pop_k(d, dur=0.30):
    """escala con rebote 0 -> 1.12 -> 1"""
    if d <= 0: return 0
    x = d / dur
    return 1 - math.exp(-6 * x) * math.cos(8 * x) if x < 3 else 1

# pegatinas: (icono, t_in, t_out, x, y, tamaño, giro_final)
TA = wt("agencia"); TN = wt("negocios"); TC = wt("Cantabria")
TCAM = wt("cámara", CUT[2]); TB = wt("bien", CUT[2])
TCOL = wt("colaboradores", CUT[1])
STK = [("megafono", TA, TN - .1, 200, 340, 230, -14), ("grafica", TA + .10, TN - .1, 800, 360, 220, 12),
       ("camara", TCAM - .02, CUT[3], 790, 520, 260, 10), ("claqueta", TB - .05, CUT[3], 200, 560, 220, -12),
       ("gente", CUT[1] + .30, CUT[2], 810, 760, 210, 10),
       ("bolsa", CUT[3] + .62, CUT[4], 810, 1180, 200, 8)]
# objeto que cae sobre la palabra gigante
DROP = [("pin", TC + .12, CUT[1], 540, 520 - 150, 170), ("manos", TCOL + .12, CUT[2], 850, 300, 150)]
# tarjetas polaroid de negocios (cascada)
NEG = [("pizza", "Restaurantes"), ("tijeras", "Peluquerías"), ("pesa", "Gimnasios"), ("diente", "Clínicas")]
TCARD = [wt("trabajamos") + .05 + k * 0.22 for k in range(4)]
POS = [(250, 990, -8), (390, 1070, 5), (260, 1180, 7), (400, 1270, -5)]  # dentro de y 220-1440
def tarjeta(icon, txt):
    w, h = 230, 270; im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 90)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (20, 30))
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=(255, 255, 255, 255))
    d.rounded_rectangle((12, 12, w - 13, 196), 14, fill=(243, 236, 222, 255))
    ic = ico(icon, 150); c.alpha_composite(ic, (int(w / 2 - ic.width / 2), int(104 - ic.height / 2)))
    f = F(HNB, 30); d.text((w / 2, 232), txt, font=f, fill=(30, 30, 30, 255), anchor="mm")
    im.alpha_composite(c, (20, 20)); return im
CARDS = [tarjeta(i, t) for i, t in NEG]

def sticker(lay, t, n, t0, t1, x, y, size, rot):
    d = t - t0
    if d < 0 or t >= t1 + 0.15: return
    k = pop_k(d); out = 1 - eio((t - t1) / 0.15) if t > t1 else 1
    sc = max(0.01, k * out); r = rot + (1 - min(1, d / 0.3)) * (-rot * 2.2) + 3 * math.sin(t * 2.6 + x)
    by = 7 * math.sin(t * 3.1 + y)
    im = ico(n, size).rotate(r, expand=True, resample=Image.BICUBIC)
    paste_c(lay, im, x, y + by, sc, min(1, k * 1.5) * out, max(0, (1 - d / 0.12)) * 6)

def caida(lay, t, n, t0, t1, x, y, size):
    d = t - t0
    if d < 0 or t >= t1: return
    p = min(1, d / 0.28); yy = y - 420 * (1 - p) ** 2
    if p >= 1:  # rebote al aterrizar
        e = d - 0.28; yy = y - 40 * abs(math.sin(e * 11)) * math.exp(-e * 7)
    sq = 1 + (0.18 * math.exp(-(d - 0.28) * 14) if d > 0.28 else 0)
    im = ico(n, size).rotate(6 * math.sin(t * 3), expand=True, resample=Image.BICUBIC)
    im = im.resize((int(im.width * sq), int(im.height / sq)), Image.LANCZOS)
    paste_c(lay, im, x, yy + 4 * math.sin(t * 3), 1, min(1, d / 0.08), (1 - p) * 5)

def cascada(lay, t):
    for k, (c, t0) in enumerate(zip(CARDS, TCARD)):
        d = t - t0; t1 = TC - 0.05
        if d < 0 or t > t1 + 0.18: continue
        x, y, r = POS[k]; p = ease(d / 0.26)
        out = 1 - eio((t - t1) / 0.18) if t > t1 else 1
        yy = y - 260 * (1 - p); rr = r + (1 - p) * 25
        im = c.rotate(rr + 1.5 * math.sin(t * 2 + k), expand=True, resample=Image.BICUBIC)
        paste_c(lay, im, x - (1 - out) * 300, yy + 5 * math.sin(t * 2.5 + k), 0.85 + 0.15 * p, min(1, p * 2) * out, (1 - p) * 8)
    # barrido amarillo detrás de las tarjetas (como la ref)
    d = t - TCARD[0]
    if 0 <= d < TC - TCARD[0]:
        a = min(1, d / 0.2) * (1 - eio((t - (TC - .25)) / .25))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle((0, 960, 500 * min(1, d / 0.35), 1420), fill=(255, 200, 40, int(120 * a)))
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))

# billetes volando en primer plano
BIL = []
for n in range(9):
    big = n < 2
    BIL.append(dict(t=CUT[3] + .45 + random.uniform(0, .45), x0=random.choice([-200, W + 200]), y0=random.uniform(200, 1500),
                    vy=random.uniform(-500, 600), sz=random.uniform(480, 640) if big else random.uniform(170, 260),
                    rot=random.uniform(-40, 40), w=random.uniform(-260, 260), big=big, ic="euro"))
def billetes(lay, t, delante):
    for b in BIL:
        if b["big"] != delante: continue
        d = t - b["t"]
        if d < 0 or d > 1.4: continue
        dirx = 1 if b["x0"] < 0 else -1; x = b["x0"] + dirx * (1500 if b["big"] else 950) * d
        y = b["y0"] + b["vy"] * d
        if b["big"] and abs(x - 540) < 260 and y < 1000: continue   # nunca delante de la cara
        im = ico(b["ic"], int(b["sz"])).rotate(b["rot"] + b["w"] * d, expand=True, resample=Image.BICUBIC)
        sx = 0.55 + 0.45 * abs(math.cos(d * 6 + b["rot"]))
        im = im.resize((max(2, int(im.width * sx)), im.height), Image.LANCZOS)
        im = im.filter(ImageFilter.GaussianBlur(10 if b["big"] else 1.5))
        paste_c(lay, im, x, y)

GIG = [("CANTABRIA", TC, CUT[1], "detras"), ("A CÁMARA", TCAM - .04, CUT[3], "pecho"), ("REMUNERADO", CUT[3] + .46, CUT[4], "pecho")]
INV = CUT[1]   # fotograma invertido al entrar en la rejilla
def render(i):
    t = i / FPS; k = v1.tramo(t)
    frame = Image.open(f"fr/{i+1:04d}.jpg").convert("RGB")
    if k == 1:
        out = v1.escena_b(frame, Image.open(f"mk/{i+1:04d}.png").convert("L"), t)
        lt = t - CUT[1]; sc = 1.0 + 0.10 * (1 - spring(lt / 0.35))
        if sc > 1.001: out = recorta(out, (W * (1 - 1 / sc) / 2, H * (1 - 1 / sc) / 2, W / sc, H / sc))
        for n, t0, t1, x, y, s, r in STK:
            if CUT[1] <= t0 < CUT[2]: sticker(out, t, n, t0, t1, x, y, s, r)
        for n, t0, t1, x, y, s in DROP:
            if CUT[1] <= t0 < CUT[2]: caida(out, t, n, t0, t1, x, y, s)
    elif k == 4:
        cx, cy, _ = cara(i); z = 1.30; sw, sh = W / z, H / z
        x0 = min(max(cx - sw / 2, 0), W - sw); y0 = min(max(cy - sh * 0.36, 0), H - sh)
        out = v1.escena_e(frame.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((W, H), Image.LANCZOS), t)
        tp = wt("privado", CUT[4]) + .05
        sticker(out, t, "sobre", tp, CUT[5], 880, 760, 200, 12)
    else:
        z = v2.zoom_at(t, k); cx, cy, _ = cara(i); sw, sh = W / z, H / z
        box = (min(max(cx - sw / 2, 0), W - sw), min(max(cy - sh * 0.33, 0), H - sh), sw, sh)
        out = recorta(frame, box).convert("RGBA"); out.alpha_composite(v1.GRAD)
        if k == 3: v1.leak(out, t, CUT[3] + 0.05); billetes(out, t, False)
        if k == 0: cascada(out, t)
        for txt, a, b, pos in GIG:
            if not (a - 0.01 <= t < b): continue
            if pos == "detras":
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); palabra(lay, txt, t, a, 540, 520); out.alpha_composite(lay)
                mk = recorta(Image.open(f"mk/{i+1:04d}.png").convert("L"), box).filter(ImageFilter.GaussianBlur(1.2))
                per = recorta(frame, box).convert("RGBA"); per.putalpha(mk); out.alpha_composite(per)
            else: palabra(out, txt, t, a, 540, 1330)
        for n, t0, t1, x, y, s, r in STK:
            if CUT[k] <= t0 < CUT[k + 1]: sticker(out, t, n, t0, t1, x, y, s, r)
        for n, t0, t1, x, y, s in DROP:
            if CUT[k] <= t0 < CUT[k + 1]: caida(out, t, n, t0, t1, x, y, s)
        v1.sub_layer(t, out); v1.esquinas(out, t, i)
        for a in v1.ARCOS: v1.arco(out, t, a)
        if k == 3: billetes(out, t, True)
    tb = v2.transicion(t)
    if tb: out = zoomblur(out, tb * 0.8)
    if 0 <= t - INV < 2 / FPS: out = ImageOps.invert(out.convert("RGB")).convert("RGBA")
    return out

if __name__ == "__main__":
    pass  # se trabaja en la carpeta del proyecto (la actual)
    if len(sys.argv) > 1 and sys.argv[1] == "fotos":
        os.makedirs("prev", exist_ok=True)
        for s in [float(x) for x in sys.argv[2:]]: render(int(s * FPS)).convert("RGB").save(f"prev/p_{s:05.2f}.jpg", quality=88)
        sys.exit()
    p = subprocess.Popen([v1.FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(render(i).convert("RGB").tobytes())
        if i % 60 == 0: print(i, NF, flush=True)
    p.stdin.close(); p.wait(); print("video ok")
