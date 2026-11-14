# Motor de referencia «motion-referencias»
No es un `formato.py` listo: es el motor completo de un reel real (Python + OpenCV + PIL + ffmpeg). Claude lo adapta a cada proyecto:
- Rutas de ffmpeg, fuentes y efectos → las del editor (`recursos-descargados/`, `editor/assets/`).
- Color de acento `YEL` y `MARCA_USUARIO` → de `mi-edicion/marca.json`.
- Tiempos: todo se ancla a palabras con `T("palabra", desde)`; cambia las listas (`GL`, `MC`, `LISTA`, `BARRAS`, `POS`, `EMO`) al guion del alumno.
- 🔴 Recolocar los gráficos dentro de la zona segura (y ≤ 1440): en el vídeo original van más abajo.
`reel.py hoja t1 t2 …` para revisar · `reel.py render i0 i1` por trozos · `mezcla_reel.py` sonido y final.
