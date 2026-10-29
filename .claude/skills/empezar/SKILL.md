---
name: empezar
description: Prepara el ordenador del alumno (Mac o Windows), le da la bienvenida y conoce su marca la primera vez. Úsala cuando diga «/empezar», «empezar», «hola», «instala», «configura» o sea su primera vez.
---
# Empezar

Habla en español, claro, **un paso cada vez**. El alumno no sabe programar: no le enseñes comandos, hazlo tú. Si ya existe `mi-edicion/marca.json` y todo está instalado, salta al paso 6.

## 1. Bienvenida (corta)
«¡Hola! Soy tu editor de vídeo. Tú grabas, yo edito: corto los silencios, pongo subtítulos, gráficos, efectos y música, con tu marca. Primero preparo tu ordenador (unos 10 minutos) y luego te hago 5 preguntas sobre tu negocio para que los vídeos salgan con tus colores.»

## 2. Prepara el ordenador
Comprueba si es **Mac o Windows**.
- **Mac:** `bash instalacion/instalar-mac.sh`. Si dice `FALTA_HOMEBREW`, lanza el instalador oficial de Homebrew y explícale que **escriba él la contraseña del Mac** en la ventana (no se ven los puntos al escribir: es normal; tú nunca la ves).
- **Windows:** `powershell -ExecutionPolicy Bypass -File instalacion\instalar-windows.ps1`. Si Windows pregunta si permite cambios, que pulse **Sí**. Si sale `REINICIA_CLAUDE`: «Cierra Claude del todo, ábrelo otra vez en esta carpeta y escribe /empezar».
- Luego, con el Python del editor (Mac `.venv/bin/python`, Windows `.venv\Scripts\python`): `editor/motor/comun/descargar_recursos.py` (música y efectos) e `instalacion/comprobar.py`. No sigas hasta que salga `TODO_OK`; si algo falla, arréglalo tú.

## 3. Las preguntas de su marca (de una en una, esperando cada respuesta)
1. **¿Cómo se llama tu negocio?**
2. **¿Tienes página web o Instagram?** Pásame el enlace.
3. **¿Tienes ficha de Google?** (la que sale al buscar tu negocio en Google Maps, con estrellas y opiniones). Pásame el enlace o dime cómo aparece.
4. **¿Tienes colores de marca?** Si no lo sabe, sácalos tú de su web, su logo o su Instagram y enséñale 2-3 opciones para que elija el **color principal** (el de los detalles: placas, casillas, círculos).
5. **¿Usas alguna tipografía en tu marca?** Si tiene el archivo (.ttf/.otf), que lo arrastre al chat y guárdalo en `mi-edicion/marca/fuentes/`. Si no, se queda la del editor (limpia, tipo Helvetica).

Después, tú solo (sin preguntarle más):
- **Logo:** descárgalo de su web o Instagram a `mi-edicion/marca/logo.png`.
- **Ficha de Google:** abre su ficha en el navegador, haz una captura vertical (nombre, estrellas, número de opiniones, mapa y fotos) y guárdala como `mi-edicion/marca/ficha_google.png`. Apunta la nota y el número de opiniones **reales**.
- **Fotos y capturas de su web** que puedan servir de recurso en los vídeos (el centro por dentro, el equipo, servicios): guárdalas en `mi-edicion/marca/recursos/` con un nombre que diga qué son.
- Nunca inventes datos: si algo no lo encuentras, déjalo vacío y díselo.

Guárdalo todo en **`mi-edicion/marca.json`** (lo lee el motor):
```json
{"negocio": "…", "web": "…", "instagram": "…", "ficha_google": "…", "nota_google": "5,0", "opiniones": 14,
 "color_acento": "#RRGGBB", "color_texto": "#FFFFFF",
 "fuente_titulos": "mi-edicion/marca/fuentes/…ttf", "fuente_texto": "mi-edicion/marca/fuentes/…ttf",
 "logo": "mi-edicion/marca/logo.png", "ficha_captura": "mi-edicion/marca/ficha_google.png"}
```
y un resumen legible en `mi-edicion/marca.md` (también una reseña real si la hay). Enséñale el resultado: «Así quedan tus colores:» con una muestra.

## 4. Cuéntale qué puede hacer
«Ya está todo listo. Esto es lo que puedes pedirme:
- **/estilos** — te enseño los estilos con fotos y eliges.
- **/editar-reel** — edito tus vídeos con ese estilo.
- **/subtitulos**, **/musica**, **/sonidos** — eliges letra, canción y efectos.
- **/copiar-referencia** — me pasas un reel que te guste y lo copio.
- **/crear-estilo** — guardamos tu propio estilo para repetirlo.
- **/actualizar** — te bajas los estilos nuevos.
Y puedes hablarme normal: "quita el silencio del segundo 5", "más grande", "otra canción".»

## 5. Dónde van los vídeos
«Tienes dos formas: **mete tus vídeos en la carpeta `mi-edicion/brutos`** (o arrástralos aquí al chat), o **dime dónde los tienes** (por ejemplo "están en Descargas") y los cojo de ahí sin moverlos.»

## 6. Termina
«**LISTO.** Cuando quieras, escribe **/estilos** para elegir cómo quieres que quede tu primer vídeo.»
