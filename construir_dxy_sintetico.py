"""
DXY sintetico -- construccion desde 6 pares FX, formula real de ICE.
=============================================================================
Este broker MT5 no tiene el indice dolar real bajo ningun simbolo (ver
'Macro DXY - fase 1.md' en el vault). Se construye un proxy desde los 6
pares que componen la formula oficial del ICE US Dollar Index, todos
confirmados disponibles en este broker: EURUSD, USDJPY, GBPUSD, USDCAD,
USDSEK, USDCHF.

Formula (constante publicada, no una aproximacion propia):
  USDX = 50.14348112 * EURUSD^(-0.576) * USDJPY^(+0.136) * GBPUSD^(-0.119)
                      * USDCAD^(+0.091) * USDSEK^(+0.042) * USDCHF^(+0.036)

Nota sobre los signos (importante, no es solo "pesos" en valor absoluto):
EURUSD y GBPUSD se cotizan como "dolares por 1 unidad de la otra moneda"
-- cuando el dolar se fortalece, EURUSD y GBPUSD BAJAN, así que llevan
exponente NEGATIVO para que el termino (y USDX) suba junto con el dolar.
USDJPY/USDCAD/USDSEK/USDCHF se cotizan al reves ("unidades de la otra
moneda por 1 dolar") -- cuando el dolar se fortalece, esos pares SUBEN,
así que llevan exponente POSITIVO. El usuario describio los pesos como
porcentajes sin signo (57.6/13.6/11.9/9.1/4.2/3.6); esos valores absolutos
coinciden con los exponentes reales, pero el signo de EUR/GBP tuvo que
completarse con la formula estandar publicada (ICE), no inventado.

Este script SOLO construye la serie y la deja lista para el paso de
validacion (comparar contra valores reales publicados de DXY en fechas
conocidas) -- no corre chequeo de frecuencia ni walk-forward todavia.
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


def bajar_pares_fx(fecha_inicio=pd.Timestamp("2000-01-01")):
    """Baja D1 de los 6 pares y los alinea por fecha (inner join -- el par
    con historial mas corto define el rango usable de la serie completa)."""
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()

    df = None
    for par in PARES:
        datos = mod.bajar_datos_rango(par, mod.mt5.TIMEFRAME_D1, fecha_inicio, ahora)
        datos = datos[["time", "close"]].rename(columns={"close": par})
        datos["time"] = datos["time"].dt.normalize()
        df = datos if df is None else df.merge(datos, on="time", how="inner")

    return df.sort_values("time").reset_index(drop=True)


def calcular_dxy_sintetico(df):
    """df debe tener una columna por par en PARES. Devuelve el df con una
    columna nueva 'dxy_sintetico'."""
    resultado = pd.Series(FACTOR, index=df.index)
    for par in PARES:
        resultado = resultado * (df[par] ** EXPONENTES[par])
    df = df.copy()
    df["dxy_sintetico"] = resultado
    return df


def main():
    df = bajar_pares_fx()
    print(f"Dias con los 6 pares solapados: {len(df)}")
    print(f"Rango: {df['time'].min().date()} -> {df['time'].max().date()}\n")

    df = calcular_dxy_sintetico(df)
    print(df[["time", "dxy_sintetico"]].tail(10).to_string(index=False))

    df.to_csv(r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico.csv", index=False)
    print("\nGuardado en historial/dxy_sintetico.csv (ignorado por git, igual que el resto de historial/).")


if __name__ == "__main__":
    main()
