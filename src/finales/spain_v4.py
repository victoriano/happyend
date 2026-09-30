"""D-035: universo español ampliado.

* Catálogo: largometrajes de ficción con España entre los países de origen (Wikidata P495), ≥50 votos en IMDb
  (antes 200), sin exigir artículo de Wikipedia.
* Españolas: regla de D-033 (sin coproducciones con origen principal extranjero).
* Por año: las 30 más votadas que cumplan la regla (1980-2026).
* Sinopsis, en este orden: Wikipedia en español, catalán, gallego, euskera, inglés, francés, italiano, portugués
  (sección de argumento de al menos 120 palabras); si no hay, la sinopsis de TMDB (en español o, si falta, en inglés),
  que suele ser breve y no contar el final. Las de TMDB no se publican en la web, solo se enlazan.
"""
from __future__ import annotations

import copy
import json
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import requests

from . import clean, wikidump as w
from .config import INTERIM, load
from .ingest import WDQS, _session, _wikidata_query
from .spain_filtro import _tmdb_origin, es_rule
from .tmdb import _key

MIN_VOTES = 50
TOP = 30
WIKI_ORDER = ["es", "ca", "gl", "eu", "en", "fr", "it", "pt"]
TMDB_DIR = INTERIM / "synopses_tmdb"


def catalog() -> pd.DataFrame:
    cfg = copy.deepcopy(load())
    cfg["periodo"]["year_max"] = 2026
    cfg["filtros_catalogo"]["min_votos_catalogo"] = MIN_VOTES
    imdb = pd.read_pickle(INTERIM / "imdb_movies.pkl")
    wd = pd.concat([pd.read_csv(f, dtype=str) for f in sorted((INTERIM / "wikidata_es_by_year").glob("*.csv"))],
                   ignore_index=True)
    first = lambda s: next((x for x in s if isinstance(x, str)), None)
    qid = wd.groupby("tconst").wikidata_id.agg(first)
    wd2 = wd.copy()
    # sin exigir artículo: el filtro de artículo del catálogo estadounidense se neutraliza con un marcador único
    wd2["enwiki_url"] = "wikidata:" + wd2["wikidata_id"]
    cat, _ = clean.apply_filters(imdb, clean.summarise_wikidata(wd2), cfg)
    cat["wikidata_id"] = cat.tconst.map(qid)
    cat["votes_rank_in_year"] = cat.groupby("year")["numVotes"].rank(method="first", ascending=False).astype(int)
    cat.to_csv(INTERIM / "catalog_es_v4.csv", index=False)
    return cat


def sitelinks(qids: list[str]) -> pd.DataFrame:
    s = _session()
    rows = []
    for i in range(0, len(qids), 150):
        vals = " ".join(f"wd:{q}" for q in qids[i:i + 150])
        q = f"""SELECT ?item ?art ?wiki WHERE {{ VALUES ?item {{ {vals} }}
          ?art schema:about ?item ; schema:isPartOf ?wiki .
          FILTER(?wiki IN ({",".join(f"<https://{x}.wikipedia.org/>" for x in WIKI_ORDER)})) }}"""
        b = _wikidata_query(q, s, f"sitelinks {i}", 5) or []
        rows += [{"wikidata_id": x["item"]["value"].rsplit("/", 1)[-1], "url": x["art"]["value"],
                  "wiki": x["wiki"]["value"].split("//")[1].split(".")[0]} for x in b]
    return pd.DataFrame(rows, columns=["wikidata_id", "url", "wiki"])


def tmdb_overview(tconsts: list[str]) -> dict:
    TMDB_DIR.mkdir(parents=True, exist_ok=True)
    key, s = _key(), requests.Session()

    def get(t):
        p = TMDB_DIR / f"{t}.json"
        if p.exists():
            return t, json.loads(p.read_text(encoding="utf-8"))
        rec = {"tconst": t, "text": None, "wiki": "tmdb"}
        for _ in range(4):
            try:
                r = s.get(f"https://api.themoviedb.org/3/find/{t}", params={"api_key": key, "external_source": "imdb_id",
                                                                       "language": "es-ES"}, timeout=20)
                if r.status_code == 429:
                    time.sleep(2)
                    continue
                res = (r.json().get("movie_results") or [])
                if res:
                    m = res[0]
                    txt, lang = m.get("overview"), "es"
                    if not txt:
                        e = s.get(f"https://api.themoviedb.org/3/movie/{m['id']}", params={"api_key": key,
                                                                                            "language": "en-US"}, timeout=20).json()
                        txt, lang = e.get("overview"), "en"
                    rec.update({"text": txt or None, "lang": lang, "revision_url": f"https://www.themoviedb.org/movie/{m['id']}",
                                "source": "TMDB API (sinopsis)", "license": "TMDB, solo enlace"})
                break
            except requests.RequestException:
                time.sleep(1)
        p.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        return t, rec
    with ThreadPoolExecutor(8) as ex:
        return dict(ex.map(get, tconsts))


def build() -> pd.DataFrame:
    cat = catalog()
    cand = cat[cat.votes_rank_in_year <= 200].sort_values(["year", "votes_rank_in_year"])
    orig = _tmdb_origin(cand.tconst).drop_duplicates("tconst").set_index("tconst")
    ok = []
    for r in cand.itertuples():
        o = orig.loc[r.tconst].to_dict() if r.tconst in orig.index else None
        ok.append(es_rule(r.countries, o))
    cand = cand.assign(espanola=[a for a, _ in ok], motivo=[b for _, b in ok])
    sel = cand[cand.espanola].groupby("year").head(TOP).copy()
    links = sitelinks(sel.wikidata_id.dropna().unique().tolist())
    lk = {(r.wikidata_id, r.wiki): r.url for r in links.itertuples()}
    sess = w.session()
    offs = {}
    for wk in WIKI_ORDER:
        titles = {w.title_from_url(u) for (q, k), u in lk.items() if k == wk}
        offs[wk] = w.build_offsets(titles, wiki=wk) if titles else None
    srcs, urls = [], []
    for r in sel.itertuples():
        got = None
        for wk in WIKI_ORDER:
            u = lk.get((r.wikidata_id, wk))
            if u and offs[wk] is not None:
                rec = w.fetch_one(r.tconst, u, offs[wk], sess, wiki=wk)
                if w.word_count(rec.get("text")) >= 120:
                    got = (wk, u)
                    break
        srcs.append(got[0] if got else None)
        urls.append(got[1] if got else None)
    sel["synopsis_wiki"], sel["wiki_url"] = srcs, urls
    miss = sel[sel.synopsis_wiki.isna()].tconst.tolist()
    tm = tmdb_overview(miss)
    sel.loc[sel.synopsis_wiki.isna(), "synopsis_wiki"] = [
        ("tmdb" if tm[t].get("text") and w.word_count(tm[t]["text"]) >= 25 else None) for t in miss]
    for wk in ("es", "en"):
        sel[f"{wk}wiki_url"] = [lk.get((q, wk)) for q in sel.wikidata_id]
    sel["country_frame"] = "ES"
    sel["anio_en_curso"] = sel.year >= 2026
    sel.to_csv(INTERIM / "universo_es_v4.csv", index=False)
    print(len(sel), sel.synopsis_wiki.value_counts(dropna=False).to_dict())
    print(sel.groupby("year").size().describe().to_dict())
    return sel


if __name__ == "__main__":
    build()
