"""H3 — Cross-Sectional Momentum FX. Fase 3 Invenio.

Corre las 3 variantes pre-registradas (H3-20, H3-60, H3-120), cada una
independiente, en Train y Validation. NO corre ni toca el período de Test
(2020-2026). Ver README.md para las reglas completas.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils_fase3 import (
    N_VARIANTS, RESULTADOS_DIR, TRAIN, VALIDATION,
    load_dev_data, report_h3_period, run_h3_variant, write_audit_table,
)


def plot_equity_conjunta(results, period, out_path, titulo):
    start, end = period
    fig, ax = plt.subplots(figsize=(11, 5))
    for res in results:
        ret_net = res["ret_net_daily"]
        mask = (ret_net.index >= start) & (ret_net.index <= end)
        sub = ret_net.loc[mask]
        equity = 100.0 * (1 + sub).cumprod()
        ax.plot(equity.index, equity.values, label=res["label"])
    ax.set_title(titulo)
    ax.set_ylabel("Equity neta (base 100)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)


def plot_retorno_anual_variantes(tablas_por_variante, out_path, titulo):
    fig, ax = plt.subplots(figsize=(11, 5))
    width = 0.8 / len(tablas_por_variante)
    for i, (label, tabla) in enumerate(tablas_por_variante.items()):
        x = np.arange(len(tabla)) + i * width
        ax.bar(x, tabla["retorno_neto_pct"], width=width, label=label)
    years = list(tablas_por_variante.values())[0]["year"]
    ax.set_xticks(np.arange(len(years)) + width * (len(tablas_por_variante) - 1) / 2)
    ax.set_xticklabels(years)
    ax.set_ylabel("Retorno neto anual (%)")
    ax.set_title(titulo)
    ax.axhline(0, color="black", linewidth=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)


def plot_heatmap_posiciones(result, out_path):
    signal_df = result["signal_df"]
    fig, ax = plt.subplots(figsize=(14, 4))
    im = ax.imshow(signal_df.T.values, aspect="auto", cmap="coolwarm", vmin=-1, vmax=1,
                    interpolation="nearest")
    ax.set_yticks(range(len(signal_df.columns)))
    ax.set_yticklabels(signal_df.columns)
    step = max(1, len(signal_df.index) // 20)
    ax.set_xticks(range(0, len(signal_df.index), step))
    ax.set_xticklabels([d.strftime("%Y-%m") for d in signal_df.index[::step]], rotation=90)
    ax.set_title(f"{result['label']} — Heatmap de posiciones (rojo=LONG, azul=SHORT)")
    fig.colorbar(im, ax=ax, label="Señal", ticks=[-1, 0, 1])
    fig.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)


def main():
    dev_frames, quality_report, flagged = load_dev_data()
    print("=== Chequeo de calidad de datos (2005-2019) ===")
    print(quality_report.to_string(index=False))
    if flagged:
        print(f"[ATENCION] Pares que superan el 10% de faltantes: {flagged}")
    print()

    results = []
    for n in N_VARIANTS:
        print(f"--- Corriendo H3-N{n} ---")
        result = run_h3_variant(dev_frames, n)
        results.append(result)

        audit_path = RESULTADOS_DIR / "train" / f"auditoria_rebalanceos_H3_N{n}.csv"
        write_audit_table(result, TRAIN, audit_path)

        plot_heatmap_posiciones(result, RESULTADOS_DIR / f"H3_N{n}_heatmap_posiciones.png")

    tablas_train, tablas_validation = {}, {}
    for result in results:
        m_train, _, tabla_train = report_h3_period(
            result, TRAIN, RESULTADOS_DIR / "train", apply_survival_criteria=False)
        m_val, _, tabla_val = report_h3_period(
            result, VALIDATION, RESULTADOS_DIR / "validation", apply_survival_criteria=True)
        tablas_train[result["label"]] = tabla_train
        tablas_validation[result["label"]] = tabla_val

    plot_equity_conjunta(results, TRAIN, RESULTADOS_DIR / "train" / "H3_equity_todas_variantes.png",
                          "H3 — Equity neta por variante (Train 2005-2014)")
    plot_equity_conjunta(results, VALIDATION, RESULTADOS_DIR / "validation" / "H3_equity_todas_variantes.png",
                          "H3 — Equity neta por variante (Validation 2015-2019)")

    plot_retorno_anual_variantes(tablas_train, RESULTADOS_DIR / "train" / "H3_retorno_anual_variantes.png",
                                  "H3 — Retorno neto anual por variante (Train)")
    plot_retorno_anual_variantes(tablas_validation, RESULTADOS_DIR / "validation" / "H3_retorno_anual_variantes.png",
                                  "H3 — Retorno neto anual por variante (Validation)")

    print()
    print("=== Veredicto de supervivencia — Validation ===")
    resumen_val = pd.read_csv(RESULTADOS_DIR / "validation" / "resumen.csv")
    cols = ["label", "sharpe_anualizado", "retorno_neto_pct", "criterio_C_annos_pos",
            "criterio_D_concentracion", "veredicto"]
    print(resumen_val[cols].to_string(index=False))


if __name__ == "__main__":
    main()
