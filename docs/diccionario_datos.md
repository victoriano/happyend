# Diccionario de datos

## `data/derived/muestra_{piloto,principal}.csv` (versionado)

Una fila por película y marco (una película puede aparecer en los dos marcos).

| Campo | Tipo | Descripción | Origen |
|---|---|---|---|
| `tconst` | texto | Identificador de título de IMDb | IMDb |
| `frame` | `popular` / `amplio` | Marco de muestra | diseño |
| `cohort` | texto | Cohorte de estreno (1980-1989 … 2020-2024) | derivado de `year` |
| `stratum_pop` | texto | Estrato de popularidad (`top` en el marco popular; `T1`-`T3` = tercil de votos dentro del año en el amplio, T3 el más votado) | diseño |
| `N_stratum`, `n_stratum` | entero | Tamaño del estrato en el universo y en la muestra (cohorte × estrato de popularidad) | diseño |
| `design_weight` | real | Peso de diseño = `N_stratum / n_stratum` | diseño |
| `wikidata_ids` | texto | QID(s) de Wikidata separados por `|` | Wikidata (CC0) |
| `year` | entero | Año de estreno (`startYear` de IMDb) | IMDb |
| `genre_main` | texto | Género principal asignado por prioridad (ver `config/config.yaml`) | derivado de los géneros de IMDb |
| `pop_tier` | 1-3 | Tercil de votos dentro del año | derivado de IMDb |
| `votes_rank_in_year` | entero | Rango por votos dentro del año de estreno (1 = más votada) en la descarga del 2026-09-29 | derivado de IMDb |
| `in_popular_universe` | booleano | Entre las 50 con más votos de su año | derivado de IMDb |
| `us_only` | booleano | Único país de origen: EE. UU. | Wikidata |
| `n_countries` | entero | Número de países de origen | Wikidata |
| `synopsis_source` | texto | Volcado de Wikipedia usado | Wikipedia |
| `synopsis_revision_url` | URL | Revisión exacta de Wikipedia (atribución CC BY-SA 4.0) | Wikipedia |
| `synopsis_heading` | texto | Encabezado de la sección extraída (*Plot*, *Synopsis*…) | Wikipedia |
| `synopsis_retrieved_at` | fecha y hora UTC | Momento de la extracción | flujo |
| `synopsis_license` | texto | Licencia del texto | Wikipedia |
| `synopsis_words` | entero | Palabras de la sección extraída (antes de truncar) | derivado |
| `synopsis_status` | texto | `ok`, `sin_seccion_argumental`, etc. | flujo |

No se incluyen votos, puntuaciones ni géneros literales de IMDb (D-015), ni el texto de las sinopsis (D-014).

## `annotation/labels/<etapa>/{A,B}/*.jsonl` (versionado)

Una línea por película anotada, con los campos definidos en la sección 7 de `docs/manual_anotacion.md`: `id` (identificador cegado), `final`, `supervivencia`, `objetivo`, `relaciones`, `justicia_narrativa`, `tono_cierre`, `agencia`, `cambio`, `vinculos`, `futuro` (−2..2 o null), `describe_final`, `reconocida`, `confianza` (1-3) y `nota`.

`annotation/labels/principal/adjudicacion/*.jsonl`: `id`, los campos en desacuerdo con el valor elegido y `nota`.

`annotation/labels/principal_obsoletas/`: etiquetas descartadas por la corrección D-017 (se conservan por trazabilidad; no entran en el análisis).

## `annotation/batches/<etapa>/*.jsonl` (versionado)

`id` y `sinopsis` cegada (título → `[TÍTULO]`, años → `[AÑO]`, truncado si pasa de 1.100 palabras). Texto derivado de Wikipedia, CC BY-SA 4.0; la atribución por película está en `muestra_*.csv`. Los lotes de adjudicación añaden `etiqueta_X`, `etiqueta_Y` y `campos_en_desacuerdo`.

## `annotation/claves/*_key.csv` (versionado)

Correspondencia `id` cegado → `tconst`, lote, palabras originales y si la sinopsis se truncó. En la adjudicación, si X/Y se intercambiaron. **No se entrega a los anotadores**; se versiona porque sin ella no se pueden unir etiquetas y películas (D-022).

## Ficheros intermedios (no versionados; se regeneran)

| Fichero | Contenido |
|---|---|
| `data/interim/catalog.csv` | Catálogo elegible con campos de IMDb (votos, puntuación, géneros), Wikidata y popularidad |
| `data/interim/exclusions.csv` | `tconst`, año, cohorte y motivo de exclusión |
| `data/interim/wikidata_us_films.csv` | Resultado de las consultas SPARQL (ítem, tconst, artículo, país, fecha) |
| `data/interim/synopses/{tconst}.json` | Sección argumental extraída, revisión, id de página y estado |
| `data/interim/analitico_principal.csv` | Conjunto analítico: muestra + etiquetas finales + variables de resultado |

## Variables de resultado (en `analitico_principal.csv`)

| Variable | Definición |
|---|---|
| `y_feliz`, `y_agridulce`, `y_ambiguo`, `y_tragico` | 1/0 sobre las películas clasificables (se excluye `NO_CLASIFICABLE`) |
| `y_resolucion_positiva` | Feliz o agridulce |
| `y_feliz_estricto` | Feliz y tono de cierre positivo |
| `y_feliz_incl_nc` | Feliz sobre todas las películas (los no clasificables cuentan como 0) |
| `y_feliz_A`, `y_feliz_B` | Final feliz según un solo anotador, sin adjudicación |
| `y_tono_positivo` | Tono de cierre esperanza, alivio o conexión (se excluye `NO_CLARO`) |
| `y_sobrevive`, `y_objetivo`, `y_justicia`, `y_relaciones` | Resultados para los protagonistas (se excluyen `NO_CLARO`/`NO_APLICA`) |
| `vision_vida` | Media de agencia, cambio, vínculos y futuro con al menos 3 ítems no nulos; los ítems son la media de A y B (o el valor adjudicado) |
| `periodo` | Cohorte, con 2010-2019 y 2020-2024 agrupadas en 2010-2024 |
| `w_design`, `w_votes` | Peso de diseño y peso de diseño × votos de IMDb |

## Tablas de `reports/tables/` (versionadas)

Cada tabla la genera el módulo indicado. Las cifras del informe se leen de ellas (`valores_informe.json` guarda el volcado).

| Tabla | Módulo |
|---|---|
| `exclusiones_resumen.csv`, `catalogo_por_cohorte.csv` | `clean` |
| `cobertura_cmu.csv` | `pipeline coverage` |
| `muestreo_log_{piloto,principal}.csv` | `pipeline pilot/main` |
| `acuerdo_*.csv`, `confusion_final_*.csv`, `desacuerdo_por_grupo_*.csv`, `marginales_anotadores_*.csv` | `analysis.agreement_report` |
| `descriptivos_*.csv`, `contrastes_vs_1990s.csv`, `efectos_ajustados.csv`, `sensibilidad.csv`, `genero_contrastes.csv`, `composicion_generos.csv`, `comparacion_follows_accion.csv`, `adjudicacion_resumen.csv`, `reconocimiento_por_cohorte.csv`, `no_clasificables_por_cohorte.csv`, `final_vs_vision.csv`, `distribucion_*_recuentos.csv` | `analysis.run` |
| `potencia_piloto.csv`, `parametros_piloto.csv`, `potencia_encuesta.csv` | `power` |
| `reanotacion_correccion_sinopsis.csv` | `scripts/rebatch_d017.py` |

## Segunda parte (v2)

### `data/derived/universo_v2.csv` (versionado)

Una fila por película y universo (`country_frame` = `US` o `ES`; 12 coproducciones aparecen en ambos). Columnas: `tconst`, `year`, `cohort`, `genre_main`, `country_frame`, `votes_rank_in_year` (rango de votos de IMDb dentro del año y el universo; no se publican los votos), `in_v1` (ya anotada en la primera parte), `has_synopsis`, `us_only`, `synopsis_wiki` (`en`/`es`).

### `data/derived/etiquetas_v2.csv` (versionado; sin votos, notas ni títulos de IMDb)

Una fila por película y universo con las etiquetas finales v2 (reglas en D-026 y D-027):

| Columna | Descripción |
|---|---|
| `id_v2`, `etapa_v2` | Id cegado y etapa de la etiqueta: `v2_completa` (anotación completa), `v2_modb` (núcleo de la primera parte + módulo B), `v2_es_en` (reanotación con la sinopsis inglesa, D-027) |
| `sinopsis_idioma` | Idioma de la sinopsis anotada |
| núcleo: `final`, `supervivencia`, `objetivo`, `relaciones`, `justicia_narrativa`, `tono_cierre`, `agencia`, `cambio`, `vinculos`, `futuro`, `vision_vida` | Como en la primera parte. `*_fuente`: `acuerdo`, `adjudicado` o `regla_A` (desacuerdo no adjudicado, se toma A) |
| módulo B: `genero_protagonista`, `edad_protagonista`, `momento_vital`, `estado_civil`, `clase_social`, `especulativa`, `epoca_trama`, `humor` | Categorías del manual 2.0 (módulo B). `*_A`, `*_B`: etiquetas de cada anotador; `*_fuente` |
| `tono_general`, `optimismo_personajes` | −2 a +2. Media de A y B si difieren <3; adjudicado si difieren ≥3; vacío si falta uno de los dos (`*_fuente`) |
| `relaciones_centrales_A/B`, `paises_trama_A/B` | Listas separadas por `|` |
| `rel_<relación>` | 0, 0,5 o 1: proporción de anotadores que marcan esa relación como central |
| `reconocida_b` | Algún anotador dijo reconocer la película en el módulo B |
| `final_es_original` | Etiqueta del final con la sinopsis española antes de la reanotación D-027 |
| `clasificable`, `y_feliz`, `y_agridulce`, `y_ambiguo`, `y_tragico` | Indicadores sobre finales clasificables |
| `y_feliz_A`, `y_feliz_B` | Final feliz según cada anotador (sensibilidad) |
| `y_optimistas`, `y_tono_pos` | Optimismo de los personajes > 0; tono general > 0 |
| `tragedia_vitalista` | Final trágico con personajes optimistas |

### `reports/tables/v2/` (versionado)

`por_cohorte.csv` (proporciones y medias por país y cohorte con IC), `por_anio.csv`, `contrastes.csv` (diferencias frente a 1990-1999 con bootstrap), `covariables.csv` (composición del módulo B por cohorte), `subgrupos.csv` (cambio 2010-2024 − 1990-1999 dentro de cada subgrupo, EE. UU.), `final_vs_animo.csv`, `ajustados.csv` (AME logit y MCO), `sensibilidad.csv`, `genero.csv`, `imdb_agregado.csv` y `imdb_modelos.csv` (solo agregados).

### `web/films.json` (versionado)

Una fila por película (título en español de TMDB, título original, año, país, género, final, optimismo, tono, módulo B, relaciones, países, `poster_path` y id de TMDB). No contiene datos de IMDb.

### No versionados

`data/interim/analitico_v2.csv` (contiene votos y notas de IMDb), `tmdb_posters.csv` y `es_nc_en_fallback.csv`.
