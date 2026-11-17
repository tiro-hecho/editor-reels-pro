# -*- coding: utf-8 -*-
# v5: halo de las palabras sin recortes (relleno alrededor) + final rediseñado sin pastillas ni tarjeta:
# él a pantalla completa y lista limpia sobre la pared (icono 3D + texto tinta + clave en ámbar), revelado desde abajo.
import os, sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v1, v2, v3, v4
from v1 import W, H, FPS, CUT, wt, ease, eio, F, HNM, ANTON, paste_c, NF

def glow(im, rad=18, col=(255, 190, 40), k=0.55):
    p = int(rad * 3); big = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0)); big.alpha_composite(im, (p, p))
    a = big.split()[3].filter(ImageFilter.GaussianBlur(rad))
    g = Image.new("RGBA", big.size, col + (0,)); g.putalpha(a.point(lambda v: int(v * k)))
    return g
v1.glow = glow
_gl = {}
def letras_pad(txt, size, maxw):
    ls, tw = v2.letras(txt, size, maxw)
    out = []
    for im, x in ls:
        if im is None: out.append((None, x)); continue
        # quitar el margen de grad_text para que no quede caja; el glow ya lleva relleno propio
        out.append((im, x))
    return out, tw
for g in v3.GIG: v2.GL[g[0]] = letras_pad(g[0], 260 if g[3] == "detras" else 230, 780)  # zona segura x 66-934

# ---------- final nuevo ----------
LIN = [("pin", "Eres de ", "CANTABRIA", v1.PILLS[0][1]), ("camara", "Te gusta hablar a ", "CÁMARA", v1.PILLS[1][1]), ("chat", "Mándanos un ", "PRIVADO", v1.PILLS[2][1])]
FN = F(HNM, 56); TINTA = (20, 20, 20, 255)
def linea_img(pre, clave):
    gk = v1.grad_text(clave, 98)
    w = int(FN.getlength(pre)) + gk.width + 10; h = 160
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((0, 112), pre, font=FN, fill=TINTA, anchor="ls")
    im.alpha_composite(gk, (int(FN.getlength(pre)) - 14, 112 - gk.height + 22))
    return im
LIM = [linea_img(p, c) for _, p, c, _ in LIN]
def escena_e(frame, t):
    out = frame.convert("RGBA"); lt = t - CUT[4]
    # velo blanco muy suave arriba para leer la tinta sobre la pared
    v = np.zeros((H, W, 4), np.uint8); yy = np.linspace(0, 1, H)[:, None]
    v[..., :3] = 250; v[..., 3] = (np.clip(1 - yy / 0.42, 0, 1) ** 1.5 * 150 * min(1, lt / 0.3)).astype(np.uint8)
    out.alpha_composite(Image.fromarray(v, "RGBA")); out.alpha_composite(v1.GRAD)
    for n, ((ic, _, _, a), im) in enumerate(zip(LIN, LIM)):
        d = t - a
        if d < 0: continue
        y = 300 + n * 140; x0 = 165
        p = ease(d / 0.28)
        # revelado desde abajo: recorte que sube
        hh = int(im.height * p);
        if hh > 0:
            cut = im.crop((0, im.height - hh, im.width, im.height))
            out.alpha_composite(cut, (x0, int(y - im.height / 2 + (im.height - hh) + (1 - p) * 30)))
        # icono 3D
        k = v3.pop_k(d); ry, rx = v4.giro(d, t, n)
        ob = v4.obj3d(v4.plano_ico(ic, 104), ry, rx, depth=12)
        paste_c(out, ob, 105, y + 14 + 4 * math.sin(t * 3 + n), max(.01, k), min(1, k * 1.5))
    return out
v1.escena_e = escena_e
_st = v4.sticker
def sticker(lay, t, n, *a):
    if n == "sobre": return
    _st(lay, t, n, *a)

def render(i):
    v3.sticker, v3.caida, v3.cascada, v3.billetes = sticker, v4.caida, v4.cascada, v4.billetes
    v2.transicion = lambda tt: 0
    t = i / FPS
    if v1.tramo(t) == 4:
        fr = Image.open(f"fr/{i+1:04d}.jpg").convert("RGB"); cx, cy, _ = v1.cara(i); z = 1.06; sw, sh = W / z, H / z
        x0 = min(max(cx - sw / 2, 0), W - sw); y0 = min(max(cy - sh * 0.50, 0), H - sh)
        return v4.transicion(escena_e(fr.crop((int(x0), int(y0), int(x0 + sw), int(y0 + sh))).resize((W, H), Image.LANCZOS), t), t)
    return v4.transicion(v3.render(i), t)

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
