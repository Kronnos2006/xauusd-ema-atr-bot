"""
Chequeo de frecuencia -- hipotesis candidata "Shock de petroleo (WTI) H4 ->
EURUSD" (H3 del marco EURUSD, 2026-08-04 -- ver Plan de investigación EURUSD.md).

Mecanismo: la Eurozona es historicamente mas dependiente de importacion de
energia que EE.UU. (mas aun tras el boom de shale de EE.UU.) -- una SUBA
fuerte del petroleo deteriora los terminos de intercambio de la Eurozona
proporcionalmente mas que los de EE.UU., sesgo BAJISTA en EURUSD. Direccional
por diseño (mismo criterio que Risk-off US500): solo SUBAS de WTI cuentan
como episodio, una caida de petroleo no es la condicion testeada.

Definicion (Fase 0, std de la serie completa, sin rolling -- mismo patron
que el resto de los candidatos):
retorno_H4(WTI) > k * std(retorno_H4), k en {0.75, 1.0, 1.25}.
Un episodio es una racha maxima de velas H4 consecutivas con la condicion activa.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\wti_h4.csv"
K_GRID = [0.75, 1.0, 1.25]


def contar_episodios(serie_bool):
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df = pd.read_csv(RUTA_CSV)
    df["time"] = pd.to_datetime(df["time"], unit="s") if df["time"].dtype != object else pd.to_datetime(df["time"])

    anios_total = (df["time"].max() - df["time"].min()).days / 365.25
    print(f"WTI H4 disponible: {df['time'].min()} -> {df['time'].max()} "
          f"({anios_total:.1f} años, {len(df)} velas)")

    ret = df["close"].pct_change(1)
    std = ret.std()
    print(f"Std retorno H4 (serie completa): {std:.6f}\n")

    print(f"{'k':>6} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (velas)':>18} | {'dur. max':>8}")
    for k in K_GRID:
        cond = (ret > k * std).fillna(False)  # SOLO subas -- direccional por diseño
        n_ep, duraciones = contar_episodios(cond)
        ep_anio = n_ep / anios_total
        dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
        dur_max = max(duraciones) if duraciones else 0
        print(f"{k:>6.2f} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    print("\nUsar el ep/año del k más restrictivo de la grilla como input conservador de "
          "triage_frecuencia.py (mismo criterio que los candidatos previos).")


if __name__ == "__main__":
    main()
