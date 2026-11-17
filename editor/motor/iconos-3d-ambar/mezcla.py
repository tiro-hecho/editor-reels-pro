# -*- coding: utf-8 -*-
# Sonido del estilo «iconos-3d-ambar»: efectos agudos, cortos y con aire, uno por cada cosa que aparece; nada de graves ni risers
import os, json, subprocess, numpy as np, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1, v2, v3, v5, v6   # uso: python mezcla.py  (tras python v6.py, que deja video.mp4)
from rutas_estilo import EFECTOS
FF = v1.FF; CUT = v1.CUT; wt = v1.wt
SR = 48000
# cada efecto del estilo -> archivo de editor/assets/efectos (los .mp3 los baja descargar_recursos.py al instalar)
MAPA = {"tr_swoosh026": "escenas-creador/swoosh1.mp3", "tr_swoosh023": "escenas-creador/swoosh2.mp3", "tr_swoosh014": "escenas-creador/swoosh1.mp3",
        "tr_swoosh027": "escenas-creador/swoosh2.mp3", "tr_swoosh015": "escenas-creador/swoosh1.mp3", "tr_swoosh024": "escenas-creador/swoosh2.mp3",
        "gl_effect1_397982": "pixabay/glitch.mp3", "holo_futuristic": "escenas-creador/whoosh_brillo.mp3", "clic_tech481191": "clic/tick.wav",
        "pop_clean467466": "aparecer/pop_1.wav", "pop_402324": "aparecer/pop_2.wav", "pop_sharp328170": "escenas-creador/pop.mp3",
        "clic_btn5_327756": "aparecer/obturador_camara.wav", "clic_mouse366460": "clic/clic_raton.wav", "clic_softpop451232": "escenas-creador/papel.mp3",
        "clic_scifi596258": "aparecer/cristal.wav", "tr_air352049": "aparecer/aparecer_suave.wav", "clic_button463065": "clic/clic_2.wav"}
def load(p, ss=0, dur=None):
    a = ["-ss", str(ss)] + (["-t", str(dur)] if dur else [])
    raw = subprocess.run([FF, "-v", "error", *a, "-i", p, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
voz = load("base.mov") * 10 ** (5 / 20); N = len(voz) + SR // 2
mix = np.zeros(N, np.float32); fxb = np.zeros(N, np.float32); mix[:len(voz)] += voz
ev = []
def E(t, name, db): ev.append((t, name, db))
# transiciones (aire)
E(0.0, "tr_swoosh026", -21); E(CUT[1], "tr_swoosh023", -20); E(CUT[2], "tr_swoosh026", -21); E(CUT[3], "tr_swoosh014", -21); E(CUT[4], "tr_swoosh027", -20)
E(v3.INV, "gl_effect1_397982", -24); E(CUT[1] - 0.06, "tr_swoosh024", -22); E(CUT[3] - 0.06, "tr_swoosh024", -22)                               # fotograma invertido
for a in v1.ARCOS: E(a + 0.25, "holo_futuristic", -25)            # arco de luz
for t0, _ in v1.ESQ: E(t0 + 0.02, "clic_tech481191", -19)         # esquinas
# pegatinas
pops = ["pop_clean467466", "pop_402324", "pop_sharp328170"]
for n, (nm, t0, *_ ) in enumerate(v3.STK): E(t0 + 0.04, pops[n % 3], -19)
E(v3.TCAM + 0.06, "clic_btn5_327756", -20)                         # obturador en la cámara
for nm, t0, *_ in v3.DROP: E(t0 + 0.28, "pop_sharp328170", -18)   # cae y rebota
# tarjetas en cascada: clic de papel cada una
for n, t0 in enumerate(v3.TCARD): E(t0 + 0.12, ["clic_mouse366460", "clic_softpop451232"][n % 2], -21)
# palabras gigantes: swish con brillo
for _, a, _, _ in v3.GIG: E(a + 0.02, "tr_swoosh015", -21); E(a + 0.10, "clic_scifi596258", -25)
E(v1.CUT[1] + .3, "clic_softpop451232", -22)
# billetes: aire que pasa por cada uno grande
for b in v3.BIL:
    if b["big"]: E(b["t"] + 0.15, "tr_air352049", -24)
# un tic suave al empezar cada frase de subtítulo
for t0, t1, ws in v1.LW:
    if ws: E(ws[0][1], "clic_button463065", -24)
for n, (_, a, _) in enumerate(v1.PILLS): E(a + 0.03, pops[n % 3], -19)
E(v6.T[2] + 0.20, "pop_sharp328170", -18); E(v6.T[2] + 0.16, "tr_swoosh015", -21)
for n in range(2): E(v6.T[n] + 0.20, "clic_tech481191", -21)
for t, name, db in ev:
    p = os.path.join(EFECTOS, *MAPA[name].split("/"))
    if not os.path.exists(p): print("falta", p); continue
    s = load(p, 0, 1.6)
    env = np.abs(s); pico = int(np.argmax(env)); w = s[max(0, pico - SR // 40): pico + SR // 40]
    rms = 20 * np.log10(np.sqrt(np.mean(w ** 2)) + 1e-9)          # volumen alrededor del pico (50 ms)
    g = 10 ** ((db - rms) / 20); st = int((t - pico / SR) * SR)
    if st < 0: s = s[-st:]; st = 0
    s = s[: N - st] * g; f = min(len(s), int(0.2 * SR)); s[-f:] *= np.linspace(1, 0, f)
    fxb[st:st + len(s)] += s
# quitar graves de los efectos (la ref casi no tiene nada por debajo de 150 Hz)
F = np.fft.rfft(fxb); fq = np.fft.rfftfreq(len(fxb), 1 / SR); F[fq < 180] *= 0.15; fxb = np.fft.irfft(F, len(fxb)).astype(np.float32)
mus = load(v1.MUS, 8.0, N / SR)[:N] if v1.MUS else np.zeros(N, np.float32)
mus = np.pad(mus, (0, max(0, N - len(mus))))
rm = np.sqrt(np.mean(mus[SR:SR * 6] ** 2)) + 1e-9; mus = mus / rm * 10 ** (-31 / 20)
fo = int(1.2 * SR); mus[-fo:] *= np.linspace(1, 0, fo); mus[:int(.2 * SR)] *= np.linspace(0, 1, int(.2 * SR))
mix[:len(mus)] += mus
pf = np.max(np.abs(fxb))
if pf > 0.5: fxb *= 0.5 / pf
mix += fxb
mix = np.where(np.abs(mix) > 0.85, np.sign(mix) * (0.85 + 0.12 * np.tanh((np.abs(mix) - 0.85) / 0.12)), mix)
mix = mix[: int(CUT[-1] * SR)]
(np.clip(mix, -1, 1) * 32767).astype(np.int16).tofile("mix.pcm")
subprocess.run([FF, "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "mix.pcm", "-i", "video.mp4", "-map", "1:v", "-map", "0:a",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "final.mp4"], check=True)
print("ok", len(ev), "efectos")
