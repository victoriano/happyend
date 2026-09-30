"""D-033: universo español sin coproducciones extranjeras.

Una película del catálogo español (P495 incluye España en Wikidata) cuenta como española si:
  a) Wikidata no le asigna ningún otro país de origen (producción solo española), o
  b) es coproducción y TMDB incluye España en `origin_country` (país de origen principal, equivalente al
     «país principal» de IMDb), o
  c) es coproducción, TMDB no da `origin_country`, y España está entre sus `production_countries` con idioma
     original español, catalán, euskera o gallego.
Por año se toman las 15 más votadas que cumplan la regla y tengan sinopsis utilizable (española o, si falta,
inglesa), igual que en D-023/D-024. Se consultan como mucho las 90 más votadas de cada año.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from . import wikidump as w
from .config import INTERIM
from .spain import TOP_ES
from .tmdb import _key

ORIG = INTERIM / "tmdb_origen_es.csv"
LANGS = {"es", "ca", "eu", "gl"}
MAX_RANK = 90


def _tmdb_origin(tconsts):
    have = pd.read_csv(ORIG) if ORIG.exists() else pd.DataFrame(columns=["tconst"])
    todo = sorted(set(tconsts) - set(have.tconst))
    if not todo:
        return have
    key, s = _key(), requests.Session()

    def get(t):
        for _ in range(4):
            try:
                r = s.get(f"https://api.themoviedb.org/3/find/{t}", params={"api_key": key, "external_source": "imdb_id"}, timeout=20)
                if r.status_code == 429:
                    time.sleep(2)
                    continue
                res = r.json().get("movie_results") or []
                if not res:
                    return {"tconst": t}
                d = s.get(f"https://api.themoviedb.org/3/movie/{res[0]['id']}", params={"api_key": key}, timeout=20).json()
                return {"tconst": t, "tmdb_id": res[0]["id"], "origin_country": "|".join(d.get("origin_country") or []),
                        "production_countries": "|".join(x["iso_3166_1"] for x in d.get("production_countries") or []),
                        "original_language": d.get("original_language")}
            except requests.RequestException:
                time.sleep(1)
        return {"tconst": t, "error": 1}
    with ThreadPoolExecutor(8) as ex:
        new = pd.DataFrame(list(ex.map(get, todo)))
    out = pd.concat([have, new], ignore_index=True)
    out.to_csv(ORIG, index=False)
    return out


def es_rule(countries: str, o) -> tuple[bool, str]:
    cs = set(str(countries).split("|"))
    if cs == {"Q29"}:
        return True, "solo_espana_wikidata"
    if o is None:
        return False, "sin_tmdb"
    oc = str(o.get("origin_country") or "")
    oc = "" if oc == "nan" else oc
    if oc:
        return ("ES" in oc.split("|")), ("tmdb_origen_es" if "ES" in oc.split("|") else "coproduccion_origen_extranjero")
    pc = str(o.get("production_countries") or "").split("|")
    ok = "ES" in pc and o.get("original_language") in LANGS
    return ok, ("tmdb_produccion_es_idioma" if ok else "coproduccion_sin_origen")


def build() -> pd.DataFrame:
    cat = pd.concat([pd.read_csv(INTERIM / "catalog_es.csv"), pd.read_csv(INTERIM / "catalog_es_ext.csv")], ignore_index=True)
    cat = cat[cat.votes_rank_in_year <= MAX_RANK].sort_values(["year", "votes_rank_in_year"])
    orig = _tmdb_origin(cat.tconst).drop_duplicates("tconst").set_index("tconst")
    s = w.session()
    off_es = w.build_offsets(set(cat.eswiki_url.dropna().map(w.title_from_url)), wiki="es")
    off_en = w.build_offsets(set(cat.enwiki_url.dropna().map(w.title_from_url)), wiki="en")
    rows = []
    for y, g in cat.groupby("year"):
        n = 0
        for r in g.itertuples():
            if n >= TOP_ES:
                break
            o = orig.loc[r.tconst].to_dict() if r.tconst in orig.index else None
            ok, why = es_rule(r.countries, o)
            src = None
            if ok:
                if isinstance(r.eswiki_url, str) and w.word_count(w.fetch_one(r.tconst, r.eswiki_url, off_es, s, wiki="es").get("text")) >= 120:
                    src = "es"
                elif isinstance(r.enwiki_url, str) and w.word_count(w.fetch_one(r.tconst, r.enwiki_url, off_en, s, wiki="en").get("text")) >= 120:
                    src = "en"
            rows.append({"tconst": r.tconst, "year": y, "votes_rank_in_year": r.votes_rank_in_year, "espanola": ok,
                         "motivo": why, "synopsis_wiki": src, "entra": bool(ok and src)})
            n += bool(ok and src)
    log = pd.DataFrame(rows)
    log.to_csv(INTERIM / "seleccion_es_v3_log.csv", index=False)
    sel = cat.merge(log[log.entra][["tconst", "synopsis_wiki", "motivo"]], on="tconst")
    sel["country_frame"] = "ES"
    sel["anio_en_curso"] = sel.year >= 2026
    sel.to_csv(INTERIM / "universo_es_v3.csv", index=False)
    print(len(sel), sel.groupby("year").size().describe().to_dict())
    return sel


if __name__ == "__main__":
    build()
