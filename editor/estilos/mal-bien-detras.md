# Estilo «Esto está mal / esto está bien» con MAL y BIEN detrás del cuerpo (APROBADO: 28/10/2026)
Para: vídeos que enseñan un ejercicio mal y luego bien, uno detrás de otro.

## 1. Estructura
- **Gancho:** al decir «bien» y «mal», las palabras BIEN (verde #21C45D) y MAL (rojo #FF3B30) gigantes aparecen DETRÁS de la persona.
- **Cada ejercicio:** placa coral 01–04 con el nombre y fila de casillas. Tanda mala → «MAL» rojo gigante detrás + pastilla «✕ ASÍ NO»; tanda buena → «BIEN» verde + «✓ ASÍ SÍ». Sin ✕/✓ gigantes (cargan y chocan con la cabecera).
- **Cierre:** captura real de la ficha de Google + «5,0 ★★★★★ · N opiniones».

## 2. Clave del montaje
- Mirar el bruto cada 0,5 s y marcar dónde CAMBIA la ejecución: MAL = desde «¿esto está mal?» hasta el final de la tanda mala; BIEN = desde «esto está bien» y toda la tanda buena. No fiarse solo de cuándo lo dice: a veces lo dice antes, a veces durante y a veces al acabar.
- Demostraciones sin voz a 1,6–1,7×; con voz a 1,07×. Cortes por energía real de la voz.

## 3. Subtítulos y sonido
Subtítulos blancos abajo (y ≈ 1250), nunca encima de un gráfico. Malo: `miticos/malo1_corto` (−23 dB) + glitch suave; bueno: `miticos/bueno3_tick` + ding. Música por debajo de la voz (aprobada con Vlog Hip-Hop).

## Motor (listo para Mac y Windows)
1. Copia `editor/motor/mal-bien-detras/formato.py` a la carpeta del proyecto y cambia solo su contenido (títulos, bloques, textos, fotos).
2. En `montaje.json`: `"estilo": "mal-bien-detras"`, `"detras": true` (los gráficos van detrás del cuerpo), la música y los tramos medidos con `cortes_energia.py`.
3. Monta con `editor/motor/comun/montar.py <proyecto>`.

