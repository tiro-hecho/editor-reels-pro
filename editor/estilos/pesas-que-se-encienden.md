# Estilo «Pesas que se encienden» (APROBADO: «con eso está perfecto», 26/10/2026)
Referencia: vídeo de un entrenador, «lo malo, lo bueno y lo perfecto» (30 s): la persona detrás de 3 pesas rusas que toca al dar cada nota.

## 1. Estructura
Gancho → 3 bloques (fuerza, cardio, movilidad: «1 día poco, 2 bueno, 3 perfecto») → cierre «me gusta / seguirnos / entrenar con nosotros» → tarjeta final con logo. Solo bloques que la persona nombra (si no dice de qué es un bloque, se quita).

## 2. Subtítulos
Preset **02-pecho**: Inter Bold blanca, interlineado junto, centrada en el pecho, cada palabra sube desde su renglón. **Siempre blanca** (se rechazó la nota en color).

## 3. Gráficos (la clave del estilo)
- **Recorte de cada objeto con BiRefNet** sobre el fotograma mediano (sin manos). Nada de umbrales ni flood fill: se veían «cutres, mal recortados».
- **Se enciende SOLO el objeto de la palabra que se dice** (malo → rojo, bueno → amarillo, perfecto → verde); al decir la siguiente nota, la anterior se apaga.
- Efecto **brillo**: el metal toma el color conservando reflejos, halo de luz de su color alrededor (desenfoque 42 px + 12 px, modo trama), destello y barrido de luz en diagonal al encenderse.
- **La mano no se tiñe**: por cada fotograma se compara con el fondo mediano de su tramo y se excluye lo que cambia.
- Poco más: cabecera mínima del bloque. Columnas, números y tiras de días se rechazaron por «muy cargado».

## 4. Ritmo
Sin pausas dentro de los bloques: se corta en los silencios reales (−34 dB) dejando ~0,08 s de aire.

## 5. Sonido
Interruptor de luz al encenderse + efecto «mítico»: malo = zumbador de concurso **corto (0,6 s) y bajito**, bueno = tick de concurso, perfecto = «level up». Música movida que elige el cliente, con juego de volúmenes (sube en los huecos, empujón en cada «perfecto», corte seco antes del cierre, arriba en la tarjeta final).

## 6. Prompt para pedirlo
«Edita con el estilo pesas-que-se-encienden: recorta cada objeto con BiRefNet, enciende solo el de la nota que digo (rojo/amarillo/verde) con brillo y halo sin teñir la mano, subtítulos estilo 2 en el pecho, efectos de concurso y juego de volúmenes.»

## Qué NO copiar
Tinte plano encima del objeto, varios objetos encendidos a la vez, textos de días y columnas.

## Motor (de referencia)
`editor/motor/pesas-que-se-encienden/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).

