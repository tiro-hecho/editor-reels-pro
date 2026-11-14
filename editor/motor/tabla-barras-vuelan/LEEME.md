# Motor de referencia «tabla-barras-vuelan»
No es un `formato.py` listo: es el motor completo de un reel real (Python + OpenCV + PIL + ffmpeg). Claude lo adapta a cada proyecto:
- Rutas de ffmpeg, fuentes, efectos y música → las del editor (`recursos-descargados/`, `editor/assets/`).
- La tabla es la función `capa_tarjeta(t)`. Cambia `FILAS` al guion del alumno: `(objetivo, consejo, segundo en que dice el objetivo, segundo en que dice el consejo, color)`, con los tiempos sacados de las palabras.
- `T_IN` (entra la tabla) y `T_OUT` (sale fila a fila). Mientras está la tabla, los subtítulos van arriba.
- Colores: `VERDE` para «SI QUIERES» y `ROJO` para «HAZ ESTO» (la columna derecha siempre en rojo).
- `CORTES`, `ZK` (zooms) y `TR` (transiciones) son del vídeo original: rehazlos con los cortes del alumno.
- 🔴 Comprueba la zona segura (y ≤ 1440) y que nada tape la cara con `reel.py revisar`.
`reel.py hoja t1 t2 …` para revisar · `reel.py <i0> <i1>` render por trozos · `mezcla_reel.py` sonido y final.
