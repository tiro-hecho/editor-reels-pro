# Motor de referencia «tabla-barras-vuelan» · estilo pro: A-roll con punch-ins, pocos recursos reales, barridos y zoom con desenfoque,
# subtítulos «muelle» (aprobados) con claves en amarillo de marca y algunos bloques «repartidos» que nunca tocan la cara.
# uso: reel.py plan | reel.py hoja t1 t2 … | reel.py (render) | reel.py revisar
import cv2, numpy as np, json, subprocess, sys, os, importlib.util
from PIL import Image
W, H, FPS = 1080, 1920, 60
FF = "ffmpeg"; ST = "recursos-descargados/stock/"
P = json.load(open("palabras.json", encoding="utf-8"))
CORTES = [0, 2.13, 4.05, 5.38, 6.71, 9.53, 11.02, 13.38, 14.85, 16.80, 19.92]
FIN_VOZ = 22.36; END = 22.9
YEL = (255, 220, 31)
BR = []
ZK = [(0, 1.12, 0), (0.54, 1.3, .14), (2.13, 1.12, 0), (4.05, 1.12, 0), (4.66, 1.25, .14), (6.71, 1.18, 0), (8.96, 1.32, .14), (9.53, 1.12, 0),
      (10.48, 1.3, .14), (11.02, 1.12, 0), (11.92, 1.25, .14), (13.38, 1.12, 0), (14.14, 1.2, .3), (14.85, 1.18, 0), (15.34, 1.32, .14),
      (16.80, 1.12, 0), (17.78, 1.12, .4), (19.92, 1.12, 0), (21.84, 1.25, .14)]
TR = [(2.13, "lado", 1), (4.05, "lado", -1), (5.38, "vert", 1), (6.71, "vert", -1), (9.53, "zoom", 1), (11.02, "giro", 1),
      (13.38, "lado", -1), (14.85, "zoom", 1), (16.80, "giro", -1), (19.92, "zoom", 1)]
TW = [(T, d) for T, _, d in TR]
CLAVE_T = [0.54, 3.08, 4.66, 6.34, 8.96, 10.48, 11.92, 14.14, 14.54, 15.34, 21.84]
REP_CAND = []
TOP_M, TOP_R = 1290, 960
BLANCO0 = 99.0; TINTA = (20, 20, 20)     # tramo final recortado sobre blanco puro

def carga(n):
    sp = importlib.util.spec_from_file_location(n, f"subs/{n}.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
MU, RE = carga("subtitulos_muelle"), carga("subtitulos_repartidos")
# ---------- vídeo
cap = cv2.VideoCapture("base.mov"); BF = {"n": -1, "im": None}
def base(t):
    n = int(round(min(t, FIN_VOZ - 1 / 60) * 60))
    if n != BF["n"]:
        if n != BF["n"] + 1: cap.set(1, n)
        ok, fr = cap.read(); BF["n"] = n
        if ok: BF["im"] = fr
    return BF["im"]
MK = {}
def mascara(t):
    n = int(min(t, FIN_VOZ - .04) * 30)
    if n not in MK:
        m = cv2.imread(f"mask/{n:05d}.png", 0); MK.clear(); MK[n] = None if m is None else cv2.resize(m, (W, H))
    return MK[n]
def cabeza(t):
    m = mascara(t)
    if m is None: return None
    ys = np.where(m.max(1) > 128)[0]; top = ys[0]; xs = np.where(m[top:top + 200].max(0) > 128)[0]
    anc = np.where(m[min(H - 1, top + 150)] > 128)[0]; hw = (anc.max() - anc.min()) if len(anc) else 300
    x0, x1 = (anc.min(), anc.max()) if len(anc) else (xs.min(), xs.max())
    return float(xs.mean()), top, x0, x1, top + 1.35 * hw     # centro x, coronilla, lados, barbilla
def cara(t):
    c = cabeza(t); return (540, 800) if c is None else (c[0], c[1] + 260.)
CEN = {c: cara(c + .3) for c in CORTES}
# barbilla más baja de cada plano (para que el zoom nunca la lleve a los subtítulos)
BAR = {}
for i, c in enumerate(CORTES):
    c1 = CORTES[i + 1] if i + 1 < len(CORTES) else FIN_VOZ
    v = [cabeza(c + k * (c1 - c) / 16) for k in range(16)]; BAR[c] = max(x[4] for x in v if x)
SC = {}
def stock(nombre, t):
    if nombre not in SC:
        c = cv2.VideoCapture(ST + nombre + ".mp4"); SC[nombre] = (c, c.get(cv2.CAP_PROP_FPS), {"n": -1, "im": None})
    c, f, B = SC[nombre]; n = int(t * f)
    if n != B["n"]:
        if n != B["n"] + 1: c.set(1, n)
        ok, fr = c.read(); B["n"] = n
        if ok: B["im"] = cv2.resize(fr, (W, H))
    return B["im"]
eo = lambda x: 1 - (1 - min(1, max(0, x))) ** 3
def escala(t):
    s = ZK[0][1]
    for t0, s1, d in ZK:
        if t < t0: break
        s0 = s; s = s1 if d == 0 else s0 + (s1 - s0) * eo((t - t0) / d)
    return s
def matriz(s, cx, cy):
    tx = min(0, max(W - s * W, W / 2 - s * cx)) if s > 1 else 0; ty = min(0, max(H - s * H, cy - s * cy)) if s > 1 else 0
    return np.float32([[s, 0, tx], [0, s, ty]])
LIM = 1000   # la barbilla nunca baja de aquí (los subtítulos empiezan en 1290)
def mat_a(t):
    # en los zooms el encuadre sube la cara lo justo para que la barbilla quede por encima de los subtítulos
    c0 = max(c for c in CORTES if c <= t); cx, cy = CEN[c0]; s = escala(t); M = matriz(s, cx, cy)
    if s > 1: M[1, 2] = min(0, max(H - s * H, min(M[1, 2], LIM - s * BAR[c0])))
    return M
quien = lambda t: next((b for b in BR if b[0] <= t < b[1]), None)
CHIPD = "assets/chip/"
def fondo_chip(t):
    im = cv2.warpAffine(base(t), mat_a(t), (W, H), borderMode=cv2.BORDER_REFLECT)
    im = cv2.GaussianBlur(cv2.resize(im, (W // 4, H // 4)), (0, 0), 6); im = cv2.resize(im, (W, H))
    return (im.astype(np.float32) * .32).astype(np.uint8)
def chip(t, br):
    a, b = br[0], br[1]; bgim = fondo_chip(t).astype(np.float32)
    p = cv2.imread(f"{CHIPD}f_{int(round(t * 60)):05d}.png", cv2.IMREAD_UNCHANGED)
    if p is None: return bgim.astype(np.uint8)
    al = p[:, :, 3:4].astype(np.float32) / 255; rgb = p[:, :, :3].astype(np.float32)
    # brillo: lo amarillo emite un halo suave
    am = ((rgb[:, :, 2] > 150) & (rgb[:, :, 1] > 140) & (rgb[:, :, 0] < 120)).astype(np.float32) * al[:, :, 0]
    halo = cv2.GaussianBlur(am, (0, 0), 18)[:, :, None] * np.array([31, 220, 255], np.float32) * .55
    out = bgim * (1 - al) + rgb * al + halo
    return np.clip(out, 0, 255).astype(np.uint8)
def raw(t, br):
    if br and br[2] == "CHIP": return chip(t, br)
    if br:
        a, b, nom, src = br; k = max(0, t - a) / .2; s = (1.0 + .06 * max(0, t - a) / (b - a)) * (1 + .10 * (1 - eo(k)))
        return cv2.warpAffine(stock(nom, max(0, src + (t - a))), matriz(s, W / 2, H / 2), (W, H), borderMode=cv2.BORDER_REFLECT)
    if t >= BLANCO0: return blanco(t)
    return cv2.warpAffine(base(t), mat_a(t), (W, H), borderMode=cv2.BORDER_REFLECT)
def blanco(t):
    n = int(round(min(t, FIN_VOZ - 1 / 60) * 60)); p = cv2.imread(f"mate/f_{n:05d}.png", cv2.IMREAD_UNCHANGED)
    a = p[:, :, 3:4].astype(np.float32) / 255; im = (p[:, :, :3].astype(np.float32) * a + 255 * (1 - a)).astype(np.uint8)
    return cv2.warpAffine(im, mat_a(t), (W, H), borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
D1, D2 = .2, .22
def suave(x): x = min(1., max(0., x)); return x * x * x * (x * (6 * x - 15) + 10)
def fuerza(t, T, d1=.1, d2=.13):
    if T - d1 <= t < T: return ((t - (T - d1)) / d1) ** 2
    if T <= t < T + d2: return (1 - (t - T) / d2) ** 2
    return 0
def zoomblur(im, k):
    acc = np.zeros(im.shape, np.float32)
    for j in range(7):
        s = 1 + .2 * k + .018 * j * k
        acc += cv2.warpAffine(im, np.float32([[s, 0, W / 2 * (1 - s)], [0, s, H / 2 * (1 - s)]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    return (acc / 7).astype(np.uint8)
def radial(im, k, giro=0.):
    acc = np.zeros(im.shape, np.float32); n = 7
    for j in range(n):
        s_ = 1 + .22 * k + .02 * j * k; ang = giro * k * (1 + .15 * j)
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, s_); acc += cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    return (acc / n).astype(np.uint8)
def imagen(t):
    for T, tipo, d in TR:
        if not (T - D1 <= t < T + D2): continue
        A = lambda: raw(min(t, T - 1 / 60), quien(T - .001)); B = lambda: raw(max(t, T), quien(T + .001))
        if tipo in ("lado", "vert"):
            p = suave((t - (T - D1)) / (D1 + D2)); a_, b_ = A(), B(); im = np.zeros_like(a_)
            if tipo == "lado":
                sh = int(p * W)
                if d > 0: im[:, :W - sh] = a_[:, sh:]; im[:, W - sh:] = b_[:, :sh]
                else: im[:, sh:] = a_[:, :W - sh]; im[:, :sh] = b_[:, W - sh:]
                n = 1 + int(60 * np.sin(np.pi * p)); return cv2.blur(im, (n, 1)) if n > 1 else im
            sh = int(p * H)
            if d > 0: im[:H - sh] = a_[sh:]; im[H - sh:] = b_[:sh]
            else: im[sh:] = a_[:H - sh]; im[:sh] = b_[H - sh:]
            n = 1 + int(80 * np.sin(np.pi * p)); return cv2.blur(im, (1, n)) if n > 1 else im
        k = .6 * fuerza(t, T, D1, D2); a_, b_ = A(), B(); mz = suave((t - (T - D1 * .6)) / (D1 * .6 + D2 * .6))
        im = cv2.addWeighted(a_, 1 - mz, b_, mz, 0)
        return radial(im, k, 0. if tipo == "zoom" else 5. * d * (1 if t < T else -1))
    return raw(t, quien(t))
# ---------- cara: caja de la cabeza en coordenadas de salida (None si en pantalla no está él)
def caja_cara(t):
    if quien(t) or any(T - D1 <= t < T + D2 for T, *_ in TR): return None
    c = cabeza(t)
    if c is None: return None
    _, top, x0, x1, y1 = c; M = mat_a(t); s = M[0, 0]
    return (s * x0 + M[0, 2] - 30, s * (top - 20) + M[1, 2], s * x1 + M[0, 2] + 30, s * y1 + M[1, 2] + 10)
# ---------- subtítulos
PW = []
for a, b, w in P:
    PW.append({"w": w.strip(), "s": a, "e": b})
    if any(abs(a - k) < .02 for k in CLAVE_T): PW[-1]["c"] = YEL
    if a >= BLANCO0 - .05: PW[-1]["c"] = TINTA
for c in CORTES[1:] + [FIN_VOZ]:
    k = max(i for i, x in enumerate(PW) if x["e"] <= c + .05); PW[k]["br"] = 1
BM = MU.bloques(PW)
def a_rep(b, lado):
    ws = [dict(x, t=RE.limpia(x["w"])) for x in b["ws"]]; ws = [x for x in ws if x["t"]]
    return {"ws": ws, "s": ws[0]["s"], "e": b["e"], "lado": lado}
def capa_sub(t, modos):
    for i, b in enumerate(BM):
        if b["s"] <= t < b["e"]:
            if modos[i] == "rep": return RE.fotograma([a_rep(b, i % 2)], t, TOP_R, None)
            return MU.fotograma([b], t, 330 if b["s"] < T_OUT else TOP_M, None)
    return None
def toca(capa, caja):
    if capa is None or caja is None: return 0
    a = np.array(capa)[:, :, 3]; x0, y0, x1, y1 = [int(v) for v in caja]
    return int((a[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] > 20).sum())
def plan():
    modos = ["mu"] * len(BM)
    for tc in REP_CAND:
        i = next(i for i, b in enumerate(BM) if any(abs(x["s"] - tc) < .02 for x in b["ws"]))
        prueba = list(modos); prueba[i] = "rep"
        malos = [round(n / 60, 2) for n in range(int(BM[i]["s"] * 60), int(BM[i]["e"] * 60)) if toca(capa_sub(n / 60, prueba), caja_cara(n / 60))]
        if malos: print("repartidos fuera (tocaría la cara):", " ".join(x["w"] for x in BM[i]["ws"]), malos[:3])
        else: modos[i] = "rep"; print("repartidos:", " ".join(x["w"] for x in BM[i]["ws"]))
    json.dump({"modos": modos, "bloques": [round(b["ws"][0]["s"], 3) for b in BM],
               "claves": [x["s"] for b in BM for x in b["ws"] if x.get("c")],
               "rep_pal": [x["s"] for i, b in enumerate(BM) if modos[i] == "rep" for x in b["ws"]]}, open("plan_subs.json", "w"))
    return modos
# ---- formato «si quieres…»: señala a la izquierda, sale un cubo verde/rojo, se aparta y deja el consejo debajo
from PIL import ImageDraw, ImageFont
FB = "editor/assets/fuentes/HN-CondBlack.ttf"   # cámbiala por la tuya; FH = "editor/assets/fuentes/HelveticaNeue.ttc"   # cámbiala por la tuya
cl = lambda x: max(0., min(1., x))
def bk(x, c=1.7): x = cl(x); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
_cache = {}
def _fuente(p, n, i=0):
    k = (p, n, i)
    if k not in _cache: _cache[k] = ImageFont.truetype(p, n, index=i)
    return _cache[k]
VERDE, ROJO = (34, 197, 94), (239, 68, 68)
FILAS = [("Visualizaciones", "Resuelve dudas", 0.54, 2.02, VERDE),
         ("Seguidores", "Habla a cámara", 4.66, 5.32, VERDE),
         ("Clientes", "Enseña trabajos", 10.48, 11.02, VERDE),
         ("Vender más", "Olvida seguidores", 15.34, 16.78, ROJO)]
T_IN, T_OUT = 0.0, 19.80
# rejilla: número + dos columnas iguales
GX0, GX1, CALLE, NUM = 96, 996 - 78, 24, 0
CW = (GX1 - GX0 - NUM - CALLE) // 2; CX = [(GX0 + NUM, GX0 + NUM + CW), (GX0 + NUM + CW + CALLE, GX1)]
Y0 = 1056; HH = 84; RH = 64; GAP = 10
_tx = {}
def _txt(txt, p, size, col, idx=0, track=0):
    if p == FB: idx = 0
    k = (txt, p, size, col, idx, track)
    if k not in _tx:
        f = _fuente(p, size, idx); asc, desc = f.getmetrics(); wt = int(f.getlength(txt) + track * len(txt)) + 6
        im = Image.new("RGBA", (wt, asc + desc + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 2
        for ch in txt: d.text((x, 2), ch, font=f, fill=col + (255,)); x += f.getlength(ch) + track
        _tx[k] = im
    return _tx[k]
TC = None
_bar = {}
def _barra(w, h, col):
    k = (w, h, col)
    if k not in _bar:
        m = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 14, fill=col + (255,)); _bar[k] = np.array(m)
    return _bar[k]
def ei(x): x = cl(x); return x ** 3
def sacudida(t):
    b = FILAS[-1][3]; u = t - b - .1
    if 0 <= u < .22: k = (1 - u / .22) ** 2 * 6; return k * np.sin(u * 90), k * np.cos(u * 70)
    return 0., 0.
ANT, VUELO = .09, .30        # anticipación y salida de la barra
def capa_tarjeta(t):
    global TC
    if not (T_IN <= t < T_OUT + .7): return None
    if TC is None:
        s_ = 46
        while s_ > 24 and max(_fuente(FH, s_, 1).getlength(x) for f in FILAS for x in f[:2]) > CW - 40: s_ -= 1
        TC = s_
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); D = ImageDraw.Draw(L)
    def pega(im, x, y, a=1.):
        if a <= 0: return
        if a < 1: arr = np.array(im); arr[:, :, 3] = (arr[:, :, 3] * a).astype(np.uint8); im = Image.fromarray(arr)
        L.alpha_composite(im, (int(x), int(y)))
    so = lambda i: ei((t - T_OUT - .05 * i) / .4)        # salida escalonada de la tabla
    # cabeceras: versalitas espaciadas
    for j, (txt, col) in enumerate((("SI QUIERES", (255, 255, 255)), ("HAZ ESTO", ROJO))):
        k = eo((t - T_IN - .08 * j) / .45); o = so(0)
        for c_, ch in enumerate(txt):
            kc = bk((t - T_IN - .08 * j - .035 * c_) / .38, 1.3); g = _txt(ch, FB, 56, col, 0)
            xx = CX[j][0] + 18 + sum(_fuente(FB, 56, 0).getlength(q) + 3 for q in txt[:c_])
            if kc > 0 and ch != ' ': pega(g, xx, Y0 - 4 + (1 - kc) * 30 + o * 40, min(1, kc * 1.5) * (1 - o))
    for i, fila in enumerate(FILAS):
        o = so(i + 1); y = Y0 + HH + i * (RH + GAP) + o * 80
        if o >= 1: continue
        # número de fila
        kn = eo((t - T_IN - .1 - .06 * i) / .4); n_ = _txt(f"{i + 1:02d}", FH, 30, (255, 255, 255), 10, 1)
        if False: pega(n_, GX0, y + (RH - n_.height) / 2 + (1 - kn) * 12, .7 * kn * (1 - o))
        for j in (0, 1):
            x0, x1 = CX[j]; w = x1 - x0; Tr = fila[2 + j]; col = ROJO if j == 1 else VERDE
            ua = (t - Tr) / ANT; uv = (t - Tr - ANT) / VUELO
            px = ei(uv) * (w + 80) if t >= Tr + ANT else 0.
            # texto: letras que suben una a una cuando pasa el borde de la barra
            f = _fuente(FH, TC, 1); txt = fila[j]; tx = x0 + 20; asc, desc = f.getmetrics(); cb = f.getbbox('H'); ty = y + RH / 2 - (cb[1] + cb[3]) / 2 - 2
            if t >= Tr + ANT:
                TRK = -0.6
                for c_, ch in enumerate(txt):
                    xx = tx + f.getlength(txt[:c_]) + TRK * c_
                    tc = Tr + ANT + VUELO * (cl((xx - x0 + 20) / (w + 80)) ** (1 / 3)) + .01 * c_
                    kk = bk((t - tc) / .22, 1.4)
                    if t >= tc and ch != " ":
                        g = _txt(ch, FH, TC, (255, 255, 255), 1)
                        pega(g, xx - 2, ty - 2 + (1 - kk) * 22, min(1, (t - tc) / .1) * (1 - o))
                # subrayado del color de su barra que se queda
                lw = int((w - 44) * eo((t - Tr - ANT - .12) / .4))
                if False: D.rounded_rectangle((x0 + 22, y + RH - 8, x0 + 22 + lw, y + RH - 5), 2, fill=col + (int(230 * (1 - o)),))
            # barra: crece desde la izquierda, se encoge un poco antes de salir y vuela a la derecha con estela
            e = bk((t - T_IN - .12 - .06 * i - .04 * j) / .42, 1.2)
            if e <= 0.01 or px >= w + 80: continue
            sq = 1 - .04 * np.sin(np.pi * cl(ua)) if t >= Tr and t < Tr + ANT else 1.
            bw = max(3, int(w * min(1.06, e))); bh = max(3, int(RH * sq))
            B = cv2.resize(_barra(w, RH, col), (bw, bh), interpolation=cv2.INTER_AREA)
            dx = -10 * np.sin(np.pi * cl(ua)) if t < Tr + ANT else 0
            if t >= Tr + ANT:
                v = int((ei(uv) - ei(uv - 1 / 60 / VUELO)) * (w + 80) * 1.4)
                if v > 2: B = cv2.blur(B, (v | 1, 1))
            xc0 = int(x0 + px + dx); keep = max(0, min(bw, W - xc0))
            if keep > 2: pega(Image.fromarray(np.ascontiguousarray(B[:, :keep])), xc0, y + (RH - bh) / 2, 1 - o)
    return L
def frame(t, modos):
    im0 = imagen(t); sx, sy = sacudida(t)
    if sx or sy: im0 = cv2.warpAffine(im0, np.float32([[1.02, 0, sx - W * .01], [0, 1.02, sy - H * .01]]), (W, H), borderMode=cv2.BORDER_REFLECT)
    img = Image.fromarray(cv2.cvtColor(im0, cv2.COLOR_BGR2RGB)).convert("RGBA")
    ct = capa_tarjeta(t)
    if ct is not None:
        yy = np.arange(H, dtype=np.float32)[:, None]; al = np.clip((yy - 1060) / 200, 0, 1) * np.clip((1560 - yy) / 120, 0, 1) * 110 * eo((t - T_IN) / .4) * (1 - cl((t - T_OUT) / .35))
        g = np.zeros((H, W, 4), np.uint8); g[:, :, 3] = np.repeat(al, W, 1).astype(np.uint8); img.alpha_composite(Image.fromarray(g)); img.alpha_composite(ct)
    cs = capa_sub(t, modos)
    if cs is not None: img.alpha_composite(cs)
    return np.array(img.convert("RGB"))
if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "render"
    if arg == "plan": plan(); sys.exit()
    modos = json.load(open("plan_subs.json"))["modos"]
    if arg == "hoja":
        TS = [float(x) for x in sys.argv[2:]]; ims = []
        for t in TS:
            f = cv2.cvtColor(frame(t, modos), cv2.COLOR_RGB2BGR); cj = caja_cara(t)
            if cj: cv2.rectangle(f, (int(cj[0]), int(cj[1])), (int(cj[2]), int(cj[3])), (0, 0, 255), 3)
            f = cv2.resize(f, (270, 480)); cv2.putText(f, f"{t:.2f}", (6, 22), 0, .6, (0, 255, 255), 2); ims.append(f)
        ims += [np.zeros_like(ims[0])] * ((-len(ims)) % 8)
        cv2.imwrite("h_reel.jpg", np.vstack([np.hstack(ims[i:i + 8]) for i in range(0, len(ims), 8)])); sys.exit()
    if arg == "revisar":   # fotograma a fotograma: subtítulo contra cara y contra la zona segura
        malos, fuera = [], []
        for n in range(int(END * FPS)):
            t = n / FPS; cs = capa_sub(t, modos)
            if cs is None and capa_tarjeta(t) is None: continue
            if cs is not None and toca(cs, caja_cara(t)): malos.append(round(t, 3))
            ct = capa_tarjeta(t)
            if ct is not None and toca(ct, caja_cara(t)): malos.append(("tarjeta", round(t, 3)))
            if cs is None: continue
            a = np.array(cs)[:, :, 3] > 20; ys, xs = np.where(a)
            if len(xs) and (xs.min() < 66 or xs.max() > 934 or ys.min() < 220 or ys.max() > 1440): fuera.append(round(t, 3))
        print("fotogramas con subtítulo sobre la cara:", len(malos), malos[:20]); print("fuera de zona segura:", len(fuera), fuera[:20]); sys.exit()
    i0, i1 = int(sys.argv[2]), int(sys.argv[3])     # trozo de fotogramas
    pr = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", f"trozo_{i0:05d}.mp4"], stdin=subprocess.PIPE)
    for n in range(i0, i1): pr.stdin.write(frame(n / FPS, modos).tobytes())
    pr.stdin.close(); pr.wait(); print("ok", i0, i1)
