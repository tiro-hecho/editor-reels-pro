# Vídeo aprobado: efectos y juego de volúmenes. Al encenderse cada pesa: luz + su efecto mítico (malo / bueno / excelente).
#   uso: python3 sonido5.py [malo] [bueno] [excelente]   (nombres de ~/editor/proyecto/sfx/miticos)
import json, os, sys
exec(open("formato_c1.py").read().split("# subtítulos repartidos")[0])
V = json.load(open("encendidos.json"))
S = os.path.expanduser("~/editor/kit/4-efectos-sonido/"); X = os.path.expanduser("~/editor/proyecto/sfx/"); C = S + "escenas-creador/"; MI = X + "miticos/"
MALO, BUENO, TOP = (sys.argv[1:4] + ["malo1_buzzer", "bueno1_concurso", "top1_tada"][len(sys.argv[1:4]):])
EV = [[0.0, S + "impacto/golpe_seco.wav", -22]]
for k, (son, db) in enumerate(((MALO, -23), (BUENO, -20), (TOP, -19))):
    for t0, t1 in V[str(k)]: EV += [[t0, X + "switch_on.mp3", -18], [t0 + 0.03, MI + son + ".mp3", db]]
for b in BLOQ: EV += [[b["t0"] - 0.08, C + "swoosh2.mp3", -23]]
c0 = CTA["t0"]
EV += [[c0 - 0.08, C + "swoosh2.mp3", -23], [t_fin, S + "impacto/golpe_seco.wav", -20], [t_fin + 0.05, C + "boom.mp3", -24]]
json.dump(sorted(e for e in EV if e[0] < DUR - 0.05), open("eventos.json", "w"))
VOL = [[0.0, 0.6, 4]]
for b in BLOQ: VOL.append([b["t0"] - 0.35, b["t0"] + 0.15, 6])
for t0, t1 in V["2"]: VOL.append([t0, t0 + 0.6, 3])
VOL += [[c0 - 0.3, c0 + 0.02, -40], [t_fin, 40, 9]]
json.dump(VOL, open("volumen.json", "w")); print(len(EV), "efectos", MALO, BUENO, TOP)
