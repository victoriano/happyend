import math

import pytest

from finales import agreement as ag


def test_cohen_kappa_known_value():
    # Ejemplo clásico: 50 pares, po=0.7, pe=0.5 -> kappa=0.4
    a = ["y"] * 25 + ["n"] * 25
    b = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15
    assert ag.cohen_kappa(a, b) == pytest.approx(0.4)


def test_kappa_perfect_and_nan_handling():
    assert ag.cohen_kappa(["a", "b", "a"], ["a", "b", "a"]) == pytest.approx(1.0)
    assert ag.cohen_kappa(["a", None, "b"], ["a", "b", "b"]) == pytest.approx(1.0)


def test_weighted_kappa_penalises_distance():
    cats = ["F", "A", "M", "T"]
    near = ag.weighted_kappa(["F", "A", "M", "T"] * 5, ["A", "A", "M", "T"] * 5, cats)
    far = ag.weighted_kappa(["F", "A", "M", "T"] * 5, ["T", "A", "M", "T"] * 5, cats)
    assert near > far


def test_krippendorff_alpha_nominal_matches_reference():
    # Datos de Krippendorff (2011), ejemplo con 4 codificadores y faltantes: alfa nominal = 0.743
    d = [[1, 1, None, 1], [2, 2, 3, 2], [3, 3, 3, 3], [3, 3, 3, 3], [2, 2, 2, 2], [1, 2, 3, 4],
         [4, 4, 4, 4], [1, 1, 2, 1], [2, 2, 2, 2], [None, 5, 5, 5], [None, None, 1, 1], [None, None, 3, None]]
    assert ag.krippendorff_alpha(d, "nominal") == pytest.approx(0.743, abs=1e-3)
    assert ag.krippendorff_alpha(d, "interval") == pytest.approx(0.849, abs=1e-3)


def test_percent_agreement():
    assert ag.percent_agreement([1, 2, 3, 4], [1, 2, 0, 0]) == 0.5
