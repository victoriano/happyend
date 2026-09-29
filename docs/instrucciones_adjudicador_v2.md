# Instrucciones para la adjudicación v2 (tercer anotador)

1. Lee completo `docs/manual_anotacion.md` (núcleo versión 1.0 y módulo B versión 2.0).
2. Abre **solo** el lote asignado (`annotation/batches/v2_adjudicacion/<lote>.jsonl`). Cada línea tiene `id`, `sinopsis`, `etiqueta_X`, `etiqueta_Y` (dos anotaciones independientes en orden aleatorio) y `campos_en_desacuerdo`.
3. En v2 solo se adjudican `final` y los ítems de −2 a 2 (`agencia`, `cambio`, `vinculos`, `futuro`, `tono_general`, `optimismo_personajes`) cuando X e Y difieren en 3 o más puntos (registro de decisiones D-026). El resto de campos de X e Y se muestra solo como contexto.
4. Lee la sinopsis completa y decide **solo los campos en desacuerdo** aplicando el manual. Normalmente elegirás el valor de X o el de Y; puedes elegir otro valor permitido si ambos contradicen claramente el manual (justifícalo en la nota). Los ítems llevan un entero de −2 a 2 o `null`.
5. Escribe una línea JSON por película con `id`, un campo por cada campo en desacuerdo y `nota` (paráfrasis en español, ≤25 palabras, sin copiar la sinopsis). Ejemplo:
   `{"id": "G0123ABCD", "final": "AGRIDULCE", "optimismo_personajes": 1, "nota": "Logra salvar al pueblo pero pierde a su hija; los personajes mantienen la esperanza."}`
6. No abras otros ficheros (etiquetas, claves, datos) ni busques información externa. Anota lo que dice el texto, no lo que recuerdes de la película.
