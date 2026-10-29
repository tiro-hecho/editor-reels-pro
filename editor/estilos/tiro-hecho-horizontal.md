# Estilo «Tiro Hecho horizontal» (EN PRUEBAS · 29/10/2026)
Para: vídeos **horizontales 16:9** (YouTube, VSL, lecciones de curso) con una o dos personas hablando a cámara y, a ratos, la pantalla del ordenador.
Sale del VSL de Tiro Hecho. La última muestra (v6, 0–55 s) aún no está aprobada: lo que no guste, apúntalo aquí en «Rechazado».

## 1. Estructura
- **Fondo real siempre** (el plano de la persona): nada de fondos de color detrás de recortes.
- **Texto gigante DETRÁS de la persona**, como portada de revista, en la parte de arriba: tinta oscura o el color de la marca, en la condensada gorda (Anton).
- **Escenas de interfaz** sobre el vídeo desenfocado cuando se habla de algo concreto: un editor con reloj (tiempo perdido), una factura (lo que cuesta), un calendario, una lista de tareas que se van marcando, un chat con la IA, palabras que se tachan, la etiqueta «editado con IA».
- Pantalla del ordenador cuando se enseña algo (grabación de pantalla), con zoom a lo que importa.
- Un estímulo cada ~3 s: zoom, escena, texto detrás o corte.

## 2. Subtítulos
Inter Bold (en lugar de Helvetica), **en minúscula**, sin fondos ni sombras, interlineado −1 px, interletra −0,065 em, muy juntas. Color según lo que haya detrás: tinta sobre pared clara, blanco sobre ropa oscura. Cuatro animaciones que se alternan: sube, pop, se teclea, escala.

## 3. Sonido
Gancho = golpe de graves · revelado = riser · transición = flash de cámara · subtítulos = tecleo suave · texto = pop · zoom = whoosh · llamada a la acción = campanita. Música phonk/hip hop por debajo de la voz con sidechain y un hueco de 0,5 s antes de cada frase clave.

## 4. Motor
`editor/motor/tiro-hecho-horizontal/referencia/`: los scripts del VSL (escenas de interfaz `escenas.py`, gráficos `gfx.py`, subtítulos `subs4.py`, base y mezcla). **No es un motor genérico**: están hechos para ese vídeo. Claude los usa como referencia y los adapta al vídeo nuevo (`montaje.json` con `"formato": "horizontal"` para el corte a 1920×1080).

## Qué NO hacer
- Fondos naranjas o de color detrás de los recortes («nos recortas mal con fondos naranjas»).
- Rótulos flotando sobre el vídeo sin relación con lo que se ve.
- Cajas o píldoras detrás de los subtítulos.
