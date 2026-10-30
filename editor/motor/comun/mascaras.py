# Silueta de la persona en cada fotograma de base.mov (rembg, modelo u2net_human_seg) -> mascaras_u2net/NNNNN.png,
# y después afina_mascaras.py deja el borde limpio en mascaras/. Lo llama montar.py solo en los estilos con gráficos detrás del cuerpo.
import os, subprocess
from PIL import Image
from rutas import ffmpeg, MODELOS, HILOS, respira
os.environ.setdefault("U2NET_HOME", MODELOS)                 # el modelo (~170 MB) se guarda en recursos-descargados/modelos
from rembg import remove, new_session
ses = new_session("u2net_human_seg"); os.makedirs("mascaras_u2net", exist_ok=True)
W, H = 1080, 1920
p = subprocess.Popen([ffmpeg(), "-v", "error", "-threads", str(HILOS), "-i", "base.mov", "-vf", "scale=540:960", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
n = 0
while True:
    b = p.stdout.read(540 * 960 * 3)
    if len(b) < 540 * 960 * 3: break
    out = f"mascaras_u2net/{n:05d}.png"
    if not os.path.exists(out):
        remove(Image.frombytes("RGB", (540, 960), b), session=ses, only_mask=True).resize((W, H), Image.BILINEAR).save(out)
    n += 1
    if n % 25 == 0: respira()
    if n % 100 == 0: print("  siluetas", n, flush=True)
print("siluetas", n)
