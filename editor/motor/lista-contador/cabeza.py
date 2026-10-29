# Posición de la cabeza en cada fotograma (desde la silueta): punto más alto de la persona y su centro -> cabeza.json (suavizado)
import os, json, numpy as np
from PIL import Image
fs = sorted(os.listdir("mascaras")); out = []
for f in fs:
    m = np.asarray(Image.open("mascaras/" + f).resize((270, 480))) > 128
    filas = np.where(m.sum(1) > 6)[0]
    if len(filas) == 0: out.append(out[-1] if out else (540, 900)); continue
    y0 = filas[0]; zona = m[y0:y0 + 40]; xs = np.where(zona.any(0))[0]
    out.append((float(xs.mean() * 4), float(y0 * 4)))
a = np.array(out); k = 9   # mediana + media para que no tiemble ni salte
pad = np.pad(a, ((k, k), (0, 0)), mode="edge"); s = np.array([np.median(pad[i:i + 2 * k + 1], 0) for i in range(len(a))]); s[:, 0] = np.clip(s[:, 0], 330, 750); s[:, 1] = np.clip(s[:, 1], 520, 1150); pad = np.pad(s, ((4, 4), (0, 0)), mode="edge"); s = np.array([pad[i:i + 9].mean(0) for i in range(len(s))])
json.dump([[round(x), round(y)] for x, y in s], open("cabeza.json", "w")); print(len(s), s[::60].astype(int).tolist())
