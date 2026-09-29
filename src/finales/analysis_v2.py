"""Análisis v2: censo del cine popular estadounidense (top 50 por año, 1980-2024) y cine español (top 15 por año).

Interpretación de la incertidumbre: en el censo no hay error de muestreo respecto al universo definido. Los intervalos
(Wilson y bootstrap por película) se interpretan como incertidumbre sobre el «proceso» que genera las películas de cada
cohorte (superpoblación), no como error de encuesta. No incluyen el error de medición de las etiquetas, que se trata con
sensibilidades (anotador A solo, B solo, etiquetas originales, excluir películas reconocidas).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from . import stats as st
from .annotation import RELACIONES
from .config import INTERIM, ROOT

TABLES = ROOT / "reports" / "tables" / "v2"
REF = "1990-1999"
RECIENTE = ["2010-2019", "2020-2024"]
COHORTS = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]
FINALS = ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"]


def load() -> pd.DataFrame:
    d = pd.read_csv(INTERIM / "analitico_v2.csv")
    d["reciente"] = d.cohort.isin(RECIENTE)
    d["log_rank"] = np.log(d.votes_rank_in_year)
    d["especulativa_si"] = (d.especulativa != "NO").astype(float)
    d["y_nf_opt"] = ((d.final != "FELIZ") & (d.optimismo_personajes > 0)).astype(float).where(d.clasificable)
    d["contemporanea"] = (d.epoca_trama == "DE_1980_EN_ADELANTE").astype(float)
    return d


def _boot_diff(y1: np.ndarray, y0: np.ndarray, n_boot: int = 4000, seed: int = 0) -> tuple[float, float, float]:
    y1, y0 = y1[~np.isnan(y1)], y0[~np.isnan(y0)]
    if len(y1) < 5 or len(y0) < 5:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    b = [rng.choice(y1, len(y1)).mean() - rng.choice(y0, len(y0)).mean() for _ in range(n_boot)]
    return y1.mean() - y0.mean(), *np.percentile(b, [2.5, 97.5])


def by_cohort(d: pd.DataFrame, keys=("country_frame", "cohort")) -> pd.DataFrame:
    rows = []
    for k, g in d.groupby(list(keys)):
        c = g[g.clasificable]
        f = st.wilson(int((c.final == "FELIZ").sum()), len(c))
        t = st.wilson(int((c.final == "TRAGICO").sum()), len(c))
        o = st.mean_ci(g.optimismo_personajes.dropna().values)
        tg = st.mean_ci(g.tono_general.dropna().values)
        rows.append({**dict(zip(keys, k if isinstance(k, tuple) else (k,))), "n": len(g), "n_clasificable": len(c),
                     "pct_no_clasificable": 1 - len(c) / len(g),
                     "feliz": f[0], "feliz_lo": f[1], "feliz_hi": f[2],
                     "agridulce": (c.final == "AGRIDULCE").mean(), "ambiguo": (c.final == "AMBIGUO").mean(),
                     "tragico": t[0], "tragico_lo": t[1], "tragico_hi": t[2],
                     "optimismo": o[0], "optimismo_lo": o[1], "optimismo_hi": o[2],
                     "pct_optimistas": g.y_optimistas.mean(),
                     "tono": tg[0], "tono_lo": tg[1], "tono_hi": tg[2], "pct_tono_pos": g.y_tono_pos.mean(),
                     "vision": g.vision_vida.mean(), "tragedia_vitalista": c.tragedia_vitalista.mean(),
                     "no_feliz_optimista": ((c.final != "FELIZ") & (c.optimismo_personajes > 0)).mean(),
                     "optimistas_en_no_felices": (c[c.final != "FELIZ"].optimismo_personajes > 0).mean(),
                     "optimistas_en_tragicos": (c[c.final == "TRAGICO"].optimismo_personajes > 0).mean()})
    return pd.DataFrame(rows)


def contrasts(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ys = {"feliz": "y_feliz", "tragico": "y_tragico", "optimismo": "optimismo_personajes", "tono": "tono_general",
          "pct_optimistas": "y_optimistas", "vision": "vision_vida", "no_feliz_optimista": "y_nf_opt"}
    for cf, g in d.groupby("country_frame"):
        g0 = g[g.cohort == REF]
        for c in COHORTS + ["2010-2024"]:
            if c == REF:
                continue
            g1 = g[g.cohort.isin(RECIENTE)] if c == "2010-2024" else g[g.cohort == c]
            for name, y in ys.items():
                est, lo, hi = _boot_diff(g1[y].astype(float).values, g0[y].astype(float).values,
                                         seed=0)
                rows.append({"country_frame": cf, "cohorte": c, "vs": REF, "variable": name,
                             "diferencia": est, "lo": lo, "hi": hi, "n1": len(g1), "n0": len(g0)})
    return pd.DataFrame(rows)


def by_year(d: pd.DataFrame) -> pd.DataFrame:
    g = d.groupby(["country_frame", "year"])
    return pd.DataFrame({"n": g.size(), "feliz": g.y_feliz.mean(), "tragico": g.y_tragico.mean(),
                         "optimismo": g.optimismo_personajes.mean(), "tono": g.tono_general.mean()}).reset_index()


def covariates(d: pd.DataFrame) -> pd.DataFrame:
    """Composición por cohorte de las variables del módulo B (proporciones)."""
    rows = []
    for var in ["genero_protagonista", "edad_protagonista", "momento_vital", "estado_civil", "clase_social",
                "especulativa", "epoca_trama", "humor"]:
        t = d.groupby(["country_frame", "cohort"])[var].value_counts(normalize=True).rename("prop").reset_index()
        t = t.rename(columns={var: "valor"})
        t["variable"] = var
        rows.append(t)
    rel = d.groupby(["country_frame", "cohort"])[[f"rel_{r.lower()}" for r in RELACIONES]].mean()
    rel = rel.stack().rename("prop").reset_index().rename(columns={"level_2": "valor"})
    rel["variable"] = "relaciones_centrales"
    rel["valor"] = rel.valor.str.replace("rel_", "").str.upper()
    rows.append(rel)
    # países de la trama (anotador A; proporción de películas que mencionan cada país)
    p = d[["country_frame", "cohort", "paises_trama_A"]].copy()
    p["pais"] = p.paises_trama_A.fillna("").str.split("|")
    p = p.explode("pais")
    tot = d.groupby(["country_frame", "cohort"]).size()
    pc = p.groupby(["country_frame", "cohort", "pais"]).size().div(tot).rename("prop").reset_index()
    pc = pc.rename(columns={"pais": "valor"})
    pc["variable"] = "paises_trama"
    rows.append(pc[pc.prop >= 0.02])
    return pd.concat(rows, ignore_index=True)[["variable", "country_frame", "cohort", "valor", "prop"]]


def subgroups(d: pd.DataFrame) -> pd.DataFrame:
    """¿Dónde creció o decreció el optimismo? Diferencia 2010-2024 − 1990-1999 dentro de cada subgrupo (EE. UU.)."""
    us = d[d.country_frame == "US"]
    specs = {"genre_main": None, "especulativa": None, "clase_social": None, "momento_vital": None,
             "genero_protagonista": None, "edad_protagonista": None, "estado_civil": None, "humor": None,
             "contemporanea": {1.0: "Contemporánea", 0.0: "De época, futura o ficticia"}}
    rows = []
    for var, lab in specs.items():
        for val, g in us.groupby(var):
            g0, g1 = g[g.cohort == REF], g[g.cohort.isin(RECIENTE)]
            if len(g0) < 25 or len(g1) < 25:
                continue
            for name, y in (("feliz", "y_feliz"), ("optimismo", "optimismo_personajes"), ("tono", "tono_general")):
                est, lo, hi = _boot_diff(g1[y].astype(float).values, g0[y].astype(float).values,
                                         seed=0)
                rows.append({"variable": var, "valor": lab.get(val, val) if lab else val, "medida": name,
                             "n_1990s": len(g0), "n_2010_24": len(g1), "nivel_1990s": g0[y].mean(),
                             "nivel_2010_24": g1[y].mean(), "diferencia": est, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


def final_vs_mood(d: pd.DataFrame) -> pd.DataFrame:
    c = d[d.clasificable]
    t = c.groupby(["country_frame", "final"]).agg(n=("tconst", "size"), optimismo=("optimismo_personajes", "mean"),
                                                   pct_optimistas=("y_optimistas", "mean"),
                                                   tono=("tono_general", "mean"),
                                                   pct_tono_pos=("y_tono_pos", "mean")).reset_index()
    return t


def imdb_relations(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Relación con la nota y los votos de IMDb, solo en agregado (no se publican valores por película)."""
    c = d[d.clasificable].copy()
    agg = c.groupby(["country_frame", "final"]).agg(n=("tconst", "size"), nota_media=("averageRating", "mean"),
                                                     votos_mediana=("numVotes", "median")).reset_index()
    for cf in ("US", "ES"):
        g = d[d.country_frame == cf]
        for lvl in (-2, -1, 0, 1, 2):
            s = g[g.optimismo_personajes.round() == lvl]
            agg = pd.concat([agg, pd.DataFrame([{"country_frame": cf, "final": f"optimismo_{lvl:+d}", "n": len(s),
                                                 "nota_media": s.averageRating.mean(),
                                                 "votos_mediana": s.numVotes.median()}])])
    models = []
    for cf in ("US", "ES"):
        g = d[(d.country_frame == cf) & d.clasificable].dropna(subset=["optimismo_personajes", "averageRating"]).copy()
        g["logv"] = np.log(g.numVotes)
        for y in ("averageRating", "logv"):
            for x in ("y_feliz", "optimismo_personajes", "tono_general"):
                m = smf.ols(f"{y} ~ {x} + C(year) + C(genre_main)", data=g).fit(cov_type="HC3")
                models.append({"country_frame": cf, "resultado": y, "predictor": x, "coef": m.params[x],
                               "lo": m.conf_int().loc[x, 0], "hi": m.conf_int().loc[x, 1], "n": int(m.nobs)})
    return agg, pd.DataFrame(models)


def adjusted(d: pd.DataFrame) -> pd.DataFrame:
    """Modelos ajustados en EE. UU.: efecto de cohorte (vs 1990s) sobre feliz (logit, AME por g-computación) y sobre
    optimismo (OLS), controlando género, popularidad y características de protagonista y trama."""
    us = d[(d.country_frame == "US") & d.clasificable].dropna(subset=["optimismo_personajes"]).copy()
    us["cohort"] = pd.Categorical(us.cohort, COHORTS)
    for v in ("clase_social", "momento_vital", "genero_protagonista", "humor", "genre_main"):
        vc = us[v].value_counts()
        rare = us[v].map(vc) < 30
        # categorías raras agrupadas en OTRO; si OTRO sigue siendo raro, se suma a la categoría modal (convergencia)
        us[v] = us[v].where(~rare, "OTRO" if rare.sum() >= 30 else vc.index[0])
    base = "C(cohort, Treatment('1990-1999')) + C(genre_main) + log_rank"
    extra = " + especulativa_si + contemporanea + C(clase_social) + C(momento_vital) + C(genero_protagonista) + C(humor)"
    rows = []
    for spec, f in (("genero+popularidad", base), ("+protagonista y trama", base + extra)):
        m = smf.logit(f"y_feliz ~ {f}", data=us).fit(disp=0, maxiter=200)
        for c in COHORTS:
            if c == REF:
                continue
            p1 = m.predict(us.assign(cohort=pd.Categorical([c] * len(us), COHORTS))).mean()
            p0 = m.predict(us.assign(cohort=pd.Categorical([REF] * len(us), COHORTS))).mean()
            name = f"C(cohort, Treatment('1990-1999'))[T.{c}]"
            lo, hi = m.conf_int().loc[name]
            rows.append({"modelo": spec, "resultado": "feliz (AME, pp)", "cohorte": c, "estimacion": p1 - p0,
                         "coef_logit": m.params[name], "coef_lo": lo, "coef_hi": hi, "n": int(m.nobs)})
        o = smf.ols(f"optimismo_personajes ~ {f}", data=us).fit(cov_type="HC3")
        for c in COHORTS:
            if c == REF:
                continue
            name = f"C(cohort, Treatment('1990-1999'))[T.{c}]"
            rows.append({"modelo": spec, "resultado": "optimismo personajes (puntos)", "cohorte": c,
                         "estimacion": o.params[name], "coef_logit": np.nan, "coef_lo": o.conf_int().loc[name, 0],
                         "coef_hi": o.conf_int().loc[name, 1], "n": int(o.nobs)})
    return pd.DataFrame(rows)


def sensitivity(d: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def add(label, g, y="y_feliz"):
        for cf, gg in g.groupby("country_frame"):
            est, lo, hi = _boot_diff(gg[gg.cohort.isin(RECIENTE)][y].astype(float).values,
                                     gg[gg.cohort == REF][y].astype(float).values, seed=0)
            rows.append({"analisis": label, "country_frame": cf, "medida": y, "diferencia_2010_24_vs_1990s": est,
                         "lo": lo, "hi": hi, "n": len(gg)})
    add("Principal", d)
    add("Solo anotador A", d, "y_feliz_A")
    add("Solo anotador B", d, "y_feliz_B")
    add("Excluye películas reconocidas", d[d.reconocida != True])
    add("Solo producciones solo de EE. UU.", d[(d.country_frame == "ES") | (d.us_only == True)])
    add("Excluye películas del estudio v1", d[d.etapa_v2 != "v2_modb"])
    es = d[d.country_frame == "ES"]
    add("ES: solo sinopsis en inglés", es[es.sinopsis_idioma == "en"])
    add("ES: solo sinopsis en español", es[es.sinopsis_idioma == "es"])
    o = es.copy()
    m = o.final_es_original.notna()
    o.loc[m, "y_feliz"] = np.where(o.loc[m, "final_es_original"] == "FELIZ", 1.0,
                                   np.where(o.loc[m, "final_es_original"] == "NO_CLASIFICABLE", np.nan, 0.0))
    add("ES: sin la reanotación D-027", o)
    add("Principal (optimismo)", d, "optimismo_personajes")
    add("Solo anotador A (optimismo)", d, "optimismo_personajes_A")
    add("Solo anotador B (optimismo)", d, "optimismo_personajes_B")
    return pd.DataFrame(rows)


def genre(d: pd.DataFrame) -> pd.DataFrame:
    us = d[(d.country_frame == "US")]
    t = us.groupby(["genre_main", "cohort"]).agg(n=("tconst", "size"), feliz=("y_feliz", "mean"),
                                                 optimismo=("optimismo_personajes", "mean")).reset_index()
    return t


def run() -> dict:
    TABLES.mkdir(parents=True, exist_ok=True)
    d = load()
    d_nodup = d  # las coproducciones EE. UU.-España cuentan en ambos universos (12 películas)
    out = {}
    for name, df in (("por_cohorte", by_cohort(d_nodup)), ("por_anio", by_year(d)), ("contrastes", contrasts(d)),
                     ("covariables", covariates(d)), ("subgrupos", subgroups(d)), ("final_vs_animo", final_vs_mood(d)),
                     ("ajustados", adjusted(d)), ("sensibilidad", sensitivity(d)), ("genero", genre(d))):
        df.to_csv(TABLES / f"{name}.csv", index=False, float_format="%.4f")
        out[name] = df
    agg, mod = imdb_relations(d)
    agg.to_csv(TABLES / "imdb_agregado.csv", index=False, float_format="%.3f")
    mod.to_csv(TABLES / "imdb_modelos.csv", index=False, float_format="%.4f")
    out["imdb_agregado"], out["imdb_modelos"] = agg, mod
    S = story(d)

    def conv(o):
        if isinstance(o, dict):
            return {k: conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        if isinstance(o, (float, np.floating)):
            return None if np.isnan(o) else round(float(o), 4)
        if isinstance(o, np.integer):
            return int(o)
        return o
    (TABLES / "historia_web.json").write_text(json.dumps(conv(S), ensure_ascii=False, indent=0), encoding="utf-8")
    return out


if __name__ == "__main__":
    o = run()
    pd.set_option("display.width", 220)
    print(o["por_cohorte"][["country_frame", "cohort", "n", "pct_no_clasificable", "feliz", "feliz_lo", "feliz_hi",
                            "tragico", "optimismo", "tono", "tragedia_vitalista"]].round(3).to_string())
    c = o["contrastes"]
    print(c[c.cohorte == "2010-2024"].round(3).to_string())
    print(o["sensibilidad"].round(3).to_string())
    print(o["ajustados"].round(3).to_string())
    print(o["final_vs_animo"].round(2).to_string())
    print(o["imdb_modelos"].round(3).to_string())


# ------------------------------------------------------------------ agregados para la historia de la web (estudio unificado)
POS_TONE = ["ESPERANZA", "ALIVIO", "CONEXION"]
PERIODS = {"1990-1999": ["1990-1999"], "2010-2024": RECIENTE}


def _prep_story(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    cl = d.clasificable
    d["y_amplia"] = d.final.isin(["FELIZ", "AGRIDULCE"]).astype(float).where(cl)
    d["y_estricta"] = ((d.final == "FELIZ") & d.tono_cierre.isin(POS_TONE)).astype(float).where(cl)
    d["y_incl_nc"] = (d.final == "FELIZ").astype(float)
    d["y_tono_positivo"] = d.tono_cierre.isin(POS_TONE).astype(float).where(d.tono_cierre != "NO_CLARO")
    d["periodo"] = np.where(d.cohort == "1990-1999", "1990-1999", np.where(d.cohort.isin(RECIENTE), "2010-2024", "otro"))
    return d


def _est(g: pd.DataFrame, y: str) -> list:
    x = g[y].dropna().astype(float).values
    if len(x) == 0:
        return [np.nan, np.nan, np.nan, 0]
    if set(np.unique(x)) <= {0.0, 1.0}:
        p, lo, hi = st.wilson(int(x.sum()), len(x))
    else:
        p, lo, hi = st.mean_ci(x)
    return [p, lo, hi, len(x)]


def _wboot(d1, d0, y, w, n_boot=2000, seed=0):
    a, b = d1.dropna(subset=[y]), d0.dropna(subset=[y])
    rng = np.random.default_rng(seed)
    f = lambda g: np.average(g[y], weights=g[w])
    est = f(a) - f(b)
    bs = []
    for _ in range(n_boot):
        bs.append(f(a.iloc[rng.integers(0, len(a), len(a))]) - f(b.iloc[rng.integers(0, len(b), len(b))]))
    return est, *np.percentile(bs, [2.5, 97.5])


def _ame_boot(g: pd.DataFrame, extra: str = "", n_boot: int = 200, seed: int = 0):
    g = g[g.clasificable].copy()
    for v in ("clase_social", "momento_vital", "genero_protagonista", "humor", "genre_main"):
        vc = g[v].value_counts()
        rare = g[v].map(vc) < 30
        g[v] = g[v].where(~rare, "OTRO" if rare.sum() >= 30 else vc.index[0])
    g = g[g.periodo != "otro"].copy()
    g["reciente"] = (g.periodo == "2010-2024").astype(int)
    f = "y_feliz ~ reciente + C(genre_main) + log_rank" + extra

    def ame(data):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = smf.logit(f, data=data).fit(disp=0, maxiter=200)
        return m.predict(data.assign(reciente=1)).mean() - m.predict(data.assign(reciente=0)).mean()
    est = ame(g)
    rng = np.random.default_rng(seed)
    bs = []
    for _ in range(n_boot):
        try:
            bs.append(ame(g.iloc[rng.integers(0, len(g), len(g))]))
        except Exception:
            pass
    return est, *np.percentile(bs, [2.5, 97.5])


def story(d: pd.DataFrame) -> dict:
    d = _prep_story(d)
    out = {"cohortes": {}, "periodos": {}, "sens": {}, "genero": {}, "accion": {}}
    ys = ["y_feliz", "y_agridulce", "y_ambiguo", "y_tragico", "y_tono_positivo", "vision_vida",
          "optimismo_personajes", "tono_general", "y_nf_opt"]
    for cf, g in d.groupby("country_frame"):
        out["cohortes"][cf] = {y: [_est(g[g.cohort == c], y) for c in COHORTS] for y in ys}
        out["periodos"][cf] = {y: {p: _est(g[g.periodo == p], y) for p in PERIODS} for y in ys}
        g0, g1 = g[g.periodo == "1990-1999"], g[g.periodo == "2010-2024"]

        def diff(y, a=g1, b=g0):
            return list(_boot_diff(a[y].astype(float).values, b[y].astype(float).values, seed=0))
        top = 20 if cf == "US" else 10
        rows = [("Análisis principal", diff("y_feliz")),
                ("Feliz o agridulce", diff("y_amplia")),
                ("Feliz y con cierre positivo", diff("y_estricta")),
                ("Contando los no clasificables", diff("y_incl_nc")),
                ("Pesando más las más votadas", list(_wboot(g1, g0, "y_feliz", "numVotes"))),
                ("Solo el anotador A", diff("y_feliz_A")),
                ("Solo el anotador B", diff("y_feliz_B")),
                ("Solo si ambos coinciden", diff("y_feliz", g1[g1.final_A == g1.final_B], g0[g0.final_A == g0.final_B])),
                ("Solo casos muy claros", diff("y_feliz", g1[g1.confianza_min == 3], g0[g0.confianza_min == 3])),
                (f"Solo las {top} más votadas/año", diff("y_feliz", g1[g1.votes_rank_in_year <= top], g0[g0.votes_rank_in_year <= top])),
                ("Ajustado por género y popularidad", list(_ame_boot(g)))]
        if cf == "US":
            rows.insert(10, ("Sin coproducciones", diff("y_feliz", g1[g1.us_only == True], g0[g0.us_only == True])))
            rows.append(("Ajustado + protagonista y trama", list(_ame_boot(
                g, " + especulativa_si + contemporanea + C(clase_social) + C(momento_vital) + C(genero_protagonista) + C(humor)"))))
        else:
            rows.insert(10, ("Solo sinopsis en inglés", diff("y_feliz", g1[g1.sinopsis_idioma == "en"], g0[g0.sinopsis_idioma == "en"])))
            rows.insert(11, ("Solo sinopsis en español", diff("y_feliz", g1[g1.sinopsis_idioma == "es"], g0[g0.sinopsis_idioma == "es"])))
        out["sens"][cf] = [[k] + [None if pd.isna(x) else float(x) for x in v] for k, v in rows]
        comp = {}
        for p in PERIODS:
            gp = g[g.periodo == p]
            comp[p] = gp.genre_main.value_counts(normalize=True).to_dict()
        gen = []
        for ge, gg in g.groupby("genre_main"):
            a, b = gg[gg.periodo == "2010-2024"], gg[gg.periodo == "1990-1999"]
            if b.y_feliz.notna().sum() >= 10 and a.y_feliz.notna().sum() >= 10:
                dd = _boot_diff(a.y_feliz.values, b.y_feliz.values, seed=0)
                gen.append([ge, int(b.y_feliz.notna().sum()), int(a.y_feliz.notna().sum()), b.y_feliz.mean(), a.y_feliz.mean(), *dd])
        out["genero"][cf] = {"composicion": comp, "felices": gen}
        ac = g[g.genre_main == "Acción/aventura"]
        grp = {"1980-1999": ac[ac.cohort.isin(["1980-1989", "1990-1999"])], "1980-1989": ac[ac.cohort == "1980-1989"],
               "1990-1999": ac[ac.cohort == "1990-1999"], "2010-2024": ac[ac.periodo == "2010-2024"]}
        out["accion"][cf] = {k: _est(v, "y_feliz") for k, v in grp.items()}
    return out
