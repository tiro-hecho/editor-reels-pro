# Subtítulos · estilo 3 «repartidos» (APROBADO)

Aprobado el 26/10/2026 en un reel de un centro de entrenamiento, inspirado en un reel viral.

Las palabras de cada frase **se reparten por la pantalla en zigzag**: una por renglón, alternando izquierda y derecha, y van apareciendo según se dicen. Llenan el plano sin tapar la cara. Mira `muestra.png`.

Para pedirlo: **«subtítulos estilo 3»** o **«subtítulos repartidos»**.

## Aspecto

| | |
|---|---|
| Fuente | **Helvetica Neue Condensed Bold** (ver «Fuente» abajo) |
| Tamaño | 104 px sobre 1080×1920 |
| Color | blanco. Sin caja, sin fondo y sin colores |
| Sombra | ninguna |
| Colocación | una palabra por renglón. Pegada a la izquierda empieza en x 70; pegada a la derecha acaba en x 1010 |
| Renglones | la palabra j va en `top + j·112` px |
| Altura | `--top 960` por defecto, por debajo de la cara. Con 4 palabras, el bloque llega hasta y ≈ 1400 |
| Puntuación | se quitan comas, puntos, «¿?» y «¡!». Se respetan mayúsculas y minúsculas |

### Fuente

El script busca, por orden:
1. `recursos/fuentes/HelveticaNeueCondensedBold.ttf` del kit, si la has puesto ahí (no viene incluida por licencia).
2. En Mac, la Helvetica Neue Condensed Bold del sistema (`/System/Library/Fonts/HelveticaNeue.ttc`). Es la que se usó en la muestra.
3. En Windows, **Inter con peso 700** de `recursos/fuentes`. No es condensada: las palabras salen más anchas, pero el estilo funciona igual.

## Cómo se agrupan las palabras

- Bloques de **4 palabras como mucho**.
- Un bloque se cierra con un signo de puntuación, con una pausa de más de 0,35 s o con `"br": 1` en `palabras.json`.
- Dentro del bloque, las palabras alternan lado. El lado de la primera palabra también alterna de un bloque al siguiente (izquierda, derecha, izquierda…).

## La animación

Cada palabra aparece **justo al decirse**, con ease-out cúbico en 0,22 s:

- **Sube** 24 px.
- **Se enfoca**: de 8 px de desenfoque a nítida.
- **Aparece**: de transparente a opaca.
- **Salida** del bloque: fundido de 0,12 s.

Todo esto está en `subtitulos_repartidos.py`.

## Cómo se usa

1. Saca `palabras.json` **en el tiempo del montaje final** (`w`, `s`, `e` y `"br": 1` al final de cada tramo).
2. Genera los subtítulos:
   ```bash
   python3 subtitulos_repartidos.py palabras.json subs/ --top 960 --dur 60.5 --hasta 57.0
   ```
3. Superponlos:
   ```bash
   ffmpeg -i montaje.mp4 -framerate 30 -i subs/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p" -c:a copy final.mp4
   ```
   En la orden final de ffmpeg, como mucho 5 entradas.
4. Para revisarlo sin generar todo: `--muestra 1.0,4.2,9.8`.

## Revisión antes de entregar

- Hoja de fotogramas: que ningún renglón tape la cara. Si la persona está más baja en el plano, baja `--top`; si el cuarto renglón pasa de y = 1440, acorta o sube.
- Que las palabras de un bloque no se pisen.
- Que las palabras de la izquierda empiecen en x 70 y las de la derecha acaben en x 1010.

## Qué NO hacer con este estilo

- No ponerle sombra, caja ni colores.
- No centrar las palabras: el zigzag izquierda/derecha es el estilo.
- No subir los subtítulos a la cara ni meter más de 4 palabras por bloque.
