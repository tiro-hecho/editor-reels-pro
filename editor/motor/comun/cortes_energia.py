# Ajusta el inicio y el fin de cada tramo a la energía REAL de la voz (ventanas de 10 ms), sin meter palabras vecinas.
# Los tiempos de Whisper se comen sílabas («controlar», la «C» de «Correr»): se corta siempre con esto.
#   uso: python cortes_energia.py <bruto> <palabras.json> a1 b1 [a2 b2 ...]   -> imprime los tramos ajustados
import json, os, subprocess, sys, tempfile, wave, numpy as np
from rutas import ffmpeg
bruto, pal = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8")); xs = [float(x) for x in sys.argv[3:]]
tmp = os.path.join(tempfile.gettempdir(), "energia_%d.wav" % os.getpid())
subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", bruto, "-vn", "-ac", "1", "-ar", "16000", tmp], check=True)
w = wave.open(tmp); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; w.close(); os.remove(tmp)
H = sr // 100; rms = np.array([np.sqrt(np.mean(a[i:i + H] ** 2) + 1e-12) for i in range(0, len(a) - H, H)]); db = 20 * np.log10(rms)
UM = np.percentile(db, 10) + 12                                      # voz = 12 dB por encima del ruido de fondo
def voz(i): return db[max(0, i):i + 3].mean() > UM                    # 30 ms seguidos con voz
for a0, b0 in zip(xs[::2], xs[1::2]):
    prev = max([p["e"] for p in pal if p["e"] <= a0 - 0.05] + [0]); nxt = min([p["s"] for p in pal if p["s"] >= b0 + 0.05] + [1e9])
    i = int(max(a0 - 0.35, prev + 0.05) * 100)
    while i < a0 * 100 + 40 and not voz(i): i += 1
    ini = max(i / 100 - 0.06, prev + 0.03)
    j = int(min(b0 + 0.45, nxt - 0.05) * 100)
    while j > b0 * 100 - 40 and not voz(j - 3): j -= 1
    fin = min(j / 100 + 0.10, nxt - 0.03)
    print(f"{a0:.2f}-{b0:.2f} -> {ini:.3f}-{fin:.3f}")
