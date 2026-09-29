"""Gráficos del informe (PNG estáticos). Leen solo tablas de reports/tables/ generadas por analysis.py."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import FIGURES, INTERIM, TABLES

# Paleta: diverging azul↔rojo con gris neutro para los finales; categórica fija para marcos.
C_FINAL = {"FELIZ": "#2a78d6", "AGRIDULCE": "#86b6ef", "AMBIGUO": "#b5b3ad", "TRAGICO": "#e34948"}
LAB_FINAL = {"FELIZ": "Feliz", "AGRIDULCE": "Agridulce", "AMBIGUO": "Ambiguo", "TRAGICO": "Trágico"}
C_FRAME = {"popular": "#2a78d6", "amplio": "#eb6834"}
LAB_FRAME = {"popular": "Marco popular (50 más votadas/año)", "amplio": "Marco amplio (estratificado por popularidad)"}
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
COHORTS = ["1980-1989", "1990-1999", "2000-2009", "2010-2019", "2020-2024"]
COHORT_LAB = ["1980-89", "1990-99", "2000-09", "2010-19", "2020-24*"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": TEXT,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "figure.dpi": 150, "savefig.bbox": "tight", "legend.frameon": False,
})


def _note(fig, text):
    fig.text(0.01, -0.02, text, fontsize=7.5, color=MUTED, ha="left", va="top", wrap=True)


def fig_distribution() -> None:
    df = pd.read_csv(INTERIM / "analitico_principal.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.8))
    for ax, frame in zip(axes, ("popular", "amplio")):
        d = df[df["frame"] == frame]
        left = np.zeros(len(COHORTS))
        for cat in C_FINAL:
            vals = []
            for c in COHORTS:
                g = d[(d["cohort"] == c) & d["clasificable"]]
                vals.append(np.average(g["final"] == cat, weights=g["w_design"]) if len(g) else np.nan)
            vals = np.array(vals)
            ax.barh(range(len(COHORTS)), vals, left=left, color=C_FINAL[cat], edgecolor="white", linewidth=2,
                    height=0.62, label=LAB_FINAL[cat])
            for i, (v, l0) in enumerate(zip(vals, left)):
                if v >= 0.06:
                    ax.text(l0 + v / 2, i, f"{v * 100:.0f}", ha="center", va="center", fontsize=8,
                            color="white" if cat in ("FELIZ", "TRAGICO") else TEXT)
            left += vals
        ns = [f"n={int(((d['cohort'] == c) & d['clasificable']).sum())}" for c in COHORTS]
        ax.set_yticks(range(len(COHORTS)), [f"{a}\n{n}" for a, n in zip(COHORT_LAB, ns)])
        ax.invert_yaxis()
        ax.set_xlim(0, 1)
        ax.set_xticks([0, .25, .5, .75, 1], ["0 %", "25 %", "50 %", "75 %", "100 %"])
        ax.grid(axis="y", visible=False)
        ax.set_title(LAB_FRAME[frame], fontsize=10, color=TEXT, loc="left")
    axes[0].legend(ncol=4, loc="upper left", bbox_to_anchor=(0, 1.2), fontsize=9)
    fig.suptitle("Tipo de final por cohorte (% de películas clasificables, ponderado por diseño)",
                 x=0.01, ha="left", y=1.1, fontsize=11.5, color=TEXT)
    _note(fig, "Etiquetas de dos modelos de lenguaje anotando sinopsis de Wikipedia a ciegas, con adjudicación; sin "
               "validación humana. *2020-2024 abarca solo cinco años. Fuente: tablas distribucion_finales_recuentos.csv "
               "y descriptivos_marco_cohorte.csv.")
    fig.savefig(FIGURES / "fig1_distribucion_finales.png")
    plt.close(fig)


def _dot_ci(ax, desc, variable, pct=True):
    for k, frame in enumerate(("popular", "amplio")):
        d = desc[(desc["frame"] == frame) & (desc["variable"] == variable)].set_index("cohort").reindex(COHORTS)
        x = np.arange(len(COHORTS)) + (k - 0.5) * 0.18
        m = 100 if pct else 1
        ax.errorbar(x, d["estimacion"] * m, yerr=[(d["estimacion"] - d["ic95_inf"]) * m, (d["ic95_sup"] - d["estimacion"]) * m],
                    fmt="o", ms=6, color=C_FRAME[frame], ecolor=C_FRAME[frame], elinewidth=2, capsize=0,
                    label=LAB_FRAME[frame], markeredgecolor="white", markeredgewidth=1.2)
    ax.set_xticks(range(len(COHORTS)), COHORT_LAB)
    ax.grid(axis="x", visible=False)


def fig_happy_ci() -> None:
    desc = pd.read_csv(TABLES / "descriptivos_marco_cohorte.csv")
    fig, ax = plt.subplots(figsize=(7.5, 4))
    _dot_ci(ax, desc, "y_feliz")
    ax.set_ylabel("% de finales felices")
    ax.set_ylim(20, 100)
    ax.legend(loc="lower left", fontsize=8.5)
    ax.set_title("Proporción de finales felices por cohorte, con IC 95 %", loc="left", fontsize=11.5, color=TEXT)
    _note(fig, "IC de Wilson con tamaño efectivo de Kish. Excluye no clasificables. *2020-2024: cinco años. "
               "Fuente: descriptivos_marco_cohorte.csv.")
    fig.savefig(FIGURES / "fig2_finales_felices_ic.png")
    plt.close(fig)


def fig_vision_ci() -> None:
    desc = pd.read_csv(TABLES / "descriptivos_marco_cohorte.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    _dot_ci(axes[0], desc, "vision_vida", pct=False)
    axes[0].axhline(0, color=MUTED, lw=0.8)
    axes[0].set_ylabel("Media (−2 pesimista … +2 optimista)")
    axes[0].set_title("Visión general de la vida", loc="left", fontsize=10.5, color=TEXT)
    _dot_ci(axes[1], desc, "y_tono_positivo")
    axes[1].set_ylabel("% con tono de cierre positivo")
    axes[1].set_ylim(40, 100)
    axes[1].set_title("Tono emocional del cierre (esperanza, alivio o conexión)", loc="left", fontsize=10.5, color=TEXT)
    axes[1].legend(loc="lower left", fontsize=8)
    _note(fig, "Visión de la vida = media de agencia, posibilidad de cambio, valor de los vínculos y expectativa de futuro "
               "(mínimo 3 de 4 ítems). IC 95 %. Fuente: descriptivos_marco_cohorte.csv.")
    fig.savefig(FIGURES / "fig3_vision_y_tono_ic.png")
    plt.close(fig)


def fig_genre() -> None:
    g = pd.read_csv(TABLES / "genero_contrastes.csv")
    g = g[(g["marco"] == "popular")].sort_values("n_1990s", ascending=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    y = np.arange(len(g))
    ax.hlines(y, g["feliz_1990s"] * 100, g["feliz_2010_2024"] * 100, color=GRID, lw=3)
    ax.plot(g["feliz_1990s"] * 100, y, "o", color="#4a3aa7", ms=8, label="1990-1999", markeredgecolor="white")
    ax.plot(g["feliz_2010_2024"] * 100, y, "o", color="#1baf7a", ms=8, label="2010-2024", markeredgecolor="white")
    ax.set_yticks(y, [f"{r.genero}  (n={int(r.n_1990s)} / {int(r.n_2010_2024)})" for r in g.itertuples()])
    ax.set_xlim(0, 100)
    ax.set_xlabel("% de finales felices")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=9)
    ax.set_title("Finales felices por género principal: noventa frente a 2010-2024 (marco popular)",
                 loc="left", fontsize=11, color=TEXT)
    _note(fig, "Muestras pequeñas por género: en todos los géneros el IC 95 % de la diferencia incluye el cero "
               "(tabla genero_contrastes.csv). Género principal asignado por prioridad sobre los géneros de IMDb.")
    fig.savefig(FIGURES / "fig4_genero.png")
    plt.close(fig)


def fig_sensitivity() -> None:
    s = pd.read_csv(TABLES / "sensibilidad.csv")
    s = s[(s["variable"] != "vision_vida") & (s["n0"] >= 20) & (s["n1"] >= 20)]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True)
    specs = list(dict.fromkeys(s["especificacion"]))
    for ax, frame in zip(axes, ("popular", "amplio")):
        d = s[s["marco"] == frame].set_index("especificacion").reindex(specs)
        y = np.arange(len(specs))
        ax.errorbar(d["diff"] * 100, y, xerr=[(d["diff"] - d["diff_lo"]) * 100, (d["diff_hi"] - d["diff"]) * 100],
                    fmt="o", color=C_FRAME[frame], elinewidth=2, ms=6, markeredgecolor="white")
        ax.axvline(0, color=MUTED, lw=1)
        ax.set_title(LAB_FRAME[frame], loc="left", fontsize=10, color=TEXT)
        ax.set_xlabel("Diferencia (puntos porcentuales), 2010-2024 − 1990-1999")
        ax.grid(axis="y", visible=False)
    axes[0].set_yticks(np.arange(len(specs)), specs, fontsize=8.5)
    axes[0].invert_yaxis()
    fig.suptitle("Pruebas de sensibilidad (IC 95 % bootstrap)", x=0.01, ha="left", fontsize=11.5, color=TEXT)
    _note(fig, "Se omiten especificaciones con menos de 20 películas en algún grupo (ver sensibilidad.csv). "
               "Filas de tono y trágico: diferencia en esas proporciones, no en finales felices.")
    fig.savefig(FIGURES / "fig5_sensibilidad.png")
    plt.close(fig)


def fig_dimensions() -> None:
    df = pd.read_csv(INTERIM / "analitico_principal.csv").drop_duplicates("tconst")
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    cats = list(C_FINAL)
    data = [df.loc[df["final"] == c, "vision_vida"].dropna() for c in cats]
    rng = np.random.default_rng(0)
    for i, (c, v) in enumerate(zip(cats, data)):
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=9, color=C_FINAL[c], alpha=0.45, linewidths=0)
        ax.plot([i - 0.25, i + 0.25], [v.mean()] * 2, color=TEXT, lw=2)
    ax.set_xticks(range(len(cats)), [f"{LAB_FINAL[c]}\n(n={len(v)})" for c, v in zip(cats, data)])
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_ylabel("Visión de la vida (−2 … +2)")
    ax.grid(axis="x", visible=False)
    ax.set_title("Final y visión de la vida: muy relacionados, pero no idénticos",
                 loc="left", fontsize=10.5, color=TEXT)
    _note(fig, "Cada punto es una película (ambos marcos, sin duplicar). Línea negra: media. La relación puede estar inflada porque "
               "los mismos anotadores puntúan ambas dimensiones. Fuente: final_vs_vision.csv.")
    fig.savefig(FIGURES / "fig6_final_vs_vision.png")
    plt.close(fig)


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig_distribution()
    fig_happy_ci()
    fig_vision_ci()
    fig_genre()
    fig_sensitivity()
    fig_dimensions()


if __name__ == "__main__":
    main()
