# Estilo «podcast-chips-coral»

**Para:** Podcast o entrevista con plano oscuro; temas con conceptos y definiciones. ~37 s.
**Paleta:** coral #E0553A, chips blancos de interfaz, escenas con degradado claro. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Gancho: el invitado en una tarjeta redondeada desenfocada sobre blanco que se enfoca, con un chip coral con el tema sobre el pecho.
2. Subtítulos: línea blanca en mayúsculas con las palabras clave sobre caja coral; las frases siguientes se apilan como chips con iconos redondos.
3. Escena blanca: línea negra pequeña en mayúsculas, palabras clave en caja coral y una pila de fotos que se voltean debajo.
4. B-roll con un degradado coral que sube desde abajo y una línea blanca pequeña.
5. Pantalla partida: dos tarjetas redondeadas (invitado arriba, presentador abajo) con el subtítulo entre ambas y un chip coral.
6. Etiqueta de definición: un asterisco coral, la palabra y chips pequeños debajo.
7. Escena con degradado claro: titular coral arriba a la izquierda, una persona recortada, estrellas de cuatro puntas y tarjetas de interfaz que aparecen alrededor.
8. Línea de ✓ sobre B-roll: un check coral redondo + texto blanco en mayúsculas; cierre con una frase en caja coral.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
