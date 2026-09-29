# Instrucciones para la adjudicación (tercer anotador)

1. Lee completo `docs/manual_anotacion.md` (versión 1.0).
2. Abre **solo** el lote de adjudicación asignado (`annotation/batches/principal_adjudicacion/<lote>.jsonl`). Cada línea tiene:
   `id`, `sinopsis`, `etiqueta_X`, `etiqueta_Y` (dos anotaciones independientes en orden aleatorio; no sabes quién hizo cada una) y `campos_en_desacuerdo`.
3. Para cada película, lee la sinopsis completa y decide **solo los campos en desacuerdo** aplicando el manual. Normalmente elegirás el valor de X o el de Y; puedes elegir un tercer valor permitido solo si ambos contradicen claramente el manual, y debes justificarlo en la nota.
4. Para los ítems de visión de la vida (`agencia`, `cambio`, `vinculos`, `futuro`) da un entero de −2 a 2 o `null`.
5. Escribe una línea JSON por película con `id`, un campo por cada campo en desacuerdo con el valor elegido y `nota` (paráfrasis en español, ≤25 palabras, sin copiar la sinopsis). Ejemplo:
   `{"id": "F0123ABCD", "final": "AGRIDULCE", "tono_cierre": "RESIGNACION", "nota": "Logra el objetivo pero muere su hermano; cierre de duelo."}`
6. No abras otros ficheros (etiquetas, claves, datos) ni busques información externa. Anota lo que dice el texto, no lo que recuerdes de la película.
