import numpy as np
import pytest

from finales import stats


def test_wilson_reference_values():
    p, lo, hi = stats.wilson(10, 20)
    assert p == 0.5 and lo == pytest.approx(0.2993, abs=1e-4) and hi == pytest.approx(0.7007, abs=1e-4)
    p, lo, hi = stats.wilson(0, 10)
    assert lo == 0 and hi == pytest.approx(0.2775, abs=1e-4)


def test_weighted_prop_equal_weights_equals_wilson():
    y = np.array([1] * 7 + [0] * 13)
    p, lo, hi, n_eff = stats.weighted_prop_ci(y, None)
    assert n_eff == pytest.approx(20)
    assert (p, lo, hi) == pytest.approx(stats.wilson(7, 20))


def test_kish_effective_n_shrinks_with_unequal_weights():
    y = np.array([1, 0, 1, 0])
    *_, n_eff = stats.weighted_prop_ci(y, np.array([1, 1, 1, 10]))
    assert n_eff < 4


def test_bootstrap_diff_covers_truth():
    rng = np.random.default_rng(1)
    y = np.r_[rng.binomial(1, 0.7, 400), rng.binomial(1, 0.5, 400)]
    g = np.r_[["a"] * 400, ["b"] * 400]
    r = stats.bootstrap_diff(y, g, "a", "b", n_boot=1000, seed=2)
    assert r["diff_lo"] < 0.2 < r["diff_hi"]
    assert r["ratio"] == pytest.approx(y[:400].mean() / y[400:].mean())


def test_sample_size_formulas():
    n1, n2 = stats.n_two_proportions(0.6, 0.5)
    assert 380 <= n1 <= 395 and n1 == n2          # valor de referencia ≈ 385-388
    assert stats.mde_two_proportions(0.5, 385, 385) == pytest.approx(0.101, abs=0.003)
    assert stats.n_two_means(1.0, 0.5) == 63


def test_mean_ci_simple():
    m, lo, hi = stats.mean_ci(np.array([1.0, 2.0, 3.0, np.nan]))
    assert m == 2.0 and lo < 2 < hi
