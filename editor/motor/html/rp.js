// rp.js — biblioteca de tipografías y animaciones para reels (1080x1920, fondo transparente).
// Se usa desde una página que define una lista de elementos con tiempos y llama a RP.montar(lista).
// render_html.mjs llama a setT(t) en cada fotograma y captura un PNG con transparencia.
//
// Reglas de movimiento (de las referencias): nada tiembla ni late; todo entra con curva suave
// y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
(function () {
  const RP = {};
  const cl = x => Math.max(0, Math.min(1, x));
  RP.easeOut = x => 1 - Math.pow(1 - cl(x), 3);
  RP.easeInOut = x => { x = cl(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
  RP.spring = (x, s = 1.6) => { x = cl(x) - 1; return 1 + x * x * ((s + 1) * x + s); };   // rebote suave
  RP.css = (el, o) => Object.assign(el.style, o);

  // ---------- TIPOGRAFÍAS PREDEFINIDAS ----------
  // Cada una es un estilo CSS listo. El color de acento se pasa en cada elemento (acento).
  RP.TIPOS = {
    linea:          { font: "600 46px Inter", letterSpacing: "-0.02em", color: "#fff", textTransform: "none" },
    linea_mayus:    { font: "600 40px Inter", letterSpacing: "0.02em", color: "#fff", textTransform: "uppercase" },
    clave_serif:    { font: "italic 400 132px 'Instrument Serif'", letterSpacing: "-0.01em" },               // serif cursiva grande
    clave_serif_dm: { font: "italic 400 120px 'DM Serif Display'", letterSpacing: "-0.01em" },
    clave_redonda:  { font: "900 128px Nunito", letterSpacing: "-0.03em" },                                  // sans redondeada gruesa
    clave_condensada:{ font: "400 150px Anton", letterSpacing: "0", textTransform: "uppercase" },            // mayúscula condensada
    clave_bebas:    { font: "400 160px 'Bebas Neue'", letterSpacing: "0.01em", textTransform: "uppercase" },
    clave_helvetica:{ font: "800 120px 'Helvetica Neue', Inter", letterSpacing: "-0.05em" },
    manuscrita:     { font: "700 140px Caveat", letterSpacing: "0" },
    pixel:          { font: "400 64px VT323", letterSpacing: "0.04em", textTransform: "uppercase" },
    mono:           { font: "500 40px 'JetBrains Mono'", letterSpacing: "0" },
    fantasma:       { font: "300 90px Inter", letterSpacing: "0.5em", textTransform: "uppercase" },
  };

  // ---------- ANIMACIONES DE TEXTO PREDEFINIDAS ----------
  // Cada animación recibe (span de cada palabra/letra, progreso local 0-1, índice, total)
  RP.ANIM = {
    // sube desde un desenfoque y se asienta (la más versátil)
    sube_desenfoque: (el, p) => RP.css(el, { opacity: cl(p * 1.6), transform: `translateY(${18 * (1 - RP.easeOut(p))}px)`, filter: `blur(${6 * (1 - RP.easeOut(p))}px)` }),
    // pop con rebote
    pop: (el, p) => RP.css(el, { opacity: cl(p * 3), transform: `scale(${0.6 + 0.4 * RP.spring(p)})` }),
    // máscara: sube desde detrás de su base
    mascara: (el, p) => RP.css(el, { transform: `translateY(${100 * (1 - RP.easeOut(p))}%)` }),
    // letras que caen muy espaciadas y se juntan
    cae_espaciado: (el, p, i, n) => RP.css(el, { opacity: cl(p * 2), transform: `translateY(${-60 * (1 - RP.spring(p))}px)`, letterSpacing: `${0.4 * (1 - RP.easeOut(p))}em` }),
    // fantasma: letras tenues muy separadas que se asientan
    fantasma: (el, p) => RP.css(el, { opacity: 0.25 + 0.75 * RP.easeOut(p), letterSpacing: `${0.5 - 0.48 * RP.easeOut(p)}em`, filter: `blur(${4 * (1 - p)}px)` }),
    // máquina de escribir
    teclea: (el, p) => RP.css(el, { opacity: p > 0 ? 1 : 0 }),
    // brillo: entra con resplandor que se apaga
    brillo: (el, p, i, n, ac) => RP.css(el, { opacity: cl(p * 2), textShadow: `0 0 ${40 * (1 - RP.easeOut(p)) + 18}px ${ac}aa`, transform: `scale(${1.08 - 0.08 * RP.easeOut(p)})` }),
  };

  // ---------- ELEMENTOS ----------
  // Todos: { t0, t1, x, y (centro), ... }. Salida: fundido de 0,12 s salvo que salida:false.
  const capa = document.createElement("div");
  RP.css(capa, { position: "fixed", left: 0, top: 0, width: "1080px", height: "1920px", overflow: "hidden" });
  document.body.appendChild(capa);
  RP.css(document.body, { margin: 0, background: "transparent" });

  function caja(e) {
    const d = document.createElement("div");
    RP.css(d, { position: "absolute", left: e.x + "px", top: e.y + "px", transform: "translate(-50%,-50%)", textAlign: "center", whiteSpace: "nowrap" });
    capa.appendChild(d); return d;
  }

  // texto: una frase cuyas palabras (o letras) aparecen con su tiempo.
  // e = { tipo:'texto', palabras:[{w, t}], tipo_letra, anim, acento, por:'palabra'|'letra', esperan_gris:true, caja_color }
  function texto(e) {
    const d = caja(e); const est = RP.TIPOS[e.tipo_letra] || RP.TIPOS.linea; RP.css(d, est);
    if (e.acento && e.tipo_letra !== "linea" && e.tipo_letra !== "linea_mayus") d.style.color = e.acento;
    if (e.color) d.style.color = e.color;
    if (e.brillo) d.style.textShadow = `0 0 28px ${e.acento}88`;
    if (e.caja_color) RP.css(d, { background: e.caja_color, padding: "4px 18px 8px", borderRadius: "6px" });
    const piezas = [];
    e.palabras.forEach((p, i) => {
      const unidades = e.por === "letra" ? [...p.w].map((c, k) => ({ c, t: p.t + k * 0.035 })) : [{ c: p.w, t: p.t }];
      unidades.forEach(u => {
        const wrap = document.createElement("span"); RP.css(wrap, { display: "inline-block", overflow: e.anim === "mascara" ? "hidden" : "visible", verticalAlign: "bottom" });
        const s = document.createElement("span"); s.textContent = u.c; RP.css(s, { display: "inline-block", whiteSpace: "pre" });
        wrap.appendChild(s); d.appendChild(wrap); piezas.push({ s, t: u.t, i: piezas.length });
      });
      if (e.por !== "letra" && i < e.palabras.length - 1) d.appendChild(document.createTextNode(" "));
    });
    return t => {
      const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "block" : "none"; if (!vis) return;
      d.style.opacity = e.salida === false ? 1 : cl((e.t1 - t) / 0.12);
      const anim = RP.ANIM[e.anim || "sube_desenfoque"];
      piezas.forEach(({ s, t: tw, i }) => {
        const p = cl((t - tw) / (e.dur || 0.28));
        if (t < tw) { s.style.opacity = e.esperan_gris ? 0.28 : 0; s.style.transform = "none"; s.style.filter = "none"; }
        else anim(s, p, i, piezas.length, e.acento || "#fff");
      });
    };
  }

  // chip/pastilla con icono: { tipo:'chip', texto, icono:'✓'|'!'|'★'|'+'|emoji, fondo, color, color_icono }
  function chip(e) {
    const d = caja(e);
    RP.css(d, { display: "flex", alignItems: "center", gap: "14px", padding: "14px 26px 14px 14px", borderRadius: "999px", background: e.fondo || "rgba(255,255,255,.95)", color: e.color || "#111", font: `600 ${e.tam || 38}px Inter`, letterSpacing: "-0.02em", boxShadow: "0 10px 30px rgba(0,0,0,.18)" });
    if (e.cristal) RP.css(d, { background: "rgba(20,22,28,.55)", backdropFilter: "blur(14px)", color: "#fff", border: "1px solid rgba(255,255,255,.18)" });
    const ic = document.createElement("span"); ic.textContent = e.icono || "✓";
    RP.css(ic, { width: "56px", height: "56px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", background: e.color_icono || "#111", color: "#fff", font: "700 32px Inter" });
    d.appendChild(ic); d.appendChild(document.createTextNode(e.texto));
    return t => {
      const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "flex" : "none"; if (!vis) return;
      const p = cl((t - e.t0) / 0.32); const s = 0.7 + 0.3 * RP.spring(p);
      d.style.opacity = cl(p * 3) * (e.salida === false ? 1 : cl((e.t1 - t) / 0.12));
      d.style.transform = `translate(-50%,-50%) translateY(${30 * (1 - RP.easeOut(p))}px) scale(${s})`;
    };
  }

  // contador que sube: { tipo:'contador', desde, hasta, formato:(n)=>string, tipo_letra, acento }
  function contador(e) {
    const d = caja(e); RP.css(d, RP.TIPOS[e.tipo_letra || "clave_helvetica"]); d.style.color = e.acento || "#fff";
    return t => {
      const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "block" : "none"; if (!vis) return;
      const p = RP.easeOut((t - e.t0) / (e.dur || 0.9)); const v = e.desde + (e.hasta - e.desde) * p;
      d.textContent = (e.formato || (n => Math.round(n).toLocaleString("es-ES")))(v);
      d.style.opacity = cl((t - e.t0) / 0.1) * cl((e.t1 - t) / 0.12);
    };
  }

  // barra que se llena: { tipo:'barra', ancho, alto, fondo, acento, hasta (0-1) }
  function barra(e) {
    const d = caja(e); RP.css(d, { width: e.ancho + "px", height: (e.alto || 16) + "px", borderRadius: "999px", background: e.fondo || "rgba(255,255,255,.25)", overflow: "hidden" });
    const r = document.createElement("div"); RP.css(r, { height: "100%", width: "0%", background: e.acento, borderRadius: "999px", boxShadow: `0 0 18px ${e.acento}` }); d.appendChild(r);
    return t => {
      const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "block" : "none"; if (!vis) return;
      r.style.width = (100 * (e.hasta || 1) * RP.easeInOut((t - e.t0 - 0.1) / (e.dur || 0.8))) + "%"; d.style.opacity = cl((e.t1 - t) / 0.12);
    };
  }

  // iconos que orbitan alrededor de un punto: { tipo:'orbita', iconos:[emoji|url], radio, vueltas_s }
  function orbita(e) {
    const ds = e.iconos.map(ic => { const d = caja(e); RP.css(d, { width: "120px", height: "120px", borderRadius: "30px", background: "#fff", boxShadow: "0 18px 40px rgba(0,0,0,.25)", display: "flex", alignItems: "center", justifyContent: "center", font: "64px sans-serif" });
      if (/^(https?:|data:|\.\/|\/)/.test(ic)) { const im = new Image(); im.src = ic; RP.css(im, { width: "84px" }); d.appendChild(im); } else d.textContent = ic; return d; });
    return t => ds.forEach((d, i) => {
      const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "flex" : "none"; if (!vis) return;
      const a = (i / ds.length) * 2 * Math.PI + (t - e.t0) * 2 * Math.PI / (e.vueltas_s || 8); const p = RP.spring((t - e.t0 - i * 0.06) / 0.4);
      d.style.transform = `translate(-50%,-50%) translate(${Math.cos(a) * e.radio * p}px, ${Math.sin(a) * e.radio * 0.55 * p}px) scale(${0.4 + 0.6 * p})`;
      d.style.opacity = cl(p) * cl((e.t1 - t) / 0.15);
    });
  }

  // estrellas brillantes junto a una palabra: { tipo:'chispas', acento }
  function chispas(e) {
    const ps = [[-60, -40, 1], [50, -60, .7], [70, 30, .5]].map(([dx, dy, k]) => { const d = caja({ x: e.x + dx, y: e.y + dy }); d.textContent = "✦"; RP.css(d, { color: e.acento, font: `${70 * k}px Inter`, textShadow: `0 0 20px ${e.acento}` }); return d; });
    return t => ps.forEach((d, i) => { const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "block" : "none"; if (!vis) return;
      const p = cl((t - e.t0 - i * 0.08) / 0.3); d.style.opacity = cl(p * 2) * cl((e.t1 - t) / 0.15); d.style.transform = `translate(-50%,-50%) scale(${RP.spring(p, 2.2)}) rotate(${20 * (1 - p)}deg)`; });
  }

  // destello / barrido de color a pantalla completa: { tipo:'barrido', color, dir:'arriba'|'derecha' }
  function barrido(e) {
    const d = document.createElement("div"); RP.css(d, { position: "absolute", left: 0, top: 0, width: "1080px", height: "1920px", background: e.color }); capa.appendChild(d);
    return t => { const dur = e.t1 - e.t0; const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "block" : "none"; if (!vis) return;
      const p = (t - e.t0) / dur; const a = RP.easeInOut(p * 2), b = RP.easeInOut(p * 2 - 1);
      d.style.clipPath = e.dir === "derecha" ? `inset(0 ${100 - 100 * a}% 0 ${100 * b}%)` : `inset(${100 - 100 * a}% 0 ${100 * b}% 0)`; };
  }

  // rótulo de nombre: { tipo:'nombre', nombre, cargo, acento }
  function nombre(e) {
    const d = caja(e); RP.css(d, { transform: "none", left: (e.x || 90) + "px", top: (e.y || 1180) + "px", borderLeft: `6px solid ${e.acento}`, paddingLeft: "22px", textAlign: "left" });
    d.innerHTML = `<div style="font:600 46px 'JetBrains Mono';color:#fff;letter-spacing:-.02em">${e.nombre}</div><div style="font:500 30px Inter;color:#fff;opacity:.8;margin-top:6px">${e.cargo || ""}</div>`;
    return t => { const vis = t >= e.t0 && t < e.t1; d.style.display = vis ? "block" : "none"; if (!vis) return;
      const p = RP.easeOut((t - e.t0) / 0.4); d.style.clipPath = `inset(0 ${100 - 100 * p}% 0 0)`; d.style.opacity = cl((e.t1 - t) / 0.15); };
  }

  const TIPOS_EL = { texto, chip, contador, barra, orbita, chispas, barrido, nombre };
  RP.montar = lista => {
    const fns = lista.map(e => TIPOS_EL[e.tipo](e));
    window.setT = t => fns.forEach(f => f(t));
  };
  window.RP = RP;
})();
