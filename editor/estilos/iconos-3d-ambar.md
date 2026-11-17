# Estilo «Iconos 3D en ámbar» (APROBADO: 17/11/2026)
Para: una persona hablando a cámara en una sola toma fija (sentada o de pie) que hay que convertir en un reel con muchísima dopamina: algo nuevo cada 0,5-1 s, iconos 3D que giran, palabras gigantes en ámbar y un efecto de sonido en cada cosa que aparece. 1080×1920 a 30 fps, de 10 a 40 s.

## 1. Regla de oro
**Cada cosa que aparece suena, y nada tapa la cara.** El plano real no se toca de color; todo lo demás se coloca en los huecos (pared, pecho, mesa) y fuera de las zonas de botones (nada por encima de y = 220).

## 2. Escenas
- **Arranque:** entra desenfocado → nítido y un **arco de luz** fino barre por arriba (la firma del estilo; se repite 2-3 veces).
- **Esquinas de enfoque:** cuatro esquinas blancas que encuadran la cara un segundo, con un tic.
- **Pegatinas 3D:** iconos con volumen (canto extruido, perspectiva y brillo), **sin sombra**, que entran dando una vuelta con rebote y se quedan balanceándose en 3D. Uno o dos por idea («agencia» → megáfono y gráfica; «cámara» → cámara de cine y claqueta).
- **Tarjetas en cascada:** polaroids blancas casi rectas (radio 6 px) con icono y etiqueta («Restaurantes», «Peluquerías»…) que caen una a una, giradas en perspectiva, con un barrido amarillo difuso detrás.
- **Objeto que cae sobre la palabra:** un pin, un apretón de manos o una bolsa de dinero cae y rebota (se aplasta al aterrizar) encima de la palabra gigante.
- **Ruptura de fondo:** fondo blanco con rejilla discontinua y nodos naranjas, la persona recortada en blanco y negro con un círculo amarillo detrás y un titular negro gigante.
- **Billetes 3D** cruzando por delante, desenfocados (profundidad), nunca delante de la cara.
- **Final en tipografía cinética apilada:** cada requisito en grande (Anton, tinta) con un check ámbar que se dibuja; al entrar el siguiente, el anterior sube, encoge y se apaga. Remate en dos piezas: frase en tinta + palabra gigante ámbar **detrás de la cabeza**, con un bocadillo 3D.

## 3. Tipografía
- Frase pequeña: Inter 42 px blanca, palabra a palabra con desenfoque → nítido.
- Palabra clave: **Anton con degradado ámbar** (255,228,92 → 246,150,30) y halo dorado. Cae letra a letra (escala 1,7 → 1, 0,03 s entre letras) y luego le pasa un brillo. Algunas van detrás de la cabeza (silueta con rembg).
- El halo se calcula con margen alrededor de cada letra: si se recorta, se ve una caja detrás.
- Nada de cajas, pastillas ni burbujas detrás del texto, y nunca mezclar emoji + letra fina + palabra gigante en la misma línea.

## 4. Movimiento
- Zoom con muelle cada 2-3 palabras (entre 1,16 y 1,42) y empuje lento continuo. Sin temblor, sin rayos, sin chispas.
- **Una transición distinta en cada corte:** barrido horizontal con desenfoque de movimiento + 2 fotogramas con el color invertido; zoom a través; barrido vertical con destello cálido; zoom suave.

## 5. Sonido (unos 45 efectos en 13 s)
Efectos **agudos, cortos y con aire**, casi sin graves (se les quita lo que está por debajo de 180 Hz): pop por icono, papel/clic por tarjeta, obturador en la cámara, swish + cristal en cada palabra gigante, aire en los billetes, glitch en el invertido, swish en cada barrido, tic suave al empezar cada frase y en cada check. Nada de booms, golpes graves ni risers. El pico de cada efecto cae justo en el fotograma de su aparición. Voz delante (+5 dB, sin loudnorm) y música muy baja (−31 dB).

## Motor (probado en Windows)
`editor/motor/iconos-3d-ambar/`. Necesita `faster-whisper` y `rembg` (como el resto del editor).
1. **Iconos:** abre `iconos/generar_iconos.html` en Chrome, descarga `emo_hoja.png` a esa carpeta y ejecuta `python corta.py` (en Mac salen los emojis 3D de Apple; en Windows, los de Microsoft). Puedes poner tus propios PNG en `iconos/` de tu proyecto con el mismo nombre.
2. En la carpeta del proyecto: `python <motor>/prep.py bruto.mov tramos.json` (tramos = `[[inicio, fin], …]` de las frases que quieres) → `base.mov`, `cuts.json` y fotogramas.
3. `python <motor>/mask.py` → silueta y cara por fotograma (tarda; en Windows lánzalo y déjalo correr).
4. Cambia el **contenido** (todo se ata a palabras con `wt("palabra")`): frases del subtítulo en `v1.py` (`LINEAS`), palabras gigantes, pegatinas, caídas y tarjetas en `v3.py` (`GIG`, `STK`, `DROP`, `NEG`), final en `v6.py` (`TXT`).
5. `python <motor>/v6.py fotos 1.6 2.6 6.6 12.6` y `python <motor>/hoja.py` → revisa cara, bordes y zonas de botones.
6. `python <motor>/v6.py` (imagen → `video.mp4`) y `python <motor>/mezcla.py` (sonido → `final.mp4`). Si dejas `musica.mp3` en el proyecto, la usa.
