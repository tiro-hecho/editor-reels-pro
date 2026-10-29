# Estilo «collage-retro-podcast»

**Para:** Podcast con plano natural; historias personales, mentalidad, emprendimiento. ~40 s.
**Paleta:** amarillo pálido en letra manuscrita, chips lima #F2FA7A, insertos retro y de papel. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Rótulo de nombre: el nombre en sans blanca con una línea de cargo pequeña resaltada.
2. Subtítulos: línea blanca pequeña + palabra clave grande en manuscrita amarillo pálido que se solapa con la línea.
3. Inserto retro: una imagen de película antigua con un cuadro de diálogo de ordenador de los 90 con el texto en mayúsculas pixeladas.
4. Muro de titulares: fondo negro, titulares y fotos desenfocados desplazándose y una línea blanca condensada enorme en el centro.
5. B-roll cenital (portátil en una mesa) con palabras blancas pequeñas; luego un plano cálido con chips lima tipo checklist apareciendo a la derecha.
6. Muro de fotos: fondo gris, fotos pequeñas apareciendo y una línea blanca con una palabra en serif roja.
7. Escena de polaroids: una pila de polaroids cayendo sobre un fondo con el subtítulo encima.
8. Escena de carpetas en papel blanco: pestañas de carpeta pastel apilándose con etiquetas pequeñas y una línea negra con palabras clave en caja roja.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
