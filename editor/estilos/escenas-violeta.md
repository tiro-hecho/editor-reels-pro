# Estilo «escenas-violeta»

**Para:** Persona a cámara en estudio con fondo azul o neutro; vídeos de opinión o consejo. ~24 s.
**Paleta:** violeta #8B5CF6, escenas blancas y lilas, una escena oscura con cuadrícula. Si el cliente tiene colores de marca, sustituye el color de acento por el suyo.
**Origen:** receta analizada de un editor de referencia que edita con Claude; probada en reels de alto rendimiento.

## Receta
1. Subtítulos: una línea blanca que se construye palabra a palabra; las palabras clave en negrita violeta debajo; las palabras que aún no ha dicho esperan en gris tenue.
2. Detalles: una línea de progreso fina con un punto que se desliza, un icono dentro de una palabra («Saltar ▸|») y un barrido de panel violeta entre planos.
3. Escena de vídeo sobre blanco: su plano bajo una cabecera de canal (avatar, nombre, suscriptores) y una barra de búsqueda con subrayado violeta.
4. Lista sobre la persona: la palabra clave en violeta y tres puntos con iconos pequeños violeta y un destello de luz suave.
5. Escena lila de formulario: pastilla «1. Pregunta» sobre una caja de respuesta punteada.
6. Escena oscura con cuadrícula: una tarjeta blanca («Plan») con puntos que aparecen uno a uno («Contenido», «Distribución», «Ventas»).
7. Banda inferior azul oscuro con palabras que se deslizan; título final en violeta.
8. Un círculo blanco con icono violeta que viaja por una curva discontinua; cada subtítulo entra desde un desenfoque.

## Reglas de movimiento (obligatorias en este estilo)
- Nada tiembla ni late de tamaño. Todo entra con una curva suave y un pequeño rebote, y se queda quieto el tiempo justo para leerse.
- Desenfoque de movimiento real (obturación de 180°: media de subfotogramas), nunca un emborronado de toda la imagen.
- Los fotogramas del bruto se usan 1:1, sin saltarse ni duplicar ninguno.
- Gráficos y textos se pintan en HTML/CSS con Chrome sin ventana, fotograma a fotograma (`motor/render_html.mjs`), y se superponen con ffmpeg.

## Sonido
Voz limpia a −14 LUFS, whoosh en las transiciones, ticks suaves al aparecer palabras y música baja. Si parece demasiado, lo es.

## Revisión antes de entregar
Exporta un fotograma de cada parte y comprueba el movimiento fotograma a fotograma; arregla todo lo que salte. Además, cumple `criterios.md` (zonas seguras, sin silencios, no tapar la cara).
