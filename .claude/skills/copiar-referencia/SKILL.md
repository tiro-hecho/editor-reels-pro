---
name: copiar-referencia
description: Copia el estilo de edición de un reel de referencia sobre los vídeos del alumno, 1:1. Úsala cuando pegue un enlace o un vídeo y diga «edítalo como este», «copia este estilo» o «quiero este efecto».
---
# Copiar una referencia

> 🔴 **Zona segura de las redes (máxima prioridad, sin que el alumno lo pida):** nada de texto, subtítulos, rótulos, tarjetas ni gráficos fuera de **x 66–934, y 220–1440** en 1080×1920 (la más restrictiva de Instagram Reels, TikTok y Facebook: barra de arriba, pie con nombre y descripción, columna de botones y margen lateral). Nunca se sale del ancho de la pantalla. Está en `editor/motor/comun/zonas_seguras.py`: el motor lo recoloca o lo reduce solo y avisa en el registro, y `montar.py` se para si algo queda fuera. En un estilo nuevo, diséñalo ya dentro; no lo desactives nunca.
> Se copia 1:1 todo **menos esto**: si en la referencia algo queda bajo los botones, el pie o la barra de arriba, o se sale del ancho, en el nuestro va dentro de la zona y lo apuntas en `DIFF.md` como diferencia aceptada.

1. Descarga la referencia con yt-dlp en `mi-edicion/referencias/<nombre>/` (la versión de mejor calidad).
2. Trabaja en ventanas de 5 segundos. En cada ventana:
   - `REF.md`: qué pasa fotograma a fotograma (posiciones, tamaños, fuentes, colores, curvas de movimiento), **medido en los fotogramas, nunca adivinado**;
   - constrúyelo y escribe `OURS.md`, `DIFF.md` (cada diferencia) y `PLAN.md` (arreglos);
   - arregla, compara otra vez y pasa a los 5 segundos siguientes.
3. Ajusta las fuentes por altura de minúscula y forma de las letras, saca los colores de los fotogramas y mide el zoom y el movimiento de cámara en cada fotograma.
4. Termina con una comparación lado a lado y un control de movimiento por zonas para que nada tiemble.
5. Guarda la receta resultante como estilo propio en `mi-edicion/estilos/<nombre>.md` (formato de `editor/estilos/`), para reutilizarla en todos sus vídeos.
6. Cumple siempre `../editar-reel/criterios.md`. Copia el método, no la marca, los textos ni las caras de otro creador.
