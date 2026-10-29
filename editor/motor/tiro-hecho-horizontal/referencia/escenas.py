# REFERENCIA del VSL de Tiro Hecho (horizontal). No es un motor genérico: Claude lo adapta a cada vídeo.
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'comun')); from rutas import *
# VSL Tiro Hecho v3: escenas DISEÑADAS (recortes sobre fondo de marca, interfaces, pantalla partida, tipografía cinética).
# Uso: python3 escenas.py muestra 0 55   |   python3 escenas.py prev 2.5 10 ...
import sys, json, subprocess, re, os, numpy as np
from PIL import Image, ImageDraw, ImageFilter
import gfx as G
import subs3 as S3
import subs4 as S4
from gfx import fnt, ease, muelle, txt_img, sube, diana_anim, NAR, CREMA, GRIS, SUP, LIN, W, H, FPS, at
import onnxruntime as ort

TINTA = (11, 11, 12)
SEG = ort.InferenceSession(os.path.join(MODELOS, "u2net_human_seg.onnx"), providers=["CPUExecutionProvider"])
os.makedirs("mascaras", exist_ok=True)

def mascara(fr, n):
    p = f"mascaras/{n:05d}.png"
    if os.path.exists(p): return Image.open(p)
    x = np.asarray(fr.resize((320, 320), Image.BILINEAR), np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    o = SEG.run(None, {SEG.get_inputs()[0].name: x})[0][0, 0]; o = (o - o.min()) / (o.max() - o.min() + 1e-6)
    m = Image.fromarray((np.clip((o - 0.15) / 0.7, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5))
    m.save(p); return m

def fondo(t, oscuro=0.0):
    ox = int(96 + 80 * np.sin(t * 0.9)); oy = int(54 + 40 * np.cos(t * 0.7))
    f = G.FONDO_G.crop((ox, oy, ox + W, oy + H)).copy()
    if oscuro: f = Image.blend(f, Image.new("RGBA", (W, H), (*TINTA, 255)), oscuro)
    return f

def fondo_v(vid, osc=0.42):
    v = vid.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC).convert("RGBA")
    return Image.blend(v, Image.new("RGBA", (W, H), (*TINTA, 255)), osc)

def redondea(im, r):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=r, fill=255)
    im = im.convert("RGBA"); im.putalpha(m); return im

def tarjeta_video(lienzo, vid, caja, r=22):
    x0, y0, x1, y1 = [int(v) for v in caja]; w, h = x1 - x0, y1 - y0
    # recorte 16:9 que llena la caja
    sc = max(w / W, h / H); v = vid.resize((int(W * sc), int(H * sc)), Image.BILINEAR)
    v = v.crop(((v.width - w) // 2, (v.height - h) // 2, (v.width - w) // 2 + w, (v.height - h) // 2 + h))
    lienzo.alpha_composite(redondea(v, r), (x0, y0))
    ImageDraw.Draw(lienzo).rounded_rectangle((x0, y0, x1, y1), radius=r, outline=(*LIN, 255), width=2)

def lerp(a, b, p): return [x + (y - x) * p for x, y in zip(a, b)]

def ventana(w, h, titulo="", r=18):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=(*SUP, 255), outline=(*LIN, 255), width=2)
    d.line((0, 54, w, 54), fill=(*LIN, 255), width=2)
    for k, c in enumerate([(70, 70, 76)] * 3): d.ellipse((24 + k * 26, 20, 38 + k * 26, 34), fill=c)
    if titulo: d.text((w // 2, 27), titulo, font=fnt("SemiBold", 22), fill=GRIS, anchor="mm")
    return im

def gigante(lienzo, txt, y, size, color, p, sep=-0.03, x=None):
    """Texto enorme que se abre desde el centro (tracking) y sube."""
    if p <= 0: return
    f = S3.hn_cb(size); w0 = f.getbbox(txt)[2]
    if w0 > 1820: f = S3.hn_cb(int(size * 1820 / w0))
    e = ease(p)
    w = f.getbbox(txt)[2]; im = Image.new("RGBA", (w + 80, int(size * 1.4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((40, size * 0.7), txt, font=f, fill=(46, 44, 42, 205) if color == TINTA else color, anchor="lm")
    s = 0.9 + 0.1 * e; im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
    if e < 1: im.putalpha(im.getchannel("A").point(lambda v: int(v * e)))
    cx = W // 2 if x is None else x
    pos = (int(cx - im.width / 2), int(y - im.height / 2 + 60 * (1 - e)))
    lienzo.alpha_composite(im, pos)

# ---------------- escenas ----------------
ES = []
def E(t0, t1, tipo, **k): ES.append(dict(t0=t0, t1=t1, tipo=tipo, **k))

E(at("entrenador personal?") - 0.25, at("Hombre,"), "recorte", textos=[("¿ENTRENADOR", 0, TINTA), ("PERSONAL?", 0.12, NAR)])
E(at("El otro día"), at("Joder, no solo"), "editor")
E(at("Joder, no solo"), at("O sea, que ese"), "factura")
E(at("O sea, que ese"), at("Y no solo eso, sino"), "recorte_cifras",
  cifras=[(at("30–40 pavos"), "30–40 €"), (at("30–40 minutos editándolo"), "30–40 MIN"), (at("CapCut"), "CAPCUT")])
E(at("Y no solo eso, sino"), at("Al final dices"), "calendario")
E(at("Al final dices"), at("Vale, pues la jugada"), "lista",
  items=[(at("tengo mi trabajo"), "Entrenar a tus clientes"), (at("pensando en ideas"), "Pensar ideas"),
         (at("ir a grabar"), "Grabar"), (at("tengo que editarlo"), "Editar"), (at("tengo que publicarlo"), "Publicar")])
E(at("Vale, pues la jugada"), at("Aquí no hay trucos"), "chat")
E(at("Aquí no hay trucos"), at("Este vídeo que estás"), "tachado",
  palabras=[(at("no hay trucos"), "TRUCOS", True), (at("no hay magia"), "MAGIA", True), (at("esto funciona"), "FUNCIONA", False)])
E(at("Este vídeo que estás"), at("Somos persona 2"), "meta")
E(at("Somos persona 2"), at("agencia de marketing", fin=True) + 0.6, "nombres")

SIN_SUBS = {"factura", "calendario", "chat", "tachado"}

def escena_en(t): return next((e for e in ES if e["t0"] <= t < e["t1"]), None)

# ---- pintores ----
def persona(e, vid, n, s=0.78):
    """Recorte de la persona, reducido y apoyado en el borde de abajo (sin hueco bajo el corte del portátil)."""
    m = mascara(vid, n)
    if "fondo_y" not in e:
        a = np.asarray(m) > 128; filas = np.where(a.sum(1) > 40)[0]; e["fondo_y"] = int(filas.max()) if len(filas) else H
    per = vid.convert("RGBA"); per.putalpha(m)
    per = per.crop((0, 0, W, e["fondo_y"])); per = per.resize((int(W * s), int(per.height * s)), Image.BICUBIC)
    return per, (W - per.width) // 2, H - per.height

def p_recorte(e, t, vid, n, cifra=None):
    dt = t - e["t0"]; lien = vid.convert("RGBA")
    for txt, d0, col in e.get("textos", []):
        k = e["textos"].index((txt, d0, col))
        gigante(lien, txt, 120 + k * 190, 200, col, (dt - d0) / 0.35)
    if cifra: gigante(lien, cifra[1], 190, 330, NAR, (t - cifra[0]) / 0.3)
    m = mascara(vid, n); per = vid.convert("RGBA"); per.putalpha(m); lien.alpha_composite(per)
    return lien

def p_editor(e, t, vid, n):
    dt = t - e["t0"]; d = e["t1"] - e["t0"]; lien = fondo_v(vid)
    p = ease(dt / 0.45)
    tarjeta_video(lien, vid, lerp((0, 0, W, H), (70, 250, 870, 700), p), 22 * p)
    # ventana del editor a la derecha
    a = ease((dt - 0.15) / 0.4)
    if a > 0:
        v = ventana(900, 640, "Editando · reel_cliente.mp4")
        d2 = ImageDraw.Draw(v)
        # pistas de la línea de tiempo
        for k, (nom, col) in enumerate([("Vídeo", (90, 90, 98)), ("Cortes", (120, 120, 128)), ("Texto", NAR), ("Audio", (70, 70, 76))]):
            y = 380 + k * 56; d2.text((24, y + 18), nom, font=fnt("Regular", 20), fill=GRIS, anchor="lm")
            x = 120; r = np.random.RandomState(k)
            while x < 870:
                w = int(r.uniform(40, 140)); q = min(1, max(0, (dt * 260 - (x - 120)) / 80))
                if q > 0: d2.rounded_rectangle((x, y, x + w * q, y + 36), radius=6, fill=(*col, 255))
                x += w + 6
        ph = 120 + (dt / d) * 750; d2.line((ph, 360, ph, 610), fill=(255, 255, 255), width=3)
        # reloj
        mins = 40 * ease(min(1, dt / (d * 0.8)))
        d2.text((450, 200), f"{int(mins):02d}:{int((mins % 1) * 60):02d}", font=fnt("SemiBold", 150), fill=NAR, anchor="mm")
        d2.text((450, 300), "MINUTOS EDITANDO UN SOLO VÍDEO", font=fnt("SemiBold", 24), fill=GRIS, anchor="mm")
        v.putalpha(v.getchannel("A").point(lambda x: int(x * a)))
        lien.alpha_composite(v, (950, int(220 + 40 * (1 - a))))
    return lien

def p_factura(e, t, vid, n):
    dt = t - e["t0"]; lien = fondo_v(vid, 0.6)
    w, h = 620, 760; tick = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(tick)
    d.rectangle((0, 0, w, h - 20), fill=(245, 241, 234, 255))
    for x in range(0, w, 30): d.polygon([(x, h - 20), (x + 15, h), (x + 30, h - 20)], fill=(245, 241, 234, 255))  # borde dentado
    ink = (11, 11, 12); g = (110, 110, 116)
    d.text((w // 2, 70), "EDITOR FREELANCE", font=fnt("Bold", 34), fill=ink, anchor="mm")
    d.text((w // 2, 112), "Factura nº 0347", font=fnt("Regular", 22), fill=g, anchor="mm")
    for k in range(6): d.line((40 + k * 95, 150, 80 + k * 95, 150), fill=g, width=2)
    filas = [("Edición reel", "1 ud."), ("Cortes y ritmo", "incl."), ("Subtítulos", "incl."), ("Música", "incl.")]
    for k, (a_, b_) in enumerate(filas):
        y = 200 + k * 58; d.text((50, y), a_, font=fnt("Regular", 28), fill=ink, anchor="lm"); d.text((w - 50, y), b_, font=fnt("Regular", 28), fill=g, anchor="rm")
    d.line((40, 440, w - 40, 440), fill=ink, width=3)
    d.text((50, 510), "TOTAL", font=fnt("Bold", 40), fill=ink, anchor="lm")
    d.text((w - 50, 510), "30–40 €", font=fnt("ExtraBold", 64), fill=NAR, anchor="rm")
    d.text((w // 2, 620), "…y la semana que viene, otra.", font=fnt("Regular", 24), fill=g, anchor="mm")
    # sale de una ranura de arriba (impresora)
    p = ease(dt / 0.9); vis = int(h * p)
    lien_t = tick.crop((0, h - vis, w, h)) if vis > 0 else None
    ImageDraw.Draw(lien).rounded_rectangle((W // 2 - 360, 120, W // 2 + 360, 150), radius=15, fill=(30, 30, 33, 255))
    if lien_t: lien.alpha_composite(lien_t, (W // 2 - w // 2, 140))
    # sello «POR VÍDEO»
    s = (dt - 1.0) / 0.25
    if s > 0:
        st = Image.new("RGBA", (330, 120), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
        ds.rounded_rectangle((4, 4, 326, 116), radius=12, outline=(*NAR, 255), width=7)
        ds.text((165, 62), "POR VÍDEO", font=fnt("ExtraBold", 50), fill=NAR, anchor="mm")
        st = st.rotate(-12, expand=True, resample=Image.BICUBIC); sc = 1 + 0.6 * (1 - muelle(s))
        st = st.resize((int(st.width * sc), int(st.height * sc)), Image.BICUBIC)
        lien.alpha_composite(st, (int(W // 2 + 150 - st.width / 2), int(560 - st.height / 2)))
    return lien

def p_recorte_cifras(e, t, vid, n):
    c = [x for x in e["cifras"] if x[0] <= t]
    return p_recorte(e, t, vid, n, c[-1] if c else None)

def p_calendario(e, t, vid, n):
    dt = t - e["t0"]; lien = fondo_v(vid, 0.6)
    v = ventana(980, 720, "Instagram · tus publicaciones"); d = ImageDraw.Draw(v)
    dias = ["L", "M", "X", "J", "V", "S", "D"]
    for k, dd in enumerate(dias): d.text((110 + k * 128, 100), dd, font=fnt("SemiBold", 26), fill=GRIS, anchor="mm")
    pub = {0, 2, 4, 8}  # días con publicación: se va apagando
    for i in range(28):
        r, c = divmod(i, 7); x, y = 60 + c * 128, 140 + r * 130; q = ease((dt - i * 0.03) / 0.25)
        if q <= 0: continue
        d.rounded_rectangle((x, y, x + 100, y + 100), radius=14, fill=(28, 28, 31, int(255 * q)), outline=(*LIN, 255), width=2)
        d.text((x + 14, y + 18), str(i + 1), font=fnt("Regular", 20), fill=GRIS, anchor="lm")
        if i in pub: d.ellipse((x + 34, y + 38, x + 66, y + 70), fill=(*NAR, int(255 * q)))
        elif i > 8 and dt > 1.2 + (i - 9) * 0.05: d.line((x + 30, y + 54, x + 70, y + 54), fill=(80, 80, 86), width=4)
    a = ease(dt / 0.35); v.putalpha(v.getchannel("A").point(lambda x: int(x * a)))
    lien.alpha_composite(v, (W // 2 - 490, int(200 + 40 * (1 - a))))
    gigante(lien, "CONSTANCIA", 130, 92, CREMA, (dt - 0.2) / 0.3)
    b = (t - at("no tiene ideas")) / 0.3   # bocadillo «¿Qué grabo hoy?»
    if b > 0:
        bub = Image.new("RGBA", (470, 150), (0, 0, 0, 0)); db = ImageDraw.Draw(bub)
        db.rounded_rectangle((0, 0, 469, 120), radius=26, fill=(*NAR, 255)); db.polygon([(60, 118), (100, 118), (50, 149)], fill=(*NAR, 255))
        cur = "|" if int(t * 3) % 2 else ""
        db.text((235, 60), "¿Qué grabo hoy?" + cur, font=fnt("Bold", 44), fill=(255, 255, 255), anchor="mm")
        s = 0.5 + 0.5 * muelle(b); bub = bub.resize((int(470 * s), int(150 * s)), Image.BICUBIC)
        lien.alpha_composite(bub, (1330 - bub.width // 2, 620 - bub.height // 2))
    return lien

def p_lista(e, t, vid, n):
    dt = t - e["t0"]; lien = fondo_v(vid); p = ease(dt / 0.45)
    tarjeta_video(lien, vid, lerp((0, 0, W, H), (1010, 180, 1850, 652), p), 22 * p)
    gigante(lien, "TU SEMANA", 150, 70, GRIS, (dt - 0.1) / 0.3, x=500)
    vis = [x for x in e["items"] if x[0] <= t]
    for k, (t0, txt) in enumerate(vis):
        q = (t - t0) / 0.35; y = 260 + k * 118; s = 0.6 + 0.4 * muelle(q)
        card = Image.new("RGBA", (780, 100), (0, 0, 0, 0)); dc = ImageDraw.Draw(card)
        dc.rounded_rectangle((0, 0, 779, 99), radius=18, fill=(*SUP, 255), outline=(*LIN, 255), width=2)
        dc.rounded_rectangle((26, 30, 66, 70), radius=9, outline=(*NAR, 255), width=4)
        dc.text((96, 50), txt, font=fnt("SemiBold", 40), fill=CREMA, anchor="lm")
        dc.text((750, 50), ["2 h", "1 h", "1 h", "40 min", "20 min"][k], font=fnt("Regular", 28), fill=GRIS, anchor="rm")
        card = card.resize((int(780 * s), int(100 * s)), Image.BICUBIC)
        if q < 1: card.putalpha(card.getchannel("A").point(lambda v: int(v * min(1, q * 3))))
        sh = 6 * np.sin(t * 60) * max(0, 1 - (t - e["t1"] + 0.8) / 0.8) if len(vis) == 5 and t > e["t1"] - 0.8 else 0
        lien.alpha_composite(card, (int(110 + (780 - card.width) / 2 + sh), int(y + (100 - card.height) / 2)))
    return lien

def p_chat(e, t, vid, n):
    dt = t - e["t0"]; lien = fondo_v(vid, 0.6)
    v = ventana(1180, 700, "Claude"); d = ImageDraw.Draw(v)
    # adjunto
    q = ease((dt - 0.2) / 0.3)
    if q > 0:
        d.rounded_rectangle((640, 110, 1140, 200), radius=16, fill=(32, 32, 36, int(255 * q)), outline=(*LIN, 255), width=2)
        d.rounded_rectangle((660, 128, 714, 182), radius=10, fill=(*NAR, int(255 * q)))
        d.polygon([(680, 140), (680, 170), (702, 155)], fill=(255, 255, 255))
        d.text((734, 140), "bruto_cliente.mov", font=fnt("SemiBold", 26), fill=CREMA, anchor="lm")
        d.text((734, 172), "Vídeo · 4 min", font=fnt("Regular", 20), fill=GRIS, anchor="lm")
    msg = "Edítalo: quita los silencios, pon subtítulos y música."
    k = int(max(0, (dt - 0.5)) * 28); txt = msg[:k]
    if txt:
        f = fnt("Regular", 32); lines = ["Edítalo: quita los silencios,", "pon subtítulos y música."]
        shown = []; rest = len(txt)
        for L_ in lines:
            shown.append(L_[:rest]); rest -= len(L_) + 1
            if rest <= 0: break
        d.rounded_rectangle((420, 230, 1140, 360), radius=22, fill=(*NAR, 255))
        for j, s_ in enumerate(shown): d.text((450, 270 + j * 44), s_, font=f, fill=(255, 255, 255), anchor="lm")
    if dt > 2.8:  # respuesta: lista que se va marcando
        for j, s_ in enumerate(["Silencios eliminados", "Subtítulos añadidos", "Música colocada"]):
            qq = ease((dt - 2.8 - j * 0.3) / 0.25)
            if qq <= 0: continue
            y = 420 + j * 70; d.ellipse((60, y - 18, 96, y + 18), fill=(*NAR, int(255 * qq)))
            d.line((70, y, 76, y + 7, 87, y - 7), fill=(255, 255, 255), width=4)
            d.text((116, y), s_, font=fnt("SemiBold", 32), fill=(*CREMA, int(255 * qq)), anchor="lm")
    # caja de escribir
    d.rounded_rectangle((40, 620, 1140, 680), radius=30, fill=(28, 28, 31, 255), outline=(*LIN, 255), width=2)
    d.text((76, 650), "Escribe a Claude…", font=fnt("Regular", 24), fill=(90, 90, 96), anchor="lm")
    a = ease(dt / 0.35); v.putalpha(v.getchannel("A").point(lambda x: int(x * a)))
    lien.alpha_composite(v, (W // 2 - 590, int(190 + 50 * (1 - a))))
    return lien

def p_tachado(e, t, vid, n):
    lien = fondo_v(vid, 0.72)
    for k, (t0, txt, tach) in enumerate(e["palabras"]):
        p = (t - t0) / 0.25
        if p <= 0: continue
        y = 300 + k * 230; col = (225, 222, 216) if tach else NAR
        gigante(lien, txt, y, 200, col if tach else NAR, p)
        if tach:
            q = ease((t - t0 - 0.35) / 0.2)
            if q > 0:
                w = fnt("ExtraBold", 200).getbbox(txt)[2]
                ImageDraw.Draw(lien).rounded_rectangle((W // 2 - w // 2 - 20, y - 6, W // 2 - w // 2 - 20 + (w + 40) * q, y + 14), radius=8, fill=(*NAR, 255))
    return lien

def p_meta(e, t, vid, n):
    dt = t - e["t0"]; d = e["t1"] - e["t0"]; lien = fondo_v(vid); p = ease(dt / 0.5)
    caja = lerp((0, 0, W, H), (360, 110, 1560, 785), p)
    tarjeta_video(lien, vid, caja, 18 * p)
    if p > 0.3:
        a = ease((dt - 0.3) / 0.35); tl = Image.new("RGBA", (1200, 230), (0, 0, 0, 0)); dt_ = ImageDraw.Draw(tl)
        dt_.rounded_rectangle((0, 0, 1199, 229), radius=18, fill=(*SUP, 255), outline=(*LIN, 255), width=2)
        for k, (nom, col) in enumerate([("Vídeo", (110, 110, 118)), ("Subtítulos", NAR), ("Música", (90, 90, 98)), ("Efectos", (150, 90, 40))]):
            y = 22 + k * 50; dt_.text((20, y + 18), nom, font=fnt("Regular", 20), fill=GRIS, anchor="lm")
            r = np.random.RandomState(k + 7); x = 150
            while x < 1170:
                w = int(r.uniform(30, 120)); dt_.rounded_rectangle((x, y + 4, min(1170, x + w), y + 34), radius=6, fill=(*col, 255)); x += w + 5
        ph = 150 + 1020 * (dt / d); dt_.line((ph, 8, ph, 222), fill=(255, 255, 255), width=3)
        tl.putalpha(tl.getchannel("A").point(lambda v: int(v * a)))
        lien.alpha_composite(tl, (360, int(810 + 30 * (1 - a))))
        b = ease((dt - 0.6) / 0.3)
        if b > 0:
            ch = G.chip("Editado con IA", "check", True); lien.alpha_composite(ch, (W // 2 - ch.width // 2, int(30 + 20 * (1 - b))))
    return lien

def p_nombres(e, t, vid, n):
    dt = t - e["t0"]; lien = vid.convert("RGBA")
    gigante(lien, "TOMÁS", 160, 260, TINTA, dt / 0.35, x=520)
    gigante(lien, "PERSONA 2", 160, 260, NAR, (dt - 0.15) / 0.35, x=1400)
    m = mascara(vid, n); per = vid.convert("RGBA"); per.putalpha(m); lien.alpha_composite(per)
    return lien

PINTA = dict(recorte=p_recorte, editor=p_editor, factura=p_factura, recorte_cifras=p_recorte_cifras, calendario=p_calendario,
             lista=p_lista, chat=p_chat, tachado=p_tachado, meta=p_meta, nombres=p_nombres)

def compone(vid, t, n):
    e = escena_en(t)
    if e: fr = PINTA[e["tipo"]](e, t, vid, n)
    else: fr = vid.convert("RGBA")
    ent = [x["t0"] for x in ES]; sal = [x["t1"] for x in ES if not any(abs(x["t1"] - y) < 0.02 for y in ent)]
    c = min(ent, key=lambda c: abs(t - c))
    if 0 <= t - c < 0.22:   # flash de cámara
        k = (1 - (t - c) / 0.22) ** 2; fr = Image.blend(fr, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.85 * k)
    if sal:
        c = min(sal, key=lambda c: abs(t - c))
        if 0 <= t - c < 0.14:
            k = 1 - (t - c) / 0.14; s_ = 1 + 0.08 * k
            fr = fr.resize((int(W * s_), int(H * s_)), Image.BILINEAR).crop((int((W * s_ - W) / 2), int((H * s_ - H) / 2), int((W * s_ - W) / 2) + W, int((H * s_ - H) / 2) + H)).filter(ImageFilter.GaussianBlur(10 * k))
    if not (e and e["tipo"] in SIN_SUBS): S4.dibuja(fr, t, 985 if (e and e["tipo"] in ("editor", "lista", "meta")) else 800)
    return fr

def lee(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.4f}", "-i", "base.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return Image.frombytes("RGB", (W, H), raw)

if __name__ == "__main__":
    modo = sys.argv[1]
    if modo == "prev":
        for t in map(float, sys.argv[2:]):
            n = round(t * FPS); compone(lee(n / FPS), n / FPS, n).convert("RGB").save(f"p3_{t:06.2f}.jpg", quality=85)
    else:
        a, b = float(sys.argv[2]), float(sys.argv[3]); out = sys.argv[4] if len(sys.argv) > 4 else "muestra.mp4"
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", "base.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n = round(a * FPS)
        while True:
            raw = dec.stdout.read(W * H * 3)
            if len(raw) < W * H * 3: break
            enc.stdin.write(compone(Image.frombytes("RGB", (W, H), raw), n / FPS, n).convert("RGB").tobytes()); n += 1
            if n % 300 == 0: print(n, flush=True)
        enc.stdin.close(); enc.wait()
        json.dump([dict(t0=e["t0"], t1=e["t1"], tipo=e["tipo"]) for e in ES], open("escenas.json", "w"), indent=0)
