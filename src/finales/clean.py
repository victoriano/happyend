"""Construcción del catálogo analizable: filtros, cruce con Wikidata, deduplicación y exclusiones.

Salidas (data/interim, no versionadas porque contienen campos de IMDb):
  catalog.csv          películas elegibles con metadatos y popularidad
  exclusions.csv       tconst + motivo de exclusión (primer filtro que falla)
Salida versionable (reports/tables):
  exclusiones_resumen.csv  recuento por motivo y cohorte
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .config import INTERIM, TABLES, cohort_of, ensure_dirs, load

US_QID = "Q30"


def primary_genre(genres: str | float, priority: list, fallback: str) -> str:
    """Asigna un género principal según una lista de prioridad sobre los géneros de IMDb."""
    if not isinstance(genres, str) or not genres:
        return fallback
    gs = set(genres.split(","))
    for imdb_name, label in priority:
        if imdb_name in gs:
            return label
    return fallback


def summarise_wikidata(wd: pd.DataFrame) -> pd.DataFrame:
    """Una fila por tconst: países, artículo de enwiki, año mínimo de publicación, n.º de ítems."""
    wd = wd.copy()
    wd["pub_year"] = pd.to_numeric(wd["pub_date"].str[:4], errors="coerce")
    g = wd.groupby("tconst")
    out = pd.DataFrame({
        "wikidata_ids": g["wikidata_id"].agg(lambda s: "|".join(sorted(set(s)))),
        "n_wikidata_items": g["wikidata_id"].nunique(),
        "countries": g["country_qid"].agg(lambda s: "|".join(sorted(set(s)))),
        "wd_min_year": g["pub_year"].min(),
        "enwiki_url": g["enwiki_url"].agg(lambda s: next((x for x in s if isinstance(x, str)), None)),
    }).reset_index()
    out["us_only"] = out["countries"] == US_QID
    out["n_countries"] = out["countries"].str.count(r"\|") + 1
    return out


def apply_filters(imdb: pd.DataFrame, wd_summary: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica los filtros en orden y devuelve (catálogo, exclusiones). Cada exclusión tiene un único motivo."""
    fc = cfg["filtros_catalogo"]
    per = cfg["periodo"]
    df = imdb.copy()
    df["startYear"] = pd.to_numeric(df["startYear"], errors="coerce")
    df["runtimeMinutes"] = pd.to_numeric(df["runtimeMinutes"], errors="coerce")
    df["numVotes"] = pd.to_numeric(df["numVotes"], errors="coerce").fillna(0).astype(int)
    df = df[(df["titleType"] == fc["title_type"])
            & df["startYear"].between(per["year_min"], per["year_max"])].copy()
    # Duplicados de identificador (no deberían existir en IMDb, pero se comprueba).
    df["reason"] = np.where(df.duplicated("tconst", keep="first"), "duplicado_tconst", None)

    df = df.merge(wd_summary, on="tconst", how="left")
    excl_genres = set(fc["excluir_generos_imdb"])

    def first_reason(r) -> str | None:
        if r["reason"]:
            return r["reason"]
        if str(r.get("isAdult")) == "1":
            return "adulto"
        if pd.isna(r["runtimeMinutes"]):
            return "sin_duracion"
        if r["runtimeMinutes"] < fc["runtime_min"]:
            return "duracion_menor_umbral"
        gs = set(str(r["genres"]).split(",")) if isinstance(r["genres"], str) else set()
        if not gs:
            return "sin_genero"
        if gs & excl_genres:
            return "genero_no_ficcion"
        if r["numVotes"] < fc["min_votos_catalogo"]:
            return "votos_bajo_umbral"
        if pd.isna(r["countries"]):
            return "nacionalidad_no_establecida_o_no_eeuu"
        if (pd.notna(r["wd_min_year"])
                and abs(r["startYear"] - r["wd_min_year"]) > fc["max_desfase_anio_wikidata"]):
            return "anio_inconsistente_imdb_wikidata"
        if not isinstance(r["enwiki_url"], str):
            return "sin_articulo_wikipedia"
        return None

    df["reason"] = df.apply(first_reason, axis=1)

    # Duplicados de artículo: un mismo artículo de Wikipedia enlazado desde varios tconst
    # (p. ej., remontajes o ítems duplicados). Se conserva el de más votos.
    ok = df["reason"].isna()
    dup = df[ok].sort_values("numVotes", ascending=False).duplicated("enwiki_url", keep="first")
    df.loc[dup[dup].index, "reason"] = "duplicado_articulo_wikipedia"

    df["cohort"] = df["startYear"].map(lambda y: cohort_of(int(y), per["cohortes"]))
    excluded = df[df["reason"].notna()][["tconst", "startYear", "cohort", "reason"]].copy()
    cat = df[df["reason"].isna()].drop(columns=["reason"]).copy()

    cat["year"] = cat["startYear"].astype(int)
    cat["genre_main"] = cat["genres"].map(
        lambda g: primary_genre(g, cfg["genero_principal_prioridad"], cfg["genero_resto"]))
    cat = add_popularity(cat, cfg)
    return cat.reset_index(drop=True), excluded.reset_index(drop=True)


def add_popularity(cat: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Rango de votos dentro del año, pertenencia al universo popular y tramo (tercil) dentro del año."""
    cat = cat.copy()
    cat["votes_rank_in_year"] = cat.groupby("year")["numVotes"].rank(method="first", ascending=False).astype(int)
    cat["votes_pct_in_year"] = cat.groupby("year")["numVotes"].rank(pct=True)
    top = cfg["marcos"]["popular"]["top_por_anio"]
    cat["in_popular_universe"] = cat["votes_rank_in_year"] <= top
    k = cfg["marcos"]["amplio"]["n_tramos_popularidad"]
    cat["pop_tier"] = np.minimum((cat["votes_pct_in_year"] * k).apply(np.ceil).astype(int), k)
    cat["pop_tier"] = cat["pop_tier"].clip(lower=1)
    return cat


def build(imdb: pd.DataFrame | None = None, wd: pd.DataFrame | None = None) -> pd.DataFrame:
    from . import ingest
    ensure_dirs()
    cfg = load()
    if imdb is None:
        cache = INTERIM / "imdb_movies.pkl"
        if cache.exists() and cache.stat().st_mtime > (ingest.RAW / "title.basics.tsv.gz").stat().st_mtime:
            imdb = pd.read_pickle(cache)
        else:
            imdb = ingest.load_imdb_movies()
            imdb.to_pickle(cache)
    wd = wd if wd is not None else pd.read_csv(INTERIM / "wikidata_us_films.csv", dtype=str)
    cat, excl = apply_filters(imdb, summarise_wikidata(wd), cfg)
    cat.to_csv(INTERIM / "catalog.csv", index=False)
    excl.to_csv(INTERIM / "exclusions.csv", index=False)
    summary = (excl.groupby(["reason", "cohort"]).size().unstack(fill_value=0))
    summary["total"] = summary.sum(axis=1)
    summary.sort_values("total", ascending=False).to_csv(TABLES / "exclusiones_resumen.csv")
    kept = cat.groupby("cohort").size().rename("catalogo_elegible")
    kept.to_csv(TABLES / "catalogo_por_cohorte.csv")
    return cat


if __name__ == "__main__":
    c = build()
    print(c.groupby("cohort").size())
