import pandas as pd
import pytest

from finales import clean
from finales.config import cohort_of, load

CFG = load()


def _imdb(rows):
    cols = ["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult", "startYear",
            "endYear", "runtimeMinutes", "genres", "averageRating", "numVotes"]
    return pd.DataFrame(rows, columns=cols)


def _wd(rows):
    return pd.DataFrame(rows, columns=["wikidata_id", "tconst", "enwiki_url", "country_qid", "pub_date", "query_year"])


def base_row(tconst, **kw):
    r = dict(tconst=tconst, titleType="movie", primaryTitle="X", originalTitle="X", isAdult="0",
             startYear="1995", endYear=None, runtimeMinutes="100", genres="Drama", averageRating=7.0,
             numVotes=5000)
    r.update(kw)
    return [r[c] for c in ["tconst", "titleType", "primaryTitle", "originalTitle", "isAdult", "startYear",
                           "endYear", "runtimeMinutes", "genres", "averageRating", "numVotes"]]


def wd_row(tconst, url="https://en.wikipedia.org/wiki/X", country="Q30", date="1995-05-01", qid=None):
    return [qid or "Q" + tconst[2:], tconst, url, country, date, 1995]


def test_cohort_of():
    assert cohort_of(1990) == "1990-1999"
    assert cohort_of(1999) == "1990-1999"
    assert cohort_of(2024) == "2020-2024"
    assert cohort_of(1979) is None
    assert cohort_of(2025) is None


def test_primary_genre_priority():
    pr = CFG["genero_principal_prioridad"]
    assert clean.primary_genre("Comedy,Drama,Romance", pr, "Otros") == "Comedia"
    assert clean.primary_genre("Animation,Comedy", pr, "Otros") == "Animación"
    assert clean.primary_genre("Drama,Horror", pr, "Otros") == "Terror"
    assert clean.primary_genre("Western", pr, "Otros") == "Otros"
    assert clean.primary_genre(float("nan"), pr, "Otros") == "Otros"


def test_filters_assign_single_reason_each():
    imdb = _imdb([
        base_row("tt0000001"),                                      # válida
        base_row("tt0000002", runtimeMinutes="45"),                 # corta
        base_row("tt0000003", genres="Documentary"),                # no ficción
        base_row("tt0000004", numVotes=10),                         # pocos votos
        base_row("tt0000005"),                                      # no está en Wikidata EE. UU.
        base_row("tt0000006", startYear="1975"),                    # fuera de periodo: ni se considera
        base_row("tt0000007", runtimeMinutes=None),                 # sin duración
        base_row("tt0000008"),                                      # año inconsistente
        base_row("tt0000009"),                                      # sin artículo
        base_row("tt0000010", isAdult="1"),
        base_row("tt0000011", titleType="tvMovie"),                 # no es 'movie'
    ])
    wd = _wd([wd_row("tt0000001", url="https://en.wikipedia.org/wiki/A"),
              wd_row("tt0000002"), wd_row("tt0000003"), wd_row("tt0000004"),
              wd_row("tt0000007"),
              wd_row("tt0000008", url="https://en.wikipedia.org/wiki/B", date="1990-01-01"),
              wd_row("tt0000009", url=None)])
    cat, excl = clean.apply_filters(imdb, clean.summarise_wikidata(wd), CFG)
    assert list(cat["tconst"]) == ["tt0000001"]
    reasons = dict(zip(excl["tconst"], excl["reason"]))
    assert reasons == {
        "tt0000002": "duracion_menor_umbral",
        "tt0000003": "genero_no_ficcion",
        "tt0000004": "votos_bajo_umbral",
        "tt0000005": "nacionalidad_no_establecida_o_no_eeuu",
        "tt0000007": "sin_duracion",
        "tt0000008": "anio_inconsistente_imdb_wikidata",
        "tt0000009": "sin_articulo_wikipedia",
        "tt0000010": "adulto",
    }
    assert "tt0000006" not in reasons and "tt0000011" not in reasons


def test_duplicate_article_keeps_most_voted():
    imdb = _imdb([base_row("tt0000001", numVotes=2000), base_row("tt0000002", numVotes=9000)])
    wd = _wd([wd_row("tt0000001", url="https://en.wikipedia.org/wiki/Same"),
              wd_row("tt0000002", url="https://en.wikipedia.org/wiki/Same")])
    cat, excl = clean.apply_filters(imdb, clean.summarise_wikidata(wd), CFG)
    assert list(cat["tconst"]) == ["tt0000002"]
    assert excl.set_index("tconst").loc["tt0000001", "reason"] == "duplicado_articulo_wikipedia"


def test_coproduction_flags():
    wd = _wd([wd_row("tt0000001", country="Q30"), wd_row("tt0000001", country="Q145"),
              wd_row("tt0000002", country="Q30")])
    s = clean.summarise_wikidata(wd).set_index("tconst")
    assert not s.loc["tt0000001", "us_only"] and s.loc["tt0000001", "n_countries"] == 2
    assert s.loc["tt0000002", "us_only"]


def test_popularity_rank_and_tiers():
    cat = pd.DataFrame({"tconst": [f"tt{i:07d}" for i in range(9)], "year": [1995] * 9,
                        "numVotes": [100, 900, 800, 700, 600, 500, 400, 300, 200]})
    out = clean.add_popularity(cat, CFG).set_index("tconst")
    assert out.loc["tt0000001", "votes_rank_in_year"] == 1
    assert out.loc["tt0000000", "votes_rank_in_year"] == 9
    assert sorted(out["pop_tier"].value_counts().tolist()) == [3, 3, 3]
    assert out.loc["tt0000001", "pop_tier"] == 3 and out.loc["tt0000000", "pop_tier"] == 1
