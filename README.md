# ¿Eran más optimistas las películas de los noventa?

Proyecto reproducible para contrastar con datos la afirmación de que el cine popular de los noventa era más optimista que el actual y de que el público echa de menos ese optimismo. El análisis no parte de que la afirmación sea cierta: puede apoyarla, matizarla o refutarla.

* **Resumen ejecutivo:** [`reports/resumen_ejecutivo.md`](reports/resumen_ejecutivo.md)
* **Informe completo:** [`reports/informe.md`](reports/informe.md)
* **Manual de anotación (versión 1.0, congelada):** [`docs/manual_anotacion.md`](docs/manual_anotacion.md)
* **Registro de decisiones:** [`docs/registro_decisiones.md`](docs/registro_decisiones.md) · **Diccionario de datos:** [`docs/diccionario_datos.md`](docs/diccionario_datos.md)
* **Diseño de la encuesta (no ejecutada):** [`docs/diseno_encuesta.md`](docs/diseno_encuesta.md)

> **Estado (2026-09-29).** Primera versión exploratoria. 994 películas estadounidenses (1980-2024) anotadas por **dos modelos de lenguaje independientes con adjudicación, sin validación humana todavía** (material preparado en `annotation/validacion_humana/`). La parte sobre la nostalgia del público **no se ha probado**.

## Requisitos

* Python 3.11 o superior, unos 2 GB de disco y conexión a `datasets.imdbws.com`, `www.cs.cmu.edu`, `query.wikidata.org` y `dumps.wikimedia.org`.
* Aceptar las [condiciones de uso no comercial de IMDb](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX). Los datos de IMDb no se redistribuyen en este repositorio.

## Reproducir desde un entorno limpio

```bash
git clone <este repositorio> finales-cine && cd finales-cine
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt && pip install -e .
make all      # descarga (unos 30-40 min por Wikidata), catálogo, cobertura, análisis, gráficos e informe
make test     # pruebas automatizadas
```

`make all` encadena estas etapas:

| Etapa | Comando | Salida |
|---|---|---|
| Descarga | `python -m finales.pipeline ingest` | `data/raw/` (IMDb, CMU), `data/interim/wikidata_us_films.csv`, `data/provenance.jsonl` |
| Catálogo | `python -m finales.pipeline catalog` | `data/interim/catalog.csv`, `reports/tables/exclusiones_resumen.csv` |
| Cobertura del CMU | `python -m finales.pipeline coverage` | `reports/tables/cobertura_cmu.csv` |
| Muestra | `python -m finales.pipeline pilot` / `main` | **Congeladas**: si ya hay muestra y etiquetas, se reutilizan (D-021) |
| Análisis | `python -m finales.analysis piloto`, `python -m finales.power`, `python -m finales.analysis principal` | `reports/tables/*.csv` |
| Gráficos | `python -m finales.figures` | `reports/figures/*.png` |
| Informe | `python -m finales.report` | `reports/informe.md`, `reports/resumen_ejecutivo.md`, `reports/tables/valores_informe.json` |

**Qué se reproduce exactamente.** Las muestras (`data/derived/`), los lotes cegados (`annotation/batches/`) y todas las etiquetas (`annotation/labels/`) están versionados, así que las tablas, los gráficos y el informe se regeneran igual. La excepción es lo que depende de los votos brutos de IMDb del día de la descarga: IMDb actualiza a diario y no guarda instantáneas, así que la sensibilidad «ponderado por votos» puede variar ligeramente.

**Empezar un estudio nuevo** (otra muestra): `python -m finales.pipeline pilot --force` y `main --force`. Esto extrae las sinopsis del volcado de Wikipedia `enwiki-20260901` (descarga el índice, 284 MB, y lee por rangos solo los bloques necesarios) y genera lotes cegados nuevos, que habrá que anotar siguiendo `docs/instrucciones_anotador.md`.

## Estructura

```
config/config.yaml        parámetros (periodo, cohortes, filtros, tamaños, semilla)
src/finales/              código: ingest, clean, sampling, wikidump, blinding, annotation,
                          agreement, stats, analysis, power, figures, report, pipeline
tests/                    pruebas (limpieza, reglas de muestra, cegado, extracción, acuerdo,
                          intervalos, anotación, coherencia de resultados e informe)
data/raw, data/interim    descargas e intermedios (no versionados)
data/derived              muestras con procedencia (versionadas; sin votos ni texto)
annotation/batches        sinopsis cegadas (CC BY-SA 4.0, derivadas de Wikipedia)
annotation/labels         etiquetas A, B y adjudicación (versionadas)
annotation/claves         claves id cegado → tconst (versionadas; nunca se entregan a los anotadores)
annotation/validacion_humana  kit de validación humana (pendiente)
docs/                     manual, instrucciones, decisiones, diccionario, encuesta, plantillas
reports/                  informe, resumen, tablas y figuras generados
scripts/                  scripts de una sola ejecución (documentados)
```

## Fuentes y licencias

* IMDb Non-Commercial Datasets: uso personal y no comercial. *Information courtesy of IMDb (https://www.imdb.com). Used with permission.*
* Wikidata: CC0.
* Wikipedia en inglés (volcado del 1 de septiembre de 2026): CC BY-SA 4.0. La atribución por película es la URL de la revisión en `data/derived/muestra_principal.csv`. Los textos cegados de `annotation/batches/` se distribuyen bajo la misma licencia.
* CMU Movie Summary Corpus (Bamman, O'Connor y Smith, 2013): CC BY-SA; solo se usa para evaluar su cobertura.
* El código de este repositorio no incluye datos de IMDb.

## Cómo se anotó

Cada sinopsis, sin título ni años, la anotaron dos modelos de lenguaje distintos por separado (lotes de 50, orden de cohortes mezclado), siguiendo `docs/instrucciones_anotador.md`. Un tercer proceso adjudicó los desacuerdos siguiendo `docs/instrucciones_adjudicador.md`. Los modelos no tuvieron acceso a la clave `id → película` ni a los metadatos. Personas anotadoras pueden seguir exactamente el mismo procedimiento.
