"""
Chequeo de frecuencia -- hipotesis candidata "Momentum de precio propio
EURUSD" (2026-08-04, primer candidato del nuevo marco EURUSD tras el
cierre del marco XAUUSD -- ver Bitácora de decisiones.md y CLAUDE.md).

Mecanismo: carry trade unwinding y rebalanceo institucional de FX generan
continuacion de corto plazo en el tipo de cambio (a diferencia del
candidato "Risk-off US500", que era direccional por diseño, acá ambos
signos cuentan -- una suba fuerte predice continuacion alcista, una
caida fuerte predice continuacion bajista).

Definicion (Fase 0, mismo patron que diagnostico_frecuencia_momentum_dxy.py
-- std de la serie completa disponible, sin rolling):
|retorno_1d(EURUSD)| > k * std(retorno_1d), k en {0.75, 1.0, 1.25}.
Un episodio es una racha maxima de dias consecutivos con la condicion activa.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\eurusd_d1.csv"
K_GRID = [0.75, 1.0, 1.25]


def contar_episodios(serie_bool):
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df = pd.read_csv(RUTA_CSV)
    df["time"] = pd.to_datetime(df["time"])

    anios_total = (df["time"].max() - df["time"].min()).days / 365.25
    print(f"EURUSD D1 disponible: {df['time'].min()} -> {df['time'].max()} "
          f"({anios_total:.1f} años, {len(df)} velas)")

    ret = df["close"].pct_change(1)
    std = ret.std()
    print(f"Std retorno 1d (serie completa): {std:.6f}\n")

    print(f"{'k':>6} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (días)':>18} | {'dur. max':>8}")
    for k in K_GRID:
        cond = (ret.abs() > k * std).fillna(False)
        n_ep, duraciones = contar_episodios(cond)
        ep_anio = n_ep / anios_total
        dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
        dur_max = max(duraciones) if duraciones else 0
        print(f"{k:>6.2f} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    print("\nUsar el ep/año del k más restrictivo de la grilla como input conservador de "
          "triage_frecuencia.py (mismo criterio que los candidatos previos).")


if __name__ == "__main__":
    main()
