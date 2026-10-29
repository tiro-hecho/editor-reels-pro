# Estilo «terracota-pantalla-partida»

**Para:** Plano cálido de entrevista o podcast largo; salud, bienestar, producto. ~50 s.
**Paleta:** terracota #B4562E, mayúsculas blancas gruesas, pantallas partidas redondeadas. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Subtítulos: línea blanca pequeña + palabras clave en mayúsculas blancas condensadas y gruesas; algunas sobre caja terracota; alguna en minúscula fina.
2. B-roll con un degradado terracota que sube desde abajo, un icono «!» redondo y una línea con un chip resaltado.
3. Pantallas partidas: dos o cuatro tarjetas redondeadas (persona, entrevistador, producto) con el subtítulo encima de la tarjeta superior y chips blancos con icono.
4. B-roll a pantalla completa con una línea de iconos pequeña y chips que se van sumando uno a uno.
5. Líneas de ✓: check redondo + texto blanco.
6. Filas de etiquetas: una estrella + un título y pastillas blancas debajo.
7. Etiquetas de nombre: pastilla blanca pequeña con avatar y nombre cuando aparece alguien nuevo.
8. Cámara: cambios entre plano medio y cerrado en las palabras fuertes.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
