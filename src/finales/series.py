"""D-037: series de televisión. Universo: las 30 series (tvSeries y tvMiniSeries de ficción) más votadas en IMDb por
año de estreno, 1980-2026, estadounidenses y españolas. Se anota la serie entera y su final (o el último punto emitido
si sigue en emisión).

* País: TMDB `origin_country` (EE. UU. si contiene «US»; España si contiene «ES»), con Wikidata P495 = España como
  fuente adicional de candidatas españolas.
* Sinopsis: Wikipedia (en para EE. UU.; es, ca, gl, eu, en, fr, it, pt para España), secciones de argumento, premisa
  o resumen de temporadas; si no hay, la sinopsis de TMDB.
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests

from . import wikidump as w
from .config import INTERIM, RAW
from .ingest import _session, _wikidata_query
from .tmdb import _key

YEARS = range(1980, 2027)
TOP = 30
CAND = 150
MIN_VOTES = 50
EXCL_GENRES = {"Talk-Show", "Reality-TV", "News", "Game-Show", "Documentary", "Adult", "Short"}
SER = INTERIM / "series"
TMDB_TV = SER / "tmdb_tv"
HEAD_EN = {"plot", "plot summary", "synopsis", "story", "summary", "premise", "storyline", "overview",
           "series overview", "plot overview", "season synopses", "narrative", "setting and premise", "premise and plot"}
HEAD_ES = {"argumento", "sinopsis", "trama", "resumen", "historia", "premisa", "argumento de la serie",
           "trama de la serie", "resumen de la serie", "temporadas"}
HEADS = {"en": HEAD_EN, "es": HEAD_ES, "ca": {"argument", "sinopsi", "trama", "resum", "història", "premissa"},
         "gl": {"argumento", "sinopse", "trama", "resumo", "historia"},
         "eu": {"argumentua", "sinopsia", "laburpena", "istorioa"},
         "fr": {"synopsis", "résumé", "intrigue", "histoire", "concept"},
         "it": {"trama", "sinossi", "storia", "stagioni"}, "pt": {"sinopse", "enredo", "trama", "resumo", "história", "premissa"}}
WIKI_ES = ["es", "ca", "gl", "eu", "en", "fr", "it", "pt"]


def catalog() -> pd.DataFrame:
    SER.mkdir(parents=True, exist_ok=True)
    out = SER / "catalogo_series.csv"
    if out.exists():
        return pd.read_csv(out)
    chunks = []
    for ch in pd.read_csv(RAW / "title.basics.tsv.gz", sep="\t", na_values="\\N", quoting=3, dtype=str, chunksize=500_000):
        chunks.append(ch[ch.titleType.isin(["tvSeries", "tvMiniSeries"])])
    b = pd.concat(chunks, ignore_index=True)
    b["year"] = pd.to_numeric(b.startYear, errors="coerce")
    b = b[b.year.between(1980, 2026) & (b.isAdult != "1")]
    g = b.genres.fillna("").str.split(",")
    b = b[~g.apply(lambda x: bool(set(x) & EXCL_GENRES) or x == [""])]
    r = pd.read_csv(RAW / "title.ratings.tsv.gz", sep="\t", na_values="\\N")
    b = b.merge(r, on="tconst")
    b = b[b.numVotes >= MIN_VOTES].copy()
    b["year"] = b.year.astype(int)
    b["rank_global"] = b.groupby("year").numVotes.rank(method="first", ascending=False).astype(int)
    b.to_csv(out, index=False)
    return b


def wikidata_es(tconsts: set) -> dict:
    """Series con país de origen España en Wikidata (P495 = Q29) e id de IMDb → {tconst: (qid, países)}."""
    p = SER / "wikidata_es_series.csv"
    if not p.exists():
        s = _session()
        q = """SELECT ?item ?imdb (GROUP_CONCAT(DISTINCT ?c; separator="|") AS ?cs) WHERE {
          ?item wdt:P495 wd:Q29 ; wdt:P345 ?imdb . ?item wdt:P31/wdt:P279* wd:Q15416 .
          ?item wdt:P495 ?cc . BIND(STRAFTER(STR(?cc), "entity/") AS ?c) } GROUP BY ?item ?imdb"""
        b = _wikidata_query(q, s, "series ES", 5) or []
        pd.DataFrame([{"tconst": x["imdb"]["value"], "wikidata_id": x["item"]["value"].rsplit("/", 1)[-1],
                       "countries": x["cs"]["value"]} for x in b]).to_csv(p, index=False)
    d = pd.read_csv(p)
    return {r.tconst: (r.wikidata_id, r.countries) for r in d.itertuples() if r.tconst in tconsts}


def tmdb_tv(tconsts: list[str]) -> pd.DataFrame:
    TMDB_TV.mkdir(parents=True, exist_ok=True)
    key, s = _key(), requests.Session()

    def get(t):
        p = TMDB_TV / f"{t}.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        rec = {"tconst": t}
        for _ in range(5):
            try:
                r = s.get(f"https://api.themoviedb.org/3/find/{t}", params={"api_key": key, "external_source": "imdb_id",
                                                                         "language": "es-ES"}, timeout=20)
                if r.status_code == 429:
                    time.sleep(2)
                    continue
                res = r.json().get("tv_results") or []
                if res:
                    m = res[0]
                    d = s.get(f"https://api.themoviedb.org/3/tv/{m['id']}", params={"api_key": key, "language": "en-US"},
                              timeout=20).json()
                    rec.update({"tmdb_id": m["id"], "titulo_es": m.get("name"), "overview_es": m.get("overview") or None,
                                "poster_path": m.get("poster_path"), "overview_en": d.get("overview") or None,
                                "origin_country": "|".join(d.get("origin_country") or []),
                                "original_language": d.get("original_language"), "status": d.get("status"),
                                "seasons": d.get("number_of_seasons"), "episodes": d.get("number_of_episodes"),
                                "last_air_date": d.get("last_air_date")})
                break
            except (requests.RequestException, ValueError):
                time.sleep(1)
        p.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
        return rec
    with ThreadPoolExecutor(12) as ex:
        return pd.DataFrame(list(ex.map(get, tconsts)))


def tmdb_discover_es() -> set:
    """Series con país de origen España en TMDB (discover), para no perder las que no están en Wikidata."""
    p = SER / "tmdb_discover_es.json"
    if p.exists():
        return set(json.loads(p.read_text()))
    key, s = _key(), requests.Session()
    ids = []
    for y in YEARS:
        for page in range(1, 6):
            r = s.get("https://api.themoviedb.org/3/discover/tv", params={"api_key": key, "with_origin_country": "ES",
                      "first_air_date_year": y, "sort_by": "vote_count.desc", "page": page}, timeout=20).json()
            ids += [x["id"] for x in r.get("results", [])]
            if page >= r.get("total_pages", 1):
                break

    def ext(i):
        for _ in range(4):
            try:
                return s.get(f"https://api.themoviedb.org/3/tv/{i}/external_ids", params={"api_key": key}, timeout=20).json().get("imdb_id")
            except (requests.RequestException, ValueError):
                time.sleep(1)
    with ThreadPoolExecutor(12) as ex:
        tt = [t for t in ex.map(ext, ids) if t]
    p.write_text(json.dumps(tt))
    return set(tt)


def sitelinks(tconsts: list[str]) -> pd.DataFrame:
    """Enlaces a Wikipedia por id de IMDb (P345) en los idiomas usados."""
    p = SER / "sitelinks_series.csv"
    have = pd.read_csv(p) if p.exists() else pd.DataFrame(columns=["tconst", "wiki", "url"])
    todo = sorted(set(tconsts) - set(have.tconst))
    s, rows = _session(), []
    for i in range(0, len(todo), 200):
        vals = " ".join(f'"{t}"' for t in todo[i:i + 200])
        q = f"""SELECT ?imdb ?art ?wiki WHERE {{ VALUES ?imdb {{ {vals} }} ?item wdt:P345 ?imdb .
          ?art schema:about ?item ; schema:isPartOf ?wiki .
          FILTER(?wiki IN ({",".join(f"<https://{x}.wikipedia.org/>" for x in WIKI_ES)})) }}"""
        b = _wikidata_query(q, s, f"sitelinks series {i}", 5) or []
        rows += [{"tconst": x["imdb"]["value"], "url": x["art"]["value"],
                  "wiki": x["wiki"]["value"].split("//")[1].split(".")[0]} for x in b]
        rows += [{"tconst": t, "wiki": None, "url": None} for t in todo[i:i + 200]]  # marca de consultado
    out = pd.concat([have, pd.DataFrame(rows)], ignore_index=True)
    out.to_csv(p, index=False)
    return out[out.url.notna()]


def _clean(wt: str) -> str:
    import re
    import mwparserfromhell
    body = mwparserfromhell.parse(wt)
    for tag in body.filter_tags(recursive=True):
        if str(tag.tag).lower() in ("ref", "gallery", "table"):
            try:
                body.remove(tag)
            except ValueError:
                pass
    t = body.strip_code(normalize=True, collapse=True)
    t = re.sub(r"^=+.*?=+\s*$", "", t, flags=re.M)
    t = re.sub(r"\[\[(File|Image|Archivo|Imagen|Fitxer|Fichier):[^\]]*\]\]", "", t)
    t = re.sub(r"^\s*(thumb|miniatura|right|left)\|.*$", "", t, flags=re.M)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t).strip()


KEYS = ("plot", "premise", "synops", "story", "summar", "overview", "argument", "sinops", "trama", "premis", "resum",
        "intrigue", "enredo", "sinossi", "laburpen", "season", "temporada", "saison", "stagion")


def extract_series(wikitext: str, heads: set) -> str | None:
    """Secciones argumentales (todas las de nivel 2 cuyo título coincide) y, si hay poco texto, la entradilla."""
    import mwparserfromhell
    H = list(w.H2_RE.finditer(wikitext))
    parts = []
    for i, h in enumerate(H):
        head = mwparserfromhell.parse(h.group(1)).strip_code().strip().lower()
        if head in heads or any(k in head for k in KEYS):
            if any(x in head for x in ("reception", "recepción", "rating", "audiencia", "broadcast", "episod", "cast", "reparto", "home media")):
                continue
            end = H[i + 1].start() if i + 1 < len(H) else len(wikitext)
            parts.append(_clean(wikitext[h.end():end]))
    txt = "\n".join(p for p in parts if p)
    if w.word_count(txt) < 250:
        lead = _clean(wikitext[:H[0].start()] if H else wikitext)
        txt = (lead + "\n" + txt).strip()
    return txt or None


def fetch_wiki(sel: pd.DataFrame, links: pd.DataFrame) -> dict:
    """Sinopsis de Wikipedia para cada serie: primer idioma con ≥120 palabras en sus secciones argumentales."""
    lk = {(r.tconst, r.wiki): r.url for r in links.itertuples()}
    sess = w.session()
    got = {}
    for wk in WIKI_ES:
        need = [t for t in sel.tconst if t not in got and (t, wk) in lk and (wk == "en" or sel.set_index("tconst").at[t, "country_frame"] == "ES")]
        if not need:
            continue
        titles = {w.title_from_url(lk[(t, wk)]) for t in need}
        # índice propio para series (no se mezcla con el de películas)
        orig = dict(w.WIKIS[wk])
        w.WIKIS[wk] = {**orig, "offsets": SER / f"offsets_{wk}.csv", "syn_dir": SER / f"syn_{wk}", "headings": HEADS[wk]}
        try:
            off = w.build_offsets(titles, wiki=wk)

            def one(t):
                pth = SER / f"syn2_{wk}" / f"{t}.json"
                if pth.exists():
                    return t, json.loads(pth.read_text(encoding="utf-8"))
                title = w.title_from_url(lk[(t, wk)])
                row = off[off.title == title]
                rec = {"tconst": t, "wiki": wk, "url": lk[(t, wk)], "text": None, "license": "CC BY-SA 4.0"}
                if not row.empty:
                    r0 = row.iloc[0]
                    try:
                        page = w.find_page(w.read_block(int(r0.offset), None if pd.isna(r0.end) else int(r0.end), sess, wk), title)
                    except Exception:
                        page = None
                    if page and not page["wikitext"].lstrip().upper().startswith(("#REDIRECT", "#REDIRECCIÓN")):
                        rec.update({"text": extract_series(page["wikitext"], HEADS[wk]), "revision": page["revision"],
                                    "revision_url": f"https://{w.WIKIS[wk]['host']}/w/index.php?oldid={page['revision']}"})
                pth.parent.mkdir(parents=True, exist_ok=True)
                pth.write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
                return t, rec
            with ThreadPoolExecutor(6) as ex:
                for t, rec in ex.map(one, need):
                    if rec and w.word_count(rec.get("text")) >= 100:
                        got[t] = wk
        finally:
            w.WIKIS[wk] = orig
    return got


def build() -> pd.DataFrame:
    cat = catalog()
    cand = cat[cat.rank_global <= CAND]
    wes = wikidata_es(set(cat.tconst))
    disc = tmdb_discover_es()
    extra_es = cat[(cat.tconst.isin(wes) | cat.tconst.isin(disc)) & (cat.rank_global > CAND)]
    cand = pd.concat([cand, extra_es]).drop_duplicates("tconst")
    tm = tmdb_tv(cand.tconst.tolist()).drop_duplicates("tconst").set_index("tconst")
    cand = cand.join(tm, on="tconst")
    oc = cand.origin_country.fillna("").str.split("|")
    cand["is_us"] = oc.apply(lambda x: "US" in x)
    # D-038: como en el cine (D-033), fuera las coproducciones de origen mayoritariamente extranjero: España debe ser
    # el único país de origen en TMDB o, si hay varios, el idioma original debe ser español, catalán, euskera o gallego;
    # sin datos de TMDB, Wikidata debe dar solo España.
    ES_LANG = {"es", "ca", "eu", "gl"}
    cand["is_es"] = [("ES" in o and (o == ["ES"] or lang in ES_LANG)) if isinstance(oc0, str) else (t in wes and wes[t][1] == "Q29")
                     for o, oc0, lang, t in zip(oc, cand.origin_country, cand.original_language, cand.tconst)]
    us = cand[cand.is_us].sort_values(["year", "numVotes"], ascending=[True, False]).groupby("year").head(TOP).assign(country_frame="US")
    es = cand[cand.is_es].sort_values(["year", "numVotes"], ascending=[True, False]).groupby("year").head(TOP).assign(country_frame="ES")
    sel = pd.concat([us, es], ignore_index=True)
    sel["votes_rank_in_year"] = sel.groupby(["country_frame", "year"]).numVotes.rank(method="first", ascending=False).astype(int)
    links = sitelinks(sel.tconst.unique().tolist())
    got = fetch_wiki(sel, links)
    lk = {(r.tconst, r.wiki): r.url for r in links.itertuples()}
    sel["synopsis_wiki"] = sel.tconst.map(got)
    sel["wiki_url"] = [lk.get((t, s)) for t, s in zip(sel.tconst, sel.synopsis_wiki)]
    # respaldo TMDB (sinopsis comercial, de premisa)
    ov = lambda r: r.overview_es if r.country_frame == "ES" and isinstance(r.overview_es, str) else (
        r.overview_en if isinstance(r.overview_en, str) else r.overview_es)
    sel["tmdb_text"] = [ov(r) for r in sel.itertuples()]
    m = sel.synopsis_wiki.isna() & sel.tmdb_text.fillna("").str.split().str.len().ge(25)
    sel.loc[m, "synopsis_wiki"] = "tmdb"
    sel["anio_en_curso"] = sel.year >= 2026
    sel["en_emision"] = sel.status.isin(["Returning Series", "In Production", "Planned"])
    sel.to_csv(SER / "universo_series.csv", index=False)
    print(sel.groupby("country_frame").size().to_dict(), sel.groupby("country_frame").synopsis_wiki.value_counts(dropna=False).to_dict())
    return sel


def synopsis(tconst: str, src: str, tmdb_text: str | None = None) -> dict | None:
    if src == "tmdb":
        return {"text": tmdb_text, "wiki": "tmdb"}
    p = SER / f"syn2_{src}" / f"{tconst}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def blind_id(tconst: str) -> str:
    import hashlib
    return "S" + hashlib.sha256(f"blind-series|20260930|{tconst}".encode()).hexdigest()[:8].upper()


def make_batches(stage: str = "series", batch_size: int = 40) -> pd.DataFrame:
    from . import blinding
    from .annotation import ANNOT, KEY_DIR
    u = pd.read_csv(SER / "universo_series.csv").drop_duplicates("tconst")
    u = u[u.synopsis_wiki.notna()]
    recs = []
    for r in u.itertuples():
        syn = synopsis(r.tconst, r.synopsis_wiki, r.tmdb_text)
        if not syn or not syn.get("text"):
            continue
        wt = r.wiki_url.rsplit("/wiki/", 1)[-1].replace("_", " ") if isinstance(r.wiki_url, str) else None
        titles = blinding.title_variants(r.primaryTitle, r.originalTitle, wt, r.titulo_es if isinstance(r.titulo_es, str) else None)
        text, trunc = blinding.truncate_words(blinding.mask(syn["text"], titles), 1100)
        recs.append({"id": blind_id(r.tconst), "tconst": r.tconst, "sinopsis": text, "idioma": r.synopsis_wiki,
                     "palabras_originales": len(syn["text"].split()), "truncada": trunc})
    df = pd.DataFrame(recs).sort_values("id").reset_index(drop=True)
    df["batch"] = [f"{stage}_{i // batch_size + 1:02d}" for i in range(len(df))]
    out = ANNOT / "batches" / stage
    out.mkdir(parents=True, exist_ok=True)
    for b, g in df.groupby("batch"):
        with open(out / f"{b}.jsonl", "w", encoding="utf-8") as fh:
            for x in g.itertuples():
                fh.write(json.dumps({"id": x.id, "sinopsis": x.sinopsis}, ensure_ascii=False) + "\n")
    df.drop(columns=["sinopsis"]).to_csv(KEY_DIR / f"{stage}_key.csv", index=False)
    return df


if __name__ == "__main__":
    build()
