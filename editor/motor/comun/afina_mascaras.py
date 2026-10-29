# Afina las siluetas: borde firme sin halo, 1-2 px hacia dentro (nada de fondo pegado) y huecos pequeños rellenos (manos, asas).
# NO mezcla fotogramas vecinos: cuando la persona se mueve, eso deja halo. mascaras_u2net/ -> mascaras/
import os, numpy as np, cv2
W, H = 1080, 1920
os.makedirs("mascaras", exist_ok=True)
fs = sorted(f for f in os.listdir("mascaras_u2net") if f.endswith(".png"))
for f in fs:
    m = cv2.imread(os.path.join("mascaras_u2net", f), 0).astype(np.float32) / 255
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    hb = (m < 0.5).astype(np.uint8); k_, lab, st, _ = cv2.connectedComponentsWithStats(hb, 4)
    for j in range(1, k_):                                           # hueco cerrado y pequeño = error del recorte
        x, y, w_, h_, area = st[j]
        if area < 3000 and x > 0 and y > 0 and x + w_ < W and y + h_ < H: m[lab == j] = 1
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    m = np.clip((m - 0.55) * 5 + 0.5, 0, 1)
    m = cv2.erode(m, np.ones((3, 3), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 0.8)
    cv2.imwrite(os.path.join("mascaras", f), (m * 255).astype(np.uint8))
print("afinadas", len(fs))
