import pandas as pd

from finales import sampling


def make_cat(n_per=30):
    rows = []
    for cohort, year in [("1990-1999", 1995), ("2010-2019", 2015)]:
        for i in range(n_per):
            rows.append({"tconst": f"tt{year}{i:03d}", "cohort": cohort, "year": year,
                         "genre_main": ["Drama", "Comedia", "Terror"][i % 3],
                         "in_popular_universe": i < 15, "pop_tier": 1 + i % 3})
    return pd.DataFrame(rows)


def test_largest_remainder_sums_exactly():
    s = sampling.largest_remainder(pd.Series({"a": 1.0, "b": 1.0, "c": 1.0}), 10)
    assert s.sum() == 10 and s.max() - s.min() <= 1
    s = sampling.largest_remainder(pd.Series({"a": 5.0, "b": 0.0}), 3)
    assert s["a"] == 3 and s["b"] == 0


def test_stable_key_deterministic_and_seed_dependent():
    assert sampling.stable_key("tt1", 1, "x") == sampling.stable_key("tt1", 1, "x")
    assert sampling.stable_key("tt1", 1, "x") != sampling.stable_key("tt1", 2, "x")


def test_popular_frame_only_from_universe_and_reproducible():
    cat = make_cat()
    s1, _ = sampling.sample_frame(cat, "popular", 6, 42, lambda t: True)
    s2, _ = sampling.sample_frame(cat.sample(frac=1, random_state=1), "popular", 6, 42, lambda t: True)
    assert set(s1["tconst"]) == set(s2["tconst"])          # no depende del orden de filas
    assert s1.groupby("cohort").size().tolist() == [6, 6]
    pop = set(cat.loc[cat["in_popular_universe"], "tconst"])
    assert set(s1["tconst"]) <= pop


def test_invalid_synopsis_replaced_and_logged():
    cat = make_cat()
    bad = set(cat["tconst"][::2])
    s, log = sampling.sample_frame(cat, "popular", 6, 42, lambda t: t not in bad)
    assert not (set(s["tconst"]) & bad)
    assert s.groupby("cohort").size().tolist() == [6, 6]
    assert log["n_skipped_no_synopsis"].sum() > 0


def test_exclusion_of_pilot_and_design_weights():
    cat = make_cat()
    s_p, _ = sampling.sample_frame(cat, "amplio", 6, 42, lambda t: True)
    s_m, _ = sampling.sample_frame(cat, "amplio", 6, 42, lambda t: True, exclude=set(s_p["tconst"]))
    assert not (set(s_p["tconst"]) & set(s_m["tconst"]))
    # amplio: 3 tramos x 2 por tramo por cohorte; peso = N_estrato / n_estrato = 10 / 2
    assert (s_p["design_weight"] == 5.0).all()
