---
name: copiar-referencia
description: Copia el estilo de edición de un reel de referencia sobre los vídeos del alumno, 1:1. Úsala cuando pegue un enlace o un vídeo y diga «edítalo como este», «copia este estilo» o «quiero este efecto».
---
# Copiar una referencia

1. Descarga la referencia con yt-dlp en `mi-edicion/referencias/<nombre>/` (la versión de mejor calidad).
2. Trabaja en ventanas de 5 segundos. En cada ventana:
   - `REF.md`: qué pasa fotograma a fotograma (posiciones, tamaños, fuentes, colores, curvas de movimiento), **medido en los fotogramas, nunca adivinado**;
   - constrúyelo y escribe `OURS.md`, `DIFF.md` (cada diferencia) y `PLAN.md` (arreglos);
   - arregla, compara otra vez y pasa a los 5 segundos siguientes.
3. Ajusta las fuentes por altura de minúscula y forma de las letras, saca los colores de los fotogramas y mide el zoom y el movimiento de cámara en cada fotograma.
4. Termina con una comparación lado a lado y un control de movimiento por zonas para que nada tiemble.
5. Guarda la receta resultante como estilo propio en `mi-edicion/estilos/<nombre>.md` (formato de `editor/estilos/`), para reutilizarla en todos sus vídeos.
6. Cumple siempre `../editar-reel/criterios.md`. Copia el método, no la marca, los textos ni las caras de otro creador.
