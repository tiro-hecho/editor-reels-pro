# Criterios de edición: lo que funciona y lo que no

Sale de editar muchas versiones de reels reales de entrenadores y apuntar cada corrección. La IA tiene que leerlo **antes de editar cualquier vídeo** y cumplirlo siempre, salvo que el alumno diga lo contrario.

## 1. Corte y ritmo
- ✅ **Cero silencios**: se cortan las pausas de más de 0,12 s y se deja todo al **1,07×** con atempo, que no cambia el tono.
- ✅ De cada frase repetida, **la mejor toma**. Transcribe **por ventanas** para cazar arranques en falso («entrenar con un pla… espera»).
- ✅ **Algo nuevo en pantalla cada 1,5–2,5 s**: zoom, palabra, luz, B-roll o efecto. Nunca más de 2,2 s quieto.
- ✅ **El final no se corta en seco**: 0,6 s de cola con la música apagándose.
- ❌ Cortar a mitad de palabra o poner un efecto sobre la última sílaba (se come la palabra).

## 2. Subtítulos (los que gustan)
- ✅ **Helvetica Neue Bold** (en Windows, Inter Bold), **minúscula y muy junta** (tracking −6 %). La palabra clave es **la misma letra, más grande**.
- ✅ De 1 a 3 palabras, que aparecen al decirse.
- ✅ Que **sigan a la persona** y **nunca le tapen la cara**: si la tocan, se mueven.
- ✅ Siempre dentro de la zona segura: x 66–934, y 220–1440.
- ❌ Mayúscula condensada mezclada, cursivas, cajas de fondo y sombras cargadas.

## 3. Gráficos
- ✅ **Poco y potente.** Lo que mejor ha funcionado:
  - texto gigante **detrás** de la persona (la cabeza lo tapa);
  - flechas y círculos dibujados sobre el cuerpo;
  - **objetos reales que se iluminan** (las pesas en rojo, amarillo y verde) con zoom de cámara;
  - números gigantes en el gancho.
- ✅ Colores **de la marca** del cliente (de su web o logo) y un color de alerta. **Nunca texto en negro** sobre el gimnasio.
- ✅ Si un texto no se lee, se le pone una pastilla oscura translúcida.
- ❌ Muy cargado:
  - tarjetas blancas con icono;
  - barras de progreso;
  - iconos de «tres rayas»;
  - listas apiladas;
  - títulos de sección;
  - poner siempre el logo.
- ❌ Desenfocar el fondo detrás de un recorte (deja halo).
- ❌ No tocar el color del vídeo ni poner sombras o bordes a la persona.
- ❌ Plantillas con aspecto de IA: chinchetas, tarjetas tipo app o cierres «nombre + dirección» en texto plano.

## 4. B-roll
- ✅ Vídeo del **propio cliente entrenando**, mejor que fotos fijas. Si son fotos, con un zoom marcado.
- ✅ **Comprueba que el plano es lo que se nombra**: si dice «cardio», tiene que verse cardio (bici, carrera), no otro ejercicio.
- ✅ Fotos de los centros: **del interior** (de su web o de su ficha de Google). Nunca la fachada.

## 5. Cierres que gustan
- ✅ Prueba social real: **la nota de Google** que cuenta hasta 5,0, estrellas que se encienden y una frase de una reseña real.
- ✅ Fotos reales del interior del centro detrás de la persona.
- ✅ El texto gigante del sitio («SEDE 2», «SEDE 1») detrás de la persona.
- ❌ Logo y dirección en una línea (básico) o tarjetas de ubicación genéricas.
- Datos (direcciones, notas, teléfonos): **solo los reales**, sacados de la web o la ficha de Google, y si no, se preguntan.

## 6. Sonido
- ✅ **Efectos con significado**: «malo» suena a error, «bueno» es un tic neutro, «perfecto» suena a acierto, y cuando algo se enciende, un interruptor. El **flash de cámara** funciona muy bien en textos gigantes y cortes.
- ✅ Efectos entre −16 y −28 dB, siempre por debajo de la voz. Volumen final entre −14 y −16 LUFS.
- ❌ Golpes graves fuertes, discos de pesa, platillos al revés: «muy fuertes, no van acorde».
- ✅ **Música:** la IA no puede escucharla.
  - **Descarga 10 canciones numeradas** (Pixabay: uso comercial sin atribución) en una carpeta y **que el alumno elija**.
  - Mueve el punto de arranque para que el golpe fuerte entre al terminar el gancho, y comprueba que ningún golpe tape una palabra (si pasa, mueve el arranque en vez de bajar el volumen).
  - Las que han gustado: percusión de tráiler y electro swing.
  - Rechazadas: house, trap «luxury», hip hop genérico y tres canciones distintas en el mismo vídeo.

## 7. Cómo iterar con el alumno
1. Primero **una versión completa** y que dé su opinión.
2. Si algo «no le convence» y no sabe decir qué, haz **10 maquetas en foto** sobre fotogramas reales, numeradas, y que elija. Es lo que más rápido acierta.
3. **Un cambio cada vez.** Lo aprobado se apunta como «Aprobado» en el estilo y lo rechazado como «Rechazado».
4. Antes de entregar, cada vez:
   - transcripción del final con el modelo grande (que no falte ni una sílaba);
   - `check_zonas.py`;
   - que el audio dure lo mismo que la imagen;
   - mirar 6 fotogramas a tamaño real.

## 8. Estilos predefinidos (en `1-skill/editor-reels-pro/estilos-predefinidos/`)
| Estilo | Para qué | Estado |
|---|---|---|
| `texto-detras-gym` | ejercicio con error y técnica correcta | aprobado |
| `lista-contador` | «5 errores», pasos numerados | aprobado |
| `boutique-medidor` | malo/bueno/perfecto, rankings, centros boutique | en pruebas (v5) |
| 9 estilos más (palabras-gigantes-detras, panel-que-baja, historia-dibujada, pizarra-marcador, podcast-pregunta, dopamina-real-3d, explicativo-3d-continuo, visita-rotulos-suelo, aviso-tipografico) | ver `LEEME.md` | aprobados en vídeos reales, solo receta |

Cada uno tiene su vídeo de muestra en `muestras/` y su motor (los scripts) en `motor/`.
