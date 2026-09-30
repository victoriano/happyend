"""Valores de la tercera parte del informe (D-035, D-036): feel good, utopía y público."""
from __future__ import annotations

import json

from .config import ROOT

TEMPLATES = ROOT / "docs" / "plantillas"
V2 = ROOT / "reports" / "tables" / "v2"


def _p(x, d=0):
    return f"{x * 100:.{d}f} %".replace(".", ",")


def _f(x, d=1):
    return f"{x:.{d}f}".replace(".", ",").replace("-", "−")


def _s(x, d=2):
    return ("+" if x >= 0 else "−") + f"{abs(x):.{d}f}".replace(".", ",")


def _ci(lo, hi, d=2):
    return f"(IC 95 %: {_s(lo, d)} a {_s(hi, d)})"


def values_v3() -> dict:
    fg = json.loads((V2 / "historia_web.json").read_text(encoding="utf-8"))["fg"]
    web = json.loads((ROOT / "web" / "data.json").read_text(encoding="utf-8"))["v2"]
    a = web["acuerdo_censo"]
    U, E = fg["cohortes"]["US"], fg["cohortes"]["ES"]
    dU, dE = fg["diff"]["US"], fg["diff"]["ES"]
    sU = {r[0]: r[1:] for r in fg["sens"]["US"]}
    sE = {r[0]: r[1:] for r in fg["sens"]["ES"]}
    pub = fg["publico"]["US"]
    fam = lambda c: pub["por_cohorte"][c].get("INFANTIL", 0) + pub["por_cohorte"][c].get("FAMILIAR", 0)
    pf = pub["fg"]
    fgfam = (pf["INFANTIL"][0] * pf["INFANTIL"][3] + pf["FAMILIAR"][0] * pf["FAMILIAR"][3]) / (pf["INFANTIL"][3] + pf["FAMILIAR"][3])
    pfin = fg["por_final"]
    tot = lambda f: (pfin["US"][f][1] * pfin["US"][f][0] + pfin["ES"][f][1] * pfin["ES"][f][0]) / (pfin["US"][f][0] + pfin["ES"][f][0])
    im = fg["imdb"]["US"]["averageRating~feel_good"]
    wm = lambda k, cf: sum(x[0] * x[3] for x in fg["cohortes"][cf][k] if x[0] is not None) / sum(x[3] for x in fg["cohortes"][cf][k] if x[0] is not None)
    V = {
        "v3_es_sin_fg": _p(web["sin_fg"]["ES"]), "v3_n_cde": f"{a['n_cde']:,}".replace(",", "."),
        "v3_a_fg": _f(a["alfa_feel_good"], 2), "v3_d2_fg": _p(a["dentro2_feel_good"]), "v3_a_ut": _f(a["alfa_utopia"], 2),
        "v3_k_pub": _f(a["kappa_publico"], 2), "v3_adj_fg": a["n_adj_feel_good"], "v3_adj_ut": a["n_adj_utopia"],
        **{f"v3_us_{k}": _f(U["feel_good"][i][0]) for i, k in enumerate(["80", "90", "00", "10", "20"])},
        "v3_us_d": _s(dU["feel_good"][0]), "v3_us_d_ci": _ci(*dU["feel_good"][1:]),
        "v3_us_d20": _s(dU["por_cohorte"]["2020-2025"]["feel_good"][0]),
        "v3_us_d20_ci": _ci(*dU["por_cohorte"]["2020-2025"]["feel_good"][1:]),
        "v3_us_fg7_90": _p(U["y_fg7"][1][0]), "v3_us_fg7_20": _p(U["y_fg7"][4][0]),
        "v3_us_adj": _s(sU["Ajustado por género y popularidad"][0]), "v3_us_adj_ci": _ci(*sU["Ajustado por género y popularidad"][1:]),
        "v3_us_nofam": _s(sU["Sin películas infantiles y familiares"][0]),
        "v3_us_nofam_ci": _ci(*sU["Sin películas infantiles y familiares"][1:]),
        "v3_us_w": _s(sU["Pesando más las más votadas"][0]), "v3_us_w_ci": _ci(*sU["Pesando más las más votadas"][1:]),
        "v3_us_A": _s(sU["Solo el anotador A"][0]), "v3_us_B": _s(sU["Solo el anotador B"][0]),
        "v3_corr": _f(fg["cruce"]["US"]["corr"], 2), "v3_fg_feliz": _f(tot("FELIZ")), "v3_fg_tragico": _f(tot("TRAGICO")),
        "v3_us_ut": _f(wm("utopia", "US")), "v3_us_ut_d20": _s(dU["por_cohorte"]["2020-2025"]["utopia"][0]),
        "v3_us_ut_d20_ci": _ci(*dU["por_cohorte"]["2020-2025"]["utopia"][1:]),
        "v3_es_ut_90": _f(fg["periodos"]["ES"]["utopia"]["1990-1999"][0]), "v3_es_ut_rec": _f(fg["periodos"]["ES"]["utopia"]["2010-2025"][0]),
        "v3_fg_fam": _f(fgfam), "v3_fg_adulto": _f(pf["ADULTO"][0]), "v3_fam_90": _p(fam("1990-1999")), "v3_fam_20": _p(fam("2020-2025")),
        "v3_es_90": _f(fg["periodos"]["ES"]["feel_good"]["1990-1999"][0]), "v3_es_rec": _f(fg["periodos"]["ES"]["feel_good"]["2010-2025"][0]),
        "v3_es_d": _s(dE["feel_good"][0]), "v3_es_d_ci": _ci(*dE["feel_good"][1:]),
        "v3_es_wiki": _s(sE["Solo sinopsis de Wikipedia"][0]), "v3_es_wiki_ci": _ci(*sE["Solo sinopsis de Wikipedia"][1:]),
        "v3_imdb_fg": _s(im[0], 3), "v3_imdb_fg_ci": _ci(im[1], im[2], 3),
        "v3_es_m": _f(wm("feel_good", "ES")), "v3_us_m": _f(wm("feel_good", "US")),
    }
    return V


def main():
    V = values_v3()
    return ((TEMPLATES / "informe_v3.md").read_text(encoding="utf-8").format_map(V),
            (TEMPLATES / "resumen_v3.md").read_text(encoding="utf-8").format_map(V), V)


def series_section() -> tuple[str, str]:
    p = ROOT / "reports" / "tables" / "series"
    if not (p / "historia_series.json").exists():
        return "", ""
    h = json.loads((p / "historia_series.json").read_text(encoding="utf-8"))
    a = json.loads((p / "acuerdo_series.json").read_text(encoding="utf-8"))
    U, E = h["cohortes"]["US"], h["cohortes"]["ES"]
    sU = {r[0]: r[1:] for r in h["sens"]["US"]}
    dU, dE = h["diff"]["US"]["feel_good"], h["diff"]["ES"]["feel_good"]
    f = lambda x: _f(x[0]) if x[0] is not None else "—"
    inf = f"""
### 9.7 Series de televisión (D-037)

**Universo.** Las 30 series de ficción con más votos en IMDb por año de estreno (1980-2025 en el análisis): {h['n']['US']['total']} estadounidenses y {h['n']['ES']['total']} españolas (menos de 30 por año en España hasta 2019). Se juzga la serie entera con el manual de series 1.0; doble anotación ciega de {a['n']} series y árbitro ({a['n_adj']} series con algún campo adjudicado). Acuerdo: *feel good* α = {_f(a['alfa_feel_good'], 2)}; utopía α = {_f(a['alfa_utopia'], 2)}; final κ = {_f(a['kappa_final'], 2)}; público κ = {_f(a['kappa_publico'], 2)}.

**Límite principal.** Wikipedia describe sobre todo la premisa de las series, no su final: el *feel good* de una serie mide la experiencia que promete (personajes, mundo, tono) más que su desenlace. Solo una minoría de textos llega al final de la serie.

**Resultados.** Nota *feel good* media de las series estadounidenses por década de estreno: {', '.join(f(x) for x in U['feel_good'])} (ochenta a 2020-2025). Diferencia 2010-2025 frente a los noventa: {_s(dU[0])} {_ci(dU[1], dU[2])}. Series con 7 o más: del {_p(U['y_fg7'][1][0])} en los noventa al {_p(U['y_fg7'][4][0])} en 2020-2025. La caída se mantiene con un solo anotador (A {_s(sU['Solo el anotador A'][0])}, B {_s(sU['Solo el anotador B'][0])}), sin las series de solo premisa ({_s(sU['Sin las que solo tienen premisa'][0])}), sin series infantiles y familiares ({_s(sU['Sin series infantiles y familiares'][0])}) y ajustando por género y popularidad ({_s(sU['Ajustado por género y popularidad'][0])}). La nota de utopía baja de {f(U['utopia'][1])} a {f(U['utopia'][4])}. Series españolas: {', '.join(f(x) for x in E['feel_good'])}; diferencia {_s(dE[0])} {_ci(dE[1], dE[2])}.

**Lectura.** A diferencia del cine, donde el cambio es pequeño y reciente, las series populares sí se han vuelto mucho menos *feel good* desde los noventa. Parte puede deberse a qué series se recuerdan y se votan hoy (supervivencia de las comedias de los noventa frente al auge del drama de prestigio) y a que el juicio se hace sobre premisas.
"""
    res = f"""
## Series: la caída sí es grande

Las series estadounidenses más votadas pasan de un *feel good* medio de {f(U['feel_good'][1])} (noventa) a {f(U['feel_good'][4])} (2020-2025), una diferencia 2010-2025 de {_s(dU[0])} puntos {_ci(dU[1], dU[2])}, robusta a todas las comprobaciones. Las españolas siguen la misma tendencia. Cautela: se juzga sobre todo la premisa de cada serie, no su final.
"""
    return inf, res
