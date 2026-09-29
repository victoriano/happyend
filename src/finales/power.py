"""Cálculo del tamaño de muestra a partir del piloto (registro de decisiones D-012).

Usa la proporción de finales felices y la desviación típica de la visión de la vida observadas en el piloto
(etiquetas finales = acuerdo de A y B; en caso de desacuerdo, media de ambos anotadores para la proporción).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import annotation as an
from . import stats as st
from .analysis import load_stage
from .config import TABLES


def pilot_parameters() -> dict:
    A, B, _, _ = load_stage("piloto")
    pr = an.pair(A, B)
    both = pr[pr["_merge"] == "both"]
    cls = both["final_A"].isin(an.ORDINAL_FINAL) & both["final_B"].isin(an.ORDINAL_FINAL)
    p_happy = float((((both["final_A"] == "FELIZ").astype(float) + (both["final_B"] == "FELIZ").astype(float)) / 2)[cls].mean())
    va = an.vision_score(both.rename(columns={f"{k}_A": k for k in an.ITEMS}))
    vb = an.vision_score(both.rename(columns={f"{k}_B": k for k in an.ITEMS}))
    v = (va + vb) / 2
    return {"n_piloto": int(len(both)), "p_feliz_piloto": p_happy, "sd_vision_piloto": float(v.std(ddof=1)),
            "media_vision_piloto": float(v.mean())}


def table(mdr_pp=(10, 15, 20), n_cap_popular: int = 150, n_cap_amplio: int = 50) -> pd.DataFrame:
    par = pilot_parameters()
    p = par["p_feliz_piloto"]
    rows = []
    for d in mdr_pp:
        p2 = p - d / 100
        n90, n_rec = st.n_two_proportions(p, p2, ratio=2.0)  # 2010-2024 agrupa dos cohortes
        rows.append({"contraste": "Final feliz: 1990-1999 vs 2010-2024 (n2 = 2·n1)", "diferencia_minima": f"{d} pp",
                     "n_por_cohorte_necesario": n90, "n_total_necesario_2cohortes_mas_referencia": n90 + n_rec})
    for dv in (0.2, 0.3, 0.4):
        n = st.n_two_means(par["sd_vision_piloto"], dv)
        rows.append({"contraste": "Visión de la vida: diferencia de medias (grupos iguales)",
                     "diferencia_minima": f"{dv} puntos", "n_por_cohorte_necesario": n,
                     "n_total_necesario_2cohortes_mas_referencia": np.nan})
    df = pd.DataFrame(rows)
    mde_pop = st.mde_two_proportions(p, n_cap_popular, 2 * n_cap_popular)
    mde_amp = st.mde_two_proportions(p, n_cap_amplio, 2 * n_cap_amplio)
    mde_coh = st.mde_two_proportions(p, n_cap_popular, n_cap_popular)
    info = pd.DataFrame([
        {"contraste": f"MDE con capacidad elegida: popular {n_cap_popular}/cohorte, 90s vs 2010-2024",
         "diferencia_minima": f"{mde_pop * 100:.1f} pp"},
        {"contraste": f"MDE con capacidad elegida: popular {n_cap_popular}/cohorte, 90s vs una cohorte",
         "diferencia_minima": f"{mde_coh * 100:.1f} pp"},
        {"contraste": f"MDE con capacidad elegida: amplio {n_cap_amplio}/cohorte, 90s vs 2010-2024",
         "diferencia_minima": f"{mde_amp * 100:.1f} pp"},
    ])
    out = pd.concat([df, info], ignore_index=True)
    out.to_csv(TABLES / "potencia_piloto.csv", index=False)
    pd.Series(par).to_csv(TABLES / "parametros_piloto.csv", header=["valor"])
    return out


if __name__ == "__main__":
    print(pilot_parameters())
    print(table().to_string())
