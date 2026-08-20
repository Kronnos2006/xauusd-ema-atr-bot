"""
Chequeo de frecuencia -- hipotesis candidata "Risk-on/off via US500 H4 ->
XAUUSD" (2026-08-04, tercer candidato de la ronda intradia -- driver
externo al precio del oro, distinto de DXY -- ver Bitácora de decisiones.md).

Mecanismo: caida intradia en acciones (risk-off) -> flujo hacia oro como
refugio. A diferencia de los candidatos DXY (umbral simetrico, cualquier
signo dispara episodio con direccion determinada por el signo), acá el
mecanismo es direccional por diseño: SOLO una caida cuenta como episodio
de risk-off -- una suba en US500 no es la condicion que se esta testeando.

Definicion (Fase 0, mismo patron de std de la serie completa que el resto
de los candidatos, sin rolling):
retorno_H4(US500) < -k * std(retorno_H4), k en {0.75, 1.0, 1.25}.
Un episodio es una racha maxima de velas H4 consecutivas con la condicion activa.

Nota de disponibilidad de datos: US500 (CFD de este broker) tiene historia
H4 real desde 2012-08-06 -- no es un limite de maxbars del pipeline (16897
velas, muy por debajo del cap de 100000), es que el broker no tiene el
instrumento antes de esa fecha. El histórico usable para este triage son
~14 años, no los ~22 de XAUUSD/DXY.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\us500_h4.csv"
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
    print(f"US500 H4 disponible (historia real del broker, no limitado por maxbars): "
          f"{df['time'].min()} -> {df['time'].max()} ({anios_total:.1f} años, {len(df)} velas)")

    ret = df["close"].pct_change(1)
    std = ret.std()
    print(f"Std retorno H4 (serie completa): {std:.6f}\n")

    print(f"{'k':>6} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (velas)':>18} | {'dur. max':>8}")
    for k in K_GRID:
        cond = (ret < -k * std).fillna(False)  # SOLO caidas -- direccional por diseño, no |ret|
        n_ep, duraciones = contar_episodios(cond)
        ep_anio = n_ep / anios_total
        dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
        dur_max = max(duraciones) if duraciones else 0
        print(f"{k:>6.2f} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    print("\nUsar el ep/año del k más restrictivo de la grilla como input conservador de "
          "triage_frecuencia.py (mismo criterio que los candidatos previos).")


if __name__ == "__main__":
    main()
