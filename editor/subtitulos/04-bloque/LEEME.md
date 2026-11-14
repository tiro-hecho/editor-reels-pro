# Subtítulos · estilo 4 «bloque» (APROBADO)

Aprobado el 14/11/2026 en una VSL, inspirado en el tutorial «Viral Caption Animation» de Premiere Pro.

Cada frase se convierte en un **bloque**: la palabra clave **enorme** y las palabras pequeñas **colgadas en sus esquinas**. Las de antes de la clave van arriba a la izquierda y las de después, abajo a la derecha. Cada palabra aparece justo al decirse. Mira `muestra.png`.

Para pedirlo: **«subtítulos estilo 4»** o **«subtítulos en bloque»**.

## Aspecto

| | |
|---|---|
| Fuente | Helvetica Neue **Bold** para la clave y **Medium** para las pequeñas (en Windows, Inter 700 y 500 de `editor/assets/fuentes`) |
| Tamaño | clave hasta el 15,5 % del lado corto (168 px en 1080) y como mucho el 72 % de ancho; pequeñas al 27 % de la clave |
| Letras | muy juntas (tracking −0,045) |
| Color | blanco. **Sin sombra, sin caja y sin colores** |
| Colocación | centrado en `--cx`; la línea base de la clave en `--cy` (por defecto a la altura del pecho: y ≈ 1250 en vertical, 840 en horizontal) |
| Puntuación | se quita; todo en minúscula, como se dice |

**Ponlo siempre sobre una zona oscura del plano** (ropa oscura, fondo oscuro). Si el plano es claro ahí, mueve el bloque con `--cx`/`--cy`; nunca oscurezcas el fondo.

## Cómo se agrupan las palabras

- Marca la palabra clave de cada frase con `"k": 1` en `palabras.json`: el bloque se cierra en ella.
- Si un trozo no tiene clave, la palabra más larga hace de clave. Si es corto, se une al siguiente (así no quedan «pero» o «ya» sueltos).
- `"br": 1` cierra el bloque aunque no haya clave. Como mucho 7 palabras por bloque.

## La animación

- Cada palabra pequeña aparece al decirse: sube 8 px, escala de 0,94 a 1 y fundido, en 0,16 s con ease-out cúbico.
- La clave entra al decirse con escala de 1,1 a 1 y fundido en 0,2 s.
- El bloque siguiente sustituye al anterior.

## Cómo se usa

1. Saca `palabras.json` **en el tiempo del montaje final** (`w`, `s`, `e`) y marca las claves con `"k": 1`.
2. Genera los subtítulos:
   ```bash
   python3 subtitulos_bloque.py palabras.json subs/ --dur 60.5
   ```
   En horizontal: `--ancho 1920 --alto 1080`.
3. Superponlos:
   ```bash
   ffmpeg -i montaje.mp4 -framerate 30 -i subs/f%05d.png -filter_complex "[0:v][1:v]overlay=0:0:eof_action=pass,format=yuv420p" -c:a copy final.mp4
   ```
4. Para revisarlo sin generar todo: `--muestra 1.0,4.2,9.8`.

**Truco:** que salte el encuadre en cada corte (plano normal, cerrado, normal, más cerrado) para esconder los saltos. Así lo usamos en la versión aprobada.

## Revisión antes de entregar

- En la hoja de fotogramas, que el bloque no tape la cara y caiga sobre una zona oscura.
- Que quede dentro de la zona segura: x 66–934 e y 220–1440 en vertical.
- Una sola clave por bloque.

## Qué NO hacer con este estilo

- No ponerle sombra, caja, viñeta ni colores.
- No poner dos claves en un bloque ni dejar palabras de unión sueltas.
- No ponerlo sobre fondo blanco o claro.
