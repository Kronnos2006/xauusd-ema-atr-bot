"""
Backtest de implementación (Decisión Salida 2, 2026-08-06) -- Donchian 20
sobre el basket de TF_Basket_H1, con costos reales (spread + swap del
terminal) Y sizing por volatilidad (8%/posición, según la ficha original
de TF_Basket_H1). NO es un test de edge (esa pregunta ya la respondió
TF_Basket_H1 Fase 0: sin edge medible, t≈-0.04 gross) -- es el filtro de
implementación pre-registrado, condición 2 de la Bitácora de decisiones:

    ABORTA si Sharpe neto pooled 2010-2026 <= 0
    ABORTA si drag de swaps > 40% del retorno bruto

Metodología: retorno diario de la señal (direccion[t-1] * retorno[t],
mismo esquema sin look-ahead que calibracion_efecto_tf_basket_h1.py --
NO el esquema de "segmentos de trade" de la primera versión de este
script, que tenía un bug real: entraba al cierre del día de breakout
(el mismo día que genera la señal -- look-ahead) y además OMITÍA el día
de reversión, que es justamente el día que carga la pérdida de sostener
la dirección vieja contra el movimiento que la revierte. Ese bug
inflaba el resultado a un Sharpe +1.6 fantasma, contradiciendo el
Sharpe≈0 ya medido en el panel Moskowitz-style de TF_Basket_H1.

Sizing: cada posición escalada a vol objetivo 8% anualizado, usando la
vol diaria realizada de todo el período (escalar estático, no rolling
-- simplificación aceptable para un filtro de costos, no para el
forward test en sí). Retorno de portfolio = promedio simple de las 10
posiciones sizadas cada día (equal-weight, sin esquema de pesos propio
especificado en la ficha).

Costos: spread cargado una vez (round-trip) en cada día de flip,
escalado por el tamaño de posición. Swap acumulado cada día que se
sostiene una posición (miércoles a triple), escalado por el tamaño de
posición.
"""
import sys
import time
import math

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

sys.stdout.reconfigure(encoding="utf-8")

INICIO_VENTANA = pd.Timestamp("2010-01-01", tz="UTC")
BASKET = ["EURUSD", "USDJPY", "GBPUSD", "XAUUSD", "XAGUSD",
          "TLT", "LQD", "GDX", "XLE", "NVDA"]
DIAS_TRADING_ANIO = 252
VOL_OBJETIVO_POSICION = 0.08


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


def direccion_donchian20(close):
    hi = close.shift(1).rolling(20).max()
    lo = close.shift(1).rolling(20).min()
    direccion = pd.Series(np.nan, index=close.index)
    direccion[close > hi] = 1
    direccion[close < lo] = -1
    return direccion.ffill()


def main():
    ok = mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    if not ok:
        print(f"FALLO conectar: {mt5.last_error()}")
        return

    series_netas = {}
    series_brutas = {}
    resumen = []

    for s in BASKET:
        info = mt5.symbol_info(s)
        df = cargar_d1(s)
        if df is None or info is None:
            print(f"[diag] {s}: sin datos/info")
            continue

        close = df.set_index("time")["close"]
        ret = close.pct_change()
        direccion = direccion_donchian20(close)

        sigma_diaria = ret.std()
        sigma_anual = sigma_diaria * math.sqrt(DIAS_TRADING_ANIO)
        tamano_posicion = VOL_OBJETIVO_POSICION / sigma_anual

        dir_lag = direccion.shift(1)
        bruto = tamano_posicion * dir_lag * ret

        flip = (direccion != direccion.shift()).fillna(False)
        spread_pct_una_vez = info.spread * info.point / close  # spread como % del precio, por día (solo cobra en flip)
        costo_spread = tamano_posicion * spread_pct_una_vez * flip

        es_miercoles = close.index.dayofweek == 2
        mult_swap = np.where(es_miercoles, 3, 1)
        swap_puntos = np.where(dir_lag == 1, info.swap_long, np.where(dir_lag == -1, info.swap_short, 0.0))
        costo_swap_precio = swap_puntos * info.point * mult_swap
        costo_swap_pct = tamano_posicion * (costo_swap_precio / close) * dir_lag.notna()

        neto = bruto - costo_spread - costo_swap_pct

        series_brutas[s] = bruto.dropna()
        series_netas[s] = neto.dropna()

        resumen.append({
            "instrumento": s,
            "tamano_posicion": tamano_posicion,
            "sigma_anual_pct": sigma_anual,
            "bruto_total": bruto.sum(),
            "spread_total": costo_spread.sum(),
            "swap_total": costo_swap_pct.sum(),
            "neto_total": neto.sum(),
        })

    mt5.shutdown()

    print(f"{'Instr':<8} {'tam.pos':>9} {'sigma_anual':>12} {'bruto':>10} {'spread':>9} {'swap':>9} {'neto':>10}")
    for r in resumen:
        print(f"{r['instrumento']:<8} {r['tamano_posicion']:>9.3f} {r['sigma_anual_pct']:>11.2%} "
              f"{r['bruto_total']:>10.2%} {r['spread_total']:>9.2%} {r['swap_total']:>9.2%} {r['neto_total']:>10.2%}")

    df_bruto = pd.DataFrame(series_brutas)
    df_neto = pd.DataFrame(series_netas)

    portfolio_bruto = df_bruto.mean(axis=1, skipna=True)
    portfolio_neto = df_neto.mean(axis=1, skipna=True)

    media_neto = portfolio_neto.mean()
    std_neto = portfolio_neto.std()
    sharpe_neto_anual = (media_neto / std_neto) * math.sqrt(DIAS_TRADING_ANIO)

    gross_total = sum(r["bruto_total"] for r in resumen)
    swap_total = sum(r["swap_total"] for r in resumen)
    spread_total = sum(r["spread_total"] for r in resumen)
    neto_total = sum(r["neto_total"] for r in resumen)

    drag_swap = abs(swap_total) / abs(gross_total) if gross_total != 0 else float("inf")

    print(f"\n=== Portfolio pooled (equal-weight, 10 posiciones sizadas a {VOL_OBJETIVO_POSICION:.0%} vol c/u) ===")
    print(f"Retorno bruto total (suma de retornos diarios sizados, sin costos): {gross_total:+.2%}")
    print(f"Costo total spread: {spread_total:.2%}")
    print(f"Costo total swap: {swap_total:+.2%}")
    print(f"Retorno neto total: {neto_total:+.2%}")
    print(f"Sharpe neto anualizado (serie diaria de portfolio, {len(portfolio_neto)} días): {sharpe_neto_anual:+.4f}")
    print(f"Drag de swaps / retorno bruto: {drag_swap:.1%}")

    print("\n=== VEREDICTO (condición 2, Decisión Salida 2) ===")
    aborta_sharpe = sharpe_neto_anual <= 0
    aborta_swap = drag_swap > 0.40
    print(f"Sharpe neto pooled <= 0: {'SI -> ABORTA' if aborta_sharpe else 'NO'} (Sharpe={sharpe_neto_anual:+.4f})")
    print(f"Drag swaps > 40% del retorno bruto: {'SI -> ABORTA' if aborta_swap else 'NO'} (drag={drag_swap:.1%})")
    if aborta_sharpe or aborta_swap:
        print("\n>>> ABORTA -- no se avanza a forward test, por condición(es) pre-registrada(s) arriba. <<<")
    else:
        print("\n>>> PASA el filtro de implementación -- procede a forward test operativo. <<<")


if __name__ == "__main__":
    main()
