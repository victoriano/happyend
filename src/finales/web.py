"""Genera web/data.json para la web divulgativa (happyend.victoriano.me).

Solo agregados de reports/tables/ y, por película del marco popular, título (de Wikipedia), año,
cohorte, género principal y etiquetas propias. No incluye votos ni puntuaciones de IMDb.
"""
from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from . import annotation as an
from .config import DERIVED, INTERIM, ROOT, TABLES
from .annotation import KEY_DIR as ANNOT_KEYS

COH = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2025"]
FIN = ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO", "NO_CLASIFICABLE"]
TONE = ["ESPERANZA", "ALIVIO", "CONEXION", "RESIGNACION", "DESESPERANZA", "NO_CLARO"]


def clean_title(t: str) -> str:
    return re.sub(r"\s*\([^)]*(film|movie|película)[^)]*\)\s*$", "", t or "").strip()


def r4(x):
    return None if pd.isna(x) or not np.isfinite(float(x)) else round(float(x), 4)


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
    main_v2()
    main_fichas()




# ------------------------------------------------------------------ v2: censo, España y explorador
V2 = ROOT / "reports" / "tables" / "v2"
EXPL = {
    "especulativa": ["NO", "CIENCIA_FICCION", "FANTASIA", "SOBRENATURAL", "SUPERHEROES"],
    "clase_social": ["BAJA_MARGINAL", "TRABAJADORA", "MEDIA", "ALTA_ELITE", "MIXTA", "NO_CLARO"],
    "momento_vital": ["INFANCIA", "ADOLESCENCIA", "JUVENTUD", "CRIANZA", "MADUREZ", "CRISIS_VITAL", "VEJEZ", "NO_CLARO"],
    "epoca_trama": ["ANTES_1500", "DE_1500_A_1899", "DE_1900_A_1945", "DE_1946_A_1979", "DE_1980_EN_ADELANTE",
                    "FUTURO", "MUNDO_FICTICIO", "VARIAS", "NO_CLARO"],
    "genero_protagonista": ["HOMBRE", "MUJER", "MIXTO", "NO_HUMANO", "NO_CLARO"],
    "estado_civil": ["SOLTERO", "EN_PAREJA", "CASADO", "SEPARADO_DIVORCIADO", "VIUDO", "NO_CLARO"],
    "edad_protagonista": ["NINO", "ADOLESCENTE", "JOVEN", "ADULTO", "MADURO", "MAYOR", "MIXTO", "NO_CLARO"],
    "humor": ["NINGUNO", "ALGO", "CENTRAL"],
}


def _num(x, d=2):
    return None if pd.isna(x) else round(float(x), d)


PUB = ["INFANTIL", "FAMILIAR", "JUVENIL", "ADULTO"]


def build_films_v2() -> dict:
    """Una fila por película del universo v2 (sin votos ni notas de IMDb)."""
    d = pd.read_csv(INTERIM / "analitico_v2.csv")
    tm = pd.read_csv(INTERIM / "tmdb_posters.csv").drop_duplicates("tconst").set_index("tconst")
    genres = sorted(d.genre_main.dropna().unique())
    paises = d.paises_trama_A.fillna("").str.split("|").explode()
    top_paises = [p for p in paises.value_counts().index if p][:40]
    rows = []
    d = d[d.final.notna()]  # sin sinopsis utilizable: fuera del explorador
    for tc, g in d.groupby("tconst", sort=False):
        r = g.iloc[0]
        cf = "+".join(sorted(g.country_frame.unique(), reverse=True))  # "US", "ES" o "US+ES"
        t_es = tm.titulo_es.get(tc) if tc in tm.index else None
        title = t_es if isinstance(t_es, str) and t_es else r.primaryTitle
        orig = r.primaryTitle if r.primaryTitle != title else (r.originalTitle if r.originalTitle != title else "")
        rels = [i for i, rel in enumerate(an.RELACIONES) if r[f"rel_{rel.lower()}"] >= 0.5]
        ps = [top_paises.index(p) if p in top_paises else -1 for p in str(r.paises_trama_A).split("|") if p]
        rows.append([
            title, orig or "", int(r.year), ["US", "ES", "US+ES"].index(cf), genres.index(r.genre_main),
            FIN.index(r.final), _num(r.optimismo_personajes, 1), _num(r.tono_general, 1),
            *[EXPL[k].index(r[k]) for k in EXPL], rels, ps,
            (tm.poster_path.get(tc) if tc in tm.index and isinstance(tm.poster_path.get(tc), str) else ""),
            int(tm.tmdb_id.get(tc)) if tc in tm.index and pd.notna(tm.tmdb_id.get(tc)) else 0,
            TONE.index(r.tono_cierre) if r.tono_cierre in TONE else 5, tc,
            int(r.numVotes) if pd.notna(r.numVotes) else None, _num(r.averageRating, 1),
            int(r.votes_rank_in_year), bool(getattr(r, "anio_en_curso", False) == True),
            _num(r.feel_good, 1), _num(r.utopia, 1), PUB.index(r.publico) if r.publico in PUB else -1,
        ])
    rows.sort(key=lambda x: (x[2], x[0]))
    cols = ["titulo", "original", "anio", "pais", "genero", "final", "optimismo", "tono"] + list(EXPL) + \
           ["relaciones", "paises_trama", "poster", "tmdb", "tono_cierre", "tconst", "imdb_votos", "imdb_nota",
            "rango_votos_anio", "anio_en_curso", "feel_good", "utopia", "publico"]
    return {"cols": cols, "publicos": PUB, "genres": genres, "finals": FIN, "tones": TONE, "cats": EXPL,
            "relaciones": an.RELACIONES, "paises": top_paises, "films": rows}


def build_v2() -> dict:
    t = lambda n: pd.read_csv(V2 / n)
    pc = t("por_cohorte.csv")
    coh = {cf: {c: [r4(x) for x in pc[pc.country_frame == cf].set_index("cohort").reindex(COH)[c]]
                for c in pc.columns if c not in ("country_frame", "cohort")} for cf in ("US", "ES")}
    py = t("por_anio.csv")
    year = {cf: [[int(r.year), int(r.n), r4(r.feliz), r4(r.optimismo), r4(r.tono)]
                 for r in py[py.country_frame == cf].itertuples()] for cf in ("US", "ES")}
    cs = t("contrastes.csv")
    contr = {f"{r.country_frame}|{r.cohorte}|{r.variable}": [r4(r.diferencia), r4(r.lo), r4(r.hi)]
             for r in cs.itertuples()}
    sg = t("subgrupos.csv")
    sub = [[r.variable, str(r.valor), r.medida, int(r.n_1990s), int(r.n_2010_24), r4(r.nivel_1990s),
            r4(r.nivel_2010_24), r4(r.diferencia), r4(r.lo), r4(r.hi)] for r in sg.itertuples()]
    fm = t("final_vs_animo.csv")
    fvm = [[r.country_frame, r.final, int(r.n), r4(r.optimismo), r4(r.pct_optimistas), r4(r.tono)] for r in fm.itertuples()]
    d_all = pd.read_csv(INTERIM / "analitico_v2.csv")
    d = d_all[d_all.anio_en_curso != True]
    c = d[d.clasificable & d.optimismo_personajes.notna()]
    mat = pd.crosstab(c.final, c.optimismo_personajes.round().clip(-2, 2)).reindex(FIN[:4]).fillna(0).astype(int)
    im = t("imdb_modelos.csv")
    imdb = {f"{r.country_frame}|{r.resultado}|{r.predictor}": [r4(r.coef), r4(r.lo), r4(r.hi), int(r.n)]
            for r in im.itertuples()}
    se = t("sensibilidad.csv")
    sens = [[r.analisis, r.country_frame, r.medida, r4(r.diferencia_2010_24_vs_1990s), r4(r.lo), r4(r.hi), int(r.n)]
            for r in se.itertuples() if pd.notna(r.diferencia_2010_24_vs_1990s)]
    aj = t("ajustados.csv")
    adj = {f"{r.modelo}|{r.resultado}|{r.cohorte}": [r4(r.estimacion), r4(r.coef_lo), r4(r.coef_hi)] for r in aj.itertuples()}
    ac = pd.concat([t("../acuerdo_v2_completa.csv").assign(etapa="v2_completa"),
                    t("../acuerdo_v2_modb.csv").assign(etapa="v2_modb")])
    acu = {f"{r.etapa}|{r.variable}": r4(r.kappa if pd.notna(r.kappa) else (r.alfa_intervalo if pd.notna(r.alfa_intervalo)
                                                                                 else r.jaccard)) for r in ac.itertuples()}
    rec = d.groupby("country_frame").reconocida.mean()
    cv = t("covariables.csv")
    cov = [[r.variable, r.country_frame, COH.index(r.cohort), str(r.valor), r4(r.prop)] for r in cv.itertuples()]
    hist = json.loads((V2 / "historia_web.json").read_text(encoding="utf-8"))
    u = d.drop_duplicates("tconst")
    both = u[u.final_A.notna() & u.final_B.notna()]
    agr = {"acuerdo_final": r4((both.final_A == both.final_B).mean()),
           "kappa_final": r4(__import__("finales.agreement", fromlist=["x"]).cohen_kappa(both.final_A, both.final_B)),
           "n_adj": int((u.final_fuente == "adjudicado").sum())}
    from .agreement import krippendorff_alpha, cohen_kappa
    cd = u[u.feel_good_A.notna() | u.feel_good_B.notna()]
    for k in ("feel_good", "utopia"):
        pr = cd[[f"{k}_A", f"{k}_B"]].dropna()
        agr[f"alfa_{k}"] = r4(krippendorff_alpha([list(x) for x in zip(pr[f"{k}_A"], pr[f"{k}_B"])], "interval"))
        agr[f"dentro2_{k}"] = r4(((pr[f"{k}_A"] - pr[f"{k}_B"]).abs() <= 2).mean())
        agr[f"n_adj_{k}"] = int((u[f"{k}_fuente"] == "adjudicado").sum())
    pb = u[u.publico_A.notna() & u.publico_B.notna()]
    agr["kappa_publico"] = r4(cohen_kappa(pb.publico_A, pb.publico_B))
    agr["acuerdo_publico"] = r4((pb.publico_A == pb.publico_B).mean())
    agr["n_cde"] = int(len(cd))
    fgb = pd.cut(d.feel_good, [-0.1, 2.49, 4.49, 6.49, 8.49, 10], labels=[0, 1, 2, 3, 4]).astype(float)
    cc = d[d.clasificable & fgb.notna()]
    mfg = pd.crosstab(cc.final, fgb[cc.index]).reindex(index=FIN[:4], columns=[0.0, 1.0, 2.0, 3.0, 4.0]).fillna(0).astype(int)
    es = d[d.country_frame == "ES"]
    src_es = es.sinopsis_idioma.fillna("ninguna").value_counts().to_dict()
    return {"historia": hist, "acuerdo_censo": agr, "cohortes": coh, "anual": year, "contrastes": contr, "subgrupos": sub, "final_animo": fvm,
            "matriz": {"filas": FIN[:4], "cols": [int(x) for x in mat.columns], "n": mat.values.tolist()},
            "matriz_fg": {"filas": FIN[:4], "n": mfg.values.tolist()}, "fuentes_es": src_es,
            "sin_fg": {cf: r4(g.feel_good.isna().mean()) for cf, g in d.groupby("country_frame")},
            "imdb": imdb, "sensibilidad": sens, "ajustados": adj, "acuerdo": acu, "covariables": cov,
            "reconocidas": {k: r4(v) for k, v in rec.items()},
            "n": {"US": int((d.country_frame == "US").sum()), "ES": int((d.country_frame == "ES").sum()),
                  "total": int(d.tconst.nunique()), "explorador": int(d_all.tconst.nunique()),
                  "en_curso": int(d_all[d_all.anio_en_curso == True].tconst.nunique())}}


def main_v2() -> None:
    # La web presenta un único estudio (censo + España): data.json solo lleva los agregados del censo.
    cat = pd.read_csv(TABLES / "catalogo_por_cohorte.csv")
    data = {"v2": build_v2(), "meta": {"catalogo_us": int(cat.catalogo_elegible.sum()),
                                       "catalogo_es": int(len(pd.read_csv(INTERIM / "catalog_es_v4.csv")))}}
    (ROOT / "web" / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    f = ROOT / "web" / "films.json"
    f.write_text(json.dumps(build_films_v2(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print((ROOT / "web" / "data.json").stat().st_size, f.stat().st_size)



def _notes(stage_dirs: list[str]) -> dict:
    """id → {"A": (final, nota), "B": (...)} a partir de las etiquetas."""
    out = {}
    for sd in stage_dirs:
        for a in "AB":
            for f in sorted((ROOT / "annotation" / "labels" / sd / a).glob("*.jsonl")):
                for line in f.read_text(encoding="utf-8").splitlines():
                    if line.strip():
                        r = json.loads(line)
                        out.setdefault(r["id"], {})[a] = [r.get("final"), r.get("nota")]
    return out


def _adj_notes(dirs: list[str]) -> dict:
    out = {}
    for sd in dirs:
        for f in sorted((ROOT / "annotation" / "labels" / sd).glob("*.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    r = json.loads(line)
                    out[r["id"]] = [r.get("final"), r.get("nota")]
    return out


def build_fichas() -> dict[int, dict]:
    """Fichas por año (carga diferida en la web): sinopsis original de Wikipedia usada (CC BY-SA 4.0, con URL de la
    revisión) y las notas de los anotadores y del adjudicador sobre el final (D-030)."""
    from . import v2
    d = pd.read_csv(INTERIM / "analitico_v2.csv").drop_duplicates("tconst")
    k1 = pd.read_csv(ANNOT_KEYS / "principal_key.csv").drop_duplicates("tconst").set_index("tconst").id
    notes = _notes(["principal", "v2_completa", "v2_es_en", "v2_ext", "v2_es3", "v2_es3_en", "v2_es4", "v2_es4_en",
                    "v2_es5"])
    adj = _adj_notes(["principal/adjudicacion", "v2_adjudicacion"])
    out: dict[int, dict] = {}
    txt = lambda v: v if isinstance(v, str) and v else None
    for r in d.itertuples():
        if pd.isna(r.final):
            continue
        i = k1.get(r.tconst) if r.etapa_v2 == "v2_modb" else r.id_v2
        lang = r.sinopsis_idioma if isinstance(r.sinopsis_idioma, str) else "en"
        rec = v2.synopsis_src(r.tconst, lang) if lang not in ("en", "es") else v2.synopsis_for(r.tconst, lang)
        n = notes.get(i, {})
        # D-035: las sinopsis de TMDB no se publican, solo se enlazan
        s = None if lang == "tmdb" else (rec or {}).get("text")
        out.setdefault(int(r.year), {})[r.tconst] = {
            "s": s, "l": lang if rec else lang, "u": (rec or {}).get("revision_url"),
            "A": n.get("A"), "B": n.get("B"), "J": adj.get(i),
            "fA": txt(getattr(r, "feel_good_por_que_A", None)), "fB": txt(getattr(r, "feel_good_por_que_B", None)),
            "fJ": txt(getattr(r, "feel_good_por_que_J", None)),
            "uA": txt(getattr(r, "utopia_por_que_A", None)), "uB": txt(getattr(r, "utopia_por_que_B", None)),
            "uJ": txt(getattr(r, "utopia_por_que_J", None))}
    return out


def main_fichas() -> None:
    fd = ROOT / "web" / "fichas"
    fd.mkdir(parents=True, exist_ok=True)
    tot = 0
    for y, recs in build_fichas().items():
        p = fd / f"{y}.json"
        p.write_text(json.dumps(recs, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        tot += p.stat().st_size
    print("fichas", tot)


if __name__ == "__main__":
    main()
