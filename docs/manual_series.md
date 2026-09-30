# Manual de anotación de series (versión 1.0): final, *feel good*, utopía y público

Se aplica a series de televisión de ficción. Se anota **la serie entera**, con más peso en cómo termina.

## 0. Reglas generales

1. **Se anota el texto, no la serie.** Anota lo que dice la sinopsis, no lo que recuerdes. Si reconoces la serie, dilo en `reconocida`, pero no uses lo que sabes para rellenar lo que el texto no cuenta.
2. Las definiciones de `feel_good`, `utopia` y `publico` son las del manual de los módulos C, D y E (`docs/manual_modulos_CDE.md`, versión 1.0), cambiando «película» por «serie». Las de `final` son las del manual principal (`docs/manual_anotacion.md`, sección del tipo de final).
3. **Qué es el «final» de una serie.** Es el cierre de la última temporada que describe el texto:
   * si el texto cuenta cómo termina la serie (último episodio o última temporada), se juzga ese cierre;
   * si la serie sigue en emisión o el texto solo llega a una temporada intermedia, se juzga el último estado que describe, y se marca `alcance = "PARCIAL"`;
   * si el texto solo presenta la premisa (quiénes son, dónde están, qué conflicto tienen), `alcance = "PREMISA"` y `final = "NO_CLASIFICABLE"`. **En las series el *feel good* se puede juzgar igualmente** a partir de la experiencia que transmite la premisa y el tono descrito (una comedia de amigos que se apoyan, un drama criminal de ruina moral), con `confianza_c = 1` o `2`. Solo usa `feel_good = null` si el texto no permite hacerse ninguna idea (una línea sin contenido, o solo datos de producción). Lo mismo vale para `utopia`.
   * No uses los datos de producción, audiencia o premios que aparezcan en el texto (éxito, crítica, cancelación) para juzgar el *feel good*.
4. **Series de episodios autoconclusivos** (procedimentales, comedias de situación, antologías): no hay un gran arco. Juzga el mundo y los vínculos que la serie repite episodio a episodio: una comedia en la que la familia siempre se reconcilia es *feel good* aunque no se cuente el último episodio. En esos casos, `alcance = "EPISODICA"`.
5. **Temporadas y giros:** si el texto resume varias temporadas, pesa más la última, pero cuenta la trayectoria (una serie que empieza luminosa y acaba en ruina baja la nota).

## 1. Campos de salida (una línea JSON por serie, en el mismo orden del lote)

* `id`
* `alcance`: `FINAL` (el texto cuenta cómo termina la serie), `PARCIAL` (llega a un punto intermedio o la serie sigue en emisión), `EPISODICA` (serie sin gran arco, de episodios autoconclusivos) o `PREMISA` (solo la premisa).
* `final`: `FELIZ`, `AGRIDULCE`, `AMBIGUO`, `TRAGICO` o `NO_CLASIFICABLE`. Con `alcance` `PARCIAL` o `EPISODICA` se clasifica el último estado descrito o el patrón habitual si el texto lo permite; si no, `NO_CLASIFICABLE`.
* `nota_final`: en español, 10 a 30 palabras, parafraseadas, sobre cómo termina o dónde se queda la historia.
* `feel_good`: entero de 0 a 10, o `null`.
* `feel_good_por_que`: explicación en español de 30 a 90 palabras (qué vínculos quedan en paz o rotos, cómo queda el mundo, si hay esperanza).
* `confianza_c`: 1 (baja), 2 (media) o 3 (alta).
* `utopia`: entero de 0 a 10, o `null`.
* `utopia_por_que`: explicación en español de 15 a 70 palabras.
* `publico`: `INFANTIL`, `FAMILIAR`, `JUVENIL` o `ADULTO`.
* `optimismo_personajes`: entero de −2 (muy pesimistas, sin esperanza) a +2 (muy optimistas, vitalistas), o `null`.
* `tono_general`: entero de −2 (muy sombrío) a +2 (muy luminoso), o `null`.
* `reconocida`: `true` si crees reconocer la serie, `false` si no.

Ejemplo:
`{"id": "S0123ABCD", "alcance": "FINAL", "final": "AGRIDULCE", "nota_final": "...", "feel_good": 7, "feel_good_por_que": "...", "confianza_c": 2, "utopia": 5, "utopia_por_que": "...", "publico": "ADULTO", "optimismo_personajes": 1, "tono_general": 0, "reconocida": true}`
