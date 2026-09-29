"""Genera web/data.json para la web divulgativa (happyend.victoriano.me).

Solo agregados de reports/tables/ y, por película del marco popular, título (de Wikipedia), año,
cohorte, género principal y etiquetas propias. No incluye votos ni puntuaciones de IMDb.
"""
from __future__ import annotations

import json
import re

import pandas as pd

from . import annotation as an
from .config import DERIVED, INTERIM, ROOT, TABLES

COH = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]
FIN = ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO", "NO_CLASIFICABLE"]
TONE = ["ESPERANZA", "ALIVIO", "CONEXION", "RESIGNACION", "DESESPERANZA", "NO_CLARO"]


def clean_title(t: str) -> str:
    return re.sub(r"\s*\([^)]*(film|movie|película)[^)]*\)\s*$", "", t or "").strip()


def r4(x):
    return None if pd.isna(x) else round(float(x), 4)


def build() -> dict:
    df = pd.read_csv(INTERIM / "analitico_principal.csv")
    titles = {}
    for f in (INTERIM / "synopses").glob("*.json"):
        j = json.loads(f.read_text(encoding="utf-8"))
        titles[j["tconst"]] = clean_title(j.get("title"))
    pop = df[df.frame == "popular"].copy()
    genres = sorted(pop.genre_main.unique())
    films = []
    for r in pop.sort_values(["cohort", "votes_rank_in_year", "year"]).itertuples():
        films.append([titles.get(r.tconst, r.tconst), int(r.year), COH.index(r.cohort), genres.index(r.genre_main),
                      FIN.index(r.final)])

    t = lambda n: pd.read_csv(TABLES / n)
    d = t("descriptivos_marco_cohorte.csv")
    agg = {}
    for fr in ("popular", "amplio"):
        agg[fr] = {}
        for var in ["y_feliz", "y_agridulce", "y_ambiguo", "y_tragico", "y_tono_positivo", "vision_vida",
                    "y_sobrevive", "y_objetivo", "y_justicia"]:
            sub = d[(d.frame == fr) & (d.variable == var)].set_index("cohort").reindex(COH)
            agg[fr][var] = [[r4(a), r4(b), r4(c), int(n)] for a, b, c, n in
                            zip(sub.estimacion, sub.ic95_inf, sub.ic95_sup, sub.n)]
    cs = t("contrastes_vs_1990s.csv")
    contr = {f"{r.marco}|{r.variable}|{r.comparacion}": [r4(r["diff"]), r4(r.diff_lo), r4(r.diff_hi)]
             for _, r in cs.iterrows()}
    sn = t("sensibilidad.csv")
    sens = [[r.marco, r.especificacion, r.variable, r4(r["diff"]), r4(r.diff_lo), r4(r.diff_hi), int(r.n0), int(r.n1)]
            for _, r in sn.iterrows() if r.n0 >= 20 and r.n1 >= 20]
    g = t("genero_contrastes.csv")
    gen = [[r.genero, r.marco, int(r.n_1990s), int(r.n_2010_2024), r4(r.feliz_1990s), r4(r.feliz_2010_2024),
            r4(r.dif_pp / 100), r4(r.dif_ic95_inf_pp / 100), r4(r.dif_ic95_sup_pp / 100)] for _, r in g.iterrows()]
    comp = t("composicion_generos.csv").set_index(["frame", "periodo"])
    compo = {f"{a}|{b}": {k: r4(v) for k, v in row.items()} for (a, b), row in comp.iterrows()}
    fo = t("comparacion_follows_accion.csv")
    follows = [[r.marco, r.grupo, int(r.n), r4(r.feliz), r4(r.ic95_inf), r4(r.ic95_sup)] for _, r in fo.iterrows()]
    ea = t("efectos_ajustados.csv")
    adj = {f"{r.marco}|{r.variable}": [r4(r.efecto_ajustado), r4(r.ic95_inf), r4(r.ic95_sup)] for _, r in ea.iterrows()}
    ac = t("acuerdo_principal.csv").set_index("variable")
    rec = t("reconocimiento_por_marco.csv")
    agreement = {"kappa_final": r4(ac.loc["final", "kappa_cohen"]), "acuerdo_final": r4(ac.loc["final", "acuerdo_pct"]),
                 "kappa_tono": r4(ac.loc["tono_cierre", "kappa_cohen"]),
                 "alfa_vision": r4(ac.loc["vision_vida (media ítems)", "alfa_krippendorff"]),
                 "rec_popular": r4(rec[rec.frame == "popular"].reconocida_alguno.mean()),
                 "rec_amplio": r4((rec[rec.frame == "amplio"].reconocida_alguno * rec[rec.frame == "amplio"].n).sum()
                                  / rec[rec.frame == "amplio"].n.sum())}
    adjs = t("adjudicacion_resumen.csv").set_index("campo")
    agreement["adj_A_final"] = r4(adjs.loc["final", "elige_A"])
    cat = t("catalogo_por_cohorte.csv")
    meta = {"n_films": int(df.tconst.nunique()), "catalogo": int(cat.catalogo_elegible.sum()),
            "cmu": {r.cohort: r4(r.cobertura_cmu) for r in t("cobertura_cmu.csv").itertuples()},
            "mde_pop": t("potencia_piloto.csv").iloc[6]["diferencia_minima"],
            "genres": genres, "cohorts": COH, "finals": FIN, "tones": TONE,
            "films_cols": ["titulo", "anio", "cohorte", "genero", "final"]}
    return {"meta": meta, "films": films, "agg": agg, "contrastes": contr, "ajustados": adj, "sensibilidad": sens,
            "generos": gen, "composicion": compo, "follows": follows, "acuerdo": agreement}


def main() -> None:
    out = ROOT / "web" / "data.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(build(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(out, out.stat().st_size)


if __name__ == "__main__":
    main()
