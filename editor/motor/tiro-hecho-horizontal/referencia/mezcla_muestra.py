# REFERENCIA del VSL de Tiro Hecho (horizontal). No es un motor genérico: Claude lo adapta a cada vídeo.
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'comun')); from rutas import *
# Sonido de la muestra v3 (0–55 s): voz + hip hop con caída antes de «FUNCIONA» + efectos por escena.
import json, subprocess, numpy as np, wave, sys
sys.argv = ["x"]; import escenas as S, subs3 as S3
SR = 48000; A, B = 0.0, 55.0; L = int((B - A) * SR)
K = EF; M = PX
FR = ESC
def carga(p, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", str(ch), "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch).copy()
CA = {}
def snd(p):
    if p not in CA: x = carga(p); CA[p] = x * (0.5 / (np.abs(x).max() + 1e-9))
    return CA[p]
fx = np.zeros((L, 2), np.float32)
def pon(p, t, g, md=None):
    x = snd(p)
    if md: x = x[:int(md * SR)].copy(); f = int(0.06 * SR); x[-f:] *= np.linspace(1, 0, f)[:, None]
    a = int((t - A) * SR); b = min(L, a + len(x))
    if 0 <= a < L: fx[a:b] += x[:b - a] * g
POPS = [M + f"pop_{n}.mp3" for n in (2354, 2356, 2357, 2358, 2359, 2361)]; ip = [0]
def pop(t, g=0.4): pon(POPS[ip[0] % 6], t, g); ip[0] += 1
WH = [K + "whoosh_1485.mp3", K + "whoosh_1490.mp3", K + "whoosh_1492.mp3", K + "whoosh_1489.mp3"]
RIS = snd(ESC + "riser.mp3"); env_ = np.abs(RIS).mean(1)
pk = int(np.convolve(env_, np.ones(2400) / 2400, "same").argmax())
def riser(t, d=1.6, g=0.45):
    x = RIS[max(0, pk - int(d * SR)):pk].copy(); f = int(0.4 * SR); x[:f] *= np.linspace(0, 1, f)[:, None]
    a = int((t - A) * SR) - len(x); a0 = max(0, a); fx[a0:a + len(x)] += x[a0 - a:] * g
# subtítulos: tecleo, pops y golpe suave en la palabra gigante
TEC = snd("sfx/teclado1.mp3")
for t, tp, d in S3.eventos_sonido():
    if not (A <= t < B): continue
    if tp == "teclea":
        x = TEC[int(1.0 * SR):int((1.0 + d) * SR)].copy(); a = int((t - A) * SR); fx[a:a + len(x)] += x[:max(0, L - a)] * 0.35
    elif tp == "pop": pon(POPS[ip[0] % 6], t, 0.16); ip[0] += 1
    elif tp == "grande": pon(POPS[ip[0] % 6], t, 0.35); ip[0] += 1
# zooms = whoosh
for i, p in enumerate(S.G.P):
    if i and p["zoom"] > S.G.P[i - 1]["zoom"] and A < p["t0"] < B and not S.escena_en(p["t0"]): pon(WH[i % 4], p["t0"] - 0.12, 0.2, 0.7)
for i, e in enumerate(S.ES):
    t0, t1, tp = e["t0"], e["t1"], e["tipo"]
    pon("sfx/flash.mp3", t0 - 0.05, 0.5, 0.9)                                    # transición = flash de cámara
    pon(K + "soft-whoosh__1346-preview.mp3", t1 - 0.12, 0.18, 0.6)
    if tp in ("chat", "meta"): riser(t0)                                          # revelados = riser metálico
    if tp in ("recorte", "nombres"): pon(FR + "boom.mp3", t0 + 0.05, 0.45)
    if tp == "recorte_cifras":
        for tc, _ in e["cifras"]: pon(FR + "boom.mp3", tc, 0.4); pon(K + "swipe__2627-preview.mp3", tc - 0.05, 0.25)
    if tp == "editor":
        for k in range(int((t1 - t0) / 0.25)): pon(K + "click__1660-preview.mp3", t0 + 0.4 + k * 0.25, 0.12, 0.12)   # reloj
    if tp == "factura":
        for k in range(14): pon(K + "click__1113-preview.mp3", t0 + k * 0.06, 0.15, 0.08)                           # impresora
        pon(K + "impact__2908-preview.mp3", t0 + 1.0, 0.5, 1.2)                                                     # sello
    if tp == "calendario":
        for k in range(0, 28, 4): pop(t0 + k * 0.03, 0.18)
        pon(K + "notification__2870-preview.mp3", S.at("no tiene ideas"), 0.35)
    if tp == "lista":
        for tc, _ in e["items"]: pop(tc, 0.42); pon(K + "click__1113-preview.mp3", tc + 0.05, 0.12, 0.2)
    if tp == "chat":
        for k in range(0, 56, 2): pon(K + "click__1660-preview.mp3", t0 + 0.5 + k / 28, 0.07, 0.06)                  # teclas
        pon(K + "swipe__707-preview.mp3", t0 + 2.6, 0.3)
        for j in range(3): pop(t0 + 2.8 + j * 0.3, 0.35)
    if tp == "tachado":
        for tc, _, tach in e["palabras"]:
            if tach: pon(K + "swipe__2627-preview.mp3", tc + 0.33, 0.4)
            else: pon(FR + "boom.mp3", tc, 0.6); pon(K + "sparkle__2603-preview.mp3", tc + 0.05, 0.2, 1.2)
    if tp == "meta": pon(K + "notification__2870-preview.mp3", t0 + 0.6, 0.3)
hh = carga("musica/upbeat_hiphop.mp3")[:L].copy()
hh *= 0.5 / np.abs(hh).max()
env = np.full(L, 0.30, np.float32)
tf = next(tc for tc, _, tach in next(e for e in S.ES if e["tipo"] == "tachado")["palabras"] if not tach)
env[int((tf - 0.45) * SR):int(tf * SR)] = 0.0                                   # silencio antes de «FUNCIONA»
k = int(0.05 * SR); env = np.convolve(env, np.ones(k) / k, "same"); hh *= env[:, None]
def guarda(n, x):
    w = wave.open(n, "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
guarda("fx_m.wav", fx); guarda("mus_m.wav", hh)
fc = ("[0:a]atrim=0:55,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9,aformat=channel_layouts=stereo,asplit=2[v][vs];"
      "[1:a][vs]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=350[m];[v][m][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.95[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "voz.wav", "-i", "mus_m.wav", "-i", "fx_m.wav", "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "mezcla_m.wav"], check=True)
print("ok")
