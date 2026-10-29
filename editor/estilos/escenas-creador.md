# Estilo «Escenas de creador» (VSL de un infoproducto, 20/10/2026)
Origen: propio, a partir de dos referencias de Instagram: subtítulos de @maxi_suga (`instagram.com/reel/Dep8LNCijBJ`) y guía de efectos (`instagram.com/reel/DcwlTN3uitC`).
Muestra: `muestras/escenas-creador.mp4` · Motor: `motor/escenas_creador.py` · Efectos: `4-efectos-sonido/escenas-creador/` (con `CATALOGO.md`).
Sirve en horizontal (VSL, YouTube) y en vertical.

## Ritmo
- Cambio visual cada ~3 s: corte, zoom con empuje lento o escena.
- Cortes secos sin silencios. Al entrar en un zoom, un pequeño golpe que se pasa un poco y vuelve.
- Contraste de ritmo: planos reales largos y, de golpe, una escena diseñada.

## Texto
- **Subtítulos:** Helvetica Neue **Bold**, en minúscula, con las letras muy juntas (tracking −6,5 %) e interlineado −1 px. Bloques de hasta 4 palabras, en 1 o 2 líneas.
  - **Sin fondos, cajas ni sombras.** El color es neutro y se adapta letra a letra: oscuro sobre la pared clara y blanco sobre la camiseta o lo oscuro.
  - **Animaciones sutiles y fluidas que se alternan:** fundido (sube 10 px desde un desenfoque leve), máscara (la línea sube desde detrás de su base) y escala suave (de 0,96 a 1). De vez en cuando, **letra a letra**.
  - En Windows, Inter Bold con tracking −5 %.
- **Texto gigante DETRÁS de la persona** en los ganchos y en las cifras (¿ENTRENADOR PERSONAL?, 30–40 €, 30–40 MIN, los nombres): Anton (condensada), arriba como una portada de revista y con las cabezas tapándolo un poco. Va en gris neutro (`#2E2C2A` al 80 %) o en el color de la marca, **siempre sobre el fondo real**.
- **Cuándo se esconden:** sin subtítulos en las escenas de pantalla completa (factura, calendario, chat y tachado).

## Gráficos (escenas diseñadas que ilustran lo que se dice en ese segundo)
- **Pantalla partida:** el vídeo se encoge en una tarjeta redondeada y, al lado, un editor con el reloj contando los minutos y la línea de tiempo llenándose.
- **Factura** que sale de una impresora, con el sello «POR VÍDEO».
- **Calendario de publicaciones** que se va vaciando, con el bocadillo «¿Qué grabo hoy?».
- **Lista de tareas** que se apila («Entrenar a tus clientes · Pensar ideas · Grabar · Editar · Publicar»).
- **Chat de IA:** se adjunta el archivo, se escribe el mensaje y llega la respuesta con pasos marcados ✓.
- **Palabras tachadas** (TRUCOS, MAGIA) y una que se salva en color (FUNCIONA).
- **«Meta»:** el propio vídeo se encoge dentro de un editor, con su línea de tiempo.
- **Fondo de estas escenas:** el mismo vídeo, desenfocado y oscurecido. Nunca fondos de color detrás de recortes.

## Sonido (ver `CATALOGO.md`: qué es cada efecto y dónde cae su pico)
- **Gancho:** sub drop + boom.
- **Texto detrás:** flash de cámara (con destello blanco) + boom.
- **Entra una escena:** whoosh rápido. **Sale:** swoosh suave.
- **Zoom:** swoosh suave.
- **Revelado:** riser que culmina en el golpe.
- **Elementos:** pop por tarea, ding por cada ✓, tic-tac en el reloj, impresora + caja registradora en la factura, teclado en el chat y papel en lo tachado.
- **Música:** phonk o trap animado y chulesco, **bajito** (~−22 dB bajo la voz), con sidechain y un hueco de 0,5 s antes de cada frase clave.

## Aprobado
- 20/10: «lo demás está muy guapo», que va por las escenas diseñadas, los recortes y el texto gigante detrás.
- 20/10: subtítulos en Helvetica «mucho más junta y un pelín más gordita».

## Rechazado
- 19/10: rótulos y pastillas flotando sobre el vídeo («no se ve creativo»).
- 20/10: recortes sobre fondo naranja («nos recortas mal»).
- 20/10: texto gigante en negro puro («el negro no queda del todo bien»).
- 20/10: los efectos de Mixkit y Kenney de la v2, y subtítulos con cursor de máquina de escribir, pop con rebote o palabra gigante naranja.

## Prompt
«Edita este vídeo con el estilo escenas-creador: subtítulos Helvetica juntitos, texto gigante detrás de mí en el gancho y en las cifras, y una escena diseñada cada vez que dé un dato.»

## Motor (de referencia)
`editor/motor/escenas-creador/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).
