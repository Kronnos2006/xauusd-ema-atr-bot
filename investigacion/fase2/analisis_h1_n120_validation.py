"""Análisis post-hoc de H1-N120 en Validation (2015-2019): concentración anual
del PF y bootstrap de significancia sobre los trades cerrados.

No es una optimización ni un ajuste de N — es un chequeo de robustez sobre la
hipótesis ya evaluada, pedido explícitamente antes de considerar Test.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from h1_momentum import build_signal
from utils import VALIDATION, load_dev_data, run_backtest

N = 120
N_BOOT = 10_000
SEED = 20260808  # fijo para reproducibilidad, no elegido para maximizar el CI


def profit_factor(returns):
    wins = returns[returns > 0].sum()
    losses = -returns[returns <= 0].sum()
    return wins / losses if losses > 0 else np.inf


def main():
    df_dev = load_dev_data()
    signal = build_signal(df_dev, N)
    result = run_backtest(df_dev, signal, f"H1_N{N}")

    trades = result["trades"]
    start, end = VALIDATION
    mask = (trades["entry_date"] >= pd.Timestamp(start)) & (trades["entry_date"] <= pd.Timestamp(end))
    closed = trades[mask & trades["closed"]].copy()
    n_open = (mask & ~trades["closed"]).sum()

    print(f"Trades cerrados en Validation: {len(closed)} (+{n_open} abierto sin cerrar, excluido)")
    print()

    print("=== PF por año de entrada (a nivel de trade) ===")
    closed["year"] = closed["entry_date"].dt.year
    rows = []
    for year, g in closed.groupby("year"):
        pf_y = profit_factor(g["return_pct"].to_numpy())
        wins = (g["return_pct"] > 0).sum()
        rows.append(dict(year=year, trades=len(g), wins=wins, pf=pf_y,
                          gross_pips=g["pips"].sum()))
    annual = pd.DataFrame(rows)
    print(annual.to_string(index=False))
    print()

    pf_total = profit_factor(closed["return_pct"].to_numpy())
    print(f"PF total (23 trades, punto original): {pf_total:.3f}")
    print()

    print(f"=== Bootstrap PF ({N_BOOT} remuestreos con reposición, seed={SEED}) ===")
    rng = np.random.default_rng(SEED)
    returns = closed["return_pct"].to_numpy()
    n = len(returns)
    boot_pf = np.empty(N_BOOT)
    for i in range(N_BOOT):
        sample = rng.choice(returns, size=n, replace=True)
        boot_pf[i] = profit_factor(sample)

    finite = boot_pf[np.isfinite(boot_pf)]
    n_inf = N_BOOT - len(finite)
    p5, p50, p95 = np.percentile(finite, [5, 50, 95])
    pct_below_1 = (boot_pf <= 1.0).mean() * 100

    print(f"Remuestreos con PF infinito (0 pérdidas en la muestra): {n_inf}/{N_BOOT}")
    print(f"Percentil 5  : {p5:.3f}")
    print(f"Mediana      : {p50:.3f}")
    print(f"Percentil 95 : {p95:.3f}")
    print(f"% de remuestreos con PF <= 1.0: {pct_below_1:.1f}%")

    out_dir = Path(__file__).resolve().parent / "resultados" / "validation"
    annual.to_csv(out_dir / "H1_N120_pf_por_anio.csv", index=False)
    pd.Series({"pf_original": pf_total, "boot_p5": p5, "boot_p50": p50, "boot_p95": p95,
               "pct_boot_le_1": pct_below_1, "n_boot": N_BOOT, "n_boot_inf": n_inf,
               "seed": SEED}).to_csv(out_dir / "H1_N120_bootstrap_pf.csv")


if __name__ == "__main__":
    main()
