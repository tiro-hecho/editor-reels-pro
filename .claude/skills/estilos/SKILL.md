---
name: estilos
description: Enseña los estilos de edición guardados con sus capturas para elegir uno y repetir el formato. Úsala cuando diga «/estilos», «qué estilos tienes», «enséñame los estilos», «quiero repetir un formato» o «edítalo como el del ranking».
---
# Estilos guardados

1. Lee `editor/catalogo/catalogo.md`. Primero van los **formatos completos** (aprobados en vídeos reales, con motor propio); después, el resto del catálogo.
2. Enseña cada formato completo con su captura de `editor/catalogo/capturas/<estilo>.jpg` (inicio, mitad y final del vídeo): ábrela con la herramienta de leer archivos o, si existe, envíala con la de mandar archivos. Debajo, una línea: para qué sirve y qué se ve.
3. Si pide el resto, cuéntale en una línea cada estilo de catálogo (`editor/estilos/`): esos no traen motor, los programas tú con su receta.
4. Cuando elija uno: lee `editor/estilos/<estilo>.md` y edita con `/editar-reel`. Si el estilo trae `editor/motor/<estilo>/formato.py`, cópialo al proyecto y cambia solo el contenido: la animación de entrada, los gráficos, el sonido y la música ya están ajustados.
5. Si pide un formato que no existe, usa la skill `crear-estilo`. Cuando el alumno apruebe un vídeo nuevo («me gusta», «guárdalo»), guárdalo como estilo: su `.md` en `mi-edicion/estilos/`, su `formato.py` y una captura (con las caras difuminadas si no son del alumno).
