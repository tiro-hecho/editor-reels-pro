---
name: editar-reel
description: Edita vídeos en bruto y los convierte en reels profesionales con un estilo del catálogo. Úsala SIEMPRE que pidan editar, montar, hacer un reel o un vídeo, o pongan brutos en la carpeta.
---
# Editar reel

Lee antes `editor/CRITERIOS.md`: son obligatorios. Python del editor: Mac `.venv/bin/python` · Windows `.venv\Scripts\python` (en esta guía, `PY`).

## 1. Organiza
- Crea `mi-edicion/proyectos/video-NN-tema/` y, desde ahí, transcribe sus brutos: `PY ../../../editor/motor/comun/transcribir.py <brutos…>` (sale `palabras/<bruto>.json` y `.txt`).
- Lee las transcripciones y saca **solo las tomas buenas**: fuera muletillas («ya», «vale», «espera»), arranques en falso, risas, charla de preparación y la voz de quien graba.
- Escribe el guion en `GUION.md` y enséñaselo en el chat antes de montar. Nunca borres un bruto.

## 2. Estilo
Si no lo ha elegido, usa `/estilos`. Lee `editor/estilos/<estilo>.md` entero: trae la estructura, los gráficos, el sonido y **qué no hacer**.

## 3. Cortes precisos
Para cada toma buena: `PY ../../../editor/motor/comun/cortes_energia.py <bruto> palabras/<bruto>.json desde hasta …`. Usa esos tiempos, nunca los de Whisper.
Mira los planos (un fotograma cada 0,5 s) cuando lo que se ve importe (p. ej. dónde empieza la tanda mal y la bien): no lo deduzcas solo del texto.

## 4. montaje.json y formato.py
- `montaje.json`: `{"estilo": "…", "formato": "vertical"|"horizontal", "musica": "<archivo de recursos-descargados/musica>", "detras": true|false, "tramos": [[ruta_bruto, desde, hasta, "bloque", velocidad], …]}`. Velocidad 1.07 con voz; 1.6 en demostraciones sin voz. `detras: true` si el estilo pinta gráficos detrás del cuerpo.
- Copia `editor/motor/<estilo>/formato.py` al proyecto y cambia solo su contenido (títulos, bloques, fotos, textos). Colores y logo de `mi-edicion/marca.md`; la ficha de Google en `mi-edicion/marca/ficha_google.png`.
- La música: la que no haya usado en el vídeo anterior (mira `mi-edicion/progreso.md`).

## 5. Monta
`PY editor/motor/comun/montar.py mi-edicion/proyectos/video-NN-tema` (desde la carpeta raíz). Tarda unos minutos (más si hay recorte de persona). Si se corta, repite con `--desde <paso>`.

## 6. Revisa antes de enseñar (obligatorio)
- Transcribe `base.wav` y compara con el guion: **no puede faltar ni cortarse ninguna palabra**.
- Mira `hoja.jpg` y 6 fotogramas a tamaño real: nada tapa la cara, nada se sale de la zona segura, los subtítulos no pisan animaciones, los gráficos detrás del cuerpo no quedan escondidos.
- Sin silencios de más de 0,25 s salvo la cola final.

## 7. Enséñalo y corrige
Envíale `movil.mp4`. Un cambio cada vez. Cuando diga que le gusta, copia `final_musica.mp4` a `mi-edicion/entregados/`, apunta en `mi-edicion/progreso.md` qué estilo y qué canción llevó, y lo aprobado/rechazado en `mi-edicion/estilos/<estilo>.md`.
