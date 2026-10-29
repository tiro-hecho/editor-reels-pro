# Monta un vídeo de principio a fin con el motor de su estilo. Igual en Mac y en Windows (sin bash).
#   uso: python editor/motor/comun/montar.py <carpeta_del_proyecto> [--desde PASO]
#   La carpeta del proyecto tiene montaje.json (tramos, estilo, música) y el formato del estilo copiado como formato.py.
#   Pasos: transcribir -> cortar -> siluetas (si hay gráficos detrás) -> formato -> capas -> componer -> mezcla -> revisión
#   Se puede repetir: cada paso se salta si ya está hecho y no ha cambiado lo anterior.
import glob, json, os, shutil, subprocess, sys, time
COMUN = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, COMUN)
from rutas import ffmpeg, MUS
PY = sys.executable
proyecto = os.path.abspath(sys.argv[1]); os.chdir(proyecto)
DESDE = sys.argv[sys.argv.index("--desde") + 1] if "--desde" in sys.argv else None
M = json.load(open("montaje.json", encoding="utf-8"))
ENV = dict(os.environ, PYTHONPATH=COMUN + os.pathsep + os.environ.get("PYTHONPATH", ""), PYTHONIOENCODING="utf-8", PYTHONUTF8="1")   # Windows: archivos en UTF-8 (tildes, emojis)
PASOS = ["transcribir", "cortar", "siluetas", "formato", "capas", "componer", "mezcla", "revision"]
hacer = set(PASOS[PASOS.index(DESDE):]) if DESDE else set(PASOS)

def corre(args, **kw):
    print("→", " ".join(os.path.basename(a) if os.sep in a else a for a in args[:3]), flush=True)
    subprocess.run(args, check=True, env=ENV, **kw)

def capa(html, carpeta, fps, intentos=12):
    """pinta una capa HTML a PNG; si Chrome se cuelga más de 3 minutos sin sacar fotogramas, se reinicia y sigue donde iba"""
    dur = str(json.load(open("plan.json"))["dur"]); fallos = 0
    while fallos < intentos:                    # tandas de 150 fotogramas con un Chrome nuevo cada una (código 3 = tanda hecha)
        p = subprocess.Popen([PY, os.path.join(COMUN, "render_html.py"), html, carpeta, dur, str(fps)], env=dict(ENV, TANDA="150"))
        ultimo, visto = time.time(), -1
        while p.poll() is None:
            time.sleep(5); n = len(glob.glob(os.path.join(carpeta, "*.png")))
            if n != visto: visto, ultimo = n, time.time()
            elif time.time() - ultimo > 180: p.kill(); p.wait(); print("  · Chrome atascado: reinicio", flush=True); break
        if p.returncode == 0: return
        if p.returncode != 3: fallos += 1
    sys.exit(f"No se pudo pintar {html}. Cierra otros programas y repite: python montar.py {proyecto} --desde capas")

def renumera(carpeta, total):
    """deja los fotogramas como f0000.png… y rellena alguno que falte con el anterior (por si Chrome se saltó alguno)"""
    for f in glob.glob(os.path.join(carpeta, "f*.png")):
        n = int(os.path.basename(f)[1:-4]); nuevo = os.path.join(carpeta, f"f{n:04d}.png")
        if f != nuevo and not os.path.exists(nuevo): os.rename(f, nuevo)
    for i in range(1, total):
        a, b = os.path.join(carpeta, f"f{i:04d}.png"), os.path.join(carpeta, f"f{i - 1:04d}.png")
        if not os.path.exists(a) and os.path.exists(b): shutil.copy(b, a)

# 1. transcribir los brutos que falten
if "transcribir" in hacer:
    faltan = sorted({t[0] for t in M["tramos"] if not os.path.exists(os.path.join("palabras", os.path.splitext(os.path.basename(t[0]))[0] + ".json"))})
    if faltan: corre([PY, os.path.join(COMUN, "transcribir.py"), *faltan])
# 2. corte limpio
if "cortar" in hacer and (DESDE or not os.path.exists("base.mov")): corre([PY, os.path.join(COMUN, "cortar.py")])
P = json.load(open("plan.json", encoding="utf-8")); DUR = P["dur"]
# 3. siluetas de la persona (solo si el estilo pinta cosas detrás del cuerpo)
detras = M.get("detras", False)
if "siluetas" in hacer and detras and not os.path.exists(os.path.join("mascaras", ".hecho")):
    corre([PY, os.path.join(COMUN, "mascaras.py")]); corre([PY, os.path.join(COMUN, "afina_mascaras.py")])
    open(os.path.join("mascaras", ".hecho"), "w").close()
# 4. formato del estilo: escribe overlay.html (+ detras.html), eventos.json, camara.json, volumen.json
if "formato" in hacer:
    corre([PY, "formato.py"])
    # colores de la marca: el acento con el que se diseñó el estilo pasa a ser el del alumno (rojo/verde de malo/bueno no se tocan)
    from rutas import MARCA, ACENTO_BASE
    nuevo = MARCA.get("color_acento", "").strip()
    if nuevo.startswith("#") and len(nuevo) == 7 and nuevo.upper() != ACENTO_BASE:
        import re
        rgb = lambda h: ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))
        for h in ("overlay.html", "detras.html"):
            if os.path.exists(h):
                t = open(h, encoding="utf-8").read()
                t = re.sub(ACENTO_BASE, nuevo, t, flags=re.I)
                t = re.sub(r"(rgba?\(\s*)255\s*,\s*75\s*,\s*43", lambda m: m.group(1) + rgb(nuevo), t)
                open(h, "w", encoding="utf-8").write(t)
        print("  · colores de la marca aplicados:", nuevo, flush=True)
# 5. capas HTML: delante a 60 fps (se promedia de dos en dos = desenfoque de movimiento real) y detrás a 30 fps
if "capas" in hacer:
    capa("overlay.html", "overlay", 60); renumera("overlay", round(DUR * 60))
    if os.path.exists("detras.html"): capa("detras.html", "overlay_detras", 30); renumera("overlay_detras", round(DUR * 30))
# 6. componer la imagen final
if "componer" in hacer: corre([PY, os.path.join(COMUN, "marcador.py")])
# 7. mezcla: voz + música + efectos
if "mezcla" in hacer:
    mus = M.get("musica")
    if mus and not os.path.exists(os.path.join(MUS, mus)): sys.exit(f"Falta la canción {mus} en recursos-descargados/musica (escribe /musica).")
    subprocess.run([PY, os.path.join(COMUN, "mezcla.py")] + (["musica"] if mus else []), check=True,
                   env=dict(ENV, MUSICA=mus or "", MUSICA_INI=str(M.get("musica_ini", 0.0))))
# 8. versión para el móvil y hoja de fotogramas para revisar
if "revision" in hacer:
    final = "final_musica.mp4" if M.get("musica") else "final.mp4"
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", final, "-c:v", "libx264", "-crf", "25", "-c:a", "aac", "-b:a", "160k", "-ac", "2",
                    "-movflags", "+faststart", "movil.mp4"], check=True)
    subprocess.run([ffmpeg(), "-v", "error", "-y", "-i", final, "-vf", f"fps=12/{DUR},scale=240:-2,tile=6x2", "-frames:v", "1", "hoja.jpg"], check=True)
    print(f"\nLISTO: {os.path.join(proyecto, final)}  ·  para el móvil: movil.mp4  ·  revisión: hoja.jpg")
