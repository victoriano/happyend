# Flujo completo: make all   |   Pruebas: make test
PY ?= python3

.PHONY: all ingest catalog coverage sample analysis figures report test clean-derived

all: ingest catalog coverage sample analysis figures report

ingest:        ## Descarga IMDb, CMU y Wikidata (unos 30-40 min por las consultas SPARQL)
	$(PY) -m finales.pipeline ingest

catalog:       ## Catálogo elegible y exclusiones
	$(PY) -m finales.pipeline catalog

coverage:      ## Cobertura del CMU Movie Summary Corpus
	$(PY) -m finales.pipeline coverage

sample:        ## Muestras piloto y principal (no hace nada si ya están congeladas y anotadas)
	$(PY) -m finales.pipeline pilot
	$(PY) -m finales.pipeline main

analysis:      ## Acuerdo, descriptivos, contrastes, modelos, sensibilidad y potencia
	$(PY) -m finales.analysis piloto
	$(PY) -m finales.power
	$(PY) -m finales.analysis principal

figures:
	$(PY) -m finales.figures

report:        ## Rellena las plantillas de docs/plantillas con las tablas
	$(PY) -m finales.report

test:
	$(PY) -m pytest -q
