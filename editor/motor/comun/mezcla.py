# Mezcla: voz + música (con sidechain y nivel automático) + efectos en cada evento -> final_musica.mp4 a -14 LUFS.
#   eventos.json: [[segundo, ruta_o_nombre, dB], ...]  ·  MUSICA=archivo de recursos-descargados/musica  ·  volumen.json opcional
import json, subprocess, numpy as np
SR = 48000
P = json.load(open("plan.json")); DUR = P["dur"]; EV = json.load(open("eventos.json"))
import os
from rutas import EF as K, ESC as V, MIT, MUS as M
S = MIT
def carga(f, ini=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ini), "-i", f] + (["-t", str(dur)] if dur else []) + ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
def db(x): return 10 ** (x / 20)

voz = carga("base.wav"); N = int(DUR * SR); voz = np.pad(voz, (0, max(0, N - len(voz))))[:N]

# ---- efectos: (archivo, dB). El pico del sonido se coloca justo en el fotograma del evento.
SFX = {"pop_grande": [(V + "flash.mp3", -21), (V + "boom.mp3", -28)],
       "golpe": [(V + "flash.mp3", -20), (V + "boom.mp3", -25)],
       "golpe_suave": [(V + "flash.mp3", -23)],
       "error": [(K + "error/error_1.wav", -25)], "flash": [(V + "flash.mp3", -19)],
       "whoosh": [(V + "swoosh1.mp3", -25)], "whoosh_suave": [(V + "swoosh1.mp3", -27)], "pop": [(V + "pop2.mp3", -21)],
       "ding": [(V + "ding.mp3", -23)], "malo": [(S + "malo1_corto.mp3", -23), (S + "switch_on.mp3", -16)], "bueno": [(K + "clic/tick.wav", -16), (S + "switch_on.mp3", -14)], "perfecto": [(S + "top2_levelup.mp3", -19), (S + "switch_on.mp3", -16)], "estrella": [(K + "clic/tick.wav", -20)], "luz": [(S + "switch_on.mp3", -12)], "luz_perfecto": [(S + "switch_on.mp3", -12), (S + "power_up.mp3", -20)], "ding_final": [(V + "ding.mp3", -21)]}
CACHE = {}
def sfx(f):
    if f not in CACHE:
        a = carga(f); env = np.convolve(np.abs(a), np.ones(240) / 240, "same"); CACHE[f] = (a, int(np.argmax(env)))
    return CACHE[f]
fx = np.zeros(N, np.float32)
fx_gancho = []          # caída de graves bajo el primer golpe
for ev in EV:
    t, k = ev[0], ev[1]
    for f, g in (SFX[k] if k in SFX else [(k, ev[2] if len(ev) > 2 else -22)]):   # también [t, ruta, dB]
        a, pk = sfx(f); i0 = int(t * SR) - pk if "reverse" not in f else int(t * SR) - len(a) + int(0.02 * SR)
        a = a * db(g); j0 = max(0, i0); a = a[j0 - i0:]; j1 = min(N, j0 + len(a)); fx[j0:j1] += a[:j1 - j0]
for t, f, g in fx_gancho:
    a, pk = sfx(f); a = a[pk - int(0.05 * SR):] * db(g); fx[:min(N, len(a))] += a[:N]

# ---- música por bloques: (desde, hasta, pista, segundo de la pista donde empieza, dB)

import sys
CON_MUSICA = "musica" in sys.argv
BLOQ = [(0.0, DUR, os.environ.get("MUSICA", "vlog_hiphop.mp3"), float(os.environ.get("MUSICA_INI", "1.0")), float(os.environ.get("MUSICA_DB", "-21")))] if CON_MUSICA else []
mus = np.zeros(N, np.float32)
for a, b, f, ini, g in BLOQ:
    x = carga(M + f, ini, b - a + 0.3) * db(g); i0 = int(a * SR); n = min(len(x), N - i0, int((b - a) * SR))
    x = x[:n].copy(); fi, fo = int(0.02 * SR), int((0.9 if b >= DUR else 0.12) * SR); x[:fi] *= np.linspace(0, 1, fi); x[-fo:] *= np.linspace(1, 0, fo)
    mus[i0:i0 + n] += x
# sidechain: la música baja ~6 dB cuando habla
env = np.convolve(np.abs(voz), np.ones(int(0.05 * SR)) / int(0.05 * SR), "same"); hab = (env > 0.02).astype(np.float32)
hab = np.convolve(hab, np.ones(int(0.15 * SR)) / int(0.15 * SR), "same")
mus *= 1 - 0.88 * np.clip(hab, 0, 1)
# nivel automático: la música queda 16 dB por debajo de la voz (medido), sea cual sea la canción
def rms(x): x = x[np.abs(x) > 1e-4]; return float(np.sqrt(np.mean(x ** 2))) if len(x) else 1e-6
if CON_MUSICA:
    v = rms(voz[hab > 0.5]) if (hab > 0.5).any() else rms(voz); m = rms(mus[hab < 0.2]) if (hab < 0.2).any() else rms(mus)
    mus *= (v / max(m, 1e-6)) * 10 ** (-16 / 20)

# juego de volúmenes de la música (volumen.json: [desde, hasta, dB] con rampas de 80 ms)
if CON_MUSICA and os.path.exists("volumen.json"):
    g = np.zeros(N, np.float32); r = int(0.08 * SR)
    for t0, t1, d in json.load(open("volumen.json")):
        i0, i1 = max(0, int(t0 * SR)), min(N, int(t1 * SR))
        if i1 <= i0: continue
        w = np.ones(i1 - i0, np.float32)
        k = min(r, len(w) // 2); w[:k] = np.linspace(0, 1, k); w[len(w) - k:] = np.linspace(1, 0, k); g[i0:i1] += w * d
    mus *= 10 ** (g / 20)
mez = voz + mus + fx
mez = mez / max(1.0, np.abs(mez).max() / 0.95)
mez.astype(np.float32).tofile("mezcla.f32")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "mezcla.f32",
                "-af", f"loudnorm=I=-14:TP=-1.5:LRA=9,apad=whole_dur={DUR}", "-t", str(DUR), "-ar", "48000", "-ac", "2", "mezcla.wav"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "video.mp4", "-i", "mezcla.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", "final_musica.mp4" if CON_MUSICA else "final.mp4"], check=True)
print("final_musica.mp4 listo" if CON_MUSICA else "final.mp4 listo")
