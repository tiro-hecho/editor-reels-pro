# Estilo «Lista contador» (APROBADO: «me mola», 23/10/2026)

Vídeo de ejemplo: el entrenador (el centro), «5 errores en flexiones», 35 s. Está en `muestras/lista-contador.mp4`.
Para vídeos con **pasos o errores numerados**. La idea es **que se vea el ejercicio**: pocos elementos, ligeros y encima del cuerpo.
Motor: `../motor/lista-contador/`, en este orden: `plan.py` → `mascaras.py` → `cabeza.py` → `render.py` → `mezcla.py musica`.

## Lo que el creador corrigió de la v1 (no volver a hacerlo)
- ❌ **Sombras cargadas** detrás de los textos: ahora la sombra es mínima (desenfoque de 6 px y opacidad del 32 %).
- ❌ **Tarjetas blancas con icono** («✗ cadera caída»): todo está muy cargado. Fuera.
- ❌ **Barra de progreso 1/5** y «error 3/5»: sobra.
- ❌ **La ✗ encima de las flechas** del medio recorrido: sobrecarga.
- ❌ **Checklist con panel blanco de fondo**: ahora son líneas de texto con un ✓ verde fino, sin fondo.
- ❌ **Cierre con los nombres de los sitios en minúscula y básico**, y **el logo en todos los vídeos**: fuera el logo y el cierre lleva fotos.

## Lo que SÍ le gusta
- **Las flechas y los circulitos** que se dibujan sobre el cuerpo (anillo con onda en cadera, manos y cuello; flechas hacia fuera en los codos; regla con doble flecha en el recorrido).
- **La burbujita** («el que hace todo el mundo»): blanca y redonda, solo texto, y mientras está **no se ven los subtítulos**.
- La cortinilla de color con el número gigante en cada error.
- La música de percusión.

## Subtítulos (nuevo en este estilo)
- **Pequeños** (Helvetica Neue Bold de 58 px, la clave a 78) y **encima de la cabeza, siguiéndola**.
  - `cabeza.py` saca de la silueta el punto más alto de la persona en cada fotograma, con mediana y media para que no tiemble.
  - `render.py` aplica el mismo zoom que a la imagen.
- Límites: x entre 340 y 740, y entre 330 y 1380. Por debajo de la checklist cuando está, y por debajo del título en el gancho.
- Un bloque de más de 640 px se reduce entero.

## Cierre
- **Fotos de los centros detrás de la persona** (recortada con su silueta, como el texto gigante del otro estilo):
  - dos tarjetas de foto redondeadas, inclinadas ±5°, que entran deslizando cuando nombra los entrenamientos;
  - el nombre del centro en **MAYÚSCULA** (Helvetica Condensed Black) sobre un degradado oscuro en la parte de abajo de la foto.
- Las fotos tienen que ser **del cliente**: suyas o de nuestro rodaje. De Google, no (no son nuestras).
- Van en `fotos/centro1.jpg` y `fotos/centro2.jpg`.
- Sin logo.

## Sonido
- Música: «action sport percussion» (Pixabay 112926) a −23 dB, **arrancando en el segundo 1,0**, con sidechain de −12 dB.
  - Con otros puntos de arranque, un golpe de percusión se comía la «p» de «pectoral».
  - **Mover el arranque de la canción** es más eficaz que bajarla.
- Flash de cámara en cada cortinilla y en cada foto, swoosh suave al aparecer cada marca y pop en la burbuja y en los ✓.

## Comprobar siempre
1. Transcribir el final con el **modelo grande** y comparar palabra a palabra. Si una palabra falla solo con música, mover el arranque de la pista.
2. Que los subtítulos no choquen con la checklist ni con las fotos (mirar 6 fotogramas a tamaño real).
3. Que las marcas del cuerpo caigan sobre la parte correcta: se colocan a mano y duran solo lo que dura la demostración.

## v3 (23/10/2026) — correcciones de el creador sobre la v2
- **Gancho más creativo**: un número gigante (Helvetica Condensed Black, 1000 px, magenta) **detrás de la persona** que rueda 1-2-3-4 en 0,3 s y se clava en 5 con un golpe. En «el tercero» pasa a un **3 rojo** con una sacudida, y sale la burbuja. Arriba, solo «errores en flexiones».
- **Forma correcta**: la lista con ✓ quedaba «muy cutre». Ahora sale **una clave cada vez**, grande (80 px, máximo 700 px de ancho) y centrada arriba, que se descubre con un barrido de izquierda a derecha junto a un ✓ verde que se dibuja. Sale cuando llega la siguiente. Antes de la primera, «forma correcta» en verde.
- **Subtítulos**: a veces tapaban la cara o se salían. Ahora:
  - siempre dentro de x 66–934;
  - si el bloque toca la silueta de la persona (más del 4 % de su caja), sube de 20 en 20 px hasta que deja de tocarla; si no hay hueco arriba, va abajo (y=1420);
  - se ocultan mientras está la burbuja.
- **Fotos del cierre**: las de la **ficha de Google de cada centro**, que pidió el creador: fachada de centro 1 (Street View, con el rótulo «TRAINING CENTER») e interior de centro 2 (foto de la ficha). Van recortadas en 4:5 y detrás de la persona.

## v4 (23/10/2026): APROBADO («me mola, guárdalo»)
- Las claves de la forma correcta llevan una **pastilla oscura translúcida** (negro, 175/255) que se abre con el barrido, para que se lean sobre cualquier fondo. Sin ella «no se leía muy bien».
- Foto del centro: **del interior**, nunca la fachada (lo pidió el creador). Si la ficha de Google no tiene foto del interior, se pide al cliente.

## Motor (de referencia)
`editor/motor/lista-contador/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).
