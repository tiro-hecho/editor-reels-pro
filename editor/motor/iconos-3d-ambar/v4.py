# -*- coding: utf-8 -*-
# v4: iconos en 3D de verdad (canto extruido + perspectiva, giran al entrar y se balancean), SIN sombras,
# tarjetas con radio pequeño; una transición distinta en cada corte.
import os, sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1, v2, v3
from v1 import W, H, FPS, CUT, wt, ease, eio, F, HNB, paste_c, cara, NF

_c = {}
def plano_ico(n, size):
    k = (n, size)
    if k not in _c:
        im = Image.open(os.path.join(v3.IC, n + ".png")).convert("RGBA"); s = size / max(im.size)
        _c[k] = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    return _c[k]

def obj3d(im, ry, rx=0.0, depth=14, edge=None):
    """im RGBA -> objeto con canto y perspectiva. ry/rx en grados."""
    a = np.asarray(im, np.float32); h, w = a.shape[:2]; P = int(max(w, h) * 0.45) + depth * 2
    big = np.zeros((h + 2 * P, w + 2 * P, 4), np.float32)
    syr, sxr = math.sin(math.radians(ry)), math.sin(math.radians(rx))
    side = a.copy()
    if edge is None: side[..., :3] *= 0.52
    else: side[..., :3] = np.array(edge, np.float32)[None, None, :] * (side[..., 3:4] > 0)
    n = max(2, depth)
    for k in range(n, 0, -1):       # canto: copias desplazadas detrás
        ox = int(round(-syr * depth * k / n)); oy = int(round(sxr * depth * k / n))
        sl = side.copy(); sl[..., :3] *= 0.85 + 0.15 * (1 - k / n)
        y0, x0 = P + oy, P + ox; reg = big[y0:y0 + h, x0:x0 + w]
        al = sl[..., 3:4] / 255; reg[..., :3] = reg[..., :3] * (1 - al) + sl[..., :3] * al; reg[..., 3:4] = np.maximum(reg[..., 3:4], sl[..., 3:4])
    reg = big[P:P + h, P:P + w]; al = a[..., 3:4] / 255
    # cara frontal con un brillo especular suave que depende del giro
    g = np.linspace(-1, 1, w)[None, :, None]; spec = np.clip(1 - np.abs(g + syr * 1.4) * 2.2, 0, 1) * 38
    front = np.clip(a[..., :3] + spec, 0, 255)
    reg[..., :3] = reg[..., :3] * (1 - al) + front * al; reg[..., 3:4] = np.maximum(reg[..., 3:4], a[..., 3:4])
    # perspectiva
    HH, WW = big.shape[:2]; cx, cy = WW / 2, HH / 2; cyr, cxr = math.cos(math.radians(ry)), math.cos(math.radians(rx))
    hw, hh = w / 2 * cyr, h / 2 * cxr; py = 0.22 * syr * h / 2; px = 0.22 * sxr * w / 2
    src = np.float32([[P, P], [P + w, P], [P + w, P + h], [P, P + h]])
    dst = np.float32([[cx - hw - px, cy - hh + py], [cx + hw + px, cy - hh - py], [cx + hw - px, cy + hh + py], [cx - hw + px, cy + hh - py]])
    M = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(big, M, (WW, HH), flags=cv2.INTER_LINEAR)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")

def giro(d, t, seed):
    """giro en Y: entra girando 300° y se queda balanceando"""
    if d < 0.45: ry = 300 * (1 - ease(d / 0.45)) ** 1.0
    else: ry = 0
    ry += 28 * math.sin(t * 2.2 + seed); rx = 16 * math.sin(t * 1.7 + seed * 2)
    ry = ((ry + 180) % 360) - 180
    if abs(ry) > 80: ry = math.copysign(80, ry)    # nunca de canto puro
    return ry, rx

def sticker(lay, t, n, t0, t1, x, y, size, rot):
    d = t - t0
    if d < 0 or t >= t1 + 0.15: return
    k = v3.pop_k(d); out = 1 - eio((t - t1) / 0.15) if t > t1 else 1
    ry, rx = giro(d, t, x * 0.01)
    im = obj3d(plano_ico(n, size), ry, rx, depth=max(16, size // 8))
    im = im.rotate(rot * 0.5 + 2 * math.sin(t * 2 + y), expand=True, resample=Image.BICUBIC)
    paste_c(lay, im, x, y + 8 * math.sin(t * 3.1 + y), max(0.01, k * out), min(1, k * 1.5) * out, max(0, 1 - d / 0.10) * 5)

def caida(lay, t, n, t0, t1, x, y, size):
    d = t - t0
    if d < 0 or t >= t1: return
    p = min(1, d / 0.28); yy = y - 420 * (1 - p) ** 2
    if p >= 1:
        e = d - 0.28; yy = y - 40 * abs(math.sin(e * 11)) * math.exp(-e * 7)
    ry, rx = 25 * math.sin(t * 2.4), 12 * math.sin(t * 1.9)
    if d < 0.28: ry = 200 * (1 - p)
    im = obj3d(plano_ico(n, size), ((ry + 180) % 360) - 180 if abs(((ry + 180) % 360) - 180) < 80 else 70, rx, depth=12)
    paste_c(lay, im, x, yy, 1, min(1, d / 0.08), (1 - p) * 4)

def tarjeta(icon, txt):
    w, h = 230, 270; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 6, fill=(255, 255, 255, 255))
    d.rounded_rectangle((12, 12, w - 13, 196), 3, fill=(243, 236, 222, 255))
    ic = plano_ico(icon, 150); c.alpha_composite(ic, (int(w / 2 - ic.width / 2), int(104 - ic.height / 2)))
    d.text((w / 2, 232), txt, font=F(HNB, 30), fill=(30, 30, 30, 255), anchor="mm")
    return c
CARDS = [tarjeta(i, t) for i, t in v3.NEG]
def cascada(lay, t):
    for k, (c, t0) in enumerate(zip(CARDS, v3.TCARD)):
        d = t - t0; t1 = v3.TC - 0.05
        if d < 0 or t > t1 + 0.18: continue
        x, y, r = v3.POS[k]; p = ease(d / 0.30)
        out = 1 - eio((t - t1) / 0.18) if t > t1 else 1
        ry = 70 * (1 - p) + 14 * math.sin(t * 2 + k); rx = -40 * (1 - p) + 8 * math.sin(t * 1.6 + k)
        im = obj3d(c, ry, rx, depth=9, edge=(205, 200, 190)).rotate(r + (1 - p) * 20, expand=True, resample=Image.BICUBIC)
        paste_c(lay, im, x - (1 - out) * 300, y - 260 * (1 - p) + 5 * math.sin(t * 2.5 + k), 0.85 + 0.15 * p, min(1, p * 2) * out, (1 - p) * 6)
    d = t - v3.TCARD[0]
    if 0 <= d < v3.TC - v3.TCARD[0]:
        a = min(1, d / 0.2) * (1 - eio((t - (v3.TC - .25)) / .25))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle((0, 960, 500 * min(1, d / 0.35), 1420), fill=(255, 200, 40, int(120 * a)))
        lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))

def billetes(lay, t, delante):
    import random
    for b in v3.BIL:
        if b["big"] != delante: continue
        d = t - b["t"]
        if d < 0 or d > 1.4: continue
        dirx = 1 if b["x0"] < 0 else -1; x = b["x0"] + dirx * (1500 if b["big"] else 950) * d; y = b["y0"] + b["vy"] * d
        if b["big"] and abs(x - 540) < 260 and y < 1000: continue
        im = obj3d(plano_ico("euro", int(b["sz"])), 60 * math.sin(d * 7 + b["rot"]), 35 * math.cos(d * 5 + b["rot"]), depth=6)
        im = im.rotate(b["rot"] + b["w"] * d, expand=True, resample=Image.BICUBIC).filter(ImageFilter.GaussianBlur(10 if b["big"] else 1.2))
        paste_c(lay, im, x, y)

# ---------- transiciones: una distinta en cada corte ----------
def mblur(im, n, horiz=True):
    if n < 2: return im
    a = np.asarray(im.convert("RGB")); k = np.ones((1, n), np.float32) / n
    if not horiz: k = k.T
    return Image.fromarray(cv2.filter2D(a, -1, k, borderType=cv2.BORDER_REFLECT)).convert("RGBA")
def desplaza(im, dx, dy):
    a = np.asarray(im); a = np.roll(a, int(dx), 1); a = np.roll(a, int(dy), 0); return Image.fromarray(a)
TRANS = {1: "barrido_h", 2: "zoom", 3: "barrido_v", 4: "zoom_suave"}
def transicion(out, t):
    for j, kind in TRANS.items():
        c = CUT[j]; d = t - c
        if not (-0.12 <= d < 0.16): continue
        if kind in ("barrido_h", "barrido_v"):
            hz = kind == "barrido_h"
            if d < 0: p = (d + 0.12) / 0.12; off = -(p ** 2) * (W if hz else H) * 0.35; bl = int(10 + 140 * p)
            else: p = d / 0.16; off = (1 - ease(p)) * (W if hz else H) * 0.35; bl = int(150 * (1 - p))
            out = desplaza(out, off if hz else 0, 0 if hz else off); out = mblur(out, bl, hz)
            if kind == "barrido_v" and 0 <= d < 0.2:
                fl = Image.new("RGBA", (W, H), (255, 236, 190, int(140 * (1 - d / 0.16)))); out.alpha_composite(fl)
        else:
            amt = 0.35 if kind == "zoom" else 0.18
            a = amt * ((1 + d / 0.12) if d < 0 else (1 - d / 0.16)); out = v2.zoomblur(out, a)
        return out
    return out

def render(i):
    t = i / FPS
    v3.sticker, v3.caida, v3.cascada, v3.billetes = sticker, caida, cascada, billetes
    v2.transicion = lambda tt: 0
    out = v3.render(i)
    out = transicion(out, t)
    return out

if __name__ == "__main__":
    pass  # se trabaja en la carpeta del proyecto (la actual)
    v3.sticker, v3.caida, v3.cascada, v3.billetes = sticker, caida, cascada, billetes
    v2.transicion = lambda tt: 0
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
