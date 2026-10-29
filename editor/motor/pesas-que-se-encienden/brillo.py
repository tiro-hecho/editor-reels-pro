# Vídeo aprobado: cada pesa rusa se ENCIENDE de su color (rojo / amarillo / verde) cuando el entrenador la toca:
# recorte BiRefNet (pesa_b*.png), la mano se respeta fotograma a fotograma (diferencia con el fondo de su tramo),
# el metal toma el color conservando reflejos, halo de luz alrededor y barrido de brillo al encenderse.
import json, subprocess, numpy as np, cv2
exec(open("formato_c1.py").read().split("# subtítulos repartidos")[0])       # BLOQ, CTA, GAN, t_fin, TR…
W, H, FPS = 1080, 1920, 30; Y0, Y1 = 1060, 1720
MS = {c: [cv2.imread(f"pesa_{c}_{k}.png", 0)[Y0:Y1].astype(np.float32) / 255 for k in range(3)] for c in ("4316", "4317")}   # un recorte por clip
A = MS["4316"]
COL = [np.array(c, np.float32) for c in ((48, 59, 255), (0, 200, 255), (93, 205, 33))]       # BGR
TOQ = np.array(json.load(open("toques.json")))
# --- momento en que la toca: subida de la presencia de la mano cerca del número que dice (si no, número + 0,2 s)
def toque(k, td, tn):
    a, b = int((td - 0.35) * FPS), int(tn * FPS)
    s = TOQ[max(a - 15, 0):b + 1, k]; base = np.median(TOQ[max(a - 15, 0):a + 1, k]) if a > 0 else s[0]
    for i in range(max(a, 0), b + 1):
        if TOQ[i, k] - base > 0.025: return i / FPS
    return td + 0.2
VENT = {0: [], 1: [], 2: []}          # solo una pesa encendida: la de la nota que acaba de decir
def tramos(notas, fin):
    for j, (k, t) in enumerate(notas):
        VENT[k].append((round(t - 0.04, 3), round(notas[j + 1][1] - 0.04 if j + 1 < len(notas) else fin, 3)))
tramos([(g["i"], g["t"] + 0.1) for g in GAN], BLOQ[0]["t0"])
for b in BLOQ: tramos([(c["i"], c["tn"]) for c in b["cols"]], b["t1"])
tramos([(c["i"], c["tn"]) for c in CTA["cols"]], t_fin)
json.dump(VENT, open("encendidos.json", "w"))
def estado(k, t):
    for a, b in VENT[k]:
        if a <= t < b: return min((t - a) / 0.12, (b - t) / 0.2, 1.0), t - a
    return 0.0, None
# --- fondo de cada tramo (para saber dónde está la mano)
def tramo_de(t): return next(i for i, tr in enumerate(TR) if t < tr["t1"] or i == len(TR) - 1)
FONDO = {}
def fondo(i):
    if i not in FONDO:
        tr = TR[i]; p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(tr["t0"]), "-t", str(tr["t1"] - tr["t0"]), "-i", "base_orig.mov", "-vf", "fps=4",
                                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
        fr = []
        while True:
            b = p.stdout.read(W * H * 3)
            if len(b) < W * H * 3: break
            fr.append(np.frombuffer(b, np.uint8).reshape(H, W, 3)[Y0:Y1])
        FONDO[i] = np.median(np.stack(fr), 0).astype(np.float32)
    return FONDO[i]
ys, xs = np.mgrid[0:Y1 - Y0, 0:W].astype(np.float32)
CAJA = []
for k in range(3):
    yy, xx = np.where(A[k] > 0.5); CAJA.append((xx.min(), xx.max(), yy.min(), yy.max()))
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "base_orig.mov", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "base_orig.mov",
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "copy", "base.mov"], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    im = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy(); t = n / FPS
    A = MS[TR[tramo_de(t)]["clip"]]
    est = [estado(k, t) for k in range(3)]
    if any(f > 0 for f, _ in est):
        reg = im[Y0:Y1].astype(np.float32); fnd = fondo(tramo_de(t))
        dif = np.abs(reg - fnd).max(-1)
        libre = 1 - np.clip((dif - 28) / 30, 0, 1)                         # 0 donde está la mano
        libre = cv2.GaussianBlur(cv2.erode(libre, np.ones((5, 5), np.uint8)), (0, 0), 2)
        l = reg.mean(-1, keepdims=True) / 255
        halo = np.zeros_like(reg); salida = reg.copy()
        for k in range(3):
            f, k_t = est[k]
            if f <= 0: continue
            a = (A[k] * libre)[..., None] * f
            c = COL[k]
            metal = c * (0.42 + 1.75 * l ** 0.8) + 255 * np.clip(l - 0.45, 0, 1) * 1.8   # color con reflejos blancos
            pulso = max(0.0, 1 - k_t / 0.45) if k_t is not None else 0.0
            x0, x1, y0, y1 = CAJA[k]
            if k_t is not None and k_t < 0.5:                                  # barrido de luz en diagonal al encenderse
                pos = x0 - 120 + (x1 - x0 + 240) * (k_t / 0.5)
                banda = np.exp(-(((xs - pos) + (ys - y0) * 0.5) / 38) ** 2)[..., None]
                metal = metal + 255 * 0.55 * banda
            salida = salida * (1 - a) + np.clip(metal * (1.12 + 0.45 * pulso), 0, 255) * a
            m = A[k] * f
            halo += cv2.GaussianBlur(m, (0, 0), 42)[..., None] * c * (1.0 + 0.7 * pulso) + cv2.GaussianBlur(m, (0, 0), 12)[..., None] * c * 0.6
        halo *= (1 - sum(A[k] for k in range(3)))[..., None].clip(0, 1) * libre[..., None]   # el halo no pisa la pesa ni la mano
        salida = 255 - (255 - salida) * (255 - np.clip(halo, 0, 255)) / 255                  # suma de luz (modo trama)
        im[Y0:Y1] = np.clip(salida, 0, 255).astype(np.uint8)
    enc.stdin.write(im.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("pesas encendidas", n, json.dumps(VENT))
