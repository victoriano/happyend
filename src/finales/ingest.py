"""Descarga de fuentes abiertas: IMDb (no comercial), CMU Movie Summary Corpus y Wikidata (CC0).

Cada descarga se registra en data/provenance.jsonl con URL, fecha, licencia y hash.
Los ficheros crudos NO se versionan (ver .gitignore): las condiciones de IMDb
prohíben redistribuir sus datos.
"""
from __future__ import annotations

import io
import json
import tarfile
import time
from pathlib import Path

import pandas as pd
import requests

from . import provenance
from .config import INTERIM, RAW, ensure_dirs, load

IMDB_FILES = {
    "title.basics.tsv.gz": "https://datasets.imdbws.com/title.basics.tsv.gz",
    "title.ratings.tsv.gz": "https://datasets.imdbws.com/title.ratings.tsv.gz",
}
CMU_URL = "https://www.cs.cmu.edu/~ark/personas/data/MovieSummaries.tar.gz"
WDQS = "https://query.wikidata.org/sparql"


def _session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = load()["project"]["user_agent"]
    return s


def download(url: str, dest: Path, source: str, force: bool = False) -> Path:
    if dest.exists() and not force:
        return dest
    with _session().get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
        tmp.rename(dest)
    provenance.record(source, url, dest)
    return dest


def fetch_imdb(force: bool = False) -> None:
    for name, url in IMDB_FILES.items():
        download(url, RAW / name, "imdb", force)


def fetch_cmu(force: bool = False) -> Path:
    tgz = download(CMU_URL, RAW / "MovieSummaries.tar.gz", "cmu", force)
    out = RAW / "MovieSummaries"
    if not out.exists():
        with tarfile.open(tgz) as tf:
            tf.extractall(RAW, filter="data")
    return out


SPARQL_TEMPLATE = """
SELECT ?item ?imdb ?article ?country ?date WHERE {{
  VALUES ?cls {{ wd:Q11424 wd:Q24869 wd:Q202866 wd:Q29168811 }}
  ?item wdt:P31 ?cls ;
        wdt:P495 wd:Q30 ;
        wdt:P345 ?imdb ;
        wdt:P577 ?date .
  FILTER({date_filter})
  ?item wdt:P495 ?country .
  OPTIONAL {{ ?article schema:about ?item ;
                      schema:isPartOf <https://en.wikipedia.org/> . }}
}}
"""


def _wikidata_query(q: str, session: requests.Session, label: str, attempts: int = 4) -> list | None:
    for attempt in range(attempts):
        try:
            r = session.get(WDQS, params={"query": q},
                            headers={"Accept": "application/sparql-results+json"}, timeout=180)
            if r.status_code == 200:
                return r.json()["results"]["bindings"]  # ValueError si la respuesta llega truncada
            print(f"[wikidata] {label}: HTTP {r.status_code}, reintento {attempt + 1}", flush=True)
        except (requests.RequestException, ValueError) as exc:
            print(f"[wikidata] {label}: {type(exc).__name__}, reintento {attempt + 1}", flush=True)
        time.sleep(10 * (attempt + 1))
    return None


def _wikidata_year(y: int, session: requests.Session, cache_dir: Path) -> pd.DataFrame:
    """Consulta un año completo; si la respuesta falla o llega truncada, lo divide por meses."""
    cache = cache_dir / f"{y}.csv"
    if cache.exists():
        return pd.read_csv(cache, dtype=str)
    bindings = _wikidata_query(SPARQL_TEMPLATE.format(date_filter=f"YEAR(?date) = {y}"), session, str(y), 2)
    if bindings is None:
        bindings = []
        for m in range(1, 13):
            f = f"YEAR(?date) = {y} && MONTH(?date) = {m}"
            part = _wikidata_query(SPARQL_TEMPLATE.format(date_filter=f), session, f"{y}-{m:02d}", 5)
            if part is None:
                raise RuntimeError(f"Wikidata falló para {y}-{m:02d}")
            bindings += part
    rows = [{
        "wikidata_id": b["item"]["value"].rsplit("/", 1)[-1],
        "tconst": b["imdb"]["value"],
        "enwiki_url": b.get("article", {}).get("value"),
        "country_qid": b["country"]["value"].rsplit("/", 1)[-1],
        "pub_date": b["date"]["value"][:10],
        "query_year": y,
    } for b in bindings]
    cols = ["wikidata_id", "tconst", "enwiki_url", "country_qid", "pub_date", "query_year"]
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(cache, index=False)
    print(f"[wikidata] {y}: {len(df)} filas", flush=True)
    return df


def fetch_wikidata(years: range | None = None, force: bool = False, workers: int = 3) -> Path:
    """Películas con país de origen EE. UU. (P495=Q30) y con identificador IMDb, por año de publicación.

    Consulta año a año (caché por año) con como máximo 3 consultas simultáneas,
    por debajo del límite de 5 por IP del servicio de consultas de Wikidata.
    """
    from concurrent.futures import ThreadPoolExecutor

    cfg = load()["periodo"]
    years = years or range(cfg["year_min"] - 2, cfg["year_max"] + 2)
    out = INTERIM / "wikidata_us_films.csv"
    if out.exists() and not force:
        return out
    cache_dir = INTERIM / "wikidata_by_year"
    cache_dir.mkdir(parents=True, exist_ok=True)
    s = _session()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        parts = list(ex.map(lambda y: _wikidata_year(y, s, cache_dir), years))
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(out, index=False)
    provenance.record("wikidata", WDQS, out,
                      notes=f"SPARQL por año {years.start}-{years.stop - 1}; plantilla en ingest.SPARQL_TEMPLATE")
    return out


def load_imdb_movies() -> pd.DataFrame:
    """Lee title.basics filtrando a titleType=movie para ahorrar memoria."""
    chunks = []
    for ch in pd.read_csv(RAW / "title.basics.tsv.gz", sep="\t", na_values="\\N", quoting=3,
                          dtype=str, chunksize=500_000):
        chunks.append(ch[ch["titleType"] == "movie"])
    basics = pd.concat(chunks, ignore_index=True)
    ratings = pd.read_csv(RAW / "title.ratings.tsv.gz", sep="\t", na_values="\\N",
                          dtype={"tconst": str, "averageRating": float, "numVotes": "Int64"})
    return basics.merge(ratings, on="tconst", how="left")


def load_cmu() -> pd.DataFrame:
    d = RAW / "MovieSummaries"
    meta = pd.read_csv(d / "movie.metadata.tsv", sep="\t", header=None, dtype=str,
                       names=["wiki_pageid", "freebase_id", "name", "release", "box_office",
                              "runtime", "languages", "countries", "genres"])
    plots = pd.read_csv(d / "plot_summaries.txt", sep="\t", header=None, dtype=str,
                        names=["wiki_pageid", "plot"], quoting=3)
    df = meta.merge(plots, on="wiki_pageid", how="left")
    df["countries"] = df["countries"].map(lambda s: list(json.loads(s).values()) if isinstance(s, str) else [])
    return df


def main() -> None:
    ensure_dirs()
    fetch_imdb()
    fetch_cmu()
    fetch_wikidata()


if __name__ == "__main__":
    main()
