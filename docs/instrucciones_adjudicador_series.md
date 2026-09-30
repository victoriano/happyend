# Instrucciones para adjudicar las series (tercer anotador)

1. Lee completos `docs/manual_series.md` y `docs/manual_modulos_CDE.md`, y la sección del tipo de final de `docs/manual_anotacion.md`.
2. Abre **solo** el lote asignado (`annotation/batches/series_adjudicacion/<lote>.jsonl`). Cada línea tiene `id`, `sinopsis`, `etiqueta_X`, `etiqueta_Y` (dos anotaciones independientes en orden aleatorio) y `campos_en_desacuerdo`.
3. Se adjudican (D-037): `final` si X e Y no coinciden; `feel_good` y `utopia` si difieren ≥3 puntos o solo uno es `null`; `publico` si no coincide.
4. Decide **solo los campos en desacuerdo**, aplicando el manual. Puedes elegir el valor de X, el de Y o cualquier otro permitido.
5. Una línea JSON por serie con `id` y un campo por cada campo en desacuerdo. Si adjudicas `feel_good` o `utopia`, añade `feel_good_por_que` o `utopia_por_que` (20 a 60 palabras, en español, con tus palabras).
6. No abras otros ficheros ni busques información externa.
