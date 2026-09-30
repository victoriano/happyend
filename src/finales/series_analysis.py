"""D-037: etiquetas finales, adjudicación y análisis de las series."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from . import annotation as an
from . import stats as st
from .analysis_v2 import _boot_diff, _est, _wboot
from .clean import primary_genre
from .config import INTERIM, ROOT, load
from .series import SER

ANNOT = ROOT / "annotation"
KEY = ANNOT / "claves" / "series_key.csv"
TAB = ROOT / "reports" / "tables" / "series"
COHORTS = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2025"]
REF, REC = "1990-1999", ["2010-2019", "2020-2025"]
FIN4 = ["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"]


def _ab():
    A, ea = an.load_labels_series(sorted((ANNOT / "labels" / "series" / "A").glob("*.jsonl")), "A")
    B, eb = an.load_labels_series(sorted((ANNOT / "labels" / "series" / "B").glob("*.jsonl")), "B")
    if ea or eb:
        raise ValueError((ea + eb)[:5])
    return A.merge(B, on="id", suffixes=("_A", "_B"))


def _diff(r) -> list[str]:
    d = []
    if r["final_A"] != r["final_B"]:
        d.append("final")
    for k in ("feel_good", "utopia"):
        a, b = r[f"{k}_A"], r[f"{k}_B"]
        if pd.notna(a) != pd.notna(b) or (pd.notna(a) and abs(a - b) >= 3):
            d.append(k)
    if r["publico_A"] != r["publico_B"]:
        d.append("publico")
    return d


def make_adjudication(seed: int = 20260930, batch_size: int = 40) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    m = _ab()
    texts = {}
    for f in (ANNOT / "batches" / "series").glob("*.jsonl"):
        for l in f.read_text(encoding="utf-8").splitlines():
            x = json.loads(l)
            texts[x["id"]] = x["sinopsis"]
    show = ["alcance", "final", "nota_final", "feel_good", "feel_good_por_que", "utopia", "utopia_por_que", "publico"]
    nn = lambda v: None if isinstance(v, float) and pd.isna(v) else (int(v) if isinstance(v, float) else v)
    rows = []
    for r in m.to_dict("records"):
        d = _diff(r)
        if not d:
            continue
        la, lb = {k: nn(r[f"{k}_A"]) for k in show}, {k: nn(r[f"{k}_B"]) for k in show}
        sw = bool(rng.integers(0, 2))
        x, y = (lb, la) if sw else (la, lb)
        rows.append({"id": r["id"], "sinopsis": texts[r["id"]], "etiqueta_X": x, "etiqueta_Y": y,
                     "campos_en_desacuerdo": d, "_swap": sw})
    df = pd.DataFrame(rows).sort_values("id").reset_index(drop=True)
    df["_batch"] = [f"series_adj_{i // batch_size + 1:02d}" for i in range(len(df))]
    out = ANNOT / "batches" / "series_adjudicacion"
    out.mkdir(parents=True, exist_ok=True)
    for b, g in df.groupby("_batch"):
        with open(out / f"{b}.jsonl", "w", encoding="utf-8") as fh:
            for rec in g.drop(columns=["_swap", "_batch"]).to_dict("records"):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    df[["id", "_swap", "_batch"]].to_csv(ANNOT / "claves" / "series_adjudicacion_key.csv", index=False)
    return df


def validate_adjudication(path: Path, batch_path: Path) -> list[str]:
    need = {json.loads(l)["id"]: set(json.loads(l)["campos_en_desacuerdo"])
            for l in Path(batch_path).read_text(encoding="utf-8").splitlines() if l.strip()}
    errs, seen = [], set()
    for ln, l in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not l.strip():
            continue
        try:
            d = json.loads(l)
        except json.JSONDecodeError as e:
            errs.append(f"línea {ln}: {e}")
            continue
        i = d.get("id")
        if i not in need:
            errs.append(f"id desconocido {i}")
            continue
        seen.add(i)
        if need[i] - set(d):
            errs.append(f"{i}: faltan {sorted(need[i] - set(d))}")
        if "final" in need[i] and d.get("final") not in an.FINALES_S:
            errs.append(f"{i}: final={d.get('final')!r}")
        for k in ("feel_good", "utopia"):
            if k in need[i]:
                v = d.get(k)
                if not (v is None or (isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 10)):
                    errs.append(f"{i}: {k}={v!r}")
                if not isinstance(d.get(f"{k}_por_que"), str) or len(d[f"{k}_por_que"].split()) < 10:
                    errs.append(f"{i}: falta {k}_por_que")
        if "publico" in need[i] and d.get("publico") not in an.PUBLICO:
            errs.append(f"{i}: publico={d.get('publico')!r}")
    if set(need) - seen:
        errs.append(f"faltan ids {sorted(set(need) - seen)[:5]}")
    return errs


def labels() -> pd.DataFrame:
    m = _ab()
    rows = []
    for f in sorted((ANNOT / "labels" / "series_adjudicacion").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    adj = pd.DataFrame(rows).set_index("id") if rows else pd.DataFrame()
    key = pd.read_csv(KEY)[["id", "tconst", "idioma"]]
    m = m.merge(key, on="id")
    out = []
    for r in m.to_dict("records"):
        i = r["id"]
        d = {"tconst": r["tconst"], "id_s": i, "sinopsis_idioma": r["idioma"]}
        dif = _diff(r)
        ok = lambda k: i in adj.index and k in adj.columns and not (isinstance(adj.at[i, k], float) and pd.isna(adj.at[i, k]) and k not in ("feel_good", "utopia"))
        # final
        if "final" not in dif:
            d["final"], d["final_fuente"] = r["final_A"], "acuerdo"
        elif ok("final") and isinstance(adj.at[i, "final"], str):
            d["final"], d["final_fuente"] = adj.at[i, "final"], "adjudicado"
        else:
            d["final"], d["final_fuente"] = r["final_A"], "regla_A"
        for k in ("feel_good", "utopia"):
            a, b = r[f"{k}_A"], r[f"{k}_B"]
            d[f"{k}_A"], d[f"{k}_B"] = a, b
            d[f"{k}_por_que_A"], d[f"{k}_por_que_B"] = r[f"{k}_por_que_A"], r[f"{k}_por_que_B"]
            d[f"{k}_por_que_J"] = None
            if k not in dif:
                d[k], d[f"{k}_fuente"] = ((a + b) / 2 if pd.notna(a) else np.nan), "media"
            elif i in adj.index and k in adj.columns:
                v = adj.at[i, k]
                d[k] = float(v) if v is not None and pd.notna(v) else np.nan
                d[f"{k}_fuente"] = "adjudicado"
                d[f"{k}_por_que_J"] = adj.at[i, f"{k}_por_que"] if f"{k}_por_que" in adj.columns else None
            else:
                d[k], d[f"{k}_fuente"] = np.nan, "sin_resolver"
        if "publico" not in dif:
            d["publico"] = r["publico_A"]
        elif i in adj.index and "publico" in adj.columns and isinstance(adj.at[i, "publico"], str):
            d["publico"] = adj.at[i, "publico"]
        else:
            d["publico"] = r["publico_A"]
        for k in ("optimismo_personajes", "tono_general"):
            a, b = r[f"{k}_A"], r[f"{k}_B"]
            d[k] = (a + b) / 2 if pd.notna(a) and pd.notna(b) else np.nan
        d["alcance_A"], d["alcance_B"] = r["alcance_A"], r["alcance_B"]
        d["con_final"] = r["alcance_A"] == "FINAL" and r["alcance_B"] == "FINAL"
        d["solo_premisa"] = r["alcance_A"] == "PREMISA" and r["alcance_B"] == "PREMISA"
        d["nota_final_A"], d["nota_final_B"] = r["nota_final_A"], r["nota_final_B"]
        d["final_A"], d["final_B"] = r["final_A"], r["final_B"]
        d["reconocida"] = bool(r["reconocida_A"]) or bool(r["reconocida_B"])
        d["confianza_c_min"] = min(r["confianza_c_A"], r["confianza_c_B"])
        out.append(d)
    lab = pd.DataFrame(out)
    # D-039: ajustes manuales documentados (fuera del método ciego)
    aj = ROOT / "annotation" / "ajustes" / "series_manual.csv"
    if aj.exists():
        for r in pd.read_csv(aj).itertuples():
            m = lab.tconst == r.tconst
            lab.loc[m, "feel_good"] = float(r.feel_good)
            lab.loc[m, "feel_good_fuente"] = "manual"
            lab.loc[m, "feel_good_por_que_M"] = r.feel_good_por_que
    return lab


def analytic() -> pd.DataFrame:
    cfg = load()
    u = pd.read_csv(SER / "universo_series.csv")
    u["cohort"] = pd.cut(u.year, [1979, 1989, 1999, 2009, 2019, 2025, 2030], labels=COHORTS + ["2026 (en curso)"]).astype(str)
    u["genre_main"] = u.genres.apply(lambda g: primary_genre(g, cfg["genero_principal_prioridad"], cfg["genero_resto"]))
    lab = labels()
    d = u.merge(lab, on="tconst", how="left")
    for c in ("solo_premisa", "con_final", "reconocida"):
        d[c] = d[c].fillna(False).astype(bool)
    d["clasificable"] = d.final.isin(FIN4)
    d["y_feliz"] = np.where(d.clasificable, (d.final == "FELIZ").astype(float), np.nan)
    d["y_tragico"] = np.where(d.clasificable, (d.final == "TRAGICO").astype(float), np.nan)
    d["y_fg7"] = (d.feel_good >= 7).astype(float).where(d.feel_good.notna())
    d["infantil_familiar"] = d.publico.isin(["INFANTIL", "FAMILIAR"])
    d["log_rank"] = np.log(d.votes_rank_in_year)
    d["wiki"] = d.sinopsis_idioma.notna() & (d.sinopsis_idioma != "tmdb")
    d.to_csv(SER / "analitico_series.csv", index=False)
    print("series", len(d), d.feel_good.notna().sum())
    return d


def story(d: pd.DataFrame) -> dict:
    d = d[d.anio_en_curso != True].copy()
    d["periodo"] = np.where(d.cohort == REF, REF, np.where(d.cohort.isin(REC), "2010-2025", "otro"))
    out = {"cohortes": {}, "periodos": {}, "diff": {}, "sens": {}, "anual": {}, "genero": {}, "publico": {}, "alcance": {}, "n": {}}
    ys = ["feel_good", "y_fg7", "utopia", "y_feliz", "y_tragico", "optimismo_personajes", "tono_general"]
    for cf, g in d.groupby("country_frame"):
        out["n"][cf] = {"total": len(g), "con_fg": int(g.feel_good.notna().sum()), "clasificables": int(g.clasificable.sum())}
        out["cohortes"][cf] = {y: [_est(g[g.cohort == c], y) for c in COHORTS] for y in ys}
        out["cohortes"][cf]["n"] = [int((g.cohort == c).sum()) for c in COHORTS]
        out["periodos"][cf] = {y: {p: _est(g[g.periodo == p], y) for p in (REF, "2010-2025")} for y in ys}
        g0, g1 = g[g.periodo == REF], g[g.periodo == "2010-2025"]
        diff = lambda y, a=g1, b=g0: list(_boot_diff(a[y].astype(float).values, b[y].astype(float).values, seed=0))
        out["diff"][cf] = {y: diff(y) for y in ys}
        out["diff"][cf]["por_cohorte"] = {c: {y: list(_boot_diff(g[g.cohort == c][y].astype(float).values, g0[y].astype(float).values, seed=0))
                                              for y in ("feel_good", "y_fg7", "utopia", "y_feliz")} for c in COHORTS if c != REF}
        both = lambda x: x[(x.feel_good_A - x.feel_good_B).abs() < 3]
        rows = [("Análisis principal", diff("feel_good")), ("Solo el anotador A", diff("feel_good_A")),
                ("Solo el anotador B", diff("feel_good_B")), ("Solo si A y B coinciden (±2)", diff("feel_good", both(g1), both(g0))),
                ("Sin las que solo tienen premisa", diff("feel_good", g1[~g1.solo_premisa], g0[~g0.solo_premisa])),
                ("Solo sinopsis de Wikipedia", diff("feel_good", g1[g1.wiki], g0[g0.wiki])),
                ("Sin series infantiles y familiares", diff("feel_good", g1[~g1.infantil_familiar], g0[~g0.infantil_familiar])),
                ("Solo las 10 más votadas/año", diff("feel_good", g1[g1.votes_rank_in_year <= 10], g0[g0.votes_rank_in_year <= 10]))]
        try:
            rows.append(("Pesando más las más votadas", list(_wboot(g1, g0, "feel_good", "numVotes"))))
        except Exception:
            pass
        try:
            h = g[g.periodo != "otro"].dropna(subset=["feel_good"]).copy()
            h["reciente"] = (h.periodo == "2010-2025").astype(int)
            vc = h.genre_main.value_counts()
            h["genre_main"] = h.genre_main.where(h.genre_main.map(vc) >= 15, "Otros")
            mm = smf.ols("feel_good ~ reciente + C(genre_main) + log_rank", data=h).fit(cov_type="HC3")
            rows.append(("Ajustado por género y popularidad", [mm.params["reciente"], *mm.conf_int().loc["reciente"].tolist()]))
        except Exception:
            pass
        out["sens"][cf] = [[k] + [None if pd.isna(x) else float(x) for x in v] for k, v in rows]
        yy = g.groupby("year").agg(n=("tconst", "size"), fg=("feel_good", "mean"), fg7=("y_fg7", "mean"),
                                   ut=("utopia", "mean"), feliz=("y_feliz", "mean")).reset_index()
        out["anual"][cf] = yy.values.tolist()
        gen = []
        for ge, gg in g.groupby("genre_main"):
            a, b = gg[gg.periodo == "2010-2025"], gg[gg.periodo == REF]
            if b.feel_good.notna().sum() >= 8 and a.feel_good.notna().sum() >= 8:
                gen.append([ge, int(b.feel_good.notna().sum()), int(a.feel_good.notna().sum()), b.feel_good.mean(),
                            a.feel_good.mean(), *_boot_diff(a.feel_good.values, b.feel_good.values, seed=0)])
        out["genero"][cf] = gen
        out["publico"][cf] = {c: g[g.cohort == c].publico.value_counts(normalize=True).to_dict() for c in COHORTS}
        out["alcance"][cf] = {c: g[g.cohort == c].alcance_A.value_counts(normalize=True).to_dict() for c in COHORTS}
        # composición por género y efecto de composición (2010-2025 reponderado a la mezcla de géneros de los noventa)
        out.setdefault("composicion", {})[cf] = {p: g[g.periodo == p].genre_main.value_counts(normalize=True).to_dict() for p in (REF, "2010-2025")}
        w90 = g0.genre_main.value_counts(normalize=True)
        m1 = g1.groupby("genre_main").feel_good.mean()
        rew = float(sum(w90.get(k, 0) * m1.get(k, np.nan) for k in w90.index if k in m1.index) / sum(w90.get(k, 0) for k in w90.index if k in m1.index))
        out.setdefault("reponderado", {})[cf] = {"m90": float(g0.feel_good.mean()), "m_rec": float(g1.feel_good.mean()), "m_rec_mezcla90": rew}
        # subgrupos
        sub = []
        g["tipo_serie"] = np.where(g.titleType == "tvMiniSeries", "Miniserie", "Serie")
        g0, g1 = g[g.periodo == REF], g[g.periodo == "2010-2025"]
        for var in ("genre_main", "alcance_A", "publico", "tipo_serie"):
            for val, gg in g.groupby(var):
                a0, a1 = gg[gg.periodo == REF], gg[gg.periodo == "2010-2025"]
                if a0.feel_good.notna().sum() >= 12 and a1.feel_good.notna().sum() >= 12:
                    sub.append([var, str(val), int(a0.feel_good.notna().sum()), int(a1.feel_good.notna().sum()), a0.feel_good.mean(),
                                a1.feel_good.mean(), *_boot_diff(a1.feel_good.values, a0.feel_good.values, seed=0)])
        out.setdefault("subgrupos", {})[cf] = sub
        # final × feel good
        fb = pd.cut(g.feel_good, [-0.1, 2.49, 4.49, 6.49, 8.49, 10], labels=[0, 1, 2, 3, 4]).astype(float)
        cc = g[g.clasificable & fb.notna()]
        out.setdefault("matriz_fg", {})[cf] = pd.crosstab(cc.final, fb[cc.index]).reindex(index=FIN4, columns=[0.0, 1.0, 2.0, 3.0, 4.0]).fillna(0).astype(int).values.tolist()
        out.setdefault("hist", {})[cf] = {c: np.bincount(g[g.cohort == c].feel_good.dropna().round().astype(int), minlength=11).tolist() for c in COHORTS}
    # comparación con películas (EE. UU. y España, mismas cohortes)
    f = pd.read_csv(INTERIM / "analitico_v2.csv")
    f = f[f.anio_en_curso != True]
    out["peliculas"] = {cf: {"feel_good": [_est(g[g.cohort == c], "feel_good") for c in COHORTS],
                             "y_fg7": [_est(g[g.cohort == c], "y_fg7") for c in COHORTS],
                             "y_feliz": [_est(g[g.cohort == c], "y_feliz") for c in COHORTS],
                             "utopia": [_est(g[g.cohort == c], "utopia") for c in COHORTS],
                             "anual": g.groupby("year").feel_good.mean().reset_index().values.tolist()}
                        for cf, g in f.groupby("country_frame")}
    return out


def run() -> dict:
    TAB.mkdir(parents=True, exist_ok=True)
    d = analytic()
    S = story(d)

    def conv(o):
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        if isinstance(o, (float, np.floating)):
            return None if not np.isfinite(o) else round(float(o), 4)
        if isinstance(o, (np.integer,)):
            return int(o)
        return o
    (TAB / "historia_series.json").write_text(json.dumps(conv(S), ensure_ascii=False), encoding="utf-8")
    m = _ab()
    from .agreement import cohen_kappa, krippendorff_alpha
    agr = {}
    for k in ("feel_good", "utopia"):
        pr = m[[f"{k}_A", f"{k}_B"]].dropna()
        agr[f"alfa_{k}"] = krippendorff_alpha([list(x) for x in zip(pr[f"{k}_A"], pr[f"{k}_B"])], "interval")
        agr[f"dentro2_{k}"] = float(((pr[f"{k}_A"] - pr[f"{k}_B"]).abs() <= 2).mean())
    agr["kappa_final"] = cohen_kappa(m.final_A, m.final_B)
    agr["kappa_publico"] = cohen_kappa(m.publico_A, m.publico_B)
    lab = labels()
    agr["n"] = len(m)
    agr["n_adj"] = int(((lab.final_fuente == "adjudicado") | (lab.feel_good_fuente == "adjudicado") | (lab.utopia_fuente == "adjudicado")).sum())
    (TAB / "acuerdo_series.json").write_text(json.dumps(conv(agr), ensure_ascii=False), encoding="utf-8")
    print(json.dumps(conv(agr)))
    return S


if __name__ == "__main__":
    run()
