---
name: estilos
description: Enseña los estilos de edición guardados con sus capturas para elegir uno y repetir el formato. Úsala cuando diga «/estilos», «qué estilos tienes», «enséñame los estilos», «quiero repetir un formato» o «edítalo como el del ranking».
---
# Estilos guardados

Cada estilo tiene **un solo número** (1-42), el de `editor/catalogo/estilos.json` y `editor/catalogo/catalogo.md`.

1. **Primero, qué va a contar.** Si no lo ha dicho, pregúntale en una frase: «¿Qué vas a contar? Un top, errores, mal y bien, mitos, "si quieres… haz esto", vender tu servicio, un consejo, una historia, un podcast…». Si ya tiene el bruto transcrito, dedúcelo tú del guion.
2. **Enseña solo 2 o 3 estilos que encajen**, sacados de `editor/catalogo/INDICE-POR-GUION.md`, aprobados primero. De cada uno: su captura `editor/catalogo/capturas/<estilo>.jpg` (ábrela con la herramienta de leer archivos o envíala con la de mandar archivos), y debajo una línea con el número, el nombre y para qué sirve.
3. **Si quiere verlos todos**, ábrele el catálogo visual en el navegador: `editor/catalogo/catalogo.html` (Mac: `open editor/catalogo/catalogo.html` · Windows: `start editor\catalogo\catalogo.html`). Tiene filtro por tipo de guion, buscador y un botón para copiar la frase de cada estilo. Si no existe o está viejo: `python editor/catalogo/generar.py`.
4. Cuando elija uno («el 13»): lee `editor/estilos/<estilo>.md` y edita con `/editar-reel`. Si el estilo trae `editor/motor/<estilo>/formato.py`, cópialo al proyecto y cambia solo el contenido. Si trae un motor de referencia (con `LEEME.md`), adáptalo como dice ese archivo. Si es una **Referencia** sin motor, avísale de que lo programas con la receta y prueba antes 10-15 s.
5. Si pide un formato que no existe, usa la skill `crear-estilo`. Cuando apruebe un vídeo nuevo («me gusta», «guárdalo»), guárdalo como estilo suyo en `mi-edicion/estilos/` con su `.md`, su `formato.py` y una captura (con las caras difuminadas si no son del alumno).
