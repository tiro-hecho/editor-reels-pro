# Estilo «Dos barras: si quieres X, haz Y» (APROBADO: 27/10/2026)
Para: vídeos de «si quieres esto, haz esto» (objetivo → consejo), uno detrás de otro.

## 1. Estructura
- Dos columnas arriba, sobre la pared y **sin tocar la cara**: izquierda «SI QUIERES» (barra roja), derecha «HAZ ESTO» (barra verde).
- Cada bloque: el objetivo cae en la caja izquierda al decirlo y los pasos se escriben a la derecha al decirlos.
- Entre bloques las cajas se vacían y se rellenan; el último bloque es la llamada a la acción (centro, ciudad).

## 2. Subtítulos
Blancos, Inter Bold 96 px, interletra −0.055em, palabra a palabra sobre el pecho (y ≈ 1060).

## 3. Gráficos
- Columnas de 440 px en x 70 y x 570, a y 230.
- Barra: 84 px de alto, esquinas de 14 px, Anton (condensada) 46 px; rojo #FF3B30 y verde #21C45D (solo malo/bueno).
- Caja: rgba(14,14,16,.62), esquinas de 14 px. Objetivo en Condensed Black 64 px; pasos en Bold 40 px.
- Entrada: las barras bajan con muelle en el segundo 0; cada palabra sale de una máscara desde abajo.

## 4. Ritmo
Empieza hablando en el 0. Cortes en el silencio real (por energía de voz), velocidad 1,07×, sin muletillas.

## 5. Sonido
Whoosh rápido al entrar las barras, swoosh entre bloques, pop + brillo al caer cada objetivo, tick o ding en cada paso y «level up» + boom en el último. Música de hip-hop suave a −16 dB con sidechain.

## Motor (listo para Mac y Windows)
1. Copia `editor/motor/dos-barras/formato.py` a la carpeta del proyecto y cambia solo su contenido (títulos, bloques, textos, fotos).
2. En `montaje.json`: `"estilo": "dos-barras"`, la música y los tramos medidos con `cortes_energia.py`.
3. Monta con `editor/motor/comun/montar.py <proyecto>`.

## 7. Prompt para pedirlo
«Edita con el estilo dos-barras: SI QUIERES en rojo a la izquierda y HAZ ESTO en verde a la derecha, el objetivo cae al decirlo y los pasos se escriben al decirlos, subtítulos blancos en el pecho y level up en el último.»

## Qué NO copiar
Cajas que bajen hasta la cara, textos largos (máximo 2 líneas por paso), rojo o verde para algo que no sea malo/bueno.
