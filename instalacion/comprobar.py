# Comprueba que el ordenador está listo para editar: ffmpeg, transcripción, capas HTML con Chrome/Edge y recorte de persona.
#   uso (con el Python del editor):  Mac  .venv/bin/python instalacion/comprobar.py   ·   Windows  .venv\Scripts\python instalacion\comprobar.py
import json, os, shutil, subprocess, sys, tempfile, traceback
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMUN = os.path.join(RAIZ, "editor", "motor", "comun"); sys.path.insert(0, COMUN)
import rutas                                # pone en el PATH el ffmpeg portátil si lo hay y arregla los acentos en Windows
tmp = tempfile.mkdtemp(prefix="comprobar_"); fallos = 0

def paso(nombre, f):
    global fallos
    try: f(); print(f"OK     {nombre}")
    except Exception as e: fallos += 1; print(f"FALLA  {nombre}: {e}"); traceback.print_exc(limit=1)

def video():
    ff = shutil.which("ffmpeg") or (_ for _ in ()).throw(RuntimeError("no encuentro ffmpeg (reinicia Claude si lo acabas de instalar)"))
    shutil.which("ffprobe") or (_ for _ in ()).throw(RuntimeError("no encuentro ffprobe"))
    subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=1080x1920:rate=30", "-f", "lavfi", "-i", "sine=f=440",
                    "-t", "3", "-pix_fmt", "yuv420p", "-shortest", os.path.join(tmp, "p.mp4")], check=True)
    subprocess.run([ff, "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=black:s=64x64,format=gbrpf32le,zscale=t=linear", "-frames:v", "1",
                    os.path.join(tmp, "z.png")], check=True)   # el tonemapping HDR del iPhone necesita zscale

def transcripcion():
    from faster_whisper import WhisperModel
    from rutas import MODELOS
    WhisperModel("small", device="cpu", compute_type="int8", download_root=os.path.join(MODELOS, "whisper"))   # la primera vez descarga ~460 MB

def capa_html():
    html = os.path.join(tmp, "p.html")
    open(html, "w").write("<html><body style='margin:0;background:transparent'><div id=x style='font:80px sans-serif;color:#fff'>OK</div>"
                          "<script>window.setT=t=>{document.getElementById('x').style.opacity=1}</script></body></html>")
    subprocess.run([sys.executable, os.path.join(COMUN, "render_html.py"), html, os.path.join(tmp, "capa"), "0.1", "10"], check=True, timeout=180)
    assert os.listdir(os.path.join(tmp, "capa")), "no salió ningún fotograma"

def recorte():
    from rutas import MODELOS
    os.environ.setdefault("U2NET_HOME", MODELOS)
    from rembg import new_session
    new_session("u2net_human_seg")                                                                            # la primera vez descarga ~170 MB

def recursos():
    from rutas import MIT, MUS
    falta = [p for p in (os.path.join(MIT, "malo1_corto.mp3"), os.path.join(MUS, "vlog_hiphop.mp3")) if not os.path.exists(p)]
    assert not falta, "faltan la música y los efectos: ejecuta editor/motor/comun/descargar_recursos.py"

for n, f in [("vídeo (ffmpeg y HDR)", video), ("transcripción (Whisper)", transcripcion), ("gráficos (Chrome/Edge)", capa_html),
             ("recorte de la persona", recorte), ("música y efectos descargados", recursos)]:
    paso(n, f)
shutil.rmtree(tmp, ignore_errors=True)
print("\nTODO_OK" if not fallos else f"\n{fallos} cosa(s) por arreglar")
sys.exit(1 if fallos else 0)
