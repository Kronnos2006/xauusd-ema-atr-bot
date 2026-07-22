"""
Backtest EMA Cross + ATR para XAUUSD en MetaTrader 5
=====================================================

PASO 1 del bot nuevo: validar la estrategia con datos reales antes de
escribir una sola línea de MQL5.

Estrategia:
- EMA rápida (9) cruza EMA lenta (21) -> señal de entrada
- Filtro de tendencia: precio debe estar del lado correcto de la EMA 50
- Stop Loss: basado en ATR (volatilidad), no un número fijo en pips
- Take Profit: múltiplo del SL (Risk:Reward configurable)

REQUISITOS (correr en tu PC Windows con MT5 abierto):
    pip install MetaTrader5 pandas numpy

USO:
    python backtest_ema_xauusd.py
"""

import sys
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# CONFIGURACIÓN - andá ajustando estos valores
# ============================================================
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M15     # M15 para empezar; después probamos M5, H1
N_VELAS = 15000                    # cuántas velas históricas bajar (subido para más robustez)

USE_SESSION_FILTER = False      # solo operar en horario de mayor liquidez (Londres/NY)
SESSION_START_HOUR = 8            # hora GMT de inicio (ajustar según tu servidor MT5)
SESSION_END_HOUR = 20             # hora GMT de fin

EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50

ATR_PERIOD = 14
SL_ATR_MULT = 1.5                 # Stop Loss = 1.5x ATR
RR_RATIO = 2.0                    # Take Profit = 2x el riesgo (1:2)

SPREAD_PUNTOS = 30                # spread aproximado en puntos (ajustar a tu broker)


def conectar_mt5():
    ruta_terminal = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(path=ruta_terminal):
        print("ERROR: no se pudo conectar a MT5:", mt5.last_error())
        quit()
    print("Conectado a MT5:", mt5.terminal_info())


def bajar_datos(symbol, timeframe, n_velas):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_velas)
    if rates is None or len(rates) == 0:
        print(f"ERROR: no se pudieron bajar datos de {symbol}. ¿Está el símbolo visible en Market Watch?")
        quit()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def calcular_indicadores(df):
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_trend"] = df["close"].ewm(span=EMA_TREND, adjust=False).mean()

    # ATR
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_PERIOD).mean()

    return df


def generar_senales(df):
    df["cruce_alcista"] = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1))
    df["cruce_bajista"] = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1))

    df["senal_compra"] = df["cruce_alcista"] & (df["close"] > df["ema_trend"])
    df["senal_venta"] = df["cruce_bajista"] & (df["close"] < df["ema_trend"])

    if USE_SESSION_FILTER:
        hora = df["time"].dt.hour
        en_sesion = (hora >= SESSION_START_HOUR) & (hora < SESSION_END_HOUR)
        df["senal_compra"] = df["senal_compra"] & en_sesion
        df["senal_venta"] = df["senal_venta"] & en_sesion

    return df


def backtest(df, point_value=0.01):
    """
    Simula operaciones una a la vez (no pyramiding).
    Devuelve lista de trades con resultado en R (múltiplos de riesgo).
    """
    trades = []
    posicion_abierta = None  # dict con datos de la posición

    for i in range(len(df)):
        row = df.iloc[i]

        # --- gestionar posición abierta ---
        if posicion_abierta is not None:
            tipo = posicion_abierta["tipo"]
            sl = posicion_abierta["sl"]
            tp = posicion_abierta["tp"]

            if tipo == "compra":
                if row["low"] <= sl:
                    trades.append({**posicion_abierta, "resultado_R": -1.0, "salida": "SL", "time_salida": row["time"]})
                    posicion_abierta = None
                elif row["high"] >= tp:
                    trades.append({**posicion_abierta, "resultado_R": RR_RATIO, "salida": "TP", "time_salida": row["time"]})
                    posicion_abierta = None
            elif tipo == "venta":
                if row["high"] >= sl:
                    trades.append({**posicion_abierta, "resultado_R": -1.0, "salida": "SL", "time_salida": row["time"]})
                    posicion_abierta = None
                elif row["low"] <= tp:
                    trades.append({**posicion_abierta, "resultado_R": RR_RATIO, "salida": "TP", "time_salida": row["time"]})
                    posicion_abierta = None

        # --- abrir nueva posición si no hay una abierta ---
        if posicion_abierta is None and not pd.isna(row["atr"]):
            riesgo = row["atr"] * SL_ATR_MULT

            if row["senal_compra"]:
                entrada = row["close"]
                sl = entrada - riesgo
                tp = entrada + riesgo * RR_RATIO
                posicion_abierta = {
                    "tipo": "compra", "entrada": entrada, "sl": sl, "tp": tp,
                    "time_entrada": row["time"]
                }
            elif row["senal_venta"]:
                entrada = row["close"]
                sl = entrada + riesgo
                tp = entrada - riesgo * RR_RATIO
                posicion_abierta = {
                    "tipo": "venta", "entrada": entrada, "sl": sl, "tp": tp,
                    "time_entrada": row["time"]
                }

    return pd.DataFrame(trades)


def mostrar_resultados(trades_df):
    if trades_df.empty:
        print("No se generaron operaciones con esta configuración.")
        return

    n_trades = len(trades_df)
    ganadoras = (trades_df["resultado_R"] > 0).sum()
    perdedoras = (trades_df["resultado_R"] < 0).sum()
    win_rate = ganadoras / n_trades * 100
    r_total = trades_df["resultado_R"].sum()
    r_promedio = trades_df["resultado_R"].mean()

    # drawdown en términos de R acumulado
    equity_curve = trades_df["resultado_R"].cumsum()
    running_max = equity_curve.cummax()
    drawdown = equity_curve - running_max
    max_drawdown_R = drawdown.min()

    print("\n" + "=" * 50)
    print(f"RESULTADOS BACKTEST — {SYMBOL} — EMA {EMA_FAST}/{EMA_SLOW}/{EMA_TREND}")
    print("=" * 50)
    print(f"Total operaciones:     {n_trades}")
    print(f"Ganadoras:             {ganadoras}")
    print(f"Perdedoras:            {perdedoras}")
    print(f"Win rate:              {win_rate:.1f}%")
    print(f"R:R configurado:       1:{RR_RATIO}")
    print(f"R total acumulado:     {r_total:.2f}R")
    print(f"R promedio por trade:  {r_promedio:.3f}R")
    print(f"Máximo drawdown:       {max_drawdown_R:.2f}R")
    print("=" * 50)

    # Punto de equilibrio (win rate mínimo necesario para no perder, dado el R:R)
    breakeven_wr = 1 / (1 + RR_RATIO) * 100
    print(f"\nWin rate de equilibrio con R:R 1:{RR_RATIO} -> {breakeven_wr:.1f}%")
    if win_rate > breakeven_wr:
        print(f"✅ Tu win rate ({win_rate:.1f}%) está POR ENCIMA del equilibrio ({breakeven_wr:.1f}%) -> estrategia rentable en este período")
    else:
        print(f"❌ Tu win rate ({win_rate:.1f}%) está POR DEBAJO del equilibrio ({breakeven_wr:.1f}%) -> no rentable en este período")


def backtest_con_rr(df, rr_ratio):
    """Igual que backtest() pero permite variar el R:R sin tocar la entrada."""
    global RR_RATIO
    original = RR_RATIO
    RR_RATIO = rr_ratio
    trades_df = backtest(df)
    RR_RATIO = original
    return trades_df


def diagnostico_entrada_vs_salida(df):
    """
    Corre la MISMA señal de entrada con distintos R:R.
    Si el win rate se mantiene parecido en todos los R:R pero ninguno
    supera el punto de equilibrio -> el problema es la ENTRADA (la señal
    no predice dirección con fiabilidad suficiente).
    Si algún R:R sí supera el equilibrio -> el problema es la SALIDA
    (la entrada tiene algo de edge, pero el R:R/gestión actual lo desperdicia).
    """
    print("\n" + "#" * 60)
    print("DIAGNÓSTICO: ¿el problema es la ENTRADA o la SALIDA?")
    print("#" * 60)

    resultados = []
    for rr in [1.0, 1.5, 2.0, 2.5, 3.0]:
        trades_df = backtest_con_rr(df, rr)
        if trades_df.empty:
            continue
        n = len(trades_df)
        wr = (trades_df["resultado_R"] > 0).sum() / n * 100
        r_total = trades_df["resultado_R"].sum()
        breakeven = 1 / (1 + rr) * 100
        edge = wr - breakeven
        resultados.append((rr, n, wr, breakeven, r_total, edge))
        estado = "✅ RENTABLE" if edge > 0 else "❌ pierde"
        print(f"R:R 1:{rr:<4} | Trades: {n:<4} | Win rate: {wr:5.1f}% | Equilibrio: {breakeven:5.1f}% | Edge: {edge:+5.1f}pp | R total: {r_total:+7.2f}R  {estado}")

    print("#" * 60)
    mejores = [r for r in resultados if r[5] > 0]
    if mejores:
        print(f"\n✅ Hay edge real en la entrada: {len(mejores)} de {len(resultados)} configuraciones de R:R son rentables.")
        print("   -> El problema NO es la señal de entrada en sí, es cómo gestionás la salida.")
        print("   -> Conviene enfocar el trabajo en break-even, trailing stop, o partial close.")
    else:
        print("\n❌ Ninguna configuración de R:R fue rentable con esta entrada.")
        print("   -> El problema está en la ENTRADA: la señal EMA+filtro no predice dirección de forma fiable.")
        print("   -> Conviene mejorar el filtro de entrada antes de optimizar la salida.")


PARTIAL_TP_R = 1.5      # R al que se cierra el 50% de la posición
TRAIL_ATR_MULT = 1.5    # distancia del trailing stop en múltiplos de ATR


def backtest_partial_trailing(df):
    """
    Gestión de salida combinada:
    1. Se abre la posición completa (100%) con SL basado en ATR.
    2. Al llegar a PARTIAL_TP_R -> se cierra el 50% (ganancia asegurada)
       y el SL del 50% restante se mueve a break-even (precio de entrada).
    3. El 50% restante se gestiona con trailing stop basado en ATR:
       el SL sigue al precio a una distancia de TRAIL_ATR_MULT * ATR.
    4. Resultado final del trade = promedio ponderado 50%/50% en R.
    """
    trades = []
    pos = None

    for i in range(len(df)):
        row = df.iloc[i]

        if pos is not None:
            tipo = pos["tipo"]
            riesgo = pos["riesgo"]

            if tipo == "compra":
                pos["max_precio"] = max(pos["max_precio"], row["high"])

                # --- parte 1: aún no se tomó la ganancia parcial ---
                if not pos["parcial_tomado"]:
                    nivel_parcial = pos["entrada"] + riesgo * PARTIAL_TP_R
                    if row["low"] <= pos["sl"]:
                        # SL golpeado antes de llegar al parcial -> pérdida completa
                        trades.append({**pos, "resultado_R": -1.0, "salida": "SL_total"})
                        pos = None
                        continue
                    if row["high"] >= nivel_parcial:
                        pos["parcial_tomado"] = True
                        pos["r_parcial"] = PARTIAL_TP_R
                        pos["sl"] = pos["entrada"]  # break-even para el resto

                # --- parte 2: ya se tomó la ganancia parcial, trailing en el resto ---
                if pos is not None and pos["parcial_tomado"]:
                    nuevo_sl = pos["max_precio"] - row["atr"] * TRAIL_ATR_MULT
                    if nuevo_sl > pos["sl"]:
                        pos["sl"] = nuevo_sl  # el SL solo sube, nunca baja

                    if row["low"] <= pos["sl"]:
                        r_resto = (pos["sl"] - pos["entrada"]) / riesgo
                        r_final = 0.5 * pos["r_parcial"] + 0.5 * r_resto
                        trades.append({**pos, "resultado_R": r_final, "salida": "trailing"})
                        pos = None

            elif tipo == "venta":
                pos["min_precio"] = min(pos["min_precio"], row["low"])

                if not pos["parcial_tomado"]:
                    nivel_parcial = pos["entrada"] - riesgo * PARTIAL_TP_R
                    if row["high"] >= pos["sl"]:
                        trades.append({**pos, "resultado_R": -1.0, "salida": "SL_total"})
                        pos = None
                        continue
                    if row["low"] <= nivel_parcial:
                        pos["parcial_tomado"] = True
                        pos["r_parcial"] = PARTIAL_TP_R
                        pos["sl"] = pos["entrada"]

                if pos is not None and pos["parcial_tomado"]:
                    nuevo_sl = pos["min_precio"] + row["atr"] * TRAIL_ATR_MULT
                    if nuevo_sl < pos["sl"]:
                        pos["sl"] = nuevo_sl

                    if row["high"] >= pos["sl"]:
                        r_resto = (pos["entrada"] - pos["sl"]) / riesgo
                        r_final = 0.5 * pos["r_parcial"] + 0.5 * r_resto
                        trades.append({**pos, "resultado_R": r_final, "salida": "trailing"})
                        pos = None

        if pos is None and not pd.isna(row["atr"]):
            riesgo = row["atr"] * SL_ATR_MULT

            if row["senal_compra"]:
                entrada = row["close"]
                pos = {
                    "tipo": "compra", "entrada": entrada, "sl": entrada - riesgo,
                    "riesgo": riesgo, "max_precio": entrada,
                    "parcial_tomado": False, "r_parcial": 0.0,
                    "time_entrada": row["time"]
                }
            elif row["senal_venta"]:
                entrada = row["close"]
                pos = {
                    "tipo": "venta", "entrada": entrada, "sl": entrada + riesgo,
                    "riesgo": riesgo, "min_precio": entrada,
                    "parcial_tomado": False, "r_parcial": 0.0,
                    "time_entrada": row["time"]
                }

    return pd.DataFrame(trades)


def comparar_salida_fija_vs_combinada(df):
    print("\n" + "#" * 60)
    print("COMPARACIÓN: TP fijo (1:2) vs Partial Close + Trailing")
    print("#" * 60)

    fija = backtest_con_rr(df, 2.0)
    combinada = backtest_partial_trailing(df)

    for nombre, td in [("TP fijo 1:2", fija), ("Partial+Trailing", combinada)]:
        if td.empty:
            print(f"{nombre}: sin operaciones")
            continue
        n = len(td)
        wr = (td["resultado_R"] > 0).sum() / n * 100
        r_total = td["resultado_R"].sum()
        r_prom = td["resultado_R"].mean()
        print(f"{nombre:<20} | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R | R promedio: {r_prom:+.3f}R")

    print("#" * 60)
    if not combinada.empty and not fija.empty:
        if combinada["resultado_R"].sum() > fija["resultado_R"].sum():
            print("\n✅ La gestión combinada (partial + trailing) mejora el resultado vs TP fijo.")
        else:
            print("\n❌ El TP fijo sigue siendo mejor que partial+trailing en este período/config.")


def backtest_trailing_con_mult(df, trail_mult, partial_r):
    """Igual que backtest_partial_trailing pero permite variar los parámetros sin tocar globals de forma permanente."""
    global TRAIL_ATR_MULT, PARTIAL_TP_R
    orig_trail, orig_partial = TRAIL_ATR_MULT, PARTIAL_TP_R
    TRAIL_ATR_MULT = trail_mult
    PARTIAL_TP_R = partial_r
    trades_df = backtest_partial_trailing(df)
    TRAIL_ATR_MULT, PARTIAL_TP_R = orig_trail, orig_partial
    return trades_df


def optimizar_trailing(df):
    print("\n" + "#" * 60)
    print("BARRIDO: distintas distancias de trailing y niveles de parcial")
    print("#" * 60)

    mejor = None
    for partial_r in [1.5, 2.0, 2.5]:
        for trail_mult in [1.5, 2.0, 2.5, 3.0, 4.0]:
            td = backtest_trailing_con_mult(df, trail_mult, partial_r)
            if td.empty:
                continue
            n = len(td)
            wr = (td["resultado_R"] > 0).sum() / n * 100
            r_total = td["resultado_R"].sum()
            print(f"Parcial 1:{partial_r} | Trailing {trail_mult}x ATR | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R")
            if mejor is None or r_total > mejor[2]:
                mejor = (partial_r, trail_mult, r_total)

    print("#" * 60)
    if mejor:
        print(f"\n🏆 Mejor combinación (sobre TODO el dataset): Parcial 1:{mejor[0]} + Trailing {mejor[1]}x ATR -> R total: {mejor[2]:+.2f}R")
        print("⚠️  Esta combinación fue elegida optimizando sobre el mismo dataset que se reporta (in-sample) —")
        print("    validando train/test antes de confiar en ella:")

        corte = int(len(df) * 0.7)
        train = df.iloc[:corte].reset_index(drop=True)
        test = df.iloc[corte:].reset_index(drop=True)
        for nombre, sub_df in [("TRAIN (primeros 70%)", train), ("TEST (últimos 30%)", test)]:
            td = backtest_trailing_con_mult(sub_df, mejor[1], mejor[0])
            if td.empty:
                print(f"{nombre}: sin operaciones")
                continue
            n = len(td)
            wr = (td["resultado_R"] > 0).sum() / n * 100
            r_total = td["resultado_R"].sum()
            estado = "✅ RENTABLE" if r_total > 0 else "❌ pierde"
            print(f"{nombre:<22} | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R  {estado}")


def validacion_train_test(df, rr_ratio=2.5):
    """
    Divide el histórico en 70% (train) y 30% (test), y corre el TP fijo
    ganador (1:2.5) en cada mitad por separado. Si el resultado se sostiene
    en AMBAS partes -> es una señal más confiable, no solo suerte de muestra.
    """
    print("\n" + "#" * 60)
    print(f"VALIDACIÓN TRAIN/TEST (TP fijo 1:{rr_ratio}) — ¿se sostiene el edge?")
    print("#" * 60)

    corte = int(len(df) * 0.7)
    train = df.iloc[:corte].reset_index(drop=True)
    test = df.iloc[corte:].reset_index(drop=True)

    for nombre, sub_df in [("TRAIN (primeros 70%)", train), ("TEST (últimos 30%)", test)]:
        td = backtest_con_rr(sub_df, rr_ratio)
        if td.empty:
            print(f"{nombre}: sin operaciones")
            continue
        n = len(td)
        wr = (td["resultado_R"] > 0).sum() / n * 100
        r_total = td["resultado_R"].sum()
        breakeven = 1 / (1 + rr_ratio) * 100
        estado = "✅ RENTABLE" if wr > breakeven else "❌ pierde"
        print(f"{nombre:<22} | Trades: {n:<4} | Win rate: {wr:5.1f}% | Equilibrio: {breakeven:5.1f}% | R total: {r_total:+7.2f}R  {estado}")

    print("#" * 60)
    print("Si TEST también da rentable -> el edge probablemente es real, no solo ruido de la muestra.")
    print("Si TEST da negativo -> lo visto en TRAIN puede haber sido suerte (overfitting).")


def descontar_spread(trades_df, spread_puntos=SPREAD_PUNTOS, point_size=0.01):
    """
    Resta el costo del spread a cada trade, expresado en R.
    El spread se paga siempre (ganes o pierdas), así que se descuenta
    de TODOS los trades, no solo de los perdedores.
    """
    td = trades_df.copy()
    spread_precio = spread_puntos * point_size
    riesgo = (td["entrada"] - td["sl"]).abs()
    costo_R = spread_precio / riesgo
    td["resultado_R_neto"] = td["resultado_R"] - costo_R
    return td


def resumen_neto_vs_bruto(df, rr_ratio=2.5):
    """Corre la config ganadora (TP fijo 1:2.5) y compara resultado bruto vs neto de spread."""
    print("\n" + "#" * 60)
    print(f"RENTABILIDAD NETA DE SPREAD (TP fijo 1:{rr_ratio}, spread={SPREAD_PUNTOS} puntos)")
    print("#" * 60)

    td = backtest_con_rr(df, rr_ratio)
    if td.empty:
        print("Sin operaciones.")
        return

    td = descontar_spread(td)
    n = len(td)

    wr_bruto = (td["resultado_R"] > 0).sum() / n * 100
    r_bruto = td["resultado_R"].sum()

    wr_neto = (td["resultado_R_neto"] > 0).sum() / n * 100
    r_neto = td["resultado_R_neto"].sum()

    costo_total_R = r_bruto - r_neto

    print(f"Trades: {n}")
    print(f"BRUTO (sin spread) | Win rate: {wr_bruto:5.1f}% | R total: {r_bruto:+7.2f}R")
    print(f"NETO  (con spread) | Win rate: {wr_neto:5.1f}% | R total: {r_neto:+7.2f}R")
    print(f"Costo total del spread: {costo_total_R:.2f}R ({costo_total_R/n:.4f}R por trade en promedio)")
    print("#" * 60)

    if r_neto > 0:
        print(f"✅ Sigue siendo rentable después de descontar spread: {r_neto:+.2f}R")
    else:
        print(f"❌ El spread se come toda la ventaja — no rentable en la práctica")

    td.to_csv("resultados_neto_spread.csv", index=False)
    print("\nDetalle guardado en resultados_neto_spread.csv")


def comparar_con_sin_filtro_sesion(df_base):
    """Compara el resultado con y sin filtro de sesión horaria, mismo TP fijo 1:2.5."""
    global USE_SESSION_FILTER
    print("\n" + "#" * 60)
    print("COMPARACIÓN: con vs sin filtro de sesión horaria (TP fijo 1:2.5)")
    print("#" * 60)

    for activar, nombre in [(False, "SIN filtro de sesión"), (True, "CON filtro de sesión")]:
        USE_SESSION_FILTER = activar
        df2 = generar_senales(df_base.copy())
        td = backtest_con_rr(df2, 2.5)
        USE_SESSION_FILTER = False  # restaurar
        if td.empty:
            print(f"{nombre}: sin operaciones")
            continue
        n = len(td)
        wr = (td["resultado_R"] > 0).sum() / n * 100
        r_total = td["resultado_R"].sum()
        print(f"{nombre:<22} | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R")

    print("#" * 60)


def main():
    conectar_mt5()
    df = bajar_datos(SYMBOL, TIMEFRAME, N_VELAS)
    df = calcular_indicadores(df)
    df = generar_senales(df)

    trades_df = backtest(df)
    mostrar_resultados(trades_df)

    if not trades_df.empty:
        trades_df.to_csv("resultados_backtest.csv", index=False)
        print("\nDetalle de operaciones guardado en resultados_backtest.csv")

    diagnostico_entrada_vs_salida(df)
    comparar_salida_fija_vs_combinada(df)
    optimizar_trailing(df)
    comparar_con_sin_filtro_sesion(df)
    validacion_train_test(df, rr_ratio=2.5)
    resumen_neto_vs_bruto(df, rr_ratio=2.5)

    mt5.shutdown()


if __name__ == "__main__":
    main()