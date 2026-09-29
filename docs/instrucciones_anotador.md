# Instrucciones para anotadores (humanos o modelos)

Estas instrucciones se entregan tal cual a cada anotador. Complementan el manual de anotación (`docs/manual_anotacion.md`), que es la referencia.

1. Lee completo `docs/manual_anotacion.md`.
2. Abre **solo** el fichero de lote que se te asigna (`annotation/batches/<etapa>/<lote>.jsonl`). Cada línea tiene `id` y `sinopsis`. No abras ningún otro fichero del repositorio: ni otros lotes, ni etiquetas de otros anotadores, ni claves, ni datos. No busques información sobre las películas fuera del texto.
3. Para cada sinopsis, aplica el manual y produce una línea JSON con exactamente los campos de la sección 7 del manual. Usa solo los códigos permitidos (en mayúsculas y sin tildes). Los ítems de visión de la vida son enteros de −2 a 2 o `null`.
4. Anota **solo lo que dice el texto**. Si reconoces la película, no uses lo que recuerdes de ella; marca `"reconocida": true`.
5. `nota`: paráfrasis breve en español (≤30 palabras). No copies frases de la sinopsis.
6. Escribe el resultado en la ruta de salida indicada, una línea por película, en el mismo orden del lote, sin texto adicional.
7. Al terminar, comprueba que el número de líneas de salida coincide con el del lote y que todas las líneas son JSON válido.

Quien anota no conoce el título, el año, la década, la popularidad ni la puntuación de ninguna película, y no debe intentar deducirlos.
