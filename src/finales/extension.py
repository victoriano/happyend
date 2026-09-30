"""Ampliación del censo v2 a 2025 (año cerrado) y 2026 (año en curso, solo explorador) — D-031.

Mismas reglas que el universo 1980-2024: EE. UU. = 50 más votadas por año con sinopsis inglesa ≥120 palabras
(las que no tienen sinopsis no se sustituyen); España = 15 más votadas con sinopsis (española o, si falta, inglesa),
sustituyendo por las siguientes. No modifica catalog.csv ni el universo de la primera parte.
"""
from __future__ import annotations

import copy

import pandas as pd

from . import clean, spain, wikidump as w
from .config import INTERIM, load
from .ingest import _session, _wikidata_year

YEARS = [2025, 2026]


def _cfg():
    cfg = copy.deepcopy(load())
    cfg["periodo"]["year_max"] = max(YEARS)
    cfg["periodo"]["cohortes"] = {**cfg["periodo"]["cohortes"], "2025": [2025, 2025], "2026": [2026, 2026]}
    return cfg


def fetch_wikidata():
    s = _session()
    us = pd.concat([_wikidata_year(y, s, INTERIM / "wikidata_by_year") for y in range(2023, 2028)], ignore_index=True)
    es = pd.concat([spain._year(y, s, INTERIM / "wikidata_es_by_year") for y in range(2023, 2028)], ignore_index=True)
    return us, es


def build() -> pd.DataFrame:
    cfg = _cfg()
    imdb = pd.read_pickle(INTERIM / "imdb_movies.pkl")
    us_wd, es_wd = fetch_wikidata()
    # --- EE. UU.
    cat, _ = clean.apply_filters(imdb, clean.summarise_wikidata(us_wd), cfg)
    cat = cat[cat.year.isin(YEARS)]
    us = cat[cat.votes_rank_in_year <= cfg["marcos"]["popular"]["top_por_anio"]].copy()
    # --- España (mismas reglas que spain.build_catalog_es)
    first = lambda s: next((x for x in s if isinstance(x, str)), None)
    es_art = es_wd.groupby("tconst").eswiki_url.agg(first)
    en_art = es_wd.groupby("tconst").enwiki_url.agg(first)
    wd2 = es_wd.copy()
    wd2["enwiki_url"] = wd2["enwiki_url"].fillna(wd2["tconst"].map(es_art))
    cfg2 = copy.deepcopy(cfg)
    cfg2["filtros_catalogo"]["min_votos_catalogo"] = spain.MIN_VOTES_ES
    ces, _ = clean.apply_filters(imdb, clean.summarise_wikidata(wd2), cfg2)
    ces = ces[ces.year.isin(YEARS)].copy()
    ces["eswiki_url"] = ces.tconst.map(es_art)
    ces["enwiki_url"] = ces.tconst.map(en_art)
    ces["votes_rank_in_year"] = ces.groupby("year")["numVotes"].rank(method="first", ascending=False).astype(int)
    ces.to_csv(INTERIM / "catalog_es_ext.csv", index=False)
    # --- sinopsis
    s = w.session()
    off_en = w.build_offsets(set(us.enwiki_url.dropna().map(w.title_from_url)) |
                             set(ces.enwiki_url.dropna().map(w.title_from_url)), wiki="en")
    off_es = w.build_offsets(set(ces.eswiki_url.dropna().map(w.title_from_url)), wiki="es")
    us["syn_words"] = [w.word_count(w.fetch_one(r.tconst, r.enwiki_url, off_en, s, wiki="en").get("text"))
                       for r in us.itertuples()]
    us = us[us.syn_words >= 120].assign(country_frame="US", synopsis_wiki="en")
    rows = []
    for r in ces[ces.votes_rank_in_year <= spain.TOP_ES + 15].sort_values(["year", "votes_rank_in_year"]).itertuples():
        src = None
        if isinstance(r.eswiki_url, str) and w.word_count(w.fetch_one(r.tconst, r.eswiki_url, off_es, s, wiki="es").get("text")) >= 120:
            src = "es"
        elif isinstance(r.enwiki_url, str) and w.word_count(w.fetch_one(r.tconst, r.enwiki_url, off_en, s, wiki="en").get("text")) >= 120:
            src = "en"
        rows.append((r.tconst, src))
    src = dict(rows)
    ces["synopsis_wiki"] = ces.tconst.map(src)
    es = ces[ces.synopsis_wiki.notna()].sort_values(["year", "votes_rank_in_year"])
    es = es[es.groupby("year").cumcount() < spain.TOP_ES].assign(country_frame="ES")
    cols = ["tconst", "primaryTitle", "originalTitle", "year", "cohort", "genres", "genre_main", "numVotes",
            "averageRating", "votes_rank_in_year", "countries", "us_only", "enwiki_url", "country_frame",
            "synopsis_wiki", "eswiki_url"]
    u = pd.concat([us.reindex(columns=cols), es.reindex(columns=cols)], ignore_index=True)
    u["anio_en_curso"] = u.year == 2026
    u.to_csv(INTERIM / "universo_ext.csv", index=False)
    print(u.groupby(["country_frame", "year"]).size().to_dict())
    return u


if __name__ == "__main__":
    build()
