"""Pruebas de integración sobre los resultados versionados (tablas, muestra, etiquetas e informe)."""
import json
import string
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from finales import annotation as an
from finales import report
from finales.config import DERIVED, INTERIM, ROOT, TABLES

HAS_TABLES = (TABLES / "descriptivos_marco_cohorte.csv").exists()
HAS_INTERIM = (INTERIM / "analitico_principal.csv").exists()
needs_tables = pytest.mark.skipif(not HAS_TABLES, reason="ejecuta antes `make analysis`")
needs_interim = pytest.mark.skipif(not HAS_INTERIM, reason="requiere datos intermedios (make all)")


@needs_tables
def test_templates_have_no_unknown_placeholders():
    V = report.values()
    for name in ("informe", "resumen_ejecutivo"):
        tmpl = (ROOT / "docs" / "plantillas" / f"{name}.md").read_text(encoding="utf-8")
        keys = {f for _, f, _, _ in string.Formatter().parse(tmpl) if f}
        assert keys <= set(V), keys - set(V)
        out = report.render(name, V)
        assert "{" not in out and "n/d" not in out


@needs_tables
def test_report_numbers_trace_to_tables():
    V = report.values()
    d = pd.read_csv(TABLES / "descriptivos_marco_cohorte.csv")
    r = d[(d.frame == "popular") & (d.cohort == "1990-1999") & (d.variable == "y_feliz")].iloc[0]
    assert V["pop_feliz_90"] == report.pct(r.estimacion)
    c = pd.read_csv(TABLES / "contrastes_vs_1990s.csv")
    r = c[(c.marco == "popular") & (c.variable == "y_feliz") & (c.comparacion == "2010-2024 − 1990-1999")].iloc[0]
    assert V["pop_d_feliz_rec"] == report.pp(r["diff"])
    rendered = (ROOT / "reports" / "informe.md").read_text(encoding="utf-8")
    assert V["pop_d_feliz_rec_ci"] in rendered


def test_formatters():
    assert report.pct(0.6604) == "66,0 %"
    assert report.pp(-0.0833) == "−8,3 pp" and report.pp(0.012) == "+1,2 pp"
    assert report.num(-0.505, signed=True) == "−0,51" or report.num(-0.505, signed=True) == "−0,50"


@needs_tables
def test_sample_design_consistency():
    s = pd.read_csv(DERIVED / "muestra_principal.csv")
    counts = s.groupby(["frame", "cohort"]).size()
    assert (counts.xs("popular") == 150).all() and (counts.xs("amplio") == 50).all()
    assert (s["design_weight"] > 0).all()
    assert s.groupby(["frame", "cohort", "stratum_pop"])["n_stratum"].nunique().max() == 1
    # peso = N/n
    assert np.allclose(s["design_weight"], s["N_stratum"] / s["n_stratum"])
    # la muestra popular solo contiene películas del universo popular (rango ≤ 50)
    assert (s.loc[s.frame == "popular", "votes_rank_in_year"] <= 50).all()
    # el piloto no se solapa con la principal
    p = pd.read_csv(DERIVED / "muestra_piloto.csv")
    assert not set(p.tconst) & set(s.tconst)
    # cada película muestreada tiene URL de revisión de Wikipedia
    assert s["synopsis_revision_url"].str.startswith("https://en.wikipedia.org/w/index.php?oldid=").all()


@needs_tables
def test_every_sampled_film_has_two_valid_labels():
    lab = ROOT / "annotation" / "labels" / "principal"
    A, ea = an.load_labels(sorted((lab / "A").glob("*.jsonl")), "A")
    B, eb = an.load_labels(sorted((lab / "B").glob("*.jsonl")), "B")
    assert not ea and not eb
    ids = set()
    for f in (ROOT / "annotation" / "batches" / "principal").glob("*.jsonl"):
        ids |= {json.loads(x)["id"] for x in f.read_text(encoding="utf-8").splitlines() if x.strip()}
    assert set(A.id) == ids == set(B.id)
    s = pd.read_csv(DERIVED / "muestra_principal.csv")
    assert len(ids) == s.tconst.nunique()


@needs_tables
def test_all_disagreements_adjudicated():
    for f in sorted((ROOT / "annotation" / "batches" / "principal_adjudicacion").glob("*.jsonl")):
        out = ROOT / "annotation" / "labels" / "principal" / "adjudicacion" / f.name
        assert an.validate_adjudication(out, f) == []


@needs_tables
def test_intervals_contain_estimates_and_are_valid():
    d = pd.read_csv(TABLES / "descriptivos_marco_cohorte.csv").dropna(subset=["ic95_inf"])
    assert (d.ic95_inf <= d.estimacion + 1e-9).all() and (d.estimacion <= d.ic95_sup + 1e-9).all()
    props = d[d.variable != "vision_vida"]
    assert props.ic95_inf.between(0, 1).all() and props.ic95_sup.between(0, 1).all()
    c = pd.read_csv(TABLES / "contrastes_vs_1990s.csv").dropna(subset=["diff_lo"])
    assert (c.diff_lo <= c["diff"] + 1e-9).all() and (c["diff"] <= c.diff_hi + 1e-9).all()


@needs_tables
def test_ending_shares_sum_to_one():
    d = pd.read_csv(TABLES / "descriptivos_marco_cohorte.csv")
    s = d[d.variable.isin(["y_feliz", "y_agridulce", "y_ambiguo", "y_tragico"])].groupby(["frame", "cohort"]).estimacion.sum()
    assert np.allclose(s, 1.0, atol=5e-4)  # tablas redondeadas a 4 decimales


@needs_interim
def test_descriptives_recomputed_from_analytic_dataset():
    df = pd.read_csv(INTERIM / "analitico_principal.csv")
    g = df[(df.frame == "popular") & (df.cohort == "1990-1999") & df.y_feliz.notna()]
    d = pd.read_csv(TABLES / "descriptivos_marco_cohorte.csv")
    r = d[(d.frame == "popular") & (d.cohort == "1990-1999") & (d.variable == "y_feliz")].iloc[0]
    assert np.isclose(np.average(g.y_feliz, weights=g.w_design), r.estimacion)
    assert len(g) == r.n
