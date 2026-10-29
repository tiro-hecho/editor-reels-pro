# Subtítulos · estilo 2 «pecho» (APROBADO)

Aprobado el 26/10/2026 en dos reels de un centro de entrenamiento.

Son subtítulos grandes, blancos y limpios, **a la altura del pecho**. Cada palabra **sube desde dentro de su propio renglón**, como si saliera de una ranura, y se enfoca justo al decirse. Al acabar el bloque, todo sube un poco, se desenfoca y se va. Mira `muestra.png`.

Para pedirlo: **«subtítulos estilo 2»** o **«subtítulos pecho»**.

## Aspecto

| | |
|---|---|
| Fuente | **Helvetica Neue Bold** (en Windows: Inter Bold de `recursos/fuentes`) |
| Tamaño | 100 px sobre 1080×1920, interletra −0,055 em (−5,5 px), interlínea 0,9 (90 px) |
| Color | blanco puro. Sin caja, sin fondo y sin colores |
| Sombra | ninguna |
| Caja | 780 px de ancho, centrada (x 150–930). Texto centrado |
| Mayúsculas | todo en minúscula. Se quitan comas, puntos, «¿?» y «¡!» |
| Altura | `--top 1030` por defecto: la primera línea queda en el pecho. Súbela o bájala según el encuadre, sin tapar la cara ni bajar de y = 1440 |

## Cómo se agrupan las palabras

- Bloques de **3 palabras como mucho**. Si no caben en 780 px, ocupan 2 líneas muy juntas.
- Un bloque se cierra con un signo de puntuación, con una pausa de más de 0,3 s o con `"br": 1` en `palabras.json` (última palabra de cada tramo de corte).
- El bloque aguanta como mucho 0,25 s después de la última palabra, sin solaparse con el siguiente.

## La animación

Para cada palabra, desde 0,04 s antes de que se diga:

- **Sube desde su renglón, recortada**: empieza 0,95 líneas más abajo y aparece desde abajo dentro de su línea (efecto máscara).
- **Se enfoca**: de 7 px de desenfoque a nítida.
- **Crece** del 92 % al 100 %.
- Todo con ease-out cúbico en 0,24 s.
- **Salida** del bloque, en los últimos 0,14 s: sube un 30 % de la línea, se desenfoca 6 px y se desvanece.

Todo esto está en `subtitulos_pecho.py`. No hay que programarlo cada vez.

## Cómo se usa

1. Monta el vídeo y saca `palabras.json` con las palabras **en el tiempo del montaje final**: `w`, `s` y `e`, más `"br": 1` en la última palabra de cada tramo. Corrige antes las palabras mal transcritas.
2. Genera los subtítulos:
   ```bash
   python3 subtitulos_pecho.py palabras.json subs/ --top 1030 --dur 60.5 --hasta 57.0
   ```
   `--hasta` es el segundo en que entra el cierre o un rótulo grande: desde ahí ya no hay subtítulos.
3. Superponlos:
   ```bash
   ffmpeg -i montaje.mp4 -framerate 30 -i subs/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p" -c:a copy final.mp4
   ```
   En la orden final de ffmpeg, como mucho 5 entradas.
4. Para revisarlo sin generar todo: `--muestra 1.0,4.2,9.8` saca solo esos instantes.

## Revisión antes de entregar

- Hoja de fotogramas: que el bloque quede en el pecho, sin tapar la cara ni las manos si está enseñando algo.
- Que las palabras no se pisen y queden dentro de x 66–934.
- Que no haya bloques con palabras de dos frases distintas.

## Qué NO hacer con este estilo

- No ponerle sombra, caja ni colores, ni resaltar palabras: es blanco y limpio a propósito.
- No usar mayúsculas ni dejar puntuación.
- No ponerlo a la altura de la cara ni hacer bloques de más de 3 palabras.
