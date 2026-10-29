# Rutas comunes del editor: todo relativo a la carpeta del alumno, igual en Mac y en Windows.
#   Los estilos hacen `from rutas import *` (montar.py pone esta carpeta en el PYTHONPATH).
import os, shutil, sys
for _s in (sys.stdout, sys.stderr):          # Windows: que los acentos y símbolos no rompan los mensajes
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

COMUN = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.dirname(os.path.dirname(COMUN))                 # .../editor
RAIZ = os.path.dirname(EDITOR)                                    # carpeta que abrió el alumno
F = os.path.join(EDITOR, "assets", "fuentes")                     # fuentes libres (Inter, Anton, Montserrat…)
EF = os.path.join(EDITOR, "assets", "efectos") + os.sep           # efectos libres que vienen en el repositorio (Kenney y propios)
DESCARGAS = os.path.join(RAIZ, "recursos-descargados")            # lo que no se puede redistribuir y se baja al instalar
MIT = os.path.join(DESCARGAS, "efectos", "miticos") + os.sep      # malo / bueno / perfecto
ESC = os.path.join(DESCARGAS, "efectos", "escenas") + os.sep      # whoosh, pop, ding, riser, boom…
PX = os.path.join(DESCARGAS, "efectos", "pixabay") + os.sep       # pack de efectos variados
MUS = os.path.join(DESCARGAS, "musica") + os.sep
MODELOS = os.path.join(DESCARGAS, "modelos")
MI, Cs, S_ = MIT, ESC, EF                                         # nombres que usan los motores antiguos

def url(p):
    """ruta local -> file:///… válido en Mac y en Windows (en CSS, una ruta con barras invertidas no funciona)"""
    from pathlib import Path
    return Path(os.path.abspath(p)).as_uri()

# Tipografías: Helvetica Neue es de pago y no existe en Windows; en su lugar, libres y casi iguales.
#   HB = titular/subtítulo (Inter Bold) · HM = texto medio (Inter Medium) · HCB/HCO = condensada gorda (Anton)
#   Inter es variable: el rango fijo de font-weight hace que Chrome la pinte con ese grosor aunque el CSS pida «normal».
_INTER, _ANTON = url(os.path.join(F, "Inter[opsz,wght].ttf")), url(os.path.join(F, "Anton-Regular.ttf"))
FUENTES_CSS = (f"@font-face{{font-family:HB;src:url('{_INTER}');font-weight:700 700}}"
               f"@font-face{{font-family:HM;src:url('{_INTER}');font-weight:500 500}}"
               f"@font-face{{font-family:HCB;src:url('{_ANTON}')}}"
               f"@font-face{{font-family:HCO;src:url('{_ANTON}')}}")

# ffmpeg del sistema o, si no hay, el portátil que deja el instalador en herramientas/ffmpeg (Windows sin winget)
_PORTATIL = os.path.join(RAIZ, "herramientas", "ffmpeg", "bin")
if os.path.isdir(_PORTATIL) and _PORTATIL not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _PORTATIL + os.pathsep + os.environ.get("PATH", "")      # así también lo encuentran los subprocesos

def ffmpeg():
    return shutil.which("ffmpeg") or sys.exit("Falta ffmpeg: escribe /empezar para instalarlo.")

def ffprobe():
    return shutil.which("ffprobe") or sys.exit("Falta ffprobe (viene con ffmpeg): escribe /empezar para instalarlo.")
