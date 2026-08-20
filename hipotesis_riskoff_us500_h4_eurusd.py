"""
Hipotesis H2 del marco EURUSD: risk-off en renta variable (US500) como
señal direccional bajista para EURUSD (dolar-refugio).
=============================================================================
Mismo driver que "Risk-off US500 H4 -> XAUUSD" (marco XAUUSD, descartado:
t=+1.525/p=0.1271, DSR=0.1806), pero mecanismo de transmision y target
distintos -- ver ficha "Risk-off US500 H4 EURUSD - fase 1.md" (vault).

Frase falsable: cuando el retorno del US500 en la vela H4 cerrada CAE mas
de k desvios estandar de su propia distribucion historica en valor
absoluto (solo caidas cuentan -- direccional por diseño), el EURUSD tiene
sesgo BAJISTA en las M velas H4 siguientes (dolar se fortalece como
refugio). Direccion SIEMPRE VENTA -- fijada por la frase falsable, no un
parametro de la grilla.

Std del umbral: congelado en TRAIN por fold (misma disciplina que el
resto del proyecto -- ver docstring de hipotesis_riskoff_us500_h4.py).

Grilla (3x3): k en {0.75, 1.0, 1.25} x M en {1, 2, 3} velas H4.
Folds: 8, reusando la derivacion ya hecha para el mismo driver (fold
minimo real 36 trades a k=1.25, +20% margen).

Regla de corte:
- |t| > 1.96 sobre R neto pooled de TEST, con y sin el fold mas fuerte.
- DSR >= 0.95, N = 144 (esta grilla 3x3x8=72 + la version XAUUSD del
  mismo driver US500, otras 72 -- confirmado por el usuario: el driver es
  el mismo aunque el mecanismo de transmision y el target difieran).
- Spread real EURUSD: SPREAD_PUNTOS_EURUSD=15 (1.5 pips, mismo supuesto
  documentado que en hipotesis_carry_eurusd.py -- este broker no dio un
  spread live confiable en la consulta).
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
DIR_PROYECTO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta"
RUTA_US500 = DIR_PROYECTO + r"\historial\us500_h4.csv"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)

spec_dsr = importlib.util.spec_from_file_location("deflated_sharpe", DIR_PROYECTO + r"\deflated_sharpe.py")
dsr_mod = importlib.util.module_from_spec(spec_dsr)
sys.modules["deflated_sharpe"] = dsr_mod
spec_dsr.loader.exec_module(dsr_mod)

GRID_K = [0.75, 1.0, 1.25]
GRID_M = [1, 2, 3]
N_FOLDS = 8
ATR_PERIOD_H4 = 14
INICIO_US500 = pd.Timestamp("2012-08-06")
MIN_TRADES_SELECCION = 30
SPREAD_PUNTOS_EURUSD = 15
POINT_SIZE_EURUSD = 0.00001
N_VARIANTES_DSR = 144  # 72 (esta grilla) + 72 (version XAUUSD, mismo driver)


def cargar_us500():
    df = pd.read_csv(RUTA_US500).rename(columns={"time": "fecha"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df[df["fecha"] >= INICIO_US500].reset_index(drop=True)
    df["retorno_h4"] = df["close"].pct_change(1)
    return df


def detectar_inicios_episodio(df_us500, k, std_congelado):
    cond = (df_us500["retorno_h4"] < -k * std_congelado).fillna(False)
    inicio_episodio = cond & ~cond.shift(1, fill_value=False)
    return list(df_us500.loc[inicio_episodio, "fecha"])


def bajar_eurusd_h4():
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()
    h4 = mod.bajar_datos_rango("EURUSD", mod.mt5.TIMEFRAME_H4, INICIO_US500, ahora)
    h4 = h4.rename(columns={"time": "fecha"})

    high_low = h4["high"] - h4["low"]
    high_close = (h4["high"] - h4["close"].shift()).abs()
    low_close = (h4["low"] - h4["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    h4["atr"] = tr.rolling(ATR_PERIOD_H4).mean()

    return h4.reset_index(drop=True)


def descontar_spread_eurusd(trades_df):
    td = trades_df.copy()
    spread_precio = SPREAD_PUNTOS_EURUSD * POINT_SIZE_EURUSD
    riesgo = td["riesgo"]
    costo_R = spread_precio / riesgo
    td["resultado_R_neto"] = td["resultado_R"] - costo_R
    return td


def metrica_robusta_eurusd(trades_df):
    n = len(trades_df)
    if n < MIN_TRADES_SELECCION:
        return float("-inf")
    r_neto = descontar_spread_eurusd(trades_df)["resultado_R_neto"]
    std = r_neto.std(ddof=1)
    if not std or pd.isna(std):
        return float("-inf")
    return r_neto.mean() / (std / np.sqrt(n))


def simular_trades(df_us500_ref, df_eurusd, k, m, std_congelado):
    inicios = detectar_inicios_episodio(df_us500_ref, k, std_congelado)
    fechas_eurusd = df_eurusd["fecha"].values

    trades = []
    fin_posicion_abierta = None

    for fecha_inicio in inicios:
        if fin_posicion_abierta is not None and fecha_inicio <= fin_posicion_abierta:
            continue

        idx_entrada = np.searchsorted(fechas_eurusd, np.datetime64(fecha_inicio), side="right")
        if idx_entrada >= len(df_eurusd):
            continue
        idx_horizonte = idx_entrada + m
        if idx_horizonte >= len(df_eurusd) or pd.isna(df_eurusd.loc[idx_entrada, "atr"]):
            continue

        fila_entrada = df_eurusd.loc[idx_entrada]
        entrada = float(fila_entrada["close"])
        riesgo = float(fila_entrada["atr"]) * mod.SL_ATR_MULT
        tipo = "venta"  # risk-off en US500 -> dolar refugio -> EURUSD baja, siempre venta
        sl = entrada + riesgo

        salida = None
        for idx in range(idx_entrada + 1, idx_horizonte + 1):
            fila = df_eurusd.loc[idx]
            if fila["high"] >= sl:
                trades.append({
                    "tipo": tipo, "entrada": entrada, "sl": sl, "riesgo": riesgo,
                    "time_entrada": fila_entrada["fecha"], "time_salida": fila["fecha"],
                    "resultado_R": -1.0, "salida": "SL_ATR",
                })
                salida = fila["fecha"]
                break
        if salida is None:
            fila_horizonte = df_eurusd.loc[idx_horizonte]
            cierre_h = float(fila_horizonte["close"])
            resultado_R = (entrada - cierre_h) / riesgo
            trades.append({
                "tipo": tipo, "entrada": entrada, "sl": sl, "riesgo": riesgo,
                "time_entrada": fila_entrada["fecha"], "time_salida": fila_horizonte["fecha"],
                "resultado_R": resultado_R, "salida": "HORIZONTE",
            })
            salida = fila_horizonte["fecha"]

        fin_posicion_abierta = salida

    return pd.DataFrame(trades)


def elegir_mejor_km(df_us500_train, df_eurusd_train, verbose=False):
    std_train = df_us500_train["retorno_h4"].std()
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for k in GRID_K:
        for m in GRID_M:
            td = simular_trades(df_us500_train, df_eurusd_train, k, m, std_train)
            metrica = metrica_robusta_eurusd(td) if not td.empty else float("-inf")
            detalle.append((k, m, len(td), metrica))
            if metrica > mejor_metrica:
                mejor_metrica = metrica
                mejor = (k, m)
    if verbose:
        for k, m, ntr, met in detalle:
            elegible = "OK" if ntr >= MIN_TRADES_SELECCION else f"< piso ({MIN_TRADES_SELECCION})"
            met_str = f"{met:.3f}" if met != float("-inf") else "-inf"
            print(f"    k={k:.2f} M={m:>2} | trades TRAIN: {ntr:>4} ({elegible}) | t-stat R neto: {met_str}")
    return mejor, mejor_metrica, std_train


def _rango_fechas(df):
    return f"{df['fecha'].iloc[0]} -> {df['fecha'].iloc[-1]}"


def correr_fold_macro(df_us500, df_eurusd_train, df_eurusd_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN EURUSD: {len(df_eurusd_train)} velas H4 ({_rango_fechas(df_eurusd_train)}) "
          f"| TEST EURUSD: {len(df_eurusd_test)} velas H4 ({_rango_fechas(df_eurusd_test)})")
    print("=" * 70)

    fecha_corte_train = df_eurusd_train["fecha"].max()
    df_us500_train = df_us500[df_us500["fecha"] <= fecha_corte_train].reset_index(drop=True)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    mejor, metrica_train, std_train = elegir_mejor_km(df_us500_train, df_eurusd_train, verbose=True)
    mejor_k, mejor_m = mejor if mejor is not None else (None, None)

    resultado = {
        "fold": fold_num, "k": None, "m": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor_k is None or metrica_train == float("-inf"):
        print(f"  ❌ Ninguna combinación llegó al piso de {MIN_TRADES_SELECCION} trades en TRAIN.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): k={mejor_k:.2f}, M={mejor_m} "
          f"(t-stat R neto: {metrica_train:.3f}, std_train={std_train:.6f})")

    fecha_fin_test = df_eurusd_test["fecha"].max()
    df_us500_hasta_test = df_us500[df_us500["fecha"] <= fecha_fin_test].reset_index(drop=True)

    df_eurusd_train_test = pd.concat([df_eurusd_train, df_eurusd_test], ignore_index=True)
    td_completo = simular_trades(df_us500_hasta_test, df_eurusd_train_test, mejor_k, mejor_m, std_train)
    fecha_inicio_test = df_eurusd_test["fecha"].min()
    td_test = td_completo[td_completo["time_entrada"] >= fecha_inicio_test].reset_index(drop=True)

    resultado["k"], resultado["m"] = mejor_k, mejor_m
    resultado["td_test"] = td_test

    if td_test.empty:
        print("  TEST (out-of-sample): sin operaciones.")
        return resultado

    n_trades = len(td_test)
    wr = (td_test["resultado_R"] > 0).sum() / n_trades * 100
    r_total = td_test["resultado_R"].sum()
    r_neto = descontar_spread_eurusd(td_test)["resultado_R_neto"].sum()
    rentable = r_neto > 0
    estado = "✅ RENTABLE" if rentable else "❌ pierde"
    print(f"  TEST (out-of-sample) | Trades: {n_trades:<4} | Win rate: {wr:5.1f}% | "
          f"R total: {r_total:+7.2f}R | Neto de spread: {r_neto:+7.2f}R  {estado}")

    resultado.update(n_trades_test=n_trades, wr_test=wr, r_total_test=r_total,
                      r_neto_test=r_neto, rentable=rentable)
    return resultado


def resumen_walk_forward_macro(resultados):
    print("\n" + "#" * 70)
    print("RESUMEN WALK-FORWARD -- Risk-off US500 H4 -> EURUSD (H2, fase 1)")
    print("#" * 70)
    for r in resultados:
        if not r["n_trades_test"]:
            motivo = "sin selección posible en TRAIN" if r["k"] is None else "sin operaciones en TEST"
            print(f"Fold {r['fold']} | {motivo}")
            continue
        estado = "✅ RENTABLE" if r["rentable"] else "❌ pierde"
        print(f"Fold {r['fold']:>2} | k={r['k']:.2f} M={r['m']:>2} | Trades: {r['n_trades_test']:<4} | "
              f"Win rate: {r['wr_test']:5.1f}% | R total: {r['r_total_test']:+7.2f}R | "
              f"Neto spread: {r['r_neto_test']:+7.2f}R  {estado}")
    print("#" * 70)

    validos = [r for r in resultados if r["n_trades_test"]]
    if not validos:
        print("\nNingún fold generó operaciones evaluables en TEST.")
        return validos

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
        if pct_dominante > 60:
            print("⚠️  Un solo fold concentra la mayoría del resultado.")

    return validos


def t_stat_pooled(td, etiqueta):
    r_neto = descontar_spread_eurusd(td)["resultado_R_neto"]
    n = len(r_neto)
    media = r_neto.mean()
    std = r_neto.std(ddof=1)
    t = media / (std / math.sqrt(n))
    p_valor = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    print(f"  [{etiqueta}] n={n} | R_neto medio={media:+.3f} | t-stat={t:+.3f} | p (aprox. normal, dos colas)={p_valor:.4f}")
    return t, p_valor, r_neto


def analisis_pooled_test(validos):
    if not validos:
        return None
    print("\n" + "#" * 70)
    print("t-stat real sobre R neto -- trades TEST agrupados (no conteo de folds)")
    print("#" * 70)
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    _, _, r_neto_todos = t_stat_pooled(todos, f"{len(todos)} trades TEST, los {len(validos)} folds evaluables")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    sin_dominante = pd.concat(
        [r["td_test"] for r in validos if r["fold"] != fold_max["fold"]], ignore_index=True)
    if not sin_dominante.empty:
        t_stat_pooled(sin_dominante, f"{len(sin_dominante)} trades TEST, sin Fold {fold_max['fold']} (el más fuerte)")

    return r_neto_todos


def analisis_dsr(r_neto_todos):
    if r_neto_todos is None or r_neto_todos.empty:
        return
    print("\n" + "#" * 70)
    print(f"Deflated Sharpe Ratio (N={N_VARIANTES_DSR}: esta grilla 3x3x8=72 + versión XAUUSD del mismo driver, 72)")
    print("#" * 70)
    resultado = dsr_mod.deflated_sharpe_ratio(r_neto_todos.values, N_VARIANTES_DSR)
    dsr_mod.reportar(resultado)


def main():
    df_us500 = cargar_us500()
    print(f"US500 H4: {len(df_us500)} filas, {df_us500['fecha'].min()} -> {df_us500['fecha'].max()}\n")

    df_eurusd = bajar_eurusd_h4()
    print(f"EURUSD H4 (MT5): {len(df_eurusd)} velas, {_rango_fechas(df_eurusd)}\n")

    folds_eurusd = mod.construir_bloques_walk_forward(df_eurusd, N_FOLDS)
    resultados = [
        correr_fold_macro(df_us500, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds_eurusd, start=1)
    ]
    validos = resumen_walk_forward_macro(resultados)
    r_neto_todos = analisis_pooled_test(validos)
    analisis_dsr(r_neto_todos)


if __name__ == "__main__":
    main()
