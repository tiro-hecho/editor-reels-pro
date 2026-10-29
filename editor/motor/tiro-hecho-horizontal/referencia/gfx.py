# REFERENCIA del VSL de Tiro Hecho (horizontal). No es un motor genérico: Claude lo adapta a cada vídeo.
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'comun')); from rutas import *
# Capa gráfica del VSL Tiro Hecho: subtítulos de marca, chips, golpes a pantalla completa, rótulos y logo.
# Lee base.mp4 fotograma a fotograma, compone encima y escribe montado.mp4 (sin audio).
import json, subprocess, re, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1920, 1080, 30
F = F + "/"
NAR, CREMA, GRIS, SUP, LIN = (224, 123, 42), (245, 241, 234), (163, 163, 170), (21, 21, 23), (42, 42, 46)

def fnt(n, s):
    if n == "play":
        f = ImageFont.truetype(F + "PlayfairDisplay-Italic[wght].ttf", s)
        try: f.set_variation_by_axes([700])
        except Exception: pass
        return f
    return ImageFont.truetype(F + f"Poppins-{n}.ttf", s)

P = json.load(open("plan.json"))
FIX = {"Tomi,": "persona 1,", "Tachos,": "Chavales,", "cloud": "Claude", "Edit.": "Edits.", "interacciones": "iteraciones",
       "Muy": "muy", "Me": "me", "Le": "le", "Para": "para", "Dinamismo": "dinamismo", "Del": "del", "Os": "Os"}
RAW = json.load(open("palabras.json"))
Wd = []
for i, (a, b, w) in enumerate(RAW):
    w = FIX.get(w, w)
    if w.startswith("-") and Wd and re.match(r"\d", Wd[-1][2]):  # 30 -40 -> 30–40
        Wd[-1][2] += "–" + w[1:]; Wd[-1][1] = b; continue
    Wd.append([a, b, w])
Wd[[i for i, w in enumerate(Wd) if w[2].startswith("gu") and w[2] != "guiones,"][0]][2] = "guiones."

def norm(s): return re.sub(r"[^\wáéíóúñü0-9]", "", s.lower())
def at(frase, despues=0.0, fin=False):
    ws = [norm(x) for x in frase.split()]
    for i in range(len(Wd) - len(ws) + 1):
        if Wd[i][0] >= despues and all(norm(Wd[i + j][2]) == ws[j] for j in range(len(ws))):
            return Wd[i + len(ws) - 1][1] if fin else Wd[i][0]
    raise SystemExit(f"no encuentro: {frase}")

# ---------- piezas gráficas ----------
def diana(size, alpha=255):
    s = size * 4; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    k = s / 64; c = (*CREMA, alpha)
    for r in (27, 15.5):
        d.ellipse(((32 - r) * k, (32 - r) * k, (32 + r) * k, (32 + r) * k), outline=c, width=int(5.5 * k))
    # hueco a 45º hacia arriba a la derecha
    m = Image.new("L", (s, s), 255); dm = ImageDraw.Draw(m)
    dm.line((32 * k, 32 * k, 70 * k, -6 * k), fill=0, width=int(7 * k))
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m))))
    d = ImageDraw.Draw(im); d.ellipse((25 * k, 25 * k, 39 * k, 39 * k), fill=(*NAR, alpha))
    return im.resize((size, size), Image.LANCZOS)

def logo(h=40):
    t = fnt("SemiBold", int(h * 0.82)); tw = t.getbbox("tiro hecho")[2]
    im = Image.new("RGBA", (h + 14 + tw, h + 10), (0, 0, 0, 0)); im.alpha_composite(diana(h), (0, 5))
    ImageDraw.Draw(im).text((h + 14, h / 2 + 5), "tiro hecho", font=t, fill=CREMA, anchor="lm")
    return im

FONDO = Image.open("gfx/fondo.png").convert("RGBA")
LOGO_S = logo(34)

def sombra(im, r=14, a=170):
    al = im.getchannel("A").filter(ImageFilter.GaussianBlur(r))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(al.point(lambda v: v * a // 255))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh); out.alpha_composite(im); return out

def chip(texto, icono="•", grande=False):
    f = fnt("SemiBold", 40 if grande else 34); pad = 26
    tw = f.getbbox(texto)[2]; h = 76 if grande else 66
    im = Image.new("RGBA", (tw + pad * 2 + 42 + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((15, 15, im.width - 16, h + 14), radius=14, fill=(*SUP, 238), outline=(*LIN, 255), width=2)
    cy = 15 + h // 2
    if icono == "check":
        d.ellipse((15 + pad - 4, cy - 15, 15 + pad + 26, cy + 15), fill=NAR)
        d.line((15 + pad + 4, cy, 15 + pad + 10, cy + 7, 15 + pad + 20, cy - 7), fill=(255, 255, 255), width=4)
    elif icono == "menos":
        d.ellipse((15 + pad - 4, cy - 15, 15 + pad + 26, cy + 15), fill=NAR)
        d.line((15 + pad + 4, cy, 15 + pad + 18, cy), fill=(255, 255, 255), width=4)
    else:
        d.ellipse((15 + pad + 2, cy - 9, 15 + pad + 20, cy + 9), fill=NAR)
    d.text((15 + pad + 42, cy), texto, font=f, fill=CREMA, anchor="lm")
    return im

def etiqueta(nombre, rol):
    f1, f2 = fnt("SemiBold", 40), fnt("Regular", 24)
    w = max(f1.getbbox(nombre)[2], f2.getbbox(rol)[2]) + 70
    im = Image.new("RGBA", (w + 30, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((15, 15, w + 15, 114), radius=14, fill=(*SUP, 238), outline=(*LIN, 255), width=2)
    d.rectangle((15 + 22, 34, 15 + 26, 96), fill=NAR)
    d.text((15 + 44, 52), nombre, font=f1, fill=CREMA, anchor="lm"); d.text((15 + 44, 88), rol.upper(), font=f2, fill=GRIS, anchor="lm")
    return im

def golpe(grande, sub, label=None, play=None):
    """Especificación de una pantalla completa animada (se dibuja fotograma a fotograma en pinta_golpe)."""
    return dict(grande=grande, sub=sub, label=label, play=play)

FONDO_G = Image.open("gfx/fondo.png").convert("RGBA").resize((2112, 1188), Image.BICUBIC)
def diana_anim(size, pr, pc, alpha=255):
    """Diana que se dibuja: anillos de 0 a 360º (pr) y el centro naranja que salta (pc)."""
    s = size * 3; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); k = s / 64
    for j, r in enumerate((27, 15.5)):
        q = min(1, max(0, pr * 1.25 - j * 0.25))
        if q > 0: d.arc(((32 - r) * k, (32 - r) * k, (32 + r) * k, (32 + r) * k), -45, -45 + 360 * q, fill=(*CREMA, alpha), width=int(5.5 * k))
    m = Image.new("L", (s, s), 255); ImageDraw.Draw(m).line((32 * k, 32 * k, 70 * k, -6 * k), fill=0, width=int(7 * k))
    im.putalpha(Image.fromarray(np.minimum(np.asarray(im.getchannel("A")), np.asarray(m))))
    if pc > 0:
        sc = 1 + 0.35 * np.sin(min(pc, 1) * np.pi) if pc < 1 else 1
        r = 7 * sc * min(1, pc * 2)
        ImageDraw.Draw(im).ellipse(((32 - r) * k, (32 - r) * k, (32 + r) * k, (32 + r) * k), fill=(*NAR, alpha))
    return im.resize((size, size), Image.LANCZOS)

GCACHE = {}
def txt_img(t, f, color):
    key = (t, id(f), color)
    if key not in GCACHE:
        bb = f.getbbox(t); im = Image.new("RGBA", (bb[2] + 40, f.size * 2), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, f.size), t, font=f, fill=color, anchor="lm"); GCACHE[key] = im
    return GCACHE[key]

def sube(fr, im, x, y, p, blur=8, dy=46):
    """Entrada de un texto: sube desde abajo, de borroso a nítido."""
    if p <= 0: return
    p = ease(p); img = im
    if p < 1:
        img = im.filter(ImageFilter.GaussianBlur(blur * (1 - p))) if blur else im.copy()
        img.putalpha(img.getchannel("A").point(lambda v: int(v * p)))
    fr.alpha_composite(img, (int(x - 20), int(y - im.height // 2 + dy * (1 - p))))

def cuenta(t, p):
    """'30–40' cuenta desde 0 mientras entra."""
    nums = re.findall(r"\d+", t)
    if not nums or p >= 1: return t
    out = t
    for n in nums: out = out.replace(n, str(int(int(n) * ease(p))), 1)
    return out

def pinta_golpe(spec, dt, dur):
    # fondo con el brillo que se mueve despacio
    ox = int(96 + 80 * np.sin(dt * 0.9)); oy = int(54 + 40 * np.cos(dt * 0.7))
    fr = FONDO_G.crop((ox, oy, ox + W, oy + H)).copy()
    fr.alpha_composite(diana_anim(84, min(1, dt / 0.45), max(0, (dt - 0.3) / 0.3)), (W // 2 - 42, 196))
    if spec["label"]:
        fl = fnt("SemiBold", 28); sube(fr, txt_img(spec["label"].upper(), fl, NAR), W // 2 - fl.getbbox(spec["label"].upper())[2] // 2, 330, (dt - 0.12) / 0.3, 4, 18)
    big = "".join(t for t, _ in spec["grande"]); fg = fnt("SemiBold", 150 if len(big) < 12 else 110)
    tot = sum(fg.getbbox(t)[2] for t, _ in spec["grande"]); x = W // 2 - tot // 2
    for j, (t, o) in enumerate(spec["grande"]):
        p = (dt - 0.08 - 0.09 * j) / 0.32
        tt = cuenta(t, (dt - 0.08) / 0.5) if re.search(r"\d", t) else t
        sube(fr, txt_img(tt, fg, NAR if o else CREMA), x, 540, p)
        if o and t.strip():  # subrayado naranja que crece
            q = ease((dt - 0.45 - 0.09 * j) / 0.3)
            if q > 0:
                w = fg.getbbox(t.strip())[2]; x0 = x + (fg.getbbox(t)[2] - fg.getbbox(t.lstrip())[2])
                ImageDraw.Draw(fr).rounded_rectangle((x0, 622, x0 + w * q, 630), radius=4, fill=(*NAR, 255))
        x += fg.getbbox(t)[2]
    p = (dt - 0.4) / 0.35; fs = fnt("Regular", 44)
    if spec["play"]:
        a, b = spec["sub"].split("|"); fp = fnt("play", 50)
        wa, wb = fs.getbbox(a)[2], fp.getbbox(b)[2]; x = W // 2 - (wa + wb) // 2
        sube(fr, txt_img(a, fs, GRIS), x, 700, p, 4, 20); sube(fr, txt_img(b, fp, NAR), x + wa, 696, (dt - 0.6) / 0.35, 6, 20)
    else:
        sube(fr, txt_img(spec["sub"], fs, GRIS), W // 2 - fs.getbbox(spec["sub"])[2] // 2, 700, p, 4, 20)
    return fr

# ---------- línea de tiempo de gráficos ----------
EV = []   # dict(t0, t1, tipo, img, x, y, anim)
def G(t0, dur, img, sfx="golpe"): EV.append(dict(t0=t0, t1=t0 + dur, tipo="golpe", img=img, sfx=sfx))
def C(t0, t1, img, x, y, sfx="pop"): EV.append(dict(t0=t0, t1=t1, tipo="chip", img=img, x=x, y=y, sfx=sfx))
def fila(t_lista, t1, textos, y, icono="check", sfx="pop"):
    ims = [chip(t, icono) for t in textos]; gap = -6
    tot = sum(i.width for i in ims) + gap * (len(ims) - 1); x = W // 2 - tot // 2
    for t, im in zip(t_lista, ims): C(t, t1, im, x, y, sfx); x += im.width + gap
def col(t_lista, t1, textos, x, y0, icono="check", sfx="pop"):
    for k, (t, s) in enumerate(zip(t_lista, textos)): C(t, t1, chip(s, icono), x, y0 + k * 78, sfx)

# Bloque 1 · dolor
t = at("30–40 minutos editando"); G(t, 1.9, golpe([("30–40", True), (" min", False)], "editando cada vídeo", "Lo que tarda un entrenador"))
t = at("30–40 euros por vídeo"); G(t, 1.8, golpe([("30–40", True), (" €", False)], "por vídeo si lo delegas", "Lo que cuesta un editor"))
t = at("no tiene ideas"); C(t, at("Claro, tiene lógica"), chip("Sin ideas de contenido", "menos", True), None, 700)
ts = [at("pensando en ideas"), at("ir a grabar"), at("tengo que editarlo"), at("tengo que publicarlo")]
fila(ts, at("Vale, pues la jugada") - 0.1, ["Pensar ideas", "Grabar", "Editar", "Publicar"], 700, "dot")
t = at("lo editamos con inteligencia"); G(t - 0.15, 1.7, golpe([("Edición con ", False), ("IA", True)], "Sin trucos. |Sin magia.", None, play=True))
t = at("Este vídeo que estás"); C(t, at("Somos persona 2") , chip("Este vídeo: editado con IA", "check", True), None, 700, "notif")
EV.append(dict(t0=at("Somos persona 2"), t1=at("agencia de marketing", fin=True) + 1.2, tipo="nombres", sfx="swipe"))
fila([at("mucho menos tiempo"), at("muchísimo menos dinero")], at("Y esto está sonando") + 0.3, ["Menos tiempo", "Menos dinero"], 700, "menos")
ts = [at("quita los silencios"), at("pone los subtítulos"), at("pone la música")]
fila(ts, at("Chavales, es que") + 0.4, ["Quita los silencios", "Pone subtítulos", "Pone la música"], 700, "check")
t = at("Vamos a empezar por"); G(t + 0.3, 1.6, golpe([("Entrenadores", True)], "personales. Empezamos por vosotros.", "El curso es para"))
t = at("De hecho, te lo"); G(t - 0.05, at("Esto que te vamos") - t + 0.05, golpe([("Te lo ", False), ("enseñamos", True)], "Así lo hacemos nosotros"), "transicion")
# Bloque 2 · demo
t = at("clase de tres horas"); G(t, 1.6, golpe([("3", True), (" horas", False)], "Al grano. |Sin paja.", "Una clase", play=True))
t = at("Vamos a tiro hecho"); C(t, t + 1.8, logo(56), None, 690, "golpe_suave")
ts = [at("del titular"), at("los planos"), at("del arranque"), at("los recursos"), at("del ritmo"), at("la música, los"), at("los subtítulos, todo")]
fila(ts[:4], at("Una vez que me") , ["Titular", "Planos", "Arranque", "Recursos"], 620, "check")
fila(ts[4:], at("Una vez que me"), ["Ritmo", "Música", "Subtítulos"], 705, "check")
fila([at("me mete los subtítulos"), at("mete zooms")], at("chavales esto") , ["Subtítulos", "Zooms"], 700, "check")
t = at("esto es brutal"); C(t, t + 1.3, chip("Brutal", "check", True), None, 690, "golpe_suave")
t = at("nueve vídeos"); G(t - 0.1, 2.1, golpe([("10 min", False), ("  →  ", True), ("9 vídeos", True)], "de una sola grabación en bruto", "Con la clienta"))
t = at("La promesa es sencilla"); G(t + 0.9, at("de vídeo.", fin=True) - t - 0.8, golpe([("Ahorra ", False), ("tiempo", True), (" y ", False), ("dinero", True)], "en la edición de cada vídeo", "La promesa"))
# Bloque 3 · el PDF
t = at("este PDF que tiene"); C(t, at("Claro, pero estos"), chip("PDF con 100 guiones listos para grabar", "check", True), None, 20)
t = at("en 5 minutos"); C(t, t + 2.2, chip("PDFs como este en 5 minutos", "check", True), None, 20)
t = at("para 3 meses"); C(t, t + 1.8, chip("Contenido para 3 meses", "check", True), None, 20)
ts = [at("El gancho"), at("lo que tiene que decir"), at("el cómo grabarlo"), at("el vídeo de referencia"), at("el número de visitas")]
col(ts, at("Efectivamente") + 1.2, ["El gancho", "Qué decir", "Cómo grabarlo", "Vídeo de referencia", "Nº de visitas"], 60, 300, "check")
t = at("A los 10 primeros"); G(t, at("pero además les vas") - t, golpe([("Regalo", True)], "Los 10 primeros: el PDF con |100 guiones", "Primera edición", play=True), "transicion")
t = at("La formación incluye"); C(t, 999, chip("Incluye: editar tus vídeos con IA", "check", True), None, 700, "notif")

json.dump([dict(t=e["t0"], t1=e["t1"], sfx=e["sfx"], tipo=e["tipo"]) for e in EV] +
          [dict(t=round(P[-1]["t0"] * FPS + P[-1]["n"]) / FPS, t1=0, sfx="outro", tipo="outro")], open("eventos.json", "w"), indent=0)

# ---------- subtítulos ----------
FS, FB = fnt("Bold", 64), fnt("play", 72)
CLAVE = set("""entrenador personal entrenadores personales minutos euros pavos vídeo capcut edits ideas constante grabar
editarlo publicarlo inteligencia artificial magia funciona oportunidad tiempo dinero marketing verdad bruto silencios
subtítulos música enseñar tres horas paja tiro hecho clienta cliente herramienta titular planos arranque recursos ritmo zooms brutal
estilo nueve diez promesa sencilla ahorrar pdf guiones 100 metodología meses gancho referencia visitas regalar formación claude""".split())
PLAY = {"verdad", "brutal", "magia", "funciona", "regalar"}
bloques = []; cur = []
for w in Wd:
    if cur and (len(cur) >= 3 or w[0] - cur[-1][1] > 0.35 or re.search(r"[.,?!…]$", cur[-1][2])):
        bloques.append(cur); cur = []
    cur.append(w)
bloques.append(cur)
def clave(b):
    best = None
    for k, w in enumerate(b):
        n = norm(w[2])
        if re.match(r"\d", n) or n in CLAVE: best = k
    return best
SUBS = []
for b in bloques:
    k = clave(b); t1 = b[-1][1] + 0.25
    SUBS.append(dict(t0=b[0][0] - 0.05, t1=t1, w=[(x[0] - 0.05, x[2].strip(), i == k, norm(x[2]) in PLAY and i == k) for i, x in enumerate(b)]))
for i in range(len(SUBS) - 1): SUBS[i]["t1"] = min(SUBS[i]["t1"], SUBS[i + 1]["t0"])

CACHE = {}
FSUB = fnt("Bold", 56)
def palabra_img(txt, naranja, play):
    key = (txt, play)
    if key not in CACHE:
        f = FB if play else FSUB; bb = f.getbbox(txt)
        im = Image.new("RGBA", (bb[2] + 4, 90), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((2, 45), txt, font=f, fill=CREMA, anchor="lm")
        CACHE[key] = (im, bb[2])
    return CACHE[key]

def dibuja_subs(fr, t):
    """Subtítulos modernos: caja tinta translúcida que crece con cada palabra y una píldora naranja
    que salta a la palabra que se está diciendo. Sin sombras."""
    s = next((s for s in SUBS if s["t0"] <= t < s["t1"]), None)
    if not s: return
    items = [(w0, palabra_img(txt, o, p)) for w0, txt, o, p in s["w"]]
    esp = 22; padx, h = 30, 92; tot = sum(iw for _, (_, iw) in items) + esp * (len(items) - 1)
    x0 = W // 2 - tot // 2; y = 930
    xs = []; x = x0
    for _, (_, iw) in items: xs.append(x); x += iw + esp
    vis = [k for k, (w0, _) in enumerate(items) if t >= w0] or [0]
    k = vis[-1]
    # entrada y salida del bloque
    a = ease((t - s["t0"]) / 0.12) * (1 - ease((t - (s["t1"] - 0.06)) / 0.06))
    if a <= 0.02: return
    # caja: ancho hasta la última palabra visible (animado)
    dk = ease((t - items[k][0]) / 0.12)
    der_prev = xs[k - 1] + items[k - 1][1][1] if k else xs[0] + items[0][1][1] * 0.6
    der = der_prev + (xs[k] + items[k][1][1] - der_prev) * dk
    lay = Image.new("RGBA", (W, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 - padx, 34, der + padx, 34 + h), radius=20, fill=(11, 11, 12, int(205 * a)))
    # píldora naranja: se desliza a la palabra activa
    px0 = xs[k - 1] if k and dk < 1 else xs[k]; pw0 = items[k - 1][1][1] if k and dk < 1 else items[k][1][1]
    px = px0 + (xs[k] - px0) * dk; pw = pw0 + (items[k][1][1] - pw0) * dk
    d.rounded_rectangle((px - 12, 46, px + pw + 12, 34 + h - 12), radius=12, fill=(*NAR, int(255 * a)))
    for j in vis:
        im, iw = items[j][1]; q = ease((t - items[j][0]) / 0.1)
        img = im if q >= 1 and a >= 1 else im.copy()
        if img is not im: img.putalpha(img.getchannel("A").point(lambda v: int(v * q * a)))
        lay.alpha_composite(img, (int(xs[j] - 2), int(34 + h / 2 - 45 + 10 * (1 - q))))
    # salto de escala de la caja al entrar
    fr.alpha_composite(lay, (0, y - 34 - h // 2))


# ---------- nombres sobre cada uno ----------
CARAS = {"S": (0.665, 0.33), "T": (0.275, 0.31), "?": (0.47, 0.33)}
def pos_pantalla(p, fx, fy):
    z = p["zoom"]
    if z == 1.0: return fx * W, fy * H
    w = 3840 / z; h = 2160 / z; cfx, cfy = CARAS[p.get("habla", "?")]
    cx = cfx * 3840; cy = cfy * 2160 + h * 0.15
    x = min(max(cx - w / 2, 0), 3840 - w); y = min(max(cy - h / 2, 0), 2160 - h)
    return (fx * 3840 - x) / w * W, (fy * 2160 - y) / h * H
ET_S, ET_T = etiqueta("persona 2", "Tiro Hecho"), etiqueta("persona 1", "Tiro Hecho")

def plano_en(t): return next(p for p in reversed(P) if p["t0"] <= t)

# ---------- composición ----------
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def muelle(x):
    x = min(max(x, 0), 1); return 1 - np.exp(-6 * x) * np.cos(9 * x) if x < 1 else 1
def entra(img, x, y, t, e):
    pin = (t - e["t0"]) / 0.38; pout = ease((t - (e["t1"] - 0.16)) / 0.16)
    if pin <= 0 or pout >= 1: return None
    sc = 0.55 + 0.45 * muelle(pin); a = min(1, pin * 4) * (1 - pout); sc *= 1 - 0.1 * pout
    im = img
    if abs(sc - 1) > 0.005:
        im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    return im, int(x + (img.width - im.width) / 2), int(y + (img.height - im.height) / 2 + 14 * pout)


def frame(fr, t):
    g = [e for e in EV if e["tipo"] == "golpe" and e["t0"] <= t < e["t1"]]
    if g:
        e = g[-1]; dt = t - e["t0"]; dur = e["t1"] - e["t0"]
        im = pinta_golpe(e["img"], dt, dur)
        pin = ease(dt / 0.16); pout = ease((t - (e["t1"] - 0.14)) / 0.14)
        if pin < 1:   # el vídeo se aleja y desenfoca mientras entra la pantalla
            v = fr.resize((int(W * (1 + 0.25 * pin)), int(H * (1 + 0.25 * pin))), Image.BILINEAR)
            v = v.crop(((v.width - W) // 2, (v.height - H) // 2, (v.width - W) // 2 + W, (v.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(14 * pin))
            fr = Image.blend(v.convert("RGBA"), im, pin)
        elif pout > 0:
            s2 = 1 + 0.06 * pout
            g2 = im.resize((int(W * s2), int(H * s2)), Image.BILINEAR).crop((int((W * s2 - W) / 2), int((H * s2 - H) / 2), int((W * s2 - W) / 2) + W, int((H * s2 - H) / 2) + H))
            fr = Image.blend(g2, fr.convert("RGBA"), pout)
        else:
            fr = im
        fr.alpha_composite(LOGO_S, (W - LOGO_S.width - 48, 40))
        return fr
    fr = fr.convert("RGBA")
    for e in EV:
        if not (e["t0"] <= t < e["t1"]): continue
        if e["tipo"] == "chip":
            img = e["img"]; x = e["x"] if e["x"] is not None else W // 2 - img.width // 2
            r = entra(img, x, e["y"], t, e)
            if r: fr.alpha_composite(r[0], (int(r[1]), r[2]))
        elif e["tipo"] == "nombres":
            p = plano_en(t)
            for et, cara, dx in ((ET_S, CARAS["S"], 0), (ET_T, CARAS["T"], 0)):
                x, y = pos_pantalla(p, cara[0], cara[1] + 0.27)
                if -100 < x < W + 100:
                    r = entra(et, int(x - et.width / 2), int(min(y, 760)), t, e)
                    if r: fr.alpha_composite(r[0], (r[1], r[2]))
    dibuja_subs(fr, t)
    fr.alpha_composite(LOGO_S, (W - LOGO_S.width - 48, 40))
    return fr

T_FIN = round(P[-1]["t0"] * FPS + P[-1]["n"]) / FPS; OUTRO = 4.5
def pinta_outro(dt):
    ox = int(96 + 80 * np.sin(dt * 0.9)); oy = int(54 + 40 * np.cos(dt * 0.7))
    fr = FONDO_G.crop((ox, oy, ox + W, oy + H)).copy()
    sz = 210; fr.alpha_composite(diana_anim(sz, min(1, dt / 0.6), max(0, (dt - 0.45) / 0.35)), (W // 2 - sz // 2, 300))
    fw = fnt("SemiBold", 92); sube(fr, txt_img("tiro hecho", fw, CREMA), W // 2 - fw.getbbox("tiro hecho")[2] // 2, 610, (dt - 0.7) / 0.4)
    ft = fnt("Regular", 40); a = "Formación al grano con "; b = "IA"
    wa = ft.getbbox(a)[2]; wb = fnt("SemiBold", 40).getbbox(b)[2]; x = W // 2 - (wa + wb) // 2
    sube(fr, txt_img(a, ft, GRIS), x, 700, (dt - 1.0) / 0.4, 4, 18); sube(fr, txt_img(b, fnt("SemiBold", 40), NAR), x + wa, 700, (dt - 1.1) / 0.4, 4, 18)
    q = ease((dt - 1.3) / 0.5)
    if q > 0: ImageDraw.Draw(fr).rounded_rectangle((W // 2 - 160 * q, 760, W // 2 + 160 * q, 766), radius=3, fill=(*NAR, 255))
    f = 1 - ease((dt - (OUTRO - 0.6)) / 0.6)   # fundido a negro al final
    if f < 1: fr = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), fr, f)
    return fr

if __name__ == "__main__":
    solo = [float(x) for x in sys.argv[1:]]
    if solo:  # vista previa de fotogramas sueltos
        for t in solo:
            if t >= T_FIN:
                pinta_outro(t - T_FIN).convert("RGB").save(f"prev_{t:06.2f}.jpg", quality=85); continue
            raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", "base.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            fr = Image.frombytes("RGB", (W, H), raw); frame(fr, t).convert("RGB").save(f"prev_{t:06.2f}.jpg", quality=85)
        raise SystemExit
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "base.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "montado.mp4"], stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        fr = frame(Image.frombytes("RGB", (W, H), raw), n / FPS).convert("RGB")
        enc.stdin.write(fr.tobytes()); n += 1
        if n % 600 == 0: print(n, flush=True)
    ultimo = fr
    for j in range(int(OUTRO * FPS)):
        dt = j / FPS; im = pinta_outro(dt); p = ease(dt / 0.25)
        if p < 1:
            v = ultimo.resize((int(W * (1 + 0.25 * p)), int(H * (1 + 0.25 * p))), Image.BILINEAR)
            v = v.crop(((v.width - W) // 2, (v.height - H) // 2, (v.width - W) // 2 + W, (v.height - H) // 2 + H)).filter(ImageFilter.GaussianBlur(14 * p))
            im = Image.blend(v.convert("RGBA"), im, p)
        enc.stdin.write(im.convert("RGB").tobytes()); n += 1
    enc.stdin.close(); enc.wait(); print("fotogramas", n)
