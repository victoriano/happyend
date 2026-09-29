"""Orquestación del flujo por etapas. Uso: python -m finales.pipeline <etapa>

Etapas:
  ingest     descarga IMDb, CMU y Wikidata (con registro de procedencia)
  catalog    catálogo elegible + exclusiones
  coverage   cobertura del CMU Movie Summary Corpus por cohorte
  pilot      muestra piloto, sinopsis de Wikipedia y lotes cegados
  main       muestra principal (excluye el piloto), sinopsis y lotes cegados
"""
from __future__ import annotations

import sys

import pandas as pd

from . import annotation, clean, ingest, provenance, sampling, wikidump
from .config import DERIVED, INTERIM, TABLES, ensure_dirs, load

PUBLIC_COLS = ["tconst", "wikidata_ids", "year", "cohort", "genre_main", "pop_tier", "votes_rank_in_year",
               "in_popular_universe", "us_only", "n_countries"]


def _catalog() -> pd.DataFrame:
    return pd.read_csv(INTERIM / "catalog.csv", dtype={"tconst": str})


def _validator(cat: pd.DataFrame):
    """Devuelve una función que obtiene (con caché) la sinopsis del volcado y comprueba su longitud mínima."""
    cfg = load()
    urls = dict(zip(cat["tconst"], cat["enwiki_url"]))
    minw = cfg["sinopsis"]["min_palabras"]
    offsets = wikidump.build_offsets(set(cat["enwiki_url"].map(wikidump.title_from_url)))
    s = wikidump.session()

    def ok(t: str) -> bool:
        rec = wikidump.fetch_one(t, urls[t], offsets, s)
        return wikidump.word_count(rec.get("text")) >= minw
    return ok


def draw(stage: str) -> pd.DataFrame:
    """Extrae la muestra. Si la etapa ya tiene muestra congelada y etiquetas, no hace nada salvo con --force:
    los votos de IMDb cambian a diario y volver a extraer produciría otra muestra (registro D-021)."""
    frozen = DERIVED / f"muestra_{stage}.csv"
    labels_dir = annotation.ANNOT / "labels" / stage
    if frozen.exists() and labels_dir.exists() and any(labels_dir.rglob("*.jsonl")) and "--force" not in sys.argv:
        print(f"[aviso] Muestra '{stage}' congelada y ya anotada: se usa {frozen.relative_to(DERIVED.parent.parent)} "
              "(usa --force para volver a extraerla).")
        return pd.read_csv(frozen)
    cfg = load()
    cat = _catalog()
    seed = cfg["project"]["seed"]
    key = "piloto" if stage == "piloto" else "principal"
    exclude = set()
    if stage == "principal":
        exclude = set(pd.read_csv(DERIVED / "muestra_piloto.csv")["tconst"])
    ok = _validator(cat)
    provenance.record("wikipedia", wikidump.BASE + wikidump.DUMP_NAME,
                      notes=f"Lectura por HTTP Range de los bloques de los artículos muestreados ({stage}); "
                            "índice verificado con SHA-1 publicado")
    parts, logs = [], []
    for frame in ("popular", "amplio"):
        n = cfg[key][f"n_por_cohorte_{frame}"]
        s, lg = sampling.sample_frame(cat, frame, n, seed, ok, exclude,
                                      cfg["marcos"]["amplio"]["n_tramos_popularidad"])
        parts.append(s)
        logs.append(lg)
    sample = pd.concat(parts, ignore_index=True)
    log = pd.concat(logs, ignore_index=True)
    log.to_csv(TABLES / f"muestreo_log_{stage}.csv", index=False)

    # Metadatos públicos + procedencia de la sinopsis (URL de revisión, no el texto).
    meta = cat.set_index("tconst")
    prov = []
    for t in sample["tconst"].unique():
        rec = annotation.load_synopsis(t) or {}
        prov.append({"tconst": t, "synopsis_source": rec.get("source"), "synopsis_revision_url": rec.get("revision_url"),
                     "synopsis_heading": rec.get("heading"), "synopsis_retrieved_at": rec.get("retrieved_at"),
                     "synopsis_license": "CC BY-SA 4.0", "synopsis_words": wikidump.word_count(rec.get("text")),
                     "synopsis_status": rec.get("status")})
    prov = pd.DataFrame(prov).set_index("tconst")
    out = sample.join(meta[[c for c in PUBLIC_COLS if c != "tconst" and c != "cohort"]], on="tconst") \
                .join(prov, on="tconst")
    out.to_csv(DERIVED / f"muestra_{stage}.csv", index=False)

    films = meta.loc[sample["tconst"].unique(), ["primaryTitle", "originalTitle", "enwiki_url"]].reset_index()
    labels_dir = annotation.ANNOT / "labels" / stage
    if labels_dir.exists() and any(labels_dir.rglob("*.jsonl")) and "--force" not in sys.argv:
        print(f"[aviso] Ya hay etiquetas para '{stage}': no se regeneran los lotes (usa --force para forzarlo).")
    else:
        annotation.make_batches(films, stage, batch_size=50)
    return out


def coverage() -> pd.DataFrame:
    """¿Cuántas películas del catálogo tienen sinopsis en el CMU (volcado de Wikipedia de 2012)?

    Emparejamiento aproximado por título normalizado y año (±1), solo para evaluar cobertura.
    """
    cat = _catalog()
    cmu = ingest.load_cmu()
    cmu = cmu[cmu["plot"].notna()].copy()
    cmu["year"] = pd.to_numeric(cmu["release"].str[:4], errors="coerce")
    norm = lambda s: s.str.lower().str.replace(r"[^a-z0-9]+", " ", regex=True).str.strip()
    cmu["k"] = norm(cmu["name"])
    cat["k"] = norm(cat["primaryTitle"])
    m = cat.merge(cmu[["k", "year"]].rename(columns={"year": "cmu_year"}), on="k", how="left")
    m["hit"] = (m["cmu_year"] - m["year"]).abs() <= 1
    hit = m.groupby("tconst")["hit"].any()
    cat["in_cmu"] = cat["tconst"].map(hit).fillna(False)
    res = cat.groupby("cohort").agg(catalogo=("tconst", "size"), con_sinopsis_cmu=("in_cmu", "sum"))
    pop = cat[cat["in_popular_universe"]].groupby("cohort").agg(
        universo_popular=("tconst", "size"), popular_con_sinopsis_cmu=("in_cmu", "sum"))
    res = res.join(pop)
    res["cobertura_cmu"] = (res["con_sinopsis_cmu"] / res["catalogo"]).round(3)
    res["cobertura_cmu_popular"] = (res["popular_con_sinopsis_cmu"] / res["universo_popular"]).round(3)
    res.to_csv(TABLES / "cobertura_cmu.csv")
    return res


def main(argv: list[str]) -> None:
    ensure_dirs()
    step = argv[1] if len(argv) > 1 else "help"
    if step == "ingest":
        ingest.main()
    elif step == "catalog":
        print(clean.build().groupby("cohort").size())
    elif step == "coverage":
        print(coverage())
    elif step == "pilot":
        print(draw("piloto").groupby(["frame", "cohort"]).size())
    elif step == "main":
        print(draw("principal").groupby(["frame", "cohort"]).size())
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
