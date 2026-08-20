"""
DXY sintetico H4 -- misma formula que construir_dxy_sintetico.py (D1), timeframe
H4. Ver ese script para la justificacion de la formula/exponentes (constante
ICE, no una aproximacion propia); acá solo cambia el timeframe de descarga.

Generado para el triage de frecuencia de la hipotesis "Momentum DXY sintetico
H4 -> XAUUSD" (candidato 2026-08-04, ver Bitácora de decisiones.md).
"""
import importlib.util
import sys

import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)

PARES = ["EURUSD", "USDJPY", "GBPUSD", "USDCAD", "USDSEK", "USDCHF"]
EXPONENTES = {
    "EURUSD": -0.576,
    "USDJPY": +0.136,
    "GBPUSD": -0.119,
    "USDCAD": +0.091,
    "USDSEK": +0.042,
    "USDCHF": +0.036,
}
FACTOR = 50.14348112


def bajar_pares_fx_h4(fecha_inicio=pd.Timestamp("2000-01-01")):
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()

    df = None
    rangos = {}
    for par in PARES:
        datos = mod.bajar_datos_rango(par, mod.mt5.TIMEFRAME_H4, fecha_inicio, ahora)
        rangos[par] = (datos["time"].min(), datos["time"].max(), len(datos))
        datos = datos[["time", "close"]].rename(columns={"close": par})
        df = datos if df is None else df.merge(datos, on="time", how="inner")

    print("Rango H4 disponible por par (antes del merge):")
    for par, (ini, fin, n) in rangos.items():
        print(f"  {par}: {ini} -> {fin} ({n} velas)")

    return df.sort_values("time").reset_index(drop=True)


def calcular_dxy_sintetico(df):
    resultado = pd.Series(FACTOR, index=df.index)
    for par in PARES:
        resultado = resultado * (df[par] ** EXPONENTES[par])
    df = df.copy()
    df["dxy_sintetico"] = resultado
    return df


def main():
    df = bajar_pares_fx_h4()
    print(f"\nVelas H4 con los 6 pares solapados: {len(df)}")
    print(f"Rango solapado: {df['time'].min()} -> {df['time'].max()}\n")

    df = calcular_dxy_sintetico(df)
    print(df[["time", "dxy_sintetico"]].tail(10).to_string(index=False))

    ruta = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico_h4.csv"
    df.to_csv(ruta, index=False)
    print(f"\nGuardado en {ruta} (ignorado por git, igual que el resto de historial/).")


if __name__ == "__main__":
    main()
