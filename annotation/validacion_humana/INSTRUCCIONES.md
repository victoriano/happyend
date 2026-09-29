# Validación humana (preparada, no realizada)

**Objetivo.** Comprobar con personas la calidad de las etiquetas de los modelos (`annotation/labels/principal/`) y si sus errores varían por década o género.

**Material.**

* `muestra.jsonl`: 100 sinopsis cegadas (20 por cohorte). La mitad de cada cohorte son películas en las que los dos modelos discreparon en el final (sobremuestreo deliberado; el análisis debe ponderar por estrato con `data/interim/keys/validacion_humana_key.csv`).
* `plantilla_anotador_1.csv` y `plantilla_anotador_2.csv`: una fila por `id` para rellenar.

**Procedimiento.**

1. Dos personas anotan de forma independiente, siguiendo `docs/instrucciones_anotador.md` y el manual 1.0, sin ver las etiquetas de los modelos ni la clave.
2. Se calcula su acuerdo (kappa por campo y alfa por ítem) con `finales.agreement`.
3. Una tercera persona adjudica sus desacuerdos.
4. La etiqueta humana adjudicada es la referencia. Se calculan la exactitud y la matriz de confusión de la etiqueta final de los modelos por campo, y los errores por cohorte y género, **ponderando por el sobremuestreo de desacuerdos**.
5. Si el error difiere por cohorte, las comparaciones entre décadas deben corregirse (por ejemplo, con una corrección de clasificación errónea o una muestra de validación mayor) antes de sacar conclusiones.
