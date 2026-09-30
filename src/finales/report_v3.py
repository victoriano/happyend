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


def _cil(lo, hi, d=1):
    return f"(IC 95 %: {_f(lo, d)} a {_f(hi, d)})"


def _pp(x):
    return _s(x * 100, 0) + " puntos"


DEC = ["ochenta", "noventa", "2000-2009", "2010-2019", "2020-2025"]
COH = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2025"]
PAIS = {"US": "EE. UU.", "ES": "España"}
SUB = {"genre_main": "género", "alcance_A": "alcance", "publico": "público", "tipo_serie": "tipo"}
ALC = {"FINAL": "final", "PARCIAL": "parcial", "EPISODICA": "episódica", "PREMISA": "premisa"}
PUB = {"ADULTO": "adulto", "FAMILIAR": "familiar", "JUVENIL": "juvenil", "INFANTIL": "infantil"}


def series_section() -> tuple[str, str]:
    p = ROOT / "reports" / "tables" / "series"
    if not (p / "historia_series.json").exists():
        return "", ""
    h = json.loads((p / "historia_series.json").read_text(encoding="utf-8"))
    a = json.loads((p / "acuerdo_series.json").read_text(encoding="utf-8"))
    C, P, D, N = h["cohortes"], h["periodos"], h["diff"], h["n"]
    S = {k: {r[0]: r[1:] for r in v} for k, v in h["sens"].items()}
    al, pel, rp = h["alcance"], h["peliculas"], h["reponderado"]
    f = lambda x, d=1: _f(x[0], d) if x[0] is not None else "—"
    pc = lambda x: _p(x[0]) if x[0] is not None else "—"
    dfg = {k: D[k]["feel_good"] for k in ("US", "ES")}

    # películas: media 2010-2025 ponderada por n y diferencia con los noventa
    def pel_rec(k):
        fg = pel[k]["feel_good"]
        return (fg[3][0] * fg[3][3] + fg[4][0] * fg[4][3]) / (fg[3][3] + fg[4][3])
    pel_d = {k: pel_rec(k) - pel[k]["feel_good"][1][0] for k in ("US", "ES")}
    pel_ci = {}
    hw = V2 / "historia_web.json"
    if hw.exists():
        fgw = json.loads(hw.read_text(encoding="utf-8"))["fg"]["diff"]
        pel_ci = {k: fgw[k]["feel_good"] for k in ("US", "ES")}
    pdi = lambda k: (_s(pel_d[k]) + (" " + _ci(*pel_ci[k][1:]) if k in pel_ci else ""))
    zero = lambda k: k in pel_ci and pel_ci[k][1] <= 0 <= pel_ci[k][2]
    nn = lambda x: f"{x:,}".replace(",", ".")

    # composición: parte de la caída debida a la mezcla de géneros
    comp = {}
    for k in ("US", "ES"):
        r = rp[k]
        tot = r["m90"] - r["m_rec"]
        c = r["m_rec_mezcla90"] - r["m_rec"]
        comp[k] = (tot, c, tot - c, c / tot)

    def mix(k, per, n=4):
        m = sorted(h["composicion"][k][per].items(), key=lambda t: -t[1])[:n]
        return ", ".join(f"{g.lower()} {_p(v)}" for g, v in m)

    def tabla(k):
        c = C[k]
        rows = ["| Década de estreno | Series | *Feel good* medio | Con 7 o más | Utopía | Final feliz (clasificables) |",
                "|---|---:|---:|---:|---:|---:|"]
        for i, lab in enumerate(DEC):
            rows.append(f"| {lab} | {c['n'][i]} | {f(c['feel_good'][i])} | {pc(c['y_fg7'][i])} | {f(c['utopia'][i])} | "
                        f"{pc(c['y_feliz'][i])} (n = {c['y_feliz'][i][3]}) |")
        return "\n".join(rows)

    def dline(k):
        d = D[k]
        return (f"Diferencia 2010-2025 frente a los noventa: *feel good* {_s(d['feel_good'][0])} {_ci(*d['feel_good'][1:])}; "
                f"series con 7 o más {_pp(d['y_fg7'][0])} {_ci(d['y_fg7'][1] * 100, d['y_fg7'][2] * 100, 0)}; "
                f"utopía {_s(d['utopia'][0])} {_ci(*d['utopia'][1:])}; "
                f"final feliz entre clasificables {_pp(d['y_feliz'][0])} {_ci(d['y_feliz'][1] * 100, d['y_feliz'][2] * 100, 0)}. "
                f"Solo 2020-2025 frente a los noventa: *feel good* {_s(d['por_cohorte']['2020-2025']['feel_good'][0])} "
                f"{_ci(*d['por_cohorte']['2020-2025']['feel_good'][1:])}.")

    # tabla series frente a películas
    cmp_rows = ["| Década de estreno | Series EE. UU. | Películas EE. UU. | Series España | Películas España |",
                "|---|---:|---:|---:|---:|"]
    for i, lab in enumerate(DEC):
        cmp_rows.append(f"| {lab} | {f(C['US']['feel_good'][i])} | {f(pel['US']['feel_good'][i])} | "
                        f"{f(C['ES']['feel_good'][i])} | {f(pel['ES']['feel_good'][i])} |")
    cmp_tab = "\n".join(cmp_rows)

    # géneros con caída cuyo IC excluye el cero
    def gen_line(k):
        out = []
        for g, n90, nrec, m90, mrec, d, lo, hi in h["genero"][k]:
            mark = "" if (lo <= 0 <= hi) else " \\*"
            out.append(f"{g.lower()} {_f(m90)} → {_f(mrec)} ({_s(d)}{mark}; n = {n90} y {nrec})")
        return "; ".join(out)

    def sub_block(k):
        rows = ["| Subgrupo | n noventa | n 2010-2025 | Noventa | 2010-2025 | Diferencia (IC 95 %) |",
                "|---|---:|---:|---:|---:|---|"]
        excl, star = [], " \\*"
        for var, val, n90, nrec, m90, mrec, d, lo, hi in h["subgrupos"][k]:
            nom = {"alcance_A": ALC, "publico": PUB}.get(var, {}).get(val, val.lower())
            lab = f"{SUB.get(var, var)}: {nom}"
            ex = not (lo <= 0 <= hi)
            if ex:
                excl.append(lab)
            rows.append(f"| {lab} | {n90} | {nrec} | {_f(m90)} | {_f(mrec)} | {_s(d)} ({_s(lo)} a {_s(hi)}){star if ex else ''} |")
        return "\n".join(rows), excl, len(h["subgrupos"][k])

    def sens_line(k):
        return "; ".join(f"{nom[0].lower() + nom[1:]} {_s(v[0])} ({_s(v[1])} a {_s(v[2])}){'' if v[2] < 0 else ' — incluye el cero'}"
                         for nom, v in S[k].items() if nom != "Análisis principal")

    sbU, exU, nU = sub_block("US")
    sbE, exE, nE = sub_block("ES")
    sU, sE = S["US"], S["ES"]
    finU = next(r for r in h["subgrupos"]["US"] if r[0] == "alcance_A" and r[1] == "FINAL")
    adjE = sE["Ajustado por género y popularidad"]
    fam = lambda k, c: h["publico"][k][c].get("INFANTIL", 0) + h["publico"][k][c].get("FAMILIAR", 0)

    inf = f"""
### 9.7 Series de televisión: la caída que no se ve en el cine (D-037)

Esta sección es ahora el resultado principal del estudio. Las películas quedan como contraste.

#### Límites específicos (leer antes que los resultados)

* **Se juzga sobre todo la premisa, no el final.** Wikipedia resume casi siempre de qué va una serie, no cómo termina. En EE. UU., las series con texto que llega al final (`alcance = FINAL`) son el {_p(al['US']['1990-1999']['FINAL'])} en los noventa y el {_p(al['US']['2020-2025']['FINAL'])} en 2020-2025; las de solo premisa pasan del {_p(al['US']['1990-1999']['PREMISA'])} al {_p(al['US']['2020-2025']['PREMISA'])}. En España, solo premisa: {_p(al['ES']['1990-1999']['PREMISA'])} en los noventa y {_p(al['ES']['2020-2025']['PREMISA'])} en 2020-2025. Así que el *feel good* de una serie mide sobre todo la experiencia que promete (personajes, mundo, tono). Y el tipo de texto cambia con el tiempo: las series recientes siguen en emisión o no tienen aún un resumen completo.
* **Supervivencia y votos actuales.** El universo son las series más votadas hoy en IMDb. De los noventa quedan las que se siguen viendo y votando; de 2020-2025, las que están de moda ahora. No es una muestra de lo que se emitía en cada época.
* **Sin validación humana.** Las etiquetas son de dos modelos de lenguaje y un árbitro. Que coincidan mucho no garantiza que acierten: pueden compartir sesgos.
* **Los modelos reconocen las series.** El manual pide juzgar solo el texto, pero en series tan conocidas los modelos pueden usar lo que ya saben de ellas o de su época.

#### Universo y método

Las 30 series de ficción (series y miniseries de IMDb, sin *reality*, concursos, *talk shows*, noticias ni documentales) con más votos por año de estreno, 1980-2025 en el análisis: {nn(N['US']['total'])} estadounidenses y {nn(N['ES']['total'])} españolas. En España no hay 30 por año hasta 2019. Cada serie cuenta una vez, en su año de estreno, y se juzga entera con el manual de series 1.0 (`docs/manual_series.md`). Tienen nota *feel good* {nn(N['US']['con_fg'])} series estadounidenses y {N['ES']['con_fg']} españolas; el final solo es clasificable en {N['US']['clasificables']} y {N['ES']['clasificables']}, respectivamente.

**Acuerdo.** Doble anotación ciega de {nn(a['n'])} series y árbitro en {a['n_adj']} (algún campo adjudicado). *Feel good*: α = {_f(a['alfa_feel_good'], 2)}, con el {_p(a['dentro2_feel_good'], 1)} de pares a 2 puntos o menos. Utopía: α = {_f(a['alfa_utopia'], 2)} ({_p(a['dentro2_utopia'], 1)} a 2 puntos o menos). Tipo de final: κ = {_f(a['kappa_final'], 2)}. Público: κ = {_f(a['kappa_publico'], 2)}.

#### Resultados por década

**EE. UU.**

{tabla('US')}

{dline('US')}

**España**

{tabla('ES')}

{dline('ES')}

El final feliz entre clasificables se apoya en pocas series en las décadas recientes (véase n en la tabla): es el indicador más frágil.

#### Comparación con las películas

Nota *feel good* media por década de estreno, con el mismo método de puntuación:

{cmp_tab}

En EE. UU., las películas pasan de {f(pel['US']['feel_good'][1])} en los noventa a {_f(pel_rec('US'))} en 2010-2025: diferencia {pdi('US')}{', con un intervalo que incluye el cero' if zero('US') else ''}. Las series, de {f(P['US']['feel_good']['1990-1999'])} a {f(P['US']['feel_good']['2010-2025'])} ({_s(dfg['US'][0])}). La caída de las series es unas {_f(dfg['US'][0] / pel_d['US'], 0)} veces la del cine. En España el cine va en sentido contrario: sube de {f(pel['ES']['feel_good'][1])} a {_f(pel_rec('ES'))}: diferencia {pdi('ES')}. Las series españolas, en cambio, bajan {_f(abs(dfg['ES'][0]), 2)} puntos.

#### Composición por géneros y efecto de composición

La mezcla de géneros cambia mucho. EE. UU., noventa: {mix('US', '1990-1999')}. EE. UU., 2010-2025: {mix('US', '2010-2025')}. España, noventa: {mix('ES', '1990-1999')}. España, 2010-2025: {mix('ES', '2010-2025')}. También cae el peso del público infantil y familiar: en EE. UU., del {_p(fam('US', '1990-1999'))} en los noventa al {_p(fam('US', '2020-2025'))} en 2020-2025.

**Reponderación.** Si las series de 2010-2025 tuvieran la mezcla de géneros de los noventa, su media sería {_f(rp['US']['m_rec_mezcla90'])} en EE. UU. (en lugar de {_f(rp['US']['m_rec'])}) y {_f(rp['ES']['m_rec_mezcla90'])} en España (en lugar de {_f(rp['ES']['m_rec'])}). Por tanto:

* **EE. UU.:** de una caída de {_f(comp['US'][0], 2)} puntos, {_f(comp['US'][1], 2)} ({_p(comp['US'][3])}) se deben a la composición y {_f(comp['US'][2], 2)} ({_p(1 - comp['US'][3])}) ocurren dentro de los géneros.
* **España:** de {_f(comp['ES'][0], 2)} puntos, {_f(comp['ES'][1], 2)} ({_p(comp['ES'][3])}) son composición y solo {_f(comp['ES'][2], 2)} ({_p(1 - comp['ES'][3])}) ocurren dentro de los géneros.

Dentro de cada género (noventa → 2010-2025; \\* = IC 95 % que excluye el cero). EE. UU.: {gen_line('US')}. España (solo géneros con suficientes series): {gen_line('ES')}.

#### Subgrupos

Diferencia de *feel good* entre 2010-2025 y los noventa dentro de cada subgrupo con suficientes series (\\* = IC 95 % que excluye el cero).

**EE. UU.**

{sbU}

**España**

{sbE}

En EE. UU., {len(exU)} de {nU} subgrupos excluyen el cero: {', '.join(exU) if exU else 'ninguno'}. En España, {len(exE)} de {nE}: {', '.join(exE) if exE else 'ninguno'}. Son {nU + nE} comparaciones sin corregir por multiplicidad: alguna puede salir por azar, y los subgrupos pequeños tienen intervalos muy anchos. Lo relevante es el patrón: en EE. UU. la nota baja en todos los subgrupos, no solo en las series de solo premisa. En las de final descrito la caída es menor: {_s(finU[6])} {_ci(finU[7], finU[8])}.

#### Sensibilidades (diferencia 2010-2025 frente a los noventa, IC 95 %)

* **EE. UU.** (principal {_s(dfg['US'][0])}): {sens_line('US')}.
* **España** (principal {_s(dfg['ES'][0])}): {sens_line('ES')}.

En EE. UU., todas las sensibilidades mantienen una caída clara, también ajustando por género y popularidad. En España, al ajustar por género y popularidad la diferencia baja a {_s(adjE[0])} y el intervalo incluye el cero: la caída española se explica sobre todo por el cambio de géneros.

#### Lo que sostienen / sugieren / no permiten afirmar

**Sostienen:** entre las series populares de hoy, las estrenadas en los noventa tienen una nota *feel good* mucho más alta que las de 2010-2025, en EE. UU. y en España. La diferencia es grande, se ve con cada anotador y es mucho mayor que en el cine. En EE. UU. resiste a todas las comprobaciones, también al ajuste por género y popularidad.

**Sugieren:** en EE. UU., la mayor parte del cambio ({_p(1 - comp['US'][3])}) no depende de qué géneros se hacen, sino de cómo se cuentan. En España, casi todo ({_p(comp['ES'][3])}) es cambio de mezcla: menos comedia y animación, más *thriller* y drama. La utopía, el optimismo de los personajes y el tono bajan en paralelo.

**No permiten afirmar:** que las series de los noventa terminaran mejor (se juzga sobre todo la premisa y hay pocos finales clasificables); que la caída sea igual en lo que se emitía entonces (solo vemos las series que sobreviven en los votos de hoy); ni por qué ha ocurrido, ni que el público eche de menos esas series.
"""
    rpct = lambda k, c, cat: al[k][c][cat]
    res = f"""
## Resultado principal: las series se han vuelto mucho menos *feel good*

* **Series de EE. UU.:** la nota *feel good* media (0-10) pasa de {f(C['US']['feel_good'][1])} en los noventa a {f(C['US']['feel_good'][4])} en 2020-2025. Diferencia 2010-2025 frente a los noventa: {_s(dfg['US'][0])} {_ci(*dfg['US'][1:])}. Las series con 7 o más bajan del {pc(C['US']['y_fg7'][1])} al {pc(C['US']['y_fg7'][4])}.
* **Series de España:** de {f(C['ES']['feel_good'][1])} a {f(C['ES']['feel_good'][4])}; diferencia {_s(dfg['ES'][0])} {_ci(*dfg['ES'][1:])}.
* **El cine apenas cambia:** las películas estadounidenses pasan de {f(pel['US']['feel_good'][1])} a {_f(pel_rec('US'))} en 2010-2025: diferencia {pdi('US')}{', con un intervalo que incluye el cero' if zero('US') else ''}. En España el cine sube.
* **Robustez:** en EE. UU. la caída se mantiene con cada anotador (A {_s(sU['Solo el anotador A'][0])}, B {_s(sU['Solo el anotador B'][0])}), sin las series de solo premisa ({_s(sU['Sin las que solo tienen premisa'][0])}) y ajustando por género y popularidad ({_s(sU['Ajustado por género y popularidad'][0])}).
* **Géneros:** con la mezcla de géneros de los noventa, la media reciente de EE. UU. sería {_f(rp['US']['m_rec_mezcla90'])}: la composición explica el {_p(comp['US'][3])} de la caída y el resto ocurre dentro de los géneros. En España la composición explica el {_p(comp['ES'][3])} y, ajustando por género, el intervalo incluye el cero.
* **Cautelas:** se juzga sobre todo la premisa (las series de solo premisa pasan del {_p(rpct('US', '1990-1999', 'PREMISA'))} al {_p(rpct('US', '2020-2025', 'PREMISA'))} en EE. UU.); solo vemos las series que siguen votándose hoy; no hay validación humana y los modelos reconocen las series. Los datos no dicen por qué ha ocurrido.
"""
    return inf, res
