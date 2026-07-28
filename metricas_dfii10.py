"""
Metricas duras + power analysis sobre los 87 trades TEST (walk-forward,
4 folds) de la hipotesis macro DFII10 (fase 1).
=============================================================================
Reutiliza la simulacion ya validada de hipotesis_macro_dfii10.py (misma
seleccion de (N,M) por fold en TRAIN, misma evaluacion OOS en TEST) para
no recalcular nada con una logica distinta -- solo agrega el analisis de
metricas sobre el mismo pool de 87 trades ya usado para el t-stat.

Traduccion de R-multiples a curva de equity: se asume 1% de riesgo de
capital por trade (convencion estandar para este tipo de reporte, no es
un tamano de posicion real todavia decidido para el proyecto), trades
ordenados cronologicamente por fecha de entrada -- los 4 folds de TEST
son bloques disjuntos y consecutivos en el tiempo, asi que concatenarlos
en orden de fold preserva el orden cronologico real.
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

DFII10_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\hipotesis_macro_dfii10.py"
spec = importlib.util.spec_from_file_location("hipotesis_macro_dfii10", DFII10_PATH)
hip = importlib.util.module_from_spec(spec)
sys.modules["hipotesis_macro_dfii10"] = hip
spec.loader.exec_module(hip)  # no corre main() porque __name__ != "__main__"

mod = hip.mod  # Backtest ema v4.py ya cargado dentro de hipotesis_macro_dfii10
RIESGO_POR_TRADE_PCT = 0.01  # 1% de capital por trade, convencion de reporte


def recolectar_trades_test():
    df_dfii10 = hip.cargar_dfii10()
    df_oro = hip.bajar_oro_diario()
    folds_oro = mod.construir_bloques_walk_forward(df_oro, hip.N_FOLDS)
    resultados = [
        hip.correr_fold_macro(df_dfii10, train, test, i, hip.N_FOLDS)
        for i, (train, test) in enumerate(folds_oro, start=1)
    ]
    validos = [r for r in resultados if r.get("n_trades_test")]
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    todos = todos.sort_values("time_entrada").reset_index(drop=True)
    todos = mod.descontar_spread(todos)
    return todos, resultados


def calcular_metricas(td):
    r_neto = td["resultado_R_neto"]
    n = len(r_neto)

    # --- Sharpe / Sortino (sobre retornos por trade, en % de capital) ---
    retornos = r_neto * RIESGO_POR_TRADE_PCT
    media = retornos.mean()
    std = retornos.std(ddof=1)
    downside = retornos[retornos < 0]
    std_downside = downside.std(ddof=1) if len(downside) > 1 else float("nan")

    dias_totales = (td["time_salida"].max() - td["time_entrada"].min()).days
    anios_totales = dias_totales / 365.25
    trades_por_anio = n / anios_totales

    sharpe_por_trade = media / std
    sharpe_anual = sharpe_por_trade * math.sqrt(trades_por_anio)
    sortino_por_trade = media / std_downside if std_downside and not math.isnan(std_downside) else float("nan")
    sortino_anual = sortino_por_trade * math.sqrt(trades_por_anio) if not math.isnan(sortino_por_trade) else float("nan")

    # --- Equity curve (1% riesgo/trade, compuesto, orden cronologico) ---
    equity = [1.0]
    for r in retornos:
        equity.append(equity[-1] * (1 + r))
    equity = pd.Series(equity)
    equity_final = equity.iloc[-1]
    cagr = equity_final ** (1 / anios_totales) - 1

    pico = equity.cummax()
    drawdown = (equity - pico) / pico
    max_drawdown = drawdown.min()

    # --- Profit factor / expectancy (en R, no en % de capital) ---
    ganadores = r_neto[r_neto > 0]
    perdedores = r_neto[r_neto < 0]
    profit_factor = ganadores.sum() / abs(perdedores.sum()) if len(perdedores) and perdedores.sum() != 0 else float("inf")
    expectancy_R = r_neto.mean()
    win_rate = (r_neto > 0).mean()

    return {
        "n_trades": n,
        "anios_totales": anios_totales,
        "trades_por_anio": trades_por_anio,
        "win_rate_pct": win_rate * 100,
        "expectancy_R": expectancy_R,
        "profit_factor": profit_factor,
        "sharpe_anual": sharpe_anual,
        "sortino_anual": sortino_anual,
        "cagr_pct": cagr * 100,
        "max_drawdown_pct": max_drawdown * 100,
        "equity_final": equity_final,
    }


def power_analysis(td, alpha=0.05, poder_objetivo=0.80):
    """Tamaño de muestra necesario para detectar el efecto YA OBSERVADO
    (media/desvio de R neto por trade) con el poder objetivo, usando la
    formula estandar de una muestra (test t de una cola sobre la media,
    H0: media=0) -- n = ((z_alpha + z_beta) * sigma / mu)^2."""
    r_neto = td["resultado_R_neto"]
    media = r_neto.mean()
    std = r_neto.std(ddof=1)

    # z para alpha=0.05 dos colas (1.96) y poder=0.80 (0.8416) -- valores
    # tabulados de la normal estandar, sin depender de scipy.
    z_alpha = 1.959963985
    z_beta = 0.841621234

    n_necesario = ((z_alpha + z_beta) * std / media) ** 2
    n_actual = len(r_neto)
    n_adicional = max(0, math.ceil(n_necesario) - n_actual)

    return {
        "media_R": media, "std_R": std, "n_actual": n_actual,
        "n_necesario_80pct_poder": math.ceil(n_necesario),
        "n_adicional_necesario": n_adicional,
    }


def main():
    todos, resultados = recolectar_trades_test()
    print(f"\nTotal trades TEST recolectados: {len(todos)}\n")

    m = calcular_metricas(todos)
    print("=" * 70)
    print("MÉTRICAS DURAS -- 87 trades TEST, walk-forward DFII10 (neto de spread)")
    print("=" * 70)
    print(f"Período cubierto: {m['anios_totales']:.1f} años | Trades/año: {m['trades_por_anio']:.2f}")
    print(f"Win rate: {m['win_rate_pct']:.1f}%")
    print(f"Expectancy: {m['expectancy_R']:+.3f}R por trade")
    print(f"Profit factor: {m['profit_factor']:.2f}")
    print(f"Sharpe anualizado (retornos por trade, {RIESGO_POR_TRADE_PCT*100:.0f}% riesgo/trade): {m['sharpe_anual']:.3f}")
    print(f"Sortino anualizado: {m['sortino_anual']:.3f}")
    print(f"CAGR equivalente ({RIESGO_POR_TRADE_PCT*100:.0f}% riesgo/trade, compuesto): {m['cagr_pct']:+.2f}%/año")
    print(f"Máximo drawdown (misma curva de equity): {m['max_drawdown_pct']:.2f}%")
    print(f"Equity final (arrancando en 1.0): {m['equity_final']:.3f}")

    print("\n" + "=" * 70)
    print("POWER ANALYSIS -- n necesario para 80% de poder, alpha=0.05 dos colas")
    print("=" * 70)
    p = power_analysis(todos)
    print(f"Efecto observado: media R neto = {p['media_R']:+.3f} | desvío = {p['std_R']:.3f}")
    print(f"n actual: {p['n_actual']} | n necesario para 80% poder: {p['n_necesario_80pct_poder']}")
    print(f"Trades adicionales necesarios: {p['n_adicional_necesario']}")

    frecuencia_anual_n60 = 8  # ~8 episodios/año para N=60, ver diagnostico_frecuencia_dfii10.py
    anios_adicionales = p['n_adicional_necesario'] / frecuencia_anual_n60
    print(f"\nA ~{frecuencia_anual_n60} episodios/año (N=60): "
          f"{anios_adicionales:.1f} años adicionales de holdout en vivo para llegar a 80% de poder.")


if __name__ == "__main__":
    main()
