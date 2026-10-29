# Vídeo aprobado: corte limpio desde ../j/base.mov — quita el «sí» del arranque, el «ya» y el arranque trabado del hombro,
# los ratos quietos sin voz (peso muerto, sentadilla, remo) y el final sobrante; mete un avance de 1,5 s con los 5 ejercicios
# delante, congela cada repetición mala/buena 0,8 s y deja cola para la tarjeta final.
import json, subprocess
J = "../j/"; BASE = J + "base.mov"; P = json.load(open(J + "plan.json"))
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout)
D0 = dur(BASE)
QUITA = [(0.0, 0.75), (7.83, 8.50), (13.38, 14.1667), (17.757, 19.357), (22.757, 23.657), (33.457, 35.057), (37.857, 41.1333)]
PUNTOS = [2.12, 4.5, 9.95, 12.9, 16.9, 20.85, 25.7, 28.7, 33.0, 37.5]          # congelados (tiempo de ../j)
AVANCE = []; PASO = 0.3; AV = 0.0   # 0,3 s de cada ejercicio
D = 0.8; COLA = 1.6
WD = P["palabras"]
def libre(t):
    for w in WD:
        if w["s"] - 0.03 < t < w["e"] + 0.03: return round(w["e"] + 0.04, 3)
    return t
PUNTOS = [libre(t) for t in PUNTOS]
for p in PUNTOS: assert not any(a <= p < b for a, b in QUITA), p
ENC = ["-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1"]
def ff(a): subprocess.run(["ffmpeg", "-v", "error", "-y"] + a, check=True)
piezas = []; n = 0
def pieza(args):
    global n; o = f"p/{n:03d}.mov"; ff(args + ENC + [o]); piezas.append(o); n += 1
for t in AVANCE:   # avance sin voz
    pieza(["-ss", f"{t:.3f}", "-i", BASE, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-map", "0:v", "-map", "1:a", "-t", str(PASO), "-r", "30"])
# tramos que se quedan, partidos por los congelados
cortes = sorted(set([0.0, D0] + [x for ab in QUITA for x in ab] + PUNTOS))
for a, b in zip(cortes, cortes[1:]):
    if b - a < 0.01 or any(qa <= a < qb for qa, qb in QUITA): continue
    pieza(["-ss", f"{a:.3f}", "-i", BASE, "-t", f"{b - a:.3f}", "-r", "30"])
    if any(abs(b - p) < 1e-6 for p in PUNTOS):
        ff(["-ss", f"{b - 0.02:.3f}", "-i", BASE, "-frames:v", "1", "p/f.png"])
        pieza(["-loop", "1", "-framerate", "30", "-i", "p/f.png", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(D)])
ff(["-sseof", "-0.1", "-i", BASE, "-frames:v", "1", "p/ult.png"])
pieza(["-loop", "1", "-framerate", "30", "-i", "p/ult.png", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(COLA)])
open("p/l.txt", "w").write("".join(f"file '{x[2:]}'\n" for x in piezas))
ff(["-f", "concat", "-safe", "0", "-i", "p/l.txt", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "base.mov"])
ff(["-i", "base.mov", "-vn", "-ac", "1", "-ar", "48000", "base.wav"])
DUR = dur("base.mov")
def nt(t):   # tiempo de ../j -> tiempo final
    if any(a <= t < b for a, b in QUITA): return None
    return AV + t - sum(b - a for a, b in QUITA if b <= t) + D * sum(1 for p in PUNTOS if p <= t)
def nt_ok(t):
    while nt(t) is None: t += 0.001
    return nt(t)
CORTES = [7.83, 13.38, 22.7, 29.5, 37.857]
TR = P["tramos"]
for i, c in enumerate(CORTES): TR[i]["t1"] = c; TR[i + 1]["t0"] = c
TR[0]["t0"] = 0.0
for tr in TR: tr["t0"] = round(nt_ok(tr["t0"]), 3); tr["t1"] = round(nt_ok(tr["t1"] - 0.001), 3)
TR[0]["t0"] = AV; TR[-1]["t1"] = DUR
W = [dict(w=w["w"], s=round(nt(w["s"]), 3), e=round(nt(w["e"]), 3)) for w in WD if nt(w["s"]) is not None and nt(w["e"]) is not None]
FRZ = [round(nt(p) - D, 3) for p in PUNTOS]
json.dump(dict(dur=round(DUR, 3), tramos=TR, palabras=W, frz=FRZ, D=D, cola=COLA, avance=AV), open("plan.json", "w"), ensure_ascii=False)
print("dur", round(DUR, 2), "tramos", [(t["blq"], t["t0"]) for t in TR], "congelados", FRZ)
