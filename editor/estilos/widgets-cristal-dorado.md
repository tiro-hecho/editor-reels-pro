# Estilo «widgets-cristal-dorado»

**Para:** Persona a cámara con fondo oscuro y contraluz cálido; negocios locales, servicios, reseñas. ~18 s.
**Paleta:** dorado #E2C36B, widgets de cristal oscuro. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Subtítulos: una línea blanca pequeña que se construye palabra a palabra; la palabra clave debajo, grande, en una sans redondeada gruesa y dorada.
2. Bajo cada subtítulo aparece un widget de cristal oscuro: una pastilla de onda de audio, tres fichas de servicios con su nota, una barra de búsqueda de mapa, una nota de estrellas («4,7»), dos contadores enfrentados («Competencia» vs «Tú»), un contador de «personas alcanzadas» que sube.
3. Una barra dorada vacía bajo la palabra que se va llenando.
4. Escena gris: una cuadrícula de iconos de personas; unas cuantas se vuelven doradas una a una, con una pastilla dorada debajo («más clientes»).
5. Palabras fantasma: letras tenues y muy espaciadas que se asientan en su sitio.
6. Cámara: plano fijo; todo el movimiento está en los gráficos, cada widget entra con un pequeño rebote.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
