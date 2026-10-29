# Estilo «Análisis por repetición» (APROBADO: «está guay», 26/10/2026)
Referencia: vídeo de un entrenador, «manera incorrecta y correcta» de 5 ejercicios (50 s). Variante del análisis de técnica para listas de ejercicios.

## 1. Estructura
1. **Empieza hablando desde el segundo 0** (nada de avance mudo: se rechazó). Título encima mientras habla: «5 EJERCICIOS / MANERA INCORRECTA Y CORRECTA» → «¿BIEN O MAL? / MIRA LA TÉCNICA».
2. **Cada ejercicio:** cabecera arriba «EJERCICIO 0X / 05» + nombre, que entran deslizando, y barra de progreso de 5 tramos.
3. **Cada repetición mala y buena se congela 0,8 s DESPUÉS de la frase** (nunca a mitad de palabra) y se dibuja sobre el cuerpo:
   codo (círculo), altura de la mancuerna vs línea del hombro, curva de la espalda vs línea recta, muslo vs paralela, línea de los hombros (tronco que gira).
   Etiqueta en pastilla con ✕/✓ y el marco de la pantalla se dibuja en rojo o verde.
4. **Entre ejercicios:** cortinilla diagonal NEGRA con el número (nada de colores que no sean de la marca).
5. **Cierre:** fotos reales de cada centro sacadas de su web, rótulo grande («CENTRO 01 · SEDE 1») y tarjeta final negra con el logo y la cuenta.

## 2. Subtítulos
Preset **03-repartidos** (Helvetica condensada, palabra a palabra a los lados).

## 3. Gráficos y B-roll
- Coordenadas medidas en cada fotograma congelado; el compositor amplía ×1,03, así que se corrigen al mismo encuadre.
- Colores: los de la web del cliente (aquí negro y blanco); rojo/verde solo para el veredicto.

## 4. Ritmo
- Quitar los ratos quietos sin voz, las palabras sueltas del equipo («sí», «ya», «listo») y los arranques trabados (buscar «manera… manera»).
- Golpe suave en cada «manera …» que no pise un congelado.

## 5. Sonido
Obturador + rayado + error/confirmación en cada congelado; swoosh y tick en la cortinilla; canción que el cliente elija (aquí indie rock «coastal sprint»).

## 6. Prompt para pedirlo
«Edita con el estilo análisis-por-repetición: cabecera EJERCICIO 0X/05 con barra, congela cada repetición mala y buena después de la frase y dibuja sobre el cuerpo lo que falla, cortinilla negra con el número, cierre con fotos de la web del centro.»

## Qué NO copiar
Etiquetas que solo repiten la frase sin explicar el gesto (se rechazó: «no va acorde al movimiento»).

## Motor (de referencia)
`editor/motor/analisis-repeticion/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).

