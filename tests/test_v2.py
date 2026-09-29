"""Pruebas de la segunda parte (v2): validación del módulo B, reglas de etiqueta final y datos de la web."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from finales import annotation as an
from finales import v2
from finales.config import ROOT

REC_B = {"id": "G1", "genero_protagonista": "MUJER", "edad_protagonista": "JOVEN", "momento_vital": "JUVENTUD",
         "estado_civil": "SOLTERO", "clase_social": "MEDIA", "relaciones_centrales": ["ROMANCE", "AMISTAD"],
         "especulativa": "NO", "epoca_trama": "DE_1900_A_1945", "paises_trama": ["Reino Unido"], "humor": "ALGO",
         "tono_general": 1, "optimismo_personajes": 2, "reconocida": True, "confianza_b": 3}


def test_validate_b_ok():
    assert an.validate_record_b(REC_B, full=False) == []


@pytest.mark.parametrize("k,v", [("clase_social", "RICA"), ("relaciones_centrales", []),
                                 ("relaciones_centrales", ["A", "B", "C", "D"]), ("paises_trama", "España"),
                                 ("optimismo_personajes", 3), ("confianza_b", 0)])
def test_validate_b_errors(k, v):
    assert an.validate_record_b({**REC_B, k: v}, full=False)


def test_item_rules():
    adj = pd.DataFrame({"optimismo_personajes": [1.0]}, index=["X"])
    assert v2._item(1, 2, adj, "Y", "optimismo_personajes") == (1.5, "media")
    assert v2._item(-1, 2, adj, "X", "optimismo_personajes") == (1.0, "adjudicado")
    val, src = v2._item(np.nan, 2, adj, "X", "optimismo_personajes")
    assert np.isnan(val) and src == "falta_alguno"


def test_blind_id_families_differ():
    assert v2.blind_id_v2("tt0120338", 1)[0] == "G" and v2.blind_id_esen("tt0120338", 1)[0] == "H"
    assert v2.blind_id_v2("tt0120338", 1)[1:] != v2.blind_id_esen("tt0120338", 1)[1:]


def _ids(p):
    return [json.loads(l)["id"] for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]


@pytest.mark.parametrize("stage", ["v2_completa", "v2_modb", "v2_es_en"])
def test_labels_aligned_with_batches(stage):
    bdir = ROOT / "annotation" / "batches" / stage
    if not bdir.exists():
        pytest.skip("sin lotes")
    for b in sorted(bdir.glob("*.jsonl")):
        for a in "AB":
            assert _ids(ROOT / "annotation" / "labels" / stage / a / b.name) == _ids(b), (stage, a, b.name)


def test_web_has_no_imdb_or_key():
    web = ROOT / "web"
    if not (web / "films.json").exists():
        pytest.skip("web no generada")
    f = json.loads((web / "films.json").read_text(encoding="utf-8"))
    assert not {"numVotes", "averageRating", "votos", "nota"} & set(f["cols"])
    assert len(f["films"]) > 2500
    titanic = [r for r in f["films"] if r[0] == "Titanic" and r[2] == 1997]
    assert titanic and titanic[0][f["cols"].index("poster")]
    blob = "".join(p.read_text(encoding="utf-8") for p in web.glob("*.*") if p.suffix in (".html", ".json"))
    assert "api_key" not in blob and "api.themoviedb.org" not in blob


def test_derived_labels_have_no_imdb():
    p = ROOT / "data" / "derived" / "etiquetas_v2.csv"
    if not p.exists():
        pytest.skip("sin etiquetas")
    cols = pd.read_csv(p, nrows=1).columns
    assert "numVotes" not in cols and "averageRating" not in cols
