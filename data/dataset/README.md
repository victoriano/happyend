# Dataset: *feel good* de películas y series (1980-2026)

Una fila por título: 3.654 películas y 1.972 series estadounidenses y españolas, con las etiquetas finales (doble anotación ciega por modelos de lenguaje y árbitro). Es la misma tabla que usa el explorador de la web.

* [`feelgood_titulos.csv`](feelgood_titulos.csv) (UTF-8, separador coma)
* [`feelgood_titulos.parquet`](feelgood_titulos.parquet)

Se regenera con `python scripts/export_dataset.py` a partir de `web/films.json`.

**No incluye la nota ni los votos de IMDb**, porque sus condiciones no permiten redistribuirlos. Con `tconst` se pueden cruzar con los [datasets de IMDb](https://developer.imdb.com/non-commercial-datasets/) (`title.ratings.tsv.gz`).

## Columnas

| Columna | Descripción |
|---|---|
| `tconst` | Identificador de IMDb |
| `tipo` | `pelicula` o `serie` |
| `titulo`, `otro_titulo` | Título mostrado en la web (en español si TMDB lo tiene) y título alternativo |
| `anio` | Año de estreno (en las series, el de la primera temporada) |
| `anio_en_curso` | `True` para 2026, que no se usa en el análisis |
| `pais_produccion` | `US`, `ES` o `US+ES` (en los dos marcos) |
| `genero` | Género principal agrupado |
| `publico` | `INFANTIL`, `FAMILIAR`, `JUVENIL` o `ADULTO` |
| `feel_good` | Nota *feel good*, 0-10 (vacía si el resumen no permite juzgarla) |
| `utopia` | Sociedad que muestra, de 0 (distopía) a 10 (utopía) |
| `final` | `FELIZ`, `AGRIDULCE`, `AMBIGUO`, `TRAGICO` o `NO_CLASIFICABLE` |
| `tono_cierre` | Emoción del cierre (solo películas) |
| `optimismo_personajes`, `tono_general` | Escalas de −2 a +2 |
| `especulativa` … `humor` | Rasgos de la historia y del protagonista (solo películas) |
| `relaciones`, `paises_trama` | Listas separadas por `\|` (solo películas; `Otro` = país fuera de los 40 más frecuentes) |
| `rango_popularidad_anio` | Puesto por número de votos en IMDb dentro de su año |
| `tmdb_id` | Identificador de TMDB |

Definiciones completas: [`docs/manual_anotacion.md`](../../docs/manual_anotacion.md), [`docs/instrucciones_anotador_v2.md`](../../docs/instrucciones_anotador_v2.md) y [`docs/diccionario_datos.md`](../../docs/diccionario_datos.md).

Resultados exploratorios: las etiquetas las generaron modelos de lenguaje y todavía no tienen validación humana. Los resúmenes de Wikipedia en que se basan son CC BY-SA 4.0.
