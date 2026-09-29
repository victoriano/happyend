"""Valores y tablas de la segunda parte del informe (v2). Todas las cifras proceden de reports/tables/v2/."""
from __future__ import annotations

import pandas as pd

from .config import INTERIM, ROOT, TABLES
from .report import ci_pct, ci_pp, num, pct, pp

V2 = TABLES / "v2"
COHS = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]
K = {"1980-1989": "80", "1990-1999": "90", "2000-2009": "00", "2010-2019": "10", "2020-2024": "20"}
LAB = {"CIENCIA_FICCION": "ciencia ficción", "CRISIS_VITAL": "protagonista en crisis vital", "MUJER": "protagonista mujer",
       "EN_PAREJA": "protagonista en pareja", "TRABAJADORA": "clase trabajadora", "NO": "historias no especulativas",
       "Contemporánea": "historias contemporáneas"}


def _n(x: int) -> str:
    return f"{int(x):,}".replace(",", ".")


def values_v2() -> dict:
    V: dict[str, str] = {}
    t = lambda n: pd.read_csv(V2 / n)
    d = pd.read_csv(INTERIM / "analitico_v2.csv")
    V["v2_n_us"], V["v2_n_es"] = _n((d.country_frame == "US").sum()), _n((d.country_frame == "ES").sum())
    V["v2_n_total"] = _n(d.tconst.nunique())
    V["v2_n_dup"] = str(int(d.tconst.duplicated().sum()))
    V["v2_n_completa"] = _n((d.etapa_v2 == "v2_completa").sum() + (d.etapa_v2 == "v2_es_en").sum())
    V["v2_n_modb"] = _n(d[d.etapa_v2 == "v2_modb"].tconst.nunique())
    V["v2_n_esen"] = str(int(d[d.etapa_v2 == "v2_es_en"].tconst.nunique()))
    u = d.drop_duplicates("tconst")
    V["v2_n_adj"] = str(int(((u.final_fuente == "adjudicado") & (u.etapa_v2 != "v2_modb")).sum()))
    ac = pd.read_csv(TABLES / "acuerdo_v2_completa.csv").set_index("variable")
    am = pd.read_csv(TABLES / "acuerdo_v2_modb.csv").set_index("variable")
    for v in ["final", "tono_cierre", "momento_vital", "clase_social", "edad_protagonista", "estado_civil", "especulativa",
              "epoca_trama", "humor", "genero_protagonista", "justicia_narrativa"]:
        V[f"v2_k_{v}"] = num(ac.loc[v, "kappa"])
    for v in ["tono_general", "optimismo_personajes"]:
        V[f"v2_a_{v}"] = num(ac.loc[v, "alfa_intervalo"])
        V[f"v2_am_{v}"] = num(am.loc[v, "alfa_intervalo"])
    for v in ["relaciones_centrales", "paises_trama"]:
        V[f"v2_j_{v}"] = num(ac.loc[v, "jaccard"])
    V["v2_km_min"] = num(am.kappa.min())
    V["v2_km_max"] = num(am.kappa.max())
    V["v2_rec_us"] = pct(d[d.country_frame == "US"].reconocida.mean(), 1)
    V["v2_rec_es"] = pct(d[d.country_frame == "ES"].reconocida.mean(), 0)
    es = d[d.country_frame == "ES"]
    V["v2_es_nc"] = pct((~es.clasificable).mean(), 0)
    orig = es.final.where(es.final_es_original.isna(), es.final_es_original)
    V["v2_es_nc_antes"] = pct((orig == "NO_CLASIFICABLE").mean(), 0)
    V["v2_es_wiki_es"] = str(int((es.sinopsis_idioma == "es").sum()))

    pc = t("por_cohorte.csv").set_index(["country_frame", "cohort"])
    for cf in ("US", "ES"):
        for c in COHS:
            r = pc.loc[(cf, c)]
            p = f"v2_{cf.lower()}_{K[c]}"
            V[p + "_feliz"] = pct(r.feliz)
            V[p + "_feliz_ci"] = ci_pct(r.feliz_lo, r.feliz_hi)
            V[p + "_opt"] = num(r.optimismo, 2, True)
            V[p + "_tono"] = num(r.tono, 2, True)
            V[p + "_nc"] = pct(r.pct_no_clasificable, 0)
    rows = []
    for cf, lab in (("US", "EE. UU."), ("ES", "España")):
        for c in COHS:
            r = pc.loc[(cf, c)]
            rows.append(f"| {lab} | {c} | {int(r.n)} | {pct(r.pct_no_clasificable, 0)} | {pct(r.feliz)} {ci_pct(r.feliz_lo, r.feliz_hi)} "
                        f"| {pct(r.agridulce)} | {pct(r.ambiguo)} | {pct(r.tragico)} | {num(r.optimismo, 2, True)} "
                        f"| {num(r.tono, 2, True)} | {pct(r.optimistas_en_no_felices, 0)} |")
    V["v2_tabla_cohortes"] = "\n".join(
        ["| País | Cohorte | n | No clasif. | Feliz [IC 95 %] | Agridulce | Ambiguo | Trágico | Optimismo personajes | Tono general | Personajes optimistas en finales no felices |",
         "|---|---|---|---|---|---|---|---|---|---|---|"] + rows)

    cs = t("contrastes.csv").set_index(["country_frame", "cohorte", "variable"])
    for cf in ("US", "ES"):
        for c, k in (("2010-2024", "rec"), ("2010-2019", "10"), ("2020-2024", "20"), ("1980-1989", "80"), ("2000-2009", "00")):
            for v in ("feliz", "tragico", "optimismo", "tono", "pct_optimistas", "no_feliz_optimista", "vision"):
                r = cs.loc[(cf, c, v)]
                p = f"v2_{cf.lower()}_d{k}_{v}"
                if v in ("optimismo", "tono", "vision"):
                    V[p] = num(r.diferencia, 2, True)
                    V[p + "_ci"] = f"[{num(r.lo, 2, True)}; {num(r.hi, 2, True)}]"
                else:
                    V[p] = pp(r.diferencia)
                    V[p + "_ci"] = ci_pp(r.lo, r.hi)
    for cf in ("US", "ES"):
        g = d[(d.country_frame == cf) & d.cohort.isin(["2010-2019", "2020-2024"])]
        V[f"v2_{cf.lower()}_rec_feliz"] = pct(g.y_feliz.mean())
    V["v2_es_tono_all"] = num(es.tono_general.mean(), 2, True)
    V["v2_us_tono_all"] = num(d[d.country_frame == "US"].tono_general.mean(), 2, True)

    aj = t("ajustados.csv").set_index(["modelo", "resultado", "cohorte"])
    for m, mk in (("genero+popularidad", "b"), ("+protagonista y trama", "x")):
        for c in ("2000-2009", "2010-2019", "2020-2024"):
            r = aj.loc[(m, "feliz (AME, pp)", c)]
            V[f"v2_adj_{mk}_{K[c]}"] = pp(r.estimacion)
            o = aj.loc[(m, "optimismo personajes (puntos)", c)]
            V[f"v2_adjo_{mk}_{K[c]}"] = num(o.estimacion, 2, True)
            V[f"v2_adjo_{mk}_{K[c]}_ci"] = f"[{num(o.coef_lo, 2, True)}; {num(o.coef_hi, 2, True)}]"
    fm = t("final_vs_animo.csv").set_index(["country_frame", "final"])
    for f in ("FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"):
        V[f"v2_opt_en_{f.lower()}"] = pct(fm.loc[("US", f), "pct_optimistas"], 0)
        V[f"v2_optm_en_{f.lower()}"] = num(fm.loc[("US", f), "optimismo"], 2, True)
    V["v2_frac_trag_opt"] = f"1 de cada {round(1 / fm.loc[('US', 'TRAGICO'), 'pct_optimistas'])}"
    c = d[d.clasificable]
    V["v2_tragvit_pct"] = pct(c.tragedia_vitalista.mean(), 1)
    ti = d[d.tconst == "tt0120338"].iloc[0]
    V["v2_titanic_final"] = ti.final.lower()
    V["v2_titanic_opt"] = num(ti.optimismo_personajes, 0, True)

    sg = t("subgrupos.csv")
    s = sg[(sg.medida == "feliz") & ((sg.lo > 0) | (sg.hi < 0)) & (sg.valor != "NO_CLARO")].sort_values("diferencia")
    V["v2_sub_caidas"] = "; ".join(f"{LAB.get(r.valor, str(r.valor).lower())} ({pp(r.diferencia)}, IC {ci_pp(r.lo, r.hi)}, n = {r.n_1990s}/{r.n_2010_24})"
                                   for r in s.itertuples())
    so = sg[(sg.medida == "optimismo") & (sg.variable == "genre_main") & (sg.valor == "Comedia")].iloc[0]
    V["v2_sub_comedia_opt"] = f"{num(so.diferencia, 2, True)} [{num(so.lo, 2, True)}; {num(so.hi, 2, True)}]"
    V["v2_sub_n_tests"] = str(len(sg[sg.medida == "feliz"]))
    V["v2_sub_n_sig"] = str(len(s))

    im = t("imdb_modelos.csv").set_index(["country_frame", "resultado", "predictor"])
    for cf in ("US", "ES"):
        for y, yk in (("averageRating", "nota"), ("logv", "votos")):
            for x, xk in (("y_feliz", "feliz"), ("optimismo_personajes", "opt"), ("tono_general", "tono")):
                r = im.loc[(cf, y, x)]
                V[f"v2_imdb_{cf.lower()}_{yk}_{xk}"] = num(r.coef, 2, True)
                V[f"v2_imdb_{cf.lower()}_{yk}_{xk}_ci"] = f"[{num(r.lo, 2, True)}; {num(r.hi, 2, True)}]"

    se = t("sensibilidad.csv")
    rows = []
    for r in se.dropna(subset=["diferencia_2010_24_vs_1990s"]).itertuples():
        f = (lambda x: num(x, 2, True)) if "optimismo" in r.medida else pp
        rows.append(f"| {r.analisis} | {'EE. UU.' if r.country_frame == 'US' else 'España'} | {f(r.diferencia_2010_24_vs_1990s)} "
                    f"| [{f(r.lo)}; {f(r.hi)}] | {r.n} |")
    V["v2_tabla_sens"] = "\n".join(["| Análisis | País | 2010-2024 − 1990-1999 | IC 95 % | n películas |", "|---|---|---|---|---|"] + rows)
    return V


def main() -> str:
    from .report import TEMPLATES
    V = values_v2()
    return (TEMPLATES / "informe_v2.md").read_text(encoding="utf-8").format_map(V), \
        (TEMPLATES / "resumen_v2.md").read_text(encoding="utf-8").format_map(V), V
