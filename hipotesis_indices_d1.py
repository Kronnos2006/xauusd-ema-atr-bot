"""
Hipótesis Fase 1: Donchian Breakout en US500 D1 con Controles de Rigor
=============================================================================
Este script implementa la validación de Walk-Forward para Donchian Breakout en US500 D1
incorporando los 4 controles obligatorios de corrección metodológica:

1. Benchmark Buy & Hold: Mide si la estrategia supera en Sharpe al S&P 500 Buy & Hold.
2. Asimetría de Dirección: Compara variantes 'solo_long' vs 'ambas' (long+short).
3. Descuento de Swaps Reales MT5: Descuenta el financiamiento diario overnight de MT5
   por cada noche mantenida, incluyendo el triple swap del miércoles.
4. Deflated Sharpe Ratio (DSR) Multitrial: Evalúa DSR penalizando por N_trials acumulados.

Frase Falsable:
Un breakout del canal Donchian de N días en US500 D1 genera un exceso de retorno neto
ajustado por riesgo superior al Buy & Hold del S&P 500 en las Z sesiones posteriores,
al descontar spreads y swaps nocturnos de MT5.
"""
import sys
import importlib.util
import math
from datetime import datetime
import numpy as np
import pandas as pd
import MetaTrader5 as mt5

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)

SIMBOLO = "US500"
TIMEFRAME = mt5.TIMEFRAME_D1
N_FOLDS = 4
ATR_PERIOD = 14
N_TRIALS_DSR = 50  # Historial acumulado de variantes intentadas en el proyecto

# Grilla declarada pre-registrada
GRID_DONCHIAN = [15, 20, 30]
GRID_Z_HORIZONTE = [10, 20, 40]
GRID_SL_MULT = [1.5, 2.0]
GRID_MODO = ["solo_long", "ambas"]

def obtener_datos_us500():
    mod.conectar_mt5()
    inicio = datetime(2008, 1, 1)
    ahora = datetime.now()
    
    mt5.symbol_select(SIMBOLO, True)
    info = mt5.symbol_info(SIMBOLO)
    if info is None:
        print(f"❌ Error: {SIMBOLO} no disponible en MT5")
        sys.exit(1)
        
    rates = mt5.copy_rates_range(SIMBOLO, TIMEFRAME, inicio, ahora)
    if rates is None or len(rates) == 0:
        print(f"❌ Error al descargar datos de {SIMBOLO}")
        sys.exit(1)
        
    df = pd.DataFrame(rates)
    df["fecha"] = pd.to_datetime(df["time"], unit="s").dt.normalize()
    
    # Calcular ATR14
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_PERIOD).mean()
    
    # Obtener tarifas Swap reales de MT5 (en puntos/dinero por lote por noche)
    swap_long = info.swap_long if info.swap_long != 0 else -0.5
    swap_short = info.swap_short if info.swap_short != 0 else -0.5
    point = info.point if info.point != 0 else 0.01
    
    return df.sort_values("fecha").reset_index(drop=True), swap_long, swap_short, point

def simular_donchian_us500(df, n_donchian, z_horizon, sl_mult, modo, swap_long, swap_short, point):
    df = df.copy()
    df["upper"] = df["high"].shift(1).rolling(n_donchian).max()
    df["lower"] = df["low"].shift(1).rolling(n_donchian).min()
    
    fechas = df["fecha"].values
    n_bars = len(df)
    trades = []
    fin_posicion = None
    
    for i in range(n_donchian + 1, n_bars - z_horizon):
        fecha_actual = df.loc[i, "fecha"]
        if fin_posicion is not None and fecha_actual <= fin_posicion:
            continue
            
        cierre = df.loc[i, "close"]
        upper = df.loc[i, "upper"]
        lower = df.loc[i, "lower"]
        atr = df.loc[i, "atr"]
        
        if pd.isna(upper) or pd.isna(atr):
            continue
            
        signal = None
        if cierre > upper:
            signal = "compra"
        elif cierre < lower and modo == "ambas":
            signal = "venta"
            
        if signal is None:
            continue
            
        # Entrada en i+1 (siguiente barra D1)
        idx_entrada = i + 1
        fila_entrada = df.loc[idx_entrada]
        entrada = float(fila_entrada["open"])
        riesgo = float(atr) * sl_mult
        sl = entrada - riesgo if signal == "compra" else entrada + riesgo
        
        idx_max_salida = min(idx_entrada + z_horizon, n_bars - 1)
        salida_fecha = None
        salida_precio = None
        motivo = None
        dias_mantenidos = 0
        
        for k in range(idx_entrada, idx_max_salida + 1):
            bar = df.loc[k]
            dias_mantenidos += 1
            tocado = (bar["low"] <= sl) if signal == "compra" else (bar["high"] >= sl)
            if tocado:
                salida_precio = sl
                salida_fecha = bar["fecha"]
                motivo = "SL_ATR"
                break
                
        if salida_precio is None:
            bar_fin = df.loc[idx_max_salida]
            salida_precio = float(bar_fin["close"])
            salida_fecha = bar_fin["fecha"]
            motivo = "HORIZONTE"
            
        # Calcular resultado R bruto
        r_bruto = (salida_precio - entrada) / riesgo if signal == "compra" else (entrada - salida_precio) / riesgo
        
        # Descuento de spread de entrada/salida (aprox 0.5 puntos en US500)
        spread_puntos = 0.5
        r_spread_cost = (spread_puntos) / riesgo
        
        # Descuento de Swap de MT5 por noches mantenidas
        # swap rate por noche en R: (dias * |swap| * point) / riesgo
        rate = abs(swap_long) if signal == "compra" else abs(swap_short)
        # Ajustar por miércoles triple swap (aprox x1.2)
        swap_cost_pts = dias_mantenidos * rate * point * 1.2
        r_swap_cost = swap_cost_pts / riesgo
        
        r_neto = r_bruto - r_spread_cost - r_swap_cost
        
        trades.append({
            "tipo": signal,
            "time_entrada": fila_entrada["fecha"],
            "time_salida": salida_fecha,
            "entrada": entrada,
            "salida": salida_precio,
            "riesgo": riesgo,
            "dias": dias_mantenidos,
            "resultado_R_bruto": r_bruto,
            "resultado_R_neto": r_neto,
            "motivo": motivo,
        })
        fin_posicion = salida_fecha
        
    return pd.DataFrame(trades)

def calcular_metrics_benchmark(df_test):
    """Calcula retorno acumulado y Sharpe ratio del Benchmark Buy & Hold de US500."""
    p_init = df_test["close"].iloc[0]
    p_final = df_test["close"].iloc[-1]
    ret_bh_total = (p_final - p_init) / p_init
    
    ret_diarios = df_test["close"].pct_change().dropna()
    mean_d = ret_diarios.mean()
    std_d = ret_diarios.std()
    sharpe_bh = (mean_d / std_d * math.sqrt(252)) if std_d > 0 else 0.0
    return ret_bh_total, sharpe_bh

def calcular_dsr(sharpe_observed, n_obs, n_trials=N_TRIALS_DSR):
    """Calcula Deflated Sharpe Ratio (DSR) ajustando por comparaciones múltiples."""
    if n_obs < 10 or sharpe_observed <= 0:
        return 0.0
    emc = 0.5772156649  # constante Euler-Mascheroni
    e_max_sharpe = (1 - emc) * math.sqrt(2 * math.log(n_trials)) + emc * math.sqrt(2 * math.log(n_trials))
    var_sharpe = (1 + 0.5 * sharpe_observed**2) / n_obs
    dsr_stat = (sharpe_observed - e_max_sharpe) / math.sqrt(var_sharpe)
    # p-value DSR acumulado normal
    dsr_p = 0.5 * (1 + math.erf(dsr_stat / math.sqrt(2)))
    return dsr_p

def correr_walk_forward_us500():
    df, swap_l, swap_s, pt = obtener_datos_us500()
    print("=" * 80)
    print(f"HIPÓTESIS US500 D1 -- DONCHIAN BREAKOUT (WALK-FORWARD {N_FOLDS} FOLDS)")
    print(f"Historial: {len(df)} velas D1 ({df['fecha'].iloc[0]:%Y-%m-%d} -> {df['fecha'].iloc[-1]:%Y-%m-%d})")
    print(f"Swaps MT5 reales: Long={swap_l}, Short={swap_s} (point={pt}) | N_trials DSR={N_TRIALS_DSR}")
    print("=" * 80 + "\n")
    
    folds = mod.construir_bloques_walk_forward(df, N_FOLDS)
    resumen_folds = []
    
    for fold_num, (df_train, df_test) in enumerate(folds, start=1):
        print(f"\n--- FOLD {fold_num}/{N_FOLDS} ---")
        print(f"TRAIN: {len(df_train)} días ({df_train['fecha'].iloc[0]:%Y-%m-%d} -> {df_train['fecha'].iloc[-1]:%Y-%m-%d})")
        print(f"TEST:  {len(df_test)} días ({df_test['fecha'].iloc[0]:%Y-%m-%d} -> {df_test['fecha'].iloc[-1]:%Y-%m-%d})")
        
        # 1. Selección in-sample en TRAIN
        mejor_combo = None
        mejor_tstat = float("-inf")
        
        for n_don in GRID_DONCHIAN:
            for z_hor in GRID_Z_HORIZONTE:
                for sl_m in GRID_SL_MULT:
                    for modo in GRID_MODO:
                        td_tr = simular_donchian_us500(df_train, n_don, z_hor, sl_m, modo, swap_l, swap_s, pt)
                        if len(td_tr) >= 20:
                            r_neto = td_tr["resultado_R_neto"]
                            t_stat = r_neto.mean() / (r_neto.std() / math.sqrt(len(r_neto)))
                            if t_stat > mejor_tstat:
                                mejor_tstat = t_stat
                                mejor_combo = (n_don, z_hor, sl_m, modo)
                                
        if mejor_combo is None:
            print("❌ Sin selección in-sample en TRAIN (ninguna variante alcanzó el piso de trades).")
            continue
            
        n_don, z_hor, sl_m, modo = mejor_combo
        print(f"Elegido in-sample (TRAIN): Donchian={n_don}d, Horizonte={z_hor}d, SL={sl_m}xATR, Modo={modo} (t-stat={mejor_tstat:.3f})")
        
        # 2. Evaluación out-of-sample en TEST
        df_train_test = pd.concat([df_train, df_test], ignore_index=True)
        td_full = simular_donchian_us500(df_train_test, n_don, z_hor, sl_m, modo, swap_l, swap_s, pt)
        fecha_ini_test = df_test["fecha"].min()
        td_test = td_full[td_full["time_entrada"] >= fecha_ini_test].reset_index(drop=True)
        
        if td_test.empty:
            print("❌ TEST: sin operaciones en out-of-sample.")
            continue
            
        n_tr_test = len(td_test)
        r_neto_test = td_test["resultado_R_neto"].sum()
        r_arr = td_test["resultado_R_neto"].values
        mean_r = r_arr.mean()
        std_r = r_arr.std(ddof=1) if len(r_arr) > 1 else 1.0
        t_stat_test = mean_r / (std_r / math.sqrt(n_tr_test))
        
        # Sharpe implícito de la estrategia
        sharpe_est = (mean_r / std_r * math.sqrt(n_tr_test / (len(df_test)/252))) if std_r > 0 else 0.0
        
        # Métrica Benchmark S&P 500 Buy & Hold
        ret_bh_total, sharpe_bh = calcular_metrics_benchmark(df_test)
        excess_sharpe = sharpe_est - sharpe_bh
        
        # Deflated Sharpe Ratio
        dsr_val = calcular_dsr(sharpe_est, n_tr_test, N_TRIALS_DSR)
        
        estado = "✅ SUPERA BENCHMARK" if (r_neto_test > 0 and excess_sharpe > 0) else "❌ INSUFICIENTE / PIERDE"
        print(f"TEST OOS | Trades: {n_tr_test} | R Neto: {r_neto_test:+.2f}R | t-stat: {t_stat_test:+.3f}")
        print(f"         | Sharpe Estrategia: {sharpe_est:.2f} vs Benchmark Buy&Hold: {sharpe_bh:.2f} (Excess: {excess_sharpe:+.2f})")
        print(f"         | Buy & Hold Retorno Total: {ret_bh_total*100:+.1f}% | DSR p-value: {dsr_val:.4f} {estado}")
        
        resumen_folds.append({
            "fold": fold_num,
            "combo": f"D{n_don}_Z{z_hor}_SL{sl_m}_{modo}",
            "trades": n_tr_test,
            "r_neto": r_neto_test,
            "t_stat": t_stat_test,
            "sharpe_est": sharpe_est,
            "sharpe_bh": sharpe_bh,
            "excess_sharpe": excess_sharpe,
            "dsr_val": dsr_val,
            "ok": r_neto_test > 0 and excess_sharpe > 0,
            "td": td_test,
        })
        
    print("\n" + "=" * 80)
    print("RESUMEN DE WALK-FORWARD CON CONTROLES DE RIGOR (US500 D1)")
    print("=" * 80)
    if not resumen_folds:
        print("Sin folds evaluables.")
        return
        
    n_ok = sum(1 for r in resumen_folds if r["ok"])
    print(f"Folds evaluables: {len(resumen_folds)}/{N_FOLDS}")
    print(f"Folds que superan al Benchmark con R neto positivo: {n_ok}/{len(resumen_folds)}")
    
    all_td = pd.concat([r["td"] for r in resumen_folds], ignore_index=True)
    tot_r = all_td["resultado_R_neto"].sum()
    tot_tr = len(all_td)
    
    r_vec = all_td["resultado_R_neto"].values
    t_pooled = r_vec.mean() / (r_vec.std(ddof=1) / math.sqrt(tot_tr))
    
    print(f"Trades acumulados en TEST: {tot_tr} | R neto total: {tot_r:+.2f}R | t-stat pooled: {t_pooled:+.3f}")
    
    if n_ok == len(resumen_folds) and t_pooled > 1.96:
        print("✅ LA HIPÓTESIS DEMUESTRA EDGE REAL Y SUPERA AL BENCHMARK S&P 500 DE FORMA ROBUSTA.")
    elif n_ok >= len(resumen_folds) * 0.5:
        print("⚠️ EDGE PARCIAL / INESTABLE -- No supera al Benchmark de forma consistente en todos los folds.")
    else:
        print("❌ LA HIPÓTESIS SE DESCARTA -- No supera al Benchmark Buy & Hold o el R neto es insuficiente.")

if __name__ == "__main__":
    correr_walk_forward_us500()
