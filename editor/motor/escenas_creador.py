# Motor del estilo «escenas-creador» (VSL Tiro Hecho, 20/10/2026).
# Subtítulos Helvetica Neue Bold en minúscula, letras muy juntas (tracking −6,5 %), interlineado −1 px,
# sin fondos ni sombras y con color que se adapta píxel a píxel al fondo (oscuro sobre claro, blanco sobre oscuro).
# Animaciones sutiles que se alternan: fundido, máscara, escala suave y, de vez en cuando, letra a letra.
# Texto gigante DETRÁS de la persona (recorte con u2net_human_seg) y flash de cámara al entrar.
#
# Uso:
#   python3 escenas_creador.py base.mp4 palabras.json salida.mp4 \
#       --detras "1.9,3.0,¿ENTRENADOR PERSONAL?,neutro" --detras "16.7,25.5,30–40 €,#E07B2A"
# palabras.json = [[inicio, fin, "palabra"], ...] con los tiempos del vídeo ya montado (Whisper por palabras).
# El modelo: ~/.u2net/u2net_human_seg.onnx (se descarga solo con `pip install rembg` y
#   `rembg i -m u2net_human_seg cualquier.jpg salida.png`, o a mano desde las releases de github.com/danielgatis/rembg).
# En Windows no hay Helvetica: pon FUENTE = Inter Bold (5-fuentes) y TRK = -0.05.
import sys, json, re, os, subprocess, argparse, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FUENTE, IDX = "/System/Library/Fonts/HelveticaNeue.ttc", 1          # Helvetica Neue Bold
FUENTE_GIGANTE, IDX_G = "/System/Library/Fonts/HelveticaNeue.ttc", 9  # Condensed Black
TRK = -0.065; NEUTRO = (46, 44, 42, 205)

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_io(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x ** 3
def alfa(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im

class Subtitulos:
    ORDEN = ["fundido", "mascara", "suave", "fundido", "letras", "mascara", "suave", "fundido", "mascara", "letras"]
    def __init__(self, palabras, W, H, tam=None):
        self.W, self.H = W, H; self.T = tam or int(W * 0.034 if W > H else W * 0.062)
        self.F = ImageFont.truetype(FUENTE, self.T, index=IDX); self.trk = TRK * self.T; self.esp = int(self.T * 0.2)
        self.inter = self.T - 1; self.cache = {}
        bl, cur = [], []
        for w in palabras:
            if cur and (len(cur) >= 4 or w[0] - cur[-1][1] > 0.35 or re.search(r"[.,?!…]$", cur[-1][2])): bl.append(cur); cur = []
            cur.append(w)
        if cur: bl.append(cur)
        self.B = []
        for i, b in enumerate(bl):
            t1 = b[-1][1] + 0.3
            if i + 1 < len(bl): t1 = min(t1, bl[i + 1][0][0] - 0.04)
            self.B.append(dict(t0=b[0][0] - 0.06, t1=t1, estilo=self.ORDEN[i % len(self.ORDEN)],
                               w=[(x[0] - 0.06, re.sub(r"[.,…¿?¡!]+", "", x[2]).lower()) for x in b]))
    def largo(self, w): return self.F.getlength(w) + self.trk * max(0, len(w) - 1)
    def img(self, txt):
        if txt not in self.cache:
            F = self.F; im = Image.new("RGBA", (int(self.largo(txt)) + 20, int(self.T * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 5
            for k, ch in enumerate(txt):
                d.text((x, int(self.T * 0.68)), ch, font=F, fill=(255, 255, 255), anchor="lm")
                x += F.getlength(ch) + self.trk + (F.getlength(txt[k:k + 2]) - F.getlength(txt[k]) - F.getlength(txt[k + 1]) if k + 1 < len(txt) else 0)
            self.cache[txt] = im
        return self.cache[txt]
    def pega(self, fr, im, x, y):
        """Color adaptativo: oscuro donde debajo hay claro, blanco donde hay oscuro."""
        x, y = int(x), int(y); x0, y0, x1, y1 = max(0, x), max(0, y), min(self.W, x + im.width), min(self.H, y + im.height)
        if x1 <= x0 or y1 <= y0: return
        sub = im.crop((x0 - x, y0 - y, x1 - x, y1 - y))
        L = np.asarray(fr.crop((x0, y0, x1, y1)).convert("L").filter(ImageFilter.GaussianBlur(3)), np.float32)
        k = np.clip((L - 120) / 70, 0, 1)[..., None]
        rgb = (1 - k) * np.array([255, 255, 255], np.float32) + k * np.array([11, 11, 12], np.float32)
        fr.alpha_composite(Image.fromarray(np.dstack([rgb, np.asarray(sub.getchannel("A"))[..., None]]).astype(np.uint8), "RGBA"), (x0, y0))
    def lineas(self, ws):
        an = [self.largo(w) for _, w in ws]
        if len(ws) >= 3 and sum(an) > self.W * 0.4:
            k = min(range(1, len(ws)), key=lambda k: abs(sum(an[:k]) - sum(an[k:]))); return [ws[:k], ws[k:]]
        return [ws]
    def dibuja(self, fr, t, y_base=None):
        y_base = y_base or int(self.H * (0.74 if self.W > self.H else 0.68))
        b = next((b for b in self.B if b["t0"] <= t < b["t1"]), None)
        if not b: return
        sal = 1 - ease((t - (b["t1"] - 0.12)) / 0.12); ls = self.lineas(b["w"]); est = b["estilo"]
        y0 = y_base - (len(ls) * self.inter) // 2
        if est == "suave": p0 = ease((t - b["t0"]) / 0.32); s = 0.96 + 0.04 * p0
        for li, ln in enumerate(ls):
            an = [self.largo(w) for _, w in ln]; x = (self.W - sum(an) - self.esp * (len(ln) - 1)) / 2
            cy = y0 + li * self.inter + self.inter // 2
            if est in ("mascara", "suave"):
                im = self.img(" ".join(w for _, w in ln))
                if est == "mascara":
                    p = ease_io((t - ln[0][0]) / 0.36); dy = int(im.height * (1 - p))
                    if p > 0 and im.height - dy > 0: self.pega(fr, alfa(im.crop((0, 0, im.width, im.height - dy)), sal), x - 5, cy - im.height / 2 + dy)
                elif p0 > 0:
                    im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
                    self.pega(fr, alfa(im2, p0 * sal), x - 5 + (im.width - im2.width) / 2, cy - im2.height / 2)
                continue
            for (w0, w), aw in zip(ln, an):
                if est == "letras":
                    cx = x
                    for k, ch in enumerate(w):
                        p = ease((t - w0 - k * 0.022) / 0.26)
                        if p > 0: im = self.img(ch); self.pega(fr, alfa(im, p * sal), cx - 5, cy - im.height / 2 + 22 * (1 - p))
                        cx += self.F.getlength(w[:k + 1]) - self.F.getlength(w[:k]) + self.trk
                else:
                    p = ease((t - w0) / 0.24)
                    if p > 0:
                        im = self.img(w)
                        if p < 1: im = im.filter(ImageFilter.GaussianBlur(3 * (1 - p)))
                        self.pega(fr, alfa(im, p * sal), x - 5, cy - im.height / 2 + 10 * (1 - p))
                x += aw + self.esp

class Recorte:
    def __init__(self, modelo=os.path.expanduser("~/.u2net/u2net_human_seg.onnx")):
        import onnxruntime as ort
        self.s = ort.InferenceSession(modelo, providers=["CoreMLExecutionProvider", "CPUExecutionProvider"])
    def mascara(self, fr):
        x = np.asarray(fr.convert("RGB").resize((320, 320), Image.BILINEAR), np.float32) / 255
        x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
        o = self.s.run(None, {self.s.get_inputs()[0].name: x})[0][0, 0]; o = (o - o.min()) / (o.max() - o.min() + 1e-6)
        return Image.fromarray((np.clip((o - 0.15) / 0.7, 0, 1) * 255).astype(np.uint8)).resize(fr.size, Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5))

def texto_detras(fr, rec, txt, p, color, W, H):
    """Palabra gigante entre el fondo real y la persona, arriba como portada de revista."""
    size = int(H * 0.19); f = ImageFont.truetype(FUENTE_GIGANTE, size, index=IDX_G); w0 = f.getbbox(txt)[2]
    if w0 > W * 0.95: f = ImageFont.truetype(FUENTE_GIGANTE, int(size * W * 0.95 / w0), index=IDX_G)
    e = ease(p); im = Image.new("RGBA", (f.getbbox(txt)[2] + 80, int(f.size * 1.4)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((40, f.size * 0.7), txt, font=f, fill=color, anchor="lm")
    s = 0.9 + 0.1 * e; im = alfa(im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC), e)
    capa = fr.copy(); capa.alpha_composite(im, (int(W / 2 - im.width / 2), int(H * 0.16 - im.height / 2 + 60 * (1 - e))))
    per = fr.copy(); per.putalpha(rec.mascara(fr)); capa.alpha_composite(per); return capa

def flash(fr, dt):
    if 0 <= dt < 0.22: return Image.blend(fr, Image.new("RGBA", fr.size, (255, 255, 255, 255)), 0.85 * (1 - dt / 0.22) ** 2)
    return fr

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("palabras"); ap.add_argument("salida")
    ap.add_argument("--detras", action="append", default=[], help="inicio,fin,TEXTO,color (neutro o #RRGGBB)")
    a = ap.parse_args()
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", a.video], capture_output=True, text=True).stdout)["streams"][0]
    W, H = info["width"], info["height"]; n_, d_ = info["r_frame_rate"].split("/"); FPS = float(n_) / float(d_)
    sub = Subtitulos(json.load(open(a.palabras)), W, H)
    det = []
    for s in a.detras:
        t0, t1, txt, col = s.split(",", 3)
        det.append((float(t0), float(t1), txt, NEUTRO if col == "neutro" else tuple(int(col[i:i + 2], 16) for i in (1, 3, 5)) + (255,)))
    rec = Recorte() if det else None
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.video, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    tmp = a.salida + ".sinaudio.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    n = 0
    while True:
        raw = dec.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        t = n / FPS; fr = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
        d = next((x for x in det if x[0] <= t < x[1]), None)
        if d: fr = flash(texto_detras(fr, rec, d[2], (t - d[0]) / 0.35, d[3], W, H), t - d[0])
        sub.dibuja(fr, t); enc.stdin.write(fr.convert("RGB").tobytes()); n += 1
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-i", a.video, "-map", "0:v", "-map", "1:a?", "-c", "copy", a.salida]); os.remove(tmp)
    print("hecho:", a.salida)
