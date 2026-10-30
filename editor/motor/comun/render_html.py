# Renderiza una página HTML animada (expone setT(t)) a PNG con transparencia, fotograma a fotograma,
# con Chrome/Chromium headless por CDP. Solo biblioteca estándar de Python (sin Node ni websockets).
#   python3 render_html.py <pagina.html> <carpeta_salida> <duracion_s | t1,t2,...> [fps]
# Funciona en Mac, Windows y Linux con Chrome, Edge o Chromium (el que haya). Tamaño: RENDER_W x RENDER_H (por defecto 1080x1920).
import base64, json, os, random, shutil, socket, struct, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path

pagina, destino, dur = sys.argv[1], sys.argv[2], sys.argv[3]
FPS = int(sys.argv[4]) if len(sys.argv) > 4 else 30
SUELTOS = [float(x) for x in dur.split(",")] if "," in dur else None
TOTAL = len(SUELTOS) if SUELTOS else round(float(dur) * FPS)
W_, H_ = int(os.environ.get("RENDER_W", 1080)), int(os.environ.get("RENDER_H", 1920))
_PF = [os.environ.get(v, "") for v in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
CHROME = os.environ.get("CHROME_PATH") or next((p for p in [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser", "/Applications/Chromium.app/Contents/MacOS/Chromium",
    *[os.path.join(b, "Google", "Chrome", "Application", "chrome.exe") for b in _PF if b],
    *[os.path.join(b, "Microsoft", "Edge", "Application", "msedge.exe") for b in _PF if b],
    "/usr/bin/chromium-browser", "/snap/bin/chromium", "/usr/bin/chromium", "/usr/bin/google-chrome"] if os.path.exists(p)), None)
if not CHROME: sys.exit("No encuentro Chrome ni Edge. Instala Google Chrome y vuelve a intentarlo.")
os.makedirs(destino, exist_ok=True)
# Reanudable: si la página no ha cambiado, se conservan los fotogramas ya hechos y se sigue por donde iba.
import hashlib
firma = hashlib.md5(open(pagina, "rb").read() + dur.encode() + str(FPS).encode()).hexdigest()
marca = os.path.join(destino, ".firma")
if not (os.path.exists(marca) and open(marca).read() == firma):
    for f in os.listdir(destino): os.remove(os.path.join(destino, f))
    open(marca, "w").write(firma)
url = Path(os.path.abspath(pagina)).as_uri()

class WS:
    """cliente WebSocket mínimo (RFC 6455) para hablar con Chrome"""
    def __init__(self, ws_url):
        host_port, ruta = ws_url[len("ws://"):].split("/", 1); host, port = host_port.split(":")
        self.s = socket.create_connection((host, int(port)), timeout=60)
        clave = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET /{ruta} HTTP/1.1\r\nHost: {host_port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                        f"Sec-WebSocket-Key: {clave}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        cab = b""
        while b"\r\n\r\n" not in cab:
            c = self.s.recv(1)
            if not c: raise RuntimeError("Chrome cerró la conexión")   # sin esto se quedaba en un bucle infinito
            cab += c
        if b" 101 " not in cab.split(b"\r\n")[0]: raise RuntimeError("handshake fallido")
    def _leer(self, n):
        b = b""
        while len(b) < n:
            c = self.s.recv(n - len(b))
            if not c: raise RuntimeError("conexión cerrada")
            b += c
        return b
    def send(self, texto):
        d = texto.encode(); m = os.urandom(4); n = len(d)
        cab = bytes([0x81]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n) if n < 65536 else bytes([0x80 | 127]) + struct.pack(">Q", n))
        self.s.sendall(cab + m + bytes(b ^ m[i % 4] for i, b in enumerate(d)))
    def recv(self):
        datos = b""
        while True:
            b1, b2 = self._leer(2); n = b2 & 0x7F
            if n == 126: n = struct.unpack(">H", self._leer(2))[0]
            elif n == 127: n = struct.unpack(">Q", self._leer(8))[0]
            datos += self._leer(n)
            if b1 & 0x80: return datos.decode()

chrome = ws = None; ID = [0]
def cdp(metodo, **params):
    ID[0] += 1; i = ID[0]; ws.send(json.dumps({"id": i, "method": metodo, "params": params}))
    while True:
        m = json.loads(ws.recv())
        if m.get("method") == "Inspector.detached": raise RuntimeError("Chrome cerró el render")
        if m.get("id") == i:
            if "error" in m: raise RuntimeError(m["error"].get("message"))
            return m.get("result", {})

def arrancar():
    global chrome, ws, udd
    puerto = 9400 + random.randint(0, 300)
    udd = os.path.expanduser(f"~/snap/chromium/common/render_{os.getpid()}_{puerto}") if CHROME.startswith(("/usr/bin/chromium-browser", "/snap")) \
        else os.path.join(tempfile.gettempdir(), f"render_{os.getpid()}_{puerto}")
    os.makedirs(udd, exist_ok=True)
    pre = ["nice", "-n", "19"] if sys.platform.startswith("linux") else []
    extra = dict(creationflags=subprocess.CREATE_NEW_PROCESS_GROUP) if os.name == "nt" else dict(start_new_session=True)
    chrome = subprocess.Popen(pre + [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                               "--mute-audio", "--renderer-process-limit=1", "--disable-extensions", "--disable-background-networking", "--allow-file-access-from-files", "--disable-lcd-text", f"--remote-debugging-port={puerto}",
                               f"--user-data-dir={udd}", "--no-first-run", "--no-default-browser-check", f"--window-size={W_},{H_}", "about:blank"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **extra)
    obj = None
    for _ in range(150):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{puerto}/json/new?{urllib.parse.quote(url, safe='')}", method="PUT")
            obj = json.load(urllib.request.urlopen(req, timeout=3))
            if obj.get("webSocketDebuggerUrl"): break
        except Exception: time.sleep(0.3)
    if not obj: raise RuntimeError("Chrome no abrió la pestaña")
    ws = WS(obj["webSocketDebuggerUrl"])
    cdp("Runtime.enable")
    cdp("Emulation.setDefaultBackgroundColorOverride", color={"r": 0, "g": 0, "b": 0, "a": 0})
    cdp("Emulation.setDeviceMetricsOverride", width=W_, height=H_, deviceScaleFactor=1, mobile=False)
    for _ in range(80):
        r = cdp("Runtime.evaluate", expression="typeof setT === 'function' && document.fonts.status === 'loaded'", returnByValue=True)
        if r["result"].get("value") is True: return
        time.sleep(0.25)
    raise RuntimeError("la página no expuso setT() o no cargaron las fuentes")

def cerrar():
    import signal
    try:
        if os.name == "nt": subprocess.run(["taskkill", "/F", "/T", "/PID", str(chrome.pid)], capture_output=True)   # Windows: el árbol entero
        else: os.killpg(chrome.pid, signal.SIGKILL)                                                        # Chromium deja hijos: el grupo entero
        chrome.wait(5)
    except Exception: pass
    time.sleep(0.5)
    shutil.rmtree(udd, ignore_errors=True)

import urllib.parse
ancho = len(str(TOTAL)); relanzados = 0
TANDA = int(os.environ.get('TANDA', '0')); hechos_ahora = 0   # con TANDA>0 sale tras ese número de fotogramas (código 3)
try:
    arrancar(); print("  · conectado a Chrome", flush=True)
    for f in range(TOTAL):
        nombre = os.path.join(destino, f"f{str(f).zfill(ancho)}.png")
        if os.path.exists(nombre): continue
        if TANDA and hechos_ahora >= TANDA: cerrar(); sys.exit(3)
        if f and f % 300 == 0: cerrar(); time.sleep(1.0); arrancar()      # Chrome acumula memoria: se renueva cada 300
        t = SUELTOS[f] if SUELTOS else f / FPS; png = None
        for intento in range(3):
            try:
                cdp("Runtime.evaluate", expression=f"setT({t})", returnByValue=True)
                png = base64.b64decode(cdp("Page.captureScreenshot", format="png", optimizeForSpeed=True, captureBeyondViewport=True,
                                           clip={"x": 0, "y": 0, "width": W_, "height": H_, "scale": 1})["data"]); break
            except Exception as e:
                relanzados += 1; print(f"  · fotograma {f}: {e} — relanzando Chrome", flush=True); cerrar(); time.sleep(4); arrancar()
        if png is None: raise SystemExit(f"no se pudo capturar el fotograma {f}")
        open(nombre, "wb").write(png); hechos_ahora += 1
        if f % 120 == 0: print(f"    {f}/{TOTAL}", flush=True)
    print(f"  · {TOTAL} fotogramas en {destino}", flush=True)
finally:
    cerrar()
