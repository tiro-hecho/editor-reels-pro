# Render del vídeo 01(lo malo, lo bueno y lo perfecto) — estilo «boutique medidor».
import os
KIT = os.environ.get("KIT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
PROYECTO = os.getcwd()
# Marca del centro: tinta #1E0101, blanco, coral #FF4B2B; titulares en Bayon (condensada); logo = el logo entre barras verticales.
# Capas: cámara -> [DETRÁS de la persona: palabra MALO/BUENO/PERFECTO + medidor de barras, gancho, logo final] -> título de sección -> subtítulos -> cortes a B-roll -> flash.
import json, math, re, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
P = json.load(open("plan.json")); DUR = P["dur"]; WD = P["palabras"]
HN = "/System/Library/Fonts/HelveticaNeue.ttc"; BAYON = "marca/fuente-titulares.ttf"
def hn(peso, s): return ImageFont.truetype(HN, s, index={"bold": 1, "medium": 10, "cblack": 9}[peso])
def bay(s): return ImageFont.truetype(BAYON, s)
TINTA, BLANCO, CORAL, GRIS = (30, 1, 1), (255, 255, 255), (255, 75, 43), (190, 182, 180)
CX = 540

def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return 3 * x * x - 2 * x ** 3
def back(x, s=1.7): x = cl(x) - 1; return 1 + x * x * ((s + 1) * x + s)
def limpia(w): return re.sub(r"[^\wáéíóúñ0-9]", "", w.lower())
def T(p, n=1, desde=0.0):
    k = 0
    for w in WD:
        if w["s"] >= desde and limpia(w["w"]) == p:
            k += 1
            if k == n: return w["s"]
    raise SystemExit("no encuentro " + p)
EV = []
def ev(t, k): EV.append((round(t, 3), k))

def texto_img(txt, font, fill, trk=0.0, sombra=False, dens=0.3):
    w = int(sum(font.getlength(ch) for ch in txt) + abs(trk) * font.size * len(txt)) + 40
    asc, desc = font.getmetrics(); im = Image.new("RGBA", (w, asc + desc + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 20
    for ch in txt: d.text((x, 20), ch, font=font, fill=fill); x += font.getlength(ch) + trk * font.size
    im = im.crop(im.getbbox() or (0, 0, 1, 1))
    if sombra:
        pad = 20; s = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); a = Image.new("L", s.size, 0)
        a.paste(im.getchannel("A"), (pad, pad)); s.putalpha(a.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * dens))); s.alpha_composite(im, (pad, pad)); im = s
    return im
def pegar(L, im, cx, cy, s=1.0, alpha=1.0):
    if s <= 0.01 or alpha <= 0.01: return
    im2 = im if abs(s - 1) < 1e-3 else im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if alpha < 1: im2 = im2.copy(); im2.putalpha(im2.getchannel("A").point(lambda v: int(v * alpha)))
    L.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))

# ---------- tiempos ----------
TR = P["tramos"]; t_b = {}
for t in TR: t_b.setdefault(t["blq"], t["t0"])
NIV = {"malo": 1, "bueno": 2, "perfecto": 3}
ETQ = []   # (t, nivel) de cada malo/bueno/perfecto fuera de la intro
for w in WD:
    l = limpia(w["w"])
    if l in NIV and w["s"] > t_b["b1"] - 0.1: ETQ.append((w["s"], NIV[l]))
SECC = [(t_b["b1"], "01", "cardio o fuerza"), (t_b["b2"], "02", "días a la semana"), (t_b["b3"], "03", "dónde entrenar"), (t_b["b4"], "04", "tu plan")]
t_cta = t_b["cta"]; t_logo = T("centro"); t_stder = T("ciudad")

# ---------- medidor (las barras del logo) ----------
def medidor(n, prog=1.0, alto=230):
    bw, g = 30, 20; hs = [0.62, 0.82, 1.0]; im = Image.new("RGBA", (3 * bw + 2 * g, alto), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(3):
        h = alto * hs[i]; x = i * (bw + g); y0 = alto - h
        d.rounded_rectangle((x, y0, x + bw, alto), radius=bw // 2, fill=(30, 1, 1, 55))            # apagada
        if i < n:
            p = eo((prog * 3) - i); col = CORAL if n == 3 else TINTA
            if p > 0: d.rounded_rectangle((x, alto - h * p, x + bw, alto), radius=bw // 2, fill=col + (255,))
    return im
F_ETQ = bay(330)
ETQ_TXT = {1: texto_img("MALO", F_ETQ, TINTA), 2: texto_img("BUENO", F_ETQ, TINTA), 3: texto_img("PERFECTO", F_ETQ, CORAL)}
def etiqueta(n, prog):
    tx = ETQ_TXT[n]; m = medidor(n, prog); g = 46
    im = Image.new("RGBA", (tx.width + g + m.width, max(tx.height, m.height)), (0, 0, 0, 0))
    im.alpha_composite(tx, (0, im.height - tx.height)); im.alpha_composite(m, (tx.width + g, im.height - m.height - 18))
    if im.width > 860: im = im.resize((860, int(im.height * 860 / im.width)), Image.LANCZOS)
    return im

# ---------- gancho: lo malo / lo bueno / lo perfecto, apilado con su medidor ----------
F_G = bay(150)
GAN = [(T("malo"), "LO MALO", 1, TINTA), (T("bueno"), "LO BUENO", 2, TINTA), (T("perfecto"), "LO PERFECTO", 3, CORAL)]
GAN_IM = [(t0, texto_img(s, F_G, c), n) for t0, s, n, c in GAN]
SALUD = texto_img("para la salud", hn("bold", 64), TINTA, -0.05)
def capa_gancho(t, LC):
    fin = t_b["b1"] - 0.05
    if not (0 <= t < fin): return
    sal = cl((fin - t) / 0.15)
    for j, (t0, im, n) in enumerate(GAN_IM):
        if t < t0 - 0.05: continue
        k = eo((t - t0 + 0.05) / 0.3); y = 300 + j * 150
        m = medidor(n, eo((t - t0) / 0.35), 120); x0 = CX - (im.width + 30 + m.width) / 2
        pegar(LC, im, x0 + im.width / 2 - 40 * (1 - k), y, 1, k * sal); pegar(LC, m, x0 + im.width + 30 + m.width / 2, y + 6, 1, k * sal)
    if t >= T("salud") - 0.1: pegar(LC, SALUD, CX, 300 + 3 * 150 - 20, 1, eo((t - T("salud") + 0.1) / 0.25) * sal)

# ---------- las 3 pesas: se iluminan con cada valoración ----------
# CAMBIAR EN CADA VÍDEO: posición de cada objeto que se ilumina (centro, radios, punto alto, tono de su color) y color de la luz
PESAS = {1: dict(c=(382, 1332), r=(92, 96), asa=(382, 1170), tono=lambda h: (h > 330) | (h < 22), luz=(255, 45, 35)),      # rosa -> ROJO (malo)
         2: dict(c=(640, 1330), r=(92, 100), asa=(640, 1180), tono=lambda h: (h > 200) & (h < 255), luz=(255, 196, 0)),   # azul -> AMARILLO (bueno)
         3: dict(c=(565, 1437), r=(112, 114), asa=(565, 1235), tono=lambda h: (h > 120) & (h < 175), luz=(40, 220, 90))}  # verde -> VERDE (perfecto)
def hue(a):
    r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]; mx = a.max(2); mn = a.min(2); d = mx - mn + 1e-6
    return np.where(mx == r_, ((g_ - b_) / d) % 6, np.where(mx == g_, (b_ - r_) / d + 2, (r_ - g_) / d + 4)) * 60, (mx - mn) / (mx + 1e-6)
def ilumina(img, n, k, pulso):
    """halo de luz alrededor de la pesa n + tinte sobre su cuerpo + reflejo en el cajón; k = intensidad 0-1"""
    if k <= 0.01: return img
    p = PESAS[n]; cx, cy = p["c"]; rx, ry = p["r"]; col = np.array(p["luz"], np.float32)
    x0, y0, x1, y1 = cx - rx * 2, p["asa"][1] - 120, cx + rx * 2, cy + ry + 160
    a = np.asarray(img, np.float32); reg = a[y0:y1, x0:x1, :3] / 255
    h, sat = hue(reg)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    cuerpo = (((xx - cx) / (rx * 1.08)) ** 2 + ((yy - cy) / (ry * 1.08)) ** 2) <= 1
    asa = (((xx - cx) / (rx * 0.75)) ** 2 + ((yy - (p["asa"][1] + ry * 0.55)) / (ry * 0.75)) ** 2 <= 1) & (yy < cy - ry * 0.6)
    m = ((cuerpo & p["tono"](h) & (sat > 0.22)) | (asa & (sat < 0.25) & (reg.max(2) > 0.45))).astype(np.float32)   # solo la pesa, no la mano
    halo = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(26)), np.float32) / 255
    suelo = np.exp(-(((xx - cx) / (rx * 1.6)) ** 2 + ((yy - (cy + ry + 30)) / 34) ** 2))   # reflejo en el cajón
    kk = k * (0.85 + 0.15 * pulso)
    luz = np.clip(halo * 1.5 + suelo * 0.55, 0, 1)[..., None] * kk
    out = reg * 255 + col * luz * (1 - m[..., None]) * 0.95                                              # halo fuera de la pesa
    out = out * (1 - m[..., None] * 0.35 * kk) + col * m[..., None] * 0.35 * kk + 40 * m[..., None] * kk     # la pesa se tiñe y brilla
    a[y0:y1, x0:x1, :3] = np.clip(out, 0, 255); return Image.fromarray(a.astype(np.uint8), "RGBA")

# etiqueta en la pared unida a su pesa con una línea que se dibuja
COL_TXT = {1: (220, 30, 25), 2: TINTA, 3: (20, 150, 60)}
F_TAG = bay(230)
TAG_TXT = {1: texto_img("MALO", F_TAG, COL_TXT[1]), 2: texto_img("BUENO", F_TAG, COL_TXT[2]), 3: texto_img("PERFECTO", F_TAG, COL_TXT[3])}
TAG_POS = {1: (290, 520), 2: (735, 520), 3: (540, 400)}   # izquierda, derecha y centro arriba (la cabeza queda libre)
def capa_tag(t, L, n, t0, fin):
    k = t - t0; tx = TAG_TXT[n]; m = medidor(n, eo(k / 0.4), 110)
    if tx.width > 420 and n != 3: tx = tx.resize((420, int(tx.height * 420 / tx.width)), Image.LANCZOS)
    x, y = TAG_POS[n]; p = PESAS[n]; al = min(1, k / 0.1) * cl((fin - t) / 0.1)
    d = ImageDraw.Draw(L); ax, ay = p["asa"]; bx, by = x, y + tx.height / 2 + 30   # línea de la pesa a la etiqueta
    pts = [(ax, ay - 10), (bx, by)] if n != 3 else [(ax, ay - 10), (ax + 330, ay - 10), (ax + 330, by), (bx + tx.width / 2 - 40, by)]   # la verde rodea a la persona
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; lim = sum(seg) * eo(k / 0.35); acc = 0; out = [pts[0]]
    for i, sg in enumerate(seg):
        if acc + sg <= lim: out.append(pts[i + 1]); acc += sg
        else: r_ = (lim - acc) / sg; out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r_, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r_)); break
    d.line(out, fill=p["luz"] + (int(230 * al),), width=5, joint="curve"); d.ellipse((ax - 9, ay - 19, ax + 9, ay - 1), fill=p["luz"] + (int(255 * al),))
    if k > 0.15:
        kk = back((k - 0.15) / 0.3, 1.8); pegar(L, tx, x, y, 0.8 + 0.2 * kk, al)
        pegar(L, m, x, y + tx.height / 2 + 75, 1, al)

# ---------- antigua palabra grande (ya no va detrás de la cabeza) ----------
DIAS = texto_img("DÍAS", hn("cblack", 340), TINTA, -0.01)   # Bayon no tiene Í con tilde
t_dias = T("días"); t_perf = T("perfectas")
def capa_etq(t, LC):
    if t_dias - 0.05 <= t < ETQ[3][0] - 0.04 and t < next(a for a, _ in ETQ if a > t_dias) - 0.04:
        k = t - t_dias + 0.05; pegar(LC, DIAS, CX, 470, 0.9 + 0.1 * back(k / 0.3, 1.8), min(1, k / 0.08))
    if t_perf - 0.04 <= t < t_logo - 0.2:
        capa_tag(t, LC, 3, t_perf, t_logo - 0.2)
    if t >= t_cta - 0.05: return
    act = [(t0, n) for t0, n in ETQ if t >= t0 - 0.04]
    if not act: return
    t0, n = act[-1]
    sig = [a for a, _ in ETQ if a > t0]; fin = min(sig[0] if sig else t_cta, next((s for s, _, _ in SECC if s > t0), 99)) - 0.04
    if t >= fin: return
    capa_tag(t, LC, n, t0, fin)

def luces(t):
    out = {}
    if t < t_b["b1"] - 0.05:                                   # gancho: se encienden las tres en orden
        for t0, _, n, _ in GAN:
            if t >= t0: out[n] = eo((t - t0) / 0.25) * cl((t_b["b1"] - 0.05 - t) / 0.2)
        return out
    act = [(t0, n) for t0, n in ETQ if t >= t0 - 0.04]
    if t_perf - 0.04 <= t < t_logo: act = [(t_perf, 3)]
    if act and t < t_logo + 0.3:
        t0, n = act[-1]; sig = [a for a, _ in ETQ if a > t0]; fin = min(sig[0] if sig else 99, next((s for s, _, _ in SECC if s > t0), 99), t_logo)
        if t < fin: out[n] = eo((t - t0) / 0.2) * cl((fin - t) / 0.12)
    return out

# ---------- título de sección arriba ----------
F_SEC = hn("bold", 56)
SEC_IM = [(s, texto_img(num, F_SEC, CORAL, -0.03), texto_img(txt, F_SEC, TINTA, -0.05)) for s, num, txt in SECC]
def capa_seccion(t, L):
    if t >= t_cta: return
    act = [x for x in SEC_IM if t >= x[0]]
    if not act: return
    s, a, b = act[-1]; k = eo((t - s) / 0.35); w = a.width + 18 + b.width; x0 = CX - w / 2
    d = ImageDraw.Draw(L); lw = (w + 40) * k; d.line((CX - lw / 2, 306, CX + lw / 2, 306), fill=TINTA + (90,), width=2)
    pegar(L, a, x0 + a.width / 2, 258, 1, k); pegar(L, b, x0 + a.width + 18 + b.width / 2, 258, 1, k)

# ---------- cortes a B-roll (fotos de su web y planos del centro) ----------
def foto(f, ang=0):
    im = Image.open(f).convert("RGB"); w_, h_ = im.size; cw = min(w_, int(h_ * 9 / 16)); chh = int(cw * 16 / 9)
    return im.crop(((w_ - cw) // 2, (h_ - chh) // 2, (w_ - cw) // 2 + cw, (h_ - chh) // 2 + chh)).resize((W, H), Image.LANCZOS)
def clip_frames(f, ini, dur):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ini), "-t", str(dur + 0.2), "-i", f, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return [Image.frombytes("RGB", (W, H), r[i:i + W * H * 3]) for i in range(0, len(r) - W * H * 3 + 1, W * H * 3)]
BR = [  # (inicio, fin, fuente)
    (T("cardio") - 0.04, T("bueno", 1, 6) - 0.06, ("clip", "broll/IMG_4331.mov", 1.6)),
    (T("fuerza") - 0.04, T("y", 1, 8) + 0.1, ("clip", "broll/IMG_4332.mov", 13.2)),
    (T("fuerza", 2) - 0.04, T("cardio", 2) - 0.04, ("clip", "broll/IMG_4333.mov", 6.0)),
    (T("cardio", 2) - 0.04, T("ahora") - 0.04, ("clip", "broll/IMG_4331.mov", 4.0)),
    (T("centro") - 0.04, T("perfecto", 1, 26) - 0.06, ("clip", "broll/IMG_4336.mov", 0.3)),
    (T("entrenador") - 0.04, T("perfecto", 1, 33.6) - 0.06, ("foto", "fotos/DSC4078.jpg")),
    (t_stder - 0.04, T("quieres", 1, 36) + 0.6, ("clip", "broll/IMG_4337.mov", 0.5)),
]
BR_IMG = []
for a, b, src in BR:
    BR_IMG.append([foto(src[1])] if src[0] == "foto" else clip_frames(src[1], src[2], b - a))
    ev(a, "flash")
def broll(t):
    for (a, b, src), fr in zip(BR, BR_IMG):
        if a <= t < b:
            k = (t - a) / (b - a); z = 1.06 - 0.06 * k   # zoom lento hacia fuera
            im = fr[min(len(fr) - 1, int((t - a) * FPS))]
            if z != 1: im = im.transform((W, H), Image.AFFINE, (1 / z, 0, CX - CX / z, 0, 1 / z, 960 - 960 / z), resample=Image.BICUBIC)
            return im.convert("RGBA")
    return None

# ---------- cierre: logo gigante detrás + dirección ----------
LOGO = Image.open("marca/logo.png").convert("RGBA")
la = np.asarray(LOGO).copy(); la[..., :3] = TINTA; LOGO_T = Image.fromarray(la, "RGBA"); LOGO_T = LOGO_T.resize((820, int(820 * LOGO_T.height / LOGO_T.width)), Image.LANCZOS)
DIR = texto_img("calle del centro · ciudad", hn("bold", 44), TINTA, -0.04)
def capa_cierre(t, LC, L):
    if t < t_logo - 0.15: return
    k = t - t_logo + 0.15; pegar(LC, LOGO_T, CX, 470, 0.85 + 0.15 * back(k / 0.35, 1.8), min(1, k / 0.1))
    pegar(L, DIR, CX, 262, 1, eo((k - 0.2) / 0.3))
ev(t_logo - 0.15, "flash"); ev(t_dias, "pop"); ev(t_perf, "golpe")

# ---------- subtítulos: Helvetica Bold junta, sobre el pecho, sin tapar la cara ----------
CAB = json.load(open("cabeza.json"))
CLAVE = {"malo", "bueno", "perfecto", "cardio", "fuerza", "combinar", "días", "cero", "dos", "tres", "cuatro", "gimnasio", "centro",
         "plan", "chatgpt", "entrenador", "salud", "perfectas"}
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.25 or re.search(r"[.,?!]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
for i, b in enumerate(BL):
    fin = b[-1]["e"] + 0.25
    if i + 1 < len(BL): fin = min(fin, BL[i + 1][0]["s"] - 0.02)
    BL[i] = dict(t0=b[0]["s"] - 0.04, t1=fin, ws=b)
F_SUB, F_CLA = hn("bold", 62), hn("bold", 84); CACHE = {}
def pieza(w):
    l = re.sub(r"[¿?¡!.,]", "", w).lower(); l = ("ChatGPT" if l == "chatgpt" else l)
    if l not in CACHE: CACHE[l] = texto_img(l, F_CLA if limpia(l) in CLAVE else F_SUB, BLANCO, -0.06, True, 0.45)
    return CACHE[l]
def capa_subs(t, L, en_broll):
    n = min(int(t * FPS), len(CAB) - 1); hx, _ = CAB[n]
    y = 1330 if en_broll else 1090; xc = max(340, min(740, hx))
    for b in BL:
        if b["t0"] <= t < b["t1"]:
            ps = [(w, pieza(w["w"])) for w in b["ws"]]; esp = -26
            tot = sum(p.width for _, p in ps) + esp * (len(ps) - 1)
            if tot > 700: f = 700 / tot; ps = [(w, p.resize((int(p.width * f), int(p.height * f)), Image.LANCZOS)) for w, p in ps]; esp = int(esp * f); tot = sum(p.width for _, p in ps) + esp * (len(ps) - 1)
            x = max(66, min(934 - tot, xc - tot / 2))
            for w, p in ps:
                k = eo((t - (w["s"] - 0.04)) / 0.14)
                if k > 0:
                    q = p if k >= 1 else p.filter(ImageFilter.GaussianBlur(4 * (1 - k)))
                    if k < 1: q = q.copy(); q.putalpha(q.getchannel("A").point(lambda v, k=k: int(v * k)))
                    L.alpha_composite(q, (int(x), int(y - p.height + 14 * (1 - k))))
                x += p.width + esp
            return

# ---------- cámara: empujes suaves (boutique, nada brusco) ----------
def camara(t):
    z = 1.0 + 0.10 * (1 - eo(t / 0.5))
    for t0, n in ETQ:
        if t0 <= t < t0 + 0.4: z += (0.025 if n < 3 else 0.05) * (1 - eo((t - t0) / 0.4))
    seg = next((s for s, _, _ in reversed(SECC) if t >= s), 0); z += 0.04 * cl((t - seg) / 6)
    return z
def cam(im, z, cy=900):
    if abs(z - 1) < 1e-3: return im
    a = 1 / z; return im.transform((W, H), Image.AFFINE, (a, 0, CX - a * CX, 0, a, cy - a * cy), resample=Image.BICUBIC)

# ---------- sonido ----------
for t0, n in ETQ: ev(t0, "pop" if n < 3 else "golpe")
for s, _, _ in SECC: ev(s, "whoosh")
for t0, _, _, _ in GAN: ev(t0, "pop")

# ---------- bucle ----------
NF = int(round(DUR * FPS)); NM = len(os.listdir("mascaras"))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "base.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
last = None
for n in range(NF):
    t = n / FPS; b = dec.stdout.read(W * H * 3)
    fr = Image.frombytes("RGB", (W, H), b) if len(b) == W * H * 3 else last; last = fr
    z = 1.0; img = fr.convert("RGBA")
    BRi = broll(t)
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if BRi is not None:
        img = BRi
    else:
        LC = Image.new("RGBA", (W, H), (0, 0, 0, 0)); capa_gancho(t, LC); capa_etq(t, LC); capa_cierre(t, LC, L)
        for nn, kk in luces(t).items(): img = ilumina(img, nn, kk, 0.5 + 0.5 * math.sin(t * 9))
        img.alpha_composite(LC)
        capa_seccion(t, L)
    capa_subs(t, L, BRi is not None); img.alpha_composite(L)
    for a_, *_ in BR:   # destello blanco de 2 fotogramas al entrar cada corte
        if a_ <= t < a_ + 2 / FPS: img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.55)
    enc.stdin.write(img.convert("RGB").tobytes())
    if n % 150 == 0: print(f"{t:.1f}s", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
json.dump(sorted(EV), open("eventos.json", "w")); print("listo", NF)
