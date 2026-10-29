"""
Subtítulos · estilo 2 «pecho» (aprobado 26/10/2026).

Genera una secuencia de PNG transparentes (1080x1920) con los subtítulos animados,
lista para superponer al vídeo con ffmpeg:

    python3 subtitulos_pecho.py palabras.json salida/ [--top 1030] [--fps 30] [--dur 60.5] [--hasta 58.2]
    ffmpeg -i video.mp4 -framerate 30 -i salida/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass" ... final.mp4

palabras.json: lista de palabras YA en el tiempo del montaje final (no del bruto):
    [{"w": "Hola,", "s": 0.24, "e": 0.68}, {"w": "esto", "s": 0.84, "e": 1.0, "br": 1}, ...]
    "br": 1 en la última palabra de cada tramo de corte -> el bloque se cierra ahí.

Opciones:
    --top    altura (y) de la primera línea. 1030 por defecto (a la altura del pecho).
    --hasta  segundo a partir del cual ya no hay subtítulos (p. ej. cuando entra el cierre).
    --muestra t1,t2,...  solo esos instantes, para revisar (salen como m_<t>.png).
"""
import argparse, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))

# ---------- aspecto (no tocar sin aprobarlo) ----------
TAM = 100                    # px
INTERLETRA = -0.055 * TAM    # px entre letras (−0,055 em)
INTERLINEA = round(0.9 * TAM)  # 90 px: dos líneas muy juntas
X0, X1 = 150, 930            # caja de 780 px
ANCHO_CAJA = X1 - X0
MAX_PAL = 3
PAUSA = 0.30
ANTES = 0.04                 # la palabra entra 0,04 s antes de decirse
T_ENTRA = 0.24               # duración de la entrada (ease-out cúbico)
T_SALE = 0.14                # salida del bloque
FUERA = re.compile(r"[,.¿?¡!]")


def fuente():
    mac = "/System/Library/Fonts/HelveticaNeue.ttc"
    if os.path.exists(mac):
        return ImageFont.truetype(mac, TAM, index=1)          # Helvetica Neue Bold
    inter = os.path.join(KIT, "recursos/fuentes", "Inter[opsz,wght].ttf")   # Windows: Inter Bold
    f = ImageFont.truetype(inter, TAM)
    try: f.set_variation_by_axes([32, 700])
    except Exception: pass
    return f

F = fuente()

def cl(x, a=0.0, b=1.0): return min(b, max(a, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3      # ease-out cúbico
def limpia(w): return FUERA.sub("", w).lower()

def ancho(txt):
    return sum(F.getlength(c) + INTERLETRA for c in txt) - INTERLETRA

def bloques(W):
    out, cur = [], []
    for w in W:
        if cur and (len(cur) >= MAX_PAL or w["s"] - cur[-1]["e"] > PAUSA):
            out.append(cur); cur = []
        cur.append(w)
        if w["w"][-1:] in ".,!?;:" or w.get("br"):
            out.append(cur); cur = []
    if cur: out.append(cur)
    B = []
    for b in out:
        ws = [dict(x, t=limpia(x["w"])) for x in b]
        ws = [x for x in ws if x["t"]]
        if ws: B.append({"ws": ws, "s": ws[0]["s"] - ANTES, "e": ws[-1]["e"]})
    for i in range(len(B) - 1):
        B[i]["e"] = min(B[i + 1]["s"], B[i]["e"] + 0.25)
    return B

_cache = {}
def palabra_img(txt):
    """Palabra blanca en RGBA, con margen para el desenfoque. Sin sombra."""
    if txt in _cache: return _cache[txt]
    m = 30
    im = Image.new("RGBA", (int(ancho(txt)) + 2 * m, TAM + 2 * m + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = m
    for c in txt:
        d.text((x, m), c, font=F, fill=(255, 255, 255, 255)); x += F.getlength(c) + INTERLETRA
    _cache[txt] = (im, m)
    return _cache[txt]

def lineas_de(blk):
    esp = F.getlength(" ")
    lineas, cur, wcur = [], [], 0
    for w in blk["ws"]:
        a = ancho(w["t"])
        if cur and wcur + esp + a > ANCHO_CAJA:
            lineas.append(cur); cur, wcur = [], 0
        wcur = wcur + (esp if cur else 0) + a; cur.append(w)
    lineas.append(cur)
    return lineas, esp

def fotograma(B, t, top, hasta):
    L = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if hasta is not None and t >= hasta - 0.1: return L
    blk = next((b for b in B if b["s"] <= t < b["e"]), None)
    if not blk: return L
    out = cl((t - (blk["e"] - T_SALE)) / T_SALE)
    lineas, esp = lineas_de(blk)
    for li, ln in enumerate(lineas):
        total = sum(ancho(w["t"]) for w in ln) + esp * (len(ln) - 1)
        x = (X0 + X1) / 2 - total / 2; y = top + li * INTERLINEA
        for w in ln:
            a = ancho(w["t"])
            k = ease((t - (w["s"] - ANTES)) / T_ENTRA)
            if t >= w["s"] - ANTES:
                im, m = palabra_img(w["t"])
                sc = 0.92 + 0.08 * k
                if sc != 1:
                    im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.BICUBIC)
                bl = (1 - k) * 7 + out * 6
                if bl > 0.3: im = im.filter(ImageFilter.GaussianBlur(bl / 2))
                op = 1 - out
                if op < 1:
                    im.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
                dy = (1 - k) * 0.95 * INTERLINEA - out * 0.3 * INTERLINEA
                cx = x + a / 2; cy = y + TAM * 0.55 + dy
                px, py = int(round(cx - im.width / 2)), int(round(cy - im.height / 2))
                if k < 1 and out == 0:
                    # máscara: la palabra sube desde abajo DENTRO de su renglón
                    corte = int(round(y + INTERLINEA + 0.12 * TAM)) - py   # borde inferior del renglón
                    if corte <= 0: im = None
                    elif corte < im.height: im = im.crop((0, 0, im.width, corte))
                if im is not None:
                    L.alpha_composite(im, (px, py)) if px >= 0 and py >= 0 else L.paste(im, (px, py), im)
            x += a + esp
    return L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("palabras"); ap.add_argument("salida")
    ap.add_argument("--top", type=int, default=1030); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--dur", type=float); ap.add_argument("--hasta", type=float)
    ap.add_argument("--muestra")
    o = ap.parse_args()
    W = json.load(open(o.palabras))
    if isinstance(W, dict): W = W["words"]
    if o.top + INTERLINEA * 2 > 1440:
        print("aviso: con --top", o.top, "una segunda línea bajaría de y=1440 (zona segura)", file=sys.stderr)
    B = bloques(W)
    os.makedirs(o.salida, exist_ok=True)
    if o.muestra:
        for t in [float(x) for x in o.muestra.split(",")]:
            fotograma(B, t, o.top, o.hasta).save(os.path.join(o.salida, f"m_{t:.2f}.png"))
        return
    dur = o.dur or (W[-1]["e"] + 0.5)
    n = round(dur * o.fps)
    for i in range(n):
        fotograma(B, i / o.fps, o.top, o.hasta).save(os.path.join(o.salida, f"f{i:05d}.png"), compress_level=1)
        if i % 150 == 0: print(f"  {i}/{n}", end="\r", flush=True)
    print(f"  {n} fotogramas en {o.salida}")

if __name__ == "__main__":
    main()
