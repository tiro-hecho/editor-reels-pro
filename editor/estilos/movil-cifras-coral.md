# Estilo «Móvil y cifras en coral» (APROBADO: 12/11/2026)
Para: una persona hablando a cámara que vende un servicio (agencia, consultor, profesional) y quiere enseñar problema → dato → resultados → llamada a la acción. 1080×1920 a 60 fps, de 30 a 45 s.

## 1. Regla de oro
La persona está **siempre de fondo**. Los gráficos van en los huecos (normalmente a su derecha) y el plano se aparta despacio hacia la izquierda para dejarles sitio. Nada le tapa la cara. Todo fuera de las zonas de botones de Instagram y TikTok.

## 2. Escenas
- **Pin de mapa** que cae con rebote sobre la cabeza en la palabra del sitio («si eres de…»), con dos ondas.
- **Móvil realista con pantalla de bloqueo** (marco de titanio, reflejo, perspectiva que gira): hora grande y dos notificaciones que bajan como en iOS («Nadie ha preguntado por tu negocio», «0 mensajes nuevos»). Debajo, la cifra del problema: «0» / *clientes*.
- **Dato a pantalla completa (100 muñecos):** entra con zoom desenfocado; los 100 aparecen en cascada, se apagan en gris mientras el porcentaje cuenta y quedan los que importan en coral, latiendo. Sale con latigazo lateral. Dura unos 2 s.
- **Resultados reales en móviles 9:16 nítidos**: el vídeo del cliente dentro del móvil, cambio rápido entre ejemplos; debajo, cifra en blanco + palabra en cursiva coral («+10.000» contando / *seguidores*).
- **Llamada a la acción:** «Rellena» / *el formulario* con cursor que hace clic, y burbuja de chat verde.

## 3. Tipografía (C7)
- Cifra o palabra grande en sans negrita blanca (Inter Bold; Helvetica si la hay), letras muy juntas (tracking −0,045).
- Palabra pequeña en **Instrument Serif cursiva coral (255, 90, 54)**, que se descubre de izquierda a derecha.
- Las cifras con número cuentan desde 0 en 0,5 s.

## 4. Subtítulos
Letra a letra con muelle y tracking apretado: las pequeñas en blanco (60 px) en una fila, la palabra clave debajo (hasta 132 px) que entra blanca, se pinta de coral de izquierda a derecha y le pasa un brillo. Chispas cuando la clave es una cifra. Sombra elíptica muy suave detrás, sin caja. Altura y ≈ 1360.

## 5. Movimiento
Entradas de unos 0,5 s con curvas suaves (cubic-bezier .2,.9,.3,1), salidas de 0,15-0,2 s. Golpe de zoom pequeño en cada palabra clave, cámara en mano muy leve y latigazo con desenfoque en cada cambio de toma.

## 6. Sonido (unos 120 efectos en 35 s, siempre por debajo de la voz)
Voz a −14,5 LUFS; música a −25 LUFS con sidechain (aprobada con `stomp_action`). Bass drop al inicio; drop + pop en el pin; whoosh de entrada y swoosh inverso de salida en cada móvil; cristal + pop en cada notificación y error en el «0»; 18 tics mientras se apagan los muñecos y golpe + ding al llegar; tics mientras cuenta la cifra; obturador + whoosh en cada ejemplo; clic de ratón en el formulario y ding doble final. Whoosh alternando izquierda y derecha en cada cambio de toma. Todo sale de `editor/assets/efectos/`.

## Motor (de referencia, probado en Windows)
`editor/motor/movil-cifras-coral/`: `motor.py` (imagen), `par.py` (render en 5 procesos), `mezcla.py` (sonido).
1. En la carpeta del proyecto: `base.mov` (el vídeo ya cortado), `palabras.json` (Whisper palabra a palabra: `[[inicio, fin, palabra], …]`), `cuts.json` (cambios de toma) y `ejemplos/` con los vídeos de resultados.
2. Cambia el bloque **CONTENIDO** de `motor.py` (palabras clave, palabra del pin, notificaciones, resultados con sus cifras REALES, porcentaje) y las palabras a las que se ata cada escena (`T("palabra")`).
3. `python3 motor.py hoja 3.5 8.0 18.0` → capturas de control. Revisar cara, zonas de botones y textos.
4. `python3 par.py` → fotogramas en `fot/`; `python3 mezcla.py musica.mp3` → `mezcla.wav`; codificar con ffmpeg a 60 fps (crf 18).
