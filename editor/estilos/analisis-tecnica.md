# Estilo «Análisis de técnica» (APROBADO: «me mola», 26/10/2026)
Referencia: vídeo de un entrenador, «sentadilla: no hagas esto si quieres piernas fuertes» (27 s). Inspirado en las repeticiones de los análisis deportivos: congelar el gesto y dibujar encima.

## 1. Estructura
1. **Gancho (0–1,3 s):** mientras dice «no hagas esto…», se ve el gesto malo (B-roll del propio bruto, sin voz encima cortada) con una pastilla «✕ así no». Luego entra la persona.
2. **Error:** pastillas cortas con lo que falla («✕ mucho peso», «✕ recorrido a medias»). En el fondo de la repetición mala, **la imagen se congela 0,9 s** y se dibuja: línea discontinua blanca a la altura de la referencia (p. ej. la paralela) y el segmento del cuerpo en rojo (cadera→rodilla) con dos puntos blancos; etiqueta «no llega a la paralela».
3. **Forma correcta:** pastillas verdes («✓ peso adecuado», «✓ rompe la paralela»).
4. **Repetición a cámara lenta (0,5×, ~2,8 s)** de la repetición buena justo después de explicarla: pastilla «CÁMARA LENTA · 0,5×» arriba; al llegar al fondo el segmento se dibuja en verde por debajo de la línea + «✓ por debajo de la paralela».
5. **Cierre:** foto del centro con la persona en ventanita al decir la ubicación; «escríbenos por privado».

## 2. Subtítulos
Preset **02-pecho** o el de la marca (Inter Bold blanca, sin sombra, una fila). Se ocultan durante el congelado y la cámara lenta (no hay voz).

## 3. Gráficos y B-roll
- Todo **por debajo del pecho, nunca encima de la cara**. Pastillas redondeadas de color (rojo #FF3B30, verde #21C45D, color de marca) con texto blanco Inter Bold.
- Las líneas se miden **en el fotograma congelado** (coordenadas reales del cuerpo) y se dibujan con trazo animado (0,35 s).
- **Sin golpes de zoom durante el congelado ni la cámara lenta**: las líneas dependen del encuadre.

## 4. Ritmo
- Cortes en los silencios reales del bruto (energía, no las marcas de Whisper). **Las repeticiones van enteras**: nunca cortar dentro del movimiento.
- Golpe de zoom en cada palabra clave y en cada cambio de plano; nada de más de 2 s sin estímulo.

## 5. Sonido
- Obturador de cámara al congelar, «rayado» suave al dibujar, error bajito en la etiqueta roja.
- Subida de tensión (riser) que termina justo en el fondo de la cámara lenta + golpe seco + ding doble.
- Música por debajo de la voz (−16 dB medido), con corte seco antes del cierre.

## 6. Prompt para pedirlo
«Edita con el estilo análisis-de-técnica: congela la repetición mala en el punto que falla y dibuja la línea sobre el cuerpo en rojo, repite la buena a cámara lenta y dibújala en verde, pastillas ✓/✕ por debajo del pecho, sin tapar la cara, repeticiones enteras sin cortes dentro.»

## Qué NO copiar
Texto gigante detrás de la persona tapando la cara, tarjetas grandes encima, sombras. Las etiquetas las tiene que validar el entrenador (no inventar el fallo).

## Motor (de referencia)
`editor/motor/analisis-tecnica/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).

