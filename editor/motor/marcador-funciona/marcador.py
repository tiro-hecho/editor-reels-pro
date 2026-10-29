# Compositor de los formatos «marcador» (funciona/no funciona, ranking 1-10): el vídeo de la persona tal cual,
# con una capa HTML encima renderizada a 60 fps y promediada de dos en dos (desenfoque de movimiento real).
#   uso (desde la carpeta del vídeo):  python3 ../marcador.py [sin_overlay]
import os, sys, json, subprocess, numpy as np
from PIL import Image

PL = os.environ.get("KIT", os.path.expanduser("~/Edicion-video/plugin-editor-reels-pro"))
W, H, FPS = 1080, 1920, 30
DUR = json.load(open("plan.json"))["dur"]
if "sin_overlay" not in sys.argv:
    # tandas de 250 fotogramas, cada una con un Chrome nuevo; si una se cae, la siguiente sigue donde quedó
    for intento in range(40):
        r = subprocess.run([sys.executable, f"{PL}/motor/render_html.py", "overlay.html", "overlay", str(DUR), str(FPS * 2)], env=dict(os.environ, TANDA="250"))
        if r.returncode == 0: break
    else: raise SystemExit("el overlay no se completó")

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", "2", "-i", "base.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-threads", "2", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
last = None
for n in range(int(round(DUR * FPS))):
    b = dec.stdout.read(W * H * 3)
    fr = Image.frombytes("RGB", (W, H), b) if len(b) == W * H * 3 else last; last = fr
    img = fr.convert("RGBA")
    p1, p2 = f"overlay/f{2 * n:04d}.png", f"overlay/f{2 * n + 1:04d}.png"
    if os.path.exists(p1):
        a1 = np.asarray(Image.open(p1).convert("RGBA"), np.float32); a2 = np.asarray(Image.open(p2).convert("RGBA"), np.float32) if os.path.exists(p2) else a1
        al = (a1[..., 3:] + a2[..., 3:]) / 2; col = (a1[..., :3] * a1[..., 3:] + a2[..., :3] * a2[..., 3:]) / 2 / np.maximum(al, 1e-3)
        img.alpha_composite(Image.fromarray(np.concatenate([col, al], -1).clip(0, 255).astype(np.uint8), "RGBA"))
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.kill(); print("video.mp4 listo")
