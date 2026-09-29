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
2. **El cegado es incompleto.** Se retiraron título y años, pero los anotadores dijeron reconocer la película en el 90 % (anotador A) y el 86 % (anotador B) de los casos; por cohorte, entre el 89 % y el 95 % fue reconocido por al menos uno. Pudieron usar lo que «saben» de la película o de su época. La prueba de sensibilidad que excluye las películas reconocidas no es evaluable en el marco popular (quedan 3/5 películas).
3. **Las sinopsis son de Wikipedia y están escritas hoy.** Es una ventaja (todas las décadas se describen con las mismas convenciones y en la misma época) y un riesgo (lo que los editores eligen contar puede variar según la película sea antigua o reciente, o más o menos conocida). El análisis mide los finales **tal como los resume Wikipedia**, no las películas.
4. **La popularidad se mide con votos actuales de IMDb.** Los votos son retrospectivos: las películas de los noventa que hoy tienen muchos votos son las que se siguen recordando, lo que introduce un sesgo de supervivencia que puede diferir por década. La taquilla de Wikidata es escasa y no está ajustada por inflación, así que no se usó.
5. **La muestra es pequeña para diferencias moderadas.** Con 150 películas por cohorte en el marco popular, la diferencia mínima detectable (potencia del 80 %) entre los noventa y 2010-2024 es de unos 13,8 pp. Para detectar 10 puntos harían falta unas 293 películas por cohorte. En el marco amplio (50 por cohorte) la diferencia mínima detectable es de 23,9 pp. **El análisis es exploratorio, no representativo en sentido estricto.**
6. **Marco amplio con umbral de visibilidad.** El marco amplio no es todo el cine estadounidense, sino las películas con al menos 1.000 votos en IMDb, artículo en Wikipedia y sección argumental de 120 palabras o más. En ese marco faltan más desenlaces en algunas cohortes (no clasificables: 8 en los noventa frente a 3 en 2010-2019), y eso influye en las comparaciones.
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

**Por qué no se usó el CMU Movie Summary Corpus como fuente principal.** Se construyó con un volcado de Wikipedia de 2012 y su cobertura de películas recientes es insuficiente: tiene sinopsis para el 83 % del catálogo de los noventa, pero solo para el 17 % del de 2010-2019 y el 0 % del de 2020-2024 (`reports/tables/cobertura_cmu.csv`). Mezclar fuentes por década habría confundido el cambio en las películas con el cambio de fuente.

**Por qué el volcado y no la API.** La API REST de Wikipedia devolvía de forma sistemática HTTP 429 (demasiadas peticiones) desde la IP compartida del entorno. El volcado público permite leer por rangos HTTP solo los bloques con los artículos necesarios, con una versión fechada y verificable.

---

## 4. Método

### 4.1 Catálogo

A partir de IMDb: `titleType = movie`, año 1980-2024, duración de 60 minutos o más, sin géneros de no ficción (*Documentary*, *Reality-TV*, *Talk-Show*, *News*, *Game-Show*, *Adult*), al menos 1.000 votos, país de origen EE. UU. en Wikidata, artículo en la Wikipedia en inglés y año coherente entre IMDb y Wikidata (desfase de un año como máximo). Los duplicados de artículo se resuelven conservando el título con más votos. Cada exclusión recibe un único motivo, el primer filtro que falla (`reports/tables/exclusiones_resumen.csv`). Por ejemplo, 179.382 títulos del periodo quedaron fuera por no llegar a 1.000 votos y 21.579 por no constar como estadounidenses en Wikidata.

Catálogo elegible: **13.950 películas** (1980-89: 1.817; 1990-99: 2.368; 2000-09: 3.332; 2010-19: 4.503; 2020-24: 1.930).

### 4.2 Marcos de muestra

* **Popular**: las 50 películas con más votos de cada año. Por cohorte se extraen 150 películas, repartidas por género principal en proporción a su peso en ese universo.
* **Amplio**: todo el catálogo elegible. Por cohorte se extraen 50 películas, a partes iguales entre los tres terciles de votos de cada año y, dentro de cada tercil, en proporción al género. Cada película lleva su peso de diseño (tamaño del estrato / muestra del estrato).

El orden aleatorio es estable (hash de semilla y título) y no depende del orden de las filas. Las películas sin sinopsis utilizable se sustituyen por la siguiente del mismo estrato y quedan registradas: 47 sustituciones en total (4 en el marco popular y 43 en el amplio; `reports/tables/muestreo_log_principal.csv`). Las del piloto no entran en la muestra principal. Resultado: 1000 filas y **994 películas distintas** (6 están en ambos marcos). La mediana de longitud de las sinopsis es de 627 palabras.

El **género principal** se asigna con una prioridad fija sobre los hasta tres géneros de IMDb: Animación > Terror > Acción/aventura > Ciencia ficción/fantasía > Comedia > Romance > Thriller/crimen > Drama > Otros.

### 4.3 Anotación

El **manual** (`docs/manual_anotacion.md`) define cinco dimensiones que se miden por separado:

1. **Final**: feliz, agridulce, ambiguo, trágico o no clasificable.
2. **Resultado para los protagonistas**: supervivencia, objetivo, vínculos y justicia narrativa.
3. **Tono del cierre**: esperanza, alivio, conexión, resignación o desesperanza (y su valencia).
4. **Visión de la vida**: agencia, posibilidad de cambio, valor de los vínculos y expectativa de futuro, de −2 a +2.
5. **Arco emocional**: **no se ha medido**. Requiere guiones o subtítulos con procedencia y permisos verificables, y no se encontró ningún corpus así.

**Piloto.** Con 50 películas de todas las cohortes, dos anotadores independientes obtuvieron un kappa de Cohen de 0,87 para el final y de 0,48 para el tono del cierre. El manual se ajustó solo con el piloto (reglas marcadas [v1.0]: poscréditos, finales alternativos, dos protagonistas, historias sin conflicto central, procedimiento de decisión del tono) y se congeló como versión 1.0 antes de la muestra principal; su hash está en `docs/manual_anotacion_v1.0.sha256`. Ninguna definición de las categorías de final cambió.

**Tamaño.** En el piloto, la proporción de finales felices fue del 58 % y la desviación típica de la visión de la vida, de 1,18. Con esos valores, detectar 10 puntos de diferencia exigiría 293 películas por cohorte y detectar 15, 130 (`reports/tables/potencia_piloto.csv`). Por capacidad de anotación se fijaron 150 por cohorte en el marco popular y 50 en el amplio.

**Anotadores.** Cada sinopsis cegada (sin título ni años) la anotaron **dos modelos de lenguaje distintos, de forma independiente** (A y B), en lotes de 50 con el orden de cohortes mezclado. Los desacuerdos de cualquier campo, y las diferencias de 3 o más puntos en los ítems, los resolvió un **adjudicador** que veía las dos etiquetas en orden aleatorio sin saber de quién era cada una. Se adjudicaron 522 películas, 96 de ellas por desacuerdo en el final. El adjudicador comparte familia de modelo con el anotador A y le dio la razón en el 74 % de los desacuerdos sobre el final. Por eso hay pruebas de sensibilidad con las etiquetas de A solas y de B solas.

**Corrección durante la anotación.** A mitad de la anotación se detectó que en algunos artículos la extracción de la sección argumental arrastraba texto de producción o de recepción. Se corrigió el extractor (con pruebas), se volvieron a anotar las 6 películas ya anotadas afectadas y se apartaron sus etiquetas obsoletas (`reports/tables/reanotacion_correccion_sinopsis.csv`, registro D-017).

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
| 1980-1989 | 56,7 % [48,7 %; 64,3 %] | 26,7 % | 6,7 % | 10,0 % |
| 1990-1999 | 66,0 % [58,1 %; 73,1 %] | 24,7 % | 2,0 % | 7,3 % |
| 2000-2009 | 57,3 % [49,3 %; 65,0 %] | 28,7 % | 8,0 % | 6,0 % |
| 2010-2019 | 58,7 % [50,7 %; 66,2 %] | 29,3 % | 6,7 % | 5,3 % |
| 2020-2024* | 55,7 % [47,7 %; 63,4 %] | 28,2 % | 8,1 % | 8,1 % |

**Marco amplio (50 películas por cohorte, ponderado por diseño):**

| Cohorte | Feliz | Agridulce | Ambiguo | Trágico |
|---|---|---|---|---|
| 1980-1989 | 57,4 % [43,2 %; 70,5 %] | 23,4 % | 6,4 % | 12,8 % |
| 1990-1999 | 66,6 % [51,5 %; 78,9 %] | 26,3 % | 0,0 % | 7,1 % |
| 2000-2009 | 67,6 % [52,7 %; 79,7 %] | 13,8 % | 7,1 % | 11,5 % |
| 2010-2019 | 47,1 % [33,6 %; 61,1 %] | 27,6 % | 2,1 % | 23,2 % |
| 2020-2024* | 56,3 % [42,3 %; 69,3 %] | 22,8 % | 10,5 % | 10,5 % |

\* Cohorte de cinco años. Los recuentos (incluidos los no clasificables: 1 en el marco popular y 23 en el amplio) están en `reports/tables/distribucion_finales_recuentos.csv`.

![Finales felices con IC](figures/fig2_finales_felices_ic.png)

### 5.2 Comparación de los noventa con 2010-2024

**Marco popular.** La proporción de finales felices pasa del 66,0 % en los noventa al 57,7 % [51,7 %; 63,4 %] en 2010-2024: **−8,3 pp [−17,9 pp; +1,2 pp]**, una razón de 0,87 [0,75; 1,02]. El intervalo incluye el cero. Por cohorte: 2010-2019 −7,3 pp [−18,7 pp; +3,3 pp] y 2020-2024 −10,3 pp [−21,0 pp; +0,4 pp].

Los noventa destacan también frente a las demás cohortes: la diferencia de los ochenta respecto a los noventa es de −9,3 pp [−20,0 pp; +2,0 pp] y la de los dos mil, de −8,7 pp. Es decir, **los noventa aparecen como un pico, no como el final de una época más feliz que empieza a caer en 2010**.

En los demás tipos de final (2010-2024 frente a los noventa):

* Agridulces: +4,3 pp [−4,7 pp; +13,2 pp].
* Ambiguos: +5,1 pp [+1,2 pp; +9,0 pp]. Es el único cambio cuyo intervalo excluye el cero, pero parte de una base muy baja en los noventa (2,0 %).
* Trágicos: −1,1 pp [−6,3 pp; +3,7 pp]. Sin indicios de más finales trágicos en el cine popular reciente.

**Efecto ajustado** por género y popularidad: −7,7 pp [−17,7 pp; +1,5 pp] en finales felices.

**Marco amplio.** La caída aparente es mayor pero mucho más incierta: finales felices −16,7 pp [−34,3 pp; +0,8 pp] (ajustado: −11,5 pp [−27,6 pp; +1,4 pp]) y trágicos +12,2 pp [+0,4 pp; +24,1 pp]. La diferencia se concentra en 2010-2019 (trágicos +16,0 pp [+2,0 pp; +30,1 pp]), no en 2020-2024. Con 50 películas por cohorte y más no clasificables en los noventa, este resultado es frágil: si los no clasificables se cuentan como no felices, la diferencia baja a −8,9 pp [−26,2 pp; +8,3 pp].

### 5.3 Tono del cierre, visión de la vida y protagonistas

![Visión y tono](figures/fig3_vision_y_tono_ic.png)

* **Tono del cierre positivo** (esperanza, alivio o conexión), marco popular: 78,5 % en los noventa; diferencia en 2010-2024: −1,6 pp [−9,9 pp; +6,8 pp]. Marco amplio: −11,7 pp [−27,1 pp; +4,4 pp].
* **Visión de la vida** (−2 a +2), marco popular: 0,88 [0,74; 1,03] en los noventa; diferencia de +0,06 [−0,11; +0,24] en 2010-2024 (ajustada: +0,03). Los ochenta puntúan más bajo (0,61 [0,45; 0,78]). **En el cine popular no hay indicios de una visión de la vida menos optimista desde 2010.**
* Marco amplio: visión de la vida −0,51 [−0,88; −0,13] (ajustada: −0,42 [−0,77; −0,08]), concentrada en 2010-2019 (−0,66 [−1,14; −0,22]). Es la señal más clara de menor optimismo, pero procede de la muestra pequeña y está sujeta a las reservas del apartado anterior.
* **Protagonistas**, marco popular (noventa frente a 2010-2019): el protagonista sobrevive en el 81,9 % frente al 83,8 %, logra su objetivo en el 79,0 % frente al 75,5 % y hay justicia narrativa en el 66,4 % frente al 62,7 %. Son valores similares; los IC están en `descriptivos_marco_cohorte.csv`.

**Las dimensiones no son lo mismo.** La visión de la vida media es de 1,32 en los finales felices, 0,48 en los agridulces, −0,18 en los ambiguos y −1,30 en los trágicos: están muy relacionadas, pero dentro de cada tipo de final hay mucha dispersión (figura 6). Parte de esa relación puede deberse a que los mismos anotadores puntúan ambas dimensiones.

![Final frente a visión](figures/fig6_final_vs_vision.png)

### 5.4 Diferencias por género (marco popular)

![Género](figures/fig4_genero.png)

| Género | n (90s/2010-24) | Feliz 90s | Feliz 2010-24 | Diferencia [IC 95 %] |
|---|---|---|---|---|
| Acción/aventura | 52/146 | 71 % | 60 % | −11,0 pp [−24,8 pp; +4,0 pp] |
| Comedia | 30/34 | 87 % | 67 % | −20,0 pp [−40,1 pp; +1,3 pp] |
| Terror | 13/36 | 46 % | 41 % | −5,3 pp [−36,5 pp; +27,2 pp] |
| Thriller/crimen | 19/25 | 37 % | 36 % | −0,7 pp [−30,2 pp; +27,8 pp] |

En ningún género el intervalo excluye el cero. La composición por géneros también cambió: en el marco popular, la acción/aventura pasa del 35 % al 49 %, la animación del 5 % al 8 % y la comedia del 20 % al 11 % (`composicion_generos.csv`; tabla por género en `genero_contrastes.csv`).

### 5.5 Pruebas de sensibilidad (marco popular, finales felices, 2010-2024 − 1990-1999)

![Sensibilidad](figures/fig5_sensibilidad.png)

| Especificación | Diferencia [IC 95 %] |
|---|---|
| Principal | −8,3 pp [−17,9 pp; +1,2 pp] |
| Feliz o agridulce | −4,0 pp [−10,0 pp; +2,3 pp] |
| Feliz con tono positivo | −7,9 pp [−17,7 pp; +1,7 pp] |
| Ponderado por votos de IMDb | +1,9 pp [−15,5 pp; +17,8 pp] |
| No clasificables como no felices | −8,4 pp [−17,8 pp; +1,3 pp] |
| Solo etiquetas de A | −10,5 pp [−20,2 pp; −0,9 pp] |
| Solo etiquetas de B | −7,0 pp [−16,6 pp; +2,5 pp] |
| Solo acuerdo inicial | −7,5 pp [−17,5 pp; +2,6 pp] |
| Solo confianza alta | −8,1 pp [−16,7 pp; +0,8 pp] |
| Solo producciones exclusivamente estadounidenses | −4,9 pp [−15,3 pp; +6,1 pp] |
| Umbral más estricto (20 más votadas/año) | −7,4 pp [−23,8 pp; +8,7 pp] |

La dirección se mantiene (menos finales felices después de los noventa) en 10 de las 11 especificaciones alternativas de «final feliz» evaluables, pero sin ponderar por votos el tamaño varía entre 4,9 pp y 10,5 pp, y solo en 1 el intervalo excluye el cero (Solo etiquetas del anotador A (sin adjudicación)). **Al ponderar por votos, la diferencia desaparece** (+1,9 pp): las películas de los noventa más votadas hoy tienen, en proporción, menos finales felices (51,0 %) que el conjunto de las 50 más votadas de cada año. Un resultado tan dependiente de la ponderación no permite hablar de un cambio robusto.

### 5.6 Calidad de la medición

* Acuerdo entre A y B en el final: 90 %, kappa de Cohen 0,84 (kappa ponderada ordinal: 0,90); final feliz sí/no: kappa 0,88.
* Tono del cierre: kappa 0,73; supervivencia 0,83; objetivo 0,75; vínculos 0,77; justicia narrativa 0,76.
* Visión de la vida: alfa de Krippendorff (intervalo) 0,95 para la puntuación media y entre 0,88 y 0,91 por ítem.
* El desacuerdo sobre «final feliz» va del 3,0 % al 8,1 % según la cohorte, sin una tendencia clara por época (`desacuerdo_por_grupo_principal.csv`). Es más alto en drama y thriller.

---

## 6. Revisión del análisis de Stephen Follows (2026)

Follows (*Has Hollywood given up on the happy ending?*) examinó 7.384 películas y clasificó los finales de 6.509 sinopsis. Según su artículo, clasificó las sinopsis con un modelo de lenguaje y una rúbrica fija, validada contra etiquetas humanas de bases de datos públicas, y lo contrastó con el análisis de expresiones faciales en 1,57 millones de primeros planos, la tonalidad musical y CinemaScore. Informa de que en torno a tres cuartas partes de las películas de acción de los ochenta y noventa terminaban felizmente, frente al 56 % desde 2010, de que aumentan los finales agridulces y de que los tristes no son más frecuentes que en los ochenta. Él mismo advierte que se trata de correlaciones.

**Lo que no se puede comprobar.** El artículo no publica los datos, no detalla cómo se seleccionaron las películas ni qué países incluye (menciona películas estadounidenses, francesas e indias) y no nombra la fuente de las sinopsis. Por eso no es replicable exactamente y sus cifras no se usan aquí como resultado.

**Comparación orientativa.** Con nuestra definición de acción (género principal Acción/aventura, marco popular), los finales felices pasan del 73,7 % [64,0 %; 81,5 %] en 1980-1999 (n=95) al 60,2 % [51,6 %; 68,1 %] en 2010-2024 (n=146): −13,5 pp [−25,4 pp; −1,1 pp]. La dirección y el orden de magnitud coinciden con los de Follows, con clasificadores, fuentes y poblaciones distintos. Pero en nuestra muestra la acción es el caso más favorable a la hipótesis: para el conjunto de géneros la diferencia es menor e incierta y, fuera de la acción, los ochenta se parecen más al cine actual que a los noventa.

---

## 7. ¿Qué dicen los datos sobre la afirmación?

**La afirmación:** «el cine popular de los noventa era más optimista sobre la vida que el actual y el público echa de menos ese optimismo».

### Lo que los datos sostienen

* En esta muestra de cine popular estadounidense, la proporción de finales felices fue **algo mayor en los noventa (66,0 %) que en 2010-2024 (57,7 %)**, aunque la diferencia (−8,3 pp, IC [−17,9 pp; +1,2 pp]) es compatible con cero y con una caída de hasta 17,9 pp.
* **No hay más finales trágicos** en el cine popular reciente (−1,1 pp), ni un tono de cierre menos positivo (−1,6 pp), ni una visión de la vida menos optimista (+0,06 en una escala de −2 a +2).
* Los finales **ambiguos** son algo más frecuentes que en los noventa (+5,1 pp), pero los noventa son la excepción: los ochenta y los dos mil tienen niveles parecidos a los actuales.

### Lo que los datos sugieren, sin confirmarlo

* Los noventa parecen un **pico** de finales felices dentro de 1980-2024, más que el final de una edad dorada. Los ochenta tienen una proporción parecida a la actual.
* En el cine de acción la caída es mayor (−13,5 pp) y coincide con lo que describe Follows.
* En el marco amplio (cine menos visible) hay indicios de menos finales felices y una visión de la vida más sombría en 2010-2019, pero con una muestra pequeña y problemas de cobertura.

### Lo que los datos no permiten afirmar

* Que el cine de los noventa fuera **claramente** más optimista: la diferencia no es robusta a la ponderación por popularidad y depende de qué anotador se tome como referencia.
* Que hubiera una **prohibición** o presión de la industria para no hacer películas pesimistas: los datos de estrenos no pueden mostrarlo.
* Que el público **eche de menos** ese optimismo: no se ha hecho ninguna encuesta ni experimento. Las taquillas, los votos o los comentarios en redes no permiten inferir nostalgia.
* Nada sobre **causas**: se trata de asociaciones temporales.
* Nada definitivo mientras las etiquetas no se validen con personas.

---

## 8. Fase pendiente: ¿el público lo echa de menos?

La fase de encuesta o experimento está diseñada en `docs/diseno_encuesta.md` y no se ha ejecutado. En resumen:

* Pares de cierres comparables (mismo género, tono equilibrado), presentados como textos breves escritos para el estudio, **sin título ni año**.
* Se miden el optimismo percibido, las ganas de ver más películas de ese tipo, la preferencia entre cierres, la familiaridad previa y la nostalgia declarada.
* Con 8 pares por persona, detectar una preferencia de 5 puntos sobre el 50 % exige unos 167 participantes, y comparar a quienes crecieron con el cine de los noventa con los menores de 30 (10 puntos), unos 160.

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
