# Descarga desde Pixabay la música y los efectos que usan los estilos (no se pueden repartir en el repositorio)
# y los deja listos en recursos-descargados/. Se puede repetir: solo baja lo que falte.
#   uso: python editor/motor/comun/descargar_recursos.py
import json, os, shutil, subprocess, sys, urllib.request
from rutas import EDITOR, DESCARGAS, ffmpeg
R = json.load(open(os.path.join(EDITOR, "recursos.json"), encoding="utf-8"))
FF = ffmpeg(); fallos = []

def baja(url, dst):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dst + ".part", "wb") as f: shutil.copyfileobj(r, f)
    os.replace(dst + ".part", dst)

for grupo, items in R.items():
    if grupo.startswith("_"): continue
    d = os.path.join(DESCARGAS, *grupo.split("/")); os.makedirs(d, exist_ok=True)
    for nombre, x in items.items():
        if nombre.startswith("_"): continue
        dst = os.path.join(d, nombre)
        if os.path.exists(dst): continue
        try:
            if isinstance(x, str) and x.startswith("http"): baja(x, dst)                                  # tal cual
            elif isinstance(x, list):                                                                      # recortado e igualado
                crudo = dst + ".crudo.mp3"; baja(x[0], crudo); m = x[1]
                subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", crudo, "-af",
                                f"silenceremove=start_periods=1:start_threshold=-45dB,atrim=0:{m},afade=t=out:st={m - 0.25}:d=0.25,loudnorm=I=-16:TP=-2",
                                "-ar", "44100", "-ac", "2", "-b:a", "192k", dst], check=True); os.remove(crudo)
            elif isinstance(x, dict):                                                                      # derivado de otro
                subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", os.path.join(d, x["de"]), *x["ffmpeg"].split(), dst], check=True)
            else:                                                                                          # copia de otro grupo
                shutil.copy(os.path.join(DESCARGAS, "efectos", *x.split("/")), dst)
            print("  ✓", grupo, nombre, flush=True)
        except Exception as e:
            fallos.append(f"{grupo}/{nombre}: {e}")
if fallos: print("No se pudieron descargar:\n  " + "\n  ".join(fallos)); sys.exit(1)
print("Recursos listos en", DESCARGAS)
