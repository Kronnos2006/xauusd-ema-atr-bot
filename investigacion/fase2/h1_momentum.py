"""H1 — Time-Series Momentum. Fase 2 Invenio.

Hipótesis: para cada N en [20, 60, 120, 252], el signo del retorno de los
últimos N días predice el retorno del día siguiente.

Los 4 valores de N son hipótesis independientes — se reportan por separado,
nunca se elige "el mejor N" para declarar que H1 funciona.

NO corre el período de Test (2020-2026). Ver utils.load_dev_data().
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from utils import RESULTADOS_DIR, TRAIN, VALIDATION, load_dev_data, report_period, run_backtest

N_VALUES = [20, 60, 120, 252]


def build_signal(df, n):
    r = df["Close"] / df["Close"].shift(n) - 1
    sig = pd.Series(np.nan, index=df.index)
    sig[r > 0] = 1.0
    sig[r < 0] = -1.0
    # r == 0 (o NaN por warm-up) queda NaN -> run_backtest hace ffill,
    # que sostiene la posición anterior, tal como pide la especificación.
    return sig


def main():
    df_dev = load_dev_data()

    for n in N_VALUES:
        label = f"H1_N{n}"
        signal = build_signal(df_dev, n)
        result = run_backtest(df_dev, signal, label)

        for period_name, period in [("train", TRAIN), ("validation", VALIDATION)]:
            report_period(result, period, RESULTADOS_DIR / period_name)


if __name__ == "__main__":
    main()
