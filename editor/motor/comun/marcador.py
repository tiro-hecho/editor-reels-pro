# Compositor de los formatos «marcador» (funciona/no funciona, ranking 1-10): el vídeo de la persona tal cual,
# con una capa HTML encima renderizada a 60 fps y promediada de dos en dos (desenfoque de movimiento real).
#   uso: lo llama montar.py desde la carpeta del vídeo
import os, sys, json, math, subprocess, numpy as np
from rutas import HILOS, respira
from PIL import Image

W, H, FPS = 1080, 1920, 30
DUR = json.load(open("plan.json"))["dur"]
# Las capas HTML (overlay/ a 60 fps y overlay_detras/ a 30 fps) las pinta antes montar.py.

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-threads", str(HILOS), "-i", "base.mov", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-threads", str(HILOS), "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
# Cámara virtual (camara.json): golpes de zoom, empujes lentos y destellos, sobre el plano de la persona (no sobre los gráficos).
#   [{"t": 3.2, "tipo": "golpe", "z": 1.15}, {"t0": 5, "t1": 8, "tipo": "empuje", "z": 1.07}, {"t": 9.1, "tipo": "flash"}]
CAM = json.load(open("camara.json")) if os.path.exists("camara.json") else []
CX, CY = 540, 700                                     # centro del zoom: la cara
def o3(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def io(x): x = max(0.0, min(1.0, x)); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def zoom_en(t):
    z = 1.0
    for c in CAM:
        if c["tipo"] == "empuje" and c["t0"] <= t < c["t1"] + 0.6:
            k = io((t - c["t0"]) / (c["t1"] - c["t0"])) if t < c["t1"] else 1 - io((t - c["t1"]) / 0.6)
            z *= 1 + (c["z"] - 1) * k
        if c["tipo"] == "golpe" and 0 <= t - c["t"] < 1.1:
            k = t - c["t"]; z *= 1 + (c["z"] - 1) * (o3(k / 0.12) if k < 0.12 else 1 - io((k - 0.12) / 0.98))
    return z
def flash_en(t): return max([0.0] + [0.55 * (1 - (t - c["t"]) / (2 / FPS)) for c in CAM if c["tipo"] == "flash" and 0 <= t - c["t"] < 2 / FPS])
# Escenas (escenas.json): B-roll a pantalla completa o pantalla partida (B-roll arriba, la persona abajo).
#   [{"t0": 0, "t1": 1.1, "tipo": "broll", "src": "../stock/x.mp4", "ini": 1.0}, {"t0": ..., "tipo": "partida", ...}]
from PIL import ImageDraw
ESC = json.load(open("escenas.json")) if os.path.exists("escenas.json") else []
PANEL = (1052, 932)
def clip(src, ini, dur, w, h):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ini), "-t", str(dur + 0.3), "-i", src, "-vf",
                        f"fps=30,scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return [Image.frombytes("RGB", (w, h), r[i:i + w * h * 3]) for i in range(0, len(r) - w * h * 3 + 1, w * h * 3)]
for e in ESC: e["fr"] = clip(e["src"], e.get("ini", 0), e["t1"] - e["t0"], *((W, H) if e["tipo"] == "broll" else PANEL)) if e.get("src") else []
def redondea(im, r):
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=r, fill=255); return m
def zoom_c(im, z, cy):
    if z <= 1.001: return im
    k = 1 / z; return im.transform(im.size, Image.AFFINE, (k, 0, (im.width - k * im.width) / 2, 0, k, min(max(cy - k * cy, 0), im.height - k * im.height)), resample=Image.BICUBIC)
last = None
for n in range(int(round(DUR * FPS))):
    if n % 60 == 0: respira()
    b = dec.stdout.read(W * H * 3)
    fr = Image.frombytes("RGB", (W, H), b) if len(b) == W * H * 3 else last; last = fr
    t = n / FPS; z = zoom_en(t) * 1.03; e = next((x for x in ESC if x["t0"] <= t < x["t1"]), None)
    # cámara en mano suave: la imagen nunca está clavada (sin temblor, solo flotación lenta)
    fx, fy = 7 * math.sin(2 * math.pi * t / 3.7), 6 * math.sin(2 * math.pi * t / 5.3 + 1.0)
    persona = fr
    if e is not None:
        k = t - e["t0"]; fs = e["fr"]; b_ = fs[min(len(fs) - 1, int(k * FPS))] if fs else Image.new("RGB", PANEL, (0, 0, 0))
        asienta = 1 + 0.08 * (1 - o3(k / 0.4)) + 0.05 * k / max(e["t1"] - e["t0"], 0.1)      # entra un poco grande, se asienta y empuja
        if e["tipo"] == "tarjeta":
            T_ = e; lienzo = Image.new("RGB", (W, H), tuple(T_.get("fondo", [242, 238, 232])))
            ent = o3(k / 0.5) if T_.get("entra") else 1.0
            sc = T_["esc"] * (1.12 - 0.12 * ent); cw, ch = int(W * sc), int(H * sc)
            cara = zoom_c(persona, 1 + 0.04 * math.sin(t / 2.0), CY).resize((cw, ch), Image.LANCZOS)
            lienzo.paste(cara, (T_["x"], T_["y"]), redondea(cara, 48)); fr = lienzo
        elif e["tipo"] == "broll":
            fr = zoom_c(b_, asienta, 960)
            if e.get("pip"):                      # la persona sigue en una ventanita bajo el marcador, a la derecha
                k2 = o3(k / 0.35); pw, ph = int(250 * k2), int(444 * k2)
                if pw > 10:
                    cara = persona.crop((240, 400, 840, 1467)).resize((pw, ph), Image.LANCZOS)
                    marco = Image.new("RGB", (pw + 10, ph + 10), (255, 255, 255)); marco.paste(cara, (5, 5))
                    fr = fr.copy(); fr.paste(marco, (934 - pw - 10, 600), redondea(marco, 28))
        else:
            lienzo = Image.new("RGB", (W, H), (12, 12, 12)); arriba = zoom_c(b_, asienta, 466)
            abajo = zoom_c(fr, 1.35 * z, CY).crop((14, CY - 300, 14 + PANEL[0], CY - 300 + PANEL[1]))
            lienzo.paste(arriba, (14, 14), redondea(arriba, 36)); lienzo.paste(abajo, (14, 14 + PANEL[1] + 14), redondea(abajo, 36)); fr = lienzo
    elif z > 1.001:
        k = 1 / z; fr = fr.transform((W, H), Image.AFFINE, (k, 0, min(max(CX - k * CX + fx, 0), W - k * W), 0, k, min(max(CY - k * CY + fy, 0), H - k * H)), resample=Image.BICUBIC)
    img = fr.convert("RGBA")
    pd = f"overlay_detras/f{n:04d}.png"
    if e is None and os.path.exists(pd) and os.path.exists(f"mascaras/{n:05d}.png"):
        capa = Image.open(pd).convert("RGBA")
        if capa.getbbox():
            m = Image.open(f"mascaras/{n:05d}.png").convert("L")
            if z > 1.001: m = m.transform((W, H), Image.AFFINE, (1 / z, 0, min(max(CX - CX / z + fx, 0), W - W / z), 0, 1 / z, min(max(CY - CY / z + fy, 0), H - H / z)), resample=Image.BILINEAR)
            pers = img.copy(); pers.putalpha(m); img.alpha_composite(capa); img.alpha_composite(pers)
    p1, p2 = f"overlay/f{2 * n:04d}.png", f"overlay/f{2 * n + 1:04d}.png"
    if os.path.exists(p1):
        a1 = np.asarray(Image.open(p1).convert("RGBA"), np.float32); a2 = np.asarray(Image.open(p2).convert("RGBA"), np.float32) if os.path.exists(p2) else a1
        al = (a1[..., 3:] + a2[..., 3:]) / 2; col = (a1[..., :3] * a1[..., 3:] + a2[..., :3] * a2[..., 3:]) / 2 / np.maximum(al, 1e-3)
        img.alpha_composite(Image.fromarray(np.concatenate([col, al], -1).clip(0, 255).astype(np.uint8), "RGBA"))
    fl = flash_en(t)
    if fl > 0: img = Image.blend(img, Image.new("RGBA", (W, H), (255, 255, 255, 255)), fl)
    enc.stdin.write(img.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.kill(); print("video.mp4 listo")
