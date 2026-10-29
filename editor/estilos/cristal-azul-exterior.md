# Estilo «cristal-azul-exterior»

**Para:** Persona a cámara en exterior; seguros, finanzas, servicios, inmobiliaria. ~23 s.
**Paleta:** azul cielo #2EA6F2 con brillo, interfaz de cristal esmerilado, textura de agua azul abajo. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Subtítulos: línea blanca pequeña en cursiva + palabras clave grandes en mayúsculas cursivas azul cielo con brillo.
2. Tarjetas de cristal sobre el pecho: tarjeta azul esmerilada con barra de progreso, pastilla oscura con ✓ verde, pastilla con escudo, pastilla blanca con emoji de mano.
3. Escena con degradado azul: el plano se encoge en una tarjeta redondeada y aparece una pastilla con emoji debajo.
4. Una polaroid cae sobre el pecho con una etiqueta roja y un pie de foto pequeño.
5. Chips con emoji junto al subtítulo.
6. Plano de foto: un ejemplo visual de la frase (p. ej. alguien en un juicio) con papeles volando por los bordes.
7. Cuatro esquinas blancas que se cierran sobre una foto.
8. Una textura de agua azul ondulada bajo todos los planos; barridos rápidos con desenfoque entre ideas.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
