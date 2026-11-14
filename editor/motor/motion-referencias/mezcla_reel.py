# Mezcla del reel 6: voz a -14,5 LUFS igualada por trozo, jazz 15 dB debajo con sidechain, cada gráfico con su sonido.
import subprocess, re, json, wave, numpy as np, glob
FF = r"C:\Users\team\herr\ffmpeg\bin\ffmpeg.exe"; PX = r"C:\Users\team\mp14\brutos1311\efectos\pixabay2026" + "\\"
MUS = r"C:\Users\team\mp14\brutos1311\musica\jazz_midnightclub568167.mp3"
import reel as R
END = R.END
def lufs(f):
    o = subprocess.run([FF, "-hide_banner", "-i", f, "-vn", "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])
INFO = json.load(open(PX + "info.json")); C = []
def m(t, n, db, al="inicio"):
    i = INFO[n]; off = i["pico_t"] if al == "pico" else i["inicio"]; C.append((max(0, t - off), PX + n + ".mp3", round(db - i["rms50_db"], 1)))
for _, G0, G1 in R.GL:
    m(G0, "gl_effect1_397982", -17); m(G0, "go_punch567196", -21); m(G0 + .95, "gl_effect1_397982", -25); m(G1 - .22, "gl_cinematic_trans", -22)
    for k in range(4): m(G0 + .12 + .09 * k, "clic_tech481191", -31)
for i, (_, t0) in enumerate(R.MC): m(t0, "go_strike466320" if i == 0 else "clic_retro514601", -22 if i == 0 else -20); m(t0 + .03, "pop_sharp328170", -27)
m(R.MV0, "tr_swoosh023", -24); m(R.MV0 + .1, "holo_appear546562", -27)
for _, _, P0, P1 in R.POS: m(P0, "go_cine352702", -21)
for T in R.T_CURSOR:
    m(T - R.CUR_PRE + .18, "clic_mouse351398", -18); m(T - .02, "clic_mouse366460", -19); m(T + .02, "tr_air352049", -26)
for T in R.T_OFFSET: m(T - R.OFF_D / 2, "wh_velocity383019", -21); m(T + .05, "go_powercine454852", -24)
for T in R.CUTS[1:-1]:
    if T not in R.T_CURSOR and T not in R.T_OFFSET: m(T - .12, "tr_swoosh014", -27)
ts = np.arange(R.R0, R.R1, 1 / 120); pv = np.array([R.pos_rueda(t) for t in ts]); last = -9
for t, a, b in zip(ts[1:], pv[:-1], pv[1:]):
    if np.floor(a + .5) != np.floor(b + .5) and t - last > .05: m(t, "clic_softpop451232", -29); last = t
m(R.R1 - .5, "pop_clean467466", -21)
m(R.OR0, "tr_swoosh026", -23); m(R.OR0 + .3, "holo_futuristic", -29)
for e, E0, E1, *_ in R.EMO: m(E0, "pop_423717", -20)
for _, _, _, _, t0 in R.BARRAS: m(t0, "tr_riser390289" if False else "clic_scifi596258", -24)
m(R.BARRAS[2][4] + .5, "go_strike466320", -24)
C = sorted(x for x in C if x[0] < END - .05); print("efectos", len(C))
w_ = wave.open("base16.wav"); x_ = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).astype(np.float32) / 32768
CU = R.CUTS; lv = []
for i in range(len(CU) - 1):
    seg = x_[int(CU[i] * 16000):int(CU[i + 1] * 16000)]; fr = seg[:len(seg) // 160 * 160].reshape(-1, 160); r = np.sqrt((fr ** 2).mean(1))
    r = r[r > np.percentile(r, 40)]; lv.append(20 * np.log10(np.sqrt((r ** 2).mean()) + 1e-9))
ref = float(np.median(lv)); gp = [max(-4, min(6, ref - l)) for l in lv]
eqv = ",".join(f"volume={10 ** (g / 20):.3f}:enable='between(t,{CU[i]:.3f},{CU[i+1]:.3f})'" for i, g in enumerate(gp))
subprocess.run([FF, "-y", "-v", "error", "-i", "base.mov", "-vn", "-af", "highpass=f=70," + eqv, "-c:a", "pcm_s16le", "voz_eq.wav"], check=True)
gv = -14.5 - lufs("voz_eq.wav"); gm = -29.5 - lufs(MUS); OFF = 79.47
inp = ["-i", "voz_eq.wav", "-ss", f"{OFF:.2f}", "-i", MUS]
fc = [f"[0:a]volume={gv:.2f}dB,aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={END:.2f},asplit=2[voz][sc]",
      f"[1:a]atrim=0:{END:.2f},aresample=48000,aformat=channel_layouts=stereo,volume={gm:.2f}dB,afade=t=in:d=0.15,afade=t=out:st={END-1.0:.2f}:d=1.0[m0]",
      "[m0][sc]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=300[mus]"]
mix = ["[voz]", "[mus]"]
for k, (t, f, db) in enumerate(C):
    inp += ["-i", f]; fc.append(f"[{k+2}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB,adelay={int(t*1000)}:all=1[s{k}]"); mix.append(f"[s{k}]")
fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.95:level=false[a]")
open("fc.txt", "w").write(";".join(fc))
subprocess.run([FF, "-y", "-v", "error", *inp, "-/filter_complex", "fc.txt", "-map", "[a]", "-t", f"{END:.2f}", "-c:a", "pcm_s16le", "mezcla.wav"], check=True)
print("mezcla LUFS", lufs("mezcla.wav"))
tr = sorted(glob.glob("trozo_*.mp4")); open("trozos.txt", "w").write("".join(f"file '{t}'\n" for t in tr))
subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "trozos.txt", "-i", "mezcla.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", "reel6.mp4"], check=True)
subprocess.run([FF, "-y", "-v", "error", "-i", "reel6.mp4", "-c:v", "libx264", "-crf", "25", "-preset", "slow", "-c:a", "aac", "-b:a", "160k", "reel6_movil.mp4"], check=True)
subprocess.run([FF, "-y", "-v", "error", "-i", "reel6.mp4", "-ac", "1", "-ar", "16000", "final16.wav"], check=True)
from faster_whisper import WhisperModel
w = wave.open("final16.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
sg, _ = WhisperModel('large-v3', device='cpu', compute_type='int8', cpu_threads=12).transcribe(a, language='es', condition_on_previous_text=False)
print("FINAL:", " ".join(s.text.strip() for s in sg))
