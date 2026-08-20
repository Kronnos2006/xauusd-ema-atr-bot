"""H2 — Donchian Breakout (N=20). Fase 2 Invenio.

Hipótesis: un cierre por fuera del rango de los 20 días previos (excluyendo
la barra actual, sin look-ahead) predice continuación en esa dirección.

NO corre el período de Test (2020-2026). Ver utils.load_dev_data().
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from utils import RESULTADOS_DIR, TRAIN, VALIDATION, load_dev_data, report_period, run_backtest

N = 20


def build_signal(df, n):
    upper = df["High"].shift(1).rolling(n).max()
    lower = df["Low"].shift(1).rolling(n).min()

    sig = pd.Series(np.nan, index=df.index)
    sig[df["Close"] > upper] = 1.0
    sig[df["Close"] < lower] = -1.0
    return sig


def main():
    df_dev = load_dev_data()

    label = f"H2_D{N}"
    signal = build_signal(df_dev, N)
    result = run_backtest(df_dev, signal, label)

    for period_name, period in [("train", TRAIN), ("validation", VALIDATION)]:
        report_period(result, period, RESULTADOS_DIR / period_name)


if __name__ == "__main__":
    main()
