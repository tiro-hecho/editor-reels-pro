import os, sys
from PIL import Image, ImageDraw
pass  # se trabaja en la carpeta del proyecto (la actual)
fs = sorted(f for f in os.listdir("prev") if f.startswith("p_"))
w, h = 360, 640; cols = min(len(fs), 8); rows = (len(fs) + cols - 1) // cols
s = Image.new("RGB", (w * cols, (h + 30) * rows))
for i, f in enumerate(fs):
    im = Image.open("prev/" + f).resize((w, h)); s.paste(im, ((i % cols) * w, (i // cols) * (h + 30)))
    ImageDraw.Draw(s).text(((i % cols) * w + 6, (i // cols) * (h + 30) + h + 6), f, fill=(255, 255, 0))
s.save(sys.argv[1] if len(sys.argv) > 1 else "hoja.jpg", quality=85)
