"""Análisis de resultados: acuerdo, descriptivos con incertidumbre, comparaciones, modelos y sensibilidad.

Todas las cifras del informe salen de las tablas que escribe este módulo en reports/tables/.
"""
from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from . import agreement as ag
from . import annotation as an
from . import stats as st
from .config import ANNOT, DERIVED, INTERIM, TABLES, load

POS_TONE = {"ESPERANZA", "ALIVIO", "CONEXION"}
NEG_TONE = {"RESIGNACION", "DESESPERANZA"}
FINALS = ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"]
RECENT = ["2010-2019", "2020-2024"]


# ---------------------------------------------------------------- carga

def load_stage(stage: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame | None, list[str]]:
    """Devuelve (A, B, adjudicación|None, errores) para una etapa."""
    errs = []
    lab = ANNOT / "labels" / stage
    A, e = an.load_labels(sorted((lab / "A").glob("*.jsonl")), "A")
    errs += [f"A {x}" for x in e]
    B, e = an.load_labels(sorted((lab / "B").glob("*.jsonl")), "B")
    errs += [f"B {x}" for x in e]
    adj = None
    adj_files = sorted((lab / "adjudicacion").glob("*.jsonl")) if (lab / "adjudicacion").exists() else []
    if adj_files:
        rows = []
        for p in adj_files:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        adj = pd.DataFrame(rows)
    return A, B, adj, errs


def attach_metadata(df: pd.DataFrame, stage: str) -> pd.DataFrame:
    key = pd.read_csv(an.KEY_DIR / f"{stage}_key.csv")
    sample = pd.read_csv(DERIVED / f"muestra_{stage}.csv")
    cat = pd.read_csv(INTERIM / "catalog.csv", usecols=["tconst", "numVotes"])
    out = df.merge(key, on="id", how="left")
    films = sample.drop_duplicates("tconst").drop(columns=["frame", "stratum_pop", "N_stratum",
                                                           "n_stratum", "design_weight"])
    out = out.merge(films, on="tconst", how="left").merge(cat, on="tconst", how="left")
    return out


# ---------------------------------------------------------------- acuerdo

def agreement_report(stage: str) -> dict:
    A, B, _, errs = load_stage(stage)
    pr = an.pair(A, B)
    both = pr[pr["_merge"] == "both"]
    rows = []
    for k in an.CATS:
        rows.append({"variable": k, "n": len(both), "acuerdo_pct": ag.percent_agreement(both[f"{k}_A"], both[f"{k}_B"]),
                     "kappa_cohen": ag.cohen_kappa(both[f"{k}_A"], both[f"{k}_B"]),
                     "alfa_krippendorff": ag.krippendorff_alpha(both[[f"{k}_A", f"{k}_B"]].values.tolist(), "nominal")})
    fa, fb = both["final_A"], both["final_B"]
    rows.append({"variable": "final (ordinal 4 cat., kappa cuadrática)", "n": int((fa.isin(an.ORDINAL_FINAL) & fb.isin(an.ORDINAL_FINAL)).sum()),
                 "acuerdo_pct": np.nan, "kappa_cohen": ag.weighted_kappa(fa, fb, an.ORDINAL_FINAL),
                 "alfa_krippendorff": np.nan})
    hap_a, hap_b = (fa == "FELIZ"), (fb == "FELIZ")
    rows.append({"variable": "final feliz (sí/no)", "n": len(both), "acuerdo_pct": ag.percent_agreement(hap_a, hap_b),
                 "kappa_cohen": ag.cohen_kappa(hap_a, hap_b), "alfa_krippendorff": np.nan})
    for k in an.ITEMS:
        rows.append({"variable": k, "n": int((both[f"{k}_A"].notna() & both[f"{k}_B"].notna()).sum()),
                     "acuerdo_pct": ag.percent_agreement(both[f"{k}_A"], both[f"{k}_B"]),
                     "kappa_cohen": np.nan,
                     "alfa_krippendorff": ag.krippendorff_alpha(both[[f"{k}_A", f"{k}_B"]].values.tolist(), "interval")})
    va, vb = an.vision_score(both.rename(columns={f"{k}_A": k for k in an.ITEMS})), \
        an.vision_score(both.rename(columns={f"{k}_B": k for k in an.ITEMS}))
    rows.append({"variable": "vision_vida (media ítems)", "n": int((va.notna() & vb.notna()).sum()),
                 "acuerdo_pct": np.nan, "kappa_cohen": np.nan,
                 "alfa_krippendorff": ag.krippendorff_alpha(np.c_[va, vb].tolist(), "interval")})
    tab = pd.DataFrame(rows)
    tab.to_csv(TABLES / f"acuerdo_{stage}.csv", index=False, float_format="%.3f")
    conf = ag.confusion(fa, fb, an.CATS["final"])
    conf.to_csv(TABLES / f"confusion_final_{stage}.csv")

    # Desacuerdo por cohorte y género: ¿el error de medida es diferencial?
    meta = attach_metadata(both[["id"]].assign(dis=(fa != fb).values,
                                               hap_dis=(hap_a != hap_b).values), stage)
    by = []
    for col in ("cohort", "genre_main"):
        g = meta.groupby(col).agg(n=("id", "size"), desacuerdo_final=("dis", "mean"),
                                  desacuerdo_feliz=("hap_dis", "mean")).reset_index().rename(columns={col: "grupo"})
        g.insert(0, "dimension", col)
        by.append(g)
    pd.concat(by).to_csv(TABLES / f"desacuerdo_por_grupo_{stage}.csv", index=False, float_format="%.3f")

    # Diferencias sistemáticas entre anotadores (sesgo de un modelo frente al otro)
    marg = pd.DataFrame({"A": fa.value_counts(normalize=True), "B": fb.value_counts(normalize=True)}).fillna(0)
    marg.to_csv(TABLES / f"marginales_anotadores_{stage}.csv", float_format="%.3f")
    info = {"n_A": len(A), "n_B": len(B), "n_pares": len(both), "errores_validacion": errs,
            "reconocidas_A": int(A["reconocida"].sum()), "reconocidas_B": int(B["reconocida"].sum())}
    (TABLES / f"acuerdo_{stage}_info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1))
    return {"tabla": tab, "confusion": conf, "info": info}


# ---------------------------------------------------------------- dataset analítico

def analytic_dataset(stage: str = "principal") -> pd.DataFrame:
    """Una fila por película × marco (una película puede estar en ambos marcos)."""
    A, B, adj, _ = load_stage(stage)
    fin = an.finalize(an.pair(A, B), adj)
    key = pd.read_csv(an.KEY_DIR / f"{stage}_key.csv")
    fin = fin.merge(key, on="id", how="left")
    # confianza mínima de los dos anotadores
    conf = A[["id", "confianza"]].merge(B[["id", "confianza"]], on="id", suffixes=("_A", "_B"))
    conf["confianza_min"] = conf[["confianza_A", "confianza_B"]].min(axis=1)
    fin = fin.merge(conf[["id", "confianza_min"]], on="id", how="left")
    # acuerdo original en final
    agree = A[["id", "final"]].merge(B[["id", "final"]], on="id", suffixes=("_A", "_B"))
    agree["acuerdo_final"] = agree["final_A"] == agree["final_B"]
    fin = fin.merge(agree[["id", "acuerdo_final", "final_A", "final_B"]], on="id", how="left")

    sample = pd.read_csv(DERIVED / f"muestra_{stage}.csv")
    # Solo los votos brutos proceden del catálogo (no redistribuible); el rango en el año está en la muestra congelada.
    cat = pd.read_csv(INTERIM / "catalog.csv", usecols=["tconst", "numVotes"])
    df = sample.merge(fin, on="tconst", how="inner").merge(cat, on="tconst", how="left")
    df["clasificable"] = df["final"].isin(FINALS)
    for f in FINALS:
        df[f"y_{f.lower()}"] = np.where(df["clasificable"], (df["final"] == f).astype(float), np.nan)
    df["y_resolucion_positiva"] = np.where(df["clasificable"], df["final"].isin(["FELIZ", "AGRIDULCE"]).astype(float), np.nan)
    for who in ("A", "B"):
        df[f"y_feliz_{who}"] = np.where(df[f"final_{who}"].isin(FINALS), (df[f"final_{who}"] == "FELIZ").astype(float), np.nan)
    df["y_feliz_incl_nc"] = (df["final"] == "FELIZ").astype(float)   # no clasificables cuentan como no felices
    df["y_feliz_estricto"] = np.where(df["clasificable"],
                                      ((df["final"] == "FELIZ") & df["tono_cierre"].isin(POS_TONE)).astype(float), np.nan)
    df["y_tono_positivo"] = np.where(df["tono_cierre"] == "NO_CLARO", np.nan,
                                     df["tono_cierre"].isin(POS_TONE).astype(float))
    df["y_sobrevive"] = np.where(df["supervivencia"] == "NO_CLARO", np.nan, (df["supervivencia"] == "SOBREVIVE").astype(float))
    df["y_objetivo"] = np.where(df["objetivo"] == "NO_CLARO", np.nan, (df["objetivo"] == "LOGRADO").astype(float))
    df["y_justicia"] = np.where(df["justicia_narrativa"].isin(["NO_CLARO", "NO_APLICA"]), np.nan,
                                (df["justicia_narrativa"] == "SI").astype(float))
    df["y_relaciones"] = np.where(df["relaciones"].isin(["NO_CLARO", "NO_APLICA"]), np.nan,
                                  (df["relaciones"] == "FORTALECIDAS").astype(float))
    df["periodo"] = np.where(df["cohort"].isin(RECENT), "2010-2024", df["cohort"])
    df["w_design"] = df["design_weight"]
    df["estrato"] = df["frame"] + "|" + df["cohort"] + "|" + df["stratum_pop"]
    df["w_votes"] = df["design_weight"] * df["numVotes"]
    df.to_csv(INTERIM / f"analitico_{stage}.csv", index=False)
    return df


OUTCOMES = {
    "y_feliz": "Final feliz", "y_agridulce": "Final agridulce", "y_ambiguo": "Final ambiguo",
    "y_tragico": "Final trágico", "y_resolucion_positiva": "Feliz o agridulce",
    "y_tono_positivo": "Tono de cierre positivo", "y_sobrevive": "Protagonista sobrevive",
    "y_objetivo": "Objetivo logrado", "y_justicia": "Justicia narrativa", "y_relaciones": "Vínculos fortalecidos",
}


def descriptives(df: pd.DataFrame, by: list[str], weight: str = "w_design") -> pd.DataFrame:
    rows = []
    for keys, g in df.groupby(by):
        keys = keys if isinstance(keys, tuple) else (keys,)
        base = dict(zip(by, keys))
        base.update({"n_peliculas": len(g), "n_no_clasificables": int((~g["clasificable"]).sum())})
        for y, lab in OUTCOMES.items():
            v = g[y].notna()
            p, lo, hi, neff = st.weighted_prop_ci(g.loc[v, y], g.loc[v, weight])
            rows.append({**base, "medida": lab, "variable": y, "n": int(v.sum()), "estimacion": p,
                         "ic95_inf": lo, "ic95_sup": hi, "n_efectivo": neff})
        m, lo, hi = st.mean_ci(g["vision_vida"].values, g[weight].values)
        rows.append({**base, "medida": "Visión de la vida (−2 a +2)", "variable": "vision_vida",
                     "n": int(g["vision_vida"].notna().sum()), "estimacion": m, "ic95_inf": lo, "ic95_sup": hi,
                     "n_efectivo": np.nan})
    return pd.DataFrame(rows)


def contrasts(df: pd.DataFrame, y: str, weight: str = "w_design", ref: str = "1990-1999",
              group_col: str = "cohort", seed: int = 0, n_boot: int = 10000) -> pd.DataFrame:
    rows = []
    groups = [c for c in sorted(df[group_col].dropna().unique()) if c != ref]
    for g in groups:
        r = st.bootstrap_diff(df[y].values, df[group_col].values, g, ref, df[weight].values,
                              n_boot=n_boot, seed=seed, strata=df["estrato"].values)
        rows.append({"comparacion": f"{g} − {ref}", "variable": y, **r})
    return pd.DataFrame(rows)


def adjusted_contrast(df: pd.DataFrame, y: str, binary: bool = True, n_boot: int = 500, seed: int = 0,
                      weight: str = "w_design") -> dict:
    """Efecto ajustado 2010-2024 frente a 1990-1999 (y por cohorte), controlando género y popularidad.

    Binario: logit ponderado + efecto marginal medio por g-computación con IC bootstrap.
    Continuo: MCO ponderado con errores HC3.
    Popularidad = log del rango de votos en el año (marco popular) o tramo de popularidad (marco amplio).
    """
    d = df[df[y].notna()].copy()
    d = d[d["periodo"].isin(["1990-1999", "2010-2024"])]
    d["recent"] = (d["periodo"] == "2010-2024").astype(int)
    d["w"] = d[weight] / d[weight].mean()
    # Géneros con muy pocos casos se agrupan para evitar separación perfecta
    counts = d["genre_main"].value_counts()
    d["genero"] = d["genre_main"].where(d["genre_main"].map(counts) >= 8, "Otros/pequeños")
    # Control de popularidad comparable entre años (D-019): el percentil de votos dentro del año depende del
    # tamaño del catálogo anual (mayor en años recientes), así que se usa el rango dentro del año (marco popular,
    # 1-50) o el tramo de popularidad de diseño (marco amplio, terciles).
    if d["frame"].iloc[0] == "popular":
        d["pop_ctrl"] = np.log(d["votes_rank_in_year"])
        formula = f"{y} ~ recent + C(genero) + pop_ctrl"
    else:
        formula = f"{y} ~ recent + C(genero) + C(pop_tier)"
    rng = np.random.default_rng(seed)

    def fit_effect(data):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if binary:
                import statsmodels.api as sm
                m = smf.glm(formula, data, family=sm.families.Binomial(), var_weights=data["w"]).fit()
                d1, d0 = data.assign(recent=1), data.assign(recent=0)
                return float(np.average(m.predict(d1) - m.predict(d0), weights=data["w"])), m
            m = smf.wls(formula, data, weights=data["w"]).fit(cov_type="HC3")
            return float(m.params["recent"]), m

    est, model = fit_effect(d)
    if binary:
        boots, failed = [], 0
        cells = [np.where(d["estrato"] == s_)[0] for s_ in d["estrato"].unique()]
        for _ in range(n_boot):
            s = d.iloc[np.concatenate([rng.choice(c, len(c)) for c in cells])]
            try:
                boots.append(fit_effect(s)[0])
            except Exception:  # separación u otro fallo de ajuste en una réplica
                failed += 1
        lo, hi = np.quantile(boots, [0.025, 0.975])
    else:
        ci = model.conf_int().loc["recent"]
        lo, hi = float(ci[0]), float(ci[1])
    return {"variable": y, "efecto_ajustado": est, "ic95_inf": lo, "ic95_sup": hi, "n": len(d),
            "modelo": "logit + EMM (bootstrap)" if binary else "MCO ponderado (HC3)",
            "replicas_fallidas": failed if binary else 0}


def sensitivity(df: pd.DataFrame, frame: str = "popular", seed: int = 0) -> pd.DataFrame:
    """Diferencia 2010-2024 − 1990-1999 bajo definiciones y submuestras alternativas."""
    d = df[df["frame"] == frame]
    specs = [
        ("Principal: final feliz, peso de diseño", d, "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Definición amplia: feliz o agridulce", d, "y_resolucion_positiva", "w_design", "periodo", "2010-2024"),
        ("Definición estricta: feliz y tono de cierre positivo", d, "y_feliz_estricto", "w_design", "periodo", "2010-2024"),
        ("Ponderado por popularidad (votos IMDb)", d, "y_feliz", "w_votes", "periodo", "2010-2024"),
        ("Incluye no clasificables como no felices", d, "y_feliz_incl_nc", "w_design", "periodo", "2010-2024"),
        ("Excluye películas reconocidas por algún anotador", d[~d["reconocida"].astype(bool)], "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Excluye películas reconocidas por ambos anotadores", d[~(d["reconocida_A"].astype(bool) & d["reconocida_B"].astype(bool))], "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Solo etiquetas del anotador A (sin adjudicación)", d, "y_feliz_A", "w_design", "periodo", "2010-2024"),
        ("Solo etiquetas del anotador B (sin adjudicación)", d, "y_feliz_B", "w_design", "periodo", "2010-2024"),
        ("Solo acuerdo inicial entre anotadores", d[d["acuerdo_final"] == True], "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Solo confianza alta (3) en ambos (selecciona casos claros)", d[d["confianza_min"] == 3], "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Solo producciones solo de EE. UU.", d[d["us_only"].astype(bool)], "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Umbral de popularidad más estricto (top 20/año)", d[d["votes_rank_in_year"] <= 20], "y_feliz", "w_design", "periodo", "2010-2024"),
        ("Solo década completa 2010-2019", d, "y_feliz", "w_design", "cohort", "2010-2019"),
        ("Solo 2020-2024", d, "y_feliz", "w_design", "cohort", "2020-2024"),
        ("Visión de la vida (media, escala −2 a +2)", d, "vision_vida", "w_design", "periodo", "2010-2024"),
        ("Visión de la vida ponderada por votos", d, "vision_vida", "w_votes", "periodo", "2010-2024"),
        ("Tono de cierre positivo", d, "y_tono_positivo", "w_design", "periodo", "2010-2024"),
        ("Final trágico", d, "y_tragico", "w_design", "periodo", "2010-2024"),
    ]
    rows = []
    for name, data, y, w, gcol, g1 in specs:
        r = st.bootstrap_diff(data[y].values, data[gcol].values, g1, "1990-1999", data[w].values,
                              n_boot=10000, seed=seed, strata=data["estrato"].values)
        p0 = data.loc[(data[gcol] == "1990-1999") & data[y].notna()]
        p1 = data.loc[(data[gcol] == g1) & data[y].notna()]
        rows.append({"especificacion": name, "marco": frame, "variable": y,
                     "valor_1990s": np.average(p0[y], weights=p0[w]) if len(p0) else np.nan,
                     "valor_comparado": np.average(p1[y], weights=p1[w]) if len(p1) else np.nan,
                     "grupo_comparado": g1, **r})
    return pd.DataFrame(rows)


def _wmean(d: pd.DataFrame, y: str, w: str = "w_design") -> float:
    d = d[d[y].notna()]
    return float(np.average(d[y], weights=d[w])) if len(d) else np.nan


def genre_table(df: pd.DataFrame, frame: str = "popular") -> pd.DataFrame:
    d = df[(df["frame"] == frame) & df["periodo"].isin(["1990-1999", "2010-2024"])]
    rows = []
    for g, gd in d.groupby("genre_main"):
        r = st.bootstrap_diff(gd["y_feliz"].values, gd["periodo"].values, "2010-2024", "1990-1999",
                              gd["w_design"].values, n_boot=4000, strata=gd["estrato"].values)
        v = {p: _wmean(gd[gd.periodo == p], "vision_vida") for p in ("1990-1999", "2010-2024")}
        rows.append({"genero": g, "marco": frame, "n_1990s": r["n0"], "n_2010_2024": r["n1"],
                     "feliz_1990s": _wmean(gd[gd.periodo == "1990-1999"], "y_feliz"),
                     "feliz_2010_2024": _wmean(gd[gd.periodo == "2010-2024"], "y_feliz"),
                     "dif_pp": r["diff"] * 100, "dif_ic95_inf_pp": r["diff_lo"] * 100, "dif_ic95_sup_pp": r["diff_hi"] * 100,
                     "vision_1990s": v.get("1990-1999", np.nan), "vision_2010_2024": v.get("2010-2024", np.nan)})
    return pd.DataFrame(rows).sort_values("n_1990s", ascending=False)


def follows_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Comparación orientativa con la cifra de acción de Follows (1980-1999 frente a 2010 en adelante).

    Nuestra definición de acción = género principal «Acción/aventura» (prioridad de géneros de IMDb), marco popular.
    No es una réplica: población, fuente de sinopsis, categorías y clasificador difieren.
    """
    rows = []
    for frame in ("popular", "amplio"):
        d = df[(df["frame"] == frame) & (df["genre_main"] == "Acción/aventura") & df["y_feliz"].notna()].copy()
        d["grupo"] = np.where(d["cohort"].isin(["1980-1989", "1990-1999"]), "1980-1999",
                              np.where(d["cohort"].isin(RECENT), "2010-2024", "2000-2009"))
        for g, gd in list(d.groupby("grupo")) + list(d[d.cohort.isin(["1980-1989", "1990-1999"])].groupby("cohort")):
            p, lo, hi, n_eff = st.weighted_prop_ci(gd["y_feliz"], gd["w_design"])
            rows.append({"marco": frame, "grupo": g, "n": len(gd), "feliz": p, "ic95_inf": lo, "ic95_sup": hi})
        r = st.bootstrap_diff(d["y_feliz"].values, d["grupo"].values, "2010-2024", "1980-1999", d["w_design"].values,
                              n_boot=10000, strata=d["estrato"].values)
        rows.append({"marco": frame, "grupo": "diferencia 2010-2024 − 1980-1999", "n": r["n1"] + r["n0"],
                     "feliz": r["diff"], "ic95_inf": r["diff_lo"], "ic95_sup": r["diff_hi"]})
    return pd.DataFrame(rows)


def adjudication_stats(stage: str) -> pd.DataFrame:
    """¿Con qué frecuencia coincide el adjudicador con A (mismo modelo) o con B? Riesgo de sesgo hacia A."""
    A, B, adj, _ = load_stage(stage)
    if adj is None:
        return pd.DataFrame()
    m = adj.merge(A, on="id", suffixes=("", "_A")).merge(B, on="id", suffixes=("", "_B"))
    rows = []
    for k in list(an.CATS) + an.ITEMS:
        if k not in adj.columns:
            continue
        sub = m[m[k].notna()]
        if k in an.CATS:
            sub = sub[sub[f"{k}_A"] != sub[f"{k}_B"]]
        else:
            sub = sub[(sub[f"{k}_A"] - sub[f"{k}_B"]).abs() >= 3]
        if sub.empty:
            continue
        rows.append({"campo": k, "n_adjudicados": len(sub), "elige_A": float((sub[k] == sub[f"{k}_A"]).mean()),
                     "elige_B": float((sub[k] == sub[f"{k}_B"]).mean())})
    return pd.DataFrame(rows)


def run(stage: str = "principal") -> dict:
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    cfg = load()
    seed = cfg["project"]["seed"]
    agreement_report(stage)
    df = analytic_dataset(stage)
    out = {}
    desc = descriptives(df, ["frame", "cohort"])
    desc.to_csv(TABLES / "descriptivos_marco_cohorte.csv", index=False, float_format="%.4f")
    descriptives(df, ["frame", "periodo"]).to_csv(TABLES / "descriptivos_marco_periodo.csv", index=False, float_format="%.4f")
    descriptives(df, ["frame", "periodo", "genre_main"]).to_csv(TABLES / "descriptivos_genero.csv", index=False, float_format="%.4f")
    descriptives(df, ["frame", "cohort"], weight="w_votes").to_csv(TABLES / "descriptivos_marco_cohorte_pond_votos.csv", index=False, float_format="%.4f")

    # distribución de las 5 categorías, incluida no clasificable
    dist = (df.groupby(["frame", "cohort"])["final"].value_counts().unstack(fill_value=0))
    dist.to_csv(TABLES / "distribucion_finales_recuentos.csv")
    tono = df.groupby(["frame", "cohort"])["tono_cierre"].value_counts().unstack(fill_value=0)
    tono.to_csv(TABLES / "distribucion_tono_recuentos.csv")

    cons = []
    for frame in ("popular", "amplio"):
        d = df[df["frame"] == frame]
        for y in ["y_feliz", "y_agridulce", "y_ambiguo", "y_tragico", "y_tono_positivo", "vision_vida"]:
            c = contrasts(d, y, seed=seed)
            c2 = contrasts(d, y, group_col="periodo", seed=seed)
            c2 = c2[c2["comparacion"].str.startswith("2010-2024")]
            cons.append(pd.concat([c, c2]).assign(marco=frame))
    cons = pd.concat(cons)
    cons.to_csv(TABLES / "contrastes_vs_1990s.csv", index=False, float_format="%.4f")

    adj = []
    for frame in ("popular", "amplio"):
        d = df[df["frame"] == frame]
        for y, binary in [("y_feliz", True), ("y_tragico", True), ("y_tono_positivo", True), ("vision_vida", False)]:
            r = adjusted_contrast(d, y, binary, seed=seed)
            adj.append({**r, "marco": frame})
    pd.DataFrame(adj).to_csv(TABLES / "efectos_ajustados.csv", index=False, float_format="%.4f")

    sens = pd.concat([sensitivity(df, "popular", seed), sensitivity(df, "amplio", seed)])
    sens.to_csv(TABLES / "sensibilidad.csv", index=False, float_format="%.4f")
    pd.concat([genre_table(df, "popular"), genre_table(df, "amplio")]).to_csv(
        TABLES / "genero_contrastes.csv", index=False, float_format="%.3f")

    comp = (df[df["periodo"].isin(["1990-1999", "2010-2024"])].groupby(["frame", "periodo"])["genre_main"]
            .value_counts(normalize=True).unstack(fill_value=0))
    comp.to_csv(TABLES / "composicion_generos.csv", float_format="%.4f")
    follows_comparison(df).to_csv(TABLES / "comparacion_follows_accion.csv", index=False, float_format="%.4f")
    adjudication_stats(stage).to_csv(TABLES / "adjudicacion_resumen.csv", index=False, float_format="%.3f")
    rec = df.drop_duplicates("tconst").assign(rec_A=lambda x: x["reconocida_A"].astype(bool),
                                               rec_B=lambda x: x["reconocida_B"].astype(bool))
    rec.groupby("cohort").agg(n=("tconst", "size"), reconocida_A=("rec_A", "mean"), reconocida_B=("rec_B", "mean"),
                              reconocida_alguno=("reconocida", "mean")).to_csv(
        TABLES / "reconocimiento_por_cohorte.csv", float_format="%.3f")
    recf = df.assign(rec_A=df["reconocida_A"].astype(bool), rec_B=df["reconocida_B"].astype(bool),
                     rec_any=df["reconocida"].astype(bool))
    recf.groupby(["frame", "cohort"]).agg(n=("tconst", "size"), reconocida_A=("rec_A", "mean"),
                                          reconocida_B=("rec_B", "mean"), reconocida_alguno=("rec_any", "mean"),
                                          reconocida_ambos=("rec_A", lambda x: float((x & recf.loc[x.index, "rec_B"]).mean()))
                                          ).to_csv(TABLES / "reconocimiento_por_marco.csv", float_format="%.3f")
    missing = df.groupby(["frame", "cohort"]).agg(n=("tconst", "size"), no_clasificables=("clasificable", lambda x: int((~x).sum())))
    missing.to_csv(TABLES / "no_clasificables_por_cohorte.csv")

    # Relación entre dimensiones: final frente a visión de la vida
    cross = df.drop_duplicates("tconst").groupby("final").agg(
        n=("tconst", "size"), vision_media=("vision_vida", "mean"),
        tono_positivo=("y_tono_positivo", "mean")).reindex(an.CATS["final"])
    cross.to_csv(TABLES / "final_vs_vision.csv", float_format="%.3f")
    out["df"] = df
    return out


if __name__ == "__main__":
    import sys
    stage = sys.argv[1] if len(sys.argv) > 1 else "principal"
    if stage == "piloto":
        agreement_report("piloto")   # el piloto solo sirve para acuerdo y tamaño muestral
    else:
        run(stage)
