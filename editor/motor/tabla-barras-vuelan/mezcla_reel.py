# Mezcla del reel entero: voz igualada por trozo a -14,5 LUFS, jazz swing 15 dB debajo con sidechain, efectos Pixabay 2025-26.
import subprocess, re, json, wave, os, numpy as np
FF = "ffmpeg"; S = "recursos-descargados/efectos/"
PX = S; MUS = "recursos-descargados/musica/tu_cancion.mp3"
import reel as R
END = R.END
def lufs(f, extra=[]):
    o = subprocess.run([FF, "-hide_banner", *extra, "-i", f, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
INFO = json.load(open(PX + "info.json"))
C = []
def m(t, n, objetivo, alinea="pico"):
    """objetivo = nivel de sus 50 ms más fuertes en dBFS (todos los efectos igualados por cómo suenan de verdad)."""
    i = INFO[n]; off = i["pico_t"] if alinea == "pico" else i["inicio"]
    C.append((max(0, t - off), PX + n + ".mp3", round(objetivo - i["rms50_db"], 1)))
# sonido de subtítulo solo de vez en cuando (~cada 24 s) y en el instante en que la palabra cae con su rebote
for tw in (0.54, 15.34):
    for blk in R.BM:
        ws = blk["ws"]; j = next((j for j, x in enumerate(ws) if abs(x["s"] - tw) < .02), None)
        if j is None: continue
        t0 = min(ws[j]["s"] - .06, blk["s"] + j * .07); m(t0 + .073, "clic_button463065", -19, "inicio")
SND = {"lado": ["tr_swoosh014", "tr_swoosh026"], "vert": ["tr_swoosh023", "tr_swoosh014"], "zoom": ["tr_swoosh026"], "giro": ["tr_swoosh023"]}
for j, (T, tipo, d) in enumerate(R.TR):
    l = SND[tipo]; m(T, l[j % len(l)], -22)
for t0, s1, d in R.ZK:
    if d and s1 >= 1.25 : m(t0, "go_punch567196", -19, "inicio")
m(0.0, "go_punch567196", -17, "inicio")
for k in range(8): m(0.05 + .035 * k, "clic_tech481191", -30, "inicio")
for n_, (_, _, a, b, _) in enumerate(R.FILAS):
    for T in (a, b):
        m(T + R.ANT, "tr_swoosh014", -27, "inicio"); m(T + R.ANT + .14, "pop_clean467466" if T == a else "clic_softpop451232", -23, "inicio")
m(R.FILAS[-1][3] + R.ANT, "go_strike466320", -24, "inicio")
for k in range(5): m(R.T_OUT + .05 * k, "clic_tech481191", -32, "inicio")
C = sorted(x for x in C if x[0] < END - .05); print("efectos", len(C))
# voz igualada por trozo
w_ = wave.open("base16.wav"); x_ = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
CU = R.CORTES + [R.FIN_VOZ]; lv = []
for i in range(len(CU) - 1):
    seg = x_[int(CU[i] * 16000):int(CU[i + 1] * 16000)]; fr = seg[:len(seg) // 160 * 160].reshape(-1, 160); r = np.sqrt((fr ** 2).mean(1))
    r = r[r > np.percentile(r, 40)]; lv.append(20 * np.log10(np.sqrt((r ** 2).mean()) + 1e-9))
ref = float(np.median(lv)); gp = [max(-4, min(6, ref - l)) for l in lv]
eqv = ",".join(f"volume={10 ** (g / 20):.3f}:enable='between(t,{CU[i]:.3f},{CU[i+1]:.3f})'" for i, g in enumerate(gp))
subprocess.run([FF, "-y", "-v", "error", "-t", f"{R.FIN_VOZ}", "-i", "base.mov", "-vn", "-af", "highpass=f=70," + eqv, "-c:a", "pcm_s16le", "voz_eq.wav"], check=True)
# arranque de la canción: tramo con energía estable y golpes en los cortes
subprocess.run([FF, "-y", "-v", "error", "-i", MUS, "-ac", "1", "-ar", "22050", "mus22.wav"], check=True)
wm = wave.open("mus22.wav"); xm = np.frombuffer(wm.readframes(wm.getnframes()), np.int16).astype(np.float32) / 32768
hop = 256; nfr = (len(xm) - 1024) // hop; win = np.hanning(1024)
Sx = np.abs(np.fft.rfft(np.stack([xm[i * hop:i * hop + 1024] * win for i in range(nfr)]), axis=1)) ** .5
env = np.maximum(0, np.diff(Sx, axis=0)).sum(1); env = (env - env.mean()) / (env.std() + 1e-9); fe = 22050 / hop
rms = np.array([20 * np.log10(np.sqrt(np.mean(xm[i:i + 11025] ** 2)) + 1e-6) for i in range(0, len(xm) - 11025, 11025)])
cuts = np.array(R.CORTES[1:] + [a for a, *_ in R.BR]); best = (-1e9, 0)
for off in np.arange(0, len(xm) / 22050 - END - 1, .01):
    tramo = rms[int(off * 2):int((off + END) * 2)]
    if tramo.min() < rms.max() - 16: continue
    idx = ((off + cuts) * fe).astype(int); sc = sum(env[max(0, i - 2):i + 3].max() for i in idx if i + 3 < len(env))
    if sc > best[0]: best = (sc, off)
OFF = best[1]; print("arranque de la canción", round(OFF, 2))
gv = -14.5 - lufs("voz_eq.wav"); gm = -29.5 - lufs(MUS)
inp = ["-i", "voz_eq.wav", "-ss", f"{OFF:.2f}", "-i", MUS]
fc = [f"[0:a]volume={gv:.2f}dB,aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={END:.2f},asplit=2[voz][sc]",
      f"[1:a]atrim=0:{END:.2f},aresample=48000,aformat=channel_layouts=stereo,volume={gm:.2f}dB,afade=t=in:d=0.15,afade=t=out:st={END-1.0:.2f}:d=1.0[m0]",
      "[m0][sc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300[mus]"]
mix = ["[voz]", "[mus]"]
for k, (t, f, db) in enumerate(C):
    inp += ["-i", f]
    fc.append(f"[{k+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB,adelay={int(t*1000)}:all=1[s{k}]"); mix.append(f"[s{k}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95:level=false[a]")
open("fc_reel.txt", "w").write(";".join(fc))
subprocess.run([FF, "-y", "-v", "error", *inp, "-/filter_complex", "fc_reel.txt", "-map", "[a]", "-t", f"{END:.2f}", "-c:a", "pcm_s16le", "mezcla_reel.wav"], check=True)
print("mezcla LUFS", lufs("mezcla_reel.wav"))
