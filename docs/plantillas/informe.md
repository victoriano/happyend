# ¿Eran más optimistas las películas de los noventa?

**Informe principal. Primera versión, exploratoria.** Generado automáticamente por `python -m finales.report` a partir de las tablas de `reports/tables/`. Cada cifra de este documento se lee de esas tablas (el volcado completo de valores está en `reports/tables/valores_informe.json`).

---

## 1. Pregunta y alcance

**Pregunta principal.** ¿En qué medida difieren las películas populares estadounidenses estrenadas entre 1990 y 1999 y las estrenadas desde 2010 en la frecuencia de finales felices, agridulces, ambiguos o trágicos y en el optimismo general que transmiten?

**Pregunta independiente.** ¿Prefiere el público actual más historias optimistas de las que percibe en el cine reciente? Esta segunda pregunta **no se ha contestado**: exige una encuesta o un experimento con personas, que se ha diseñado (sección 8 y `docs/diseno_encuesta.md`) pero no se ha realizado.

**Lo que este análisis no puede probar.** La idea de que «estaba prohibido hacer películas no optimistas» es una frase retórica. Con películas estrenadas solo se puede describir qué se estrenó, no qué se impidió estrenar. Probar una presión de la industria exigiría documentos de producción, versiones de guion, notas de estudio o testimonios, que quedan fuera de este proyecto.

**Población.** Largometrajes de ficción con país de origen EE. UU. (Wikidata), estrenados entre 1980 y 2024, en cinco cohortes: 1980-1989, 1990-1999, 2000-2009, 2010-2019 y 2020-2024. La última cohorte solo abarca **cinco años** y se analiza también por separado.

---

## 2. Límites que condicionan todas las conclusiones

Estos límites aparecen antes de los resultados a propósito: ninguna conclusión de este informe debe leerse sin ellos.

1. **Las etiquetas las han puesto modelos de lenguaje, no personas.** Dos modelos distintos anotaron cada sinopsis de forma independiente y a ciegas, y un tercer proceso adjudicó los desacuerdos. **No se ha hecho la validación humana**: el material para hacerla está preparado en `annotation/validacion_humana/` (100 películas estratificadas por cohorte). Un acuerdo alto entre dos modelos no garantiza que acierten: pueden compartir sesgos.
2. **El cegado apenas funcionó en el cine popular.** Se retiraron título y años, pero los anotadores dijeron reconocer la película en el {rec_A} (anotador A) y el {rec_B} (anotador B) de los casos. En el marco popular, **al menos uno reconoció el {rec_pop_any_max} de las películas en todas las cohortes** y ambos, el {rec_pop_ambos}. En el marco amplio, entre el {rec_amp_any_min} y el {rec_amp_any_max}, según la cohorte. Los anotadores pudieron usar lo que «saben» de la película o de su época. Por eso la sensibilidad que excluye las películas reconocidas no es evaluable en el marco popular: quedan {pop_s_noreca_n} películas si se excluyen las reconocidas por alguno y {pop_s_norec_n} (90s/2010-2024) si se excluyen las reconocidas por ambos.
3. **Las sinopsis son de Wikipedia y están escritas hoy.** Es una ventaja (todas las décadas se describen con las mismas convenciones y en la misma época) y un riesgo (lo que los editores eligen contar puede variar según la película sea antigua o reciente, o más o menos conocida). El análisis mide los finales **tal como los resume Wikipedia**, no las películas.
4. **La popularidad se mide con votos actuales de IMDb.** Los votos son retrospectivos: las películas de los noventa que hoy tienen muchos votos son las que se siguen recordando, lo que introduce un sesgo de supervivencia que puede diferir por década. La taquilla de Wikidata es escasa y no está ajustada por inflación, así que no se usó.
5. **La muestra es pequeña para diferencias moderadas.** Con 150 películas por cohorte en el marco popular, la diferencia mínima detectable (potencia del 80 %) entre los noventa y 2010-2024 es de unos {mde_pop}. Para detectar 10 puntos harían falta unas {n_10pp} películas por cohorte. En el marco amplio (50 por cohorte) la diferencia mínima detectable es de {mde_amp}. **El análisis es exploratorio, no representativo en sentido estricto.**
6. **Marco amplio con umbral de visibilidad.** El marco amplio no es todo el cine estadounidense, sino las películas con al menos 1.000 votos en IMDb, artículo en Wikipedia y sección argumental de 120 palabras o más. En ese marco faltan más desenlaces en algunas cohortes (no clasificables: {nc_amp_90} en los noventa frente a {nc_amp_10} en 2010-2019), y eso influye en las comparaciones.
7. **Nacionalidad por Wikidata.** «Estadounidense» = EE. UU. figura entre los países de origen; se incluyen coproducciones (hay una prueba de sensibilidad solo con producciones exclusivamente estadounidenses). Las películas no estadounidenses y las de nacionalidad no establecida no se distinguen en las exclusiones.
8. **Condiciones de uso de IMDb.** Los datos de IMDb solo se permiten para uso personal y no comercial y no pueden republicarse como base de datos. Por eso los datos derivados publicados no incluyen votos ni puntuaciones de IMDb, solo identificadores y tramos de popularidad. Quien reproduzca el flujo debe descargarlos y aceptar esas condiciones.

---

## 3. Datos y procedencia

| Fuente | Uso | Licencia o condiciones | Consulta |
|---|---|---|---|
| IMDb Non-Commercial Datasets (`title.basics`, `title.ratings`) | Títulos, año, duración, géneros, votos | Uso personal y no comercial; atribución: *Information courtesy of IMDb (https://www.imdb.com). Used with permission.* | 2026-09-29 |
| Wikidata (consulta SPARQL por año) | País de origen, enlace a Wikipedia, fecha de publicación | CC0 | 2026-09-29 |
| Volcado de Wikipedia en inglés, 1 de septiembre de 2026 (`enwiki-20260901-pages-articles-multistream`) | Sección argumental (*Plot*) de cada película muestreada | CC BY-SA 4.0 | 2026-09-29, índice verificado con el SHA-1 publicado |
| CMU Movie Summary Corpus (Bamman, O'Connor y Smith, 2013) | Solo para evaluar su cobertura | CC BY-SA | 2026-09-29 |

Cada descarga está registrada en `data/provenance.jsonl` (URL, fecha, licencia y hash). Cada película de la muestra guarda la URL de la revisión exacta de Wikipedia usada (`data/derived/muestra_principal.csv`). El texto de las sinopsis no se redistribuye en los datos derivados (minimización), aunque su licencia lo permitiría con atribución.

**Por qué no se usó el CMU Movie Summary Corpus como fuente principal.** Se construyó con un volcado de Wikipedia de 2012 y su cobertura de películas recientes es insuficiente: tiene sinopsis para el {cmu_90} del catálogo de los noventa, pero solo para el {cmu_10} del de 2010-2019 y el {cmu_20} del de 2020-2024 (`reports/tables/cobertura_cmu.csv`). Mezclar fuentes por década habría confundido el cambio en las películas con el cambio de fuente.

**Por qué el volcado y no la API.** La API REST de Wikipedia devolvía de forma sistemática HTTP 429 (demasiadas peticiones) desde la IP compartida del entorno. El volcado público permite leer por rangos HTTP solo los bloques con los artículos necesarios, con una versión fechada y verificable.

---

## 4. Método

### 4.1 Catálogo

A partir de IMDb: `titleType = movie`, año 1980-2024, duración de 60 minutos o más, sin géneros de no ficción (*Documentary*, *Reality-TV*, *Talk-Show*, *News*, *Game-Show*, *Adult*), al menos 1.000 votos, país de origen EE. UU. en Wikidata, artículo en la Wikipedia en inglés y año coherente entre IMDb y Wikidata (desfase de un año como máximo). Los duplicados de artículo se resuelven conservando el título con más votos. Cada exclusión recibe un único motivo, el primer filtro que falla (`reports/tables/exclusiones_resumen.csv`). Por ejemplo, {excl_votos_bajo_umbral} títulos del periodo quedaron fuera por no llegar a 1.000 votos y {excl_nacionalidad_no_establecida_o_no_eeuu} por no constar como estadounidenses en Wikidata.

Catálogo elegible: **{cat_total} películas** (1980-89: {cat_80}; 1990-99: {cat_90}; 2000-09: {cat_00}; 2010-19: {cat_10}; 2020-24: {cat_20}).

### 4.2 Marcos de muestra

* **Popular**: las 50 películas con más votos de cada año. Por cohorte se extraen 150 películas, repartidas por género principal en proporción a su peso en ese universo.
* **Amplio**: todo el catálogo elegible. Por cohorte se extraen 50 películas, a partes iguales entre los tres terciles de votos de cada año y, dentro de cada tercil, en proporción al género. Cada película lleva su peso de diseño (tamaño del estrato / muestra del estrato).

El orden aleatorio es estable (hash de semilla y título) y no depende del orden de las filas. Las películas sin sinopsis utilizable se sustituyen por la siguiente del mismo estrato y quedan registradas: {n_sustituidas} sustituciones en total ({n_sust_popular} en el marco popular y {n_sust_amplio} en el amplio; `reports/tables/muestreo_log_principal.csv`). Las del piloto no entran en la muestra principal. Resultado: {n_filas_muestra} filas y **{n_peliculas} películas distintas** ({n_solapadas} están en ambos marcos). La mediana de longitud de las sinopsis es de {palabras_mediana} palabras.

El **género principal** se asigna con una prioridad fija sobre los hasta tres géneros de IMDb: Animación > Terror > Acción/aventura > Ciencia ficción/fantasía > Comedia > Romance > Thriller/crimen > Drama > Otros.

### 4.3 Anotación

El **manual** (`docs/manual_anotacion.md`) define cinco dimensiones que se miden por separado:

1. **Final**: feliz, agridulce, ambiguo, trágico o no clasificable.
2. **Resultado para los protagonistas**: supervivencia, objetivo, vínculos y justicia narrativa.
3. **Tono del cierre**: esperanza, alivio, conexión, resignación o desesperanza (y su valencia).
4. **Visión de la vida**: agencia, posibilidad de cambio, valor de los vínculos y expectativa de futuro, de −2 a +2.
5. **Arco emocional**: **no se ha medido**. Requiere guiones o subtítulos con procedencia y permisos verificables, y no se encontró ningún corpus así.

**Piloto.** Con 50 películas de todas las cohortes, dos anotadores independientes obtuvieron un kappa de Cohen de {pil_k_final} para el final y de {pil_k_tono} para el tono del cierre. El manual se ajustó solo con el piloto (reglas marcadas [v1.0]: poscréditos, finales alternativos, dos protagonistas, historias sin conflicto central, procedimiento de decisión del tono) y se congeló como versión 1.0 antes de la muestra principal; su hash está en `docs/manual_anotacion_v1.0.sha256`. Ninguna definición de las categorías de final cambió.

**Tamaño.** En el piloto, la proporción de finales felices fue del {pil_p_feliz} y la desviación típica de la visión de la vida, de {pil_sd_vision}. Con esos valores, detectar 10 puntos de diferencia exigiría {n_10pp} películas por cohorte y detectar 15, {n_15pp} (`reports/tables/potencia_piloto.csv`). Por capacidad de anotación se fijaron 150 por cohorte en el marco popular y 50 en el amplio.

**Anotadores.** Cada sinopsis cegada (sin título ni años) la anotaron **dos modelos de lenguaje distintos, de forma independiente** (A y B), en lotes de 50 con el orden de cohortes mezclado. Los desacuerdos de cualquier campo, y las diferencias de 3 o más puntos en los ítems, los resolvió un **adjudicador** que veía las dos etiquetas en orden aleatorio sin saber de quién era cada una. Se adjudicaron {n_adjudicadas} películas, {adj_n_final} de ellas por desacuerdo en el final. El adjudicador comparte familia de modelo con el anotador A y le dio la razón en el {adj_A_final} de los desacuerdos sobre el final. Por eso hay pruebas de sensibilidad con las etiquetas de A solas y de B solas.

**Corrección durante la anotación.** A mitad de la anotación se detectó que en algunos artículos la extracción de la sección argumental arrastraba texto de producción o de recepción. Se corrigió el extractor (con pruebas), se volvieron a anotar las {n_reanotadas} películas ya anotadas afectadas y se apartaron sus etiquetas obsoletas (`reports/tables/reanotacion_correccion_sinopsis.csv`, registro D-017).

### 4.4 Análisis

* Proporciones con intervalo de Wilson y tamaño efectivo de Kish (ponderación de diseño); medias con IC t.
* Diferencias frente a los noventa en puntos porcentuales y como razón, con IC bootstrap estratificado (4.000 réplicas).
* Efecto ajustado de 2010-2024 frente a 1990-1999: logit ponderado con género principal y popularidad como controles y efecto marginal medio por g-computación (bootstrap de 500 réplicas); MCO con errores HC3 para la visión de la vida. La popularidad se controla con el logaritmo del rango de votos en el año (marco popular) o con el tercil (marco amplio). El percentil de votos se descartó porque depende del tamaño del catálogo anual, que crece con los años (registro D-019).
* Los no clasificables se excluyen de las proporciones de final y se incluyen en una prueba de sensibilidad.

---

## 5. Resultados

### 5.1 Tipos de final por cohorte

![Distribución de finales](figures/fig1_distribucion_finales.png)

**Marco popular (150 películas por cohorte), % de finales felices con IC 95 %:**

| Cohorte | Feliz | Agridulce | Ambiguo | Trágico |
|---|---|---|---|---|
| 1980-1989 | {pop_feliz_80} {pop_feliz_80_ci} | {pop_agri_80} | {pop_amb_80} | {pop_trag_80} |
| 1990-1999 | {pop_feliz_90} {pop_feliz_90_ci} | {pop_agri_90} | {pop_amb_90} | {pop_trag_90} |
| 2000-2009 | {pop_feliz_00} {pop_feliz_00_ci} | {pop_agri_00} | {pop_amb_00} | {pop_trag_00} |
| 2010-2019 | {pop_feliz_10} {pop_feliz_10_ci} | {pop_agri_10} | {pop_amb_10} | {pop_trag_10} |
| 2020-2024* | {pop_feliz_20} {pop_feliz_20_ci} | {pop_agri_20} | {pop_amb_20} | {pop_trag_20} |

**Marco amplio (50 películas por cohorte, ponderado por diseño):**

| Cohorte | Feliz | Agridulce | Ambiguo | Trágico |
|---|---|---|---|---|
| 1980-1989 | {amp_feliz_80} {amp_feliz_80_ci} | {amp_agri_80} | {amp_amb_80} | {amp_trag_80} |
| 1990-1999 | {amp_feliz_90} {amp_feliz_90_ci} | {amp_agri_90} | {amp_amb_90} | {amp_trag_90} |
| 2000-2009 | {amp_feliz_00} {amp_feliz_00_ci} | {amp_agri_00} | {amp_amb_00} | {amp_trag_00} |
| 2010-2019 | {amp_feliz_10} {amp_feliz_10_ci} | {amp_agri_10} | {amp_amb_10} | {amp_trag_10} |
| 2020-2024* | {amp_feliz_20} {amp_feliz_20_ci} | {amp_agri_20} | {amp_amb_20} | {amp_trag_20} |

\* Cohorte de cinco años. Los recuentos (incluidos los no clasificables: {nc_popular} en el marco popular y {nc_amplio} en el amplio) están en `reports/tables/distribucion_finales_recuentos.csv`.

![Finales felices con IC](figures/fig2_finales_felices_ic.png)

### 5.2 Comparación de los noventa con 2010-2024

**Marco popular.** La proporción de finales felices pasa del {pop_feliz_90} en los noventa al {pop_feliz_rec} {pop_feliz_rec_ci} en 2010-2024: **{pop_d_feliz_rec} {pop_d_feliz_rec_ci}**, una razón de {pop_d_feliz_rec_ratio} {pop_d_feliz_rec_ratio_ci}. El intervalo incluye el cero. Por cohorte: 2010-2019 {pop_d_feliz_10} {pop_d_feliz_10_ci} y 2020-2024 {pop_d_feliz_20} {pop_d_feliz_20_ci}.

Los noventa también tienen la proporción más alta frente a las demás cohortes: la diferencia de los ochenta respecto a los noventa es de {pop_d_feliz_80} {pop_d_feliz_80_ci} y la de los dos mil, de {pop_d_feliz_00}. Estos intervalos también incluyen el cero. El patrón **sugiere** que los noventa fueron un pico más que el final de una época feliz que se rompe en 2010, pero no lo demuestra.

En los demás tipos de final (2010-2024 frente a los noventa):

* Agridulces: {pop_d_agri_rec} {pop_d_agri_rec_ci}.
* Ambiguos: {pop_d_amb_rec} {pop_d_amb_rec_ci}. De los contrastes del marco popular entre 2010-2024 y los noventa, solo excluyen el cero los de estas variables: {pop_excl0_vars}. Además, parte de una base muy baja en los noventa ({pop_amb_90}).
* Trágicos: {pop_d_trag_rec} {pop_d_trag_rec_ci}. Sin indicios de más finales trágicos en el cine popular reciente.

**Efecto ajustado** por género y popularidad: {pop_adj_feliz} {pop_adj_feliz_ci} en finales felices.

**Marco amplio.** La caída aparente es mayor pero mucho más incierta: finales felices {amp_d_feliz_rec} {amp_d_feliz_rec_ci} (ajustado: {amp_adj_feliz} {amp_adj_feliz_ci}) y trágicos {amp_d_trag_rec} {amp_d_trag_rec_ci}, un intervalo que roza el cero. La diferencia procede sobre todo de 2010-2019 (trágicos {amp_d_trag_10} {amp_d_trag_10_ci}); en 2020-2024 es de {amp_d_trag_20} {amp_d_trag_20_ci}. Con 50 películas por cohorte y más no clasificables en los noventa, el resultado es frágil y la sensibilidad apunta en ambos sentidos. Si los no clasificables se cuentan como no felices, la diferencia baja a {amp_s_incl_nc} {amp_s_incl_nc_ci}. En cambio, con otras definiciones de final feliz el intervalo excluye el cero: {amp_sens_excl0_nombres}. En los contrastes del marco amplio excluyen el cero: {amp_excl0_vars}.

### 5.3 Tono del cierre, visión de la vida y protagonistas

![Visión y tono](figures/fig3_vision_y_tono_ic.png)

* **Tono del cierre positivo** (esperanza, alivio o conexión), marco popular: {pop_tono_90} en los noventa; diferencia en 2010-2024: {pop_d_tono_rec} {pop_d_tono_rec_ci}. Marco amplio: {amp_d_tono_rec} {amp_d_tono_rec_ci}.
* **Visión de la vida** (−2 a +2), marco popular: {pop_vision_90} {pop_vision_90_ci} en los noventa; diferencia de {pop_d_vision_rec} {pop_d_vision_rec_ci} en 2010-2024 (ajustada: {pop_adj_vision}). Ochenta: {pop_vision_80} {pop_vision_80_ci}. **En el cine popular no se observa una visión de la vida menos optimista desde 2010**; el intervalo descarta caídas de más de {pop_d_vision_rec_lo_abs} puntos.
* Marco amplio: visión de la vida {amp_d_vision_rec} {amp_d_vision_rec_ci} (ajustada: {amp_adj_vision} {amp_adj_vision_ci}), concentrada en 2010-2019 ({amp_d_vision_10} {amp_d_vision_10_ci}). Es la señal más clara de menor optimismo, pero procede de la muestra pequeña y está sujeta a las reservas del apartado anterior.
* **Protagonistas**, marco popular (noventa frente a 2010-2019): el protagonista sobrevive en el {pop_surv_90} frente al {pop_surv_10}, logra su objetivo en el {pop_obj_90} frente al {pop_obj_10} y hay justicia narrativa en el {pop_just_90} frente al {pop_just_10}. Son valores similares; los IC están en `descriptivos_marco_cohorte.csv`.

**Las dimensiones no son lo mismo.** La visión de la vida media (descriptiva, sin ponderar, ambos marcos juntos) es de {fv_feliz} en los finales felices, {fv_agri} en los agridulces, {fv_amb} en los ambiguos y {fv_trag} en los trágicos. Están muy relacionadas, pero dentro de cada tipo de final hay mucha dispersión (figura 6). Parte de esa relación puede deberse a que los mismos anotadores puntúan ambas dimensiones.

![Final frente a visión](figures/fig6_final_vs_vision.png)

### 5.4 Diferencias por género (marco popular)

![Género](figures/fig4_genero.png)

| Género | n (90s/2010-24) | Feliz 90s | Feliz 2010-24 | Diferencia [IC 95 %] |
|---|---|---|---|---|
| Acción/aventura | {g_accion_n} | {g_accion_90} | {g_accion_rec} | {g_accion_d} {g_accion_ci} |
| Comedia | {g_comedia_n} | {g_comedia_90} | {g_comedia_rec} | {g_comedia_d} {g_comedia_ci} |
| Terror | {g_terror_n} | {g_terror_90} | {g_terror_rec} | {g_terror_d} {g_terror_ci} |
| Thriller/crimen | {g_thriller_n} | {g_thriller_90} | {g_thriller_rec} | {g_thriller_d} {g_thriller_ci} |

Por género, {g_excl0_texto}. La mayor caída puntual es la de {g_mayor_caida} ({g_mayor_caida_d}). La composición por géneros también cambió: en el marco popular, la acción/aventura pasa del {comp_accion_90} al {comp_accion_rec}, la animación del {comp_anim_90} al {comp_anim_rec} y la comedia del {comp_comedia_90} al {comp_comedia_rec} (`composicion_generos.csv`; tabla por género en `genero_contrastes.csv`).

### 5.5 Pruebas de sensibilidad (marco popular, finales felices, 2010-2024 − 1990-1999)

![Sensibilidad](figures/fig5_sensibilidad.png)

| Especificación | Diferencia [IC 95 %] |
|---|---|
| Principal | {pop_d_feliz_rec} {pop_d_feliz_rec_ci} |
| Feliz o agridulce | {pop_s_def_amplia} {pop_s_def_amplia_ci} |
| Feliz con tono positivo | {pop_s_def_estricta} {pop_s_def_estricta_ci} |
| Ponderado por votos de IMDb | {pop_s_votos} {pop_s_votos_ci} |
| No clasificables como no felices | {pop_s_incl_nc} {pop_s_incl_nc_ci} |
| Solo etiquetas de A | {pop_s_soloA} {pop_s_soloA_ci} |
| Solo etiquetas de B | {pop_s_soloB} {pop_s_soloB_ci} |
| Solo acuerdo inicial | {pop_s_acuerdo} {pop_s_acuerdo_ci} |
| Solo confianza alta | {pop_s_conf3} {pop_s_conf3_ci} |
| Solo producciones exclusivamente estadounidenses | {pop_s_usonly} {pop_s_usonly_ci} |
| Umbral más estricto (20 más votadas/año) | {pop_s_top20} {pop_s_top20_ci} |

De las {pop_sens_n} especificaciones alternativas de la tabla (sin contar la principal), {pop_sens_n_neg} mantienen la dirección (menos finales felices después de los noventa). Sin la ponderación por votos, el tamaño varía entre {pop_sens_min_abs} y {pop_sens_max_abs}, y solo en {pop_sens_n_excl0} el intervalo excluye el cero: {pop_sens_excl0_nombres}. **Al ponderar por votos, el resultado se vuelve indeterminado** ({pop_s_votos} {pop_s_votos_ci}; el tamaño efectivo de los noventa baja a unas {pop_s_votos_neff0} películas). Las películas de los noventa más votadas hoy tienen, en proporción, menos finales felices ({popv_feliz_90}) que el conjunto de las 50 más votadas de cada año. Además, ponderar por votos actuales acentúa el sesgo de supervivencia. La variante «solo confianza alta» selecciona los casos más claros y cambia la base (los noventa pasan al {pop_s_conf3_v0}), así que se interpreta con cautela. Un resultado tan dependiente de la especificación no permite hablar de un cambio robusto.

### 5.6 Calidad de la medición

* Acuerdo entre A y B en el final: {pa_final}, kappa de Cohen {k_final} (kappa ponderada ordinal: {wk_final}); final feliz sí/no: kappa {k_feliz}.
* Tono del cierre: kappa {k_tono}; supervivencia {k_surv}; objetivo {k_obj}; vínculos {k_rel}; justicia narrativa {k_just}.
* Visión de la vida: alfa de Krippendorff (intervalo) {alfa_vision} para la puntuación media y entre {alfa_items_min} y {alfa_items_max} por ítem.
* El desacuerdo sobre «final feliz» va del {dis_feliz_min} al {dis_feliz_max} según la cohorte (`desacuerdo_por_grupo_principal.csv`). Por género, el desacuerdo sobre el final es mayor en {dis_top_generos}.

---

## 6. Revisión del análisis de Stephen Follows (2026)

Follows (*Has Hollywood given up on the happy ending?*) examinó 7.384 películas y clasificó los finales de 6.509 sinopsis. Según su artículo, clasificó las sinopsis con un modelo de lenguaje y una rúbrica fija, validada contra etiquetas humanas de bases de datos públicas, y lo contrastó con el análisis de expresiones faciales en 1,57 millones de primeros planos, la tonalidad musical y CinemaScore. Informa de que en torno a tres cuartas partes de las películas de acción de los ochenta y noventa terminaban felizmente, frente al 56 % desde 2010, de que aumentan los finales agridulces y de que los tristes no son más frecuentes que en los ochenta. Él mismo advierte que se trata de correlaciones.

**Lo que no se puede comprobar.** El artículo no publica los datos, no detalla cómo se seleccionaron las películas ni qué países incluye (menciona películas estadounidenses, francesas e indias) y no nombra la fuente de las sinopsis. Por eso no es replicable exactamente y sus cifras no se usan aquí como resultado.

**Comparación orientativa.** Con nuestra definición de acción (género principal Acción/aventura, marco popular), los finales felices pasan del {fol_8099} {fol_8099_ci} en 1980-1999 (n={fol_n_8099}) al {fol_1024} {fol_1024_ci} en 2010-2024 (n={fol_n_1024}): {fol_diff} {fol_diff_ci}. La dirección y el orden de magnitud coinciden con los de Follows, aunque los clasificadores, las fuentes y las poblaciones son distintos. Dos matices: agrupar los ochenta con los noventa, como hace Follows, favorece el contraste, porque la acción de los ochenta tuvo más finales felices ({fol_80}) que la de los noventa ({fol_90}). Y para el conjunto de géneros la diferencia es menor e incierta; la mayor caída puntual por género es la de {g_mayor_caida}, no la de la acción.

---

## 7. ¿Qué dicen los datos sobre la afirmación?

**La afirmación:** «el cine popular de los noventa era más optimista sobre la vida que el actual y el público echa de menos ese optimismo».

### Lo que los datos sostienen

Siempre con las etiquetas de modelos y las limitaciones de la sección 2:

* **En el cine popular no se observa un cambio grande hacia lo sombrío desde los noventa.** Los intervalos descartan una caída de los finales felices mayor de {pop_d_feliz_rec_lo_abs}, un aumento de los trágicos mayor de {pop_d_trag_rec_hi_abs}, una caída del tono de cierre positivo mayor de {pop_d_tono_rec_lo_abs} y una caída de la visión de la vida mayor de {pop_d_vision_rec_lo_abs} puntos (escala de −2 a +2). No haber encontrado diferencias no demuestra que no existan: diferencias moderadas siguen siendo compatibles con los datos.
* Los finales **ambiguos** son algo más frecuentes que en los noventa ({pop_d_amb_rec} {pop_d_amb_rec_ci}), pero los noventa son la excepción: los ochenta y los dos mil tienen niveles parecidos a los actuales.

### Lo que los datos sugieren, sin confirmarlo

* La proporción de finales felices en el cine popular fue **algo mayor en los noventa ({pop_feliz_90}) que en 2010-2024 ({pop_feliz_rec})**: {pop_d_feliz_rec}, IC {pop_d_feliz_rec_ci}, ajustado {pop_adj_feliz} {pop_adj_feliz_ci}. El intervalo incluye el cero.
* Los noventa parecen un **pico** de finales felices dentro de 1980-2024, más que el final de una edad dorada. Los ochenta tienen una proporción parecida a la actual.
* En el cine de acción la caída es mayor ({fol_diff}) y coincide con lo que describe Follows, aunque la comedia cae incluso más ({g_comedia_d}).
* En el marco amplio (cine menos visible) hay indicios de menos finales felices y una visión de la vida más sombría en 2010-2019, pero con una muestra pequeña y problemas de cobertura.

### Lo que los datos no permiten afirmar

* Que el cine de los noventa fuera **claramente** más optimista: la diferencia se vuelve indeterminada al ponderar por popularidad y solo excluye el cero con las etiquetas de uno de los dos anotadores.
* Que hubiera una **prohibición** o presión de la industria para no hacer películas pesimistas: los datos de estrenos no pueden mostrarlo.
* Que el público **eche de menos** ese optimismo: no se ha hecho ninguna encuesta ni experimento. Las taquillas, los votos o los comentarios en redes no permiten inferir nostalgia.
* Nada sobre **causas**: se trata de asociaciones temporales.
* Nada definitivo mientras las etiquetas no se validen con personas.

---

## 8. Fase pendiente: ¿el público lo echa de menos?

La fase de encuesta o experimento está diseñada en `docs/diseno_encuesta.md` y no se ha ejecutado. En resumen:

* Pares de cierres comparables (mismo género, tono equilibrado), presentados como textos breves escritos para el estudio, **sin título ni año**.
* Se miden el optimismo percibido, las ganas de ver más películas de ese tipo, la preferencia entre cierres, la familiaridad previa y la nostalgia declarada.
* Con 8 pares por persona, detectar una preferencia de 5 puntos sobre el 50 % exige unos {enc_5pp} participantes, y comparar a quienes crecieron con el cine de los noventa con los menores de 30 (10 puntos), unos {enc_h2_10}.

Hasta que se haga, **la parte «se echa de menos» de la afirmación queda sin probar**.

---

## 9. Reproducibilidad

Todo el flujo se ejecuta desde el `README.md`: descarga, catálogo, cobertura, muestra, lotes cegados, análisis, gráficos e informe. Las etiquetas de anotación están versionadas en `annotation/labels/`. Las decisiones y sus motivos están en `docs/registro_decisiones.md` y el diccionario de datos, en `docs/diccionario_datos.md`.

## 10. Fuentes

* Follows, S. (2026). *Has Hollywood given up on the happy ending?* https://stephenfollows.com/p/has-hollywood-given-up-on-the-happy-ending (consultado el 2026-09-29).
* IMDb Non-Commercial Datasets. https://developer.imdb.com/non-commercial-datasets/ y condiciones en https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX. *Information courtesy of IMDb (https://www.imdb.com). Used with permission.*
* Wikidata Query Service. https://query.wikidata.org/ (CC0).
* Wikipedia en inglés, volcado del 1 de septiembre de 2026. https://dumps.wikimedia.org/enwiki/20260901/ (CC BY-SA 4.0). Cada sinopsis se atribuye con la URL de su revisión en `data/derived/muestra_principal.csv`.
* Bamman, D., O'Connor, B. y Smith, N. A. (2013). *Learning Latent Personas of Film Characters*. ACL. CMU Movie Summary Corpus: https://www.cs.cmu.edu/~ark/personas/ (CC BY-SA).
* Del Vecchio, M., Kharlamov, A., Parry, G. y Pogrebna, G. (2018). *The Data Science of Hollywood: Using Emotional Arcs of Movies to Drive Business Model Innovation in Entertainment Industries*. arXiv:1807.02221. https://arxiv.org/abs/1807.02221
* Chun, J. (2024). *MultiSentimentArcs: a novel method to measure coherence in multimodal sentiment analysis for long-form narratives in film*. Frontiers in Computer Science. https://doi.org/10.3389/fcomp.2024.1444549
