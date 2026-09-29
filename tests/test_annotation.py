import json

import numpy as np
import pandas as pd
import pytest

from finales import annotation as an


def rec(id_, **kw):
    r = {"id": id_, "final": "FELIZ", "supervivencia": "SOBREVIVE", "objetivo": "LOGRADO",
         "relaciones": "FORTALECIDAS", "justicia_narrativa": "SI", "tono_cierre": "ESPERANZA",
         "agencia": 2, "cambio": 1, "vinculos": 2, "futuro": 1, "describe_final": True,
         "reconocida": False, "confianza": 3, "nota": "x"}
    r.update(kw)
    return r


def write(tmp_path, name, recs):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    return p


def test_validate_rejects_bad_values():
    assert an.validate_record(rec("F1")) == []
    errs = an.validate_record(rec("F1", final="HAPPY", agencia=3, reconocida="no", confianza=5))
    assert len(errs) == 4


def test_load_labels_reports_errors_and_duplicates(tmp_path):
    p = write(tmp_path, "b.jsonl", [rec("F1"), rec("F2", final="X"), rec("F1", final="TRAGICO")])
    df, errs = an.load_labels([p], "A")
    assert list(df["id"]) == ["F1"] and df.loc[0, "final"] == "FELIZ"
    assert any("no permitido" in e for e in errs) and any("duplicados" in e for e in errs)


def test_null_items_become_nan(tmp_path):
    p = write(tmp_path, "b.jsonl", [rec("F1", futuro=None)])
    df, errs = an.load_labels([p], "A")
    assert not errs and np.isnan(df.loc[0, "futuro"])


def test_vision_requires_three_items():
    df = pd.DataFrame({"agencia": [2, 2], "cambio": [0, np.nan], "vinculos": [1, np.nan], "futuro": [np.nan, 1]})
    v = an.vision_score(df)
    assert v[0] == pytest.approx(1.0) and np.isnan(v[1])


def test_disagreements_and_finalize(tmp_path):
    A = pd.DataFrame([rec("F1"), rec("F2", final="AGRIDULCE"), rec("F3", agencia=-2)])
    B = pd.DataFrame([rec("F1"), rec("F2", final="TRAGICO"), rec("F3", agencia=2)])
    for d in (A, B):
        for k in an.ITEMS:
            d[k] = d[k].astype(float)
    pr = an.pair(A, B)
    dis = an.disagreements(pr)
    assert set(dis["id"]) == {"F2", "F3"}
    adj = pd.DataFrame([{"id": "F2", "final": "AGRIDULCE"}, {"id": "F3", "agencia": 1}])
    fin = an.finalize(pr, adj).set_index("id")
    assert fin.loc["F1", "final"] == "FELIZ" and fin.loc["F1", "final_fuente"] == "acuerdo"
    assert fin.loc["F2", "final"] == "AGRIDULCE" and fin.loc["F2", "final_fuente"] == "adjudicado"
    assert fin.loc["F3", "agencia"] == 1.0                       # gap >= 3 -> adjudicador
    assert fin.loc["F1", "cambio"] == 1.0                        # media de A y B
    assert fin.loc["F1", "vision_vida"] == pytest.approx(1.5)


def test_unresolved_when_no_adjudication():
    A = pd.DataFrame([rec("F1", final="FELIZ")])
    B = pd.DataFrame([rec("F1", final="TRAGICO")])
    fin = an.finalize(an.pair(A, B), None)
    assert fin.loc[0, "final"] is None and fin.loc[0, "final_fuente"] == "sin_resolver"
