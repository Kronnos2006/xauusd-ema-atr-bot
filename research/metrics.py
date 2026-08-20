"""Métricas estándar de research sobre un DataFrame de trades en R-múltiplos
(columnas resultado_R, time_entrada, time_salida, ...).

Todo se calcula sobre el R NETO de spread (vía `descontar_spread`, ya
validado en el motor) -- coherente con la disciplina del proyecto de nunca
evaluar en bruto (ver Metodología.md, "Criterio de selección: t-stat sobre R
neto de spread").

Anualización de Sharpe/Sortino: se deriva de la frecuencia de trades
observada en los propios datos (n_trades / años de calendario que cubre la
muestra), no de una convención fija asumida -- evita tener que fijar a mano
cuántas barras "deberían" haber por año en un mercado 24/5 con feriados de
broker variables.

CAGR / Max Drawdown: se calculan sobre una curva de equity ADITIVA en R
(equity = 1 + cumsum(R_neto)), no compuesta -- este proyecto no maneja
tamaño de posición real ni moneda, solo R-múltiplos, así que "compounding"
no tiene una base monetaria a la que aplicarse. Si la equity final queda
<= 0, CAGR no está definido y se devuelve None (no un número negativo
engañoso vía raíz de un número no positivo).

Profit factor / Sharpe / Sortino quedan en None (en vez de infinito) cuando
el denominador es cero (sin trades perdedores / sin varianza) -- así el dict
resultante siempre es serializable a JSON sin manejo especial de
inf/NaN en export.py.
"""

import numpy as np

from research._engine_loader import cargar_engine

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = cargar_engine()
    return _engine


def metrica_robusta(trades_df):
    """Reexporta metrica_robusta de "Backtest ema v4.py" tal cual -- es la
    métrica de selección de modelo ya validada y congelada en la
    metodología del proyecto, no se reimplementa acá."""
    return _get_engine().metrica_robusta(trades_df)


def descontar_spread(trades_df, **kwargs):
    """Reexporta descontar_spread de "Backtest ema v4.py" tal cual."""
    return _get_engine().descontar_spread(trades_df, **kwargs)


_METRICAS_VACIAS = {
    "n_trades": 0, "r_por_trade": None, "expectancy_R": None,
    "profit_factor": None, "sharpe": None, "sortino": None,
    "cagr": None, "max_drawdown_R": None, "max_drawdown_pct": None,
    "win_rate_pct": None,
}


def _anios_calendario(trades_df):
    inicio = trades_df["time_entrada"].min()
    fin = trades_df["time_salida"].max()
    dias = (fin - inicio).total_seconds() / 86400
    return max(dias, 1.0) / 365.25  # piso de 1 día para no dividir por ~0 con trades muy próximos


def calcular_todas(trades_df):
    """
    Dado un DataFrame de trades (salida de `backtest`/`correr_fold`, con
    columnas resultado_R, time_entrada, time_salida), devuelve un dict con
    las métricas de research: n_trades, R por trade, Expectancy, Profit
    Factor, Sharpe, Sortino, CAGR, Max Drawdown (en R y en %), win rate.

    Devuelve todas las métricas en None/0 si `trades_df` está vacío.
    """
    if trades_df.empty:
        return dict(_METRICAS_VACIAS)

    trades_neto = descontar_spread(trades_df)
    r = trades_neto["resultado_R_neto"].to_numpy(dtype=float)
    n = len(r)

    ganadoras = r[r > 0]
    perdedoras = r[r < 0]
    win_rate = len(ganadoras) / n * 100

    r_promedio = float(r.mean())
    avg_win = float(ganadoras.mean()) if len(ganadoras) else 0.0
    avg_loss_abs = float(abs(perdedoras.mean())) if len(perdedoras) else 0.0
    expectancy = (win_rate / 100) * avg_win - (1 - win_rate / 100) * avg_loss_abs

    gross_profit = float(ganadoras.sum())
    gross_loss = float(abs(perdedoras.sum()))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    std_r = r.std(ddof=1) if n > 1 else 0.0
    downside_dev = float(np.sqrt(np.mean(np.minimum(r, 0.0) ** 2)))

    anios = _anios_calendario(trades_neto)
    trades_por_anio = n / anios

    sharpe = (r_promedio / std_r * np.sqrt(trades_por_anio)) if std_r > 0 else None
    sortino = (r_promedio / downside_dev * np.sqrt(trades_por_anio)) if downside_dev > 0 else None

    equity = 1.0 + np.cumsum(r)
    equity_final = equity[-1]
    cagr = (equity_final ** (1 / anios) - 1) if equity_final > 0 else None

    running_max = np.maximum.accumulate(equity)
    drawdown_R = equity - running_max
    max_drawdown_R = float(drawdown_R.min())
    with np.errstate(invalid="ignore", divide="ignore"):
        drawdown_pct = np.where(running_max > 0, drawdown_R / running_max, np.nan)
    max_drawdown_pct = float(np.nanmin(drawdown_pct)) if not np.all(np.isnan(drawdown_pct)) else None

    return {
        "n_trades": n,
        "r_por_trade": r_promedio,
        "expectancy_R": float(expectancy),
        "profit_factor": profit_factor,
        "sharpe": float(sharpe) if sharpe is not None else None,
        "sortino": float(sortino) if sortino is not None else None,
        "cagr": float(cagr) if cagr is not None else None,
        "max_drawdown_R": max_drawdown_R,
        "max_drawdown_pct": max_drawdown_pct,
        "win_rate_pct": float(win_rate),
    }
