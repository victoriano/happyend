"""Medidas de acuerdo entre anotadores, implementadas sin dependencias externas y probadas en tests/."""
from __future__ import annotations

from collections import Counter
from itertools import product

import numpy as np
import pandas as pd


def cohen_kappa(a, b) -> float:
    """Kappa de Cohen para dos anotadores y categorías nominales. Ignora pares con algún nulo."""
    pairs = [(x, y) for x, y in zip(a, b) if pd.notna(x) and pd.notna(y)]
    if not pairs:
        return float("nan")
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n**2
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def weighted_kappa(a, b, categories: list, weights: str = "quadratic") -> float:
    """Kappa ponderada (lineal o cuadrática) para categorías ordenadas."""
    idx = {c: i for i, c in enumerate(categories)}
    pairs = [(idx[x], idx[y]) for x, y in zip(a, b) if x in idx and y in idx]
    if not pairs:
        return float("nan")
    k = len(categories)
    O = np.zeros((k, k))
    for i, j in pairs:
        O[i, j] += 1
    O /= O.sum()
    E = np.outer(O.sum(1), O.sum(0))
    W = np.array([[abs(i - j) ** (2 if weights == "quadratic" else 1) for j in range(k)] for i in range(k)], float)
    W /= W.max() if W.max() else 1
    den = (W * E).sum()
    return float("nan") if den == 0 else 1 - (W * O).sum() / den


def krippendorff_alpha(data: list[list], level: str = "nominal") -> float:
    """Alfa de Krippendorff. `data` = lista de unidades, cada una con los valores de los anotadores (None = falta).

    level: 'nominal' o 'interval'.
    """
    units = [[v for v in u if v is not None and not (isinstance(v, float) and np.isnan(v))] for u in data]
    units = [u for u in units if len(u) >= 2]
    if not units:
        return float("nan")
    values = sorted({v for u in units for v in u}, key=str)

    def delta(c, k):
        if level == "nominal":
            return 0.0 if c == k else 1.0
        return (float(c) - float(k)) ** 2

    # Matriz de coincidencias
    o = Counter()
    for u in units:
        m = len(u)
        for i, j in product(range(m), range(m)):
            if i != j:
                o[(u[i], u[j])] += 1.0 / (m - 1)
    n_c = Counter()
    for (c, _k), w in o.items():
        n_c[c] += w
    n = sum(n_c.values())
    Do = sum(w * delta(c, k) for (c, k), w in o.items()) / n
    De = sum(n_c[c] * n_c[k] * delta(c, k) for c in values for k in values) / (n * (n - 1))
    return float("nan") if De == 0 else 1 - Do / De


def percent_agreement(a, b) -> float:
    pairs = [(x, y) for x, y in zip(a, b) if pd.notna(x) and pd.notna(y)]
    return float("nan") if not pairs else sum(x == y for x, y in pairs) / len(pairs)


def confusion(a, b, categories: list) -> pd.DataFrame:
    return pd.crosstab(pd.Categorical(a, categories), pd.Categorical(b, categories),
                       rownames=["anotador_A"], colnames=["anotador_B"], dropna=False)
