#!/bin/bash
# Prueba rápida en el VPS: overlay en unos instantes sueltos sobre el vídeo base -> hoja.jpg
# uso (en la carpeta del vídeo): bash ../prueba_fotogramas.sh 1.0,6.5,12.0,20.0
set -e
python3 $KIT/motor/render_html.py overlay.html prueba "$1" 30 > /dev/null
i=0; for t in ${1//,/ }; do
  ffmpeg -v error -y -ss $t -i base.mov -i prueba/f$i.png -filter_complex "[0:v][1:v]overlay,scale=270:480" -frames:v 1 prueba/c$i.png; i=$((i+1)); done
ffmpeg -v error -y $(for j in $(seq 0 $((i-1))); do echo -i prueba/c$j.png; done) -filter_complex "hstack=$i" prueba/hoja.jpg
