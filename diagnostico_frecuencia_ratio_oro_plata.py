"""
Chequeo de frecuencia -- hipotesis ratio oro/plata (XAUUSD/XAGUSD), fase 1.
=============================================================================
Antes de tocar walk-forward: cuenta cuantos episodios de "z-score extremo"
genera la regla candidata sobre el historial real (MT5, D1) del ratio
XAUUSD/XAGUSD, para la grilla declarada de Y (ventana de la media movil,
dias habiles) y X (umbral en desvios estandar). Mismo chequeo de sanidad que
se hizo para DFII10/2s10s antes de bajar mas datos o escribir el
walk-forward completo.

Frase falsable (fijada antes de correr esto, sin variantes fuera de la
grilla declarada mas abajo): cuando el ratio XAUUSD/XAGUSD se aleja mas de
X desvios estandar de su propia media movil de Y dias, el oro tiene sesgo
direccional OPUESTO al signo del z-score en las siguientes Z sesiones
(z>>0 -> oro caro relativo a la plata -> sesgo bajista; z<<0 -> sesgo
alcista). Z (horizonte de reversion) no afecta este chequeo de frecuencia
-- solo importa para el walk-forward posterior.

Definicion operacional de "episodio" (unica forma declarada):
- z[t] = (ratio[t] - media_movil_Y[t]) / std_movil_Y[t], ventana rolling
  con min_periods=Y (sin fuga: el z de hoy solo usa datos hasta hoy).
- Episodio: racha maxima de dias consecutivos con |z[t]| > X. Se cuenta
  como 1 observacion independiente por racha, no 1 por dia con condicion
  activa (mismo criterio que DFII10/2s10s).

Fuente: MT5 real (mismo terminal del proyecto), D1, XAUUSD y XAGUSD.
"""
import importlib.util
import sys

import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # no corre main() porque __name__ != "__main__"

GRID_Y = [20, 60, 120]
GRID_X = [1.5, 2.0]


def bajar_ratio_diario():
    """D1 directo de MT5 para XAUUSD y XAGUSD, alineado por fecha (inner join
    -- XAGUSD arranca despues que XAUUSD en este broker, ver mas abajo)."""
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()
    inicio = pd.Timestamp("2004-01-01")  # rango amplio; el inner join recorta al solapamiento real

    oro = mod.bajar_datos_rango(mod.SYMBOL, mod.mt5.TIMEFRAME_D1, inicio, ahora)
    plata = mod.bajar_datos_rango("XAGUSD", mod.mt5.TIMEFRAME_D1, inicio, ahora)

    oro = oro[["time", "close"]].rename(columns={"close": "oro"})
    plata = plata[["time", "close"]].rename(columns={"close": "plata"})
    oro["time"] = oro["time"].dt.normalize()
    plata["time"] = plata["time"].dt.normalize()

    df = oro.merge(plata, on="time", how="inner").sort_values("time").reset_index(drop=True)
    df["ratio"] = df["oro"] / df["plata"]
    return df


def contar_episodios(serie_bool):
    """Cuenta rachas maximas de True consecutivos en una serie booleana."""
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones


def main():
    df = bajar_ratio_diario()
    print(f"Dias con ratio valido (XAUUSD y XAGUSD solapados): {len(df)}")
    print(f"Rango: {df['time'].min().date()} -> {df['time'].max().date()}")
    anios_total = (df["time"].max() - df["time"].min()).days / 365.25
    print(f"Total anios cubiertos: {anios_total:.1f}\n")

    for y in GRID_Y:
        media = df["ratio"].rolling(y, min_periods=y).mean()
        std = df["ratio"].rolling(y, min_periods=y).std()
        z = (df["ratio"] - media) / std

        print(f"=== Y={y} dias (ventana de la media movil) ===")
        for x in GRID_X:
            extremo_alto = (z > x).fillna(False)
            extremo_bajo = (z < -x).fillna(False)
            extremo_cualquiera = extremo_alto | extremo_bajo

            n_alto, dur_alto = contar_episodios(extremo_alto)
            n_bajo, dur_bajo = contar_episodios(extremo_bajo)
            n_total, dur_total = contar_episodios(extremo_cualquiera)

            anios_validos = z.notna().sum() / 252
            dur_prom = sum(dur_total) / len(dur_total) if dur_total else 0
            dur_max = max(dur_total) if dur_total else 0

            print(f"  X={x} desvios estandar:")
            print(f"    Episodios z>+X (oro caro, sesgo bajista): {n_alto} | "
                  f"z<-X (oro barato, sesgo alcista): {n_bajo} | total: {n_total}")
            print(f"    Episodios/año (total): {n_total / anios_validos:.2f} | "
                  f"Duracion media: {dur_prom:.1f}d | max: {dur_max}d")
        print()


if __name__ == "__main__":
    main()
