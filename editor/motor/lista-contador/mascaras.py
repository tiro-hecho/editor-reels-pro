# Silueta de la persona en cada fotograma de base.mov (u2net_human_seg) -> mascaras/00000.png (1080x1920, L)
import os
KIT = os.environ.get("KIT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))  # raíz de la carpeta del kit
PROYECTO = os.getcwd()
import os, subprocess, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
W, H = 1080, 1920
SEG = ort.InferenceSession(os.path.join(os.environ.get("CLAUDE_PLUGIN_DATA", os.path.join(KIT, "_datos")), "modelos", "u2net_human_seg.onnx"),
                           providers=["CoreMLExecutionProvider", "CPUExecutionProvider"])
os.makedirs("mascaras", exist_ok=True)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", "base.mov", "-vf", "scale=320:320", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
n = 0
while True:
    b = p.stdout.read(320 * 320 * 3)
    if len(b) < 320 * 320 * 3: break
    x = np.frombuffer(b, np.uint8).reshape(320, 320, 3).astype(np.float32) / 255
    x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
    o = SEG.run(None, {SEG.get_inputs()[0].name: x})[0][0, 0]; o = (o - o.min()) / (o.max() - o.min() + 1e-6)
    m = Image.fromarray((np.clip((o - 0.15) / 0.7, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5))
    m.save(f"mascaras/{n:05d}.png"); n += 1
print("máscaras:", n)
