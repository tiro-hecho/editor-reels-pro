# Estilo «Boutique medidor» (v1, 23/10/2026, pendiente de aprobar)

Vídeo de ejemplo: el entrenador (un centro boutique, su ciudad), «lo malo, lo bueno y lo perfecto para la salud», 40 s. Está en `muestras/boutique-medidor.mp4`.
Para centros **boutique o premium** y formatos de **valoración**: malo/bueno/perfecto, funciona/no funciona, rankings. Más elegante y con más aire que los estilos de el centro: pocos colores, movimientos suaves y mucho espacio.
Motor: `../motor/boutique-medidor/`, en este orden: `plan.py` → `mascaras.py` → `cabeza.py` → `render.py` → `mezcla.py musica`.

## Idea
- **La marca, animada**: el logo de el centro son barras verticales. Se convierten en un **medidor de 3 barras** que se enciende con cada valoración: 1 barra (malo), 2 (bueno) y 3 en el color de acento (perfecto).
- Solo tres colores, los de la marca: tinta (#1E0101), blanco y acento coral (#FF4B2B). En otro cliente, los de su `marca.md`.
- Titulares en la tipografía condensada de la marca (Bayon). **Ojo: Bayon no tiene vocales con tilde en mayúscula** («DÍAS»); esas palabras van en Anton (condensada).

## Estructura
1. **Gancho**: «LO MALO / LO BUENO / LO PERFECTO» apilados, entrando cuando lo dice, cada uno con su mini-medidor; «para la salud» debajo. Todo **detrás de la persona**.
2. **Cada sección**:
   - arriba, un título pequeño con número de color y una línea fina («01 cardio o fuerza», «02 días a la semana»…);
   - al presentar una sección sin valoración, su palabra en grande detrás («DÍAS»).
3. **Cada valoración**: la palabra gigante (330 px) + el medidor, **detrás de la cabeza** (y≈650, para que la cabeza tape la parte de abajo). Entra con un rebote suave y un pequeño empuje de cámara (más fuerte en «perfecto»).
4. **Cortes a B-roll de 0,5–1,2 s** cuando nombra algo visual: fotos profesionales del cliente (de su web) y planos del centro vacío, con un zoom lento hacia fuera y un destello blanco de 2 fotogramas. Mientras dura el corte, los subtítulos bajan a y=1330.
5. **Cierre**: «PERFECTO» con las 3 barras en «todas las cosas perfectas» y, al decir el nombre, el logo del centro gigante en tinta detrás de la persona, con la dirección arriba.

## Subtítulos
Helvetica Neue Bold blanca, junta (−6 %) y con sombra mínima, la clave a 84 px. Sobre el pecho (y≈1090), siguiendo a la persona en horizontal y dentro de x 66–934.

## Sonido
- **Música**: «house fashion» (Pixabay 619982) a −21 dB con sidechain, arrancando en el segundo 11,5 para que su golpe caiga al terminar el gancho. Suena a marca de ropa: premium, nada de gimnasio.
- **Efectos**: pop en malo/bueno, golpe (flash + boom suave) en perfecto, swoosh en cada sección y flash en cada corte de B-roll.

## Comprobar
- Transcripción del final con el modelo grande, check_zonas, duración, y mirar que el texto gigante quede **detrás** de la cabeza.
- En la toma de la persona sentada hay arranques en falso («entrenar con un pla… espera»): transcribir por ventanas antes de elegir la toma.

## v2 (23/10/2026) — correcciones de el creador sobre la v1
- **Pesas que se iluminan**: «cuando toca malo, bueno o perfecto, que se ilumine la pesa». La pesa rosa se enciende en **rojo** (malo), la azul en **amarillo** (bueno) y la verde en **verde** (perfecto):
  - halo de luz alrededor;
  - tinte y brillo sobre el cuerpo de la pesa (recortada por forma y color, para no teñir la mano);
  - reflejo en el cajón;
  - pulso suave.
  - En el gancho se encienden las tres en orden.
  - Para que la luz caiga justo en la pesa, **la cámara no hace zoom** en este plano.
- **Ya no hay texto detrás de la cabeza** («que no sea igual que el otro»). La palabra va **en la pared, al lado de su pesa** (malo a la izquierda, bueno a la derecha, perfecto arriba en el centro), unida a ella por una **línea del color de la luz** que se dibuja, con el medidor debajo. La línea de la pesa del centro rodea a la persona por la derecha para no cruzarle la cara.
- **B-roll en vídeo, no en fotos** («fuerza, muy básico»): el propio entrenador en su centro. Ergómetro para cardio, press con mancuernas para fuerza y jalón + ergómetro alternados en «combinar».
- **Música**: el house no le gustó. Ahora va «trap luxury» (Pixabay 620136) a −22 dB.

## v3 (23/10/2026)
- Brillo rehecho («se ve fatal»): máscara fija de cada pesa (elipse + asa) sobre un fondo mediano sin manos; lo que tapa la pesa (manos) no se tiñe. Neón: la pesa toma el color manteniendo su volumen, borde de luz, resplandor cercano (10 px) y amplio (38 px) aditivos, destello blanco de 0,35 s al encenderse y pulso suave.
- Sonido de luz: interruptor + parpadeo de fluorescente (Pixabay 382714, 29596) y power-up en «perfecto».
- Música: hip hop enérgico (Pixabay 612652) desde el segundo 3, para que caiga el golpe al acabar el gancho.
- Cierre rehecho («muy cutre»): degradado oscuro arriba, logo blanco grande que se revela desde el centro, línea coral y dirección en mayúsculas espaciadas.

## v4 (23/10/2026)
- Fuera el medidor de tres rayas («cargado, se ve mal») y los títulos de sección.
- Gancho: las tres palabras salen en su color mientras se encienden sus pesas (sin lista apilada ni líneas).
- B-roll: cardio = bici de aire (fotos del cliente), nunca un ejercicio que no corresponda. Comprobar SIEMPRE que el plano es lo que se nombra.
- SFX con significado: malo = sonido de respuesta incorrecta, bueno = tick neutro, perfecto = sonido de acierto; más interruptor de luz suave.
- Música: percusión (Pixabay 618229).

## v5 (23/10/2026), elegido por el creador entre maquetas
- Opción 1: en cada valoración, zoom de cámara (×1,75) a la pesa que se enciende; la palabra en su color arriba a la izquierda, en la pared; los subtítulos bajan a y=1420. En el gancho, zoom rápido a cada pesa.
- Opción 6 (cierre): degradado oscuro arriba, «5,0» que cuenta desde 4,0, cinco estrellas que se encienden una a una, una frase real de una reseña y «14 opiniones en Google».
- Música elegida por él: electro swing (Pixabay 596999), desde el segundo 10,5.
- Truco: cuando no aciertes con lo visual o la música, manda 10 maquetas o 10 canciones numeradas y que elija.

## Motor (de referencia)
`editor/motor/boutique-medidor/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).
