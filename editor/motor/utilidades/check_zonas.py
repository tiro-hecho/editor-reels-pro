"""Pinta la zona tapada por TikTok/Instagram sobre fotogramas del vídeo y avisa si hay texto en ella.
Uso: python3 check_zonas.py video.mp4  →  video_zonas.jpg (hoja con cuadrícula) + informe en pantalla."""
import sys, subprocess, numpy as np
from PIL import Image, ImageDraw
V = sys.argv[1]; W, H = 1080, 1920; X0, X1, Y0, Y1 = 60, 940, 220, 1440
dur = float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",V],capture_output=True,text=True).stdout)
n = min(24, max(6, int(dur))); fotos, avisos = [], []
for i in range(n):
    t = dur * (i + .5) / n
    raw = subprocess.run(["ffmpeg","-v","error","-ss",f"{t:.2f}","-i",V,"-frames:v","1","-vf",f"scale={W}:{H}","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(int)
    # texto ≈ píxel claro (blanco/amarillo) pegado a uno oscuro a ≤3 px (letra con contorno o sobre fondo)
    L = a.mean(2); claro = (a.min(2) > 200) | ((a[...,0] > 200) & (a[...,1] > 170) & (a[...,2] < 110))
    osc = L < 90; cerca = np.zeros_like(osc)
    for dx in (-3, 3):
        cerca |= np.roll(osc, dx, 1); cerca |= np.roll(osc, dx, 0)
    m = claro & cerca; zona = np.ones((H, W), bool); zona[Y0:Y1, X0:X1] = False
    k = (m & zona).sum()
    if k > 600: avisos.append(f"  ⚠️  {t:5.1f}s: posible texto en zona tapada ({k} px)")
    im = Image.fromarray(a.astype(np.uint8)); ov = Image.new("RGBA", (W, H), (0,0,0,0)); d = ImageDraw.Draw(ov)
    for r in [(0,0,W,Y0),(0,Y1,W,H),(0,Y0,X0,Y1),(X1,Y0,W,Y1)]: d.rectangle(r, fill=(255,0,0,70))
    d.rectangle((X0,Y0,X1,Y1), outline=(0,255,0,255), width=6)
    fotos.append(Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB").resize((270,480)))
cols = 6; filas = (len(fotos)+cols-1)//cols; hoja = Image.new("RGB", (270*cols, 480*filas))
for i,f in enumerate(fotos): hoja.paste(f, ((i%cols)*270, (i//cols)*480))
out = V.rsplit(".",1)[0] + "_zonas.jpg"; hoja.save(out, quality=85)
print(f"Hoja: {out}"); print("\n".join(avisos) if avisos else "✅ No se detecta texto en las zonas tapadas (revisa igualmente la hoja).")
