from finales import wikidump as w

WT = """Lead text.
==Plot==
Hero fights.<ref>{{cite web|url=x
Unclosed ref swallows everything in naive parsers.
===Ending===
Hero wins and goes home.
==Cast==
* Actor as Hero
==Reception==
Rotten Tomatoes gives 90%.
"""


def test_plot_section_bounded_even_with_broken_markup():
    h, t = w.plot_from_wikitext(WT)
    assert h == "Plot"
    assert "Hero wins" in t and "Rotten" not in t and "Actor" not in t


def test_no_plot_section():
    assert w.plot_from_wikitext("==Cast==\nx\n") == (None, None)


def test_title_from_url():
    assert w.title_from_url("https://en.wikipedia.org/wiki/Heat_(1995_film)") == "Heat (1995 film)"
    assert w.title_from_url("https://en.wikipedia.org/wiki/Am%C3%A9lie") == "Amélie"


def test_heading_with_trailing_comment():
    wt = "==Plot==<!-- per WP:FILMPLOT --> \nStory here.\n==Cast==\nX\n"
    assert w.plot_from_wikitext(wt) == ("Plot", "Story here.")


def test_level3_not_treated_as_level2():
    wt = "==Plot==\nA.\n===Part two===\nB.\n==Cast==\nX\n"
    h, t = w.plot_from_wikitext(wt)
    assert "A." in t and "B." in t and "X" not in t
