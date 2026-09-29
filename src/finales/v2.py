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


def make_batches_v2(films: pd.DataFrame, stage: str, batch_size: int = 50) -> pd.DataFrame:
    """Lotes cegados para anotación completa (núcleo + módulo B)."""
    cfg = load()
    seed, maxw = cfg["project"]["seed"], cfg["sinopsis"]["max_palabras_anotacion"]
    out_dir = ANNOT / "batches" / stage
    out_dir.mkdir(parents=True, exist_ok=True)
    recs = []
    for r in films.itertuples():
        syn = synopsis_for(r.tconst, "es" if r.country_frame == "ES" else "en")
        titles = blinding.title_variants(
            r.primaryTitle, r.originalTitle,
            r.enwiki_url.rsplit("/wiki/", 1)[-1] if isinstance(r.enwiki_url, str) else None,
            r.eswiki_url.rsplit("/wiki/", 1)[-1] if isinstance(r.eswiki_url, str) else None)
        text = blinding.mask(syn["text"], titles)
        text, trunc = blinding.truncate_words(text, maxw)
        recs.append({"id": blind_id_v2(r.tconst, seed), "tconst": r.tconst, "sinopsis": text,
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
