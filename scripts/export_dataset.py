"""Exporta el dataset por título (películas y series) a CSV y Parquet.

Lee web/films.json (generado por `python -m finales.web`) y decodifica sus
códigos a etiquetas legibles. No incluye la nota ni los votos de IMDb, que no
se pueden redistribuir; `tconst` permite cruzarlos con los datasets de IMDb.

    python scripts/export_dataset.py   # → data/dataset/feelgood_titulos.{csv,parquet}
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dataset"


def build() -> pd.DataFrame:
    F = json.loads((ROOT / "web" / "films.json").read_text(encoding="utf-8"))
    C = {c: i for i, c in enumerate(F["cols"])}

    def lab(lst, i):
        return lst[i] if i is not None and 0 <= i < len(lst) else None

    rows = []
    for f in F["films"]:
        serie = f[C["tipo"]] == 1
        r = {
            "tconst": f[C["tconst"]],
            "tipo": "serie" if serie else "pelicula",
            "titulo": f[C["titulo"]],
            "otro_titulo": f[C["original"]] or None,
            "anio": f[C["anio"]],
            "anio_en_curso": bool(f[C["anio_en_curso"]]),
            "pais_produccion": ["US", "ES", "US+ES"][f[C["pais"]]],
            "genero": lab(F["genres"], f[C["genero"]]),
            "publico": lab(F["publicos"], f[C["publico"]]),
            "feel_good": f[C["feel_good"]],
            "utopia": f[C["utopia"]],
            "final": lab(F["finals"], f[C["final"]]),
            "tono_cierre": None if serie else lab(F["tones"], f[C["tono_cierre"]]),
            "optimismo_personajes": f[C["optimismo"]],
            "tono_general": f[C["tono"]],
        }
        for k, opts in F["cats"].items():
            r[k] = lab(opts, f[C[k]])
        r["relaciones"] = "|".join(F["relaciones"][i] for i in f[C["relaciones"]]) or None
        r["paises_trama"] = "|".join(lab(F["paises"], i) or "Otro" for i in f[C["paises_trama"]]) or None
        r["rango_popularidad_anio"] = f[C["rango_votos_anio"]]
        r["tmdb_id"] = f[C["tmdb"]] or None
        rows.append(r)
    d = pd.DataFrame(rows)
    for c in ["anio", "rango_popularidad_anio", "tmdb_id"]:
        d[c] = d[c].astype("Int64")
    return d


def main() -> None:
    d = build()
    OUT.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT / "feelgood_titulos.csv", index=False)
    d.to_parquet(OUT / "feelgood_titulos.parquet", index=False)
    print(f"{len(d)} títulos ({(d.tipo == 'serie').sum()} series) → {OUT}")


if __name__ == "__main__":
    main()
