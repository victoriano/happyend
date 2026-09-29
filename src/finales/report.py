"""Genera el informe y el resumen ejecutivo rellenando plantillas con cifras leídas de reports/tables/.

Ninguna cifra del informe se escribe a mano: cada marcador {clave} procede de values(), que lee las tablas
generadas por analysis.py, power.py y pipeline.py. Así cada número es trazable a su tabla de origen.
"""
from __future__ import annotations

import json

import pandas as pd

from .config import ROOT, TABLES

TEMPLATES = ROOT / "docs" / "plantillas"
COH = {"1980-1989": "80", "1990-1999": "90", "2000-2009": "00", "2010-2019": "10", "2020-2024": "20"}


def pct(x: float, d: int = 1) -> str:
    return "n/d" if pd.isna(x) else f"{x * 100:.{d}f}".replace(".", ",") + " %"


def pp(x: float, d: int = 1) -> str:
    if pd.isna(x):
        return "n/d"
    s = f"{abs(x) * 100:.{d}f}".replace(".", ",")
    return ("−" if x < 0 else "+") + s + " pp"


def num(x: float, d: int = 2, signed: bool = False) -> str:
    if pd.isna(x):
        return "n/d"
    s = f"{abs(x):.{d}f}".replace(".", ",")
    if signed:
        return ("−" if x < 0 else "+") + s
    return ("−" if x < 0 else "") + s


def ci_pp(lo: float, hi: float) -> str:
    return f"[{pp(lo)}; {pp(hi)}]"


def ci_pct(lo: float, hi: float) -> str:
    return f"[{pct(lo)}; {pct(hi)}]"


def values() -> dict:
    V: dict[str, str] = {}
    t = lambda name: pd.read_csv(TABLES / name)

    cat = t("catalogo_por_cohorte.csv").set_index("cohort")["catalogo_elegible"]
    V["cat_total"] = f"{int(cat.sum()):,}".replace(",", ".")
    for c, k in COH.items():
        V[f"cat_{k}"] = f"{int(cat[c]):,}".replace(",", ".")
    ex = t("exclusiones_resumen.csv").set_index("reason")["total"]
    for r in ex.index:
        V[f"excl_{r}"] = f"{int(ex[r]):,}".replace(",", ".")
    cov = t("cobertura_cmu.csv").set_index("cohort")
    for c, k in COH.items():
        V[f"cmu_{k}"] = pct(cov.loc[c, "cobertura_cmu"], 0)
        V[f"cmu_pop_{k}"] = pct(cov.loc[c, "cobertura_cmu_popular"], 0)

    ms = pd.read_csv(ROOT / "data" / "derived" / "muestra_principal.csv")
    V["n_filas_muestra"] = str(len(ms))
    V["n_peliculas"] = str(ms["tconst"].nunique())
    V["n_solapadas"] = str(len(ms) - ms["tconst"].nunique())
    lg = t("muestreo_log_principal.csv")
    V["n_sustituidas"] = str(int(lg["n_skipped_no_synopsis"].sum()))
    V["n_sust_amplio"] = str(int(lg.loc[lg.frame == "amplio", "n_skipped_no_synopsis"].sum()))
    V["n_sust_popular"] = str(int(lg.loc[lg.frame == "popular", "n_skipped_no_synopsis"].sum()))
    V["palabras_mediana"] = str(int(ms.drop_duplicates("tconst")["synopsis_words"].median()))

    # Piloto y potencia
    ap = t("acuerdo_piloto.csv").set_index("variable")
    V["pil_k_final"] = num(ap.loc["final", "kappa_cohen"])
    V["pil_k_tono"] = num(ap.loc["tono_cierre", "kappa_cohen"])
    par = t("parametros_piloto.csv").set_index("Unnamed: 0")["valor"]
    V["pil_p_feliz"] = pct(par["p_feliz_piloto"], 0)
    V["pil_sd_vision"] = num(par["sd_vision_piloto"])
    pw = t("potencia_piloto.csv")
    V["n_10pp"] = str(int(pw.iloc[0]["n_por_cohorte_necesario"]))
    V["n_15pp"] = str(int(pw.iloc[1]["n_por_cohorte_necesario"]))
    V["mde_pop"] = pw.iloc[6]["diferencia_minima"].replace(".", ",")
    V["mde_pop_coh"] = pw.iloc[7]["diferencia_minima"].replace(".", ",")
    V["mde_amp"] = pw.iloc[8]["diferencia_minima"].replace(".", ",")

    # Acuerdo principal
    a = t("acuerdo_principal.csv").set_index("variable")
    V["k_final"] = num(a.loc["final", "kappa_cohen"])
    V["pa_final"] = pct(a.loc["final", "acuerdo_pct"], 0)
    V["wk_final"] = num(a.loc["final (ordinal 4 cat., kappa cuadrática)", "kappa_cohen"])
    V["k_feliz"] = num(a.loc["final feliz (sí/no)", "kappa_cohen"])
    V["k_tono"] = num(a.loc["tono_cierre", "kappa_cohen"])
    V["k_obj"] = num(a.loc["objetivo", "kappa_cohen"])
    V["k_just"] = num(a.loc["justicia_narrativa", "kappa_cohen"])
    V["k_rel"] = num(a.loc["relaciones", "kappa_cohen"])
    V["k_surv"] = num(a.loc["supervivencia", "kappa_cohen"])
    V["alfa_vision"] = num(a.loc["vision_vida (media ítems)", "alfa_krippendorff"])
    items = a.loc[["agencia", "cambio", "vinculos", "futuro"], "alfa_krippendorff"]
    V["alfa_items_min"], V["alfa_items_max"] = num(items.min()), num(items.max())
    info = json.loads((TABLES / "acuerdo_principal_info.json").read_text())
    V["rec_A"] = pct(info["reconocidas_A"] / info["n_pares"], 0)
    V["rec_B"] = pct(info["reconocidas_B"] / info["n_pares"], 0)
    rc = t("reconocimiento_por_cohorte.csv").set_index("cohort")
    V["rec_any_min"], V["rec_any_max"] = pct(rc["reconocida_alguno"].min(), 0), pct(rc["reconocida_alguno"].max(), 0)
    dg = t("desacuerdo_por_grupo_principal.csv")
    dc = dg[dg.dimension == "cohort"].set_index("grupo")["desacuerdo_feliz"]
    V["dis_feliz_min"], V["dis_feliz_max"] = pct(dc.min()), pct(dc.max())
    adj = t("adjudicacion_resumen.csv").set_index("campo")
    V["adj_n_final"] = str(int(adj.loc["final", "n_adjudicados"]))
    V["adj_A_final"] = pct(adj.loc["final", "elige_A"], 0)
    V["adj_A_tono"] = pct(adj.loc["tono_cierre", "elige_A"], 0)
    V["n_adjudicadas"] = str(sum(1 for f in (ROOT / "annotation" / "labels" / "principal" / "adjudicacion").glob("*.jsonl")
                                 for line in f.read_text().splitlines() if line.strip()))
    nc = t("no_clasificables_por_cohorte.csv")
    V["nc_popular"] = str(int(nc.loc[nc.frame == "popular", "no_clasificables"].sum()))
    V["nc_amplio"] = str(int(nc.loc[nc.frame == "amplio", "no_clasificables"].sum()))
    ncd = nc.set_index(["frame", "cohort"])["no_clasificables"]
    V["nc_amp_90"], V["nc_amp_10"] = str(int(ncd[("amplio", "1990-1999")])), str(int(ncd[("amplio", "2010-2019")]))

    # Descriptivos
    d = t("descriptivos_marco_cohorte.csv")
    fr = {"popular": "pop", "amplio": "amp"}
    for f, fk in fr.items():
        for c, k in COH.items():
            for var, vk in [("y_feliz", "feliz"), ("y_agridulce", "agri"), ("y_ambiguo", "amb"), ("y_tragico", "trag"),
                            ("y_tono_positivo", "tono"), ("y_sobrevive", "surv"), ("y_objetivo", "obj"),
                            ("y_justicia", "just"), ("vision_vida", "vision")]:
                r = d[(d.frame == f) & (d.cohort == c) & (d.variable == var)].iloc[0]
                if var == "vision_vida":
                    V[f"{fk}_{vk}_{k}"] = num(r.estimacion)
                    V[f"{fk}_{vk}_{k}_ci"] = f"[{num(r.ic95_inf)}; {num(r.ic95_sup)}]"
                else:
                    V[f"{fk}_{vk}_{k}"] = pct(r.estimacion)
                    V[f"{fk}_{vk}_{k}_ci"] = ci_pct(r.ic95_inf, r.ic95_sup)
    dp = t("descriptivos_marco_periodo.csv")
    for f, fk in fr.items():
        r = dp[(dp.frame == f) & (dp.periodo == "2010-2024") & (dp.variable == "y_feliz")].iloc[0]
        V[f"{fk}_feliz_rec"] = pct(r.estimacion)
        V[f"{fk}_feliz_rec_ci"] = ci_pct(r.ic95_inf, r.ic95_sup)
    dv = t("descriptivos_marco_cohorte_pond_votos.csv")
    for c, k in COH.items():
        r = dv[(dv.frame == "popular") & (dv.cohort == c) & (dv.variable == "y_feliz")].iloc[0]
        V[f"popv_feliz_{k}"] = pct(r.estimacion)

    # Contrastes
    cs = t("contrastes_vs_1990s.csv")
    for f, fk in fr.items():
        for var, vk in [("y_feliz", "feliz"), ("y_agridulce", "agri"), ("y_ambiguo", "amb"), ("y_tragico", "trag"),
                        ("y_tono_positivo", "tono"), ("vision_vida", "vision")]:
            for comp, ck in [("2010-2024 − 1990-1999", "rec"), ("2010-2019 − 1990-1999", "10"),
                             ("2020-2024 − 1990-1999", "20"), ("1980-1989 − 1990-1999", "80"), ("2000-2009 − 1990-1999", "00")]:
                r = cs[(cs.marco == f) & (cs.variable == var) & (cs.comparacion == comp)].iloc[0]
                key = f"{fk}_d_{vk}_{ck}"
                if var == "vision_vida":
                    V[key] = num(r["diff"], signed=True)
                    V[key + "_ci"] = f"[{num(r.diff_lo, signed=True)}; {num(r.diff_hi, signed=True)}]"
                else:
                    V[key] = pp(r["diff"])
                    V[key + "_ci"] = ci_pp(r.diff_lo, r.diff_hi)
                V[key + "_ratio"] = num(r.ratio)
                V[key + "_ratio_ci"] = f"[{num(r.ratio_lo)}; {num(r.ratio_hi)}]"
    ea = t("efectos_ajustados.csv")
    for f, fk in fr.items():
        for var, vk in [("y_feliz", "feliz"), ("y_tragico", "trag"), ("y_tono_positivo", "tono"), ("vision_vida", "vision")]:
            r = ea[(ea.marco == f) & (ea.variable == var)].iloc[0]
            if var == "vision_vida":
                V[f"{fk}_adj_{vk}"] = num(r.efecto_ajustado, signed=True)
                V[f"{fk}_adj_{vk}_ci"] = f"[{num(r.ic95_inf, signed=True)}; {num(r.ic95_sup, signed=True)}]"
            else:
                V[f"{fk}_adj_{vk}"] = pp(r.efecto_ajustado)
                V[f"{fk}_adj_{vk}_ci"] = ci_pp(r.ic95_inf, r.ic95_sup)

    sn = t("sensibilidad.csv")
    keys = {
        "Definición amplia: feliz o agridulce": "def_amplia", "Definición estricta: feliz y tono de cierre positivo": "def_estricta",
        "Ponderado por popularidad (votos IMDb)": "votos", "Incluye no clasificables como no felices": "incl_nc",
        "Solo etiquetas del anotador A (sin adjudicación)": "soloA", "Solo etiquetas del anotador B (sin adjudicación)": "soloB",
        "Solo acuerdo inicial entre anotadores": "acuerdo", "Solo confianza alta (3) en ambos (selecciona casos claros)": "conf3",
        "Solo producciones solo de EE. UU.": "usonly", "Umbral de popularidad más estricto (top 20/año)": "top20",
        "Excluye películas reconocidas por ambos anotadores": "norec",
        "Visión de la vida ponderada por votos": "vision_votos",
    }
    for f, fk in fr.items():
        for name, k in keys.items():
            r = sn[(sn.marco == f) & (sn.especificacion == name)].iloc[0]
            if k == "vision_votos":
                V[f"{fk}_s_{k}"] = num(r["diff"], signed=True)
                V[f"{fk}_s_{k}_ci"] = f"[{num(r.diff_lo, signed=True)}; {num(r.diff_hi, signed=True)}]"
            else:
                V[f"{fk}_s_{k}"] = pp(r["diff"])
                V[f"{fk}_s_{k}_ci"] = ci_pp(r.diff_lo, r.diff_hi)
            V[f"{fk}_s_{k}_n"] = f"{int(r.n0)}/{int(r.n1)}"
            V[f"{fk}_s_{k}_v0"], V[f"{fk}_s_{k}_v1"] = pct(r.valor_1990s), pct(r.valor_comparado)

    ALT = ["Definición amplia: feliz o agridulce", "Definición estricta: feliz y tono de cierre positivo",
           "Ponderado por popularidad (votos IMDb)", "Incluye no clasificables como no felices",
           "Solo etiquetas del anotador A (sin adjudicación)", "Solo etiquetas del anotador B (sin adjudicación)",
           "Solo acuerdo inicial entre anotadores", "Solo confianza alta (3) en ambos (selecciona casos claros)",
           "Solo producciones solo de EE. UU.", "Umbral de popularidad más estricto (top 20/año)"]
    for f, fk in fr.items():
        alt = sn[(sn.marco == f) & sn.especificacion.isin(ALT) & (sn.n0 >= 20) & (sn.n1 >= 20)]
        alt_nv = alt[~alt.especificacion.str.contains("votos")]
        V[f"{fk}_sens_n"] = str(len(alt))
        V[f"{fk}_sens_n_neg"] = str(int((alt["diff"] < 0).sum()))
        V[f"{fk}_sens_min_abs"] = pp(alt_nv["diff"].abs().min()).lstrip("+")
        V[f"{fk}_sens_max_abs"] = pp(alt_nv["diff"].abs().max()).lstrip("+")
        ex0 = alt[(alt.diff_lo > 0) | (alt.diff_hi < 0)]
        V[f"{fk}_sens_n_excl0"] = str(len(ex0))
        V[f"{fk}_sens_excl0_nombres"] = "; ".join(f"«{x}»" for x in ex0["especificacion"]) or "ninguna"
    rv = sn[(sn.marco == "popular") & (sn.especificacion == "Ponderado por popularidad (votos IMDb)")].iloc[0]
    V["pop_s_votos_neff0"] = str(int(round(rv.n_ef0)))
    # qué contrastes del marco popular (2010-2024 − 90s) excluyen el cero
    names = {"y_feliz": "finales felices", "y_agridulce": "agridulces", "y_ambiguo": "ambiguos", "y_tragico": "trágicos",
             "y_tono_positivo": "tono positivo", "vision_vida": "visión de la vida"}
    for f, fk in fr.items():
        cc = cs[(cs.marco == f) & (cs.comparacion == "2010-2024 − 1990-1999")]
        ex = cc[(cc.diff_lo > 0) | (cc.diff_hi < 0)]
        V[f"{fk}_excl0_vars"] = ", ".join(names[v] for v in ex.variable) or "ninguno"
        V[f"{fk}_excl0_n"] = str(len(ex))
    for var, vk in [("y_tragico", "trag"), ("y_tono_positivo", "tono")]:
        r = cs[(cs.marco == "popular") & (cs.variable == var) & (cs.comparacion == "2010-2024 − 1990-1999")].iloc[0]
        V[f"pop_d_{vk}_rec_hi_abs"] = pp(abs(r.diff_hi)).lstrip("+")
        V[f"pop_d_{vk}_rec_lo_abs"] = pp(abs(r.diff_lo)).lstrip("+")
    r = cs[(cs.marco == "popular") & (cs.variable == "vision_vida") & (cs.comparacion == "2010-2024 − 1990-1999")].iloc[0]
    V["pop_d_vision_rec_lo_abs"] = num(abs(r.diff_lo))
    r0 = cs[(cs.marco == "popular") & (cs.variable == "y_feliz") & (cs.comparacion == "2010-2024 − 1990-1999")].iloc[0]
    V["pop_d_feliz_rec_lo_abs"] = pp(abs(r0.diff_lo)).lstrip("+")
    cg = t("composicion_generos.csv").set_index(["frame", "periodo"])
    for gen, gk in [("Acción/aventura", "accion"), ("Animación", "anim"), ("Comedia", "comedia")]:
        V[f"comp_{gk}_90"] = pct(cg.loc[("popular", "1990-1999"), gen], 0)
        V[f"comp_{gk}_rec"] = pct(cg.loc[("popular", "2010-2024"), gen], 0)
    V["n_reanotadas"] = str(len(t("reanotacion_correccion_sinopsis.csv")))

    fo = t("comparacion_follows_accion.csv")
    p = fo[fo.marco == "popular"].set_index("grupo")
    V["fol_8099"], V["fol_8099_ci"] = pct(p.loc["1980-1999", "feliz"]), ci_pct(p.loc["1980-1999", "ic95_inf"], p.loc["1980-1999", "ic95_sup"])
    V["fol_1024"], V["fol_1024_ci"] = pct(p.loc["2010-2024", "feliz"]), ci_pct(p.loc["2010-2024", "ic95_inf"], p.loc["2010-2024", "ic95_sup"])
    dr = p.loc["diferencia 2010-2024 − 1980-1999"]
    V["fol_diff"], V["fol_diff_ci"] = pp(dr.feliz), ci_pp(dr.ic95_inf, dr.ic95_sup)
    V["fol_n_8099"], V["fol_n_1024"] = str(int(p.loc["1980-1999", "n"])), str(int(p.loc["2010-2024", "n"]))
    V["fol_80"], V["fol_90"] = pct(p.loc["1980-1989", "feliz"]), pct(p.loc["1990-1999", "feliz"])

    g = t("genero_contrastes.csv")
    gp = g[g.marco == "popular"].set_index("genero")
    for gen, gk in [("Acción/aventura", "accion"), ("Comedia", "comedia"), ("Terror", "terror"), ("Thriller/crimen", "thriller")]:
        V[f"g_{gk}_90"], V[f"g_{gk}_rec"] = pct(gp.loc[gen, "feliz_1990s"], 0), pct(gp.loc[gen, "feliz_2010_2024"], 0)
        V[f"g_{gk}_d"] = pp(gp.loc[gen, "dif_pp"] / 100)
        V[f"g_{gk}_ci"] = ci_pp(gp.loc[gen, "dif_ic95_inf_pp"] / 100, gp.loc[gen, "dif_ic95_sup_pp"] / 100)
        V[f"g_{gk}_n"] = f"{int(gp.loc[gen, 'n_1990s'])}/{int(gp.loc[gen, 'n_2010_2024'])}"

    gex = gp[(gp.dif_ic95_inf_pp > 0) | (gp.dif_ic95_sup_pp < 0)]
    V["g_excl0_n"] = str(len(gex))
    V["g_excl0_texto"] = ("en ningún género el intervalo excluye el cero" if gex.empty
                          else "el intervalo excluye el cero en: " + ", ".join(gex.index))
    gmin = gp["dif_pp"].idxmin()
    V["g_mayor_caida"], V["g_mayor_caida_d"] = gmin, pp(gp.loc[gmin, "dif_pp"] / 100)
    dgg = dg[dg.dimension == "genre_main"].set_index("grupo")
    dgg = dgg[dgg.n >= 30].sort_values("desacuerdo_final", ascending=False)
    V["dis_top_generos"] = " y ".join(f"{g_.lower()} ({pct(r_.desacuerdo_final, 0)})" for g_, r_ in dgg.head(2).iterrows())
    rf = t("reconocimiento_por_marco.csv").set_index(["frame", "cohort"])
    V["rec_pop_any_min"] = pct(rf.xs("popular")["reconocida_alguno"].min(), 0)
    V["rec_pop_any_max"] = pct(rf.xs("popular")["reconocida_alguno"].max(), 0)
    V["rec_amp_any_min"] = pct(rf.xs("amplio")["reconocida_alguno"].min(), 0)
    V["rec_amp_any_max"] = pct(rf.xs("amplio")["reconocida_alguno"].max(), 0)
    V["rec_pop_ambos"] = pct((rf.xs("popular")["reconocida_ambos"] * rf.xs("popular")["n"]).sum() / rf.xs("popular")["n"].sum(), 0)
    V["pop_s_noreca_n"] = f"{int(sn[(sn.marco == 'popular') & sn.especificacion.str.startswith('Excluye películas reconocidas por algún')].iloc[0].n0 + sn[(sn.marco == 'popular') & sn.especificacion.str.startswith('Excluye películas reconocidas por algún')].iloc[0].n1)}"

    fv = t("final_vs_vision.csv").set_index("final")
    for c, k in [("FELIZ", "feliz"), ("AGRIDULCE", "agri"), ("AMBIGUO", "amb"), ("TRAGICO", "trag")]:
        V[f"fv_{k}"] = num(fv.loc[c, "vision_media"])

    se = t("potencia_encuesta.csv")
    V["enc_5pp"] = str(int(se.iloc[0]["participantes_necesarios"]))
    V["enc_h2_10"] = str(int(se.iloc[3]["participantes_necesarios"]))
    return V


def render(name: str, V: dict | None = None) -> str:
    V = V or values()
    tmpl = (TEMPLATES / f"{name}.md").read_text(encoding="utf-8")
    return tmpl.format_map(V)


def main() -> None:
    V = values()
    for name in ("informe", "resumen_ejecutivo"):
        (ROOT / "reports" / f"{name}.md").write_text(render(name, V), encoding="utf-8")
    (TABLES / "valores_informe.json").write_text(json.dumps(V, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
