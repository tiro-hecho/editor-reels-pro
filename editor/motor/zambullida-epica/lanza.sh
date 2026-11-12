#!/bin/bash
# Render a 60 fps por fotogramas, a baja prioridad; retoma lo que falte. Luego mezcla y codifica.
#   bash lanza.sh musica.mp3        (desde la carpeta del proyecto, con ejemplo.py adaptado como vf.py)
cd "$(dirname "$0")" || exit 1
PISTA=${1:-musica.mp3}
mkdir -p fot
nice -n 19 python3 vf.py render fot > render.log 2>&1 || { echo FALLO; tail -5 render.log; exit 1; }
python3 mezcla.py "$PISTA" mezcla.wav
ffmpeg -hide_banner -loglevel error -y -framerate 60 -i fot/%05d.png -i mezcla.wav -vf scale=out_color_matrix=bt709:out_range=tv,format=yuv420p -c:v libx264 -preset slow -crf 19 -colorspace bt709 -color_primaries bt709 -color_trc bt709 -c:a aac -b:a 256k -shortest -movflags +faststart final.mp4 && echo HECHO
