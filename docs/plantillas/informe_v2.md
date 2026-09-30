
---

## 9. Segunda parte (v2): censo del cine popular, cine español y ánimo de los personajes

La primera parte usaba una muestra aleatoria (150 películas populares por cohorte), y películas muy conocidas como *Titanic* no salieron en el sorteo. En esta segunda parte se anota el **universo completo** del marco popular estadounidense y se añade el cine español. Además, se miden características de los protagonistas y de la trama, y dos dimensiones de ánimo distintas del final: el **tono general** de la película y el **optimismo de los personajes**.

### 9.1 Límites específicos de la segunda parte

* **Sigue sin haber validación humana.** Todas las etiquetas son de dos modelos de lenguaje y un adjudicador.
* **El cegado no funciona en el cine popular.** Al menos un modelo dijo reconocer el {v2_rec_us} de las películas estadounidenses (y el {v2_rec_es} de las españolas). La sensibilidad que excluye las películas reconocidas no puede calcularse en EE. UU.
* **Adjudicación parcial (D-026).** Solo se adjudicaron `final` y los ítems de −2 a 2 con diferencia ≥3. En las demás categóricas en desacuerdo manda el anotador A, así que las covariables del módulo B tienen más error de medición que el núcleo v1.
* **El cine español se lee peor.** La Wikipedia en español a menudo no cuenta el desenlace. Tras volver a anotar {v2_n_esen} películas con la sinopsis inglesa (D-027), el {v2_es_nc} de las españolas sigue sin final clasificable (antes, el {v2_es_nc_antes}). Ese porcentaje varía por cohorte (del {v2_es_10_nc} en 2010-2019 al {v2_es_90_nc} en los noventa), así que las comparaciones españolas se hacen sobre las clasificables, con riesgo de selección. Hay además un umbral de votos distinto del estadounidense (50 frente a 1.000) y sinopsis en varios idiomas o de TMDB (D-035).
* **Un censo de lo que hoy se vota.** «Las 50 más votadas de cada año» se mide con votos actuales, con sesgo de supervivencia. Los intervalos miden la variabilidad del proceso que genera las películas (superpoblación), no un error de muestreo (D-029).
* **Tono y optimismo son juicios más subjetivos** que el tipo de final, aunque el acuerdo fue alto (α {v2_a_tono_general} y {v2_a_optimismo_personajes}). Además, el optimismo de los personajes se infiere de un resumen, no de la película.
* **Muchas comparaciones por subgrupo.** De {v2_sub_n_tests} contrastes de finales felices por subgrupo, {v2_sub_n_sig} excluyen el cero. Con tantas pruebas, alguno lo hará por azar. Se presentan como exploratorios.
* **IMDb solo en agregado.** La relación con la nota de IMDb es asociativa: mide la opinión de quien vota en IMDb, no la del público general, y no dice nada de la nostalgia.

### 9.2 Datos y método

* **Universo estadounidense:** las 50 películas estadounidenses con más votos de cada año, 1980-2025, con sinopsis utilizable: **{v2_n_us} películas**.
* **Universo español:** las 30 películas españolas (sin coproducciones mayoritariamente extranjeras) más votadas de cada año con al menos 50 votos: **{v2_n_es} películas** (D-023, D-033 a D-035). Hay {v2_n_dup} coproducciones que están en ambos universos y cuentan en los dos.
* **Anotación completa** (núcleo del manual 1.0 más módulo B del manual 2.0) de {v2_n_completa} películas con doble anotación ciega. Las {v2_n_modb} películas del universo que ya estaban en la primera parte conservan sus etiquetas del núcleo, adjudicadas por completo, y recibieron solo el módulo B, con el mismo texto cegado.
* **Módulo B:** género, edad, momento vital, estado civil y clase social del protagonista; relaciones centrales (hasta 3); si la historia es especulativa (ciencia ficción, fantasía, sobrenatural, superhéroes); época y países de la trama; humor; tono general (−2 a +2); optimismo de los personajes (−2 a +2).
* **Acuerdo A-B** (películas nuevas): final κ = {v2_k_final}; tono de cierre κ = {v2_k_tono_cierre}; momento vital κ = {v2_k_momento_vital}; clase social κ = {v2_k_clase_social}; estado civil κ = {v2_k_estado_civil}; especulativa κ = {v2_k_especulativa}; época κ = {v2_k_epoca_trama}; humor κ = {v2_k_humor}; tono general α = {v2_a_tono_general}; optimismo de los personajes α = {v2_a_optimismo_personajes}; relaciones (Jaccard) {v2_j_relaciones_centrales}; países (Jaccard) {v2_j_paises_trama}. En las películas de la primera parte, las κ del módulo B van de {v2_km_min} a {v2_km_max}. Tablas: `reports/tables/acuerdo_v2_completa.csv` y `acuerdo_v2_modb.csv`.
* **Adjudicación:** {v2_n_adj} finales adjudicados por un tercer modelo que no sabía qué anotador había dicho qué.
* **Análisis** (`src/finales/analysis_v2.py`): proporciones con intervalo de Wilson y medias con IC t; contrastes entre 2010-2025 y los noventa con bootstrap por película (2.000 réplicas); modelos ajustados en EE. UU. (logit con efecto marginal medio por g-computación para final feliz; MCO con errores HC3 para el optimismo), controlando género, log del rango de votos en el año y, en una segunda especificación, especulativa, época contemporánea, clase social, momento vital, género del protagonista y humor. Relación con IMDb: MCO de la nota media y del log de los votos sobre final feliz, optimismo o tono, con efectos fijos de año y género.

### 9.3 Resultados

**Tipos de final y ánimo por cohorte** (finales sobre películas clasificables):

{v2_tabla_cohortes}

**EE. UU.: el censo confirma una caída pequeña de los finales felices, concentrada en 2020-2025.** En los noventa acababa bien el {v2_us_90_feliz} {v2_us_90_feliz_ci} de las películas populares; en 2010-2025, el {v2_us_rec_feliz}. La diferencia es de {v2_us_drec_feliz} {v2_us_drec_feliz_ci}. Por cohortes: 2010-2019 {v2_us_d10_feliz} {v2_us_d10_feliz_ci} y 2020-2025 {v2_us_d20_feliz} {v2_us_d20_feliz_ci}. Los ochenta ({v2_us_80_feliz}) y los dos mil ({v2_us_00_feliz}) también quedan por debajo de los noventa, que vuelven a parecer un pico. Ajustado por género y popularidad, la diferencia es de {v2_adj_b_10} en 2010-2019 y {v2_adj_b_20} en 2020-2025. Si se ajusta también por protagonista y trama, queda en {v2_adj_x_10} y {v2_adj_x_20}: parte de la caída se explica por el tipo de historias. Los finales trágicos no aumentan ({v2_us_drec_tragico} {v2_us_drec_tragico_ci}).

**El optimismo de los personajes no ha bajado, salvo en 2020-2025.** La media del cine popular estadounidense va de {v2_us_80_opt} en los ochenta a {v2_us_90_opt} en los noventa y {v2_us_10_opt} en 2010-2019. En 2020-2025 cae a {v2_us_20_opt} ({v2_us_d20_optimismo} {v2_us_d20_optimismo_ci} frente a los noventa). El **tono general** sí se oscurece algo: {v2_us_drec_tono} {v2_us_drec_tono_ci} entre los noventa y 2010-2025.

**Final y ánimo son cosas distintas.** Entre los finales felices, el {v2_opt_en_feliz} tiene personajes optimistas; entre los agridulces, el {v2_opt_en_agridulce}; entre los ambiguos, el {v2_opt_en_ambiguo}; y entre los trágicos, {v2_frac_trag_opt} ({v2_opt_en_tragico}). *Titanic* se clasifica como final {v2_titanic_final}, con optimismo de los personajes {v2_titanic_opt}: es el caso típico de desenlace con pérdida y personajes vitalistas. Las «tragedias vitalistas» en sentido estricto (final trágico y personajes optimistas) son raras: el {v2_tragvit_pct} de las películas. La proporción de finales no felices con personajes optimistas no cambia de forma clara entre los noventa y 2010-2025 ({v2_us_drec_no_feliz_optimista} {v2_us_drec_no_feliz_optimista_ci}).

**¿Dónde cayó el final feliz? (EE. UU., exploratorio).** Los subgrupos en los que la caída entre los noventa y 2010-2025 excluye el cero son: {v2_sub_caidas}. En la comedia baja además el optimismo de los personajes ({v2_sub_comedia_opt} puntos). Las diferencias por clase alta, drama o historias de época tienen signo positivo, pero con intervalos amplios.

**España va al revés.** El cine español popular es mucho menos feliz y mucho más sombrío que el estadounidense: el tono general medio es {v2_es_tono_all}, frente a {v2_us_tono_all}. Pero sus finales felices **suben**: del {v2_es_90_feliz} {v2_es_90_feliz_ci} en los noventa al {v2_es_rec_feliz} en 2010-2025 ({v2_es_drec_feliz} {v2_es_drec_feliz_ci}; el intervalo apenas excluye el cero), y los trágicos bajan ({v2_es_drec_tragico} {v2_es_drec_tragico_ci}). El optimismo de los personajes no cambia ({v2_es_drec_optimismo} {v2_es_drec_optimismo_ci}). Con cambios en la proporción de no clasificables y sinopsis de fuentes e idiomas distintos, este resultado es frágil (ver sensibilidad).

**IMDb (asociación, en agregado).** Entre películas del mismo año y género, las de final feliz tienen una nota media de IMDb {v2_imdb_us_nota_feliz} puntos distinta {v2_imdb_us_nota_feliz_ci} en EE. UU. y {v2_imdb_es_nota_feliz} {v2_imdb_es_nota_feliz_ci} en España. Cada punto de optimismo de los personajes se asocia con {v2_imdb_us_nota_opt} {v2_imdb_us_nota_opt_ci} puntos de nota en EE. UU. Los finales felices también acumulan algo menos de votos (log de votos {v2_imdb_us_votos_feliz} {v2_imdb_us_votos_feliz_ci}). Quien vota en IMDb puntúa algo mejor las películas menos felices; eso no dice nada de si el público echa de menos el optimismo.

### 9.4 Sensibilidad (2010-2025 − 1990-1999)

{v2_tabla_sens}

En EE. UU., la caída de finales felices se mantiene con las etiquetas de un solo anotador y, en el límite, sin coproducciones. En cambio, pierde nitidez al excluir las películas que ya estaban en la primera parte: con solo las películas nuevas del censo, el intervalo incluye el cero. En España, el aumento se sostiene con el anotador A y sin la reanotación D-027, pero no con el anotador B ni al separar por idioma de la sinopsis. En los dos países, el optimismo de los personajes no cambia con ningún anotador.

### 9.5 ¿Qué añade la segunda parte a la conclusión?

**Lo que los datos sostienen.** Con el censo completo del cine popular estadounidense, los noventa tienen más finales felices que 2010-2025 ({v2_us_drec_feliz} {v2_us_drec_feliz_ci}), sobre todo por 2020-2025. Pero no hay más tragedias y el optimismo de los personajes no baja hasta 2020. Final y ánimo son dimensiones distintas: muchos finales agridulces, como el de *Titanic*, tienen personajes optimistas.

**Lo que sugieren, sin confirmarlo.** La caída se concentra en la ciencia ficción, la comedia, la acción, las historias con protagonista femenina y las de personajes en crisis vital. El tono general es algo más oscuro que en los noventa. En el cine español la tendencia es la contraria, con más finales felices en 2010-2025. Y las notas de IMDb son algo más bajas para los finales felices.

**Lo que no permiten afirmar.** Que hubiera una prohibición de películas pesimistas en los noventa; que el público eche de menos ese optimismo (la encuesta sigue sin hacerse); las causas de ninguno de estos cambios. Tampoco que las diferencias entre subgrupos sean robustas, dado el número de comparaciones.
