"""Motor de referencia: los 6 estilos predefinidos programados (subtítulos, glow, tarjeta, texto detrás, karaoke). La IA lo usa como base y lo adapta a cada vídeo: cambia WS (palabras con tiempos), los tramos TR y las posiciones según dónde esté la cara."""
import json, subprocess, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
F = os.environ.get("FUENTES", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "5-fuentes"))
WS = json.load(open("pal_corte.json")); DUR = 16.27
LIMA, CIAN, AMAR, BL, MOR = (215, 255, 58), (127, 243, 230), (255, 210, 31), (255, 255, 255), (178, 77, 255)
_f = {}
def font(n, sz, var=None):
    k = (n, sz, var)
    if k not in _f:
        f = ImageFont.truetype(f"{F}/{n}", sz)
        if var: f.set_variation_by_name(var)
        _f[k] = f
    return _f[k]
INTER = "Inter[opsz,wght].ttf"; MONT = "Montserrat[wght].ttf"; PLAY = "PlayfairDisplay-Italic[wght].ttf"; ARCH = "ArchivoBlack-Regular.ttf"; UNB = "Unbounded[wght].ttf"
cl = lambda x: min(1.0, max(0.0, x)); eo = lambda x: 1 - (1 - cl(x)) ** 3
def W_(i): return WS[i]
def idx(word, desde=0):
    return next(i for i, w in enumerate(WS) if w["w"].lower().strip(",.") == word and w["a"] >= desde)

def txt_img(t, f, col, track=0.0, glow=None, glow_r=14, halo=False):
    d0 = ImageDraw.Draw(Image.new("RGB", (4, 4))); sz = f.size
    anc = sum(d0.textlength(c, font=f) + sz * track for c in t) - sz * track
    w, h = int(anc + sz * 1.2), int(sz * 1.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = (w - anc) / 2
    for c in t: d.text((x, h / 2), c, font=f, fill=col + (255,), anchor="lm"); x += d.textlength(c, font=f) + sz * track
    if glow:
        g = Image.new("RGBA", (w, h), glow + (0,)); g.putalpha(im.split()[3].point(lambda v: int(v * 0.55))); g = g.filter(ImageFilter.GaussianBlur(glow_r))
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0)); sh.paste((0, 0, 0, 110), (0, 0), im.split()[3]); sh = sh.filter(ImageFilter.GaussianBlur(sz * 0.12))
        im = Image.alpha_composite(Image.alpha_composite(sh, g), im)
    if halo:
        hl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); hl.paste((0, 0, 0, 150), (0, 0), im.split()[3])
        im = Image.alpha_composite(hl.filter(ImageFilter.GaussianBlur(sz * 0.22)), im)
    return im, anc
def alfa(im, a):
    if a >= 0.999: return im
    r = im.copy(); r.putalpha(r.split()[3].point(lambda v: int(v * a))); return r
def pon(fr, im, cx, cy, a=1.0, s=1.0, izq=None):
    if a <= 0.01: return
    if izq is None and im.width * s > 0:   # nunca fuera de la zona segura (60-940): se reduce lo que no quepa
        bb = im.getbbox()
        if bb and (bb[2] - bb[0]) * s > 840: s = s * 840 / ((bb[2] - bb[0]) * s)
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    x = int(izq - (im.width - 0) * 0 if izq is not None else cx - im.width / 2)
    fr.alpha_composite(alfa(im, a), (x, int(cy - im.height / 2)))

# ---------------------------------------------------------------- tramos
TR = [(0.0, 6.55, "1 · Editorial contraste"), (6.55, 8.2, "2 · Minimal palabra"), (8.2, 10.15, "3 · Neón glow"),
      (10.15, 11.2, "4 · Texto detrás"), (11.2, 12.8, "5 · Gym documental"), (12.8, DUR, "6 · Elegante editorial")]
def etiqueta(fr, t):
    for a, b, n in TR:
        if a <= t < b:
            f = font(INTER, 34, "SemiBold"); im, anc = txt_img(n, f, BL, -0.01)
            pill = Image.new("RGBA", (int(anc + 56), 64), (0, 0, 0, 0)); ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, 63), 32, fill=(0, 0, 0, 150))
            pill.alpha_composite(im, (int((pill.width - im.width) / 2), int(32 - im.height / 2)))
            k = min((t - a) / 0.15, 1) * min((b - t) / 0.1, 1); pon(fr, pill, 500, 262, cl(k)); return

# 1 · Editorial contraste: frase fina + clave en negrita lima, apilado a la izquierda, arriba (hueco sobre la cabeza)
B1 = [  # (líneas [(texto, tipo, palabra-de-arranque)], t0, t1)
    ([("nosotros montamos", "fino", "nosotros"), ("un sistema", "clave", "sistema")], 0.0, 2.0),
    ([("que resuelve esa", "fino", "que"), ("intención de", "fino", "intención"), ("búsqueda", "clave", "búsqueda")], 2.0, 4.15),
    ([("cuando alguien", "fino", "para"), ("pregunte eso en", "fino", "pregunte"), ("internet", "clave", "internet")], 4.15, 6.55)]
def s1(fr, t):
    for lineas, t0, t1 in B1:
        if not (t0 <= t < t1): continue
        y = 1290 if len(lineas) == 2 else 1235; fo = min((t1 - t) / 0.12, 1)
        for txt, tipo, pal in lineas:
            ta = WS[idx(pal, t0 - 0.3)]["a"] - 0.05
            if tipo == "fino": f = font(MONT, 54, "Light"); col = BL; tr = -0.02; gl = None
            else: f = font(MONT, 100, "Black"); col = LIMA; tr = -0.035; gl = LIMA
            im, anc = txt_img(txt, f, col, tr, glow=gl, glow_r=10, halo=(tipo == 'fino'))
            e = eo((t - ta) / 0.18) if tipo == "fino" else eo((t - ta) / 0.14)
            if t >= ta:
                s = (0.85 + 0.15 * e + (0.06 * np.sin(np.pi * cl((t - ta) / 0.25)) if tipo == "clave" else 0))
                im2 = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
                fr.alpha_composite(alfa(im2, e * fo), (int(95 - (im.width - anc) / 2 * s), int(y + (1 - e) * 12 - im2.height / 2)))
            y += 60 if tipo == "fino" else 100

# 2 · Minimal palabra: una palabra en minúsculas, cada una en un sitio distinto, sin animación
POS2 = [(300, 1300), (790, 1060), (260, 1180), (780, 1330), (330, 1390), (770, 1180)]
def s2(fr, t):
    ws = [w for w in WS if 6.55 <= w["a"] < 8.2]
    for k, w in enumerate(ws):
        fin = ws[k + 1]["a"] - 0.03 if k + 1 < len(ws) else 8.2
        if w["a"] - 0.03 <= t < fin:
            im, _ = txt_img(w["w"].lower(), font(INTER, 84, "Medium"), BL, -0.02, halo=True); x, y = POS2[k % len(POS2)]
            x = min(max(x, 60 + im.width / 2 - 30), 940 - im.width / 2 + 30); pon(fr, im, x, y)

# 3 · Neón glow: mayúsculas anchas turquesa con brillo, vídeo en tarjeta con borde morado
G3 = [("LA INMOBILIARIA", 8.2, 8.9), ("QUE RESUELVE", 8.9, 9.45), ("ESA INTENCIÓN", 9.45, 9.85), ("DE BÚSQUEDA", 9.85, 10.15)]
def tarjeta(base, t, a, b):
    k = eo((t - a) / 0.2) * eo((b - t) / 0.2)
    if k <= 0.01: return base
    fondo = base.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(3)).resize((W, H)).point(lambda v: int(v * 0.55))
    s = 1 - 0.13 * k; cw, ch = int(W * s), int(H * s); peq = base.resize((cw, ch), Image.LANCZOS)
    m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, cw - 1, ch - 1), int(46 * k), fill=255)
    x0, y0 = (W - cw) // 2, int((H - ch) / 2 - 40 * k)
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(gl).rounded_rectangle((x0 - 4, y0 - 4, x0 + cw + 4, y0 + ch + 4), 50, outline=MOR + (int(255 * k),), width=9)
    gl = Image.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)), gl)
    out = fondo.convert("RGBA"); out.alpha_composite(gl); out.paste(peq, (x0, y0), m); return out
def s3(fr, t):
    for txt, a, b in G3:
        if a <= t < b:
            e = eo((t - a) / 0.12); im, _ = txt_img(txt, font(UNB, 76, "Bold"), CIAN, 0.0, glow=CIAN, glow_r=20)
            pon(fr, im, 500, 1250, e, 0.92 + 0.08 * e)

# 4 · Texto detrás: «TÚ» gigante entre el fondo y la persona
MK0 = 10.1
def s4(fr, t, base):
    if not (10.15 <= t < 11.2): return
    k = eo((t - 10.85) / 0.12) if t >= 10.85 else 0
    sub = [w for w in WS if 10.15 <= w["a"] < 10.85]
    vis = " ".join(w["w"] for w in sub if t >= w["a"] - 0.03).upper()
    if vis and t < 10.85:
        im, _ = txt_img(vis, font(INTER, 64, "Bold"), BL, -0.02, halo=True); pon(fr, im, 500, 1300)
    if k > 0:
        im, _ = txt_img("TÚ", font(INTER, 620, "Black"), LIMA, -0.04, glow=LIMA, glow_r=12)
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pon(capa, im, 520, 640, k, 0.9 + 0.1 * k)
        i = min(35, max(0, int(round((t - MK0) * FPS)))); m = Image.open(f"mk/{i + 1:03d}.png").convert("L").resize((W, H))
        capa.putalpha(Image.fromarray((np.array(capa.split()[3]) * (1 - np.array(m) / 255)).astype(np.uint8)))
        fr.alpha_composite(capa)

# 5 · Gym documental: una palabra en mayúsculas en el centro; la clave en amarillo y a dos pisos; flash de color
def s5(fr, t):
    ws = [w for w in WS if 11.2 <= w["a"] < 12.8]
    for k, w in enumerate(ws):
        fin = ws[k + 1]["a"] - 0.02 if k + 1 < len(ws) else 12.8
        if w["a"] - 0.02 <= t < fin:
            p = w["w"].upper()
            if p in ("INTELIGENCIA", "ARTIFICIAL"):
                a1, _ = txt_img("INTELIGENCIA", font(ARCH, 92), AMAR, -0.01); a2, _ = txt_img("ARTIFICIAL", font(ARCH, 92), AMAR if p == "ARTIFICIAL" else BL, -0.01)
                pon(fr, a1, 500, 1270); pon(fr, a2, 500, 1370, 1.0 if p == "ARTIFICIAL" else 0.0)
            else:
                im, _ = txt_img(p, font(ARCH, 66), BL, 0.0); sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 170), (0, 0), im.split()[3])
                pon(fr, sh.filter(ImageFilter.GaussianBlur(3)), 503, 1303); pon(fr, im, 500, 1300)
FLASH = (11.2, 11.27, (196, 160, 70))

# 6 · Elegante editorial: bloques de 1-3 palabras, Montserrat ExtraBold + Playfair en la emocional, karaoke
PLAYF = {"oficina"}; AMA6 = {"contactos"}
BLOQ = [[w for w in WS if 12.8 <= w["a"] < 13.35], [w for w in WS if 13.35 <= w["a"] < 14.07], [w for w in WS if 14.07 <= w["a"] < 14.81], [w for w in WS if 14.81 <= w["a"]]]
def s6(fr, t):
    for j, b in enumerate(BLOQ):
        bi = b[0]["a"] - 0.06; bf = BLOQ[j + 1][0]["a"] - 0.06 if j + 1 < len(BLOQ) else DUR
        if not (bi <= t < bf): continue
        tiles = []
        for w in b:
            c = w["w"].lower().strip(",.")
            if c in PLAYF: im, anc = txt_img(c, font(PLAY, 96, "Italic"), BL, -0.02, halo=True)
            else: im, anc = txt_img(c, font(MONT, 90, "ExtraBold"), AMAR if c in AMA6 else BL, -0.055, halo=True)
            tiles.append((w, im, anc))
        gap = 16; tot = sum(a for _, _, a in tiles) + gap * (len(tiles) - 1); esc = min(1.0, 840 / tot)
        tiles = [(w, im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS), a * esc) for w, im, a in tiles]; gap *= esc; tot *= esc; x = 500 - tot / 2; fade = min((t - bi) / 0.1, 1) * min((bf - t) / 0.12, 1)
        for w, im, anc in tiles:
            dicha = t >= w["a"] - 0.02; e = eo((t - w["a"] + 0.02) / 0.2)
            a = fade * ((0.34 + 0.66 * e) if dicha else 0.34); r = (14 * (1 - e)) if dicha else 6; s = (0.89 + 0.11 * e) if dicha else 0.89
            im2 = im.filter(ImageFilter.GaussianBlur(r)) if r > 0.4 else im
            pon(fr, im2, x + anc / 2, 1290, a, s); x += anc + gap

# ---------------------------------------------------------------- bucle
def cuadro(buf, t):
    base = Image.frombuffer("RGB", (W, H), buf, "raw", "RGB", 0, 1).convert("RGBA")
    if 8.2 <= t < 10.15 + 0.2: base = tarjeta(base, t, 8.2, 10.15)
    fr = base
    if t < 6.55: s1(fr, t)
    elif t < 8.2: s2(fr, t)
    elif t < 10.15: s3(fr, t)
    elif t < 11.2: s4(fr, t, base)
    elif t < 12.8:
        s5(fr, t)
        if FLASH[0] <= t < FLASH[1]: fr.alpha_composite(Image.new("RGBA", (W, H), FLASH[2] + (235,)))
    else: s6(fr, t)
    etiqueta(fr, t)
    return fr.convert("RGB").tobytes()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:   # prueba: python3 render.py 1.5 9 10.9 …  → pruebas/t.jpg
        os.makedirs("pruebas", exist_ok=True)
        for ts in sys.argv[1:]:
            t = float(ts); raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", ts, "-i", "corte.mov", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            Image.frombuffer("RGB", (W, H), cuadro(raw, t), "raw", "RGB", 0, 1).resize((540, 960)).save(f"pruebas/{ts}.jpg")
        sys.exit()
    n = int(DUR * FPS)
    rd = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "corte.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    wr = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "video_sin_audio.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        buf = rd.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: break
        wr.stdin.write(cuadro(buf, i / FPS))
    wr.stdin.close(); wr.wait(); print("ok", i)
