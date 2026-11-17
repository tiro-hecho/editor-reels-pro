# -*- coding: utf-8 -*-
# v2 «más épico»: cámara viva con rebote, temblor + RGB en golpes, palabras letra a letra con destello y rayos,
# CANTABRIA detrás de la cabeza, transiciones con zoom-blur, lluvia de monedas, chispas en primer plano.
import os, sys, math, json, subprocess, random, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1
from v1 import W, H, FPS, CUT, wt, ease, eio, F, ANTON, HNM, paste_c, cara, NF
random.seed(7)

# ---------- impactos y zooms ----------
GIG = [("CANTABRIA", wt("Cantabria"), CUT[1], "detras"),
       ("A CÁMARA", wt("cámara", CUT[2]) - 0.04, CUT[3], "pecho"),
       ("REMUNERADO", CUT[3] + 0.46, CUT[4], "pecho")]
# (t, zoom) por tramo; cada 2-3 palabras
ZK = {0: [(0.0, 1.22), (wt("agencia") - .02, 1.34), (wt("trabajamos") - .02, 1.24), (wt("negocios") - .02, 1.40), (wt("Cantabria") - .02, 1.18)],
      2: [(CUT[2], 1.20), (wt("guste", CUT[2]) - .02, 1.34), (wt("cámara", CUT[2]) - .06, 1.16), (wt("bien", CUT[2]) - .2, 1.30)],
      3: [(CUT[3], 1.42), (CUT[3] + 0.44, 1.22)]}
GOLPES = [g[1] for g in GIG] + [CUT[1], CUT[2], CUT[3], CUT[4]]
def spring(x):
    x = max(0, x); return 1 - math.exp(-7 * x) * math.cos(10 * x)
def zoom_at(t, k):
    ks = ZK[k]; z = ks[0][1]
    for i in range(1, len(ks)):
        t0, z1 = ks[i]
        if t >= t0: z = ks[i - 1][1] + (z1 - ks[i - 1][1]) * spring((t - t0) / 0.30) if t - t0 < 0.6 else z1
    return z * (1 + 0.02 * (t - CUT[k]))
def shake(t):
    dx = dy = 0.0; rgb = 0.0
    for g in GOLPES:
        d = t - g
        if 0 <= d < 0.35:
            a = math.exp(-d * 14)
            dx += 22 * a * math.sin(d * 95); dy += 16 * a * math.cos(d * 80); rgb = max(rgb, 12 * math.exp(-d * 20))
    return dx, dy, rgb

def encuadre(i, t, k):
    z = zoom_at(t, k); cx, cy, _ = cara(i); dx, dy, _ = shake(t)
    sw, sh = W / z, H / z
    x0 = min(max(cx - sw / 2 + dx / z, 0), W - sw); y0 = min(max(cy - sh * 0.33 + dy / z, 0), H - sh)
    return (x0, y0, sw, sh)
def recorta(im, box, mode=Image.LANCZOS):
    x0, y0, sw, sh = box
    return im.transform((W, H), Image.AFFINE, (sw / W, 0, x0, 0, sh / H, y0), resample=Image.BICUBIC)

# ---------- palabra letra a letra ----------
def letras(txt, size=230, maxw=900):
    f = F(ANTON, size); tw = sum(f.getlength(c) for c in txt) + 2 * (len(txt) - 1)
    s = min(1, maxw / tw); f = F(ANTON, int(size * s)); out = []; x = 0
    for c in txt:
        im = v1.grad_text(c, int(size * s)) if c != " " else None
        out.append((im, x + f.getlength(c) / 2)); x += f.getlength(c) + 2
    return out, x
GL = {g[0]: letras(g[0], 260 if g[3] == "detras" else 230, 1000 if g[3] == "detras" else 900) for g in GIG}
def palabra(lay, txt, t, a, cx, cy):
    ls, tw = GL[txt]
    for n, (im, x) in enumerate(ls):
        if im is None: continue
        d = t - a - n * 0.03; k = ease(d / 0.16)
        if k <= 0: continue
        sc = 1.7 - 0.7 * k
        gl = v1.glow(im, 22, (255, 180, 30), 0.65)
        px = cx - tw / 2 + x; py = cy - (1 - k) * 90
        paste_c(lay, gl, px, py, sc, k * (0.75 + 0.25 * math.sin(t * 6)))
        paste_c(lay, im, px, py, sc, k, (1 - k) * 16)
    # brillo que recorre la palabra
    p = (t - a - 0.45) / 0.45
    if 0 <= p <= 1:
        x = cx - tw / 2 + (tw + 200) * p - 100
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x - 30, cy - 130), (x + 40, cy - 130), (x + 0, cy + 130), (x - 70, cy + 130)], fill=(255, 255, 230, 150))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        m = Image.new("L", (W, H));
        for im, xx in ls:
            if im is not None: m.paste(im.split()[3], (int(cx - tw / 2 + xx - im.width / 2), int(cy - im.height / 2)), im.split()[3])
        sh.putalpha(Image.fromarray(np.minimum(np.array(sh.split()[3]), np.array(m))))
        lay.alpha_composite(sh)

def rayos(lay, t, a, cx, cy):
    d = t - a
    if not (0 <= d < 0.6): return
    k = ease(d / 0.15) * (1 - eio((d - 0.2) / 0.4))
    m = np.zeros((H // 2, W // 2), np.float32)
    for n in range(18):
        ang = n / 18 * 2 * math.pi + d * 0.8; L = 900
        x1 = cx / 2 + math.cos(ang) * L / 2; y1 = cy / 2 + math.sin(ang) * L / 2
        cv2.line(m, (int(cx / 2), int(cy / 2)), (int(x1), int(y1)), 1.0, 7 if n % 2 else 3, cv2.LINE_AA)
    rr = np.hypot(*np.meshgrid(np.arange(W // 2) - cx / 2, np.arange(H // 2) - cy / 2))
    m = cv2.GaussianBlur(m, (0, 0), 6) * np.exp(-(rr / 330) ** 2) * k
    m = cv2.resize(m, (W, H))
    g = np.zeros((H, W, 4), np.uint8); g[..., 0] = 255; g[..., 1] = 205; g[..., 2] = 90; g[..., 3] = np.clip(m * 200, 0, 255).astype(np.uint8)
    lay.alpha_composite(Image.fromarray(g, "RGBA"))

# ---------- monedas ----------
def moneda(r):
    s = int(r * 2 + 8); im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(int(r), 0, -1):
        f = k / r; c = (int(180 + 70 * (1 - f) ** .5), int(130 + 80 * (1 - f) ** .5), int(30 + 40 * (1 - f)))
        d.ellipse((s / 2 - k, s / 2 - k, s / 2 + k, s / 2 + k), fill=c + (255,))
    d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=(255, 236, 160, 255), width=max(2, int(r * .08)))
    d.ellipse((s / 2 - r * .78, s / 2 - r * .78, s / 2 + r * .78, s / 2 + r * .78), outline=(150, 100, 20, 255), width=max(1, int(r * .04)))
    fe = F(ANTON, int(r * 1.0)); d.text((s / 2, s / 2), "€", font=fe, fill=(255, 240, 180, 255), anchor="mm")
    return im
MON = []
T0M = CUT[3] + 0.40
for n in range(22):
    big = n < 4
    MON.append(dict(x=(random.choice([random.uniform(40, 200), random.uniform(880, 1040)]) if big else random.choice([random.uniform(50, 330), random.uniform(750, 1030)])), r=random.uniform(150, 210) if big else random.uniform(45, 85), t=T0M + random.uniform(-.1, .6),
                    v=random.uniform(1700, 2400) if big else random.uniform(900, 1500), w=random.uniform(4, 9), ph=random.uniform(0, 6), big=big))
for m in MON: m["im"] = moneda(m["r"])
def monedas(lay, t, delante):
    for m in MON:
        if m["big"] != delante: continue
        d = t - m["t"]
        if d < 0: continue
        y = -250 + m["v"] * d
        if y > H + 300: continue
        sx = abs(math.cos(m["ph"] + d * m["w"])); im = m["im"]
        im = im.resize((max(2, int(im.width * max(.12, sx))), im.height), Image.LANCZOS)
        im = im.rotate(math.degrees(m["ph"]) % 40 - 20, expand=True, resample=Image.BICUBIC)
        if m["big"]: im = im.filter(ImageFilter.GaussianBlur(9))
        else: im = im.filter(ImageFilter.BoxBlur(1))
        paste_c(lay, im, m["x"], y)

# ---------- chispas ----------
CH = [dict(x=random.uniform(0, W), y=random.uniform(0, H), r=random.uniform(2, 7), v=random.uniform(30, 90), ph=random.uniform(0, 6)) for _ in range(40)]
def chispas(lay, t):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for c in CH:
        y = (c["y"] - c["v"] * t) % H; x = c["x"] + 20 * math.sin(t + c["ph"])
        a = int(110 + 90 * math.sin(t * 3 + c["ph"]))
        d.ellipse((x - c["r"], y - c["r"], x + c["r"], y + c["r"]), fill=(255, 210, 120, max(0, a)))
    lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(2.2)))

# ---------- efectos de imagen ----------
def zoomblur(im, amt):
    if amt < 0.01: return im
    a = np.asarray(im.convert("RGB"), np.float32); acc = a.copy(); n = 7
    for k in range(1, n):
        s = 1 + amt * k / n; M = cv2.getRotationMatrix2D((W / 2, H * .42), 0, s)
        acc += cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return Image.fromarray((acc / n).astype(np.uint8)).convert("RGBA")
def rgbsplit(im, px):
    if px < 1: return im
    a = np.asarray(im.convert("RGB")).copy(); s = int(px)
    a[:, s:, 0] = a[:, :-s, 0]; a[:, :-s, 2] = np.asarray(im.convert("RGB"))[:, s:, 2]
    return Image.fromarray(a).convert("RGBA")
def flash(im, t):
    a = 0
    for g in GOLPES:
        d = t - g
        if 0 <= d < 0.12: a = max(a, 0.28 * (1 - d / 0.12))
    if a <= 0: return im
    w = Image.new("RGBA", (W, H), (255, 250, 235, int(255 * a))); im.alpha_composite(w); return im
def transicion(t):
    for c in CUT[1:-1]:
        d = t - c
        if -0.10 <= d < 0: return 0.35 * (1 + d / 0.10)
        if 0 <= d < 0.14: return 0.35 * (1 - d / 0.14)
    return 0

def render(i):
    t = i / FPS; k = v1.tramo(t)
    frame = Image.open(f"fr/{i+1:04d}.jpg").convert("RGB")
    if k == 1:
        out = v1.escena_b(frame, Image.open(f"mk/{i+1:04d}.png").convert("L"), t)
        lt = t - CUT[1]; sc = 1.0 + 0.10 * (1 - spring(lt / 0.35))
        if sc > 1.001:
            box = (W * (1 - 1 / sc) / 2, H * (1 - 1 / sc) / 2, W / sc, H / sc); out = recorta(out, box)
    elif k == 4:
        cx, cy, _ = cara(i); z = 1.30; sw, sh = W / z, H / z
        x0 = min(max(cx - sw / 2, 0), W - sw); y0 = min(max(cy - sh * 0.36, 0), H - sh)
        out = v1.escena_e(frame.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((W, H), Image.LANCZOS), t)
    else:
        box = encuadre(i, t, k)
        out = recorta(frame, box).convert("RGBA"); out.alpha_composite(v1.GRAD)
        if k == 3: v1.leak(out, t, CUT[3] + 0.05); monedas(out, t, False)
        for txt, a, b, pos in GIG:
            if not (a - 0.01 <= t < b): continue
            if pos == "detras":
                cy = max(330, int(cara(i)[1] - 40)); cy = 520
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rayos(lay, t, a, 540, cy); palabra(lay, txt, t, a, 540, cy)
                out.alpha_composite(lay)
                mk = recorta(Image.open(f"mk/{i+1:04d}.png").convert("L"), box).filter(ImageFilter.GaussianBlur(1.2))
                per = recorta(frame, box).convert("RGBA"); per.putalpha(mk); out.alpha_composite(per)
            else:
                rayos(out, t, a, 540, 1330); palabra(out, txt, t, a, 540, 1330)
        if k == 2 and t >= v1.TREC:
            kk = ease((t - v1.TREC) / 0.25); im = v1.REC.rotate(-14 * (1 - kk) + 8, expand=True, resample=Image.BICUBIC)
            paste_c(out, im, 830, 560, 0.6 + 0.4 * kk, kk)
        # subtítulos (sin la línea de CANTABRIA, que ya está arriba)
        v1.sub_layer(t, out); v1.esquinas(out, t, i)
        for a in v1.ARCOS: v1.arco(out, t, a)
        if k == 3: monedas(out, t, True)
        chispas(out, t)
    tb = transicion(t)
    if tb: out = zoomblur(out, tb)
    _, _, rg = shake(t); out = rgbsplit(out, rg); out = flash(out, t)
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
