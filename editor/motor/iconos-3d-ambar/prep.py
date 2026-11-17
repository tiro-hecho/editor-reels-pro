# -*- coding: utf-8 -*-
# Paso 1 del estilo «iconos-3d-ambar»: corta el bruto por tramos (bordes afinados por energía a 10 ms),
# saca base.mov 1080x1920 a 30 fps, transcribe palabra a palabra y deja cuts.json.
#   python prep.py bruto.mov tramos.json      tramos.json = [[inicio, fin], ...] en segundos (tiempos de Whisper)
import subprocess, json, sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas_estilo import FF
BRUTO, TRAMOS = sys.argv[1], json.load(open(sys.argv[2]))
raw = subprocess.run([FF, "-v", "error", "-i", BRUTO, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768; n = 160
E = 20 * np.log10(np.sqrt(np.mean(a[:len(a)//n*n].reshape(-1, n) ** 2, 1)) + 1e-9)
TH = -42; PRE, POST, GAP = .06, .08, .22
piezas = []
for k, (s0, s1) in enumerate(TRAMOS):
    i0, i1 = int(s0 * 100), int(s1 * 100); idx = np.where(E[i0:i1] > TH)[0]
    if not len(idx): continue
    s, e = i0 + idx[0], i0 + idx[-1] + 1; sub = []; j = s; cur = s
    while j < e:                       # parte las pausas internas largas
        if E[j] <= TH:
            q = j
            while q < e and E[q] <= TH: q += 1
            if (q - j) / 100 >= GAP: sub.append((cur, j)); cur = q
            j = q
        else: j += 1
    sub.append((cur, e))
    for x, y in sub: piezas.append((k, max(0, x / 100 - PRE), y / 100 + POST))
inp = []; fc = []
for i, (k, s0, s1) in enumerate(piezas):
    inp += ["-ss", f"{s0:.3f}", "-t", f"{s1-s0:.3f}", "-i", BRUTO]
    fc.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30[v{i}];"
              f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,afade=t=in:d=0.008,afade=t=out:st={s1-s0-0.012:.3f}:d=0.012[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(len(piezas))) + f"concat=n={len(piezas)}:v=1:a=1[v][a]")
subprocess.run([FF, "-y", "-v", "error", *inp, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "pcm_s16le", "base.mov"], check=True)
cuts = [0.0]
for k, s0, s1 in piezas: cuts.append(round(cuts[-1] + s1 - s0, 3))
subprocess.run([FF, "-y", "-v", "error", "-i", "base.mov", "-vn", "-ac", "1", "-ar", "16000", "base16.wav"], check=True)
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8")
au = np.frombuffer(open("base16.wav", "rb").read()[44:], np.int16).astype(np.float32) / 32768
segs, _ = m.transcribe(au, language="es", word_timestamps=True)
pal = [[round(x.start, 2), round(x.end, 2), x.word.strip()] for sg in segs for x in sg.words]
json.dump({"cuts": cuts, "piezas": piezas, "pal": pal}, open("cuts.json", "w", encoding="utf8"), ensure_ascii=False)
os.makedirs("fr", exist_ok=True)
subprocess.run([FF, "-y", "-v", "error", "-i", "base.mov", "-q:v", "2", os.path.join("fr", "%04d.jpg")], check=True)
print(cuts); print(" ".join(p[2] for p in pal))
