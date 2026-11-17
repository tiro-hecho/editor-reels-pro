# -*- coding: utf-8 -*-
# v6: final en tipografía cinética apilada (sin lista): cada requisito grande en tinta con check 3D que cae;
# al entrar el siguiente, el anterior sube, encoge y se apaga. Remate «MÁNDANOS UN PRIVADO» en ámbar con bocadillo 3D.
import os, sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1, v2, v3, v4, v5
from v1 import W, H, FPS, CUT, wt, ease, eio, F, ANTON, paste_c, NF
from v2 import spring

def tinta(txt, size, maxw=900, col=(22, 22, 22)):
    f = F(ANTON, size); w = f.getlength(txt)
    if w > maxw: f = F(ANTON, int(size * maxw / w)); w = f.getlength(txt)
    bb = f.getbbox(txt); im = Image.new("RGBA", (int(w) + 20, bb[3] + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 6), txt, font=f, fill=col + (255,)); return im
TXT = [("DE CANTABRIA", "tinta"), ("TE GUSTA LA CÁMARA", "tinta"), ("MÁNDANOS UN PRIVADO", "ambar")]
T = [v1.PILLS[0][1], v1.PILLS[1][1], v1.PILLS[2][1]]
IMG = []
for s, kind in TXT:
    if kind == "tinta": IMG.append(tinta(s, 150, 600))
    else:
        IMG.append(tinta("MÁNDANOS UN", 110, 640))
PRIV = v2.letras("PRIVADO", 330, 780)
SLOT = [(640, 1.0, 1.0), (470, 0.58, 0.38), (360, 0.42, 0.18)]   # (y, escala, opacidad) actual / anterior / más antigua
def estado(n, t):
    """posición interpolada del renglón n según cuántos han entrado después"""
    later = [T[m] for m in range(n + 1, len(T)) if t >= T[m]]
    s0 = SLOT[min(len(later), 2)]
    if not later: return s0
    p = spring((t - later[-1]) / 0.32); prev = SLOT[min(len(later) - 1, 2)]
    return tuple(prev[i] + (s0[i] - prev[i]) * min(1.05, p) for i in range(3))

def escena_e(frame, t):
    out = frame.convert("RGBA")
    v = np.zeros((H, W, 4), np.uint8); yy = np.linspace(0, 1, H)[:, None]
    v[..., :3] = 248; v[..., 3] = (np.clip(1 - yy / 0.45, 0, 1) ** 1.6 * 120 * min(1, (t - CUT[4]) / 0.3)).astype(np.uint8)
    out.alpha_composite(Image.fromarray(v, "RGBA")); out.alpha_composite(v1.GRAD)
    for n in range(len(T)):
        d = t - T[n]
        if d < 0: continue
        y, sc, al = estado(n, t); im = IMG[n]
        if n == 2: y = 600
        # entrada: sube desde abajo con desenfoque vertical y escala 1.25 -> 1
        p = ease(d / 0.26)
        e = 1.25 - 0.25 * p
        x = 540 if n == 2 else 540 - 50 * sc
        lay = im if p >= 1 else im.filter(ImageFilter.GaussianBlur(8 * (1 - p)))
        paste_c(out, lay, x, y + (1 - p) * 70, sc * e, al * min(1, p * 1.6))
        if n < 2:
            # check 3D que cae a la derecha del renglón y aplasta al aterrizar
            dc = d - 0.16
            if dc > 0:
                pc = ease(dc / 0.22); xr = x + im.width * sc / 2 + 75 * sc; s_ = 52 * sc
                pts = [(xr - s_, y), (xr - s_ * 0.3, y + s_ * 0.7), (xr + s_, y - s_ * 0.8)]
                L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); Lt = (L1 + L2) * pc
                cl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(cl); wd = max(6, int(20 * sc))
                col = (255, 186, 38, int(255 * al))
                if Lt <= L1:
                    q = Lt / L1; dd.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * q, pts[0][1] + (pts[1][1] - pts[0][1]) * q)], fill=col, width=wd, joint="curve")
                else:
                    q = (Lt - L1) / L2; dd.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * q, pts[1][1] + (pts[2][1] - pts[1][1]) * q)], fill=col, width=wd, joint="curve")
                for pp in pts[:1]: dd.ellipse((pp[0] - wd / 2, pp[1] - wd / 2, pp[0] + wd / 2, pp[1] + wd / 2), fill=col)
                out.alpha_composite(v1.glow(cl.crop((int(xr - 120), int(y - 120), int(xr + 120), int(y + 120))), 10, (255, 180, 30), 0.5), (int(xr - 120 - 30), int(y - 120 - 30)))
                out.alpha_composite(cl)
        else:
            # remate: bocadillo 3D que sale disparado y queda flotando
            dc = d - 0.12
            if dc > 0:
                k = v3.pop_k(dc); ry, rx = v4.giro(dc, t, 5)
                ob = v4.obj3d(v4.plano_ico("chat", 190), ry, rx, depth=18)
                paste_c(out, ob, 820 - 60 * (1 - min(1, dc / .3)), 330 + 8 * math.sin(t * 3), max(.01, k), min(1, k * 1.5))
    return out
v5.escena_e = escena_e

def render(i):
    t = i / FPS
    if v1.tramo(t) != 4: return v5.render(i)
    fr = Image.open(f"fr/{i+1:04d}.jpg").convert("RGB"); cx, cy, _ = v1.cara(i); z = 1.06; sw, sh = W / z, H / z
    x0 = min(max(cx - sw / 2, 0), W - sw); y0 = min(max(cy - sh * 0.50, 0), H - sh); box = (int(x0), int(y0), int(x0 + sw), int(y0 + sh))
    f2 = fr.crop(box).resize((W, H), Image.LANCZOS); out = escena_e(f2, t)
    a = T[2] + 0.18
    if t >= a:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); v2.GL["PRIVADO"] = PRIV; v2.palabra(lay, "PRIVADO", t, a, 540, 810); out.alpha_composite(lay)
        mk = Image.open(f"mk/{i+1:04d}.png").convert("L").crop(box).resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.2))
        per = f2.convert("RGBA"); per.putalpha(mk); out.alpha_composite(per)
    return v4.transicion(out, t)

if __name__ == "__main__":
    pass  # se trabaja en la carpeta del proyecto (la actual)
    if len(sys.argv) > 1 and sys.argv[1] == "fotos":
        os.makedirs("prev", exist_ok=True)
        for s in [float(x) for x in sys.argv[2:]]: render(int(s * FPS)).convert("RGB").save(f"prev/p_{s:05.2f}.jpg", quality=88)
        sys.exit()
    p = subprocess.Popen([v1.FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "video.mp4"], stdin=subprocess.PIPE)
    for i in range(NF):
        p.stdin.write(render(i).convert("RGB").tobytes())
        if i % 60 == 0: print(i, NF, flush=True)
    p.stdin.close(); p.wait(); print("video ok")
