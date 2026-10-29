#!/bin/sh
# Hoja de fotogramas: 1 por segundo en mosaico. Uso: sh hoja.sh video.mp4 [salida.jpg]
f="$1"; o="${2:-${f%.*}_hoja.jpg}"
ffmpeg -nostdin -v error -y -i "$f" -vf "fps=1,scale=180:-1,tile=10x6" -frames:v 1 "$o" && echo "$o"
