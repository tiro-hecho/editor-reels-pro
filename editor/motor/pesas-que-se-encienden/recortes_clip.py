# Vídeo aprobado: recorte de las 3 pesas POR CLIP (entre 4316 y 4317 la imagen se mueve 7 px): BiRefNet por pesa sobre el
# fotograma mediano de cada clip (sin manos), la verde delante, el hueco de su asa deja ver la azul, y borde afinado.
#   uso: python recortes_clip.py <clip>      -> pesa_<clip>_0/1/2.png (rosa/azul/verde) a tamaño 1080x1920
import sys, subprocess, numpy as np, cv2
clip = sys.argv[1]; W, H = 1080, 1920; Y0, X0 = 1080, 230
med = cv2.imread(f"med_{clip}.png")
CAJAS = {"rosa": (30, 50, 280, 380), "azul": (230, 70, 560, 400), "verde": (190, 140, 480, 510)}
for k, (x0, y0, x1, y1) in ([] if __import__("os").path.exists(f"bir_{clip}_verde.png") else CAJAS.items()):   # cada pesa en su propio proceso (BiRefNet gasta mucha memoria)
    subprocess.run([sys.executable, "-c", f"""
import numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
med = cv2.imread('med_{clip}.png'); c = med[{y0}:{y1}, {x0}:{x1}]
c2 = cv2.resize(c, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)          # al doble: más detalle en el borde
mk = np.asarray(remove(Image.fromarray(cv2.cvtColor(c2, cv2.COLOR_BGR2RGB)), session=new_session('birefnet-general'), only_mask=True))
mk = cv2.resize(mk, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_AREA)
full = np.zeros(med.shape[:2], np.uint8); full[{y0}:{y1}, {x0}:{x1}] = mk; cv2.imwrite('bir_{clip}_{k}.png', full)
"""], check=True)
hsv = cv2.cvtColor(med, cv2.COLOR_BGR2HSV); h, s, v = [hsv[..., i].astype(int) for i in range(3)]
R, A, G = [cv2.imread(f"bir_{clip}_{k}.png", 0).astype(np.float32) / 255 for k in ("rosa", "azul", "verde")]
def guiado(I, p, r=6, eps=1e-3):        # filtro guiado: el borde de la máscara se pega al borde real de la imagen
    I = I.astype(np.float32) / 255; box = lambda x: cv2.boxFilter(x, -1, (r, r))
    mI, mp = box(I), box(p); a = (box(I * p) - mI * mp) / (box(I * I) - mI * mI + eps); b = mp - a * mI
    return np.clip(box(a) * I + box(b), 0, 1)
gris = cv2.cvtColor(med, cv2.COLOR_BGR2GRAY)
R, A, G = [guiado(gris, x) for x in (R, A, G)]
azulpx = (h > 98) & (h < 135) & (s > 45) & (v < 150)
hueco = cv2.morphologyEx((azulpx & (G > 0.5)).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
hueco = cv2.GaussianBlur(cv2.morphologyEx(hueco, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)).astype(np.float32), (0, 0), 1.0)
G = G * (1 - hueco)
Gf = np.clip(G * 1.6 - 0.3, 0, 1)                                 # delante: la verde manda en el borde compartido
Gd = cv2.dilate((G > 0.3).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
A = np.maximum(A * (1 - np.maximum(Gf, Gd)), hueco); R = R * (1 - Gf)
def solo_grande(x, minimo=400):
    b = (x > 0.5).astype(np.uint8); n, lab, st, _ = cv2.connectedComponentsWithStats(b)
    keep = np.isin(lab, [i for i in range(1, n) if st[i, 4] > minimo]); keep = cv2.dilate(keep.astype(np.uint8), np.ones((5, 5), np.uint8))
    return x * keep
R, A, G = solo_grande(R, 3000), solo_grande(A), solo_grande(G, 3000)
for k, x in enumerate((R, A, G)):
    full = np.zeros((H, W), np.uint8); full[Y0:Y0 + x.shape[0], X0:X0 + x.shape[1]] = (np.clip(x, 0, 1) * 255).astype(np.uint8); cv2.imwrite(f"pesa_{clip}_{k}.png", full)
vis = []
for x, col in ((R, (48, 59, 255)), (A, (0, 200, 255)), (G, (93, 205, 33))):
    a = np.clip(x, 0, 1)[..., None]; o = (med * (1 - 0.65 * a) + np.array(col) * 0.65 * a).astype(np.uint8)
    c2, _ = cv2.findContours((x > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cv2.drawContours(o, c2, -1, (255, 255, 255), 1); vis.append(o)
cv2.imwrite(f"/tmp/recortes_{clip}.png", np.hstack(vis)); print(clip, "ok")
