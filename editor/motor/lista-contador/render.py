# Render del vídeo 02 (5 errores en flexiones) — estilo «lista contador».
import os
KIT = os.environ.get("KIT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
PROYECTO = os.getcwd()
# Capas: cámara -> anillos/flechas sobre el cuerpo -> barra de progreso 1/5 -> títulos -> checklist -> subtítulos -> cortinillas magenta -> flash.
import json, math, re, os, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
P = json.load(open("plan.json")); DUR = P["dur"]; WD = P["palabras"]
HN = "/System/Library/Fonts/HelveticaNeue.ttc"
def hn(peso, s): return ImageFont.truetype(HN, s, index={"bold": 1, "medium": 10, "cblack": 9, "light": 7}[peso])
BLANCO, MAG, ROJO, VERDE, TINTA = (255, 255, 255), (204, 51, 102), (255, 59, 48), (52, 199, 89), (14, 14, 16)
CX = 540

def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return 3 * x * x - 2 * x ** 3
def back(x, s=1.7): x = cl(x) - 1; return 1 + x * x * ((s + 1) * x + s)
def T(palabra, n=1, desde=0.0):
    k = 0
    for w in WD:
        if w["s"] >= desde and re.sub(r"[^\wáéíóúñ]", "", w["w"].lower()) == palabra:
            k += 1
            if k == n: return w["s"]
    raise SystemExit("no encuentro " + palabra)

# ---------- tiempos ----------
tr = {t["blq"]: t for t in reversed(P["tramos"])}           # primer tramo de cada bloque
E = [T("primer"), T("segundo"), T("tercer"), T("cuarto"), T("quinto")]
t_bien = T("forma"); t_cta = tr["cta"]["t0"]; t_tercero = T("tercero"); t_cantabria = T("cantabria"); t_dos = T("dos", 1, 30)
FIN_E = E[1:] + [t_bien]
EV = []
def ev(t, k): EV.append((round(t, 3), k))

# ---------- texto ----------
def texto_img(txt, font, fill, trk=0.0, sombra=False, dens=0.32):
    w = int(sum(font.getlength(ch) for ch in txt) + abs(trk) * font.size * len(txt)) + 40
    asc, desc = font.getmetrics(); im = Image.new("RGBA", (w, asc + desc + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 20
    for ch in txt: d.text((x, 20), ch, font=font, fill=fill); x += font.getlength(ch) + trk * font.size
    im = im.crop(im.getbbox() or (0, 0, 1, 1))
    if sombra:
        pad = 24; s = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); a = Image.new("L", s.size, 0)
        a.paste(im.getchannel("A"), (pad, pad)); s.putalpha(a.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(min(255, v * dens)))); s.alpha_composite(im, (pad, pad)); im = s
    return im

def pegar(L, im, cx, cy, s=1.0, alpha=1.0):
    if s <= 0.01 or alpha <= 0.01: return
    im2 = im if abs(s - 1) < 1e-3 else im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if alpha < 1: im2 = im2.copy(); im2.putalpha(im2.getchannel("A").point(lambda v: int(v * alpha)))
    L.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))

def trazo(d, pts, color, ancho, prog):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; lim = sum(seg) * cl(prog); acc = 0; out = [pts[0]]
    for i, s in enumerate(seg):
        if acc + s <= lim: out.append(pts[i + 1]); acc += s
        else:
            r = (lim - acc) / s if s else 0; out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r)); break
    if len(out) > 1: d.line(out, fill=color, width=ancho, joint="curve")
    for p in (out[0], out[-1]): d.ellipse((p[0] - ancho / 2, p[1] - ancho / 2, p[0] + ancho / 2, p[1] + ancho / 2), fill=color)
    return out

def anillo(L, cx, cy, r, prog, color=ROJO, ancho=12, pulso=0.0):
    d = ImageDraw.Draw(L); n = 60; a0 = -110
    pts = [(cx + r * math.cos(math.radians(a0 + 360 * i / n)), cy + r * 0.82 * math.sin(math.radians(a0 + 360 * i / n))) for i in range(n + 1)]
    trazo(d, pts, color, ancho, prog)
    if pulso > 0:  # onda que sale del anillo
        rr = r * (1 + 0.5 * pulso); a = int(200 * (1 - pulso))
        d.ellipse((cx - rr, cy - rr * 0.82, cx + rr, cy + rr * 0.82), outline=color + (a,), width=6)

def flecha(L, x0, y0, x1, y1, prog, color=ROJO, ancho=16):
    d = ImageDraw.Draw(L); out = trazo(d, [(x0, y0), (x1, y1)], color, ancho, prog)
    if prog > 0.2:
        (xa, ya), (xb, yb) = out[-2], out[-1]; ang = math.atan2(yb - ya, xb - xa); L2 = 40
        d.polygon([(xb + math.cos(ang) * 14, yb + math.sin(ang) * 14), (xb - math.cos(ang - 0.5) * L2, yb - math.sin(ang - 0.5) * L2),
                   (xb - math.cos(ang + 0.5) * L2, yb - math.sin(ang + 0.5) * L2)], fill=color)

def cruz(L, cx, cy, r, prog, color=ROJO, ancho=14):
    d = ImageDraw.Draw(L); trazo(d, [(cx - r, cy - r), (cx + r, cy + r)], color, ancho, prog * 2)
    if prog > 0.5: trazo(d, [(cx + r, cy - r), (cx - r, cy + r)], color, ancho, (prog - 0.5) * 2)
def check(L, cx, cy, r, prog, color=VERDE, ancho=14):
    trazo(ImageDraw.Draw(L), [(cx - r, cy), (cx - r * 0.3, cy + r * 0.7), (cx + r, cy - r * 0.8)], color, ancho, prog)

# ---------- cámara ----------
def camara(t):
    z = 1.0 + 0.14 * (1 - eo(t / 0.4)); dx = dy = 0.0
    for e0 in E + [t_bien]:            # al salir la cortinilla, golpe de zoom
        a = e0 + 0.42
        if a <= t < a + 0.35: z += 0.09 * (1 - eo((t - a) / 0.35))
    for i, e0 in enumerate(E):         # empuje lento durante cada error
        if e0 <= t < FIN_E[i]: z += 0.05 * cl((t - e0) / (FIN_E[i] - e0))
    if t_tercero <= t < t_tercero + 0.3: z += 0.08 * (1 - eo((t - t_tercero) / 0.3))
    if t_cta <= t: z += 0.05 * cl((t - t_cta) / (DUR - t_cta))
    return z, dx, dy
def cam_apply(im, z, cy):
    if abs(z - 1) < 1e-3: return im
    a = 1 / z; return im.transform((W, H), Image.AFFINE, (a, 0, CX - a * CX, 0, a, cy - a * cy), resample=Image.BICUBIC)

# ---------- barra de progreso 1/5 (arriba) ----------
F_CNT = hn("bold", 52)
def capa_progreso(t, L):
    if t >= t_bien: return
    k_in = eo((t - 0.15) / 0.35)
    if k_in <= 0: return
    d = ImageDraw.Draw(L); n = 5; w = 132; g = 16; x0 = CX - (n * w + (n - 1) * g) / 2; y = 262
    hecho = sum(1 for e0 in E if t >= e0)
    for i in range(n):
        x = x0 + i * (w + g); d.rounded_rectangle((x, y, x + w, y + 22), radius=11, fill=(255, 255, 255, int(150 * k_in)))
        if i < hecho:
            p = eo((t - E[i]) / 0.3); col = MAG if i != 2 else ROJO
            d.rounded_rectangle((x, y, x + w * p, y + 22), radius=11, fill=col + (255,))
        if i == 2 and t_tercero <= t:   # el tercero, señalado desde el gancho
            pu = ((t - t_tercero) * 1.6) % 1; d.rounded_rectangle((x - 6 * pu, y - 6 * pu, x + w + 6 * pu, y + 14 + 6 * pu), radius=10, outline=ROJO + (int(220 * (1 - pu)),), width=3)
    if hecho and t >= E[0] + 0.45:
        txt = texto_img(f"error {hecho}/5", F_CNT, BLANCO, -0.04, True); pegar(L, txt, CX, y + 66, 1, k_in)

# ---------- cortinilla magenta con el número ----------
F_NUM = hn("cblack", 820)
TIT = ["cadera caída", "manos muy abiertas", "codos abiertos", "medio recorrido", "cuello tenso"]
NUM_IM = [texto_img(str(i + 1), F_NUM, BLANCO, 0) for i in range(5)]
F_TIT = hn("bold", 92)
def cortinilla(t, img):
    for i, e0 in enumerate(E):
        a = e0 - 0.06; d1, hold, d2 = 0.14, 0.30, 0.14
        if a <= t < a + d1 + hold + d2:
            u = t - a
            if u < d1: x = W * (1 - eio(u / d1))                     # entra desde la derecha
            elif u < d1 + hold: x = 0
            else: x = -W * eio((u - d1 - hold) / d2)                  # sale por la izquierda
            pan = Image.new("RGBA", (W, H), MAG + (255,)); d = ImageDraw.Draw(pan)
            k = back((u - 0.05) / 0.3, 2.0); pegar(pan, NUM_IM[i], CX + 30 * (1 - k), 820, 0.8 + 0.2 * k)
            pegar(pan, texto_img("error", hn("bold", 80), BLANCO, -0.05), CX, 1260, 1, cl((u - 0.08) / 0.1))
            img.alpha_composite(pan, (int(x), 0)); return True
    return False

# ---------- marcas sobre el cuerpo en cada error ----------
TARJ_COMUN = None
def tarjeta(txt, color_icono, icono="!", tam=70):
    f = hn("bold", tam); tw = sum(f.getlength(c) for c in txt) - 0.04 * tam * (len(txt) - 1)
    h = int(tam * 1.75); ic = int(h * 0.72); pad = 28; w = int(pad + ic + 22 + tw + pad + 8)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 28, 20 + w, 28 + h), radius=h // 2.6, fill=110); im.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=h // 2.6, fill=BLANCO)
    cx, cy = 20 + pad + ic / 2, 20 + h / 2; d.ellipse((cx - ic / 2, cy - ic / 2, cx + ic / 2, cy + ic / 2), fill=color_icono)
    if icono == "ok": r_ = ic * 0.24; trazo(d, [(cx - r_, cy), (cx - r_ * 0.3, cy + r_ * 0.75), (cx + r_, cy - r_ * 0.7)], BLANCO, 10, 1)
    elif icono == "x": r_ = ic * 0.22; trazo(d, [(cx - r_, cy - r_), (cx + r_, cy + r_)], BLANCO, 10, 1); trazo(d, [(cx + r_, cy - r_), (cx - r_, cy + r_)], BLANCO, 10, 1)
    else: d.text((cx, cy + 2), icono, font=hn("bold", int(ic * 0.66)), fill=BLANCO, anchor="mm")
    x = 20 + pad + ic + 22
    for c in txt: d.text((x, cy + 3), c, font=f, fill=TINTA, anchor="lm"); x += f.getlength(c) - 0.04 * tam
    return im
T_ERR = [tarjeta(s, ROJO, "x") for s in TIT]
def burbuja(txt, tam=50):
    f = hn("bold", tam); t = texto_img(txt, f, TINTA, -0.04); pad = 26
    im = Image.new("RGBA", (t.width + 2 * pad, t.height + 2 * pad - 6), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=(255, 255, 255, 240)); im.alpha_composite(t, (pad, pad - 3))
    return im
T_COMUN = burbuja("el que hace todo el mundo")

def capa_errores(t, L):
    for i, e0 in enumerate(E):
        a = e0 + 0.45; b = FIN_E[i] - 0.05
        if not (a <= t < b): continue
        k = (t - a)
        # título del error (tarjeta blanca con ✗), debajo de la barra
        p = eo((k - 0.15) / 0.4); pu = cl((k - 0.55) / 0.5)
        if i == 0 and k < 1.1: anillo(L, 300, 1000, 150, p, pulso=pu); flecha(L, 300, 1170, 300, 1270, eo((k - 0.4) / 0.3))
        if i == 1: anillo(L, 230, 1200, 95, p, pulso=pu); anillo(L, 860, 1300, 95, p, pulso=pu)
        if i == 2:
            flecha(L, 380, 1150, 190, 1130, p); flecha(L, 720, 1200, 900, 1220, p)
            pegar(L, T_COMUN, CX, 470, back((k - 0.3) / 0.25, 1.8) if k > 0.3 else 0)
        if i == 3:
            d = ImageDraw.Draw(L); y0, y1 = 960, 1160; x = 900; pp = eo((k - 0.1) / 0.35)
            d.line((x, y0, x, y0 + (y1 - y0) * pp), fill=BLANCO, width=8)
            flecha(L, x - 70, 1080, x - 70, 1000, eo((k - 0.35) / 0.25)); flecha(L, x - 70, 1080, x - 70, 1160, eo((k - 0.35) / 0.25))
        if i == 4: anillo(L, 600, 1050, 120, p, pulso=pu)

# ---------- gancho: número gigante DETRÁS de la persona que rueda 1-2-3-4 y se clava en 5; en «el tercero» pasa a 3 rojo
F_GIG = hn("cblack", 1000)
DIG = {(d, c): texto_img(d, F_GIG, c, 0) for d in "12345" for c in (MAG, ROJO)}
G_TIT = texto_img("errores en flexiones", hn("bold", 92), BLANCO, -0.06, True)
def capa_gancho_detras(t, LC):
    fin = E[0] - 0.08
    if not (0 <= t < fin): return
    sal = cl((fin - t) / 0.1); dx = 0
    if t < 0.32: d, c, s_ = str(1 + int(t / 0.08)), MAG, 0.9
    elif t < t_tercero: d, c, s_ = "5", MAG, 0.75 + 0.25 * back((t - 0.32) / 0.25, 2.2)
    else:
        d, c, s_ = "3", ROJO, 0.8 + 0.2 * back((t - t_tercero) / 0.22, 2.2)
        if t < t_tercero + 0.3: dx = 22 * (1 - (t - t_tercero) / 0.3) * math.sin((t - t_tercero) * 90)
    pegar(LC, DIG[(d, c)], CX + dx, 760, s_, sal)
def capa_gancho(t, L):
    fin = E[0] - 0.08
    if not (0.25 <= t < fin): return
    sal = cl((fin - t) / 0.1)
    pegar(L, G_TIT, CX, 300 + 30 * (1 - eo((t - 0.25) / 0.3)), 1, min(1, (t - 0.25) / 0.12) * sal)
    if t >= t_tercero + 0.1: pegar(L, T_COMUN, CX, 420, back((t - t_tercero - 0.1) / 0.25, 1.8), sal)

# ---------- checklist de la forma correcta ----------
ITEMS = [(T("manos", 1, 17), "manos fuera de los hombros"), (T("glúteo"), "glúteo activo, cadera fija"), (T("codos", 1, 24), "codos hacia atrás"),
         (T("pectoral"), "pecho hacia el suelo"), (T("movimiento"), "movimiento controlado")]
F_IT = hn("bold", 80)
IT_IM = [texto_img(s_, F_IT, BLANCO, -0.06, True) for _, s_ in ITEMS]
IT_IM = [im if im.width <= 700 else im.resize((700, int(im.height * 700 / im.width)), Image.LANCZOS) for im in IT_IM]   # que quepan con el ✓ en la zona segura
T_BIEN = texto_img("forma correcta", hn("bold", 92), VERDE, -0.06, True)
def revela(im, p):   # máscara que descubre de izquierda a derecha
    if p >= 1: return im
    im = im.copy(); a = np.asarray(im.getchannel("A")).copy(); a[:, int(im.width * p):] = 0; im.putalpha(Image.fromarray(a)); return im
def capa_checklist(t, L):
    if not (t_bien <= t < t_cta - 0.05): return
    sal = cl((t_cta - 0.05 - t) / 0.15); k = t - t_bien
    if k < ITEMS[0][0] - t_bien:   # al principio, solo «forma correcta»
        pegar(L, revela(T_BIEN, eo(k / 0.3)), CX, 330, 1, sal); return
    i = max(j for j, (ti, _) in enumerate(ITEMS) if t >= ti); ti = ITEMS[i][0]; kk = t - ti
    sig = ITEMS[i + 1][0] if i + 1 < len(ITEMS) else t_cta - 0.05
    out = cl((sig - t) / 0.12)                                     # sale al llegar la siguiente
    it = IT_IM[i]; w = it.width + 70; x0 = CX - w / 2; y = 330 - 24 * (1 - out)
    # fondo: pastilla oscura translúcida que se abre con el barrido, para que se lea sobre cualquier fondo
    pw = (w + 56) * eo(kk / 0.22); ph = it.height + 34
    if pw > 10:
        pan = Image.new("RGBA", (int(pw), int(ph)), (0, 0, 0, 0))
        ImageDraw.Draw(pan).rounded_rectangle((0, 0, int(pw) - 1, int(ph) - 1), radius=int(ph / 2), fill=(12, 12, 14, int(175 * out * sal)))
        L.alpha_composite(pan, (int(x0 - 28), int(y - ph / 2)))
    check(L, x0 + 26, y, 22, eo(kk / 0.2), VERDE, 11)
    pegar(L, revela(it, eo(kk / 0.28)), x0 + 70 + it.width / 2, y, 1, out * sal)

# ---------- cierre: ubicación sin plantilla (tipografía + línea) ----------
LOGO = Image.open("logo.png").convert("RGBA"); LOGO = LOGO.resize((170, int(170 * LOGO.height / LOGO.width)), Image.LANCZOS)
F_LUG = hn("bold", 118); F_SUB2 = hn("medium", 44)
LUG = texto_img("sede 1 · sede 2", F_LUG, BLANCO, -0.06, True)
FOTOS = []
for f, nombre, caja in (("fotos/centro1.jpg", "CENTRO 1", None), ("fotos/centro2.jpg", "CENTRO 2", None)):
    ph = Image.open(f).convert("RGB"); ph = (ph.crop(caja) if caja else ph).resize((400, 500), Image.LANCZOS)
    card = Image.new("RGBA", (400, 500), (0, 0, 0, 0)); m = Image.new("L", (400, 500), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 399, 499), radius=30, fill=255)
    ph = ph.convert("RGBA"); ph.putalpha(m); card.alpha_composite(ph)
    g = np.clip((np.arange(500) - 280) / 220, 0, 1) * 170; ga = np.repeat(g[:, None], 400, 1).astype(np.uint8)
    osc = Image.new("RGBA", (400, 500), (0, 0, 0, 255)); osc.putalpha(Image.fromarray(np.minimum(ga, np.asarray(m)))); card.alpha_composite(osc)
    lab = texto_img(nombre, hn("cblack", 96 if len(nombre) < 6 else 74), BLANCO, -0.01); card.alpha_composite(lab, (int(200 - lab.width / 2), 500 - lab.height - 28))
    FOTOS.append(card)
t_f1, t_f2 = T("entrenamientos", 1, 30) - 0.1, T("personalizados") - 0.1
def capa_cierre(t, L):
    for card, t0, cx, ang in ((FOTOS[0], t_f1, 315, 5), (FOTOS[1], t_f2, 745, -5)):
        if t < t0: continue
        k = eo((t - t0) / 0.35); kb = back((t - t0) / 0.35, 1.6)
        im = card.rotate(ang * kb + 10 * (1 - k), resample=Image.BICUBIC, expand=True)
        pegar(L, im, cx + (-260 if cx < CX else 260) * (1 - k), 560, 0.78 + 0.12 * kb, min(1, (t - t0) / 0.1))

# ---------- subtítulos (Helvetica Bold junta, clave más grande) ----------
CLAVE = {"cinco", "errores", "flexiones", "tercero", "cadera", "manos", "abiertas", "codos", "recorridos", "cuello", "tensión",
         "correcta", "hombros", "glúteo", "fija", "atrás", "suelo", "controlado", "cantabria", "guiados", "personalizados", "centros", "mundo"}
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.25 or re.search(r"[.,?!]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
for i, b in enumerate(BL):
    fin = b[-1]["e"] + 0.25
    if i + 1 < len(BL): fin = min(fin, BL[i + 1][0]["s"] - 0.02)
    BL[i] = dict(t0=b[0]["s"] - 0.04, t1=fin, ws=b)
F_SUB, F_CLA = hn("bold", 58), hn("bold", 78)
CAB = json.load(open("cabeza.json")); MASK_ACT = [None]
CACHE = {}
def pieza(w):
    l = re.sub(r"[¿?¡!.,]", "", w).lower()
    if l not in CACHE: CACHE[l] = texto_img(l, F_CLA if l in CLAVE else F_SUB, BLANCO, -0.06, True, 1.0)
    return CACHE[l]
def capa_subs(t, L):
    if E[2] + 0.75 <= t < FIN_E[2] - 0.05: return            # con la burbuja no hay subtítulo
    if t_tercero + 0.1 <= t < E[0]: return                       # ni en el gancho cuando sale la burbuja
    n = min(int(t * FPS), len(CAB) - 1); hx, hy = CAB[n]
    z, _, _ = camara(t); cyz = 1300 if t >= t_cta else 1050
    hx = CX + (hx - CX) * z; hy = cyz + (hy - cyz) * z           # mismo zoom que la imagen
    y = max(330, min(1380, hy - 50)); xc = max(340, min(740, hx))
    if t_bien <= t < t_cta: y = max(y, 470)                     # por debajo de la clave
    if t < E[0]: y = max(y, 470)                                # por debajo del título del gancho
    for b in BL:
        if b["t0"] <= t < b["t1"]:
            ps = [(w, pieza(w["w"])) for w in b["ws"]]; esp = -30
            tot = sum(p.width for _, p in ps) + esp * (len(ps) - 1)
            if tot > 640:   # no cabe en la zona segura: se reduce todo el bloque
                f = 640 / tot; ps = [(w, p.resize((int(p.width * f), int(p.height * f)), Image.LANCZOS)) for w, p in ps]; esp = int(esp * f)
                tot = sum(p.width for _, p in ps) + esp * (len(ps) - 1)
            x = max(66, min(934 - tot, xc - tot / 2))               # dentro del ancho seguro
            hmax = max(p.height for _, p in ps); M = MASK_ACT[0]
            def choca(yy):
                if M is None: return 0
                return M[int(max(0, yy - hmax)):int(yy), int(x):int(x + tot)].mean() if yy > hmax else 0
            if choca(y) > 0.04:                                     # tapa a la persona: sube hasta que no choque
                yy = y
                while yy > 330 and choca(yy) > 0.04: yy -= 20
                y = yy if choca(yy) <= 0.04 else (1420 if choca(1420) <= 0.04 else y)
            for w, p in ps:
                k = eo((t - (w["s"] - 0.04)) / 0.14)
                if k > 0:
                    q = p if k >= 1 else p.filter(ImageFilter.GaussianBlur(4 * (1 - k)))
                    if k < 1: q = q.copy(); q.putalpha(q.getchannel("A").point(lambda v, k=k: int(v * k)))
                    L.alpha_composite(q, (int(x), int(y - p.height + 14 * (1 - k))))
                x += p.width + esp
            return

# ---------- eventos de sonido ----------
for e0 in E: ev(e0 - 0.06, "flash"); ev(e0 + 0.6, "whoosh_suave")

ev(t_tercero, "golpe"); ev(T("tercero") + 0.35, "pop"); ev(t_bien - 0.06, "flash"); ev(t_bien + 0.45, "ding")
for ti, _ in ITEMS: ev(ti + 0.4, "whoosh_suave")
ev(0.32, "golpe"); ev(0.25, "pop"); ev(t_cta, "whoosh"); ev(t_f1, "flash"); ev(t_f2, "flash")

# ---------- bucle ----------
NF = int(round(DUR * FPS)); NM = len(os.listdir("mascaras"))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "base.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
last = None
for n in range(NF):
    t = n / FPS; b = dec.stdout.read(W * H * 3)
    fr = Image.frombytes("RGB", (W, H), b) if len(b) == W * H * 3 else last; last = fr
    z, dx, dy = camara(t); cy = 1300 if t >= t_cta else 1050
    img = cam_apply(fr, z, cy).convert("RGBA")
    mk = cam_apply(Image.open(f"mascaras/{min(n, NM - 1):05d}.png"), z, cy); MASK_ACT[0] = np.asarray(mk, np.float32) / 255
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    capa_gancho(t, L); capa_errores(t, L); capa_checklist(t, L); capa_subs(t, L)
    LC = Image.new("RGBA", (W, H), (0, 0, 0, 0)); capa_cierre(t, LC); capa_gancho_detras(t, LC)
    if LC.getbbox():   # número del gancho y fotos del cierre DETRÁS de la persona
        a = np.asarray(LC, np.float32); mm = MASK_ACT[0][..., None]
        al = a[..., 3:4] / 255 * (1 - mm); im = np.asarray(img, np.float32); im[..., :3] = im[..., :3] * (1 - al) + a[..., :3] * al
        img = Image.fromarray(im.astype(np.uint8), "RGBA")
    img.alpha_composite(L)
    cortinilla(t, img)
    if t_bien - 0.06 <= t < t_bien + 0.04: img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.7)
    enc.stdin.write(img.convert("RGB").tobytes())
    if n % 90 == 0: print(f"{t:.1f}s", flush=True)
enc.stdin.close(); enc.wait(); dec.kill()
json.dump(sorted(EV), open("eventos.json", "w")); print("listo", NF)
