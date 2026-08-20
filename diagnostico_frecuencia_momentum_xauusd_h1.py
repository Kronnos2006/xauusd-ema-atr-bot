"""
Chequeo de frecuencia -- hipotesis candidata "Momentum propio XAUUSD H1"
(2026-08-04, segundo candidato de la ronda intradia -- ver Bitácora de
decisiones.md). Mecanismo: el oro se mueve por su PROPIO order flow /
momentum de corto plazo, sin depender de otro activo (a diferencia de los
dos candidatos DXY ya descartados y excluidos como driver -- ver Criterios
de cierre del enfoque.md, NO HACER).

Definicion (Fase 0, mismo patron que diagnostico_frecuencia_momentum_dxy.py
-- std de la serie completa disponible, NO rolling; la version rolling
solo se adopto para el candidato H4-DXY por decision explicita de esa
ficha, no es el default del proyecto):
|retorno_H1(XAUUSD)| > k * std(retorno_H1), k en {0.75, 1.0, 1.25}.
Un episodio es una racha maxima de velas H1 consecutivas con la condicion activa.

Nota de disponibilidad de datos (importante, no silenciada): el terminal
MT5 de este broker tiene maxbars=100000 configurado -- copy_rates_range
falla con "Invalid params" para rangos que impliquen mas de ~100k velas
H1 hacia atras. XAUUSD H1 SI esta disponible mas atras en el broker (D1/H4
llegan a 2004-06-11), pero este pipeline solo puede traer de forma
confiable los ultimos ~99000 velas H1 en una sola llamada (~16.9 años,
desde 2009-09-04) sin tocar la configuracion del terminal. Se usa ese
rango, documentado como limitacion del pipeline, no del broker.
"""
import sys

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

RUTA_CSV = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\xauusd_h1.csv"
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
    print(f"XAUUSD H1 disponible (limitado por maxbars=100000 del terminal, no por el broker): "
          f"{df['time'].min()} -> {df['time'].max()} ({anios_total:.1f} años, {len(df)} velas)")

    ret = df["close"].pct_change(1)
    std = ret.std()
    print(f"Std retorno H1 (serie completa): {std:.6f}\n")

    print(f"{'k':>6} | {'episodios':>9} | {'ep/año':>8} | {'dur. media (velas)':>18} | {'dur. max':>8}")
    for k in K_GRID:
        cond = (ret.abs() > k * std).fillna(False)
        n_ep, duraciones = contar_episodios(cond)
        ep_anio = n_ep / anios_total
        dur_prom = sum(duraciones) / len(duraciones) if duraciones else 0
        dur_max = max(duraciones) if duraciones else 0
        print(f"{k:>6.2f} | {n_ep:>9} | {ep_anio:>8.2f} | {dur_prom:>18.1f} | {dur_max:>8}")

    print("\nUsar el ep/año del k más restrictivo de la grilla como input conservador de "
          "triage_frecuencia.py (mismo criterio que los candidatos DXY previos).")


if __name__ == "__main__":
    main()
