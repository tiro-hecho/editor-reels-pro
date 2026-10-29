// Renderiza motion graphics: abre la página en Chrome headless y captura un PNG con
// transparencia por fotograma. ffmpeg los superpone luego al vídeo.
//
//   node render_mg2.mjs <pagina.html> <carpeta_salida> <duracion_s | t1,t2,...> [fps]
//
// Diferencias con el render_mg.mjs original:
//  - Chrome 144 mata el proceso de render si se arranca con --default-background-color=0.
//    La transparencia se pide por CDP con Emulation.setDefaultBackgroundColorOverride.
//  - El viewport real es menor que --window-size, así que se captura con un clip explícito.
//  - En renders largos Chrome deja de responder de vez en cuando (visto: se colgó en el
//    fotograma 552 de 942). Ahora se reintenta y, si hace falta, se relanza Chrome y se
//    sigue por donde iba, en vez de morirse y dejar la secuencia a medias.
import { spawn } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import path from "node:path";

const CHROME = process.env.CHROME_PATH || ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome","/Applications/Brave Browser.app/Contents/MacOS/Brave Browser","/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge","C:/Program Files/Google/Chrome/Application/chrome.exe","C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"].find(p => fs.existsSync(p));
const [pagina, destino, durStr, fpsStr] = process.argv.slice(2);
const SUELTOS = durStr.includes(",") ? durStr.split(",").map(Number) : null;
const FPS = parseInt(fpsStr || "30", 10);
const TOTAL = SUELTOS ? SUELTOS.length : Math.round(parseFloat(durStr) * FPS);

const sleep = ms => new Promise(r => setTimeout(r, ms));
const portUp = p => new Promise(res => {
  const s = net.connect(p, "127.0.0.1");
  s.on("connect", () => { s.destroy(); res(true); });
  s.on("error", () => res(false));
});

fs.mkdirSync(destino, { recursive: true });
for (const f of fs.readdirSync(destino)) fs.unlinkSync(path.join(destino, f));

const url = "file:///" + path.resolve(pagina).replace(/\\/g, "/");

let chrome = null, sock = null, puerto = 0, udd = "";
let id = 0; const pend = new Map();

function cdp(method, params = {}, ms = 20000) {
  return new Promise((res, rej) => {
    const i = ++id;
    const reloj = setTimeout(() => { pend.delete(i); rej(new Error(`${method} sin respuesta en ${ms} ms`)); }, ms);
    pend.set(i, { res: v => { clearTimeout(reloj); res(v); }, rej: e => { clearTimeout(reloj); rej(e); } });
    try { sock.send(JSON.stringify({ id: i, method, params })); }
    catch (e) { clearTimeout(reloj); pend.delete(i); rej(e); }
  });
}

function cerrar() {
  for (const [, p] of pend) p.rej(new Error("sesión cerrada"));
  pend.clear();
  try { sock?.close(); } catch { }
  try { chrome?.kill(); } catch { }
  sock = null; chrome = null;
}

async function arrancar() {
  puerto = 9400 + Math.floor(Math.random() * 300);
  udd = `${process.env.TEMP}/nb_mg_${process.pid}_${puerto}`;
  chrome = spawn(CHROME, [
    "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
    "--force-device-scale-factor=1", "--mute-audio", "--allow-file-access-from-files",
    "--disable-lcd-text",
    `--remote-debugging-port=${puerto}`, `--user-data-dir=${udd}`,
    "--no-first-run", "--no-default-browser-check", "--window-size=1080,1920", "about:blank",
  ], { stdio: "ignore" });

  for (let i = 0; i < 80 && !(await portUp(puerto)); i++) await sleep(250);
  const esPagina = x => x.type === "page" && x.webSocketDebuggerUrl &&
    !x.url.startsWith("chrome-extension://") && !x.url.startsWith("devtools://");

  let objetivo = null, ultimo = "";
  for (let i = 0; i < 24 && !objetivo; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${puerto}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
      const nueva = await r.json();
      if (nueva && esPagina(nueva)) { objetivo = nueva; break; }
      const lista = await (await fetch(`http://127.0.0.1:${puerto}/json/list`)).json();
      objetivo = lista.find(esPagina);
      ultimo = JSON.stringify(lista.map(x => x.type));
    } catch (e) { ultimo = e.message; }
    if (!objetivo) await sleep(400);
  }
  if (!objetivo) throw new Error("Chrome no abrió ninguna pestaña. Último estado: " + ultimo);

  sock = new WebSocket(objetivo.webSocketDebuggerUrl);
  await new Promise((res, rej) => {
    const reloj = setTimeout(() => rej(new Error("el WebSocket no abrió")), 15000);
    sock.addEventListener("open", () => { clearTimeout(reloj); res(); });
    sock.addEventListener("error", () => { clearTimeout(reloj); rej(new Error("WebSocket no conectó")); });
  });
  sock.addEventListener("message", async e => {
    try {
      const crudo = typeof e.data === "string" ? e.data : await e.data.text();
      const m = JSON.parse(crudo);
      // si el render muere hay que enterarse: si no, todo espera al timeout
      if (m.method === "Inspector.detached") {
        for (const [, p] of pend) p.rej(new Error("Chrome cerró el render: " + (m.params?.reason || "detached")));
        pend.clear();
      }
      const p = m.id && pend.get(m.id);
      if (p) { pend.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    } catch { /* eventos sueltos */ }
  });

  await cdp("Runtime.enable");
  // Fondo transparente por CDP (el flag equivalente tumba Chrome 144).
  await cdp("Emulation.setDefaultBackgroundColorOverride", { color: { r: 0, g: 0, b: 0, a: 0 } });
  // El viewport real de Chrome es 1062x1824, y como la página lleva overflow:hidden,
  // los 18 px que le sobran al lienzo de 1080 se RECORTAN: el PNG salía sin borde
  // derecho y en el vídeo aparecía una franja negra vertical de 18 px. Fijando las
  // métricas, el viewport pasa a medir exactamente el lienzo y deja de recortar.
  await cdp("Emulation.setDeviceMetricsOverride", {
    width: 1080, height: 1920, deviceScaleFactor: 1, mobile: false,
  });

  let listo = false;
  for (let i = 0; i < 60 && !listo; i++) {
    const r = await cdp("Runtime.evaluate", {
      expression: "typeof setT === 'function' && document.fonts.status === 'loaded'",
      returnByValue: true,
    });
    listo = r.result.value === true;
    if (!listo) await sleep(250);
  }
  if (!listo) throw new Error("la página no expuso setT() o no cargaron las fuentes");
}

async function capturar(t) {
  await cdp("Runtime.evaluate", { expression: `setT(${t})`, returnByValue: true });
  // El viewport real es algo menor que --window-size: se recorta el lienzo exacto o los
  // PNG salen a 1062x1824 y el overlay queda descuadrado.
  const shot = await cdp("Page.captureScreenshot", {
    format: "png", optimizeForSpeed: true, captureBeyondViewport: true,
    clip: { x: 0, y: 0, width: 1080, height: 1920, scale: 1 },
  });
  return Buffer.from(shot.data, "base64");
}

const ancho = String(TOTAL).length;
let relanzados = 0;
try {
  await arrancar();
  console.log("  · conectado a Chrome");

  for (let f = 0; f < TOTAL; f++) {
    const t = SUELTOS ? SUELTOS[f] : f / FPS;
    let png = null;
    for (let intento = 0; intento < 3 && !png; intento++) {
      try {
        png = await capturar(t);
      } catch (e) {
        // Chrome se atasca de vez en cuando en renders largos: se relanza y se sigue
        // por el mismo fotograma, en vez de abandonar la secuencia a medias.
        relanzados++;
        console.log(`\n  · fotograma ${f}: ${e.message} — relanzando Chrome (${relanzados})`);
        cerrar();
        await sleep(1200);
        try { fs.rmSync(udd, { recursive: true, force: true }); } catch { }
        await arrancar();
      }
    }
    if (!png) throw new Error(`no se pudo capturar el fotograma ${f} tras 3 intentos`);
    fs.writeFileSync(path.join(destino, `f${String(f).padStart(ancho, "0")}.png`), png);
    if (f % 60 === 0) process.stdout.write(`    ${f}/${TOTAL}\r`);
  }

  const hechos = fs.readdirSync(destino).filter(x => x.endsWith(".png")).length;
  if (hechos !== TOTAL) throw new Error(`faltan fotogramas: ${hechos} de ${TOTAL}`);
  console.log(`  · ${TOTAL} fotogramas en ${destino}${relanzados ? ` (${relanzados} relanzamientos)` : ""}        `);
} finally {
  cerrar();
  await sleep(500);
  try { fs.rmSync(udd, { recursive: true, force: true }); } catch { }
}
