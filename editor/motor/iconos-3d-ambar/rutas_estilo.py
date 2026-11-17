# Rutas portables del estilo «iconos-3d-ambar» (Mac y Windows). Se trabaja siempre en la carpeta del proyecto.
import os, shutil
AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.normpath(os.path.join(AQUI, "..", ".."))
FUENTES = os.path.join(EDITOR, "assets", "fuentes")
EFECTOS = os.path.join(EDITOR, "assets", "efectos")
FF = shutil.which("ffmpeg") or "ffmpeg"
ANTON = os.path.join(FUENTES, "Anton-Regular.ttf")
INTER = os.path.join(FUENTES, "Inter[opsz,wght].ttf")
INTER_B = os.path.join(FUENTES, "Poppins-SemiBold.ttf")
# iconos: los de la carpeta del proyecto (iconos/*.png) o, si no, los de esta carpeta
ICONOS = os.path.join(os.getcwd(), "iconos") if os.path.isdir(os.path.join(os.getcwd(), "iconos")) else os.path.join(AQUI, "iconos")
# música: musica.mp3 en el proyecto, o la primera de editor/assets/musica
def _musica():
    p = os.path.join(os.getcwd(), "musica.mp3")
    if os.path.exists(p): return p
    d = os.path.join(EDITOR, "assets", "musica")
    ms = sorted(f for f in os.listdir(d) if f.endswith(".mp3")) if os.path.isdir(d) else []
    return os.path.join(d, ms[0]) if ms else None
MUSICA = _musica()
