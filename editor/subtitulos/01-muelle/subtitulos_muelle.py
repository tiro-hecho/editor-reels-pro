"""
Subtítulos · estilo 1 «muelle» (aprobado 26/10/2026).

Genera una secuencia de PNG transparentes (1080x1920) con los subtítulos animados,
lista para superponer al vídeo con ffmpeg:

    python3 subtitulos_muelle.py palabras.json salida/ [--top 1310] [--fps 30] [--dur 60.5] [--hasta 58.2]
    ffmpeg -i video.mp4 -framerate 30 -i salida/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass" ... final.mp4

palabras.json: lista de palabras YA en el tiempo del montaje final (no del bruto):
    [{"w": "Hola,", "s": 0.24, "e": 0.68}, {"w": "esto", "s": 0.84, "e": 1.0, "br": 1}, ...]
    "br": 1 en la última palabra de cada tramo de corte -> el bloque se cierra ahí y nunca
    junta palabras de dos tramos distintos.

Opciones:
    --top    altura (y) de la primera línea. 1310 por defecto; súbelo si abajo hay producto o manos.
    --hasta  segundo a partir del cual ya no hay subtítulos (p. ej. cuando entra el cierre).
    --muestra t1,t2,...  solo esos instantes, para revisar (salen como m_<t>.png).
"""
import argparse, json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))

# ---------- aspecto (no tocar sin aprobarlo) ----------
TAM = 64            # px
INTERLETRA = -1     # px entre letras (juntita)
INTERLINEA = 63     # px
ANCHO_CAJA = 600    # px, centrada (x 240-840)
ANCHO_BLOQUE = 560  # px, ancho máximo de un bloque antes de partirlo
MAX_PAL = 3         # palabras por bloque
PAUSA = 0.30        # s de silencio que cierra un bloque
SOMBRAS = [(0, 0, 2, (30, 24, 23, 175)), (0, 3, 12, (30, 24, 23, 135))]  # dx, dy, desenfoque, color: sombra suave para leer sobre fondos claros
DEBILES = set("la el de del los las un una y que para por en me lo le no mi o es este estos con muy más ha he tan".split())


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
def muelle(x):  # sube con un pequeño rebote
    x = cl(x); return 1 - math.exp(-6 * x) * math.cos(9 * x)

def ancho(txt):
    return sum(F.getlength(c) + INTERLETRA for c in txt) - INTERLETRA

def bloques(W):
    out, cur = [], []
    for w in W:
        if cur and (len(cur) >= MAX_PAL or ancho(" ".join(x["w"] for x in cur + [w])) > ANCHO_BLOQUE or w["s"] - cur[-1]["e"] > PAUSA):
            out.append(cur); cur = []
        cur.append(w)
        if w["w"][-1:] in ".,!?" or w.get("br"):
            out.append(cur); cur = []
    if cur: out.append(cur)
    # una palabra débil («de», «la»…) no se queda colgando al final: pasa al bloque siguiente
    for i in range(len(out) - 1):
        b = out[i]
        if len(b) > 1 and not b[-1].get("br") and b[-1]["w"].lower() in DEBILES:
            out[i + 1].insert(0, b.pop())
    B = [{"ws": b, "s": b[0]["s"] - 0.08, "e": b[-1]["e"]} for b in out]
    for i in range(len(B) - 1):
        B[i]["e"] = min(B[i + 1]["s"], B[i]["e"] + 0.25)
    return B

_cache = {}
def palabra_img(txt):
    """Palabra blanca con su sombra, en RGBA, con margen para desenfoque."""
    if txt in _cache: return _cache[txt]
    m = 40
    wd = int(ancho(txt)) + 2 * m; hg = TAM + 2 * m + 20
    def dibuja(color):
        im = Image.new("RGBA", (wd, hg), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = m
        for c in txt:
            d.text((x, m), c, font=F, fill=color); x += F.getlength(c) + INTERLETRA
        return im
    letras = dibuja((255, 255, 255, 255))
    base = Image.new("RGBA", (wd, hg), (0, 0, 0, 0))
    for dx, dy, r, col in SOMBRAS:
        s = dibuja(col).filter(ImageFilter.GaussianBlur(r / 2))
        base.alpha_composite(s, (dx, dy))
    base.alpha_composite(letras)
    _cache[txt] = (base, m)
    return _cache[txt]

def fotograma(B, t, top, hasta):
    L = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if hasta is not None and t >= hasta - 0.1: return L
    blk = next((b for b in B if b["s"] <= t < b["e"]), None)
    if not blk: return L
    out = cl((t - (blk["e"] - 0.12)) / 0.12)
    esp = F.getlength(" ")
    # reparto en líneas dentro de la caja de 600 px, centradas
    lineas, cur, wcur = [], [], 0
    for w in blk["ws"]:
        a = ancho(w["w"])
        if cur and wcur + esp + a > ANCHO_CAJA:
            lineas.append(cur); cur, wcur = [], 0
        wcur = wcur + (esp if cur else 0) + a; cur.append(w)
    lineas.append(cur)
    j = 0
    for li, ln in enumerate(lineas):
        total = sum(ancho(w["w"]) for w in ln) + esp * (len(ln) - 1)
        x = 540 - total / 2; y = top + li * INTERLINEA
        for w in ln:
            t0 = min(w["s"] - 0.06, blk["s"] + j * 0.07); j += 1
            k = muelle((t - t0) / 0.42)
            op = cl((t - t0) / 0.12) * (1 - out)
            bl = (1 - cl((t - t0) / 0.2)) * 10 + out * 8
            dy = (1 - k) * 34 - out * 18
            sc = 0.9 + 0.1 * k
            a = ancho(w["w"])
            if op > 0.003:
                im, m = palabra_img(w["w"])
                if sc != 1:
                    im = im.resize((max(1, round(im.width * sc)), max(1, round(im.height * sc))), Image.BICUBIC)
                if bl > 0.3: im = im.filter(ImageFilter.GaussianBlur(bl * 0.85))     # medido contra la version aprobada
                if op < 1:
                    al = im.getchannel("A").point(lambda v: int(v * op)); im.putalpha(al)
                cx = x + a / 2; cy = y + TAM * 0.55 + dy
                L.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))
            x += a + esp
    return L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("palabras"); ap.add_argument("salida")
    ap.add_argument("--top", type=int, default=1310); ap.add_argument("--fps", type=int, default=30)
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
