#!/usr/bin/env python3
"""Genera catalogo.md y catalogo.html (visual, con visor de subtítulos) a partir de estilos.json y subtitulos.json.
Uso: python editor/catalogo/generar.py   (solo usa Python, sin instalar nada)"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
E = json.load(open(os.path.join(AQUI, 'estilos.json'), encoding='utf-8'))
S = json.load(open(os.path.join(AQUI, 'subtitulos.json'), encoding='utf-8'))
G = {'si-quieres': '«Si quieres X, haz Y»', 'listas': 'Top, rankings y listas', 'mal-bien': 'Mal / bien y mitos',
     'tecnica': 'Corregir un ejercicio', 'vender': 'Vender un servicio o producto', 'consejos': 'Opinión y consejos',
     'historia': 'Contar una historia', 'sin-grabar': 'Sin grabarte (voz en off)', 'podcast': 'Podcast y entrevista',
     'avisos': 'Locales, inmuebles y avisos', 'horizontal': 'Horizontal (YouTube, VSL)'}
EST = {'aprobado': 'Aprobado', 'pruebas': 'En pruebas', 'referencia': 'Referencia'}

estilos = []
for i, e in enumerate(E, 1):
    n = e['n']
    cap = f'capturas/{n}.jpg' if os.path.exists(os.path.join(AQUI, 'capturas', n + '.jpg')) else None
    estilos.append(dict(e, num=i, tira=cap, receta=f'editor/estilos/{n}.md',
                        motor=os.path.isdir(os.path.join(AQUI, '..', 'motor', n))))

md = ['# Catálogo de estilos', '',
      f'{len(estilos)} estilos con un solo número: pide «hazlo con el estilo 13». **Catálogo visual:** abre `editor/catalogo/catalogo.html` (tarjetas animadas, filtros y visor de subtítulos).',
      'Elige por lo que vas a contar en `INDICE-POR-GUION.md`. Las recetas siguen `PLANTILLA-FICHA.md`.', '',
      'Estado: **Aprobado** (salió en vídeos reales y gustó) · **En pruebas** · **Referencia** (receta sacada de otro creador; Claude la programa y conviene probar 10-15 s antes).', '',
      '| N.º | Estilo | Para qué | Guion | Para quién | Estado | Captura | Motor |', '|---|---|---|---|---|---|---|---|']
for f in estilos:
    md.append(f'| **{f["num"]}** | `{f["n"]}` | {f["para"]} | {G[f["g"]]} | {", ".join(f.get("pub", []))} | {EST[f["est"]]} | {"`" + f["tira"] + "`" if f["tira"] else "muestra animada"} | {"sí" if f["motor"] else "receta"} |')
md += ['', '## Subtítulos', '', 'Se configuran en la pestaña **Subtítulos** del catálogo visual. Presets: ' + ', '.join(f'**{s["n"]}**' for s in S) + ' (código en `editor/subtitulos/`).']
open(os.path.join(AQUI, 'catalogo.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')

datos = {'fondos': ['fondos/persona1.jpg', 'fondos/persona2.jpg'], 'publico': 'entrenadores', 'estilos': estilos, 'subs': S, 'clientes': []}
t = open(os.path.join(AQUI, 'plantilla.html'), encoding='utf-8').read()
t = t.replace('__TITULO_HTML__', 'Tiro Hecho · <b>estilos</b>').replace('__TITULO__', 'Estilos Tiro Hecho').replace('__DATOS__', json.dumps(datos, ensure_ascii=False))
open(os.path.join(AQUI, 'catalogo.html'), 'w', encoding='utf-8').write(t)
print(len(estilos), 'estilos ·', len(S), 'subtítulos')
