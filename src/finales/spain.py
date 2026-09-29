"""Cine español (v2): películas con país de origen España (P495=Q29) en Wikidata, con enlaces a la
Wikipedia en español e inglés. La sinopsis se toma de la Wikipedia en español (sección Argumento/Sinopsis…)
y, si no existe o es corta, de la inglesa (registro de decisiones D-024).
"""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

from . import provenance
from .config import INTERIM, load
from .ingest import WDQS, _session, _wikidata_query

SPARQL_ES = """
SELECT ?item ?imdb ?enart ?esart ?country ?date WHERE {{
  VALUES ?cls {{ wd:Q11424 wd:Q24869 wd:Q202866 wd:Q29168811 }}
  ?item wdt:P31 ?cls ;
        wdt:P495 wd:Q29 ;
        wdt:P345 ?imdb ;
        wdt:P577 ?date .
  FILTER({date_filter})
  ?item wdt:P495 ?country .
  OPTIONAL {{ ?enart schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> . }}
  OPTIONAL {{ ?esart schema:about ?item ; schema:isPartOf <https://es.wikipedia.org/> . }}
}}
"""


def _year(y: int, s: requests.Session, cache_dir: Path) -> pd.DataFrame:
    cache = cache_dir / f"{y}.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype=str)
    b = _wikidata_query(SPARQL_ES.format(date_filter=f"YEAR(?date) = {y}"), s, f"ES {y}", 5)
    if b is None:
        raise RuntimeError(f"Wikidata ES falló para {y}")
    rows = [{"wikidata_id": x["item"]["value"].rsplit("/", 1)[-1], "tconst": x["imdb"]["value"],
             "enwiki_url": x.get("enart", {}).get("value"), "eswiki_url": x.get("esart", {}).get("value"),
             "country_qid": x["country"]["value"].rsplit("/", 1)[-1], "pub_date": x["date"]["value"][:10],
             "query_year": y} for x in b]
    df = pd.DataFrame(rows, columns=["wikidata_id", "tconst", "enwiki_url", "eswiki_url", "country_qid",
                                     "pub_date", "query_year"])
    df.to_csv(cache, index=False)
    print(f"[wikidata ES] {y}: {len(df)} filas", flush=True)
    return df


def fetch_wikidata_es(force: bool = False, workers: int = 3) -> Path:
    from concurrent.futures import ThreadPoolExecutor
    cfg = load()["periodo"]
    years = range(cfg["year_min"] - 2, cfg["year_max"] + 2)
    out = INTERIM / "wikidata_es_films.csv"
    if out.exists() and not force:
        return out
    cache_dir = INTERIM / "wikidata_es_by_year"
    cache_dir.mkdir(parents=True, exist_ok=True)
    s = _session()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        parts = list(ex.map(lambda y: _year(y, s, cache_dir), years))
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(out, index=False)
    provenance.record("wikidata", WDQS, out, notes="SPARQL España (P495=Q29) por año; plantilla spain.SPARQL_ES")
    return out


TOP_ES = 15          # universo popular español: 15 películas con más votos por año (D-023)
MIN_VOTES_ES = 200   # umbral de votos menor que el de EE. UU. (1.000): el cine español acumula menos votos en IMDb


def build_catalog_es() -> pd.DataFrame:
    """Catálogo español con los mismos filtros que el estadounidense salvo el umbral de votos."""
    from . import clean
    cfg = load()
    imdb = pd.read_pickle(INTERIM / "imdb_movies.pkl")
    wd = pd.read_csv(INTERIM / "wikidata_es_films.csv", dtype=str)
    first = lambda s: next((x for x in s if isinstance(x, str)), None)
    es_art = wd.groupby("tconst").eswiki_url.agg(first)
    en_art = wd.groupby("tconst").enwiki_url.agg(first)
    wd2 = wd.copy()
    wd2["enwiki_url"] = wd2["enwiki_url"].fillna(wd2["tconst"].map(es_art))  # basta con artículo en una de las dos
    cfg2 = dict(cfg)
    cfg2["filtros_catalogo"] = {**cfg["filtros_catalogo"], "min_votos_catalogo": MIN_VOTES_ES}
    cat, excl = clean.apply_filters(imdb, clean.summarise_wikidata(wd2), cfg2)
    cat["eswiki_url"] = cat.tconst.map(es_art)
    cat["enwiki_url"] = cat.tconst.map(en_art)
    cat["votes_rank_in_year"] = cat.groupby("year")["numVotes"].rank(method="first", ascending=False).astype(int)
    cat["in_popular_universe"] = cat["votes_rank_in_year"] <= TOP_ES
    cat["country_frame"] = "ES"
    cat.to_csv(INTERIM / "catalog_es.csv", index=False)
    excl.to_csv(INTERIM / "exclusions_es.csv", index=False)
    return cat


def fetch_synopses_es(cat: pd.DataFrame, min_words: int = 120) -> pd.DataFrame:
    """Sinopsis de la Wikipedia en español; si falta o es corta, de la inglesa."""
    from . import wikidump as w
    pop = cat[cat.votes_rank_in_year <= TOP_ES + 15]   # candidatos: se toman los 15 primeros con sinopsis
    s = w.session()
    off_es = w.build_offsets(set(pop.eswiki_url.dropna().map(w.title_from_url)), wiki="es")
    off_en = w.build_offsets(set(pop.enwiki_url.dropna().map(w.title_from_url)) |
                             set(pd.read_csv(INTERIM / "catalog.csv").enwiki_url.map(w.title_from_url)), wiki="en")
    rows = []
    for r in pop.itertuples():
        src, rec = None, None
        if isinstance(r.eswiki_url, str):
            rec = w.fetch_one(r.tconst, r.eswiki_url, off_es, s, wiki="es")
            if w.word_count(rec.get("text")) >= min_words:
                src = "es"
        if src is None and isinstance(r.enwiki_url, str):
            rec = w.fetch_one(r.tconst, r.enwiki_url, off_en, s, wiki="en")
            if w.word_count(rec.get("text")) >= min_words:
                src = "en"
        rows.append({"tconst": r.tconst, "synopsis_wiki": src,
                     "synopsis_words": w.word_count(rec.get("text")) if rec else 0})
    return pd.DataFrame(rows)


def select_universe_es(cat: pd.DataFrame, syn: pd.DataFrame) -> pd.DataFrame:
    """Universo popular español: por año, las TOP_ES películas más votadas que tienen sinopsis utilizable."""
    c = cat.merge(syn, on="tconst", how="left")
    c = c[c.synopsis_wiki.notna()].sort_values(["year", "votes_rank_in_year"])
    c["rank_con_sinopsis"] = c.groupby("year").cumcount() + 1
    u = c[c.rank_con_sinopsis <= TOP_ES].copy()
    u.to_csv(INTERIM / "universo_es.csv", index=False)
    return u


if __name__ == "__main__":
    print(fetch_wikidata_es())
    cat = build_catalog_es()
    syn = fetch_synopses_es(cat)
    u = select_universe_es(cat, syn)
    print(len(u), u.groupby("cohort").size().to_dict(), u.synopsis_wiki.value_counts().to_dict())
