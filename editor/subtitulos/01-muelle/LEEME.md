# Subtítulos · estilo 1 «muelle» (APROBADO)

Aprobado el 26/10/2026 («me encanta ese estilo de subtítulos»), en dos reels de producto (unboxing y haul) para una marca de cosmética.

Son subtítulos limpios, en bloques cortos, que **entran palabra a palabra con un pequeño rebote**: cada palabra sube unos píxeles, se enfoca y se asienta justo cuando se dice. Al acabar el bloque, las palabras suben un poco y se desenfocan. Mira `muestra.png`.

Para pedirlo: **«subtítulos estilo 1»** o **«subtítulos muelle»**.

## Aspecto

| | |
|---|---|
| Fuente | **Helvetica Neue Bold** (en Windows: Inter Bold de `recursos/fuentes`) |
| Tamaño | 64 px sobre 1080×1920, interletra −1 px (juntita), interlínea 63 px |
| Color | blanco puro. Sin caja, sin fondo y sin resaltar palabras clave |
| Sombra | muy suave, para leer sobre fondos claros: halo de 2 px y sombra de 12 px hacia abajo, en marrón casi negro (`#1E1817`) al 60 % y al 45 % |
| Caja | 600 px de ancho, centrada (x 240–840). Texto centrado |
| Altura | `--top 1310` por defecto. Si abajo hay manos o producto, súbela (en el unboxing fue `--top 1090`, a la altura del cuello). Nunca más abajo de y = 1440 |

## Cómo se agrupan las palabras

- Bloques de **3 palabras como mucho** y 560 px de ancho como mucho.
- Un bloque se cierra con un punto, una coma, una interrogación o una exclamación, o con una pausa de más de 0,3 s.
- **Nunca junta palabras de dos tramos de corte distintos**: la última palabra de cada tramo lleva `"br": 1` en `palabras.json`. Esto se pidió expresamente: un bloque tipo «ha hecho / Esto se» queda mal.
- Una palabra débil (de, la, que, en, y…) no se queda colgando al final del bloque: pasa al siguiente.
- El bloque aparece 0,08 s antes de la primera palabra y aguanta como mucho 0,25 s después de la última, sin solaparse con el siguiente.

## La animación (el «muelle»)

Para cada palabra, desde su instante de entrada t0 (0,06 s antes de que se diga, y como mucho 0,07 s después de la anterior):

- **Sube** desde 34 px más abajo con un rebote (`1 − e^(−6x)·cos(9x)` en 0,42 s).
- **Crece** del 90 % al 100 %.
- **Se enfoca**: pasa de 10 px de desenfoque a nítida en 0,2 s.
- **Aparece**: de transparente a opaca en 0,12 s.
- **Salida** del bloque, en los últimos 0,12 s: sube 18 px, se desenfoca 8 px y se va.

Todo esto está en `subtitulos_muelle.py`. No hay que programarlo cada vez.

## Cómo se usa

1. Monta el vídeo y saca `palabras.json` con las palabras **en el tiempo del montaje final**: `w`, `s` y `e`, más `"br": 1` en la última palabra de cada tramo. Corrige antes las palabras mal transcritas (marcas, nombres).
2. Genera los subtítulos:
   ```bash
   python3 subtitulos_muelle.py palabras.json subs/ --top 1310 --dur 60.5 --hasta 57.0
   ```
   `--hasta` es el segundo en que entra el cierre o un rótulo grande: desde ahí ya no hay subtítulos (nunca texto y subtítulo a la vez).
3. Superponlos:
   ```bash
   ffmpeg -i montaje.mp4 -framerate 30 -i subs/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p" -c:a copy final.mp4
   ```
   Si el vídeo lleva más gráficos en PNG, mejor dibuja todo en la misma secuencia o superpón primero los subtítulos. En la orden final de ffmpeg, como mucho 5 entradas.
4. Para revisarlo sin generar todo: `--muestra 1.0,4.2,9.8` saca solo esos instantes.

## Revisión antes de entregar

- Hoja de fotogramas: que ningún bloque tape la cara ni el producto que se está enseñando, y que no baje de y = 1440.
- Que no haya ningún bloque con palabras de dos frases distintas.
- Que las marcas estén bien escritas en los subtítulos aunque el transcriptor las escriba mal.

## Qué NO hacer con este estilo

- No ponerle caja, fondo de color ni palabras clave resaltadas: es limpio a propósito.
- No subir la sombra: tiene que parecer que no hay sombra.
- No hacer bloques largos ni de dos líneas llenas: se lee de un vistazo.
