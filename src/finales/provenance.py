"""Registro de procedencia: cada fuente descargada/consultada deja una línea JSON."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import PROVENANCE

LICENSES = {
    "imdb": "IMDb Non-Commercial Datasets: uso personal y no comercial; "
            "atribución 'Information courtesy of IMDb (https://www.imdb.com). Used with permission.'; "
            "prohibido republicar/alterar como base de datos. https://developer.imdb.com/non-commercial-datasets/",
    "wikidata": "CC0 1.0 (dominio público). https://www.wikidata.org/wiki/Wikidata:Licensing",
    "wikipedia": "CC BY-SA 4.0 (texto de Wikipedia en inglés); atribución por URL de revisión. "
                 "https://en.wikipedia.org/wiki/Wikipedia:Copyrights",
    "cmu": "CC BY-SA (CMU Movie Summary Corpus, Bamman, O'Connor y Smith, ACL 2013). "
           "https://www.cs.cmu.edu/~ark/personas/",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record(source: str, url: str, local_path: Path | None = None, notes: str = "",
           log: Path = PROVENANCE) -> dict:
    entry = {
        "source": source,
        "url": url,
        "retrieved_at": now_utc(),
        "license": LICENSES.get(source, "desconocida"),
        "local_path": str(local_path.relative_to(log.parent.parent)) if local_path else None,
        "sha256": sha256(local_path) if local_path and local_path.is_file() else None,
        "notes": notes,
    }
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
