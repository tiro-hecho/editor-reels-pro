# Estilo «lima-apps-orbitando»

**Para:** Persona con micro y fondo gris suave; redes sociales, marketing, tecnología. ~36 s.
**Paleta:** lima #C9F25B con brillo, escenas de app en blanco. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Subtítulos: línea blanca pequeña en mayúsculas + la palabra clave grande en serif cursiva lima con brillo suave; algunas palabras caen letra a letra muy espaciadas.
2. Tarjeta lima: el plano se encoge en una tarjeta redondeada tintada de lima sobre blanco con brillo alrededor.
3. Escena social: su plano en una tarjeta pequeña con iconos 3D de apps orbitando alrededor y una línea negra en mayúsculas arriba.
4. Pantalla partida: B-roll en tarjeta arriba (dinero, calculadora, valla publicitaria), ella abajo, subtítulo entre ambas.
5. Escena de app en blanco: su plano dentro de un marco de app, un cursor pulsa un botón «Publicar», el marco se desliza y el subtítulo crece al lado.
6. Tarjeta de dato: un contador de visualizaciones («641K») en tarjeta esmerilada.
7. Pequeñas estrellas que brillan junto a palabras enumeradas.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
