"""
Fase 0 (rediseño panel Moskowitz-style) -- TF_Basket_H1. Paso empirico
previo al rediseño del power analysis: correlacion real entre los 10
instrumentos del basket (retornos D1, 2010-2026), para estimar cuantos
"bets" genuinamente independientes hay -- insumo necesario para pasar
de un test de portfolio ya combinado (invariante a N, ver
mde_trend_following_tf_basket_h1.py) a un panel instrumento x periodo
real.

N_efectivo (formula estandar de diversificacion, N instrumentos con
correlacion promedio rho_bar):
    N_eff = N / (1 + (N-1) * rho_bar)
"""
import sys
import time

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

sys.stdout.reconfigure(encoding="utf-8")

INICIO_VENTANA = pd.Timestamp("2010-01-01", tz="UTC")
BASKET = ["EURUSD", "USDJPY", "GBPUSD", "XAUUSD", "XAGUSD",
          "TLT", "LQD", "GDX", "XLE", "NVDA"]


def cargar_d1(simbolo):
    if not mt5.symbol_select(simbolo, True):
        return None
    rates = None
    for _ in range(5):
        rates = mt5.copy_rates_from_pos(simbolo, mt5.TIMEFRAME_D1, 0, 50000)
        if rates is not None and len(rates) > 0:
            break
        time.sleep(1.0)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df = df[df["time"] >= INICIO_VENTANA].reset_index(drop=True)
    return df[["time", "close"]] if len(df) > 0 else None


def main():
    ok = mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    if not ok:
        print(f"FALLO conectar: {mt5.last_error()}")
        return

    series = {}
    for s in BASKET:
        print(f"[diag] cargando {s}...", flush=True)
        df = cargar_d1(s)
        if df is None:
            print(f"[diag] {s}: sin datos", flush=True)
            continue
        close = df.set_index("time")["close"]
        series[s] = close.pct_change()

    mt5.shutdown()

    ret_df = pd.DataFrame(series).dropna(how="all")
    ret_df = ret_df.dropna()  # días donde los 10 instrumentos cotizan
    print(f"\nDías comunes a los 10 instrumentos: {len(ret_df)}")

    corr = ret_df.corr()
    print("\n=== Matriz de correlación (retornos D1, 2010-2026) ===\n")
    print(corr.round(2).to_string())

    n = len(BASKET)
    valores = corr.values
    off_diag = valores[~np.eye(n, dtype=bool)]
    rho_bar = off_diag.mean()
    print(f"\nCorrelación promedio (pares, off-diagonal): {rho_bar:.4f}")

    n_eff = n / (1 + (n - 1) * rho_bar)
    print(f"N efectivo (N={n}, rho_bar={rho_bar:.4f}): {n_eff:.2f}")

    # También calcular correlación promedio EXCLUYENDO NVDA (el único
    # instrumento sin relación macro/FX obvia con el resto), para ver
    # cuánto pesa como diversificador genuino vs. si el resto ya está
    # muy correlacionado entre sí
    resto = [s for s in BASKET if s != "NVDA" and s in corr.columns]
    corr_resto = corr.loc[resto, resto]
    off_resto = corr_resto.values[~np.eye(len(resto), dtype=bool)]
    print(f"\nCorrelación promedio excluyendo NVDA ({len(resto)} instrumentos): {off_resto.mean():.4f}")


if __name__ == "__main__":
    main()
