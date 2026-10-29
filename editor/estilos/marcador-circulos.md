# Estilo «Marcador con círculos» (APROBADO: «me flipa», 26/10/2026)
Referencia: vídeo de un centro de entrenamiento, «¿funciona o no funciona?»: alguien fuera de cámara pregunta cosas y la persona da su veredicto.

## 1. Estructura
- La persona responde a preguntas que alguien hace **fuera de cámara**. Se usan **solo las tomas buenas**; la conversación de preparación se quita.
- Cada pregunta: entra la cosa en un círculo → la persona explica → veredicto → la foto vuela a su columna.
- Cierre: «¿y seguirnos? funciona», con el «level up».
- **La tarjeta final con el logo no va siempre**: solo si encaja.

## 2. Subtítulos
Preset **02-pecho** para la explicación. **No aparecen mientras la foto vuela** a su columna.

## 3. Gráficos (la clave del estilo)
- **Marcador arriba:** barra negra translúcida (rgba 14,14,16,.82) a todo el ancho, desde y=200. Encima, «FUNCIONA» en verde #21C45D a la izquierda y «NO FUNCIONA» en rojo #FF3B30 a la derecha, en Anton (condensada) de 60 px, con una línea vertical blanca al 55 % en el centro.
- **Círculo grande sobre el pecho:** 380 px, borde blanco de 9 px, con la pregunta debajo en Inter Bold de 64 px.
- **Veredicto:** el círculo se ilumina en verde o rojo (borde y halo) y aparece una insignia ✓ o ✕.
- **Vuelo:** la foto vuela a su columna y se queda como círculo de 92 px (4 por fila), con su nombre debajo (21 px).
- **Fotos reales:** fotografías de libre uso (Pixabay) de cada cosa, o el logo del centro. **Nada de emojis ni recortes automáticos.**

## 4. Ritmo
Sin preguntas de relleno ni charla de preparación: se corta en los silencios reales y se empieza hablando desde el segundo 0.

## 5. Sonido
Efectos de `4-efectos-sonido/miticos/`:
- pop al entrar el círculo;
- «malo» (zumbador corto, −30 dB) o «bueno» (tick, −20 dB) en el veredicto;
- swoosh al volar a la columna;
- cierre «¿y seguirnos? funciona» con el «level up» (−19 dB).

## 6. Prompt para pedirlo
«Edita con el estilo marcador-circulos: quita la conversación de preparación, marcador FUNCIONA / NO FUNCIONA arriba, cada cosa en un círculo con foto real sobre el pecho y la pregunta debajo, al dar el veredicto se ilumina en verde o rojo con ✓/✕ y vuela a su columna, subtítulos estilo 2 y efectos míticos.»

## Qué NO copiar
Emojis o recortes automáticos en vez de fotos, subtítulos encima del vuelo, la tarjeta final con logo cuando no pinta nada.

## Motor (de referencia)
`editor/motor/marcador-circulos/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).

