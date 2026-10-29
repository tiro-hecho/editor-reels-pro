# Vídeo aprobado definitivo: sobre el corte limpio (corte.mov, planos de ejercicio enteros) mete el congelado de la sentadilla mala
# y la repetición a cámara lenta de la buena; prepara los B-roll (gancho y foto del centro) y las palabras en tiempo final.
import json, subprocess, os, glob
FPS = 30; PL = json.load(open("plan.json")); TR = PL["tramos"]; DUR0 = PL["dur"]
T_FRZ, D_FRZ = round(TR[1]["t0"] + (5.84 - 2.00) / 1.07, 3), 0.9
T_SLOW, RAW_A, RAW_B, VEL_S, RAW_FONDO = TR[2]["t1"], 6.30, 7.70, 0.5, 7.45
D_SLOW = (RAW_B - RAW_A) / VEL_S
TONO = "zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=1080:1920:flags=lanczos"
def raw(c): return glob.glob(os.path.expanduser(f"~/editor/brutos/**/IMG_{c}.MOV"), recursive=True)[0]
ENC = ["-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1"]
def tramo(a, b, o): subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", "corte.mov", "-t", f"{b - a:.3f}", "-r", "30"] + ENC + [o], check=True)
os.makedirs("p", exist_ok=True)
tramo(0, T_FRZ, "p/0.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{T_FRZ - 0.02:.3f}", "-i", "corte.mov", "-frames:v", "1", "p/frz.png"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", "p/frz.png", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(D_FRZ)] + ENC + ["p/1.mov"], check=True)
tramo(T_FRZ, T_SLOW, "p/2.mov")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{RAW_A:.3f}", "-t", f"{RAW_B - RAW_A:.3f}", "-i", raw("4298"), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                "-vf", f"{TONO},fps=60,setpts=PTS/{VEL_S},minterpolate=fps=30:mi_mode=blend", "-map", "0:v", "-map", "1:a", "-t", f"{D_SLOW:.3f}"] + ENC + ["p/3.mov"], check=True)
tramo(T_SLOW, DUR0, "p/4.mov")
open("p/l.txt", "w").write("".join(f"file '{i}.mov'\n" for i in range(5)))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "p/l.txt", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "base.mov"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "base.mov", "-vn", "-ac", "1", "-ar", "48000", "base.wav"], check=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "base.mov"], capture_output=True, text=True).stdout)
def nt(t): return t if t < T_FRZ else t + D_FRZ if t < T_SLOW else t + D_FRZ + D_SLOW
# B-roll: gancho (la sentadilla mala, sin voz) y foto del interior del centro con empuje lento
os.makedirs("broll", exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "4.70", "-t", "1.4", "-i", raw("4297"), "-vf", f"{TONO},fps=30", "-an", "-c:v", "libx264", "-crf", "16", "broll/gancho.mp4"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", os.path.expanduser("~/editor/fotos/sede1_interior.jpg"), "-t", "2",
                "-vf", "scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z='1+0.0015*on':d=60:s=1080x1920:fps=30", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "broll/centro.mp4"], check=True)
FIX = {0: list(zip("No hagas esto si quieres unas piernas fuertes.".split(), [(0, .5), (.52, .72), (.72, .92), (.92, 1.08), (1.08, 1.26), (1.26, 1.42), (1.42, 1.76), (1.76, 2.1)]))}
W = []
for i, tr in enumerate(TR):
    ws = [dict(w=t, s=s, e=e) for t, (s, e) in FIX[i]] if i in FIX else json.load(open(f"seg{i:02d}.json"))
    for w in ws:
        W.append(dict(w=w["w"].replace("Cantabre", "Cantabria"), s=round(nt(tr["t0"] + w["s"]), 3), e=round(nt(tr["t0"] + w["e"]), 3)))
INS = dict(frz=[T_FRZ, T_FRZ + D_FRZ], slow=[nt(T_SLOW) - D_SLOW, nt(T_SLOW)], fondo_slow=nt(T_SLOW) - D_SLOW + (RAW_FONDO - RAW_A) / VEL_S,
           tramos=[nt(t["t0"]) for t in TR])
json.dump(dict(dur=round(dur, 3), ins=INS, tramos=TR), open("plan.json", "w")); json.dump(W, open("palabras.json", "w"), ensure_ascii=False)
print("dur", round(dur, 2), INS)
