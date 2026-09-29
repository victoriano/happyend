"""Sinopsis desde el volcado público de Wikipedia en inglés (CC BY-SA 4.0), por acceso aleatorio.

Motivo (registro de decisiones D-016): la API REST de Wikipedia devolvía HTTP 429 de forma sistemática
desde la IP compartida del entorno. El volcado multistream permite descargar solo los bloques bz2 que
contienen los artículos necesarios mediante peticiones HTTP Range, sin raspar páginas y con una
versión fechada y verificable (checksum SHA-1 publicado por Wikimedia).

Volcado usado: enwiki-20260901-pages-articles-multistream (config: DUMP_DATE).
"""
from __future__ import annotations

import bz2
import json
import re
import time
from pathlib import Path
from urllib.parse import quote, unquote

import mwparserfromhell
import pandas as pd
import requests

from . import provenance
from .config import INTERIM, RAW, load

DUMP_DATE = "20260901"
BASE = f"https://dumps.wikimedia.org/enwiki/{DUMP_DATE}/"
DUMP_NAME = f"enwiki-{DUMP_DATE}-pages-articles-multistream.xml.bz2"
INDEX_NAME = f"enwiki-{DUMP_DATE}-pages-articles-multistream-index.txt.bz2"
PLOT_HEADINGS = {"plot", "plot summary", "synopsis", "story", "summary", "premise", "storyline",
                 "plot synopsis", "narrative"}
SYN_DIR = INTERIM / "synopses"
OFFSETS = INTERIM / f"wikidump_offsets_{DUMP_DATE}.csv"


def title_from_url(url: str) -> str:
    return unquote(url.rsplit("/wiki/", 1)[-1]).replace("_", " ")


def fetch_index(force: bool = False) -> Path:
    dest = RAW / INDEX_NAME
    if not dest.exists() or force:
        from .ingest import download
        download(BASE + INDEX_NAME, dest, "wikipedia")
    return dest


def build_offsets(titles: set[str], force: bool = False) -> pd.DataFrame:
    """Recorre el índice (offset:page_id:título) y guarda offset inicial/final del bloque de cada título."""
    if OFFSETS.exists() and not force:
        df = pd.read_csv(OFFSETS, dtype={"title": str})
        if titles <= set(df["title"]):
            return df
    idx = fetch_index()
    found, all_offsets = {}, []
    last = None
    with bz2.open(idx, "rt", encoding="utf-8") as fh:
        for line in fh:
            off, pid, title = line.rstrip("\n").split(":", 2)
            title = _unescape(title)
            off = int(off)
            if off != last:
                all_offsets.append(off)
                last = off
            if title in titles:
                found[title] = (off, int(pid))
    import bisect
    rows = []
    for t, (off, pid) in found.items():
        i = bisect.bisect_right(all_offsets, off)
        end = all_offsets[i] if i < len(all_offsets) else None
        rows.append({"title": t, "page_id": pid, "offset": off, "end": end})
    df = pd.DataFrame(rows)
    df.to_csv(OFFSETS, index=False)
    return df


PAGE_RE = re.compile(r"<page>.*?</page>", re.S)


def _unescape(s: str) -> str:
    import html
    return html.unescape(s)


def read_block(offset: int, end: int | None, session: requests.Session) -> str:
    rng = f"bytes={offset}-{'' if end is None else end - 1}"
    for attempt in range(6):
        try:
            r = session.get(BASE + DUMP_NAME, headers={"Range": rng}, timeout=120)
            if r.status_code == 206:
                return bz2.decompress(r.content).decode("utf-8")
        except (requests.RequestException, OSError, EOFError):
            pass
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"No se pudo leer el bloque {rng}")


def find_page(block: str, title: str) -> dict | None:
    for m in PAGE_RE.finditer(block):
        p = m.group(0)
        t = re.search(r"<title>(.*?)</title>", p)
        if t and _unescape(t.group(1)) == title:
            rev = re.search(r"<revision>\s*<id>(\d+)</id>", p)
            ts = re.search(r"<timestamp>(.*?)</timestamp>", p)
            txt = re.search(r"<text[^>]*>(.*?)</text>", p, re.S)
            return {"revision": rev.group(1) if rev else None,
                    "revision_timestamp": ts.group(1) if ts else None,
                    "wikitext": _unescape(txt.group(1)) if txt else ""}
    return None


def plot_from_wikitext(wikitext: str) -> tuple[str | None, str | None]:
    """Devuelve (encabezado, texto plano) de la primera sección de nivel 2 argumental."""
    code = mwparserfromhell.parse(wikitext)
    for sec in code.get_sections(levels=[2], include_lead=False):
        heads = sec.filter_headings()
        if not heads:
            continue
        heading = heads[0].title.strip_code().strip()
        if heading.lower() in PLOT_HEADINGS:
            body = mwparserfromhell.parse(str(sec)[len(str(heads[0])):])
            for tag in body.filter_tags(recursive=True):
                if str(tag.tag).lower() in ("ref", "gallery"):
                    try:
                        body.remove(tag)
                    except ValueError:
                        pass
            text = body.strip_code(normalize=True, collapse=True)
            text = re.sub(r"^=+.*?=+\s*$", "", text, flags=re.M)      # subencabezados
            text = re.sub(r"\[\[(File|Image):[^\]]*\]\]", "", text)
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n\s*\n+", "\n", text).strip()
            return heading, (text or None)
    return None, None


def fetch_one(tconst: str, enwiki_url: str, offsets: pd.DataFrame, session: requests.Session,
              force: bool = False) -> dict:
    SYN_DIR.mkdir(parents=True, exist_ok=True)
    out = SYN_DIR / f"{tconst}.json"
    if out.exists() and not force:
        return json.loads(out.read_text(encoding="utf-8"))
    title = title_from_url(enwiki_url)
    rec = {"tconst": tconst, "enwiki_url": enwiki_url, "title": title, "source": f"enwiki dump {DUMP_DATE}",
           "dump_url": BASE + DUMP_NAME, "retrieved_at": provenance.now_utc(),
           "license": provenance.LICENSES["wikipedia"]}
    row = offsets[offsets["title"] == title]
    if row.empty:
        rec.update({"status": "titulo_no_en_volcado", "text": None})
    else:
        r = row.iloc[0]
        page = find_page(read_block(int(r["offset"]), None if pd.isna(r["end"]) else int(r["end"]), session), title)
        if page is None:
            rec.update({"status": "pagina_no_encontrada_en_bloque", "text": None})
        elif page["wikitext"].lstrip().upper().startswith("#REDIRECT"):
            rec.update({"status": "redireccion", "text": None})
        else:
            heading, text = plot_from_wikitext(page["wikitext"])
            rec.update({"page_id": int(r["page_id"]), "revision": page["revision"],
                        "revision_timestamp": page["revision_timestamp"], "heading": heading, "text": text,
                        "revision_url": f"https://en.wikipedia.org/w/index.php?oldid={page['revision']}",
                        "status": "ok" if text else "sin_seccion_argumental"})
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    return rec


def session() -> requests.Session:
    s = requests.Session()
    s.headers["User-Agent"] = load()["project"]["user_agent"].encode("ascii", "ignore").decode()
    return s


def word_count(text: str | None) -> int:
    return len(text.split()) if text else 0
