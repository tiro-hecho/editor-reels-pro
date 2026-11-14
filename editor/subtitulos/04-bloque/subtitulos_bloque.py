"""
Subtítulos · estilo 4 «bloque» (aprobado 14/11/2026).

La frase se convierte en un BLOQUE: la palabra clave ENORME y las palabras pequeñas colgadas en sus esquinas
(las de antes de la clave arriba a la izquierda, las de después abajo a la derecha). Cada palabra aparece justo al decirse.
Todo blanco, sin sombra ni caja: colócalo sobre una zona oscura del plano (ropa, fondo oscuro).

Genera una secuencia de PNG transparentes lista para superponer con ffmpeg:

    python3 subtitulos_bloque.py palabras.json salida/ [--ancho 1080 --alto 1920] [--cx 540 --cy 1250] [--fps 30] [--dur 60.5] [--hasta 58.2]
    ffmpeg -i video.mp4 -framerate 30 -i salida/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass" ... final.mp4

palabras.json: palabras YA en el tiempo del montaje final:
    [{"w": "empiezas", "s": 0.0, "e": 0.5}, {"w": "la", "s": 0.52, "e": 0.6}, {"w": "dieta", "s": 0.66, "e": 0.9, "k": 1}, ...]
    "k": 1  -> esa palabra es la CLAVE (va enorme). El bloque se cierra en la clave.
    "br": 1 -> cierra el bloque aunque no haya clave (fin de un tramo de corte).
    Si un bloque no tiene clave, la palabra más larga hace de clave.

Opciones:
    --ancho/--alto  tamaño del vídeo (1080x1920 vertical por defecto; 1920x1080 para horizontal).
    --cx/--cy       centro horizontal del bloque y línea base de la clave (por defecto, a la altura del pecho).
    --muestra t1,t2,...  solo esos instantes, para revisar (salen como m_<t>.png).
"""
import argparse, json, os, re
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))          # carpeta del editor
FUENTES = os.path.join(REPO, "editor", "assets", "fuentes")

# ---------- aspecto (no tocar sin aprobarlo) ----------
CLAVE_REL = 0.155   # tamaño máximo de la clave respecto al lado corto del vídeo (168 px en 1080)
PEQ_REL = 0.27      # palabras pequeñas: 27 % del tamaño de la clave
ANCHO_MAX = 0.72    # la clave como mucho ocupa el 72 % del lado corto
TRACK = -0.045      # letras muy juntas
MAX_PAL = 7
PAUSA = 0.35
T_PEQ, T_CLAVE = 0.16, 0.20
FUERA = re.compile(r"[,.¿?¡!;:…\"]")


def _ease(u):
    u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3


def fuentes(tam_clave, tam_peq):
    """Clave en negrita y pequeñas en medium. 1) editor/assets/fuentes/HelveticaNeue.ttc si la pones · 2) Helvetica Neue del Mac · 3) Inter de editor/assets/fuentes (Windows)."""
    for hn in (os.path.join(FUENTES, "HelveticaNeue.ttc"), "/System/Library/Fonts/HelveticaNeue.ttc", os.environ.get("FUENTE_HN", "")):
        if hn and os.path.exists(hn):
            return ImageFont.truetype(hn, tam_clave, index=1), ImageFont.truetype(hn, tam_peq, index=10)
    inter = os.path.join(FUENTES, "Inter[opsz,wght].ttf")
    fk, fp = ImageFont.truetype(inter, tam_clave), ImageFont.truetype(inter, tam_peq)
    for f, peso in ((fk, 700), (fp, 500)):
        try: f.set_variation_by_axes([32, peso])
        except Exception: pass
    return fk, fp


def ancho(s, f, tr):
    return sum(f.getlength(c) for c in s) + tr * f.size * (len(s) - 1)


def capa_texto(s, f, tr):
    asc, desc = f.getmetrics(); im = Image.new("RGBA", (int(ancho(s, f, tr)) + 30, asc + desc + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im); x = 15
    for c in s:
        d.text((x, 10 + asc), c, font=f, fill=(255, 255, 255, 255), anchor="ls"); x += f.getlength(c) + tr * f.size
    return im, 10 + asc


def pega(img, lay, x0, y0, a=1.0, s=1.0):
    if s != 1: lay = lay.resize((max(1, int(lay.width * s)), max(1, int(lay.height * s))), Image.BICUBIC)
    if a < 1:
        al = lay.getchannel("A").point(lambda v: int(v * a)); lay = lay.copy(); lay.putalpha(al)
    img.alpha_composite(lay, (int(x0), int(y0)))


def bloques(pal):
    bl, cur = [], []
    for i, p in enumerate(pal):
        if cur and (len(cur) >= MAX_PAL or (p["s"] - pal[i - 1]["e"] > PAUSA and len(cur) >= 2)):
            bl.append(cur); cur = []
        cur.append(i)
        if p.get("k") or p.get("br"):
            bl.append(cur); cur = []
    if cur: bl.append(cur)
    out = []                                   # un bloque sin clave y corto se une al siguiente (nada de «pero» suelto)
    for b in bl:
        if out and not any(pal[i].get("k") for i in out[-1]) and not pal[out[-1][-1]].get("br") and len(out[-1]) + len(b) <= MAX_PAL:
            out[-1] += b
        else:
            out.append(b)
    return out


def dibuja(t, pal, bls, W, H, cx, cy):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); lado = min(W, H)
    for bi, b in enumerate(bls):
        a0 = pal[b[0]]["s"] - .05; b1 = pal[bls[bi + 1][0]]["s"] - .05 if bi + 1 < len(bls) else pal[b[-1]]["e"] + .6
        if not a0 <= t < b1: continue
        ks = [i for i in b if pal[i].get("k")]; k = ks[-1] if ks else max(b, key=lambda i: len(pal[i]["w"]))
        tam = int(lado * CLAVE_REL)
        while True:
            fk, fp = fuentes(tam, max(14, int(tam * PEQ_REL))); kw = ancho(pal[k]["w"], fk, TRACK)
            if kw <= lado * ANCHO_MAX or tam < 60: break
            tam -= 6
        x0 = cx - kw / 2
        for grupo, arriba in (([i for i in b if i < k], True), ([i for i in b if i > k], False)):
            if not grupo: continue
            frase = " ".join(pal[i]["w"] for i in grupo)
            xx = x0 if arriba else x0 + kw - ancho(frase, fp, -.02)
            yy = cy - tam * .74 - fp.size * .15 if arriba else cy + fp.size * 1.05
            for i in grupo:
                lay, base = capa_texto(pal[i]["w"], fp, -.02); u = t - pal[i]["s"] + .04
                if u > 0:
                    q = _ease(u / T_PEQ); pega(img, lay, xx - 15, yy - base + (1 - q) * 8, q, .94 + .06 * q)
                xx += fp.getlength(pal[i]["w"] + " ") - .02 * fp.size * len(pal[i]["w"])
        u = t - pal[k]["s"] + .04
        if u > 0:
            q = _ease(u / T_CLAVE); lay, base = capa_texto(pal[k]["w"], fk, TRACK); s = 1.1 - .1 * q
            pega(img, lay, cx - lay.width * s / 2, cy - base * s + (1 - q) * 10, q, s)
        break
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("palabras"); ap.add_argument("salida")
    ap.add_argument("--ancho", type=int, default=1080); ap.add_argument("--alto", type=int, default=1920)
    ap.add_argument("--cx", type=float); ap.add_argument("--cy", type=float)
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--dur", type=float); ap.add_argument("--hasta", type=float, default=1e9)
    ap.add_argument("--muestra")
    a = ap.parse_args()
    pal = json.load(open(a.palabras, encoding="utf-8"))
    for p in pal: p["w"] = FUERA.sub("", p["w"]).strip().lower()
    pal = [p for p in pal if p["w"]]
    W, H = a.ancho, a.alto; cx = a.cx if a.cx is not None else W / 2; cy = a.cy if a.cy is not None else (H * .65 if H > W else H * .78)
    bls = bloques(pal); os.makedirs(a.salida, exist_ok=True)
    if a.muestra:
        for t in map(float, a.muestra.split(",")): dibuja(t, pal, bls, W, H, cx, cy).save(os.path.join(a.salida, f"m_{t:05.2f}.png"))
        return
    dur = a.dur or pal[-1]["e"] + .6
    for n in range(int(dur * a.fps)):
        t = n / a.fps; im = dibuja(t, pal, bls, W, H, cx, cy) if t < a.hasta else Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im.save(os.path.join(a.salida, f"f{n:05d}.png"))
    print("subtítulos en bloque:", int(dur * a.fps), "fotogramas,", len(bls), "bloques")


if __name__ == "__main__":
    main()
