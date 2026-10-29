# Estilos de subtítulos

Son presets de subtítulos que funcionan **con cualquier estilo de edición**. Se pide con: «Edita este reel con el estilo <estilo> y **subtítulos estilo N**». Si no se dice nada, se usan los del estilo de edición elegido.

| N.º | Nombre | Cómo son | Carpeta |
|---|---|---|---|
| **1** | **muelle** (APROBADO) | Helvetica Neue Bold blanca, bloques de hasta 3 palabras; cada palabra entra con un pequeño rebote, desenfoque y fundido justo al decirse. Sin caja ni colores | `01-muelle/` |
| **2** | **pecho** (APROBADO) | Helvetica Neue Bold blanca de 100 px, en minúscula y sin puntuación, a la altura del pecho; bloques de hasta 3 palabras en 1 o 2 líneas muy juntas. Cada palabra sube desde dentro de su renglón (máscara) y se enfoca. Sin sombra ni colores | `02-pecho/` |
| **3** | **repartidos** (APROBADO) | Helvetica Neue Condensed Bold blanca de 104 px; una palabra por renglón, en zigzag pegada a izquierda y derecha, por debajo de la cara. Cada palabra sube, se enfoca y aparece al decirse | `03-repartidos/` |

Cada carpeta trae:
- `LEEME.md`: la receta completa (aspecto, cómo agrupa las palabras, animación, cómo se usa y qué no hacer).
- El script que genera la secuencia de PNG transparentes.
- `muestra.png` y un `ejemplo-palabras.json` para probarlo.

Para añadir un estilo nuevo, copia la carpeta `01-muelle` como `02-<nombre>`, cambia el aspecto y la animación, y apúntalo en esta tabla.
