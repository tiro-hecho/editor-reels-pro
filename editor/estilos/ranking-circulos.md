# Estilo «Ranking con círculos» (APROBADO: 26/10/2026)
Referencia: vídeo de un centro de entrenamiento, «top 5 ejercicios».

## 1. Estructura
- La persona está **a un lado** de la pantalla y el ranking va **en el otro lado**.
- Cada ejercicio entra en un círculo grande sobre el pecho con su nombre; al decir «número N» vuela a su puesto.
- Cuando dice «ponlo en tu lista», los círculos **laten uno detrás de otro**.

## 2. Subtítulos
Los del estilo de edición elegido (por ejemplo, preset 02-pecho), siempre blancos y sin tapar la cara ni el panel.

## 3. Gráficos (la clave del estilo)
- **Panel:** oscuro translúcido (rgba 14,14,16,.62), esquinas de 28 px, de x 44 a x 510. **No llega a la cara.**
- **Título:** «TOP 5» en Anton (condensada) de 92 px. Debajo, «MEJORES EJERCICIOS» en Inter Medium de 21 px con interletra pequeña (pequeño y con las letras juntas).
- **5 filas:** número en Condensed Black de 50 px (pequeño), un hueco circular discontinuo de 100 px y el nombre en Bold de 28 px, que puede ocupar 2 líneas. **Nada puede salirse del panel.**
- **Círculo grande:** 360 px sobre el pecho, con el nombre del ejercicio.
- **Número 1:** borde y número dorados (#FFD84D) con halo.
- **Fotos:** fotogramas reales del propio centro haciendo ese ejercicio, sacados de otros vídeos del mismo cliente.

## 4. Ritmo
Cortes en los silencios reales; el vuelo de cada ejercicio va justo en «número N».

## 5. Sonido
Efectos de `4-efectos-sonido/miticos/`: tick (−20 dB) en cada puesto y «level up» (−19 dB) en el número 1.

## 6. Prompt para pedirlo
«Edita con el estilo ranking-circulos: persona a un lado y panel TOP 5 al otro sin tocar la cara, cada ejercicio con un fotograma real del centro en un círculo que vuela a su puesto al decir el número, el 1 en dorado, latido en "ponlo en tu lista", tick en cada puesto y level up en el 1.»

## Qué NO copiar
Textos o fotos que se salgan del panel, números o subtítulo grandes, fotos de stock cuando hay vídeos del propio centro.

## Motor (listo para Mac y Windows)
1. Copia `editor/motor/ranking-circulos/formato.py` a la carpeta del proyecto y cambia solo su contenido (títulos, bloques, textos, fotos).
2. En `montaje.json`: `"estilo": "ranking-circulos"`, la música y los tramos medidos con `cortes_energia.py`.
3. Monta con `editor/motor/comun/montar.py <proyecto>`.

