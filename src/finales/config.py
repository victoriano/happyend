"""Carga de configuración y rutas del proyecto."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
DERIVED = DATA / "derived"
ANNOT = ROOT / "annotation"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
TABLES = REPORTS / "tables"
PROVENANCE = DATA / "provenance.jsonl"


@lru_cache(maxsize=1)
def load(path: str | Path | None = None) -> dict:
    p = Path(path) if path else ROOT / "config" / "config.yaml"
    with open(p, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def cohort_of(year: int, cohorts: dict | None = None) -> str | None:
    """Devuelve la etiqueta de cohorte para un año, o None si queda fuera."""
    cohorts = cohorts or load()["periodo"]["cohortes"]
    if year is None:
        return None
    for label, (a, b) in cohorts.items():
        if a <= int(year) <= b:
            return label
    return None


def ensure_dirs() -> None:
    for d in (RAW, INTERIM, DERIVED, ANNOT, FIGURES, TABLES):
        d.mkdir(parents=True, exist_ok=True)
