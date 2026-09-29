"""Carátulas de TMDB (v2). La clave se lee de ~/.config/finales/secrets.env (fuera del repositorio) y solo se usa
en el servidor para obtener `poster_path`; la web carga las imágenes de image.tmdb.org sin clave.
Atribución obligatoria: «This product uses the TMDB API but is not endorsed or certified by TMDB.»
"""
from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests

from .config import INTERIM

SECRETS = Path.home() / ".config" / "finales" / "secrets.env"
OUT = INTERIM / "tmdb_posters.csv"


def _key() -> str:
    if os.environ.get("TMDB_API_KEY"):
        return os.environ["TMDB_API_KEY"]
    for line in SECRETS.read_text().splitlines():
        if line.startswith("TMDB_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("Falta TMDB_API_KEY")


def _find(tconst: str, key: str, s: requests.Session) -> dict:
    for attempt in range(5):
        try:
            r = s.get(f"https://api.themoviedb.org/3/find/{tconst}",
                      params={"api_key": key, "external_source": "imdb_id", "language": "es-ES"}, timeout=20)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            r.raise_for_status()
            res = r.json().get("movie_results") or []
            if not res:
                return {"tconst": tconst, "tmdb_id": None, "poster_path": None, "titulo_es": None}
            m = res[0]
            return {"tconst": tconst, "tmdb_id": m.get("id"), "poster_path": m.get("poster_path"),
                    "titulo_es": m.get("title")}
        except requests.RequestException:
            time.sleep(1 + attempt)
    return {"tconst": tconst, "tmdb_id": None, "poster_path": None, "titulo_es": None, "error": True}


def fetch(tconsts: list[str], workers: int = 8) -> pd.DataFrame:
    done = pd.read_csv(OUT) if OUT.exists() else pd.DataFrame(columns=["tconst"])
    todo = sorted(set(tconsts) - set(done.tconst))
    key, s = _key(), requests.Session()
    with ThreadPoolExecutor(workers) as ex:
        rows = list(ex.map(lambda t: _find(t, key, s), todo))
    df = pd.concat([done, pd.DataFrame(rows)], ignore_index=True)
    df.to_csv(OUT, index=False)
    return df


if __name__ == "__main__":
    u = pd.read_csv(INTERIM / "universo_v2.csv")
    df = fetch(u.tconst.unique().tolist())
    print(len(df), df.poster_path.notna().sum())
