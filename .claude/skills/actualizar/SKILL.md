---
name: actualizar
description: Baja la última versión del editor de Tiro Hecho sin tocar el trabajo del alumno. Úsala con «/actualizar», «actualiza el editor» o «hay estilos nuevos».
---
# Actualizar

1. Avisa: «Voy a bajar la última versión del editor; tus vídeos, tu marca y tus estilos no se tocan».
2. Si la carpeta es un repositorio git (`.git` existe): `git pull`. Si no: descarga el zip de la última versión del repositorio de Tiro Hecho (el enlace está en `README.md`), descomprímelo aparte y copia encima **solo** `editor/`, `.claude/`, `instalacion/`, `CLAUDE.md` y `README.md`. **Nunca** sobrescribas `mi-edicion/`, `recursos-descargados/` ni `.venv/`.
3. Instala lo nuevo que pida: `instalacion/requisitos.txt` con el Python del editor y `editor/motor/comun/descargar_recursos.py`.
4. Cuéntale en 3 líneas qué ha cambiado (mira el historial de cambios) y dile que abra un chat nuevo en la carpeta para que carguen los comandos nuevos.
