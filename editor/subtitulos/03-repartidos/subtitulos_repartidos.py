"""
Subtítulos · estilo 3 «repartidos» (aprobado 26/10/2026).

Genera una secuencia de PNG transparentes (1080x1920) con los subtítulos animados,
lista para superponer al vídeo con ffmpeg:

    python3 subtitulos_repartidos.py palabras.json salida/ [--top 960] [--fps 30] [--dur 60.5] [--hasta 58.2]
    ffmpeg -i video.mp4 -framerate 30 -i salida/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass" ... final.mp4

palabras.json: lista de palabras YA en el tiempo del montaje final (no del bruto):
    [{"w": "Hola,", "s": 0.24, "e": 0.68}, {"w": "esto", "s": 0.84, "e": 1.0, "br": 1}, ...]
    "br": 1 en la última palabra de cada tramo de corte -> el bloque se cierra ahí.

Opciones:
    --top    altura (y) del primer renglón. 960 por defecto, para no tapar la cara.
    --hasta  segundo a partir del cual ya no hay subtítulos (p. ej. cuando entra el cierre).
    --muestra t1,t2,...  solo esos instantes, para revisar (salen como m_<t>.png).
"""
import argparse, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))

# ---------- aspecto (no tocar sin aprobarlo) ----------
TAM = 104          # px
PASO = 112         # px entre renglones: la palabra j va en top + j·112
X_IZQ = 70         # palabras pegadas a la izquierda empiezan aquí
X_DER = 1010       # palabras pegadas a la derecha acaban aquí
MAX_PAL = 4
PAUSA = 0.35
T_ENTRA = 0.22     # ease-out cúbico
SUBE = 24          # px
T_SALE = 0.12      # fundido de salida
FUERA = re.compile(r"[,.¿?¡!;:]")


def fuente():
    """1) recursos/fuentes/HelveticaNeueCondensedBold.ttf · 2) Helvetica Neue Condensed Bold del Mac · 3) Inter 700."""
    propia = os.path.join(KIT, "recursos/fuentes", "HelveticaNeueCondensedBold.ttf")
    if os.path.exists(propia):
        return ImageFont.truetype(propia, TAM)
    mac = "/System/Library/Fonts/HelveticaNeue.ttc"
    if os.path.exists(mac):
        return ImageFont.truetype(mac, TAM, index=4)          # Helvetica Neue Condensed Bold
    inter = os.path.join(KIT, "recursos/fuentes", "Inter[opsz,wght].ttf")   # Windows: Inter 700 (no es condensada)
    f = ImageFont.truetype(inter, TAM)
    try: f.set_variation_by_axes([32, 700])
    except Exception: pass
    return f

F = fuente()

def cl(x, a=0.0, b=1.0): return min(b, max(a, x))
def ease(x): x = cl(x); return 1 - (1 - x) ** 3
def limpia(w): return FUERA.sub("", w)

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
        if ws: B.append({"ws": ws, "s": ws[0]["s"], "e": ws[-1]["e"], "lado": len(B) % 2})
    for i in range(len(B) - 1):
        B[i]["e"] = min(B[i + 1]["s"], B[i]["e"] + 0.25)
    return B

_cache = {}
def palabra_img(txt):
    """Palabra blanca en RGBA, con margen para el desenfoque. Sin sombra."""
    if txt in _cache: return _cache[txt]
    m = 30
    a = F.getlength(txt)
    im = Image.new("RGBA", (int(a) + 2 * m + 2, TAM + 2 * m + 30), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((m, m), txt, font=F, fill=(255, 255, 255, 255))
    _cache[txt] = (im, m, a)
    return _cache[txt]

def fotograma(B, t, top, hasta):
    L = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if hasta is not None and t >= hasta - 0.1: return L
    blk = next((b for b in B if b["s"] <= t < b["e"]), None)
    if not blk: return L
    op_sal = 1 - cl((t - (blk["e"] - T_SALE)) / T_SALE)
    for j, w in enumerate(blk["ws"]):
        if t < w["s"]: continue
        k = ease((t - w["s"]) / T_ENTRA)
        im, m, a = palabra_img(w["t"])
        bl = (1 - k) * 8
        if bl > 0.3: im = im.filter(ImageFilter.GaussianBlur(bl / 2))
        op = k * op_sal
        if op < 1:
            im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * op)))
        izq = (j + blk["lado"]) % 2 == 0
        x = X_IZQ if izq else X_DER - a
        y = top + j * PASO + (1 - k) * SUBE
        L.alpha_composite(im, (int(round(x - m)), int(round(y - m))))
    return L

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("palabras"); ap.add_argument("salida")
    ap.add_argument("--top", type=int, default=960); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--dur", type=float); ap.add_argument("--hasta", type=float)
    ap.add_argument("--muestra")
    o = ap.parse_args()
    W = json.load(open(o.palabras))
    if isinstance(W, dict): W = W["words"]
    if o.top + PASO * MAX_PAL > 1440:
        print("aviso: con --top", o.top, "el cuarto renglón bajaría de y=1440 (zona segura)", file=sys.stderr)
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
