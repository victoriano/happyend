# Instrucciones para adjudicar los módulos C, D y E (tercer anotador)

1. Lee completo `docs/manual_modulos_CDE.md` (versión 1.0).
2. Abre **solo** el lote asignado (`annotation/batches/cde_adjudicacion/<lote>.jsonl`). Cada línea tiene `id`, `sinopsis`, `etiqueta_X`, `etiqueta_Y` (dos anotaciones independientes en orden aleatorio) y `campos_en_desacuerdo`.
3. Se adjudican (registro de decisiones D-036):
   * `feel_good` y `utopia` cuando X e Y difieren en 3 puntos o más, o cuando uno da `null` y el otro no;
   * `publico` cuando X e Y no coinciden.
4. Lee la sinopsis completa y decide **solo los campos en desacuerdo** aplicando el manual. Puedes elegir el valor de X, el de Y o cualquier otro permitido. `feel_good` y `utopia` llevan un entero de 0 a 10 o `null` (si la sinopsis no permite juzgar).
5. Escribe una línea JSON por película con `id` y un campo por cada campo en desacuerdo. Si adjudicas `feel_good` o `utopia`, añade también `feel_good_por_que` o `utopia_por_que`: explicación en español de 20 a 60 palabras, con tus palabras, sin copiar la sinopsis. Ejemplo:
   `{"id": "G0123ABCD", "feel_good": 7, "feel_good_por_que": "La familia se reconcilia tras la muerte del abuelo...", "publico": "FAMILIAR"}`
6. No abras otros ficheros ni busques información externa. Anota lo que dice el texto, no lo que recuerdes de la película.
