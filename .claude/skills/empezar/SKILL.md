---
name: empezar
description: Prepara el ordenador del alumno (Mac o Windows) y conoce su marca la primera vez. Úsala cuando diga «/empezar», «empezar», «hola», «instala», «configura» o sea su primera vez.
---
# Empezar

Habla en español, claro, **un paso cada vez**. El alumno no sabe programar: no le enseñes comandos, hazlo tú.

## 1. Mira qué ordenador es
Comprueba si es **Mac o Windows** (y en Windows, si Git Bash está disponible). Dile en una frase: «Voy a preparar tu ordenador, tarda unos 10 minutos».

## 2. Instala lo que falte
- **Mac:** `bash instalacion/instalar-mac.sh`
  - Si dice `FALTA_HOMEBREW`, lanza el instalador oficial de Homebrew y explícale que **escriba él su contraseña del Mac** en la ventana (tú nunca la ves, y no se ven los puntos al escribir: es normal).
- **Windows:** `powershell -ExecutionPolicy Bypass -File instalacion\instalar-windows.ps1`
  - Si Windows pregunta «¿Quieres permitir que esta aplicación haga cambios?», dile que pulse **Sí**.
  - Si el script dice `REINICIA_CLAUDE`, dile: «Cierra Claude del todo y vuelve a abrirlo en esta misma carpeta, y escribe /empezar otra vez». (Windows solo ve los programas nuevos al reabrir la app.)
- El script es seguro de repetir. Si algo falla, lee el error, arréglalo y vuelve a lanzarlo.

## 3. Descarga la música y los efectos
Con el Python del editor (Mac `.venv/bin/python`, Windows `.venv\Scripts\python`): `editor/motor/comun/descargar_recursos.py`. Baja de Pixabay las canciones y efectos que usan los estilos.

## 4. Comprueba que todo funciona DE VERDAD
Con el Python del editor, `instalacion/comprobar.py` hace: un vídeo de 3 s con ffmpeg, una transcripción corta, una capa HTML con Chrome/Edge y un recorte de persona. Si algo sale en rojo, arréglalo y repite. No sigas hasta que salga todo «OK».

## 5. Su marca
Si no existe `mi-edicion/marca.md`, pregúntale **de una en una**:
1. el nombre de su centro o marca;
2. su web o su Instagram;
3. la dirección de su ficha de Google.

Saca tú de su web y de su ficha: colores, logo, fotos del centro por dentro, la nota de Google y el número de opiniones (reales, nunca inventadas) y alguna reseña real. Haz una captura de su ficha de Google y guárdala como `mi-edicion/marca/ficha_google.png`. Guárdalo todo en `mi-edicion/marca.md`.

## 6. Termina
Dile: «**LISTO**. Mete tus vídeos en la carpeta `mi-edicion/brutos` (o arrástralos aquí) y escribe **/estilos** para elegir cómo quieres que queden».
