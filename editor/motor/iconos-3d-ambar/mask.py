import os, json, numpy as np
from PIL import Image
from rembg import remove, new_session
pass  # se trabaja en la carpeta del proyecto (la actual)
os.makedirs("mk", exist_ok=True); ses = new_session("u2net_human_seg")
caras = {}; log = open("mask.log", "w")
for f in sorted(os.listdir("fr")):
    o = "mk/" + f.replace(".jpg", ".png")
    if not os.path.exists(o):
        sm = Image.open("fr/" + f).resize((540, 960))
        remove(sm, session=ses, only_mask=True).resize((1080, 1920), Image.BILINEAR).save(o)
    m = np.array(Image.open(o)) > 128
    rows = np.where(m.sum(1) > 20)[0]
    if len(rows):
        top = rows[0]; band = m[top:top + 330]; xs = np.where(band.any(0))[0]
        w = int(np.percentile(np.where(m[top + 200:top + 330].any(0))[0], 95) - np.percentile(np.where(m[top + 200:top + 330].any(0))[0], 5)) if m[top+200:top+330].any() else 260
        cx = int(np.where(m[top + 120:top + 260])[1].mean()) if m[top+120:top+260].any() else 540
        caras[f] = [int(cx - w // 2), int(top + 40), int(w), int(w)]
    log.write(f + "\n"); log.flush()
json.dump(caras, open("caras.json", "w")); log.write("FIN\n")
