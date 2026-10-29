# Estilo «Errores con gráficos detrás del cuerpo» (APROBADO: 27/10/2026)
Para: listas de errores o consejos numerados («5 errores al entrenar pierna»), grabando cada punto en un sitio del centro.

## 1. Estructura
- **Gancho:** número gigante de la lista (p. ej. «5») en el color de la marca, DETRÁS de la persona; arriba, placa con el número + título y una fila de casillas 01–05 (la que más importa con 🔥).
- **Cada punto:** la placa cambia (01, 02…) y la casilla se enciende; un gráfico propio sale de lo que pasa en el plano y va DETRÁS del cuerpo:
  - técnica → marco de escáner que recorre el cuerpo y «✕ TÉCNICA INCORRECTA»;
  - peso → solo el número de kilos gigante subiendo (nada más: no cargar);
  - repeticiones → anillo que cuenta hasta «25+» con «POCO PESO»;
  - movilidad → medidor tipo velocímetro que se queda corto en rojo;
  - progresión → gráfica: lo ideal sube y lo real se queda plano, «ESTANCADO».
- **Cierre:** captura REAL de la ficha de Google del centro subiendo detrás + «5,0 ★★★★★ · N opiniones» (datos reales).

## 2. Subtítulos
Blancos, Inter Bold 96 px, palabra a palabra, **más abajo (y ≈ 1250) y nunca encima de una animación**.

## 3. Reglas
- Sin sombras ni brillos en textos y gráficos.
- Recortes de la persona limpios: máscara u2net afinada (borde firme, 1-2 px hacia dentro, huecos pequeños rellenos, SIN mezclar fotogramas porque deja halo). `afina_mascaras.py`.
- Cortes por energía real de la voz (`cortes_energia.py`), nunca con los tiempos de Whisper a pelo.

## 4. Sonido
Pack Pixabay: whoosh + pop + ding por punto, y uno propio por gráfico (riser/glitch, teclas/puñetazo, impacto, swipe…); cierre con ding y público suave. Música por debajo de la voz (aprobada con coastal_sprint).

## Motor (listo para Mac y Windows)
1. Copia `editor/motor/errores-detras/formato.py` a la carpeta del proyecto y cambia solo su contenido (títulos, bloques, textos, fotos).
2. En `montaje.json`: `"estilo": "errores-detras"`, `"detras": true` (los gráficos van detrás del cuerpo), la música y los tramos medidos con `cortes_energia.py`.
3. Monta con `editor/motor/comun/montar.py <proyecto>`.

