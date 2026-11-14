# Estilo «motion-referencias»: técnicas de After Effects por código (APROBADO: 15/11/2026)
Para: persona hablando a cámara (vertical, 40-70 s) con un guion de pasos, cifras y consejos. Cada idea lleva una técnica distinta, copiada de plantillas profesionales (Jitter y Motion Array). Opinión al aprobarlo: «me flipa… súper épico».

## 1. Técnicas (una por idea; ninguna más de dos veces)
| Técnica | Cuándo |
|---|---|
| **Pantalla rota**: cifra gigante en el color de marca con líneas de escaneo, cortes que se desplazan, separación de color, brillo y etiquetas tipo terminal que se teclean | El precio o la cifra del gancho |
| **Corte en el mismo sitio**: la palabra con marcador de color no se mueve y cambia el soporte (periódico, pantalla, cartel) | Enumerar 3 cosas |
| **Cursor**: un puntero arrastra un marco discontinuo con tiradores, dentro va el plano siguiente pixelado y el marco crece a pantalla completa | Transición a «lo primero…» |
| **Columnas de móviles** que suben y bajan (mapa, reseñas, fotos, servicios) | Ficha de Google o una app |
| **Cartel**: palabra gigante con relleno del propio vídeo teñido y cursiva serif encima | GRATIS, SÍGUEME |
| **Desplazamiento documental**: el plano sube en bucle con desenfoque, con «02» gigante translúcido | Transición a «lo segundo…» |
| **Rueda de palabras**: la central nítida con flecha y las demás grises y desenfocadas | «Hay muchas opciones…» |
| **Tarjetas en órbita** (anuncios con fotos de su vídeo) en arco bajo la cara | Redes y anuncios |
| **Emoji 3D** que rebota y saluda, sin pastilla | «Ojo», «sígueme» |
| **Barras de encuesta** con etiqueta en cursiva, regla y número que cuenta | Repartos de dinero o tiempo |

## 2. Subtítulos
Helvetica/Inter Bold 74 px, blancos y sin caja, encima de la cabeza. La frase aparece en gris tenue y desenfocada y cada palabra se enciende en blanco al decirla; las claves en el color de marca.

## 3. Composición
Gráficos en el pecho sobre un degradado oscuro suave, **siempre dentro de la zona segura (y ≤ 1440)** y sin tocar la cara. Color del vídeo sin tocar. Fundido corto con leve acercamiento en el resto de cortes.

## 4. Sonido
Voz a −14,5 LUFS, música suave 15 dB debajo con sidechain. Cada técnica con su sonido: glitch + golpe, clic de ratón, pop por palabra en la rueda, swoosh en la órbita, pop en el emoji, clic + golpe en las barras.

## Motor (de referencia)
`editor/motor/motion-referencias/` (`reel.py`, `mezcla_reel.py` y `LEEME.md`). Claude lo adapta al guion: ancla cada técnica a la palabra con `T("palabra")`.

## Prompt para pedirlo
«Edita con el estilo motion-referencias: una técnica distinta en cada idea (pantalla rota en la cifra, corte en el mismo sitio, cursor, móviles, cartel, rueda, órbita, emoji y encuesta) y subtítulos que pasan de gris a blanco.»

## Qué NO copiar
Repetir la misma técnica en todo el vídeo, gráficos sobre la cara o fuera de la zona segura, pastillas detrás del texto, datos inventados en las barras.
