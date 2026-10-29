# Estilo «entrevista-serif-naranja»

**Para:** Entrevista en oficina luminosa, dos personas; negocio, tecnología, emprendimiento. ~28 s.
**Paleta:** naranja-rojo #F05A28 en serif cursiva, escenas blancas y oscuras. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Títulos de nombre: al aparecer cada persona, su nombre en blanco monoespaciado con su cargo debajo y una barra naranja fina a la izquierda.
2. Subtítulos: línea blanca pequeña en mayúsculas + palabras clave grandes en serif cursiva naranja; de vez en cuando una palabra en mayúsculas condensadas altas sobre caja naranja.
3. Muro de logos: fichas oscuras con logos grandes deslizándose y un titular blanco cruzando.
4. Escena blanca: líneas naranjas finas que salen de un sol en la esquina y una frase negra grande con una barra naranja bajo una palabra.
5. Escena de chat: degradado naranja suave, una tarjeta de mensaje que se escribe sola y un cursor que pulsa enviar.
6. Plano general: el subtítulo entre las dos personas; cortes entre plano general y primer plano en las palabras fuertes.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
