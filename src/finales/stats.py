"""Estimación con incertidumbre: intervalos de Wilson, bootstrap y modelos de regresión."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def wilson(k: int, n: int, level: float = 0.95) -> tuple[float, float, float]:
    """Proporción y su intervalo de Wilson."""
    if n == 0:
        return (np.nan, np.nan, np.nan)
    z = stats.norm.ppf(1 - (1 - level) / 2)
    p = k / n
    den = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def weighted_prop_ci(y: np.ndarray, w: np.ndarray | None, level: float = 0.95) -> tuple[float, float, float, float]:
    """Proporción ponderada con IC de Wilson usando el tamaño efectivo de Kish. Devuelve (p, lo, hi, n_ef)."""
    y = np.asarray(y, float)
    w = np.ones_like(y) if w is None else np.asarray(w, float)
    if len(y) == 0 or w.sum() == 0:
        return (np.nan, np.nan, np.nan, 0.0)
    p = float((w * y).sum() / w.sum())
    n_eff = float(w.sum() ** 2 / (w**2).sum())
    _, lo, hi = wilson(p * n_eff, n_eff, level)
    return (p, lo, hi, n_eff)


def mean_ci(x: np.ndarray, w: np.ndarray | None = None, level: float = 0.95) -> tuple[float, float, float]:
    """Media (ponderada) con IC t basado en el tamaño efectivo."""
    x = np.asarray(x, float)
    m = ~np.isnan(x)
    x = x[m]
    w = np.ones_like(x) if w is None else np.asarray(w, float)[m]
    if len(x) < 2:
        return (float(np.mean(x)) if len(x) else np.nan, np.nan, np.nan)
    mu = float((w * x).sum() / w.sum())
    n_eff = w.sum() ** 2 / (w**2).sum()
    var = float((w * (x - mu) ** 2).sum() / w.sum()) * n_eff / (n_eff - 1)
    se = np.sqrt(var / n_eff)
    t = stats.t.ppf(1 - (1 - level) / 2, df=max(n_eff - 1, 1))
    return (mu, mu - t * se, mu + t * se)


def bootstrap_diff(y: np.ndarray, group: np.ndarray, g1, g0, w: np.ndarray | None = None,
                   n_boot: int = 4000, seed: int = 0, level: float = 0.95,
                   strata: np.ndarray | None = None) -> dict:
    """Diferencia de medias (o proporciones) ponderadas g1 − g0 con bootstrap estratificado.

    El remuestreo se hace dentro de cada grupo y, si se da `strata`, dentro de cada estrato de diseño
    (p. ej., cohorte × tramo de popularidad), respetando así el diseño muestral.
    Devuelve diferencia absoluta, razón g1/g0, sus IC percentiles y el tamaño efectivo de Kish por grupo.
    """
    rng = np.random.default_rng(seed)
    y = np.asarray(y, float)
    group = np.asarray(group)
    w = np.ones_like(y) if w is None else np.asarray(w, float)
    strata = np.zeros(len(y), dtype=int) if strata is None else np.asarray(strata)
    i1, i0 = np.where(group == g1)[0], np.where(group == g0)[0]
    i1 = i1[~np.isnan(y[i1])]
    i0 = i0[~np.isnan(y[i0])]
    if len(i1) == 0 or len(i0) == 0:
        return {"diff": np.nan, "diff_lo": np.nan, "diff_hi": np.nan, "ratio": np.nan,
                "ratio_lo": np.nan, "ratio_hi": np.nan, "n1": len(i1), "n0": len(i0), "n_ef1": np.nan, "n_ef0": np.nan}

    def wm(idx):
        return (w[idx] * y[idx]).sum() / w[idx].sum()

    d0, r0 = wm(i1) - wm(i0), (wm(i1) / wm(i0) if wm(i0) else np.nan)
    cells1 = [i1[strata[i1] == s] for s in np.unique(strata[i1])]
    cells0 = [i0[strata[i0] == s] for s in np.unique(strata[i0])]

    def resample(cells):
        return np.concatenate([rng.choice(c, len(c), replace=True) for c in cells])

    diffs, ratios = np.empty(n_boot), np.empty(n_boot)
    for b in range(n_boot):
        s1, s0 = resample(cells1), resample(cells0)
        m1, m0 = wm(s1), wm(s0)
        diffs[b] = m1 - m0
        ratios[b] = m1 / m0 if m0 else np.nan
    a = (1 - level) / 2
    return {"diff": d0, "diff_lo": np.nanquantile(diffs, a), "diff_hi": np.nanquantile(diffs, 1 - a),
            "ratio": r0, "ratio_lo": np.nanquantile(ratios, a), "ratio_hi": np.nanquantile(ratios, 1 - a),
            "n1": len(i1), "n0": len(i0),
            "n_ef1": float(w[i1].sum() ** 2 / (w[i1] ** 2).sum()), "n_ef0": float(w[i0].sum() ** 2 / (w[i0] ** 2).sum())}


def n_two_proportions(p1: float, p2: float, alpha: float = 0.05, power: float = 0.8, ratio: float = 1.0) -> tuple[int, int]:
    """Tamaño por grupo para detectar p1 vs p2 (bilateral), con n2 = ratio · n1. Aproximación normal."""
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    pbar = (p1 + ratio * p2) / (1 + ratio)
    num = (za * np.sqrt(pbar * (1 - pbar) * (1 + 1 / ratio))
           + zb * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / ratio)) ** 2
    n1 = num / (p1 - p2) ** 2
    return int(np.ceil(n1)), int(np.ceil(n1 * ratio))


def mde_two_proportions(p: float, n1: int, n2: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Diferencia mínima detectable (aprox.) alrededor de una proporción base p."""
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return float((za + zb) * np.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)))


def n_two_means(sd: float, delta: float, alpha: float = 0.05, power: float = 0.8) -> int:
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return int(np.ceil(2 * ((za + zb) * sd / delta) ** 2))
