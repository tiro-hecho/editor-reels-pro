#!/usr/bin/env python3
"""Genera catalogo.md y catalogo.html a partir de estilos.json (la fuente de verdad).
Uso: python editor/catalogo/generar.py   (solo usa Python, sin instalar nada)"""
import html, json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(AQUI, 'estilos.json'), encoding='utf-8'))
GUION = {
    'si-quieres': '«Si quieres X, haz Y»', 'listas': 'Top, rankings y listas', 'mal-bien': 'Mal / bien y mitos',
    'tecnica': 'Corregir un ejercicio', 'vender': 'Vender tu servicio', 'consejos': 'Opinión y consejos',
    'historia': 'Contar una historia', 'sin-grabar': 'Sin grabarte (voz en off)', 'podcast': 'Podcast y entrevista',
    'avisos': 'Avisos y enseñar un local', 'horizontal': 'Horizontal (YouTube, VSL)'}
ESTADO = {'aprobado': 'Aprobado', 'pruebas': 'En pruebas', 'referencia': 'Referencia'}

filas = []
for i, (n, g, est, para) in enumerate(E, 1):
    cap = f'capturas/{n}.jpg' if os.path.exists(os.path.join(AQUI, 'capturas', n + '.jpg')) else ''
    motor = os.path.isdir(os.path.join(AQUI, '..', 'motor', n))
    filas.append(dict(num=i, n=n, g=g, est=est, para=para, cap=cap, motor=motor, mini=f'_miniaturas_no_subir/{i - 13:02d}-{n}.jpg' if i > 13 else ''))

# ---- catalogo.md
md = ['# Catálogo de estilos', '',
      f'{len(filas)} estilos con un solo número cada uno: pide «hazlo con el estilo 13». Catálogo visual: abre `editor/catalogo/catalogo.html`.',
      '¿No sabes cuál? Elige por lo que vas a contar en `INDICE-POR-GUION.md`. Las recetas siguen `PLANTILLA-FICHA.md`.', '',
      'Estado: **Aprobado** (salió en vídeos reales y gustó) · **En pruebas** · **Referencia** (receta sacada de otro creador; Claude la programa y conviene probar 10-15 s antes).', '',
      '| N.º | Estilo | Para qué | Guion | Estado | Captura | Motor |', '|---|---|---|---|---|---|---|']
for f in filas:
    md.append(f'| **{f["num"]}** | `{f["n"]}` | {f["para"]} | {GUION[f["g"]]} | {ESTADO[f["est"]]} | {"`" + f["cap"] + "`" if f["cap"] else "—"} | {"sí" if f["motor"] else "receta"} |')
open(os.path.join(AQUI, 'catalogo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')

# ---- catalogo.html
def card(f):
    img = (f'<img src="{f["cap"]}" alt="" loading="lazy">' if f['cap'] else
           f'<img src="{f["mini"]}" alt="" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement(\'div\'),{{className:\'sin\',textContent:\'{html.escape(f["n"])}\'}}))">')
    pide = f'Edítalo con el estilo {f["num"]}, {f["n"]}'
    return (f'<article data-g="{f["g"]}" data-e="{f["est"]}" data-b="{html.escape((f["n"] + " " + f["para"]).lower())}">'
            f'<div class="im {"ancha" if f["cap"] else ""}">{img}</div><div class="c"><div class="top"><span class="num">{f["num"]}</span>'
            f'<span class="est {f["est"]}">{ESTADO[f["est"]]}</span></div><h3>{html.escape(f["n"])}</h3><p>{html.escape(f["para"])}</p>'
            f'<p class="g">{GUION[f["g"]]} · {"motor listo" if f["motor"] else "Claude lo programa con la receta"}</p>'
            f'<button data-p="{html.escape(pide)}">Copiar «{html.escape(pide)}»</button></div></article>')

chips = ''.join(f'<button class="chip" data-g="{k}">{v}</button>' for k, v in GUION.items() if any(f['g'] == k for f in filas))
doc = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Estilos Tiro Hecho</title><style>
:root{{--bg:#f6f5f2;--card:#fff;--t:#141414;--s:#666;--l:#e4e2dc;--a:#ffd60a;--ok:#1f9d55;--pr:#c77700;--rf:#6b6b6b}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111113;--card:#1b1b1e;--t:#f2f2f2;--s:#a3a3a3;--l:#2c2c30;--ok:#34c759;--pr:#ff9f0a;--rf:#9a9a9a}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--t);font:15px/1.45 -apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
header{{position:sticky;top:0;z-index:2;background:var(--bg);padding:20px 16px 12px;border-bottom:1px solid var(--l)}}
h1{{margin:0 0 4px;font-size:26px;letter-spacing:-.02em}}.sub{{margin:0 0 12px;color:var(--s)}}
.fil{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}input{{flex:1 1 220px;padding:9px 12px;border-radius:10px;border:1px solid var(--l);background:var(--card);color:var(--t);font:inherit}}
.chip{{padding:7px 12px;border-radius:999px;border:1px solid var(--l);background:var(--card);color:var(--t);font:inherit;font-size:13px;cursor:pointer}}.chip.on{{background:var(--a);color:#111;border-color:var(--a)}}
main{{padding:16px;display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}}
article{{background:var(--card);border:1px solid var(--l);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}}
.im{{aspect-ratio:1080/741;background:#000;display:flex;align-items:center;justify-content:center;overflow:hidden}}.im img{{width:100%;height:100%;object-fit:cover}}
.im:not(.ancha) img{{object-fit:contain}}.sin{{color:#888;font-weight:700;padding:20px;text-align:center}}
.c{{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}}.top{{display:flex;justify-content:space-between;align-items:center}}
.num{{background:var(--a);color:#111;font-weight:800;border-radius:8px;padding:2px 10px;font-size:18px}}
.est{{font-size:12px;font-weight:700;border:1.5px solid;border-radius:999px;padding:2px 10px}}.aprobado{{color:var(--ok)}}.pruebas{{color:var(--pr)}}.referencia{{color:var(--rf)}}
h3{{margin:2px 0 0;font-size:17px}}p{{margin:0}}.g{{color:var(--s);font-size:13px}}
button[data-p]{{margin-top:auto;padding:9px;border-radius:10px;border:0;background:var(--t);color:var(--bg);font:inherit;font-size:13px;cursor:pointer}}
</style></head><body><header><h1>Estilos de edición</h1><p class="sub">{len(filas)} estilos. Elige qué vas a contar, mira la captura y copia la frase para pedírselo a Claude.</p>
<div class="fil"><input id="q" placeholder="Buscar (ranking, mitos, podcast…)"><button class="chip on" data-g="">Todos</button>{chips}<button class="chip" id="ap">Solo aprobados</button></div></header>
<main>{"".join(card(f) for f in filas)}</main><script>
let g='',ap=false;const q=document.getElementById('q');
function f(){{const b=q.value.toLowerCase();document.querySelectorAll('article').forEach(a=>{{a.style.display=(a.dataset.b.includes(b)&&(!g||a.dataset.g===g)&&(!ap||a.dataset.e==='aprobado'))?'':'none'}})}}
q.oninput=f;document.querySelectorAll('.chip[data-g]').forEach(c=>c.onclick=()=>{{g=c.dataset.g;document.querySelectorAll('.chip[data-g]').forEach(x=>x.classList.toggle('on',x===c));f()}});
document.getElementById('ap').onclick=e=>{{ap=!ap;e.target.classList.toggle('on',ap);f()}};
document.querySelectorAll('button[data-p]').forEach(b=>b.onclick=()=>{{try{{navigator.clipboard.writeText(b.dataset.p)}}catch(e){{}}const t=b.textContent;b.textContent='Copiado ✓';setTimeout(()=>b.textContent=t,1400)}});
</script></body></html>'''
open(os.path.join(AQUI, 'catalogo.html'), 'w', encoding='utf-8').write(doc)
print(len(filas), 'estilos')
