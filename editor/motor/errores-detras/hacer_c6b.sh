#!/bin/bash
set -e -x
cd $HOME/editor/proyecto/mi-video
export KIT=~/editor/kit
D=$(python3 -c "import json;print(json.load(open('plan.json'))['dur'])")
# máscaras de la persona por fotograma (solo si cambia el corte)
[ -e mascaras/.hecho ] || { ~/rembg-venv/bin/python afina_mascaras.py && touch mascaras/.hecho; }
python3 formato_c6.py
rm -rf overlay overlay_detras
for i in $(seq 1 40); do TANDA=250 python3 $KIT/motor/render_html.py overlay.html overlay $D 60 && break || true; done
cd overlay; for f in f???.png; do [ -e "$f" ] && mv $f f0${f#f}; done; cd ..
timeout 900 bash -c "for i in $(seq 1 8); do TANDA=250 python3 $KIT/motor/render_html.py detras.html overlay_detras $D 30 && break || true; done" || true
python3 -c "import json,os,shutil;D=json.load(open('plan.json'))['dur'];T=round(D*30);w=len(str(T))
for i in range(1,T):
 f=f'overlay_detras/f{str(i).zfill(w)}.png'
 if not os.path.exists(f): shutil.copy(f'overlay_detras/f{str(i-1).zfill(w)}.png',f)"
python3 ~/editor/proyecto/marcador.py sin_overlay
SFXKIT=$KIT MUSICA=coastal_sprint.mp3 MUSICA_INI=0.0 MUSICA_DIR=~/editor/proyecto/musica/ SFX_DIR=~/editor/proyecto/sfx/ python3 mezcla.py musica
ffmpeg -nostdin -v error -y -i final_musica.mp4 -c:v libx264 -crf 25 -c:a aac -b:a 160k -ac 2 -movflags +faststart movil.mp4
ffmpeg -nostdin -v error -y -i final_musica.mp4 -vf "fps=12/$D,scale=240:427,tile=6x2" -frames:v 1 hoja.jpg
echo TERMINADO_C6B
