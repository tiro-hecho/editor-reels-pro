#!/bin/bash
# Prepara un Mac para editar. Lo lanza Claude desde la carpeta del editor. Se puede repetir sin miedo: solo instala lo que falte.
cd "$(dirname "$0")/.." || exit 1
ok(){ echo "OK  $1"; }
if ! command -v brew >/dev/null 2>&1; then
  for b in /opt/homebrew/bin/brew /usr/local/bin/brew; do [ -x "$b" ] && eval "$("$b" shellenv)"; done
fi
command -v brew >/dev/null 2>&1 || { echo "FALTA_HOMEBREW"; exit 2; }
command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg; ok "ffmpeg (cortar, unir y exportar vídeo)"
PYB=$(brew --prefix)/bin/python3.12
[ -x "$PYB" ] || brew install python@3.12; ok "Python 3.12"
if [ ! -d "/Applications/Google Chrome.app" ] && [ ! -d "/Applications/Microsoft Edge.app" ] && [ ! -d "/Applications/Brave Browser.app" ]; then
  brew install --cask google-chrome
fi; ok "navegador para pintar los gráficos"
[ -x .venv/bin/python ] || "$PYB" -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -r instalacion/requisitos.txt || { echo "ERROR_PIP"; exit 3; }
ok "librerías de Python (transcribir, recortar a la persona, dibujar)"
mkdir -p mi-edicion/{brutos,proyectos,entregados,referencias,estilos,marca} recursos-descargados; ok "carpeta mi-edicion"
echo "TODO_LISTO"
