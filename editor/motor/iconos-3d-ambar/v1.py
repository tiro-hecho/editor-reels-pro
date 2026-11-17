# -*- coding: utf-8 -*-
# Estilo «iconos-3d-ambar»: capa base (encuadre, subtítulos de dos niveles, arco de luz, esquinas, rejilla). Ver editor/estilos/iconos-3d-ambar.md
import os, sys, json, math, subprocess, sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rutas_estilo import FF, ANTON, INTER, INTER_B, MUSICA
pass  # se trabaja en la carpeta del proyecto (la actual)
MUS = MUSICA
W, H, FPS = 1080, 1920, 30
C = json.load(open("cuts.json", encoding="utf8")); CUT = C["cuts"]; PAL = C["pal"]
CAR = json.load(open("caras.json")) if os.path.exists("caras.json") else {}
HNM = INTER; HNB = INTER_B; HNC = ANTON   # Inter y Poppins en lugar de Helvetica (de pago)
NF = int(round(CUT[-1] * FPS))
def F(p, s): return ImageFont.truetype(p, s)
def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def eio(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def wt(word, after=0):
    for a, b, w in PAL:
        if a >= after - 0.05 and word.lower() in w.lower(): return a
    raise KeyError(word)

# ---------- cara (suavizada) ----------
def cara(i):
    ks = sorted(CAR.keys())
    if not ks: return (540, 640, 260)
    f = f"{i+1:04d}.jpg"
    near = [k for k in ks if abs(int(k[:4]) - (i + 1)) <= 6] or [min(ks, key=lambda k: abs(int(k[:4]) - (i + 1)))]
    a = np.array([CAR[k] for k in near], float).mean(0)
    return (a[0] + a[2] / 2, a[1] + a[3] / 2, a[2])

# ---------- capas ----------
def grad_text(txt, size, top=(255, 228, 92), bot=(246, 150, 30), font=ANTON, track=0):
    f = F(font, size); bb = f.getbbox(txt); w = bb[2] - bb[0] + track * len(txt) + 40; h = bb[3] + 30
    m = Image.new("L", (w, h)); d = ImageDraw.Draw(m)
    x = 20
    for ch in txt:
        d.text((x, 10), ch, font=f, fill=255); x += f.getlength(ch) + track
    g = np.zeros((h, w, 3), np.float32); yy = np.linspace(0, 1, h)[:, None]
    yy = np.clip((yy * h - (10 + bb[1])) / max(1, bb[3] - bb[1]), 0, 1)
    for c in range(3): g[:, :, c] = top[c] + (bot[c] - top[c]) * yy
    im = Image.fromarray(g.astype(np.uint8)).convert("RGBA"); im.putalpha(m)
    return im
def glow(im, rad=18, col=(255, 190, 40), k=0.55):
    a = im.split()[3].filter(ImageFilter.GaussianBlur(rad))
    g = Image.new("RGBA", im.size, col + (0,)); g.putalpha(a.point(lambda v: int(v * k)))
    return g
def paste_c(base, im, cx, cy, sc=1.0, alpha=1.0, blur=0):
    if sc != 1: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    if blur > 0.4: im = im.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1:
        a = im.split()[3].point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

# grandes palabras: (texto, t_entrada, t_salida, y_centro)
GIG = [("CANTABRIA", wt("Cantabria"), CUT[1] - 0.02, 1330),
       ("A CÁMARA", wt("cámara", CUT[2]) - 0.04, CUT[3] - 0.02, 1330),
       ("REMUNERADO", CUT[3] + 0.50, CUT[4] - 0.02, 1330)]
def fit(im, mw=900):
    return im if im.width <= mw else im.resize((mw, int(im.height * mw / im.width)), Image.LANCZOS)
GIMG = {g[0]: fit(grad_text(g[0], 230, track=2), 780) for g in GIG}
GGLO = {k: glow(v) for k, v in GIMG.items()}

# subtitulos pequeños (por tramos) — los de la escena B y E van aparte
LINEAS = [(0, CUT[1], ["Desde", "nuestra", "agencia", "de", "marketing"]),
          (0, CUT[1], ["trabajamos", "con", "negocios", "de"]),
          (CUT[2], CUT[3], ["Simplemente", "que", "te", "guste", "hablar"]),
          (CUT[3], CUT[4], ["Evidentemente"])]
FS = F(HNM, 42)
def palabras_linea(t0, t1, ws):
    out = []; after = t0
    for w in ws:
        try: a = wt(w, after)
        except KeyError: continue
        if a > t1: break
        out.append((w, a)); after = a + 0.01
    return out
LW = [(t0, t1, palabras_linea(t0, t1, ws)) for t0, t1, ws in LINEAS]
# las dos primeras lineas: la segunda sustituye a la primera
def sub_layer(t, lay):
    for idx, (t0, t1, ws) in enumerate(LW):
        if not ws or not (t0 <= t < t1): continue
        nxt = LW[idx + 1][2][0][1] if idx + 1 < len(LW) and LW[idx + 1][0] == t0 and LW[idx + 1][2] else 99
        if t >= nxt: continue
        if t < ws[0][1] - 0.02: continue
        # para que la linea de la palabra gigante quede encima de ella
        gig = [g for g in GIG if g[1] - 0.6 <= t < g[2] and t0 <= g[1] < t1]
        y = 1190 if gig else 1260
        txt = " ".join(w for w, _ in ws); tw = FS.getlength(txt); x = 540 - tw / 2
        for w, a in ws:
            k = ease((t - a) / 0.14)
            if k > 0:
                im = Image.new("RGBA", (int(FS.getlength(w)) + 30, 70), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((15, 8), w, font=FS, fill=(255, 255, 255, 255))
                paste_c(lay, im, x + FS.getlength(w) / 2, y + (1 - k) * 10, 1, k, (1 - k) * 6)
            x += FS.getlength(w + " ")

# ---------- arco de luz ----------
ARCOS = [0.05, CUT[3] + 0.02, CUT[4] + 0.40]
def arco(lay, t, t0, cx=540, cy=980, r=760):
    p = (t - t0) / 0.75
    if not (0 <= p <= 1.25): return
    head = -168 + 156 * ease(min(p, 1)); tail = head - 70
    fade = 1 - max(0, (p - 1) / 0.25)
    m = np.zeros((H, W), np.float32)
    for k in range(24):
        a0 = tail + (head - tail) * k / 24; a1 = tail + (head - tail) * (k + 1) / 24
        cv2.ellipse(m, (cx, cy), (r, int(r * 0.92)), 0, a0, a1, float((k + 1) / 24), 4, cv2.LINE_AA)
    g = cv2.GaussianBlur(m, (0, 0), 14) * 3.0 + cv2.GaussianBlur(m, (0, 0), 3) * 1.2 + m
    g = np.clip(g * fade, 0, 1)
    col = np.zeros((H, W, 4), np.float32); col[..., 0] = 255; col[..., 1] = 236; col[..., 2] = 170; col[..., 3] = g * 255
    lay.alpha_composite(Image.fromarray(col.astype(np.uint8), "RGBA"))

# ---------- esquinas de enfoque ----------
ESQ = [(0.95, 2.05), (CUT[2] + 0.10, CUT[2] + 1.00)]
def esquinas(lay, t, i):
    for t0, t1 in ESQ:
        if not (t0 <= t < t1): continue
        cx, cy, fw = cara(i); k = ease((t - t0) / 0.16); out = 1 - eio((t - (t1 - 0.12)) / 0.12)
        s = (1.55 - 0.45 * k) * fw * 0.62; a = int(255 * min(k, out))
        d = ImageDraw.Draw(lay); L = 30
        for sx in (-1, 1):
            for sy in (-1, 1):
                x, y = cx + sx * s, cy + sy * s * 1.05
                d.line([(x, y), (x - sx * L, y)], fill=(255, 255, 255, a), width=6)
                d.line([(x, y), (x, y - sy * L)], fill=(255, 255, 255, a), width=6)

# ---------- pegatina REC ----------
def rec_sticker():
    im = Image.new("RGBA", (300, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 290, 110), 50, fill=(236, 40, 40, 255))
    d.ellipse((42, 42, 78, 78), fill=(255, 255, 255, 255))
    d.text((98, 26), "REC", font=F(HNB, 58), fill=(255, 255, 255, 255))
    return im
REC = rec_sticker(); TREC = wt("cámara", CUT[2]) + 0.10

# ---------- escena B: rejilla blanca ----------
def escena_b(fr, mk, t):
    lt = t - CUT[1]
    bg = Image.new("RGBA", (W, H), (244, 243, 240, 255)); d = ImageDraw.Draw(bg)
    for x in (150, 540, 930):
        for y in range(0, H, 22): d.line([(x, y), (x, y + 10)], fill=(200, 200, 196, 255), width=2)
    for y in (300, 560):
        for x in range(0, W, 22): d.line([(x, y), (x + 10, y)], fill=(200, 200, 196, 255), width=2)
    for x in (150, 540, 930):
        for y in (300, 560): d.rectangle((x - 7, y - 7, x + 7, y + 7), fill=(240, 120, 40, 255))
    # el, en B/N, recortado
    g = cv2.cvtColor(np.array(fr), cv2.COLOR_RGB2GRAY); g = cv2.convertScaleAbs(g, alpha=1.12, beta=-6)
    p = Image.fromarray(np.dstack([g, g, g])).convert("RGBA"); p.putalpha(mk)
    sc = 0.92 + 0.03 * ease(lt / 2.2)
    p = p.resize((int(W * sc), int(H * sc)), Image.LANCZOS)
    # circulo amarillo detras de la cabeza
    k = ease((lt - 0.10) / 0.30)
    if k > 0:
        r = 190 * k; cy = 300 + 640 * sc * 0 + 690
        d.ellipse((540 - r, cy - r, 540 + r, cy + r), fill=(255, 205, 50, 255))
    bg.alpha_composite(p, (int(540 - p.width / 2), int(H - p.height + 80)))
    # titulo
    ws = ["Nuestra", "idea", "es", "crear", "una", "base", "de", "datos", "de"]
    pal = palabras_linea(CUT[1], CUT[2], ws); f = F(HNM, 36); txt = " ".join(w for w, _ in pal)
    x = 540 - f.getlength(txt) / 2
    for w, a in pal:
        kk = ease((t - a) / 0.14)
        if kk > 0:
            im = Image.new("RGBA", (int(f.getlength(w)) + 30, 70), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((15, 8), w, font=f, fill=(25, 25, 25, 255)); paste_c(bg, im, x + f.getlength(w) / 2, 380 + (1 - kk) * 10, 1, kk, (1 - kk) * 6)
        x += f.getlength(w + " ")
    tc = wt("colaboradores", CUT[1])
    kk = ease((t - tc) / 0.18)
    if kk > 0:
        im = Image.new("RGBA", (1080, 190), (0, 0, 0, 0)); fb = F(ANTON, 124)
        ImageDraw.Draw(im).text((540 - fb.getlength("COLABORADORES") / 2, 5), "COLABORADORES", font=fb, fill=(18, 18, 18, 255))
        paste_c(bg, im, 540, 480, 1.18 - 0.18 * kk, kk, (1 - kk) * 10)
    return bg

# ---------- escena E: tarjeta en fondo crema con pastillas ----------
PILLS = [("Eres de Cantabria", wt("Cantabria", CUT[4]) - 0.05, (232, 112, 40)),
         ("Te gusta hablar a cámara", wt("encaja", CUT[4]) - 0.10, (96, 92, 34)),
         ("Mándanos un privado", wt("privado", CUT[4]) - 0.25, (140, 58, 26))]
def pill(txt, col):
    f = F(HNM, 44); w = int(f.getlength(txt)) + 130
    im = Image.new("RGBA", (w, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = tuple(min(255, c + 40) for c in col)
    g = np.zeros((96, w, 4), np.uint8)
    for y in range(96):
        k = y / 95; g[y, :, :3] = [int(top[c] + (col[c] - top[c]) * k) for c in range(3)]
    m = Image.new("L", (w, 96)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, 95), 48, fill=255)
    im = Image.fromarray(g, "RGBA"); im.putalpha(m); d = ImageDraw.Draw(im)
    cx, cy, r = 58, 48, 15
    d.polygon([(cx, cy - r), (cx + 4, cy - 4), (cx + r, cy), (cx + 4, cy + 4), (cx, cy + r), (cx - 4, cy + 4), (cx - r, cy), (cx - 4, cy - 4)], fill=(255, 245, 220, 255))
    d.text((92, 22), txt, font=f, fill=(255, 255, 255, 255))
    return im
PIM = [pill(a, c) for a, _, c in PILLS]
def escena_e(frame, t):
    lt = t - CUT[4]; k = ease(lt / 0.40)
    bg = Image.new("RGBA", (W, H), (250, 244, 232, 255)); d = ImageDraw.Draw(bg)
    for y in range(40, H, 60):
        for x in range(30, W, 60): d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(225, 215, 198, 255))
    # brillo calido abajo
    gl = np.zeros((H, W, 4), np.uint8); yy = np.linspace(0, 1, H)[:, None]
    gl[..., 0] = 255; gl[..., 1] = 214; gl[..., 2] = 150; gl[..., 3] = (np.clip((yy - 0.6) / 0.4, 0, 1) * 120).astype(np.uint8)
    bg.alpha_composite(Image.fromarray(gl, "RGBA"))
    sc = 1 - 0.30 * k; cw, ch = int(W * sc), int(H * sc)
    cy = 960 + (1240 - 960) * k
    fr = frame.resize((cw, ch), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (cw, ch)); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), int(60 * k), fill=255); fr.putalpha(m)
    bg.alpha_composite(fr, (int(540 - cw / 2), int(cy - ch / 2)))
    for n, ((txt, a, col), im) in enumerate(zip(PILLS, PIM)):
        kk = ease((t - a) / 0.22)
        if kk <= 0: continue
        y = 250 + n * 112
        paste_c(bg, im, 540, y - (1 - kk) * 60, 0.9 + 0.1 * kk, kk, (1 - kk) * 8)
        # destello que recorre la pastilla al entrar
        fl = (t - a - 0.12) / 0.35
        if 0 <= fl <= 1:
            sh = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
            x = 540 - im.width / 2 + im.width * fl
            ds.polygon([(x - 20, 10), (x + 30, 10), (x + 10, 110), (x - 40, 110)], fill=(255, 255, 255, 110))
            sh = sh.filter(ImageFilter.GaussianBlur(6)); mm = Image.new("L", (W, 120))
            ImageDraw.Draw(mm).rounded_rectangle((540 - im.width / 2, 12, 540 + im.width / 2, 108), 48, fill=255)
            sh.putalpha(Image.fromarray(np.minimum(np.array(sh.split()[3]), np.array(mm)))); bg.alpha_composite(sh, (0, int(y - 60)))
    return bg

# ---------- plano normal ----------
ZOOM = {0: (1.28, 1.40), 2: (1.22, 1.38), 3: (1.45, 1.50)}  # (inicio, tras el punch)
PUNCH = {0: wt("trabajamos"), 2: wt("hablar", CUT[2]) - 0.02, 3: 99}
def tramo(t):
    for k in range(len(CUT) - 1):
        if CUT[k] <= t < CUT[k + 1]: return k
    return len(CUT) - 2
def plano(frame, t, k, i):
    z0, z1 = ZOOM[k]; z = z1 if t >= PUNCH[k] else z0
    z *= 1 + 0.015 * (t - CUT[k])
    cx, cy, _ = cara(i)
    sw, sh = W / z, H / z
    x0 = min(max(cx - sw / 2, 0), W - sw); y0 = min(max(cy - sh * 0.33, 0), H - sh)
    im = frame.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((W, H), Image.LANCZOS)
    # entrada desenfocada en cada corte y en el punch
    for t0 in (CUT[k], PUNCH[k]):
        d = t - t0
        if 0 <= d < 0.16: im = im.filter(ImageFilter.GaussianBlur(18 * (1 - d / 0.16)))
    return im.convert("RGBA")
GRAD = np.zeros((H, W, 4), np.uint8); yy = np.linspace(0, 1, H)[:, None]
GRAD[..., 3] = (np.clip((yy - 0.55) / 0.45, 0, 1) ** 1.4 * 200).astype(np.uint8); GRAD = Image.fromarray(GRAD, "RGBA")
def leak(lay, t, t0):
    p = (t - t0) / 0.9
    if not (0 <= p <= 1): return
    a = math.sin(math.pi * p)
    g = np.zeros((H, W, 4), np.uint8); xx = np.linspace(0, 1, W)[None, :]
    c = -0.3 + 1.4 * p
    v = np.exp(-((xx - c) / 0.30) ** 2) * a * 105
    g[..., 0] = 255; g[..., 1] = 196; g[..., 2] = 60; g[..., 3] = np.broadcast_to(v, (H, W)).astype(np.uint8)
    lay.alpha_composite(Image.fromarray(g, "RGBA"))

def render(i):
    t = i / FPS; k = tramo(t)
    frame = Image.open(f"fr/{i+1:04d}.jpg").convert("RGB")
    if k == 1:
        mk = Image.open(f"mk/{i+1:04d}.png").convert("L")
        out = escena_b(frame, mk, t)
        lt = t - CUT[1]
        if lt < 0.16: out = out.filter(ImageFilter.GaussianBlur(16 * (1 - lt / 0.16)))
        return out
    if k == 4:
        cx, cy, _ = cara(i); z = 1.30; sw, sh = W / z, H / z
        x0 = min(max(cx - sw / 2, 0), W - sw); y0 = min(max(cy - sh * 0.36, 0), H - sh)
        return escena_e(frame.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((W, H), Image.LANCZOS), t)
    out = plano(frame, t, k, i); out.alpha_composite(GRAD)
    if k == 3: leak(out, t, CUT[3] + 0.05)
    for txt, a, b, y in GIG:
        if a <= t < b:
            kk = ease((t - a) / 0.20)
            paste_c(out, GGLO[txt], 540, y, 1.25 - 0.25 * kk, kk * 0.9, 0)
            paste_c(out, GIMG[txt], 540, y, 1.25 - 0.25 * kk, kk, (1 - kk) * 14)
    if k == 2 and t >= TREC:
        kk = ease((t - TREC) / 0.25); im = REC.rotate(-14 * (1 - kk) + 8, expand=True, resample=Image.BICUBIC)
        paste_c(out, im, 830, 560, 0.6 + 0.4 * kk, kk)
    sub_layer(t, out); esquinas(out, t, i)
    for a in ARCOS: arco(out, t, a)
    return out

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "fotos":
        os.makedirs("prev", exist_ok=True)
        for s in [float(x) for x in sys.argv[2:]]:
            render(int(s * FPS)).convert("RGB").save(f"prev/p_{s:05.2f}.jpg", quality=88)
        sys.exit()
    p = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(render(i).convert("RGB").tobytes())
        if i % 60 == 0: print(i, NF, flush=True)
    p.stdin.close(); p.wait(); print("video ok")
