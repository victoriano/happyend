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

## Ficheros intermedios (no versionados; se regeneran)

| Fichero | Contenido |
|---|---|
| `data/interim/catalog.csv` | Catálogo elegible con campos de IMDb (votos, puntuación, géneros), Wikidata y popularidad |
| `data/interim/exclusions.csv` | `tconst`, año, cohorte y motivo de exclusión |
| `data/interim/wikidata_us_films.csv` | Resultado de las consultas SPARQL (ítem, tconst, artículo, país, fecha) |
| `data/interim/synopses/{tconst}.json` | Sección argumental extraída, revisión, id de página y estado |
| `data/interim/keys/*_key.csv` | Correspondencia `id` cegado → `tconst`, lote y truncado (**no se entrega a los anotadores**) |
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
