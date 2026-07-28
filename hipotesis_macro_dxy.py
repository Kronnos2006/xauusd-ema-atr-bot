"""
Hipotesis macro, fase 1: DXY sintetico como filtro de regimen para XAUUSD.
=============================================================================
Analoga a hipotesis_macro_dfii10.py, mismo diseño exacto (misma frase,
misma definicion de episodio, mismo esquema de entrada/salida) aplicado
al DXY sintetico en vez de DFII10 -- unica variable que cambia es la
fuente de la señal macro.

Frase falsable: cuando el DXY (sintetico, 6 pares FX, formula ICE, ver
construir_dxy_sintetico.py y validar_dxy_sintetico.py -- correlacion
0.9945 vs. 21 valores reales de investing.com) viene cayendo de forma
sostenida en los ultimos N dias habiles, el oro tiene sesgo alcista
sostenido en las M sesiones siguientes.

Definiciones fijas (identicas a DFII10, sin variantes nuevas):
- Señal de "caida sostenida": DXY[t] < DXY[t-N].
- Episodio: racha maxima de dias consecutivos con la señal activa. Se
  opera UNA sola vez por episodio.
- Entrada: SOLO compra, al cierre de la primera sesion de oro posterior
  al dia en que el episodio arranca (D+1).
- Riesgo/SL: ATR14 diario * SL_ATR_MULT. Sin take-profit fijo.
- Salida: horizonte fijo de M sesiones o SL tocado (low <= sl),
  lo que ocurra primero.
- Sin pyramiding.

Grilla declarada (3x3, identica a DFII10):
  N (dias habiles de caida sostenida): 20, 60, 120
  M (sesiones de horizonte de salida): 5, 10, 20

Walk-forward: 4 folds anclados -- mismo N_FOLDS que DFII10, justificado
por frecuencia comparable (ver diagnostico_frecuencia_dxy.py: 260/200/111
episodios para N=20/60/120, vs. 291/177/132 de DFII10).

Fuente de datos: DXY sintetico (historial/dxy_sintetico.csv, construido
por construir_dxy_sintetico.py desde 6 pares FX de MT5, formula ICE real,
validado contra investing.com). Oro: XAUUSD diario via MT5.

Regla de corte: p<0.05 en el t-stat pooled sobre R neto de spread, CON y
SIN el fold mas fuerte (mismo estandar aplicado al ratio oro/plata, mas
estricto que la redaccion original de DFII10 -- fijado explicitamente
esta vez antes de correr nada, ver nota metodologica en el vault sobre
la falta de un numero explicito en el intento del ratio oro/plata).
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
RUTA_DXY = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\historial\dxy_sintetico.csv"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)

GRID_N = [20, 60, 120]
GRID_M = [5, 10, 20]
N_FOLDS = 4
ATR_PERIOD_DIARIO = 14
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")


# ============================================================
# 1. Datos DXY sintetico
# ============================================================

def cargar_dxy():
    df = pd.read_csv(RUTA_DXY)
    df = df.rename(columns={"time": "fecha", "dxy_sintetico": "dxy"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df[["fecha", "dxy"]].reset_index(drop=True)


def detectar_inicios_episodio(df_dxy, n):
    cond = df_dxy["dxy"] < df_dxy["dxy"].shift(n)
    cond = cond.fillna(False)
    inicio_episodio = cond & ~cond.shift(1, fill_value=False)
    return df_dxy.loc[inicio_episodio, "fecha"].tolist()


# ============================================================
# 2. Datos de oro (diario) + ATR
# ============================================================

def bajar_oro_diario():
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()
    diario = mod.bajar_datos_rango(mod.SYMBOL, mod.mt5.TIMEFRAME_D1, INICIO_DATOS_ORO_MT5, ahora)
    diario = diario.rename(columns={"time": "fecha"})
    diario["fecha"] = diario["fecha"].dt.normalize()

    high_low = diario["high"] - diario["low"]
    high_close = (diario["high"] - diario["close"].shift()).abs()
    low_close = (diario["low"] - diario["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    diario["atr"] = tr.rolling(ATR_PERIOD_DIARIO).mean()

    return diario.reset_index(drop=True)


# ============================================================
# 3. Simulacion de trades para una combinacion (N, M) dada
# ============================================================

def simular_trades(df_dxy, df_oro, n, m):
    inicios = detectar_inicios_episodio(df_dxy, n)
    fechas_oro = df_oro["fecha"].values

    trades = []
    fin_posicion_abierta = None

    for fecha_inicio in inicios:
        if fin_posicion_abierta is not None and fecha_inicio <= fin_posicion_abierta:
            continue

        idx_entrada = np.searchsorted(fechas_oro, np.datetime64(fecha_inicio), side="right")
        if idx_entrada >= len(df_oro):
            continue
        idx_horizonte = idx_entrada + m
        if idx_horizonte >= len(df_oro) or pd.isna(df_oro.loc[idx_entrada, "atr"]):
            continue

        fila_entrada = df_oro.loc[idx_entrada]
        entrada = float(fila_entrada["close"])
        riesgo = float(fila_entrada["atr"]) * mod.SL_ATR_MULT
        sl = entrada - riesgo

        salida = None
        for idx in range(idx_entrada + 1, idx_horizonte + 1):
            fila = df_oro.loc[idx]
            if fila["low"] <= sl:
                trades.append({
                    "tipo": "compra", "entrada": entrada, "sl": sl, "riesgo": riesgo,
                    "time_entrada": fila_entrada["fecha"], "time_salida": fila["fecha"],
                    "resultado_R": -1.0, "salida": "SL_ATR",
                })
                salida = fila["fecha"]
                break
        if salida is None:
            fila_horizonte = df_oro.loc[idx_horizonte]
            resultado_R = (float(fila_horizonte["close"]) - entrada) / riesgo
            trades.append({
                "tipo": "compra", "entrada": entrada, "sl": sl, "riesgo": riesgo,
                "time_entrada": fila_entrada["fecha"], "time_salida": fila_horizonte["fecha"],
                "resultado_R": resultado_R, "salida": "HORIZONTE",
            })
            salida = fila_horizonte["fecha"]

        fin_posicion_abierta = salida

    return pd.DataFrame(trades)


# ============================================================
# 4. Seleccion de (N, M) en TRAIN + walk-forward
# ============================================================

def elegir_mejor_nm(df_dxy_train, df_oro_train, verbose=False):
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for n in GRID_N:
        for m in GRID_M:
            td = simular_trades(df_dxy_train, df_oro_train, n, m)
            metrica = mod.metrica_robusta(td) if not td.empty else float("-inf")
            detalle.append((n, m, len(td), metrica))
            if metrica > mejor_metrica:
                mejor_metrica = metrica
                mejor = (n, m)
    if verbose:
        for n, m, ntr, met in detalle:
            elegible = "OK" if ntr >= mod.MIN_TRADES_SELECCION else f"< piso ({mod.MIN_TRADES_SELECCION})"
            met_str = f"{met:.3f}" if met != float("-inf") else "-inf"
            print(f"    N={n:>3} M={m:>2} | trades TRAIN: {ntr:>3} ({elegible}) | t-stat R neto: {met_str}")
    return mejor, mejor_metrica


def _rango_fechas_oro(df):
    return f"{df['fecha'].iloc[0]:%Y-%m-%d} -> {df['fecha'].iloc[-1]:%Y-%m-%d}"


def correr_fold_macro(df_dxy, df_oro_train, df_oro_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN oro: {len(df_oro_train)} días ({_rango_fechas_oro(df_oro_train)}) "
          f"| TEST oro: {len(df_oro_test)} días ({_rango_fechas_oro(df_oro_test)})")
    print("=" * 70)

    fecha_corte_train = df_oro_train["fecha"].max()
    df_dxy_train = df_dxy[df_dxy["fecha"] <= fecha_corte_train].reset_index(drop=True)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    (mejor_n, mejor_m), metrica_train = elegir_mejor_nm(df_dxy_train, df_oro_train, verbose=True)

    resultado = {
        "fold": fold_num, "n": None, "m": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor_n is None or metrica_train == float("-inf"):
        print(f"  ❌ Ninguna combinación de la grilla llegó al piso de "
              f"{mod.MIN_TRADES_SELECCION} trades en TRAIN -- fold sin selección posible.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): N={mejor_n}, M={mejor_m} (t-stat R neto: {metrica_train:.3f})")

    fecha_fin_test = df_oro_test["fecha"].max()
    df_dxy_hasta_test = df_dxy[df_dxy["fecha"] <= fecha_fin_test].reset_index(drop=True)

    df_oro_train_test = pd.concat([df_oro_train, df_oro_test], ignore_index=True)
    td_completo = simular_trades(df_dxy_hasta_test, df_oro_train_test, mejor_n, mejor_m)
    fecha_inicio_test = df_oro_test["fecha"].min()
    td_test = td_completo[td_completo["time_entrada"] >= fecha_inicio_test].reset_index(drop=True)

    resultado["n"], resultado["m"] = mejor_n, mejor_m
    resultado["td_test"] = td_test

    if td_test.empty:
        print("  TEST (out-of-sample): sin operaciones.")
        return resultado

    n_trades = len(td_test)
    wr = (td_test["resultado_R"] > 0).sum() / n_trades * 100
    r_total = td_test["resultado_R"].sum()
    r_neto = mod.descontar_spread(td_test)["resultado_R_neto"].sum()
    rentable = r_neto > 0
    estado = "✅ RENTABLE" if rentable else "❌ pierde"
    print(f"  TEST (out-of-sample) | Trades: {n_trades:<3} | Win rate: {wr:5.1f}% | "
          f"R total: {r_total:+7.2f}R | Neto de spread: {r_neto:+7.2f}R  {estado}")

    resultado.update(n_trades_test=n_trades, wr_test=wr, r_total_test=r_total,
                      r_neto_test=r_neto, rentable=rentable)
    return resultado


def resumen_walk_forward_macro(resultados):
    print("\n" + "#" * 70)
    print("RESUMEN WALK-FORWARD -- Hipótesis macro DXY sintético (fase 1)")
    print("#" * 70)
    for r in resultados:
        if not r["n_trades_test"]:
            motivo = "sin selección posible en TRAIN" if r["n"] is None else "sin operaciones en TEST"
            print(f"Fold {r['fold']} | {motivo}")
            continue
        estado = "✅ RENTABLE" if r["rentable"] else "❌ pierde"
        print(f"Fold {r['fold']} | N={r['n']:>3} M={r['m']:>2} | Trades: {r['n_trades_test']:<3} | "
              f"Win rate: {r['wr_test']:5.1f}% | R total: {r['r_total_test']:+7.2f}R | "
              f"Neto spread: {r['r_neto_test']:+7.2f}R  {estado}")
    print("#" * 70)

    validos = [r for r in resultados if r["n_trades_test"]]
    if not validos:
        print("\nNingún fold generó operaciones evaluables en TEST -- hipótesis se descarta.")
        return

    rentables_neto = [r for r in validos if r["r_neto_test"] and r["r_neto_test"] > 0]
    print(f"\nFolds evaluables: {len(validos)}/{len(resultados)}")
    print(f"Folds rentables (neto de spread): {len(rentables_neto)}/{len(validos)}")

    trades_totales = sum(r["n_trades_test"] for r in validos)
    r_neto_total = sum(r["r_neto_test"] for r in validos)
    print(f"Trades TEST acumulados: {trades_totales} | R neto acumulado: {r_neto_total:+.2f}R")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    if r_neto_total != 0:
        pct_dominante = fold_max["r_neto_test"] / r_neto_total * 100
        r_neto_sin_dominante = r_neto_total - fold_max["r_neto_test"]
        trades_sin_dominante = trades_totales - fold_max["n_trades_test"]
        print(f"\nFold más fuerte: Fold {fold_max['fold']} ({fold_max['r_neto_test']:+.2f}R neto) "
              f"-> {pct_dominante:.0f}% del R neto acumulado.")
        if trades_sin_dominante > 0:
            print(f"Sin ese fold: {r_neto_sin_dominante:+.2f}R neto en {trades_sin_dominante} trades "
                  f"({r_neto_sin_dominante/trades_sin_dominante:+.3f}R/trade en promedio).")


def t_stat_pooled(td, etiqueta):
    r_neto = mod.descontar_spread(td)["resultado_R_neto"]
    n = len(r_neto)
    media = r_neto.mean()
    std = r_neto.std(ddof=1)
    t = media / (std / math.sqrt(n))
    p_valor = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    print(f"  [{etiqueta}] n={n} | R_neto medio={media:+.3f} | t-stat={t:+.3f} | p (aprox. normal, dos colas)={p_valor:.4f}")
    return t, p_valor


def analisis_pooled_test(resultados):
    print("\n" + "#" * 70)
    print("t-stat real sobre R neto -- trades TEST agrupados (no conteo de folds)")
    print("#" * 70)
    validos = [r for r in resultados if r.get("n_trades_test")]
    if not validos:
        print("  Sin folds evaluables.")
        return None, None, None, None
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    t_todos, p_todos = t_stat_pooled(todos, f"{len(todos)} trades TEST, los {len(validos)} folds evaluables")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    sin_dominante = pd.concat(
        [r["td_test"] for r in validos if r["fold"] != fold_max["fold"]], ignore_index=True)
    t_sin, p_sin = (None, None)
    if not sin_dominante.empty:
        t_sin, p_sin = t_stat_pooled(sin_dominante, f"{len(sin_dominante)} trades TEST, sin Fold {fold_max['fold']} (el más fuerte)")

    print(f"\nRegla de corte (p<0.05 con y sin el fold más fuerte, fijada antes de correr):")
    pasa = (p_todos is not None and p_todos < 0.05) and (p_sin is not None and p_sin < 0.05)
    print("✅ PASA EL CHECKPOINT" if pasa else "❌ NO PASA EL CHECKPOINT")
    return t_todos, p_todos, t_sin, p_sin


# ============================================================
# main
# ============================================================

def main():
    df_dxy = cargar_dxy()
    print(f"DXY sintético: {len(df_dxy)} días, {df_dxy['fecha'].min().date()} -> {df_dxy['fecha'].max().date()}")

    df_oro = bajar_oro_diario()
    print(f"Oro diario (MT5): {len(df_oro)} días, {_rango_fechas_oro(df_oro)}\n")

    folds_oro = mod.construir_bloques_walk_forward(df_oro, N_FOLDS)
    resultados = [
        correr_fold_macro(df_dxy, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds_oro, start=1)
    ]
    resumen_walk_forward_macro(resultados)
    analisis_pooled_test(resultados)


if __name__ == "__main__":
    main()
