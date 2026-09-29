"""Versión 2 del estudio: censo del cine popular de EE. UU., cine español y módulo B de anotación.

Universos:
  US: las 50 películas con más votos de cada año (1980-2024) del catálogo estadounidense, con sinopsis ≥120 palabras.
  ES: las 15 películas españolas con más votos de cada año que tienen sinopsis (spain.select_universe_es).

Anotación:
  v2_completa  → películas sin etiquetas v1 con manual 1.0 (núcleo): núcleo + módulo B.
  v2_modb      → películas del estudio v1 (994): solo módulo B, con el mismo texto cegado que en v1.
Los identificadores cegados de v2_completa usan una sal distinta ("v2") para que no coincidan con los de v1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from . import blinding
from .annotation import ANNOT, KEY_DIR
from .config import DERIVED, INTERIM, load
from .wikidump import WIKIS, word_count


def blind_id_v2(tconst: str, seed: int) -> str:
    return "G" + hashlib.sha256(f"blind-v2|{seed}|{tconst}".encode()).hexdigest()[:8].upper()


def synopsis_for(tconst: str, prefer: str = "en") -> dict | None:
    order = [prefer, "en" if prefer == "es" else "es"]
    for w in order:
        p = WIKIS[w]["syn_dir"] / f"{tconst}.json"
        if p.exists():
            rec = json.loads(p.read_text(encoding="utf-8"))
            if word_count(rec.get("text")) >= load()["sinopsis"]["min_palabras"]:
                return rec
    return None


def universe() -> pd.DataFrame:
    """Une los dos universos y marca qué películas ya tienen anotación v1."""
    us = pd.read_csv(INTERIM / "catalog.csv")
    us = us[us.in_popular_universe].copy()
    us["country_frame"] = "US"
    us["synopsis_wiki"] = "en"
    es = pd.read_csv(INTERIM / "universo_es.csv")
    es["country_frame"] = "ES"
    cols = ["tconst", "primaryTitle", "originalTitle", "year", "cohort", "genres", "genre_main", "numVotes",
            "averageRating", "votes_rank_in_year", "countries", "us_only", "enwiki_url", "country_frame",
            "synopsis_wiki"]
    es = es.reindex(columns=cols + ["eswiki_url"])
    us = us.reindex(columns=cols + ["eswiki_url"])
    u = pd.concat([us, es], ignore_index=True)
    # Coproducciones EE. UU.-España pueden estar en ambos universos: se anotan una vez y cuentan en los dos.
    v1 = pd.read_csv(DERIVED / "muestra_principal.csv")
    u["in_v1"] = u.tconst.isin(v1.tconst)
    ok = []
    for r in u.itertuples():
        rec = synopsis_for(r.tconst, "es" if r.country_frame == "ES" else "en")
        ok.append(rec is not None and (r.country_frame == "ES" or rec.get("wiki", "en") == "en"))
    u["has_synopsis"] = ok
    return u


def _texts_v1() -> dict[str, tuple[str, str]]:
    """tconst → (id v1, texto cegado v1) a partir de los lotes versionados."""
    key = pd.read_csv(KEY_DIR / "principal_key.csv")
    id2t = dict(zip(key.id, key.tconst))
    out = {}
    for f in (ANNOT / "batches" / "principal").glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            out[id2t[d["id"]]] = (d["id"], d["sinopsis"])
    return out


def make_batches_v2(films: pd.DataFrame, stage: str, batch_size: int = 50, prefer: str | None = None,
                    id_fn=None) -> pd.DataFrame:
    """Lotes cegados para anotación completa (núcleo + módulo B).
    prefer fuerza el idioma de la sinopsis; id_fn permite otra familia de ids (p. ej. la reanotación D-027)."""
    id_fn = id_fn or blind_id_v2
    cfg = load()
    seed, maxw = cfg["project"]["seed"], cfg["sinopsis"]["max_palabras_anotacion"]
    out_dir = ANNOT / "batches" / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    recs = []
    for r in films.itertuples():
        syn = synopsis_for(r.tconst, prefer or ("es" if r.country_frame == "ES" else "en"))
        titles = blinding.title_variants(
            r.primaryTitle, r.originalTitle,
            r.enwiki_url.rsplit("/wiki/", 1)[-1] if isinstance(r.enwiki_url, str) else None,
            r.eswiki_url.rsplit("/wiki/", 1)[-1] if isinstance(r.eswiki_url, str) else None)
        text = blinding.mask(syn["text"], titles)
        text, trunc = blinding.truncate_words(text, maxw)
        recs.append({"id": id_fn(r.tconst, seed), "tconst": r.tconst, "sinopsis": text,
                     "idioma": syn.get("wiki", "en"), "palabras_originales": len(syn["text"].split()),
                     "truncada": trunc, "revision_url": syn.get("revision_url")})
    df = pd.DataFrame(recs).sort_values("id").reset_index(drop=True)
    df["batch"] = [f"{stage}_{i // batch_size + 1:02d}" for i in range(len(df))]
    for b, g in df.groupby("batch"):
        with open(out_dir / f"{b}.jsonl", "w", encoding="utf-8") as fh:
            for x in g.itertuples():
                fh.write(json.dumps({"id": x.id, "sinopsis": x.sinopsis}, ensure_ascii=False) + "\n")
    df.drop(columns=["sinopsis"]).to_csv(KEY_DIR / f"{stage}_key.csv", index=False)
    return df


def make_batches_modb(stage: str = "v2_modb", batch_size: int = 50) -> pd.DataFrame:
    """Lotes de solo módulo B para las películas v1, con el mismo id y texto cegado que en v1."""
    texts = _texts_v1()
    out_dir = ANNOT / "batches" / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = sorted(((i, t, tc) for tc, (i, t) in texts.items()), key=lambda x: x[0])
    recs = []
    for k, (i, t, tc) in enumerate(rows):
        b = f"{stage}_{k // batch_size + 1:02d}"
        recs.append({"id": i, "tconst": tc, "batch": b})
        with open(out_dir / f"{b}.jsonl", "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"id": i, "sinopsis": t}, ensure_ascii=False) + "\n")
    df = pd.DataFrame(recs)
    df.to_csv(KEY_DIR / f"{stage}_key.csv", index=False)
    return df


def blind_id_esen(tconst: str, seed: int) -> str:
    return "H" + hashlib.sha256(f"blind-esen|{seed}|{tconst}".encode()).hexdigest()[:8].upper()


def make_batches_esen() -> pd.DataFrame:
    """D-027: películas españolas cuya sinopsis en español no describe el final (NO_CLASIFICABLE) y que tienen
    sinopsis inglesa utilizable: se reanotan completas con la inglesa."""
    fb = pd.read_csv(INTERIM / "es_nc_en_fallback.csv")
    fb = fb[fb.palabras_en >= load()["sinopsis"]["min_palabras"]]
    u = pd.read_csv(INTERIM / "universo_v2.csv")
    films = u[(u.country_frame == "ES") & u.tconst.isin(fb.tconst)].drop_duplicates("tconst")
    return make_batches_v2(films, "v2_es_en", batch_size=45, prefer="en", id_fn=blind_id_esen)


def pilot_v2(u: pd.DataFrame, n_us: int = 15, n_es: int = 15, seed: int = 20260929) -> pd.DataFrame:
    """Piloto del módulo B: películas nuevas (sin v1) de ambos países, estratificadas por cohorte."""
    rng = np.random.default_rng(seed)
    cand = u[(~u.in_v1) & u.has_synopsis]
    picks = []
    for cf, n in (("US", n_us), ("ES", n_es)):
        c = cand[cand.country_frame == cf]
        per = max(1, n // c.cohort.nunique())
        for _, g in c.groupby("cohort"):
            picks.append(g.sample(min(per, len(g)), random_state=int(rng.integers(1e9))))
    return pd.concat(picks).drop_duplicates("tconst")


# ------------------------------------------------------------------ adjudicación y etiquetas finales v2 (D-026)
ADJ_FIELDS_CORE = ["final"]


def _labels(stage: str, full: bool):
    from . import annotation as an
    A, ea = an.load_labels_b(sorted((ANNOT / "labels" / stage / "A").glob("*.jsonl")), "A", full)
    B, eb = an.load_labels_b(sorted((ANNOT / "labels" / stage / "B").glob("*.jsonl")), "B", full)
    if ea or eb:
        raise ValueError(f"errores de validación en {stage}: {(ea + eb)[:5]}")
    return A, B


def _texts(stage: str) -> dict[str, str]:
    out = {}
    for f in (ANNOT / "batches" / stage).glob("*.jsonl"):
        for line in f.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            out[d["id"]] = d["sinopsis"]
    return out


def make_adjudication_v2(seed: int = 20260929, batch_size: int = 40,
                         stages=(("v2_completa", True), ("v2_modb", False)), prefix: str = "v2_adj",
                         key_name: str = "v2_adjudicacion_key.csv") -> pd.DataFrame:
    """Adjudica solo `final` (resultado principal) y los ítems −2..2 con diferencia ≥3 (D-026).
    Resto de categóricas en desacuerdo: regla fija (A) con sensibilidad B."""
    from . import annotation as an
    rng = np.random.default_rng(seed)
    rows = []
    for stage, full in stages:
        A, B = _labels(stage, full)
        m = A.merge(B, on="id", suffixes=("_A", "_B"))
        texts = _texts(stage)
        items = an.ITEMS_B + (an.ITEMS if full else [])
        for r in m.to_dict("records"):
            diff = [k for k in (ADJ_FIELDS_CORE if full else []) if r[f"{k}_A"] != r[f"{k}_B"]]
            diff += [k for k in items if pd.notna(r[f"{k}_A"]) and pd.notna(r[f"{k}_B"])
                     and abs(r[f"{k}_A"] - r[f"{k}_B"]) >= 3]
            if not diff:
                continue
            show = (list(an.CATS) + an.ITEMS if full else []) + list(an.CATS_B) + an.ITEMS_B
            la = {k: (None if isinstance(r[f"{k}_A"], float) and pd.isna(r[f"{k}_A"]) else r[f"{k}_A"]) for k in show}
            lb = {k: (None if isinstance(r[f"{k}_B"], float) and pd.isna(r[f"{k}_B"]) else r[f"{k}_B"]) for k in show}
            for d in (la, lb):
                for k in items:
                    d[k] = None if d[k] is None else int(d[k])
            swap = bool(rng.integers(0, 2))
            x, y = (lb, la) if swap else (la, lb)
            rows.append({"id": r["id"], "sinopsis": texts[r["id"]], "etiqueta_X": x, "etiqueta_Y": y,
                         "campos_en_desacuerdo": diff, "_swap": swap, "_stage": stage})
    df = pd.DataFrame(rows).sort_values("id").reset_index(drop=True)
    df["_batch"] = [f"{prefix}_{i // batch_size + 1:02d}" for i in range(len(df))]
    out_dir = ANNOT / "batches" / "v2_adjudicacion"
    out_dir.mkdir(parents=True, exist_ok=True)
    for b, g in df.groupby("_batch"):
        with open(out_dir / f"{b}.jsonl", "w", encoding="utf-8") as fh:
            for rec in g.drop(columns=["_swap", "_batch", "_stage"]).to_dict("records"):
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    df[["id", "_swap", "_batch", "_stage"]].to_csv(KEY_DIR / key_name, index=False)
    return df


def _adj_v2() -> pd.DataFrame:
    rows = []
    for f in sorted((ANNOT / "labels" / "v2_adjudicacion").glob("*.jsonl")):
        rows += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return pd.DataFrame(rows).set_index("id") if rows else pd.DataFrame()


def _item(a, b, adj, i, k):
    if pd.notna(a) and pd.notna(b):
        if abs(a - b) < 3:
            return (a + b) / 2, "media"
        if i in adj.index and k in adj.columns and pd.notna(adj.at[i, k]):
            return float(adj.at[i, k]), "adjudicado"
        return np.nan, "sin_resolver"
    return np.nan, "falta_alguno"  # D-026: si uno de los dos da null, el ítem queda sin valor


def final_labels_v2() -> pd.DataFrame:
    """Etiquetas finales por tconst para todo el universo v2 (núcleo + módulo B). Reglas en D-026."""
    from . import annotation as an
    adj = _adj_v2()
    out = []
    for stage, full in (("v2_completa", True), ("v2_modb", False), ("v2_es_en", True)):
        A, B = _labels(stage, full)
        m = A.merge(B, on="id", suffixes=("_A", "_B"))
        key = pd.read_csv(KEY_DIR / f"{stage}_key.csv")
        key["sinopsis_idioma"] = key["idioma"] if "idioma" in key else "en"
        key = key[["id", "tconst", "sinopsis_idioma"]]
        m = m.merge(key, on="id")
        recs = []
        for r in m.to_dict("records"):
            i = r["id"]
            d = {"tconst": r["tconst"], "id_v2": i, "etapa_v2": stage, "sinopsis_idioma": r["sinopsis_idioma"]}
            cats = (list(an.CATS) if full else []) + list(an.CATS_B)
            for k in cats:
                a, b = r[f"{k}_A"], r[f"{k}_B"]
                if a == b:
                    d[k], d[f"{k}_fuente"] = a, "acuerdo"
                elif k == "final" and i in adj.index and pd.notna(adj.at[i, "final"]):
                    d[k], d[f"{k}_fuente"] = adj.at[i, "final"], "adjudicado"
                else:
                    d[k], d[f"{k}_fuente"] = a, "regla_A"
                d[f"{k}_A"], d[f"{k}_B"] = a, b
            for k in an.ITEMS_B + (an.ITEMS if full else []):
                d[k], d[f"{k}_fuente"] = _item(r[f"{k}_A"], r[f"{k}_B"], adj, i, k)
                d[f"{k}_A"], d[f"{k}_B"] = r[f"{k}_A"], r[f"{k}_B"]
            for k in ("relaciones_centrales", "paises_trama"):
                d[f"{k}_A"] = "|".join(r[f"{k}_A"])
                d[f"{k}_B"] = "|".join(r[f"{k}_B"])
            for rel in an.RELACIONES:
                d[f"rel_{rel.lower()}"] = ((rel in r["relaciones_centrales_A"]) + (rel in r["relaciones_centrales_B"])) / 2
            d["reconocida_b"] = bool(r["reconocida_A"]) or bool(r["reconocida_B"])
            if full:
                d["reconocida"] = d["reconocida_b"]
                d["describe_final"] = bool(r["describe_final_A"]) and bool(r["describe_final_B"])
            recs.append(d)
        out.append(pd.DataFrame(recs))
    lab = pd.concat(out, ignore_index=True)
    # D-027: si la sinopsis española no describía el final y se reanotó con la inglesa, manda la reanotación;
    # la etiqueta original se conserva como sensibilidad (final_es_original).
    esen = set(lab.loc[lab.etapa_v2 == "v2_es_en", "tconst"])
    orig = lab[(lab.etapa_v2 == "v2_completa") & lab.tconst.isin(esen)].set_index("tconst")["final"]
    lab = lab[~((lab.etapa_v2 == "v2_completa") & lab.tconst.isin(esen))].copy()
    lab["final_es_original"] = lab.tconst.map(orig)
    # núcleo v1 para las películas del estudio v1 (manual 1.0, adjudicación completa del núcleo)
    v1 = pd.read_csv(INTERIM / "analitico_principal.csv").drop_duplicates("tconst")
    core = list(an.CATS) + an.ITEMS + ["final_A", "final_B", "reconocida", "describe_final"] + \
        [f"{k}_fuente" for k in an.CATS]
    v1 = v1[["tconst"] + core].set_index("tconst")
    isv1 = lab.etapa_v2 == "v2_modb"
    for c in core:
        if c not in lab.columns:
            lab[c] = np.nan
        lab[c] = lab[c].astype(object)
        lab.loc[isv1, c] = lab.loc[isv1, "tconst"].map(v1[c]).values
    lab["vision_vida"] = an.vision_score(lab.assign(**{k: lab[k].astype(float) for k in an.ITEMS}))
    return lab


def analytic_v2() -> pd.DataFrame:
    u = pd.read_csv(INTERIM / "universo_v2.csv")
    u = u[u.has_synopsis]
    lab = final_labels_v2()
    df = u.merge(lab, on="tconst", how="left")
    miss = df.final.isna().sum()
    df["clasificable"] = df.final.isin(["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"])
    for c in ("FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"):
        df[f"y_{c.lower()}"] = np.where(df.clasificable, (df.final == c).astype(float), np.nan)
    df["y_feliz_A"] = np.where(df.final_A.isin(["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"]),
                               (df.final_A == "FELIZ").astype(float), np.nan)
    df["y_feliz_B"] = np.where(df.final_B.isin(["FELIZ", "AGRIDULCE", "AMBIGUO", "TRAGICO"]),
                               (df.final_B == "FELIZ").astype(float), np.nan)
    df["y_optimistas"] = (df.optimismo_personajes > 0).astype(float).where(df.optimismo_personajes.notna())
    df["y_tono_pos"] = (df.tono_general > 0).astype(float).where(df.tono_general.notna())
    df["tragedia_vitalista"] = ((df.final == "TRAGICO") & (df.optimismo_personajes > 0)).astype(float).where(df.clasificable)
    df.to_csv(INTERIM / "analitico_v2.csv", index=False)
    pub = df.drop(columns=["numVotes", "averageRating", "primaryTitle", "originalTitle", "genres", "countries",
                           "enwiki_url", "eswiki_url"], errors="ignore")
    pub.to_csv(DERIVED / "etiquetas_v2.csv", index=False)
    print(f"analitico_v2: {len(df)} filas, sin etiqueta final: {miss}")
    return df


if __name__ == "__main__":
    analytic_v2()
