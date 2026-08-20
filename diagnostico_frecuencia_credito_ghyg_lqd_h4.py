"""
Chequeo de frecuencia -- hipotesis candidata "Spread de credito HY/IG
(GHYG/LQD) H4 -> XAUUSD" (2026-08-04, cuarto candidato de la ronda
intradia -- driver externo al precio del oro -- ver Bitácora de decisiones.md).

Mecanismo: ensanchamiento del spread de credito high-yield/investment-grade
(aversion al riesgo crediticio) -> flujo hacia oro como refugio. No hay
serie de yield-spread intradia disponible en este broker -- se usa el
proxy estandar de la industria: la RATIO GHYG/LQD (high-yield sobre
investment-grade). Cuando el credito se deteriora, high-yield cae mas que
investment-grade (mayor beta al riesgo), asi que la ratio CAE -- eso es
"ensanchamiento" en este proxy. Direccional por diseño (igual que el
candidato US500): solo caidas de la ratio cuentan como episodio de
risk-off crediticio, una suba de la ratio no es la condicion testeada.

Definicion (Fase 0, std de la serie completa, sin rolling -- mismo patron
que el resto de los candidatos):
retorno_H4(ratio GHYG/LQD) < -k * std(retorno_H4(ratio)), k en {0.75, 1.0, 1.25}.

Nota de disponibilidad: GHYG (sustituto de HYG -- HYG solo tiene 402 velas
H4 desde 2025-10-27 en este broker, inutilizable) tiene historia real desde
2012-04-05 (~14.3 años solapados con LQD, que llega a 2003). El histórico
usable queda acotado por GHYG, comparable en longitud al candidato US500
(14.0 años) -- no es casualidad, ambos CFDs de este broker arrancan cerca
de 2012.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_GHYG = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\ghyg_h4.csv"
RUTA_LQD = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\lqd_h4.csv"
K_GRID = [0.75, 1.0, 1.25]


def contar_episodios(serie_bool):
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    ghyg = pd.read_csv(RUTA_GHYG).rename(columns={"close": "ghyg"})
    lqd = pd.read_csv(RUTA_LQD).rename(columns={"close": "lqd"})
    ghyg["time"] = pd.to_datetime(ghyg["time"])
    lqd["time"] = pd.to_datetime(lqd["time"])

    df = ghyg.merge(lqd, on="time", how="inner").sort_values("time").reset_index(drop=True)
    df["ratio"] = df["ghyg"] / df["lqd"]

    anios_total = (df["time"].max() - df["time"].min()).days / 365.25
    print(f"GHYG/LQD solapado (H4): {df['time'].min()} -> {df['time'].max()} "
          f"({anios_total:.1f} años, {len(df)} velas)")

    ret = df["ratio"].pct_change(1)
    std = ret.std()
    print(f"Std retorno H4 de la ratio (serie completa): {std:.6f}\n")

    print(f"{'k':>6} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (velas)':>18} | {'dur. max':>8}")
    for k in K_GRID:
        cond = (ret < -k * std).fillna(False)  # SOLO caidas de la ratio -- ensanchamiento del spread
        n_ep, duraciones = contar_episodios(cond)
        ep_anio = n_ep / anios_total
        dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
        dur_max = max(duraciones) if duraciones else 0
        print(f"{k:>6.2f} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    print("\nUsar el ep/año del k más restrictivo de la grilla como input conservador de "
          "triage_frecuencia.py (mismo criterio que los candidatos previos).")


if __name__ == "__main__":
    main()
