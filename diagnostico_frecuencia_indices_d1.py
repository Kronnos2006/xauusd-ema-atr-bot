"""
Diagnóstico de Frecuencia -- Trend Following / Breakout en Índices (D1)
=============================================================================
Este script evalúa la frecuencia de señales de breakout Donchian 20 y Cruce MA (20/50)
en frecuencia diaria (D1) para los índices principales disponibles en MT5:
- US500 (S&P 500)
- US30 (Dow Jones)
- USTEC / NAS100 (Nasdaq 100)

Verifica si la cantidad de señales por año es suficiente para alimentar un
Walk-Forward multi-fold sin violar el piso de 30 trades/fold en D1.
"""
import sys
import importlib.util
import numpy as np
import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)

SIMBOLOS_INDICES = ["US500", "US30", "USTEC", "NAS100", "US100"]

def contar_episodios(serie_bool):
    cambios = serie_bool.ne(serie_bool.shift()).cumsum()
    grupos = serie_bool.groupby(cambios)
    episodios = [grupo for _, grupo in grupos if grupo.iloc[0]]
    duraciones = [len(g) for g in episodios]
    return len(episodios), duraciones

def evaluar_indice(simbolo):
    print(f"\n==================================================")
    print(f"Evaluando Índice: {simbolo} en D1")
    print(f"==================================================")
    
    mod.conectar_mt5()
    inicio = pd.Timestamp("2005-01-01")
    ahora = pd.Timestamp.now()
    
    # Verificar si el símbolo existe
    info = mod.mt5.symbol_info(simbolo)
    if info is None:
        print(f"❌ Símbolo {simbolo} no disponible en este broker.")
        return None
        
    try:
        df = mod.bajar_datos_rango(simbolo, mod.mt5.TIMEFRAME_D1, inicio, ahora)
    except Exception as e:
        print(f"❌ Error al descargar datos de {simbolo}: {e}")
        return None
        
    if df.empty or len(df) < 500:
        print(f"⚠️ Datos insuficientes para {simbolo}: {len(df)} velas.")
        return None
        
    n_velas = len(df)
    anios = (df["time"].max() - df["time"].min()).days / 365.25
    print(f"Velas D1: {n_velas} ({anios:.1f} años: {df['time'].min().date()} -> {df['time'].max().date()})")
    
    # 1. Donchian 20 Breakout
    df["upper_20"] = df["high"].shift(1).rolling(20).max()
    df["lower_20"] = df["low"].shift(1).rolling(20).min()
    
    breakout_up = df["close"] > df["upper_20"]
    breakout_dn = df["close"] < df["lower_20"]
    breakout_any = breakout_up | breakout_dn
    
    n_donchian, dur_donchian = contar_episodios(breakout_any)
    
    # 2. Cruce MA 20 / 50
    df["ma_20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ma_50"] = df["close"].ewm(span=50, adjust=False).mean()
    
    cruce_up = (df["ma_20"] > df["ma_50"]) & (df["ma_20"].shift(1) <= df["ma_50"].shift(1))
    cruce_dn = (df["ma_20"] < df["ma_50"]) & (df["ma_20"].shift(1) >= df["ma_50"].shift(1))
    n_cruces = (cruce_up | cruce_dn).sum()
    
    print(f"Signals Donchian 20: {n_donchian} episodios ({n_donchian / anios:.1f}/año)")
    print(f"Signals Cruce MA 20/50: {n_cruces} cruces ({n_cruces / anios:.1f}/año)")
    
    return {
        "simbolo": simbolo,
        "n_velas": n_velas,
        "anios": round(anios, 1),
        "donchian_ep_yr": round(n_donchian / anios, 1),
        "ma_cross_yr": round(n_cruces / anios, 1),
    }

def main():
    resumen = []
    for s in SIMBOLOS_INDICES:
        res = evaluar_indice(s)
        if res:
            resumen.append(res)
            
    print("\n" + "=" * 80)
    print("RESUMEN DE FRECUENCIA EN ÍNDICES D1 (FASE 0)")
    print("=" * 80)
    if resumen:
        df_res = pd.DataFrame(resumen)
        print(df_res.to_string(index=False))
    else:
        print("No se encontraron símbolos de índices evaluables.")

if __name__ == "__main__":
    main()
