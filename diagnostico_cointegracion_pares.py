"""
Diagnóstico de Cointegración y Estacionariedad de Pares (Fase 0) - Robusto
=============================================================================
Evaluación de cointegración entre pares de activos en MT5 (D1 y H4) usando
Engle-Granger (ADF test sobre residuos OLS).
"""
import sys
import importlib.util
from datetime import datetime
import numpy as np
import pandas as pd
import MetaTrader5 as mt5

PARES_CANDIDATOS = [
    ("SPY", "DIA"),        # S&P 500 vs Dow Jones ETFs
    ("QQQ", "SPY"),        # Nasdaq vs S&P 500 ETFs
    ("AUDUSD", "NZDUSD"),  # Commodity Currencies Forex
    ("GLD", "SLV"),        # Gold vs Silver ETFs
    ("LQD", "GHYG"),       # Credit Spreads IG vs HY
    ("US500", "US30"),     # CFDs Índices
]

TIMEFRAMES = [
    ("D1", mt5.TIMEFRAME_D1, 252),
    ("H4", mt5.TIMEFRAME_H4, 252 * 6),
]

def conectar():
    ruta = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(path=ruta):
        print("ERROR inicializando MT5:", mt5.last_error())
        return False
    return True

def obtener_datos(simbolo, tf_code, n_velas=5000):
    mt5.symbol_select(simbolo, True)
    rates = mt5.copy_rates_from_pos(simbolo, tf_code, 0, n_velas)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

def adf_test_simple(series):
    y = series.values
    dy = np.diff(y)
    y_lag = y[:-1]
    X = np.column_stack([np.ones(len(y_lag)), y_lag])
    beta, _, _, _ = np.linalg.lstsq(X, dy, rcond=None)
    lambda_val = beta[1]
    
    resids = dy - X @ beta
    df_err = len(dy) - 2
    sigma2 = np.sum(resids**2) / df_err
    var_beta = sigma2 * np.linalg.inv(X.T @ X)[1, 1]
    se_beta = np.sqrt(var_beta)
    t_stat = lambda_val / se_beta
    # t_stat crítico al 5% para 2 variables es aprox -3.34
    p_val = 0.01 if t_stat < -3.9 else (0.049 if t_stat < -3.34 else (0.10 if t_stat < -2.89 else 0.20))
    return t_stat, p_val, lambda_val

def calcular_half_life(residuos):
    res = residuos.values
    dy = np.diff(res)
    y_lag = res[:-1]
    X = np.column_stack([np.ones(len(y_lag)), y_lag])
    beta, _, _, _ = np.linalg.lstsq(X, dy, rcond=None)
    lambda_val = beta[1]
    if lambda_val >= 0:
        return np.inf
    return -np.log(2) / lambda_val

def evaluar_par(sym_a, sym_b, timeframe_str, tf_code, velas_por_anio):
    df_a = obtener_datos(sym_a, tf_code, 5000)
    df_b = obtener_datos(sym_b, tf_code, 5000)
    
    if df_a is None or df_b is None:
        print(f"⚠️ Sin datos suficientes para {sym_a} o {sym_b} en {timeframe_str}")
        return None
        
    df_a = df_a[["time", "close"]].rename(columns={"close": sym_a})
    df_b = df_b[["time", "close"]].rename(columns={"close": sym_b})
    
    df = pd.merge(df_a, df_b, on="time", how="inner").sort_values("time").reset_index(drop=True)
    n_obs = len(df)
    if n_obs < 200:
        print(f"⚠️ Pocas obs solapadas para {sym_a}/{sym_b} ({n_obs})")
        return None
        
    anios = n_obs / velas_por_anio
    
    log_a = np.log(df[sym_a].values)
    log_b = np.log(df[sym_b].values)
    
    X = np.column_stack([np.ones(len(log_b)), log_b])
    beta, _, _, _ = np.linalg.lstsq(X, log_a, rcond=None)
    alpha_val, hedge_ratio = beta[0], beta[1]
    
    residuos = log_a - (alpha_val + hedge_ratio * log_b)
    df["residuo"] = residuos
    
    t_stat, p_val, lambda_val = adf_test_simple(pd.Series(residuos))
    hl = calcular_half_life(pd.Series(residuos))
    
    media_res = df["residuo"].rolling(120, min_periods=40).mean()
    std_res = df["residuo"].rolling(120, min_periods=40).std()
    z_score = (df["residuo"] - media_res) / std_res
    df["z_score"] = z_score
    
    extremo_15 = (z_score.abs() > 1.5).fillna(False)
    extremo_20 = (z_score.abs() > 2.0).fillna(False)
    
    cambios_15 = extremo_15.ne(extremo_15.shift()).cumsum()
    n_ep_15 = len([g for _, g in extremo_15.groupby(cambios_15) if g.iloc[0]])
    
    cambios_20 = extremo_20.ne(extremo_20.shift()).cumsum()
    n_ep_20 = len([g for _, g in extremo_20.groupby(cambios_20) if g.iloc[0]])
    
    status = "✅ COINTEGRADO" if p_val < 0.05 else "❌ NO"
    hl_dias = hl / (velas_por_anio / 252)
    print(f"Par: {sym_a:<6}/{sym_b:<6} [{timeframe_str:>2}] | Obs: {n_obs:>4} ({anios:4.1f}y) | Beta: {hedge_ratio:6.4f} | ADF t: {t_stat:6.3f} (p={p_val:.3f}) {status:<15} | HL: {hl_dias:5.1f}d | ep|z|>1.5: {n_ep_15/anios:4.1f}/y")
    
    return {
        "par": f"{sym_a}/{sym_b}",
        "tf": timeframe_str,
        "n_obs": n_obs,
        "anios": round(anios, 1),
        "beta": round(hedge_ratio, 4),
        "t_stat": round(t_stat, 3),
        "p_val": round(p_val, 4),
        "cointegrado": p_val < 0.05,
        "hl_dias": round(hl_dias, 1),
        "ep_15_yr": round(n_ep_15 / anios, 1),
        "ep_20_yr": round(n_ep_20 / anios, 1),
    }

def main():
    if not conectar():
        return
    resumen = []
    print("\n" + "=" * 90)
    print("EVALUACIÓN DE COINTEGRACIÓN Y ESTACIONARIEDAD EN MT5 (FASE 0)")
    print("=" * 90)
    for tf_str, tf_code, v_yr in TIMEFRAMES:
        for sa, sb in PARES_CANDIDATOS:
            res = evaluar_par(sa, sb, tf_str, tf_code, v_yr)
            if res:
                resumen.append(res)
                
    print("\n" + "=" * 90)
    print("RESUMEN DE RESULTADOS DE COINTEGRACIÓN")
    print("=" * 90)
    if resumen:
        df_res = pd.DataFrame(resumen)
        print(df_res.to_string(index=False))

if __name__ == "__main__":
    main()
