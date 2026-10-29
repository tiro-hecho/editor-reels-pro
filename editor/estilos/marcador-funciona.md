# Estilo «Marcador funciona / no funciona» (APROBADO: «me gusta, guárdalo», 24/10/2026)

Formato viral copiado de un reel de 2,1 M de visitas (referencia en `referencias/formatos-virales/funciona_ref.mp4`).
Para vídeos de mitos o sí/no: «¿esto funciona?» → veredicto. Motor: `motor/marcador-funciona/` (`formato.py` → `marcador.py` → mezcla).

## Cómo se ve
- **Marcador fijo arriba**: barra negra translúcida a todo lo ancho (y=200), «✓ FUNCIONA» verde a la izquierda y «✕ NO FUNCIONA» rojo a la derecha, raya fina en medio. **El lado de «Funciona» va hacia donde señala la persona** (en el vídeo de José, a la izquierda de la pantalla).
- **Cada mito**: su foto (fotograma real de B-roll, cuadrada, borde blanco) entra grande sobre el pecho con rebote; el mito escrito justo debajo del marcador, encima de la cabeza (nunca sobre la cara).
- **Veredicto**: al oírlo sale ✓ verde o ✕ roja en la esquina de la foto y la foto vuela a su columna (112 px, 3 por fila). El marcador crece a una segunda fila cuando hace falta.
- **Subtítulos**: solo en las respuestas, negrita blanca en minúscula, palabra a palabra, la clave más grande; sin repetir «no funciona» (ya lo dice la ✕). Con espacios entre palabras (no usar flex en el contenedor).
- **Sonido**: pop al entrar la foto, error / ding en el veredicto, whoosh al volar. Música electro swing.

## Zona segura (todas las redes)
Todo entre x 66 y 934, marcador por debajo de y 200, nada importante por debajo de 1330 y nada en la franja derecha de botones.

## Rechazado en este formato
- Emojis y recortes automáticos de objetos (salían manchas): usar fotos reales del B-roll.
- Rojo sobre pared blanca sin barra detrás (no se leía), mito + subtítulo a la vez, subtítulos pegados.

## Motor (listo para Mac y Windows)
1. Copia `editor/motor/marcador-funciona/formato.py` a la carpeta del proyecto y cambia solo su contenido (títulos, bloques, textos, fotos).
2. En `montaje.json`: `"estilo": "marcador-funciona"`, la música y los tramos medidos con `cortes_energia.py`.
3. Monta con `editor/motor/comun/montar.py <proyecto>`.
