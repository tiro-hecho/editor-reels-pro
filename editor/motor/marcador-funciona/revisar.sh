#!/bin/bash
# Revisión de un vídeo terminado en el VPS: copia para el móvil, hoja de 12 fotogramas y transcripción del audio final.
set -e
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 final_musica.mp4)
[ -f movil.mp4 ] || ffmpeg-seguro -v error -y -i final_musica.mp4 -c:v libx264 -crf 25 -c:a aac -b:a 160k -ac 2 -movflags +faststart movil.mp4
ffmpeg-seguro -v error -y -i final_musica.mp4 -vf "fps=12/$d,scale=240:427,tile=6x2" -frames:v 1 hoja.jpg
ffmpeg -v error -y -i final_musica.mp4 -vn -ac 1 -ar 16000 rev.wav && python3 ../transcribe.py rev.wav rev.json >/dev/null && rm rev.wav
python3 -c "import json;print(' '.join(w['w'] for w in json.load(open('rev.json'))))"
ffprobe -v error -show_entries stream=codec_type,duration -of csv=p=0 final_musica.mp4
