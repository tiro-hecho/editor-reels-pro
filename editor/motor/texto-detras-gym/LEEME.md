# Motor «texto-detras-gym»

Son 4 scripts que montan un reel completo con el estilo `estilos-predefinidos/texto-detras-gym.md`. Se ejecutan **desde la carpeta del proyecto del vídeo** (la de `mi-edicion/proyectos/<vídeo>/`), en este orden:

| Paso | Script | Qué hace | Qué hay que cambiar para cada vídeo |
|---|---|---|---|
| 1 | `plan.py` | Corta los clips sin silencios y al 1,07× → `base.mov`, `base.wav` y `plan.json` (palabras con su tiempo) | La lista `SEG` (clip, desde, hasta y bloque), sacada de las transcripciones |
| 2 | `mascaras.py` | Silueta de la persona en cada fotograma → `mascaras/` | Nada |
| 3 | `render.py` | Cámara, texto gigante detrás, tarjetas, ✗/✓, pantalla partida y subtítulos → `video.mp4` | Las palabras de `T("…")`, la lista `DETRAS`, el texto de las tarjetas, `CLAVE` y `UBI` |
| 4 | `mezcla.py musica` | Voz + efectos + música con sidechain → `final_musica.mp4` | La pista de `BLOQ` |

## Antes de usarlo
- Los clips de iPhone, en SDR: `avconvert -s CLIP.MOV -o sdr/CLIP.mov -p Preset1920x1080` (Mac). Ponerlos en `sdr/` junto a su `*.palabras.json` (faster-whisper con `word_timestamps=True`).
- **El modelo de silueta** (168 MB, no va en el kit) se descarga una vez en `_modelos/` en la raíz del kit:
  `https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx`
- **La música** se descarga de Pixabay a `musica/` del proyecto. Por licencia, no se puede incluir en el kit. La aprobada es «stylish trailer percussion»: `pixabay.com/music/percussion-stylish-trailer-percussion-622881/`.
- El logo del cliente, como `logo.png` (blanco con fondo transparente), en el proyecto.
- Necesita `pip install faster-whisper pillow numpy onnxruntime` y ffmpeg.
- **Helvetica Neue** viene con el Mac. En Windows, cambia `hn()` en `render.py` por Inter de `5-fuentes`.

## Comprobaciones (obligatorias antes de entregar)
1. Transcribir `final_musica.mp4` y comparar con el guion: que no falte ninguna sílaba.
2. `python3 ../../scripts/check_zonas.py final_musica.mp4` y mirar la hoja.
3. Que el audio y la imagen duren lo mismo.
4. Mirar 4 fotogramas a tamaño real: que el texto gigante quede detrás de la cabeza y no encima.
