# Render del vídeo 01 (curl de bíceps). Lee base.mov + mascaras/ + plan.json y escribe video.mp4 (sin audio) y eventos.json (para los SFX).
import os
KIT = os.environ.get("KIT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))  # raíz de la carpeta del kit
PROYECTO = os.getcwd()
# Capas por fotograma: cámara (zoom/sacudida) -> texto gigante DETRÁS de la persona -> gráficos (flechas, etiquetas, ✗ ✓) -> subtítulos -> flash.
import json, math, re, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
P = json.load(open("plan.json")); DUR = P["dur"]; WD = P["palabras"]
HN = "/System/Library/Fonts/HelveticaNeue.ttc"
PF = os.path.join(KIT, "assets", "fuentes", "PlayfairDisplay-Italic[wght].ttf")
def hn(peso, s): return ImageFont.truetype(HN, s, index={"bold": 1, "medium": 10, "cblack": 9}[peso])
def pf(s):
    f = ImageFont.truetype(PF, s)
    try: f.set_variation_by_axes([700])
    except Exception: pass
    return f
TINTA, BLANCO, MAG, ROJO, VERDE = (14, 14, 16), (255, 255, 255), (204, 51, 102), (255, 59, 48), (52, 199, 89)
CX = 540                                     # todo centrado en el mismo eje

def cl(x): return max(0.0, min(1.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3                       # ease out
def back(x, s=1.7): x = cl(x) - 1; return 1 + x * x * ((s + 1) * x + s)  # rebote
def T(palabra, n=1, desde=0.0):
    k = 0
    for w in WD:
        if w["s"] >= desde and re.sub(r"[^\wáéíóúñ]", "", w["w"].lower()) == palabra:
            k += 1
            if k == n: return w["s"]
    raise SystemExit("no encuentro " + palabra)

# ---------- tiempos clave (salen de las palabras, no a ojo) ----------
t_crecer = T("crecer"); t_forma = T("forma"); t_asi = T("así"); t_espalda = T("espalda")
t_balanceo = T("balanceo"); t_conseguir = T("conseguir"); t_lesion = T("lesionarte")
t_que = T("qué"); t_pectoral = T("pectoral"); t_recta = T("recta"); t_buscar = T("buscar")
t_completo = T("completo"); t_si2 = T("si", 1, 13.0); t_tecnica = T("técnica"); t_bajar = T("bajar")
t_cta = T("si", 1, 16.9); t_dudas = T("dudas"); t_dos = T("dos"); t_somo = T("sede1"); t_asti = T("sede2"); t_te = T("te", 1, 22.5)
t_split1 = t_pectoral - 0.02

EV = []  # (tiempo, tipo) para la pista de efectos
def ev(t, k): EV.append((round(t, 3), k))

# ---------- cámara ----------
def camara(t):
    z = 1.0; dx = dy = 0.0
    z += 0.16 * (1 - eo(t / 0.40))                                      # golpe de entrada
    if t_asi <= t < t_lesion: z += 0.07 * cl((t - t_asi) / (t_lesion - t_asi))   # empuje lento en el error
    if t_conseguir - 0.05 <= t < t_que: z += 0.12 * eo((t - t_conseguir + 0.05) / 0.12)  # golpe en «conseguir… lesionarte»
    if t_completo <= t < t_si2: z += 0.10 * eo((t - t_completo) / 0.15)
    if t_si2 <= t < t_bajar: z += 0.05 * (1 - cl((t - t_si2) / 2.5))
    if t_bajar <= t < t_cta: z += 0.10 * eo((t - t_bajar) / 0.14)
    if t_cta <= t: z += 0.06 * cl((t - t_cta) / (DUR - t_cta)) + 0.10 * (1 - eo((t - t_cta) / 0.35))
    for t0 in (T("balanceo"), T("pectoral"), T("recta"), T("técnica"), T("peso"), T("dudas"), T("fuerza")):
        if t0 <= t < t0 + 0.30: z += 0.05 * (1 - eo((t - t0) / 0.30))
    for t0, a in ((t_lesion, 16), (t_crecer, 9), (t_bajar, 7)):          # sacudidas
        if t0 <= t < t0 + 0.30:
            k = (1 - (t - t0) / 0.30); dx += a * k * math.sin((t - t0) * 95); dy += a * 0.6 * k * math.cos((t - t0) * 80)
    return z, dx, dy

def cam_apply(im, z, dx, dy, cy=760, resample=Image.BICUBIC):
    if abs(z - 1) < 1e-3 and abs(dx) < 0.3 and abs(dy) < 0.3: return im
    # escala alrededor de (CX, cy) y desplaza
    a = 1 / z; c = CX - a * CX - dx * a; f = cy - a * cy - dy * a
    return im.transform((W, H), Image.AFFINE, (a, 0, c, 0, a, f), resample=resample)

# ---------- texto ----------
def texto_img(txt, font, fill, trk=0.0, sombra=False):
    w = int(sum(font.getlength(ch) for ch in txt) + trk * font.size * max(0, len(txt) - 1)) + 40
    asc, desc = font.getmetrics(); h = asc + desc + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 20
    for ch in txt:
        d.text((x, 20), ch, font=font, fill=fill); x += font.getlength(ch) + trk * font.size
    im = im.crop(im.getbbox() or (0, 0, 1, 1))
    if sombra:   # sombra suave DETRÁS DE LAS LETRAS (no sobre la persona) para que se lea en cualquier fondo
        pad = 24; s = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
        a = Image.new("L", s.size, 0); a.paste(im.getchannel("A"), (pad, pad))
        a = a.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.55))
        s.putalpha(a); s.alpha_composite(im, (pad, pad)); im = s
    return im

CACHE = {}
def gigante(txt, color, alto=470, ancho_max=840):
    k = (txt, color, alto)
    if k not in CACHE:
        f = hn("cblack", alto)
        if isinstance(color, tuple) and isinstance(color[0], tuple):   # varios colores, uno por palabra
            partes = [texto_img(p, f, c, trk=-0.01) for p, c in zip(txt.split(" "), color)]; gap = int(alto * 0.18)
            im = Image.new("RGBA", (sum(p.width for p in partes) + gap * (len(partes) - 1), max(p.height for p in partes)), (0, 0, 0, 0)); x = 0
            for p in partes: im.alpha_composite(p, (x, im.height - p.height)); x += p.width + gap
        else: im = texto_img(txt, f, color, trk=-0.01)
        if im.width > ancho_max: im = im.resize((ancho_max, int(im.height * ancho_max / im.width)), Image.LANCZOS)
        CACHE[k] = im
    return CACHE[k]

# texto gigante DETRÁS de la persona: (inicio, fin, texto, color, y_centro)
DETRAS = [
    (0.00, t_crecer - 0.02, "ASÍ NO", ROJO, 560),
    (t_crecer - 0.02, t_asi, "CRECE", MAG, 560),
    (t_lesion - 0.06, t_que, "LESIÓN", MAG, 560),
    (t_completo - 0.04, t_si2, "BÍCEPS", TINTA, 560),
    (t_bajar - 0.04, t_cta, "PESO", TINTA, 560),
    (t_dos - 0.30, t_somo - 0.02, "2 CENTROS", (MAG, TINTA), 590),
    (t_somo - 0.02, t_asti - 0.02, "SEDE 1", ROJO, 520),
    (t_asti - 0.02, DUR + 1, "SEDE 2", ROJO, 520),
]
for a, b, txt, c, y in DETRAS: ev(a, "golpe" if c in (ROJO, MAG) else "pop_grande")

def capa_detras(t):
    for a, b, txt, c, y in DETRAS:
        if a <= t < b:
            im = gigante(txt, c); p = back((t - a) / 0.22, 2.2); s = 0.55 + 0.45 * p
            sal = cl((b - t) / 0.08) if b < DUR else 1.0
            im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
            if sal < 1: im2.putalpha(im2.getchannel("A").point(lambda v: int(v * sal)))
            L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L.alpha_composite(im2, (int(CX - 20 - im2.width / 2), int(y - im2.height / 2)))
            return L
    return None

# ---------- piezas gráficas ----------
def trazo(d, pts, color, ancho, prog):
    """dibuja una polilínea hasta 'prog' (0-1) de su longitud"""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(seg); lim = tot * cl(prog); acc = 0; out = [pts[0]]
    for i, s in enumerate(seg):
        if acc + s <= lim: out.append(pts[i + 1]); acc += s
        else:
            r = (lim - acc) / s if s else 0; out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * r, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * r)); break
    if len(out) > 1: d.line(out, fill=color, width=ancho, joint="curve")
    for p in (out[0], out[-1]): d.ellipse((p[0] - ancho / 2, p[1] - ancho / 2, p[0] + ancho / 2, p[1] + ancho / 2), fill=color)
    return out[-1]

def cruz(L, cx, cy, r, prog, color=ROJO, ancho=22):
    d = ImageDraw.Draw(L)
    trazo(d, [(cx - r, cy - r), (cx + r, cy + r)], color, ancho, prog * 2)
    if prog > 0.5: trazo(d, [(cx + r, cy - r), (cx - r, cy + r)], color, ancho, (prog - 0.5) * 2)

def check(L, cx, cy, r, prog, color=VERDE, ancho=22):
    trazo(ImageDraw.Draw(L), [(cx - r, cy), (cx - r * 0.3, cy + r * 0.7), (cx + r, cy - r * 0.8)], color, ancho, prog)

def pastilla(txt, fondo, color=BLANCO, tam=46):
    f = hn("bold", tam); tw = f.getlength(txt); pad = 26
    im = Image.new("RGBA", (int(tw + 2 * pad), int(tam * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=im.height // 2, fill=fondo)
    d.text((im.width / 2, im.height / 2 + 2), txt, font=f, fill=color, anchor="mm"); return im

def pegar(L, im, cx, cy, s=1.0, alpha=1.0):
    if s <= 0.01 or alpha <= 0.01: return
    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BICUBIC)
    if alpha < 1: im2.putalpha(im2.getchannel("A").point(lambda v: int(v * alpha)))
    L.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))

def entra_sale(t, a, b, e=0.18, s=0.12):
    if t < a or t >= b: return 0.0
    return min(back((t - a) / e, 2.0), cl((b - t) / s))

def flecha_arco(L, cx, cy, r, a0, a1, prog, color=MAG, ancho=16):
    n = 40; pts = [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    d = ImageDraw.Draw(L); fin = trazo(d, pts, color, ancho, prog)
    if prog > 0.15:  # punta
        ang = math.radians(a0 + (a1 - a0) * cl(prog)); tg = (-math.sin(ang), math.cos(ang)) if a1 > a0 else (math.sin(ang), -math.cos(ang))
        nx, ny = -tg[1], tg[0]; L2 = 34
        d.polygon([(fin[0] + tg[0] * 18, fin[1] + tg[1] * 18), (fin[0] - tg[0] * L2 + nx * 22, fin[1] - tg[1] * L2 + ny * 22),
                   (fin[0] - tg[0] * L2 - nx * 22, fin[1] - tg[1] * L2 - ny * 22)], fill=color)

def tarjeta(txt, icono, color_icono, tam=84):
    """tarjeta blanca con icono redondo a la izquierda y texto negro grueso; sombra bajo la tarjeta"""
    f = hn("bold", tam); tw = sum(f.getlength(c) for c in txt) - 0.04 * tam * (len(txt) - 1)
    h = int(tam * 1.75); ic = int(h * 0.72); pad = 30; w = int(pad + ic + 24 + tw + pad + 10)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 28, 20 + w, 28 + h), radius=h // 2.6, fill=110); im.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=h // 2.6, fill=BLANCO)
    cx, cy = 20 + pad + ic / 2, 20 + h / 2; d.ellipse((cx - ic / 2, cy - ic / 2, cx + ic / 2, cy + ic / 2), fill=color_icono)
    r_ = ic * 0.24
    if icono == "ok": trazo(d, [(cx - r_, cy), (cx - r_ * 0.3, cy + r_ * 0.75), (cx + r_, cy - r_ * 0.7)], BLANCO, 11, 1)
    elif icono == "no": trazo(d, [(cx - r_, cy - r_), (cx + r_, cy + r_)], BLANCO, 11, 1); trazo(d, [(cx + r_, cy - r_), (cx - r_, cy + r_)], BLANCO, 11, 1)
    else: d.text((cx, cy + 2), "!", font=hn("bold", int(ic * 0.7)), fill=BLANCO, anchor="mm")
    x = 20 + pad + ic + 24
    for c in txt: d.text((x, cy + 3), c, font=f, fill=TINTA, anchor="lm"); x += f.getlength(c) - 0.04 * tam
    return im

def entra_tarjeta(L, im, cx, cy, t, t0, t1):
    if not (t0 <= t < t1): return
    k = back((t - t0) / 0.26, 1.9); sal = cl((t1 - t) / 0.12)
    pegar(L, im, cx, cy + 70 * (1 - eo((t - t0) / 0.26)), 0.6 + 0.4 * k, min(1, (t - t0) / 0.08) * sal)

def pin3d(ang, tam=200):
    """chincheta de mapa con volumen: degradado radial, brillo y sombra; gira en Y (escala horizontal = cos)"""
    S = tam * 2; im = Image.new("RGBA", (S, int(S * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy, R = S / 2, S * 0.5, S * 0.36
    gota = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in range(150, 391, 4)] + [(cx, cy + R * 2.05)]
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).polygon(gota, fill=255)
    yy, xx = np.mgrid[0:im.height, 0:im.width]; dist = np.sqrt((xx - (cx - R * 0.35)) ** 2 + (yy - (cy - R * 0.4)) ** 2) / (R * 2.2)
    k = np.clip(dist, 0, 1)[..., None]; c1 = np.array([255, 110, 100]); c2 = np.array([150, 18, 24])
    col = (c1 * (1 - k) + c2 * k).astype(np.uint8); body = Image.fromarray(np.dstack([col, np.asarray(m)]), "RGBA")
    im.alpha_composite(body); d = ImageDraw.Draw(im)
    d.ellipse((cx - R * 0.42, cy - R * 0.42, cx + R * 0.42, cy + R * 0.42), fill=(255, 255, 255, 255))
    brillo = Image.new("L", im.size, 0); ImageDraw.Draw(brillo).ellipse((cx - R * 0.75, cy - R * 0.85, cx - R * 0.2, cy - R * 0.45), fill=120)
    im.alpha_composite(Image.merge("RGBA", [Image.new("L", im.size, 255)] * 3 + [brillo.filter(ImageFilter.GaussianBlur(8))]))
    sx = max(0.12, abs(math.cos(ang))); im = im.resize((max(1, int(im.width * sx)), im.height), Image.LANCZOS)
    out = Image.new("RGBA", (S, int(S * 1.55)), (0, 0, 0, 0))
    out.alpha_composite(im, (int((S - im.width) / 2), 0))
    return out.resize((tam, int(tam * 1.55)), Image.LANCZOS)

def tarjeta_osc(nombre, calle, tam=86):
    """tarjeta de centro: negra, franja magenta, etiqueta CENTRO, nombre grande y calle"""
    fe, f1, f2 = hn("bold", 30), hn("bold", tam), hn("medium", int(tam * 0.46))
    w = int(max(f1.getlength(nombre) - 0.03 * tam * len(nombre), f2.getlength(calle), fe.getlength("CENTRO") * 1.3) + 110); h = int(tam * 2.35)
    im = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); sh = Image.new("L", im.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle((20, 30, 20 + w, 30 + h), radius=34, fill=120); im.putalpha(sh.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(im); d.rounded_rectangle((20, 20, 20 + w, 20 + h), radius=34, fill=(14, 14, 16, 245))
    d.rounded_rectangle((20, 20, 34, 20 + h), radius=7, fill=MAG)
    x = 70; y = 20 + h * 0.20
    for c in "CENTRO": d.text((x, y), c, font=fe, fill=MAG, anchor="lm"); x += fe.getlength(c) + 4
    x = 68
    for c in nombre: d.text((x, 20 + h * 0.52), c, font=f1, fill=BLANCO, anchor="lm"); x += f1.getlength(c) - 0.03 * tam
    if calle: d.text((70, 20 + h * 0.83), calle, font=f2, fill=(190, 190, 196), anchor="lm")
    return im

UBI = [(t_somo, t_asti - 0.02, tarjeta_osc("Sede 1", "Calle")), (t_asti, DUR + 1, tarjeta_osc("Sede 2", ""))]
def capa_ubicacion(t, L):
    for a, b, card in UBI:
        if a <= t < b:
            yc = 1060; k = back((t - a) / 0.28, 1.7)
            pegar(L, card, CX, yc + 50 * (1 - eo((t - a) / 0.28)), 0.75 + 0.25 * k, min(1, (t - a) / 0.08))
            # la chincheta cae desde arriba y se posa en la esquina de la tarjeta, girando
            caida = eo((t - a - 0.05) / 0.32); yb = yc - card.height / 2 - 70
            pin = pin3d((t - a) * 4.0 + 1.2, 150)
            if t > a + 0.05: pegar(L, pin, CX + card.width / 2 - 70, yb - 260 * (1 - caida) + 18 * math.sin(min(1, (t - a) / 0.6) * math.pi) * (1 - caida))

LOGO = Image.open("logo.png").convert("RGBA"); LOGO = LOGO.resize((170, int(170 * LOGO.height / LOGO.width)), Image.LANCZOS)
P_BAL = tarjeta("balanceo", "!", MAG); P_PEC = tarjeta("pectoral fuera", "ok", VERDE); P_ESP = tarjeta("espalda recta", "ok", VERDE)
P_MAL = tarjeta("mal", "no", ROJO, 76); P_BIEN = tarjeta("bien", "ok", VERDE, 76); P_TEC = tarjeta("técnica > peso", "!", MAG); P_DUD = tarjeta("¿dudas?", "!", MAG)
ev(t_forma, "error"); ev(t_espalda, "whoosh"); ev(t_balanceo, "pop"); ev(t_split1 - 1.34, "whoosh"); ev(t_split1 - 1.25, "ding")
ev(t_pectoral, "pop"); ev(t_recta, "pop"); ev(t_buscar, "whoosh_suave"); ev(t_tecnica, "pop"); ev(t_asi - 0.02, "flash"); ev(t_cta - 0.02, "flash")
ev(t_te, "ding_final"); ev(t_lesion, "error"); ev(t_dudas, "pop"); ev(T("peso"), "whoosh_suave"); ev(T("fuerza"), "whoosh_suave")

def capa_graficos(t, L):
    # ✗ sobre el balanceo del gancho
    a = entra_sale(t, t_forma, t_asi - 0.05, 0.2)
    if a: cruz(L, 820, 1010, 70, eo((t - t_forma) / 0.22))
    # flecha del balanceo + etiqueta
    if t_espalda <= t < t_lesion - 0.1:
        flecha_arco(L, 540, 980, 330, 205, 150, eo((t - t_espalda) / 0.35))
        entra_tarjeta(L, P_BAL, CX, 340, t, t_balanceo, t_lesion - 0.1)
    # ✗ grande en «lesionarte»
    if t_lesion <= t < t_que: cruz(L, CX, 1010, 120, eo((t - t_lesion) / 0.18), ancho=30)
    # etiquetas de la técnica correcta (con línea al cuerpo)
    d = ImageDraw.Draw(L)
    for k, (t0, pl) in enumerate(((t_pectoral, P_PEC), (t_recta, P_ESP))):
        entra_tarjeta(L, pl, CX, 340 + k * 175, t, t0, t_buscar)
    # arco de recorrido completo
    if t_buscar <= t < t_completo + 0.1: flecha_arco(L, 760, 1180, 170, 100, -40, eo((t - t_buscar) / 0.9), BLANCO, 12)
    # TÉCNICA > PESO
    entra_tarjeta(L, P_TEC, CX, 340, t, t_tecnica, t_bajar - 0.05)
    # flecha que baja junto a PESO
    if t_bajar <= t < t_cta:
        p = eo((t - t_bajar) / 0.3); x = 900; y0 = 250; y1 = 250 + 230 * p
        d.line((x, y0, x, y1), fill=MAG, width=20); d.polygon([(x - 34, y1 - 10), (x + 34, y1 - 10), (x, y1 + 40)], fill=MAG)
    entra_tarjeta(L, P_DUD, CX, 340, t, t_dudas, t_dos - 0.32)
    capa_ubicacion(t, L)
    # logo final
    if t >= t_te: pegar(L, LOGO, CX, 1300, back((t - t_te) / 0.25, 1.6))

# ---------- pantalla partida MAL / BIEN ----------
SP_A, SP_B = t_split1 - 1.34, t_split1 - 0.02   # durante «¿Qué tengo que hacer para hacer bien este ejercicio?»
def frame_en(t):
    n = min(int(t * FPS), NF - 1); return frame_cache(n)

# ---------- subtítulos ----------
CLAVE = {"curl", "bíceps", "crecer", "espalda", "balanceo", "lesionarte", "bien", "pectoral", "recta", "completo", "técnica",
         "bajar", "peso", "dudas", "fuerza", "dos", "esperamos"}
CURSIVA = set()
BL, cur = [], []
for w in WD:
    if cur and (len(cur) >= 3 or w["s"] - cur[-1]["e"] > 0.25 or re.search(r"[.,?!]$", cur[-1]["w"])): BL.append(cur); cur = []
    cur.append(w)
BL.append(cur)
for i, b in enumerate(BL):
    fin = b[-1]["e"] + 0.25
    if i + 1 < len(BL): fin = min(fin, BL[i + 1][0]["s"] - 0.02)
    BL[i] = dict(t0=b[0]["s"] - 0.04, t1=fin, ws=b)
F_SUB, F_CLA = hn("bold", 78), hn("bold", 108)
SUB_Y = 1330
def pieza_palabra(w):
    limpio = re.sub(r"[¿?¡!.,]", "", w).lower()
    if limpio in CURSIVA: return texto_img(limpio, pf(90), BLANCO, -0.01, True)
    if limpio in CLAVE: return texto_img(limpio, F_CLA, BLANCO, -0.06, True)
    return texto_img(limpio, F_SUB, BLANCO, -0.06, True)

def capa_subs(t, L):
    if SP_A <= t < SP_B: return
    if t >= t_te: return
    for b in BL:
        if b["t0"] <= t < b["t1"]:
            piezas = [(w, pieza_palabra(w["w"])) for w in b["ws"]]
            esp = -30; tot = sum(p.width for _, p in piezas) + esp * (len(piezas) - 1)
            x = CX - tot / 2; base = SUB_Y
            for w, p in piezas:
                k = eo((t - (w["s"] - 0.04)) / 0.14)        # cada palabra sube desde un leve desenfoque al decirla
                if k > 0:
                    q = p if k >= 1 else p.filter(ImageFilter.GaussianBlur(4 * (1 - k)))
                    if k < 1: q.putalpha(q.getchannel("A").point(lambda v, k=k: int(v * k)))
                    L.alpha_composite(q, (int(x), int(base - p.height + 14 * (1 - k))))
                x += p.width + esp
            return

# ---------- bucle ----------
import os
NF = int(round(DUR * FPS)); NMASK = len(os.listdir("mascaras"))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "base.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
FR = {}; LEIDOS = [0]
def frame_cache(n):
    while n not in FR:
        if n < LEIDOS[0]: return FR[min(FR, key=lambda k: abs(k - n))]
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3: return FR[max(FR)]
        FR[LEIDOS[0]] = Image.frombytes("RGB", (W, H), b); LEIDOS[0] += 1
    return FR[n]
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
solo = [float(x) for x in sys.argv[1:3]] if len(sys.argv) > 2 else None
for n in range(NF):
    t = n / FPS
    fr = frame_cache(n)
    for k in [k for k in FR if k < n - 200]: del FR[k]
    if solo and not (solo[0] <= t < solo[1]): continue
    z, dx, dy = camara(t)
    if SP_A <= t < SP_B:   # pantalla partida: arriba el error (bloque 2), abajo lo correcto (actual)
        top = frame_cache(int((P["tramos"][1]["t0"] + 1.0 + (t - SP_A)) * FPS)).crop((0, 330, W, 330 + H // 2))
        bot = fr.crop((0, 330, W, 330 + H // 2)); img = Image.new("RGB", (W, H)); img.paste(top, (0, 0)); img.paste(bot, (0, H // 2))
        img = img.convert("RGBA"); L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        p = eo((t - SP_A) / 0.25); d.rectangle((0, H // 2 - 4, int(W * p), H // 2 + 4), fill=BLANCO)
        entra_tarjeta(L, P_MAL, 250, 300, t, SP_A + 0.05, SP_B); entra_tarjeta(L, P_BIEN, 260, H // 2 + 300, t, SP_A + 0.3, SP_B)
        cruz(L, 820, 640, 55, eo((t - SP_A - 0.15) / 0.2), ancho=16); check(L, 820, H // 2 + 330, 55, eo((t - SP_A - 0.45) / 0.2), ancho=16)
        img.alpha_composite(L)
    else:
        img = cam_apply(fr, z, dx, dy).convert("RGBA")
        G = capa_detras(t)
        if G is not None:
            m = cam_apply(Image.open(f"mascaras/{min(n, NMASK - 1):05d}.png"), z, dx, dy)
            ga = np.asarray(G, np.float32); mm = np.asarray(m, np.float32)[..., None] / 255
            im = np.asarray(img, np.float32); bl = None
            t_in = max(a0 for a0, b0, *_ in DETRAS if a0 <= t < b0); kb = 0.0
            fondo = im[..., :3].copy()
            ta = ga[..., 3:4] / 255; fondo = fondo * (1 - ta) + ga[..., :3] * ta    # texto sobre el fondo
            im[..., :3] = im[..., :3] * mm + fondo * (1 - mm)                      # la persona encima, nítida
            img = Image.fromarray(im.astype(np.uint8), "RGBA")
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); capa_graficos(t, L); capa_subs(t, L); img.alpha_composite(L)
    # flash blanco de 2 fotogramas en los cambios de bloque
    for tf in (t_asi - 0.02, SP_A, t_cta - 0.02):
        if tf <= t < tf + 2 / FPS: img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.75 if t < tf + 1 / FPS else 0.35)
    enc.stdin.write(img.convert("RGB").tobytes())
    if n % 60 == 0: print(f"{t:.1f}s", flush=True)
enc.stdin.close(); enc.wait()
json.dump(sorted(EV), open("eventos.json", "w"))
print("listo", NF, "fotogramas")
