from finales import blinding


def test_mask_removes_years_and_title():
    titles = blinding.title_variants("Heat", None, "Heat_(1995_film)")
    out = blinding.mask("In 1995, the Heat crew robs a bank. In the 1980s they met. HEAT ends.", titles)
    assert "1995" not in out and "1980" not in out and "Heat" not in out and "HEAT" not in out
    assert out.count("[TÍTULO]") == 2 and "[AÑO]" in out
    assert blinding.mask("In 2047 and the '80s", []) == "In [AÑO] and the [AÑO]"


def test_short_titles_not_masked():
    assert blinding.title_variants("Up") == []


def test_truncate_keeps_head_and_tail():
    text = " ".join(f"w{i}" for i in range(100))
    out, trunc = blinding.truncate_words(text, 20)
    assert trunc and out.startswith("w0 ") and out.endswith("w99") and "[…]" in out
    same, t2 = blinding.truncate_words("a b c", 20)
    assert same == "a b c" and not t2


def test_blind_id_stable():
    assert blinding.blind_id("tt1", 1) == blinding.blind_id("tt1", 1)
    assert blinding.blind_id("tt1", 1) != blinding.blind_id("tt2", 1)
