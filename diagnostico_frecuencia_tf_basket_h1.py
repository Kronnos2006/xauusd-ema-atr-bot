"""
Triage de frecuencia (Fase 0, hypothesis-gate) -- TF_Basket_H1, trend
following Donchian/MA sobre basket diversificado de 10 instrumentos.

Frase falsable (ver "TF_Basket_H1 -- Fase 0.md" en el vault): sistema
trend following (Donchian 20/55/100 + MA cruce 50/200, 20/100, 10/50)
aplicado al basket, evaluado en el periodo 2010-2026.

Este script SOLO cuenta episodios (flips de tendencia) por combinacion
señal x instrumento -- no simula un solo trade todavia. Ventana
restringida a 2010-01-01 en adelante (el periodo real de la hipotesis,
no todo el historico disponible via MT5), mismo patron que
diagnostico_frecuencia_momentum_dxy_h4.py restringiendo a la ventana de
oro en MT5.

Logica de señal:
- Donchian N: breakout de maximo/minimo de N dias (shift 1, sin
  look-ahead). Direccion se mantiene hasta el breakout opuesto.
  Episodio = cada flip de direccion (cada flip = una entrada nueva).
- MA cruce F/S: direccion = signo(MA_F - MA_S). Episodio = cada cruce.
"""
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

sys.stdout.reconfigure(encoding="utf-8")

INICIO_VENTANA = pd.Timestamp("2010-01-01", tz="UTC")

BASKET = ["EURUSD", "USDJPY", "GBPUSD", "XAUUSD", "XAGUSD",
          "TLT", "LQD", "GDX", "XLE", "NVDA"]

DONCHIAN_N = [20, 55, 100]
MA_CRUCE = [(50, 200), (20, 100), (10, 50)]

# Referencia de efecto tipico -- unica hipotesis del proyecto con media_R
# y std_R completos (DFII10, macro diario). No es un diseño equivalente
# a trend following (evento direccional vs. sistema de flips continuos),
# pero es el unico precedente calibrado con datos reales de este mercado
# que tiene el proyecto -- se usa a falta de uno mejor, señalado
# explicitamente como limitacion del triage, no como equivalencia de diseño.
MEDIA_R_REF = 0.230
STD_R_REF = 1.135
HORIZONTE_LIMITE_ANIOS = 5


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


def contar_flips_donchian(close, n):
    hi = close.shift(1).rolling(n).max()
    lo = close.shift(1).rolling(n).min()
    direccion = pd.Series(np.nan, index=close.index)
    direccion[close > hi] = 1
    direccion[close < lo] = -1
    direccion = direccion.ffill()
    valida = direccion.notna()
    if valida.sum() == 0:
        return 0, None
    dir_valida = direccion[valida]
    flips = int((dir_valida.diff().fillna(0) != 0).sum())
    primer_idx = dir_valida.index[0]
    return flips, primer_idx


def contar_flips_ma(close, fast, slow):
    ma_f = close.rolling(fast).mean()
    ma_s = close.rolling(slow).mean()
    direccion = np.sign(ma_f - ma_s)
    valida = direccion.notna()
    if valida.sum() == 0:
        return 0, None
    dir_valida = direccion[valida]
    flips = int((dir_valida.diff().fillna(0) != 0).sum())
    primer_idx = dir_valida.index[0]
    return flips, primer_idx


def n_necesario_80_poder(media_r, std_r, alpha=0.05, poder_objetivo=0.80):
    z_alpha = 1.959963985
    z_beta = 0.841621234
    import math
    return math.ceil(((z_alpha + z_beta) * std_r / media_r) ** 2)


def main():
    ok = mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    if not ok:
        print(f"FALLO conectar: {mt5.last_error()}")
        return

    datos = {}
    for s in BASKET:
        print(f"[diag] cargando {s}...", flush=True)
        df = cargar_d1(s)
        if df is None:
            print(f"[diag] {s}: sin datos D1 en la ventana >= 2010-01-01", flush=True)
        else:
            print(f"[diag] {s}: {len(df)} barras cargadas", flush=True)
        datos[s] = df

    mt5.shutdown()
    print("[diag] mt5.shutdown() completo, arrancando cálculo de flips", flush=True)

    columnas = [f"Donchian{n}" for n in DONCHIAN_N] + [f"MA{f}/{s}" for f, s in MA_CRUCE]
    tabla_epanio = pd.DataFrame(index=BASKET, columns=columnas, dtype=float)
    tabla_flips = pd.DataFrame(index=BASKET, columns=columnas, dtype="Int64")

    for s in BASKET:
        print(f"[diag] flips {s}...", flush=True)
        df = datos[s]
        if df is None:
            continue
        close = df.set_index("time")["close"]
        fin = close.index.max()

        for n in DONCHIAN_N:
            flips, primer_idx = contar_flips_donchian(close, n)
            col = f"Donchian{n}"
            if primer_idx is None:
                tabla_flips.loc[s, col] = 0
                tabla_epanio.loc[s, col] = 0.0
                continue
            anios = (fin - primer_idx).days / 365.25
            tabla_flips.loc[s, col] = flips
            tabla_epanio.loc[s, col] = flips / anios if anios > 0 else 0.0

        for f, sl in MA_CRUCE:
            flips, primer_idx = contar_flips_ma(close, f, sl)
            col = f"MA{f}/{sl}"
            if primer_idx is None:
                tabla_flips.loc[s, col] = 0
                tabla_epanio.loc[s, col] = 0.0
                continue
            anios = (fin - primer_idx).days / 365.25
            tabla_flips.loc[s, col] = flips
            tabla_epanio.loc[s, col] = flips / anios if anios > 0 else 0.0

    print("=== Flips totales por combinación (ventana 2010-01-01 -> hoy) ===\n")
    print(tabla_flips.to_string())
    print("\n=== Episodios/año por combinación ===\n")
    print(tabla_epanio.round(2).to_string())

    print("\n=== Total basket (suma de flips de las 10 instrumentos) por señal ===\n")
    total_flips = tabla_flips.sum(axis=0)
    # años efectivos del basket: usar el promedio de años disponibles por
    # instrumento y señal, ponderado por flips (aproximación razonable
    # para un triage -- no se está simulando el sistema todavía)
    resumen = []
    for col in columnas:
        flips_totales = int(total_flips[col])
        anios_por_instrumento = []
        for s in BASKET:
            df = datos[s]
            if df is None:
                continue
            close = df.set_index("time")["close"]
            fin = close.index.max()
            if col.startswith("Donchian"):
                n = int(col.replace("Donchian", ""))
                _, primer_idx = contar_flips_donchian(close, n)
            else:
                f, sl = col.replace("MA", "").split("/")
                _, primer_idx = contar_flips_ma(close, int(f), int(sl))
            if primer_idx is not None:
                anios_por_instrumento.append((fin - primer_idx).days / 365.25)
        anios_prom = sum(anios_por_instrumento) / len(anios_por_instrumento) if anios_por_instrumento else 0
        ep_anio_basket = flips_totales / anios_prom if anios_prom > 0 else 0
        resumen.append((col, flips_totales, anios_prom, ep_anio_basket))

    print(f"{'Señal':<12} {'Flips totales':>14} {'Años prom.':>11} {'Ep/año basket':>14}")
    for col, ft, ap, epb in resumen:
        print(f"{col:<12} {ft:>14} {ap:>11.1f} {epb:>14.2f}")

    print(f"\n=== Power analysis (efecto de referencia: DFII10, media_R={MEDIA_R_REF}, std_R={STD_R_REF}) ===")
    n_necesario = n_necesario_80_poder(MEDIA_R_REF, STD_R_REF)
    print(f"n necesario para 80% de poder (alpha=0.05, dos colas): {n_necesario}\n")

    print(f"{'Señal':<12} {'Ep/año basket':>14} {'Horizonte proyectado (años)':>28} {'Veredicto':>20}")
    resultado_final = {}
    for col, ft, ap, epb in resumen:
        if epb <= 0:
            horizonte = float("inf")
        else:
            horizonte = n_necesario / epb
        veredicto = "DESCARTA" if horizonte > HORIZONTE_LIMITE_ANIOS else "PASA"
        resultado_final[col] = (horizonte, veredicto)
        print(f"{col:<12} {epb:>14.2f} {horizonte:>28.1f} {veredicto:>20}")


if __name__ == "__main__":
    main()
