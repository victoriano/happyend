"""Marcos de muestra y extracción estratificada reproducible.

Principios:
* Orden aleatorio estable: cada película recibe una clave hash(semilla, marco, tconst). El orden no
  depende del orden de filas del catálogo, así que añadir películas no altera el orden relativo.
* Marco POPULAR: universo = las N películas con más votos IMDb de cada año (config marcos.popular).
  Asignación por cohorte fija; dentro de cada cohorte, proporcional al peso de cada género principal.
* Marco AMPLIO: universo = todo el catálogo elegible. Asignación por cohorte fija, repartida a partes
  iguales entre tramos de popularidad (terciles de votos dentro del año) y, dentro de cada tramo,
  proporcional por género. Se guardan pesos de diseño (N_estrato / n_estrato).
* Películas sin sinopsis utilizable se sustituyen por la siguiente del mismo estrato; se registran.
* Las películas del piloto quedan excluidas de la muestra principal.
"""
from __future__ import annotations

import hashlib
from typing import Callable

import numpy as np
import pandas as pd


def stable_key(tconst: str, seed: int, salt: str) -> float:
    h = hashlib.sha256(f"{seed}|{salt}|{tconst}".encode()).hexdigest()
    return int(h[:15], 16) / float(16 ** 15)


def largest_remainder(shares: pd.Series, n: int) -> pd.Series:
    """Reparte n unidades proporcionalmente a `shares` con el método del resto mayor (Hamilton)."""
    if n <= 0 or shares.sum() == 0:
        return pd.Series(0, index=shares.index, dtype=int)
    raw = shares / shares.sum() * n
    base = np.floor(raw).astype(int)
    rem = n - base.sum()
    order = (raw - base).sort_values(ascending=False, kind="mergesort").index
    base.loc[order[:rem]] += 1
    return base.astype(int)


def allocate(universe: pd.DataFrame, n: int, by: str) -> pd.Series:
    return largest_remainder(universe.groupby(by).size().astype(float), n)


def draw_stratum(cands: pd.DataFrame, n: int, is_valid: Callable[[str], bool], exclude: set[str]) -> tuple[list, list]:
    """Recorre candidatos en orden aleatorio estable; devuelve (seleccionados, descartados_sin_sinopsis)."""
    chosen, skipped = [], []
    for t in cands.sort_values("_key")["tconst"]:
        if len(chosen) >= n:
            break
        if t in exclude:
            continue
        if is_valid(t):
            chosen.append(t)
        else:
            skipped.append(t)
    return chosen, skipped


def sample_frame(cat: pd.DataFrame, frame: str, n_per_cohort: int, seed: int,
                 is_valid: Callable[[str], bool], exclude: set[str] | None = None,
                 n_tiers: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (muestra, log) para el marco 'popular' o 'amplio'."""
    exclude = set(exclude or ())
    if frame == "popular":
        uni = cat[cat["in_popular_universe"]].copy()
        uni["stratum_pop"] = "top"
    elif frame == "amplio":
        uni = cat.copy()
        uni["stratum_pop"] = "T" + uni["pop_tier"].astype(str)
    else:
        raise ValueError(frame)
    uni["_key"] = uni["tconst"].map(lambda t: stable_key(t, seed, frame))

    rows, log = [], []
    for cohort, cu in uni.groupby("cohort"):
        pops = sorted(cu["stratum_pop"].unique())
        pop_alloc = largest_remainder(pd.Series(1.0, index=pops), n_per_cohort)
        for sp in pops:
            su = cu[cu["stratum_pop"] == sp]
            g_alloc = allocate(su, int(pop_alloc[sp]), "genre_main")
            shortfall = 0
            chosen_all = []
            for g, ng in g_alloc.items():
                cand = su[su["genre_main"] == g]
                chosen, skipped = draw_stratum(cand, int(ng), is_valid, exclude | set(chosen_all))
                chosen_all += chosen
                shortfall += int(ng) - len(chosen)
                log.append({"frame": frame, "cohort": cohort, "stratum_pop": sp, "genre_main": g,
                            "N_universe": len(cand), "n_target": int(ng), "n_drawn": len(chosen),
                            "n_skipped_no_synopsis": len(skipped)})
            if shortfall > 0:  # si un género se agota, se completa con cualquier género del mismo estrato
                chosen, skipped = draw_stratum(su, shortfall, is_valid, exclude | set(chosen_all))
                chosen_all += chosen
                log.append({"frame": frame, "cohort": cohort, "stratum_pop": sp, "genre_main": "_relleno",
                            "N_universe": len(su), "n_target": shortfall, "n_drawn": len(chosen),
                            "n_skipped_no_synopsis": len(skipped)})
            n_sp = len(chosen_all)
            for t in chosen_all:
                rows.append({"tconst": t, "frame": frame, "cohort": cohort, "stratum_pop": sp,
                             "N_stratum": len(su), "n_stratum": n_sp,
                             "design_weight": len(su) / n_sp if n_sp else np.nan})
    return pd.DataFrame(rows), pd.DataFrame(log)
