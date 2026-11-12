# Estilo «zambullida-epica»

**Para:** anuncio o vídeo de autoridad vertical con voz en off, sin grabar a nadie o con fotos reales, de 40-60 s a 60 fps. La cámara se mete dentro de los objetos y la escena siguiente se abre desde dentro.

**Aprobado el 2/11/2026** en un anuncio de 54 s para negocios de una región.

Hoja: `editor/catalogo/capturas/zambullida-epica.jpg`. Código: `editor/motor/zambullida-epica/` (el vídeo de ejemplo es `ejemplo.py`). Sale de los tutoriales de Bart_VFX (https://www.youtube.com/watch?v=cpQzSKuEAkM) y Vane Motion (https://www.youtube.com/watch?v=JUbXgxkSWXw), más cámara continua e historia de objetos.

## Aspecto
- Alternar gris Apple (236, 236, 239) o crema en lo limpio con negro, pizarra o madera en el problema y la autoridad.
- Sin subtítulos aparte: el texto es el gráfico. Helvetica junta, frase pequeña en regular y clave grande en negrita, centrado. Sin subrayados.
- Palabra gigante desenfocada detrás de cada escena y motas fuera de foco delante, con paralaje.
- Datos, fotos y sitios reales del negocio: dan más autoridad que cualquier efecto. Nada inventado.

## Flujo, en este orden
1. **Guion** con la voz definitiva, y ritmo rápido: una voz un 8 % más rápida queda bien con `atempo=1.08`.
2. **Tiempos:** transcribir con Whisper palabra a palabra a `voz/w.json` y repartir en frases con `tiempos.py`. Todo se sincroniza con `T(frase, palabra)`.
3. **Plan de escenas:** una idea visual por frase, algo nuevo cada 3 s como mucho y un gancho en el primer segundo. Cambiar objetos e ideas: lo que se reutiliza es el lenguaje, no las escenas.
4. **Escribir escenas** en `vf.py` (copia de `ejemplo.py`) a partir de las piezas de abajo. Elegir qué cortes son zambullida y cuáles latigazo.
5. **Hoja de control:** `python3 vf.py hoja t1,t2,... salida.jpg 8`. Corregir textos anchos (avisa con ANCHO), solapes y lo que se queme con la luz.
6. **Probar la mezcla antes del render:** `python3 mezcla.py pista.mp3 mezcla.wav`. Falla pronto si falta un efecto.
7. **`bash lanza.sh pista.mp3`** en segundo plano y desacoplado. Retoma lo que falta. En el vídeo de 54,6 s, unos 40 min.
8. **Medir:** movimiento por segundo (diferencia media entre fotogramas): ningún tramo largo por debajo de 1. Hoja de un fotograma por segundo y Whisper de la mezcla.
9. **Cambios parciales:** borrar solo los PNG de esos segundos y relanzar. La mezcla se rehace sin renderizar, así que se pueden entregar dos músicas.

## Movimiento: las piezas de `vf.py`
- **`zambulle(n, frase, dx, dy, dz, dur)`:** la transición estrella. Acelera hacia el objeto hasta que llena el plano y corta en un iris circular (`PORT`). `dx`, `dy` = posición del objeto respecto al centro. Para objetos pequeños, subir `dz`. Si la palabra final se tiene que leer, `dur=.24`.
- **`corte()` + `giro()`:** latigazo con corte en el pico de velocidad, y giro de 90° en tres cortes. Alternar con zambullidas; aquí 7 y 6.
- **`cam()`:** trayectoria + cámara en mano + golpe en cada palabra fuerte (`BEATS`). Vuelve a cero. Colocar las capas siempre con `rest()`, que usa `cam0()`.
- **`pildora_txt`:** punto → círculo → píldora con rebote; el botón se hunde antes de abrirse (Apple).
- **`Movil3D`:** móvil con perspectiva real, canto metálico, reflejo y pantalla viva. La pantalla es una función `pant(t)`: ver `pant_busca`, `pant_chat`, `pant_vieja`.
- **`Globo` + `geo(lon, lat, t)`:** globo de puntos que baja hasta un mapa con la región levantada. Colocar cosas por coordenadas. Contornos a mano: sirve para otra región cambiando el polígono.
- **`FotoPan`:** foto real a pantalla completa, abierta en círculo, con recorrido de cámara.
- **`FotoMorf`:** foto de círculo a rectángulo. **`HojaCurl`:** nota que se pasa. **`Liquido`:** esferas que se funden. Moneda con canto: reloj que gira y es dinero.
- **`gigante`, `bokeh`, `post`, `efectos`:** palabra de fondo, motas, brillo y rayos en escenas oscuras, luz que barre las claras, chispas, ondas y flash (`FX`, `FLASH`).

## Sonido
- Solo efectos aprobados: gancho y texto gigante = `boom`, revelado = `riser`, transición = `flash` o whoosh, texto = `pop`, bien = `bueno3_tick`, mal = `malo1_corto`, perfecto = `top2_levelup`, llamada a la acción = campanita (`ding_doble`).
- Efecto por cada acción visible, sin amontonar: 98 en 54 s. Un único grave de verdad, en el clímax.
- Estéreo: la voz al centro y los whoosh cruzando de lado a lado. `pon()` normaliza el pico: −11 los golpes, −17 los whoosh, −20 los pop. Reverberación corta solo en lo grande.
- Voz a −14,5 LUFS. Música 14 dB por debajo y 6 dB más al hablar, con limitador. Calla antes de los momentos clave y su subida más grande cae en el golpe (`mezcla.py` la busca sola).
- Estos niveles y esta densidad son los aprobados en este estilo, algo por encima de la regla general (música 16 + 7 dB, un efecto cada 2-4 s). Si suena cargado, volver a la regla general.
- Música: una canción de `editor/assets/musica/` distinta en cada vídeo, que vaya con la historia.

## Prohibido
- Glitch, rasgados, platillo invertido, disco de pesa y golpes graves seguidos: rechazados.
- Texto oscuro sobre fondo negro, y solapa de la hoja fuera de la nota.
- Umbral bajo en el brillo: quema papeles y móviles. Pantallas oscuras en escenas oscuras.
- Prometer en los textos cosas que la voz no dice.
- Enseñar pantallas con datos privados.

## Ojo al programar
- `HojaCurl` tarda minutos a tamaño enorme: ya limitado con L > 1100. Máximo 10 subfotogramas en zambullidas.
- Usar `pega()` para componer: `alpha_composite` directo revienta con piezas fuera de cuadro.
- Comprobar siempre la mezcla con Whisper: una caché por ruta relativa coló la voz de otro proyecto. Ya corregido en `mezcla.py`.
- El render es largo (unos 40 min para 55 s): lanzarlo en segundo plano y retomar lo que falte.

## Para usarlo
1. Copia `editor/motor/zambullida-epica/` entero a la carpeta del proyecto y renombra `ejemplo.py` a `vf.py`.
2. Pon `voz/voz.wav`, transcribe a `voz/w.json` y saca `voz/tiempos.json` con `tiempos.py`. Pon tu foto en `foto_persona.jpg` (y `foto_circulo.png`) y las fotos del sitio en `fotos/`.
3. Cambia `NOMBRE` (en `piezas.py`), `REGION` y `PUEBLO` (en `vf.py`) y reescribe las escenas para el guion nuevo. Para otra región, cambia el polígono del mapa.
4. Hoja de control, mezcla y `bash lanza.sh musica.mp3`. Los efectos salen de `editor/assets/efectos/` (si falta alguno, la mezcla avisa y sigue).
