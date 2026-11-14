# Reel 6 «300 € al mes» completo (14-15/11/2026). Técnicas por ingeniería inversa de las referencias (ver ref/referencias-r6.md):
#  glitch de pantalla rota (300 €, 50 €), corte en el mismo sitio con marcador amarillo (empresa/autónomo/negocio), columnas de móviles
#  (ficha de Google), cartel con texto relleno de vídeo (GRATIS, SÍGUEME), transición desplazada tipo documental (PASO 2), rueda de
#  palabras desenfocada (herramientas), tarjetas en órbita (anuncios), emoji animado (ojo, saludo), barras de encuesta (300/50/250),
#  transición de cursor con marco pixelado, subtítulos de gris a blanco.
# uso: reel.py hoja t1 t2 … | reel.py render i0 i1
import cv2, numpy as np, json, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H, FPS = 1080, 1920, 60
FF = r"C:\Users\team\herr\ffmpeg\bin\ffmpeg.exe"
P = json.load(open("palabras.json", encoding="utf-8")); CUTS = [float(x) for x in json.load(open("cuts.json"))["cuts"]]
FIN_VOZ = CUTS[-1]; END = FIN_VOZ + .7
MARCA_USUARIO = "@tu_cuenta"   # se lee de mi-edicion/marca.json
YEL = (255, 220, 31); WHITE = (255, 255, 255); INK = (20, 20, 20)
FB, FH = r"C:\Users\team\mp14\brutos1311\r4\HN-CondBlack.ttf", r"C:\Users\team\mp14\brutos1311\r4\HelveticaNeue.ttc"
FM, FS, FE = r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\georgiai.ttf", r"C:\Windows\Fonts\seguiemj.ttf"
_f = {}
def fuente(p, s, i=0):
    k = (p, s, i)
    if k not in _f: _f[k] = ImageFont.truetype(p, s, index=i)
    return _f[k]
cl = lambda x: max(0., min(1., x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def ei(x): x = cl(x); return x ** 3
def suave(x): x = cl(x); return x * x * x * (x * (6 * x - 15) + 10)
def bk(x, c=1.6): x = cl(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def pega(L, im, x, y, a=1.):
    if a <= .01: return
    if a < 1: arr = np.array(im); arr[:, :, 3] = (arr[:, :, 3] * a).astype(np.uint8); im = Image.fromarray(arr)
    L.alpha_composite(im, (int(round(x)), int(round(y))))
# palabras del montaje
WS = []
for a, b, w in P:
    w = w.strip()
    if w.startswith("300"): w = "300 €"
    if w.startswith("50") and len(w) <= 3 + 1: w = "50 €"
    WS.append({"w": w, "s": float(a), "e": float(b)})
WS = [x for x in WS if x["w"].lower().strip(".,") != "euros"]
def T(pal, desde=0.):
    return next(x["s"] for x in WS if x["s"] >= desde - .01 and x["w"].lower().strip(".,¿?%") .startswith(pal.lower()))
# ================= vídeo y transiciones
cap = cv2.VideoCapture("base.mov"); BF = {"n": -1, "im": None}
def raw(t):
    n = int(round(min(max(t, 0), FIN_VOZ - 1 / 60) * 60))
    if n != BF["n"]:
        if n != BF["n"] + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ok, im = cap.read(); BF["n"] = n; BF["im"] = im if ok else BF["im"]
    return BF["im"].copy()
def plano(t):
    t = min(t, FIN_VOZ - .001); return max(j for j in range(len(CUTS) - 1) if CUTS[j] <= t)
ZOOMS = {}
def empuje(im, t):
    i = plano(t); d = CUTS[i + 1] - CUTS[i]; u = (min(t, FIN_VOZ) - CUTS[i]) / max(.5, d)
    s = 1.0 + .045 * suave(u) + (.05 if i % 2 else 0)
    M = np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H * .38 * (1 - s)]]); return cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT)
def cuadro(t): return empuje(raw(t), t)
T_CURSOR = [CUTS[3], CUTS[16]]          # «lo primero» y «si no, una agencia»
T_OFFSET = [CUTS[5]]                    # «lo segundo»
def antes_despues(T): return cuadro(T - 1 / 60), cuadro(T)
def tr_fundido(t, T, D1=.16, D2=.2):
    a, b = cuadro(min(t, T - 1 / 60)), cuadro(max(t, T)); m = suave((t - (T - D1)) / (D1 + D2))
    im = cv2.addWeighted(a, 1 - m, b, m, 0); k = math.sin(math.pi * m) * .6; acc = np.zeros(im.shape, np.float32)
    for j in range(5):
        s = 1 + .05 * k * j / 4; acc += cv2.warpAffine(im, np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H * .38 * (1 - s)]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    return (acc / 5).astype(np.uint8)
CUR_PRE, CUR_POST = .55, .35
def rect_cursor(t, T):
    """marco de selección: se arrastra antes del corte y crece a pantalla completa después."""
    x0, y0 = 250, 560; x1t, y1t = 860, 1330
    if t < T:
        u = eo((t - (T - CUR_PRE + .18)) / (CUR_PRE - .2)); return x0, y0, x0 + (x1t - x0) * u, y0 + (y1t - y0) * u, u
    u = suave((t - T) / CUR_POST); return x0 * (1 - u), y0 * (1 - u), x1t + (W - x1t) * u, y1t + (H - y1t) * u, 1 + u
def tr_cursor(t, T):
    a = cuadro(min(t, T - 1 / 60)); b = cuadro(max(t, T)); x0, y0, x1, y1, f = rect_cursor(t, T)
    im = a.copy()
    if x1 - x0 > 4 and y1 - y0 > 4:
        px = int(max(1, 34 * (1 - cl(f - 1)) ** 1.5)) if f > 1 else 34
        bb = cv2.resize(cv2.resize(b, (W // px, H // px), interpolation=cv2.INTER_AREA), (W, H), interpolation=cv2.INTER_NEAREST) if px > 1 else b
        X0, Y0, X1, Y1 = int(x0), int(y0), int(x1), int(y1); im[Y0:Y1, X0:X1] = bb[Y0:Y1, X0:X1]
    return im
def capa_cursor(t, L):
    for T in T_CURSOR:
        if not (T - CUR_PRE <= t < T + CUR_POST): continue
        x0, y0, x1, y1, f = rect_cursor(t, T); D = ImageDraw.Draw(L); al = int(255 * (1 - cl((t - T) / CUR_POST * 1.6)))
        if t >= T - CUR_PRE + .18 and al > 0:
            for (xa, ya, xb, yb) in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1)):   # línea discontinua
                n = int(math.hypot(xb - xa, yb - ya) // 22) + 1
                for k in range(n):
                    p0, p1 = k / n, min(1, (k + .55) / n); D.line((xa + (xb - xa) * p0, ya + (yb - ya) * p0, xa + (xb - xa) * p1, ya + (yb - ya) * p1), fill=(255, 255, 255, al), width=4)
            for hx, hy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)):
                D.rectangle((hx - 9, hy - 9, hx + 9, hy + 9), fill=(255, 255, 255, al), outline=(20, 20, 20, al), width=2)
            nombre = "PASO_01.mov" if T == T_CURSOR[0] else "AGENCIA.mov"
            D.text((x0 + 4, y0 - 44), nombre, font=fuente(FM, 30), fill=YEL + (al,))
        # puntero: entra desde abajo a la derecha, pulsa y arrastra
        u0 = eo((t - (T - CUR_PRE)) / .18)
        if t < T - CUR_PRE + .18: cx, cy = 980 + (250 - 980) * u0, 1700 + (560 - 1700) * u0
        else: cx, cy = x1, y1
        if al > 0:
            pts = [(0, 0), (0, 58), (15, 45), (26, 70), (37, 65), (26, 41), (46, 41)]
            sc = .9 if abs(t - (T - CUR_PRE + .18)) < .05 else 1.
            D.polygon([(cx + x * sc, cy + y * sc) for x, y in pts], fill=(255, 255, 255, al), outline=(10, 10, 10, al))
OFF_D = .5
def tr_offset(t, T):
    """todo el plano se desplaza en vertical en bucle con desenfoque de movimiento (sale A, entra B desde abajo)."""
    a, b = cuadro(min(t, T - 1 / 60)), cuadro(max(t, T)); p = suave((t - (T - OFF_D / 2)) / OFF_D)
    tira = np.vstack([a, b]); y = int(p * H); im = tira[y:y + H].copy()
    n = 1 + int(220 * math.sin(math.pi * p)); return cv2.blur(im, (1, n)) if n > 1 else im
def capa_offset(t, L):
    for T in T_OFFSET:
        u = (t - (T - OFF_D / 2)) / (OFF_D + 1.1)
        if not (0 <= u < 1): continue
        a = min(1, u * 6) * (1 - cl((u - .75) / .25))
        big = _txt("02", FB, 760, WHITE); pega(L, big, W / 2 - big.width / 2, 1500 - 2200 * u - big.height / 2, .16 * a)
        tt = _txt("LO SEGUNDO", FB, 150, WHITE); pega(L, tt, W / 2 - tt.width / 2, 1300 - 700 * eo(u * 1.6) + 420 * ei((u - .7) / .3), a)
def imagen(t):
    for T in T_CURSOR:
        if T - CUR_PRE <= t < T + CUR_POST: return tr_cursor(t, T)
    for T in T_OFFSET:
        if T - OFF_D / 2 <= t < T + OFF_D / 2: return tr_offset(t, T)
    for T in CUTS[1:-1]:
        if T in T_CURSOR or T in T_OFFSET: continue
        if T - .16 <= t < T + .2: return tr_fundido(t, T)
    return cuadro(t)
_tx = {}
def _txt(txt, p, size, col, idx=0, track=0):
    k = (txt, p, size, col, idx, track)
    if k not in _tx:
        f = fuente(p, size, idx); asc, desc = f.getmetrics(); w = int(f.getlength(txt) + track * len(txt)) + 20
        im = Image.new("RGBA", (w, asc + desc + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 10
        for ch in txt: d.text((x, 10), ch, font=f, fill=col + (255,)); x += f.getlength(ch) + track
        _tx[k] = im
    return _tx[k]
# ================= subtítulos «de gris a blanco»
CLAVE = {"300 €", "50 €", "250", "clientes", "gratis", "google", "facebook", "instagram", "profesional", "sígueme", "recuperar", "agencia"}
def grupos():
    BL = []; cur = []
    for i, x in enumerate(WS):
        cur.append(x); txt = " ".join(y["w"] for y in cur); fin = x["w"][-1:] in ".,?" if x["w"] else False
        nxt = WS[i + 1] if i + 1 < len(WS) else None
        corte = nxt is None or any(x["e"] - .1 <= c <= nxt["s"] + .1 for c in CUTS[1:-1]) or nxt["s"] - x["e"] > .25
        if len(cur) >= 3 or len(txt) > 15 or fin or corte: BL.append(cur); cur = []
    if cur: BL.append(cur)
    out = []
    for k, ws in enumerate(BL):
        out.append({"ws": ws, "s": ws[0]["s"] - .12})
    for k, b in enumerate(out): b["e"] = out[k + 1]["s"] if k + 1 < len(out) else FIN_VOZ + .4
    return out
BL = grupos()
_g = {}
def glifo(txt, size, col, blur):
    k = (txt, size, col, blur)
    if k not in _g:
        f = fuente(FH, size, 1); w = int(f.getlength(txt)) + 40; im = Image.new("RGBA", (w, size + 40), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((20, 14), txt, font=f, fill=col + (255,))
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        _g[k] = im
    return _g[k]
SUB_Y = 520
def capa_sub(t, L):
    b = next((b for b in BL if b["s"] <= t < b["e"]), None)
    if b is None: return
    S = 74; f = fuente(FH, S, 1); esp = f.getlength(" ") * .9
    pal = [x["w"].rstrip(".,") for x in b["ws"]]; anchos = [f.getlength(p) for p in pal]; tot = sum(anchos) + esp * (len(anchos) - 1); x = W / 2 - tot / 2
    ent = eo((t - b["s"]) / .2); sal = cl((t - (b["e"] - .08)) / .08)
    for x_w, p, wd in zip(b["ws"], pal, anchos):
        u = (t - (x_w["s"] - .03)) / .14; clave = p.lower() in CLAVE
        col = YEL if (clave and u >= 0) else WHITE
        if u < 0: im = glifo(p, S, WHITE, 3); a = .32 * ent; dy = (1 - ent) * 14
        else:
            q = eo(u); im = glifo(p, S, col, 0) if q > .6 else glifo(p, S, col, 2); a = .32 + .68 * q; dy = -4 * math.sin(math.pi * cl(u))
        pega(L, im, x - 20, SUB_Y - S / 2 - 14 + dy, a * (1 - sal)); x += wd + esp
# ================= glitch de pantalla rota
GL = [("300 €", T("300"), T("empresa") + .4), ("50 €", T("50", 10), T("negocio", 13.5) + .1)]
_big = {}
def texto_big(txt):
    if txt not in _big:
        f = fuente(FB, 330); w = int(f.getlength(txt)) + 80; im = Image.new("RGBA", (w, 400), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((40, 10), txt, font=f, fill=YEL + (255,)); a = np.array(im)
        a[1::5, :, 3] = (a[1::5, :, 3] * .45).astype(np.uint8)
        glow = np.array(im.filter(ImageFilter.GaussianBlur(26))); glow[:, :, 3] = (glow[:, :, 3] * .55).astype(np.uint8)
        _big[txt] = (Image.fromarray(a), Image.fromarray(glow))
    return _big[txt]
def rafaga(t, G0, G1): return max(1 - cl((t - G0) / .28), math.exp(-((t - (G0 + .95)) / .05) ** 2) * .8, cl((t - (G1 - .22)) / .22))
def capa_glitch(t, L):
    for txt, G0, G1 in GL:
        if not (G0 <= t < G1 + .02): continue
        tx, gl = texto_big(txt); g = rafaga(t, G0, G1); rng = np.random.default_rng(int(t * 60))
        x0, y0 = W / 2 - tx.width / 2, 1400 - tx.height / 2; a = np.array(tx)
        if g > .05:
            out = np.zeros_like(a); y = 0
            while y < a.shape[0]:
                h = int(rng.integers(6, 46)); dx = int(rng.normal(0, 70 * g)) if rng.random() < .55 + .4 * g else 0
                out[y:y + h] = np.roll(a[y:y + h], dx, axis=1); y += h
            a = out; sh = int(14 * g)
            for col, s_ in (((255, 40, 60), sh), ((40, 200, 255), -sh)):
                c = np.zeros_like(a); c[:, :, :3] = col; c[:, :, 3] = (np.roll(a[:, :, 3], s_, 1) * .5 * g).astype(np.uint8); pega(L, Image.fromarray(c), x0, y0)
        vis = (1 - cl((t - (G1 - .06)) / .06)) * (1 if rng.random() > g * .35 else .25)
        pega(L, gl, x0, y0, vis); pega(L, Image.fromarray(a), x0, y0, vis)
        fm = fuente(FM, 26); D = ImageDraw.Draw(L)
        et = (("[ PRESUPUESTO ]", "/MES · 01", "INVERSIÓN_MÍNIMA", "REC ●") if txt.startswith("300") else ("[ ANUNCIOS ]", "/MES · 02", "META_ADS", "REC ●"))
        for e_, xx, yy, d0 in zip(et, (110, 790, 110, 860), (1215, 1215, 1580, 1580), (.1, .2, .3, .35)):
            n = int(len(e_) * cl((t - G0 - d0) / .35)); al = int(220 * vis)
            if n: D.text((xx, yy), e_[:n] + ("_" if n < len(e_) and int(t * 8) % 2 else ""), font=fm, fill=YEL + (al,))
# ================= corte en el mismo sitio con marcador (empresa / autónomo / negocio)
MC = [("EMPRESA", T("empresa", 7)), ("AUTÓNOMO", T("autónomo")), ("NEGOCIO", T("negocio", 9))]
MC_FIN = CUTS[2] - .1
def soporte(k, w, h):
    rng = np.random.default_rng(k + 3)
    if k == 0:   # periódico
        im = Image.new("RGBA", (w, h), (238, 234, 224, 255)); D = ImageDraw.Draw(im)
        for y in range(30, h - 20, 22):
            if 90 < y < h - 90: continue
            x = 30
            while x < w - 40: l = int(rng.integers(40, 140)); D.rectangle((x, y, min(w - 30, x + l), y + 8), fill=(160, 156, 148, 255)); x += l + 14
        D.text((30, 4), "EDICIÓN DIGITAL · 2026", font=fuente(FM, 20), fill=(110, 110, 110, 255))
    elif k == 1:  # pantalla
        im = Image.new("RGBA", (w, h), (18, 18, 20, 255)); D = ImageDraw.Draw(im)
        for y in range(24, h, 26):
            if 90 < y < h - 90: continue
            D.text((24, y - 12), "> " + "".join(rng.choice(list("01abcdef_")) for _ in range(34)), font=fuente(FM, 18), fill=(90, 90, 90, 255))
    else:        # cartel
        im = Image.new("RGBA", (w, h), (250, 250, 250, 255)); D = ImageDraw.Draw(im)
        D.text((30, 14), "SI TIENES UN", font=fuente(FS, 34), fill=(30, 30, 30, 255)); D.text((w - 160, h - 44), "N.º 03", font=fuente(FM, 22), fill=(30, 30, 30, 255))
    return im
_sp = {}
def capa_match(t, L):
    if not (MC[0][1] - .25 <= t < MC_FIN + .25): return
    k = max(i for i in range(3) if MC[i][1] - .02 <= max(t, MC[0][1])) ; w, h = 860, 260
    if k not in _sp: _sp[k] = soporte(k, w, h)
    ent = eo((t - (MC[0][1] - .25)) / .25); sal = ei((t - MC_FIN) / .25)
    card = _sp[k].copy(); D = ImageDraw.Draw(card); f = fuente(FB, 150); word = MC[k][0]; tw = f.getlength(word)
    u = eo((t - MC[k][1]) / .18); mx = (w - tw) / 2
    D.rectangle((mx - 18, 70, mx - 18 + (tw + 36) * u, 70 + 130), fill=YEL + (255,))      # marcador
    D.text((mx, 52), word, font=f, fill=(INK if k != 1 else (255, 255, 255)) + (255,))
    if k == 1 and u > .3: D.text((mx, 52), word, font=f, fill=INK + (255,))
    jit = (np.random.default_rng(int(t * 60)).normal(0, 2.5, 2) if t - MC[k][1] < .08 else (0, 0))
    pega(L, card, (W - w) / 2 + jit[0], 1250 + (1 - ent) * 60 + sal * 80 + jit[1], ent * (1 - sal))
# ================= columnas de móviles (ficha de Google)
MV0, MV1 = T("ficha", 15) - .3, CUTS[4] - .05
_cap = {}
def captura(n, w, h):
    if n not in _cap:
        c = cv2.VideoCapture("base.mov"); c.set(cv2.CAP_PROP_POS_FRAMES, n); ok, im = c.read(); c.release()
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB); y0 = 500; crop = im[y0:y0 + int(W * h / w), :]; _cap[n] = Image.fromarray(cv2.resize(crop, (w, h), interpolation=cv2.INTER_AREA)).convert("RGBA")
    return _cap[n]
def pantalla(k, w=236, h=480):
    sc = Image.new("RGBA", (w, h), (255, 255, 255, 255)); D = ImageDraw.Draw(sc); fb, fr = fuente(FH, 22, 1), fuente(FH, 17, 0)
    tipo = k % 5
    if tipo == 0:      # mapa
        D.rectangle((0, 0, w, h), fill=(233, 236, 228, 255))
        for i in range(-3, 9): D.line((i * 50, 0, i * 50 + 160, h), fill=(255, 255, 255, 255), width=10)
        D.line((0, 210, w, 250), fill=(255, 214, 120, 255), width=14)
        D.ellipse((w / 2 - 26, 180, w / 2 + 26, 232), fill=(234, 67, 53, 255)); D.ellipse((w / 2 - 9, 197, w / 2 + 9, 215), fill=(255, 255, 255, 255))
        D.rounded_rectangle((14, h - 130, w - 14, h - 20), 16, fill=(255, 255, 255, 255)); D.text((28, h - 118), "Tu negocio", font=fb, fill=INK + (255,))
        D.text((28, h - 86), "★★★★★  4,9", font=fr, fill=(240, 160, 0, 255)); D.text((28, h - 60), "Abierto · Cierra a las 20:00", font=fr, fill=(30, 140, 60, 255))
    elif tipo == 1:    # reseñas
        D.text((18, 24), "Reseñas", font=fb, fill=INK + (255,)); D.text((18, 60), "4,9", font=fuente(FH, 64, 1), fill=INK + (255,))
        D.text((120, 84), "★★★★★", font=fr, fill=(240, 160, 0, 255))
        for i in range(4):
            y = 170 + i * 74; D.ellipse((18, y, 58, y + 40), fill=[(66, 133, 244), (52, 168, 83), (251, 188, 5), (234, 67, 53)][i] + (255,))
            D.text((70, y + 2), "★★★★★", font=fr, fill=(240, 160, 0, 255)); D.rectangle((70, y + 28, w - 24 - 30 * (i % 2), y + 34), fill=(205, 205, 205, 255))
    elif tipo == 2:    # fotos (de su propio vídeo)
        D.text((18, 20), "Fotos", font=fb, fill=INK + (255,)); ph = captura(int(60 * (2 + 7 * (k % 3))), w - 24, 200); sc.paste(ph, (12, 60))
        ph2 = captura(int(60 * (35 + 3 * (k % 4))), (w - 30) // 2, 150); sc.paste(ph2, (12, 272)); sc.paste(captura(int(60 * 52), (w - 30) // 2, 150), (18 + (w - 30) // 2, 272))
    elif tipo == 3:    # servicios
        D.text((18, 24), "Servicios", font=fb, fill=INK + (255,))
        for i in range(6):
            y = 80 + i * 62; D.rounded_rectangle((16, y, w - 16, y + 48), 12, fill=(244, 244, 244, 255)); D.rectangle((32, y + 20, 32 + 60 + 25 * (i % 3), y + 28), fill=(120, 120, 120, 255))
    else:              # ficha
        sc.paste(captura(int(60 * 18), w, 170), (0, 0)); D.text((18, 186), "Tu negocio", font=fuente(FH, 26, 1), fill=INK + (255,))
        D.text((18, 222), "★★★★★ 4,9 · 128 reseñas", font=fr, fill=(240, 160, 0, 255))
        for i, lab in enumerate(("Cómo llegar", "Llamar", "Web")):
            D.ellipse((20 + i * 72, 270, 66 + i * 72, 316), fill=(26, 115, 232, 255))
        for i in range(4): D.rectangle((18, 350 + i * 30, w - 30 - 20 * (i % 2), 358 + i * 30), fill=(210, 210, 210, 255))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=255)
    fon = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0)); ImageDraw.Draw(fon).rounded_rectangle((0, 0, w + 15, h + 15), 38, fill=(14, 14, 16, 255))
    fon.paste(sc, (8, 8), m); ImageDraw.Draw(fon).rounded_rectangle(((w + 16) / 2 - 36, 16, (w + 16) / 2 + 36, 34), 9, fill=(0, 0, 0, 255)); return fon
_mov = {}
def capa_moviles(t, L):
    if not (MV0 <= t < MV1 + .35): return
    ent = eo((t - MV0) / .45); sal = ei((t - MV1) / .35); u = t - MV0
    if not _mov: _mov.update({k: pantalla(k) for k in range(15)})
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); PH = 496 + 34
    for c in range(3):
        x = 165 + c * 262; d = -1 if c % 2 else 1; off = (u * 120 * d + c * 170) % (PH * 5)
        for r in range(-1, 5):
            k = (c * 5 + r) % 15; y = 1060 + r * PH - off + (1 - ent) * 500 * (1 if c != 1 else 1.3)
            if -PH < y < H: capa.alpha_composite(_mov[k], (int(x), int(y)))
    a = np.array(capa); yy = np.arange(H)[:, None]; m = np.clip((yy - 1120) / 160, 0, 1)
    a[:, :, 3] = (a[:, :, 3] * m * ent * (1 - sal)).astype(np.uint8); L.alpha_composite(Image.fromarray(a))
# ================= carteles con texto relleno de vídeo (GRATIS, SÍGUEME)
POS = [("GRATIS", "totalmente", T("totalmente") - .1, CUTS[5] - .5), ("SÍGUEME", "si quieres aprender más", T("sígueme") - .25, T("tienes", 58) + .15)]
def capa_poster(t, img_np):
    for txt, sub, P0, P1 in POS:
        if not (P0 <= t < P1 + .25): continue
        ent = eo((t - P0) / .3); sal = ei((t - P1) / .25); f = fuente(FB, 300 if len(txt) < 7 else 250)
        tw = f.getlength(txt); m = Image.new("L", (W, H), 0); D = ImageDraw.Draw(m); y = 1220 + (1 - ent) * 90
        x = 0
        for i, ch in enumerate(txt):         # letras que suben escalonadas
            k = eo((t - P0 - .04 * i) / .3); D.text((W / 2 - tw / 2 + f.getlength(txt[:i]), y + (1 - k) * 120), ch, font=f, fill=int(255 * k))
        mk = np.array(m).astype(np.float32) / 255 * (1 - sal)
        osc = (img_np.astype(np.float32) * (1 - .62 * ent * (1 - sal) * np.clip((np.arange(H)[:, None, None] - 1100) / 150, 0, 1)))
        brillo = np.clip(img_np.astype(np.float32) * .5 + np.array(YEL, np.float32) * .62, 0, 255)
        img_np = (osc * (1 - mk[:, :, None]) + brillo * mk[:, :, None]).astype(np.uint8)
    return img_np
def capa_poster_txt(t, L):
    for txt, sub, P0, P1 in POS:
        if not (P0 <= t < P1 + .25): continue
        ent = eo((t - P0 - .1) / .3); sal = ei((t - P1) / .25); im = _txt(sub, FS, 64, YEL)
        pega(L, im, W / 2 - im.width / 2 - 60 * (1 - ent), 1150, ent * (1 - sal))
        D = ImageDraw.Draw(L); al = int(200 * ent * (1 - sal))
        D.text((90, 1590), "POSTER · 0" + ("1" if txt == "GRATIS" else "2"), font=fuente(FM, 24), fill=(255, 255, 255, al)); D.text((830, 1590), MARCA_USUARIO, font=fuente(FM, 24), fill=(255, 255, 255, al))
# ================= rueda de palabras (herramientas)
LISTA = ["Página web", "SEO", "TikTok", "Email", "Google Ads", "Ficha de Google", "Influencers", "WhatsApp", "YouTube", "Newsletter", "Instagram", "Anuncios Meta"]
R0 = T("herramientas") - .25; R1 = T("cuento") + .9
RC, PAS = 1330, 112
_rw = {}
def fila(txt, centro, blur):
    k = (txt, centro, blur)
    if k not in _rw:
        f = fuente(FH, 94, 1); col = WHITE if centro else (200, 200, 200); w = int(f.getlength(txt)) + 60
        im = Image.new("RGBA", (w, 150), (0, 0, 0, 0)); ImageDraw.Draw(im).text((30, 22), txt, font=f, fill=col + (255,))
        if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
        _rw[k] = im
    return _rw[k]
def pos_rueda(t): u = cl((t - R0) / (R1 - .5 - R0)); return (len(LISTA) - 1) * (1 - (1 - u) ** 2.4)
def capa_rueda(t, L):
    if not (R0 <= t < R1 + .3): return
    p = pos_rueda(t); ent = eo((t - R0) / .3); sal = cl((t - R1) / .3)
    for i, txt in enumerate(LISTA):
        d = i - p
        if abs(d) > 3.4: continue
        th = d * .42; y = RC + math.sin(th) * PAS / .42; s = math.cos(th) ** 1.3; cen = abs(d) < .5
        im = fila(txt, cen, 0 if cen else int(min(8, 2 + abs(d) * 2.4)))
        if s < .98: im = im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS)
        a = (1 if cen else max(0, .55 - .14 * abs(d))) * ent * (1 - sal)
        pega(L, im, 210 + d * 18 - 30, y - im.height / 2 + (1 - ent) * 60, a)
    D = ImageDraw.Draw(L); al = int(255 * ent * (1 - sal)); ay = RC + 4
    D.line((96, ay, 168, ay), fill=YEL + (al,), width=10); D.polygon([(160, ay - 22), (192, ay), (160, ay + 22)], fill=YEL + (al,))
# ================= tarjetas en órbita (anuncios en Facebook e Instagram)
OR0, OR1 = T("campañas", 32) - .2, CUTS[11] - .1
def anuncio(k, w=270, h=360):
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255)); D = ImageDraw.Draw(im); fr = fuente(FH, 18, 0); fb = fuente(FH, 20, 1)
    D.ellipse((14, 14, 46, 46), fill=YEL + (255,)); D.text((54, 12), "Tu negocio", font=fb, fill=INK + (255,)); D.text((54, 34), "Publicidad", font=fr, fill=(120, 120, 120, 255))
    im.paste(captura(int(60 * [3, 12, 20, 28, 38, 45, 55, 61][k % 8]), w, 220), (0, 60))
    D.rectangle((0, 282, w, h), fill=(242, 242, 242, 255)); D.text((14, 296), ["Pide cita", "Más información", "Enviar mensaje", "Reservar"][k % 4], font=fb, fill=INK + (255,))
    D.text((14, 326), ["Instagram", "Facebook"][k % 2], font=fr, fill=(110, 110, 110, 255))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=255); out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(im, (0, 0), m); return out
_ad = {}
def capa_orbita(t, L):
    if not (OR0 <= t < OR1 + .35): return
    if not _ad: _ad.update({k: anuncio(k) for k in range(8)})
    ent = eo((t - OR0) / .5); sal = ei((t - OR1) / .35); giro = (t - OR0) * .32 + (1 - ent) * 1.2
    items = []
    for k in range(8):
        th = (k / 8 * 2 * math.pi + giro) % (2 * math.pi)
        if th > math.pi: th -= 2 * math.pi
        if abs(th) > 1.25: continue
        items.append((abs(th), k, th))
    for _, k, th in sorted(items, reverse=True):
        s = .55 + .45 * math.cos(th); x = W / 2 + math.sin(th) * 520; y = 1330 + (1 - math.cos(th)) * 260 + (1 - ent) * 400 + sal * 500
        im = _ad[k].resize((int(270 * s), int(360 * s)), Image.LANCZOS).rotate(-math.degrees(th) * 22, resample=Image.BICUBIC, expand=True)
        pega(L, im, x - im.width / 2, y - im.height / 2, min(1, (1.25 - abs(th)) * 4) * ent * (1 - sal))
# ================= emoji animado
EMO = [("👀", T("ojo") - .05, T("recomiendo") + .55, 820, 1330), ("👋", T("sígueme") - .05, T("tienes", 58) + .2, 830, 1080)]
_em = {}
def emoji(e, size=200):
    if e not in _em:
        im = Image.new("RGBA", (size + 60, size + 60), (0, 0, 0, 0)); ImageDraw.Draw(im).text((30, 20), e, font=fuente(FE, int(size * .78)), embedded_color=True); _em[e] = im
    return _em[e]
def capa_emoji(t, L):
    for e, E0, E1, x, y in EMO:
        if not (E0 <= t < E1 + .2): continue
        u = t - E0; s = bk(u / .35, 2.2) * (1 - ei((t - E1) / .2)); ang = 14 * math.sin(u * 14) * math.exp(-u * 1.2) if e == "👋" else 6 * math.sin(u * 9) * math.exp(-u * 2)
        if s <= .02: continue
        im = emoji(e); im = im.resize((max(2, int(im.width * s)), max(2, int(im.height * s))), Image.LANCZOS).rotate(ang, resample=Image.BICUBIC, expand=True)
        pega(L, im, x - im.width / 2, y - im.height / 2 - 20 * math.sin(min(u, .35) / .35 * math.pi))
# ================= barras de encuesta (300 / 50 / 250)
BA0, BA1 = T("gastar") - .5, CUTS[15] - .08
BARRAS = [("Presupuesto", "300 €", 1.0, WHITE, BA0 + .1), ("Anuncios", "50 €", 50 / 300, YEL, T("50", 46)), ("Te sobran", "250 €", 250 / 300, YEL, T("250", 48))]
def capa_barras(t, L):
    if not (BA0 <= t < BA1 + .35): return
    ent = eo((t - BA0) / .35); sal = ei((t - BA1) / .35); D = ImageDraw.Draw(L); X0, X1 = 120, 960
    for i, (lab, val, fr, col, t0) in enumerate(BARRAS):
        y = 1170 + i * 140 + (1 - ent) * 50 + sal * 60; a = ent * (1 - sal) * cl((t - t0 + .25) / .2)
        if a <= .01: continue
        al = int(255 * a); D.text((X0, y), lab, font=fuente(FS, 46), fill=(255, 255, 255, al))
        D.rectangle((X0, y + 66, X1, y + 66 + 34), fill=(255, 255, 255, int(40 * a)))
        g = eo((t - t0) / .55) * fr; D.rectangle((X0, y + 66, X0 + (X1 - X0) * g, y + 100), fill=col + (al,))
        for k in range(0, 11): D.line((X0 + (X1 - X0) * k / 10, y + 104, X0 + (X1 - X0) * k / 10, y + 112), fill=(255, 255, 255, int(120 * a)), width=2)
        D.ellipse((X0 - 34, y + 74, X0 - 16, y + 92), fill=col + (al,))
        n = int(round(float(val.split()[0]) * cl(g / max(fr, 1e-3)))); tv = f"{n} €"; fv = fuente(FB, 64); D.text((X1 - fv.getlength(tv), y - 4), tv, font=fv, fill=col + (al,))
# ================= composición
def degradado(t, img):
    on = 0.
    for a, b in ((GL[0][1], GL[0][2]), (GL[1][1], GL[1][2]), (MC[0][1] - .25, MC_FIN), (MV0, MV1), (R0, R1), (OR0, OR1), (BA0, BA1)):
        on = max(on, eo((t - a) / .3) * (1 - cl((t - b) / .3)))
    if on <= 0: return img
    yy = np.arange(H, dtype=np.float32)[:, None]; al = np.clip((yy - 1080) / 220, 0, 1) * 150 * on
    g = np.zeros((H, W, 4), np.uint8); g[:, :, 3] = np.repeat(al, W, 1).astype(np.uint8); img.alpha_composite(Image.fromarray(g)); return img
def frame(t):
    im = cv2.cvtColor(imagen(t), cv2.COLOR_BGR2RGB); im = capa_poster(t, im)
    img = Image.fromarray(im).convert("RGBA"); img = degradado(t, img); L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    capa_moviles(t, L); capa_orbita(t, L); capa_glitch(t, L); capa_match(t, L); capa_rueda(t, L); capa_barras(t, L)
    capa_poster_txt(t, L); capa_emoji(t, L); capa_offset(t, L); capa_cursor(t, L); capa_sub(t, L); img.alpha_composite(L)
    return np.array(img.convert("RGB"))
if __name__ == "__main__":
    if sys.argv[1] == "hoja":
        ims = []
        for t in map(float, sys.argv[2:]):
            f = cv2.resize(cv2.cvtColor(frame(t), cv2.COLOR_RGB2BGR), (270, 480)); cv2.putText(f, f"{t:.2f}", (6, 22), 0, .6, (0, 255, 255), 2); ims.append(f)
        ims += [np.zeros_like(ims[0])] * ((-len(ims)) % 8)
        cv2.imwrite("h_reel.jpg", np.vstack([np.hstack(ims[i:i + 8]) for i in range(0, len(ims), 8)])); sys.exit()
    if sys.argv[1] == "tiempos":
        print("GL", GL, "MC", MC, "MV", MV0, MV1, "POS", POS, "R", R0, R1, "OR", OR0, OR1, "EMO", [(e[1], e[2]) for e in EMO], "BA", BA0, BA1, "CUR", T_CURSOR, "OFF", T_OFFSET); sys.exit()
    i0, i1 = int(sys.argv[2]), int(sys.argv[3])
    pr = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", f"trozo_{i0:05d}.mp4"], stdin=subprocess.PIPE)
    for n in range(i0, i1): pr.stdin.write(frame(n / FPS).tobytes())
    pr.stdin.close(); pr.wait(); print("ok", i0, i1)
