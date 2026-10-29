# Estilo «Texto detrás gym» (APROBADO: «está increíble», 22/10/2026)

Vídeo de ejemplo: el de el entrenador (un centro de entrenamiento), «curl de bíceps: el error que no te deja crecer», 24 s.
Hecho a partir de cuatro referencias de Instagram: texto gigante detrás de la persona, mezcla de grosores en los subtítulos, estímulo cada 2 s y música de tráiler.
Motor listo para usar: `../motor/texto-detras-gym/` (ver su LEEME).

## 1. Estructura
1. **Gancho (0–3 s)**:
   - la mejor toma, sin silencio;
   - golpe de zoom de entrada (116 % → 100 % en 0,4 s);
   - texto gigante detrás de la persona que cambia de palabra en la frase fuerte («ASÍ NO» → «CRECE»);
   - ✗ roja que se dibuja sobre el error.
2. **Error**: empuje lento de cámara; flecha curva sobre el movimiento malo + tarjeta («balanceo»); en la consecuencia, texto gigante («LESIÓN») + ✗ grande + sacudida.
3. **Pantalla partida MAL / BIEN** (1,3 s) en la pregunta «¿qué tengo que hacer para hacerlo bien?».
4. **Técnica correcta**: tarjetas con ✓ que se apilan arriba al nombrar cada clave; arco del recorrido; texto gigante en la palabra clave.
5. **CTA**: texto gigante con cada sitio («2 CENTROS» y el nombre de cada sitio), tarjeta de ubicación con chincheta, logo y **0,6 s de cola** (nunca cortar en seco).

## 2. Subtítulos (lo que más le gusta)
- **Helvetica Neue Bold** en minúscula, **muy junta** (tracking −6 %), sin caja, con una sombra suave solo detrás de las letras.
  - En Windows, **Inter Bold**.
- Normal a 78 px; **la palabra clave, la MISMA letra a 108 px**.
  - ❌ Nada de mayúscula condensada mezclada ni de cursiva («dudas» en Playfair Italic: rechazado).
- Bloques de 3 palabras como mucho, centrados en x=540 y a la altura del pantalón (y=1330).
- Cada palabra aparece al decirse, subiendo 14 px desde un leve desenfoque.

## 3. Texto gigante detrás de la persona
- Anton (condensada) a 470 px, de 840 px de ancho como mucho, centrado y **a la altura de la cabeza** (y≈560) para que la cabeza lo tape.
  - Si se pone más arriba, queda encima y pierde el efecto.
- La silueta se saca fotograma a fotograma con `u2net_human_seg` (`mascaras.py`).
- ❌ **No desenfocar el fondo**: el recorte deja un halo alrededor de la persona.
- **Colores** (corrección para los siguientes): **nunca negro**. Rojo #FF3B30 para lo que tiene que saltar (ASÍ NO, sitios), magenta de marca para el resto, o dos colores por palabra («2» magenta + «CENTROS» en el otro). El negro se pierde sobre gimnasios con máquinas oscuras.
- Entra con rebote (55 % → 100 %) y suena un **flash de cámara**.

## 4. Gráficos
- **Tarjetas**:
  - blancas, redondeadas, con un icono circular de color (✓ verde, ! magenta, ✗ rojo) y texto Inter Bold negro a 84 px;
  - entran subiendo con rebote y un golpe de zoom del 5 %;
  - siempre centradas arriba (y≈340), apiladas si hay dos.
- ✗ y ✓ dibujadas con trazo (no iconos pegados), flechas curvas magenta y arco de recorrido en blanco.
- **Ubicación**: tarjeta negra con franja magenta y etiqueta «CENTRO …» + chincheta 3D que cae girando.
  - Corrección para los siguientes: **que no parezca hecha con IA**. Menos plantilla de app: integrarla con la tipografía del vídeo (Helvetica junta), sin etiqueta genérica y con la chincheta más sutil o dibujada a mano.
- La dirección solo si el cliente la confirma.

## 5. Ritmo (medido)
- Sin silencios de más de 0,12 s y acelerado al **1,07×** con atempo (sin cambiar el tono).
- **Ningún tramo de más de 2,2 s sin un estímulo**: zoom, tarjeta, texto gigante, flash o sacudida. Los eventos se generan desde las palabras (`T("palabra")`), no a ojo.

## 6. Sonido
- **Música**: una sola pista de **percusión de tráiler** (Pixabay «stylish trailer percussion», 622881) a −20 dB, con sidechain de −6 dB cuando habla y fundido final de 0,9 s. «Con música está increíble».
  - ❌ Rechazado: tres bloques distintos (tensión, phonk y trap): «la música fatal».
- **Efectos**:
  - el principal es el **flash de cámara** (le gusta), en cada texto gigante;
  - pop2 en las tarjetas, swoosh1 suave en los zooms, ding en el final y error_1 bajito en la ✗;
  - todo entre −19 y −28 dB.
  - ❌ Rechazados: disco de pesa, platillo invertido y caída de graves («muy fuertes, no van acorde»).
- **Nunca un efecto en los 0,15 s finales de una palabra** (se comía el «-te» de «lesionarte»).
- Volumen final de −14 a −16 LUFS.

## 7. Cómo pedírselo a la IA
«Edita este vídeo con el estilo texto-detras-gym: usa el motor de `1-skill/editor-reels-pro/motor/texto-detras-gym`, corta sin silencios al 1,07×, texto gigante detrás de mí en las palabras fuertes (rojo o magenta, nunca negro), tarjetas blancas con ✓/✗, pantalla partida mal/bien, subtítulos en Inter Bold junta con la clave más grande, flash en cada texto gigante y percusión de tráiler bajita. Que no haya más de 2 segundos sin un estímulo.»

## Qué NO copiar
El texto ni los colores del cliente de ejemplo: los colores salen de `marca.md` de cada uno.

## Motor (de referencia)
`editor/motor/texto-detras-gym/` son los scripts del vídeo en el que se aprobó. Aún no van solos con `montar.py`: Claude los usa de referencia y monta el vídeo con el motor común (`editor/motor/comun/`), reproduciendo la receta de arriba. Fuentes: Inter (en vez de Helvetica) y Anton (condensada).
