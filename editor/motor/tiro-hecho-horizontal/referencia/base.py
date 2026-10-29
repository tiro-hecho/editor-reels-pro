# REFERENCIA del VSL de Tiro Hecho (horizontal). No es un motor genérico: Claude lo adapta a cada vídeo.
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'comun')); from rutas import *
# Renderiza cada plano a 1920x1080 30 fps (sin audio) y monta la voz con fundidos de 5 ms.
import json, subprocess, os, numpy as np, wave
from concurrent.futures import ThreadPoolExecutor
FPS = 30; P = json.load(open("plan.json"))
REC = "brutos/grabacion_pantalla.mp4"; REC_OFF = 9.221; COFF = 184.0
CARAS = {"S": (0.665, 0.33), "T": (0.275, 0.31), "?": (0.47, 0.33)}
os.makedirs("seg", exist_ok=True)

# modo de cada plano de C: pantalla salvo cada 3.º y el último de cada tramo
c = 0
for i, p in enumerate(P):
    if p["clip"] != "C": p["modo"] = "cam"; continue
    ult = i + 1 == len(P) or P[i + 1]["seg"] != p["seg"]
    p["modo"] = "cam" if (c % 3 == 0 or ult) else ("card" if c % 2 else "full")
    c += 1

def crop(p):
    z = p["zoom"]
    if z == 1.0: return ""
    w = 3840 / z; h = 2160 / z
    if p["clip"] == "A": fx, fy = CARAS[p.get("habla", "?")]
    elif p["clip"] == "B": fx, fy = 0.5, 0.42
    else: fx, fy = 0.46, 0.40
    cx = fx * 3840; cy = fy * 2160 + h * 0.15
    x = min(max(cx - w / 2, 0), 3840 - w); y = min(max(cy - h / 2, 0), 2160 - h)
    return f"crop={int(w)//2*2}:{int(h)//2*2}:{int(x)}:{int(y)},"

def kb(i):
    """Empuje lento durante el plano + golpe de zoom (sobrepaso) al entrar si sube el zoom."""
    p = P[i]; d = max(p["f"] - p["s"], 0.3)
    punch = 0.06 if i and p["zoom"] > P[i - 1]["zoom"] else 0.0
    Z = f"(1+0.04*t/{d:.3f}+{punch}*exp(-t*13))"
    return (f"scale=w='2*trunc(960*{Z})':h='2*trunc(540*{Z})':eval=frame:flags=lanczos,"
            f"crop=1920:1080:(iw-1920)/2:(ih-1080)/2")

def render(i):
    p = P[i]; out = f"seg/{i:03d}.mp4"
    n = round((p["f"] - p["s"]) * FPS); p["n"] = n
    if os.path.exists(out): return
    enc = ["-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-pix_fmt", "yuv420p", "-r", "30", "-frames:v", str(n)]
    if p["modo"] == "cam":
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{p['s']:.4f}", "-i", f"src/{p['clip']}.mov", "-vf", crop(p) + kb(i) + ",setsar=1"] + enc + [out]
    else:
        rt = p["s"] + COFF - REC_OFF
        if p["modo"] == "card":
            fc = ("[1:v]fps=30,scale=1360:880:flags=lanczos,format=rgba[r];[2:v]format=gray[m];[r][m]alphamerge[rm];"
                  "[0:v][rm]overlay=280:100[o];[o][3:v]overlay=0:0,format=yuv420p")
            cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", "gfx/fondo.png", "-ss", f"{rt:.4f}", "-i", REC,
                   "-loop", "1", "-i", "gfx/mask_pantalla.png", "-loop", "1", "-i", "gfx/borde_pantalla.png", "-filter_complex", fc] + enc + [out]
        else:  # pantalla completa: recorte a 16:9 de la parte de arriba (la tabla del PDF)
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{rt:.4f}", "-i", REC, "-vf",
                   "fps=30,crop=2880:1620:0:120," + kb(i) + ",setsar=1"] + enc + [out]
    subprocess.run(cmd, check=True)

for i, p in enumerate(P): p["n"] = round((p["f"] - p["s"]) * FPS)
with ThreadPoolExecutor(5) as ex: list(ex.map(render, range(len(P))))

# concatenar
with open("seg/lista.txt", "w") as f:
    for i in range(len(P)): f.write(f"file '{i:03d}.mp4'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-i", "seg/lista.txt", "-c", "copy", "base.mp4"], check=True)

# voz: mismas fronteras de fotograma, fundido de 5 ms en cada unión de corte
def rd(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)
SR = 48000
for k in "ABC":
    if not os.path.exists(f"audio/{k}48.wav"):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"src/{k}.mov", "-vn", "-ac", "1", "-ar", "48000", f"audio/{k}48.wav"], check=True)
A = {k: rd(f"audio/{k}48.wav") for k in "ABC"}
out = []; fd = int(0.005 * SR)
for p in P:
    a = round(p["s"] * SR); x = A[p["clip"]][a:a + p["n"] * SR // FPS].copy()
    x = np.pad(x, (0, p["n"] * SR // FPS - len(x)))
    if p["nuevo_corte"]: x[:fd] *= np.linspace(0, 1, fd)
    out.append(x)
# fundido de salida al final de cada pieza que acaba en corte
for i in range(len(P) - 1):
    if P[i + 1]["nuevo_corte"]: out[i][-fd:] *= np.linspace(1, 0, fd)
v = np.concatenate(out)
w = wave.open("voz.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(np.clip(v, -32768, 32767).astype(np.int16).tobytes()); w.close()
# línea de tiempo: t0 de cada plano en fotogramas
t = 0
for p in P: p["t0"] = t / FPS; t += p["n"]
json.dump(P, open("plan.json", "w"), indent=1)
print("duración", t / FPS)
