# Plantilla de ficha de estilo

Toda receta nueva en `editor/estilos/<nombre>.md` lleva estas partes, en este orden:

```
# Estilo «<nombre>»: <qué es en una frase> (APROBADO | EN PRUEBAS | REFERENCIA: fecha)
Para: <qué guion y qué vídeo: a cámara o voz en off, vertical u horizontal, duración>.

## 1. Qué se ve        (colores, letras, dónde va cada cosa; captura en catalogo/capturas/<nombre>.jpg)
## 2. Movimiento       (cómo entra, cómo cambia con la voz, cómo sale)
## 3. Sonido           (efectos y música)
## 4. Motor            (ruta en editor/motor/<nombre>/ y qué hay que cambiar; si no hay, «sin motor»)
## 5. Prompt para pedirlo
## Qué NO copiar       (lo rechazado al crearlo)
```

Al añadir un estilo: receta + motor (o «sin motor») + captura con las caras difuminadas + fila en `editor/catalogo/estilos.json` + línea en `INDICE-POR-GUION.md`, y `python editor/catalogo/generar.py` (rehace catalogo.md y catalogo.html).
