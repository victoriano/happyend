"""Valores de la tercera parte del informe (D-035, D-036): feel good, utopía y público."""
from __future__ import annotations

import json

from .config import ROOT

TEMPLATES = ROOT / "docs" / "plantillas"
V2 = ROOT / "reports" / "tables" / "v2"


def _p(x, d=0):
    return f"{x * 100:.{d}f} %".replace(".", ",")


def _f(x, d=1):
    return f"{x:.{d}f}".replace(".", ",").replace("-", "−")


def _s(x, d=2):
    return ("+" if x >= 0 else "−") + f"{abs(x):.{d}f}".replace(".", ",")


def _ci(lo, hi, d=2):
    return f"(IC 95 %: {_s(lo, d)} a {_s(hi, d)})"


def values_v3() -> dict:
    fg = json.loads((V2 / "historia_web.json").read_text(encoding="utf-8"))["fg"]
    web = json.loads((ROOT / "web" / "data.json").read_text(encoding="utf-8"))["v2"]
    a = web["acuerdo_censo"]
    U, E = fg["cohortes"]["US"], fg["cohortes"]["ES"]
    dU, dE = fg["diff"]["US"], fg["diff"]["ES"]
    sU = {r[0]: r[1:] for r in fg["sens"]["US"]}
    sE = {r[0]: r[1:] for r in fg["sens"]["ES"]}
    pub = fg["publico"]["US"]
    fam = lambda c: pub["por_cohorte"][c].get("INFANTIL", 0) + pub["por_cohorte"][c].get("FAMILIAR", 0)
    pf = pub["fg"]
    fgfam = (pf["INFANTIL"][0] * pf["INFANTIL"][3] + pf["FAMILIAR"][0] * pf["FAMILIAR"][3]) / (pf["INFANTIL"][3] + pf["FAMILIAR"][3])
    pfin = fg["por_final"]
    tot = lambda f: (pfin["US"][f][1] * pfin["US"][f][0] + pfin["ES"][f][1] * pfin["ES"][f][0]) / (pfin["US"][f][0] + pfin["ES"][f][0])
    im = fg["imdb"]["US"]["averageRating~feel_good"]
    wm = lambda k, cf: sum(x[0] * x[3] for x in fg["cohortes"][cf][k] if x[0] is not None) / sum(x[3] for x in fg["cohortes"][cf][k] if x[0] is not None)
    V = {
        "v3_es_sin_fg": _p(web["sin_fg"]["ES"]), "v3_n_cde": f"{a['n_cde']:,}".replace(",", "."),
        "v3_a_fg": _f(a["alfa_feel_good"], 2), "v3_d2_fg": _p(a["dentro2_feel_good"]), "v3_a_ut": _f(a["alfa_utopia"], 2),
        "v3_k_pub": _f(a["kappa_publico"], 2), "v3_adj_fg": a["n_adj_feel_good"], "v3_adj_ut": a["n_adj_utopia"],
        **{f"v3_us_{k}": _f(U["feel_good"][i][0]) for i, k in enumerate(["80", "90", "00", "10", "20"])},
        "v3_us_d": _s(dU["feel_good"][0]), "v3_us_d_ci": _ci(*dU["feel_good"][1:]),
        "v3_us_d20": _s(dU["por_cohorte"]["2020-2025"]["feel_good"][0]),
        "v3_us_d20_ci": _ci(*dU["por_cohorte"]["2020-2025"]["feel_good"][1:]),
        "v3_us_fg7_90": _p(U["y_fg7"][1][0]), "v3_us_fg7_20": _p(U["y_fg7"][4][0]),
        "v3_us_adj": _s(sU["Ajustado por género y popularidad"][0]), "v3_us_adj_ci": _ci(*sU["Ajustado por género y popularidad"][1:]),
        "v3_us_nofam": _s(sU["Sin películas infantiles y familiares"][0]),
        "v3_us_nofam_ci": _ci(*sU["Sin películas infantiles y familiares"][1:]),
        "v3_us_w": _s(sU["Pesando más las más votadas"][0]), "v3_us_w_ci": _ci(*sU["Pesando más las más votadas"][1:]),
        "v3_us_A": _s(sU["Solo el anotador A"][0]), "v3_us_B": _s(sU["Solo el anotador B"][0]),
        "v3_corr": _f(fg["cruce"]["US"]["corr"], 2), "v3_fg_feliz": _f(tot("FELIZ")), "v3_fg_tragico": _f(tot("TRAGICO")),
        "v3_us_ut": _f(wm("utopia", "US")), "v3_us_ut_d20": _s(dU["por_cohorte"]["2020-2025"]["utopia"][0]),
        "v3_us_ut_d20_ci": _ci(*dU["por_cohorte"]["2020-2025"]["utopia"][1:]),
        "v3_es_ut_90": _f(fg["periodos"]["ES"]["utopia"]["1990-1999"][0]), "v3_es_ut_rec": _f(fg["periodos"]["ES"]["utopia"]["2010-2025"][0]),
        "v3_fg_fam": _f(fgfam), "v3_fg_adulto": _f(pf["ADULTO"][0]), "v3_fam_90": _p(fam("1990-1999")), "v3_fam_20": _p(fam("2020-2025")),
        "v3_es_90": _f(fg["periodos"]["ES"]["feel_good"]["1990-1999"][0]), "v3_es_rec": _f(fg["periodos"]["ES"]["feel_good"]["2010-2025"][0]),
        "v3_es_d": _s(dE["feel_good"][0]), "v3_es_d_ci": _ci(*dE["feel_good"][1:]),
        "v3_es_wiki": _s(sE["Solo sinopsis de Wikipedia"][0]), "v3_es_wiki_ci": _ci(*sE["Solo sinopsis de Wikipedia"][1:]),
        "v3_imdb_fg": _s(im[0], 3), "v3_imdb_fg_ci": _ci(im[1], im[2], 3),
        "v3_es_m": _f(wm("feel_good", "ES")), "v3_us_m": _f(wm("feel_good", "US")),
    }
    return V


def main():
    V = values_v3()
    return ((TEMPLATES / "informe_v3.md").read_text(encoding="utf-8").format_map(V),
            (TEMPLATES / "resumen_v3.md").read_text(encoding="utf-8").format_map(V), V)
