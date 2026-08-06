"""
Fase 0 (panel Moskowitz-style) -- TF_Basket_H1. Calibracion empirica del
efecto individual (no el Sharpe=0.3 ya diversificado del portfolio) para
Donchian 20 y MA 10/50, con datos ya bajados de MT5. Sin costos, sin
walk-forward, sin train/test -- chequeo liviano de Fase 0/calibracion de
panel, no un resultado validado de Fase 1.

Diseño panel Moskowitz-style: retorno diario de la estrategia de señal
(direccion[t-1] * retorno_diario[t]), normalizado por la vol propia de
cada instrumento (unidades "R", mismo concepto que media_R/std_R usado
en el resto del proyecto), pooleado como panel instrumento x dia.

La correlacion cruzada entre instrumentos en el mismo dia infla la
significancia si se tratan los 10*T dias como independientes -- se
corrige escalando el N efectivo por el factor N_eff/N ya calculado en
correlacion_basket_tf_h1.py (N_eff=4.40, N=10).
"""
import sys
import math
import time

import numpy as np
import pandas as pd
import MetaTrader5 as mt5

sys.path.insert(0, r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta")
from triage_frecuencia import n_necesario_80_poder, HORIZONTE_LIMITE_ANIOS

sys.stdout.reconfigure(encoding="utf-8")

INICIO_VENTANA = pd.Timestamp("2010-01-01", tz="UTC")
BASKET = ["EURUSD", "USDJPY", "GBPUSD", "XAUUSD", "XAGUSD",
          "TLT", "LQD", "GDX", "XLE", "NVDA"]
N_INSTRUMENTOS = len(BASKET)
N_EFECTIVO = 4.40  # correlacion_basket_tf_h1.py, 2026-08-06
DIAS_TRADING_ANIO = 252


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


def direccion_donchian(close, n):
    hi = close.shift(1).rolling(n).max()
    lo = close.shift(1).rolling(n).min()
    direccion = pd.Series(np.nan, index=close.index)
    direccion[close > hi] = 1
    direccion[close < lo] = -1
    return direccion.ffill()


def direccion_ma(close, fast, slow):
    ma_f = close.rolling(fast).mean()
    ma_s = close.rolling(slow).mean()
    return np.sign(ma_f - ma_s)


def panel_r(close, direccion):
    ret = close.pct_change()
    sigma = ret.std()  # vol diaria del instrumento, ventana completa
    r_diario = (direccion.shift(1) * ret) / sigma
    return r_diario.dropna()


def evaluar_señal(nombre, datos, fn_direccion):
    r_pool = []
    for s in BASKET:
        df = datos[s]
        if df is None:
            continue
        close = df.set_index("time")["close"]
        direccion = fn_direccion(close)
        r = panel_r(close, direccion)
        r_pool.append(r)

    r_total = pd.concat(r_pool)
    n_naive = len(r_total)
    media_r = r_total.mean()
    std_r = r_total.std()

    t_naive = media_r / (std_r / math.sqrt(n_naive))
    n_eff_total = n_naive * (N_EFECTIVO / N_INSTRUMENTOS)
    t_corregido = media_r / (std_r / math.sqrt(n_eff_total))

    from math import erf
    def p_valor_dos_colas(t):
        return 2 * (1 - 0.5 * (1 + erf(abs(t) / math.sqrt(2))))

    p_naive = p_valor_dos_colas(t_naive)
    p_corregido = p_valor_dos_colas(t_corregido)

    sharpe_individual_anual = (media_r / std_r) * math.sqrt(DIAS_TRADING_ANIO)
    sharpe_portfolio_implicito = sharpe_individual_anual * math.sqrt(N_EFECTIVO)

    n_necesario = n_necesario_80_poder(media_r, std_r)
    # n_necesario esta en unidades de observaciones INDEPENDIENTES; cada
    # dia calendario aporta el equivalente informativo de N_EFECTIVO
    # observaciones independientes (no N_INSTRUMENTOS, que están
    # correlacionadas entre sí) -- de ahí la conversión a días reales.
    horizonte_dias = n_necesario / N_EFECTIVO
    horizonte_anios = horizonte_dias / DIAS_TRADING_ANIO

    print(f"=== {nombre} ===")
    print(f"Panel: {n_naive} obs. instrumento-dia (naive) | N efectivo ajustado por correlación: {n_eff_total:.0f}")
    print(f"media_R/día = {media_r:+.5f} | std_R/día = {std_r:.5f}")
    print(f"t naive (10 instrumentos independientes, SOBRE-estimado): {t_naive:+.3f}, p={p_naive:.4f}")
    print(f"t corregido (N_eff=4.40 por correlación cruzada): {t_corregido:+.3f}, p={p_corregido:.4f}")
    print(f"Sharpe anualizado de UN bet individual (sin diversificar): {sharpe_individual_anual:+.3f}")
    print(f"Sharpe de portfolio implícito (diversificando N_eff={N_EFECTIVO} bets ~Sharpe iguales): {sharpe_portfolio_implicito:+.3f}")
    print(f"  (vs. objetivo de la hipótesis: Sharpe > 0.3)")
    print(f"n necesario (80% poder, efecto empírico real): {n_necesario}")
    print(f"Horizonte proyectado (usando N_eff efectivo/año): {horizonte_anios:.1f} años")
    print()
    return {
        "media_r": media_r, "std_r": std_r, "t_corregido": t_corregido, "p_corregido": p_corregido,
        "sharpe_individual": sharpe_individual_anual, "sharpe_portfolio": sharpe_portfolio_implicito,
        "n_necesario": n_necesario, "horizonte_anios": horizonte_anios,
    }


def main():
    ok = mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    if not ok:
        print(f"FALLO conectar: {mt5.last_error()}")
        return

    datos = {}
    for s in BASKET:
        datos[s] = cargar_d1(s)

    mt5.shutdown()

    evaluar_señal("Donchian 20", datos, lambda close: direccion_donchian(close, 20))
    evaluar_señal("MA 10/50", datos, lambda close: direccion_ma(close, 10, 50))


if __name__ == "__main__":
    main()
