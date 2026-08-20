"""
Hipotesis macro H4, fase 1: risk-off en renta variable (US500) como señal
direccional de refugio para XAUUSD.
=============================================================================
Tercer candidato de la ronda intradia (2026-08-04) y primer driver externo
distinto de DXY -- ver ficha completa en "Risk-off US500 H4 - fase 1.md"
(vault) y Bitácora de decisiones.md.

Frase falsable (ficha hypothesis-gate, aprobada antes de este codigo):
cuando el retorno del US500 en la vela H4 cerrada CAE mas de k desvios
estandar de su propia distribucion historica en valor absoluto (solo
caidas cuentan -- direccional por diseño, una suba de US500 no es la
condicion testeada), el oro (XAUUSD) tiene sesgo ALCISTA en las M velas H4
siguientes.

Nota sobre el std del umbral: la ficha describe el chequeo de Fase 0 con
el std de la serie completa (mismo patron que los demas diagnosticos de
frecuencia, que solo cuentan episodios, no operan nada). Para el
WALK-FORWARD real se aplica la misma disciplina que TODAS las demas
hipotesis de este proyecto (incluida la version original de Momentum DXY
diario): el std usado para el umbral operativo se calcula SOLO sobre el
TRAIN de cada fold y se congela para evaluar TRAIN+TEST -- usar el std de
la serie completa (con datos futuros) para operar en folds tempranos
seria look-ahead sutil sobre el parametro, el mismo tipo de fuga que el
proyecto ya audito y corrigio para la version diaria de Momentum DXY.

A diferencia de los candidatos DXY (direccion determinada por el signo
del retorno disparador), acá la direccion es SIEMPRE COMPRA -- fijada por
la frase falsable, no un parametro de la grilla.

Definiciones fijas:

- Señal: retorno_H4(US500) < -k * std_train(retorno_H4). Un "episodio" es
  una racha maxima de velas H4 consecutivas con la señal activa. Se opera
  UNA sola vez por episodio.
- Entrada: al cierre de la primera vela H4 de oro posterior a la vela H4
  en que el episodio arranca (D+1, mismo criterio del resto del proyecto).
- Riesgo/SL: ATR14 en H4 (oro) * SL_ATR_MULT. Sin take-profit fijo.
- Salida: lo que ocurra primero entre (a) horizonte fijo de M velas H4 al
  cierre, o (b) el SL tocado por una vela H4 (resultado_R = -1.0).
- Sin pyramiding.

Grilla declarada (3x3, NO se prueba nada fuera de esto):
  k (desvios estandar del retorno H4 de US500): 0.75, 1.0, 1.25
  M (velas H4 de horizonte de salida): 1, 2, 3

Walk-forward: 8 folds anclados (derivados del chequeo de distribucion real
de episodios sobre 14.0 años de historia de US500 -- fold minimo real de
36 trades, +20% de margen sobre el piso de 30; K=10 ya deja solo +7%,
K=12 llega justo al piso, K=14+ lo rompe).

Regla de corte (fijada de antemano, ficha hypothesis-gate):
- t-stat |t| > 1.96 sobre R neto pooled de TEST, con y sin el fold de
  mayor R neto -- la conclusion cualitativa no puede cambiar entre ambos.
- DSR >= 0.95, N = esta grilla (3x3x8=24) -- sin sumar hermanas de DXY o
  credito: el driver (renta variable) es nuevo en este proyecto.
- Piso de 30 trades por fold (seleccion en TRAIN).
- R neto de spread real (SPREAD_PUNTOS=30).
- Sin iterar la grilla ni el diseño de señal fuera de lo declarado arriba
  una vez visto el resultado.
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
N_FOLDS = 8  # derivado de la distribucion real -- min 36 trades/fold, +20%
ATR_PERIOD_H4 = 14
INICIO_US500 = pd.Timestamp("2012-08-06")  # historia real del broker, no limite de pipeline
N_VARIANTES_DSR = 3 * 3 * N_FOLDS  # 24 -- driver nuevo, sin hermanas que sumar


# ============================================================
# 1. Datos US500 H4
# ============================================================

def cargar_us500():
    df = pd.read_csv(RUTA_US500).rename(columns={"time": "fecha"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df[df["fecha"] >= INICIO_US500].reset_index(drop=True)
    df["retorno_h4"] = df["close"].pct_change(1)
    return df


def detectar_inicios_episodio(df_us500, k, std_congelado):
    """std_congelado viene de TRAIN -- nunca se recalcula con datos de TEST.
    Direccional: SOLO caidas (retorno negativo mas alla del umbral) cuentan."""
    cond = (df_us500["retorno_h4"] < -k * std_congelado).fillna(False)
    inicio_episodio = cond & ~cond.shift(1, fill_value=False)
    return list(df_us500.loc[inicio_episodio, "fecha"])


# ============================================================
# 2. Datos de oro H4 (MT5) + ATR14 H4
# ============================================================

def bajar_oro_h4():
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()
    h4 = mod.bajar_datos_rango(mod.SYMBOL, mod.mt5.TIMEFRAME_H4, INICIO_US500, ahora)
    h4 = h4.rename(columns={"time": "fecha"})

    high_low = h4["high"] - h4["low"]
    high_close = (h4["high"] - h4["close"].shift()).abs()
    low_close = (h4["low"] - h4["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    h4["atr"] = tr.rolling(ATR_PERIOD_H4).mean()

    return h4.reset_index(drop=True)


# ============================================================
# 3. Simulacion de trades para una combinacion (k, M) dada
# ============================================================

def simular_trades(df_us500_ref, df_oro, k, m, std_congelado):
    inicios = detectar_inicios_episodio(df_us500_ref, k, std_congelado)
    fechas_oro = df_oro["fecha"].values

    trades = []
    fin_posicion_abierta = None

    for fecha_inicio in inicios:
        if fin_posicion_abierta is not None and fecha_inicio <= fin_posicion_abierta:
            continue  # ya hay posicion abierta -- sin pyramiding

        idx_entrada = np.searchsorted(fechas_oro, np.datetime64(fecha_inicio), side="right")
        if idx_entrada >= len(df_oro):
            continue
        idx_horizonte = idx_entrada + m
        if idx_horizonte >= len(df_oro) or pd.isna(df_oro.loc[idx_entrada, "atr"]):
            continue

        fila_entrada = df_oro.loc[idx_entrada]
        entrada = float(fila_entrada["close"])
        riesgo = float(fila_entrada["atr"]) * mod.SL_ATR_MULT
        tipo = "compra"  # risk-off en US500 -> refugio en oro, siempre compra
        sl = entrada - riesgo

        salida = None
        for idx in range(idx_entrada + 1, idx_horizonte + 1):
            fila = df_oro.loc[idx]
            if fila["low"] <= sl:
                trades.append({
                    "tipo": tipo, "entrada": entrada, "sl": sl, "riesgo": riesgo,
                    "time_entrada": fila_entrada["fecha"], "time_salida": fila["fecha"],
                    "resultado_R": -1.0, "salida": "SL_ATR",
                })
                salida = fila["fecha"]
                break
        if salida is None:
            fila_horizonte = df_oro.loc[idx_horizonte]
            cierre_h = float(fila_horizonte["close"])
            resultado_R = (cierre_h - entrada) / riesgo
            trades.append({
                "tipo": tipo, "entrada": entrada, "sl": sl, "riesgo": riesgo,
                "time_entrada": fila_entrada["fecha"], "time_salida": fila_horizonte["fecha"],
                "resultado_R": resultado_R, "salida": "HORIZONTE",
            })
            salida = fila_horizonte["fecha"]

        fin_posicion_abierta = salida

    return pd.DataFrame(trades)


# ============================================================
# 4. Seleccion de (k, M) en TRAIN + walk-forward
# ============================================================

def elegir_mejor_km(df_us500_train, df_oro_train, verbose=False):
    std_train = df_us500_train["retorno_h4"].std()
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for k in GRID_K:
        for m in GRID_M:
            td = simular_trades(df_us500_train, df_oro_train, k, m, std_train)
            metrica = mod.metrica_robusta(td) if not td.empty else float("-inf")
            detalle.append((k, m, len(td), metrica))
            if metrica > mejor_metrica:
                mejor_metrica = metrica
                mejor = (k, m)
    if verbose:
        for k, m, ntr, met in detalle:
            elegible = "OK" if ntr >= mod.MIN_TRADES_SELECCION else f"< piso ({mod.MIN_TRADES_SELECCION})"
            met_str = f"{met:.3f}" if met != float("-inf") else "-inf"
            print(f"    k={k:.2f} M={m:>2} | trades TRAIN: {ntr:>4} ({elegible}) | t-stat R neto: {met_str}")
    return mejor, mejor_metrica, std_train


def _rango_fechas_oro(df):
    return f"{df['fecha'].iloc[0]} -> {df['fecha'].iloc[-1]}"


def correr_fold_macro(df_us500, df_oro_train, df_oro_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN oro: {len(df_oro_train)} velas H4 ({_rango_fechas_oro(df_oro_train)}) "
          f"| TEST oro: {len(df_oro_test)} velas H4 ({_rango_fechas_oro(df_oro_test)})")
    print("=" * 70)

    fecha_corte_train = df_oro_train["fecha"].max()
    df_us500_train = df_us500[df_us500["fecha"] <= fecha_corte_train].reset_index(drop=True)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    mejor, metrica_train, std_train = elegir_mejor_km(df_us500_train, df_oro_train, verbose=True)
    mejor_k, mejor_m = mejor if mejor is not None else (None, None)

    resultado = {
        "fold": fold_num, "k": None, "m": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor_k is None or metrica_train == float("-inf"):
        print("  ❌ Ninguna combinación de la grilla llegó al piso de "
              f"{mod.MIN_TRADES_SELECCION} trades en TRAIN -- fold sin selección posible.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): k={mejor_k:.2f}, M={mejor_m} "
          f"(t-stat R neto: {metrica_train:.3f}, std_train={std_train:.6f})")

    fecha_fin_test = df_oro_test["fecha"].max()
    df_us500_hasta_test = df_us500[df_us500["fecha"] <= fecha_fin_test].reset_index(drop=True)

    df_oro_train_test = pd.concat([df_oro_train, df_oro_test], ignore_index=True)
    td_completo = simular_trades(df_us500_hasta_test, df_oro_train_test, mejor_k, mejor_m, std_train)
    fecha_inicio_test = df_oro_test["fecha"].min()
    td_test = td_completo[td_completo["time_entrada"] >= fecha_inicio_test].reset_index(drop=True)

    resultado["k"], resultado["m"] = mejor_k, mejor_m
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
    print(f"  TEST (out-of-sample) | Trades: {n_trades:<4} | Win rate: {wr:5.1f}% | "
          f"R total: {r_total:+7.2f}R | Neto de spread: {r_neto:+7.2f}R  {estado}")

    resultado.update(n_trades_test=n_trades, wr_test=wr, r_total_test=r_total,
                      r_neto_test=r_neto, rentable=rentable)
    return resultado


def resumen_walk_forward_macro(resultados):
    print("\n" + "#" * 70)
    print("RESUMEN WALK-FORWARD -- Hipótesis Risk-off US500 H4 (fase 1)")
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
        print("\nNingún fold generó operaciones evaluables en TEST -- hipótesis se descarta, "
              "sin datos suficientes para juzgar el edge.")
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
            print("⚠️  Un solo fold concentra la mayoría del resultado -- no es evidencia fuerte de un edge estable.")

    if len(validos) < len(resultados):
        print(f"\n⚠️  {len(resultados) - len(validos)} fold(s) no fueron evaluables -- la conclusión de abajo "
              "solo cubre los folds evaluables, no la ventana completa.")

    if len(rentables_neto) == len(validos):
        print("\n✅ El edge se sostuvo en TODOS los folds evaluables -> evidencia más fuerte de que es real.")
    elif len(rentables_neto) >= len(validos) * 0.5:
        print("\n⚠️  El edge se sostuvo en algunos folds pero no en todos -> puede depender del régimen. "
              "No tratarlo como robusto todavía.")
    else:
        print("\n❌ El edge NO se sostuvo en la mayoría de los folds evaluables -> según la regla de corte "
              "declarada, esta hipótesis se descarta en esta fase.")

    return validos


def t_stat_pooled(td, etiqueta):
    r_neto = mod.descontar_spread(td)["resultado_R_neto"]
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
    print(f"Deflated Sharpe Ratio (N={N_VARIANTES_DSR} variantes: grilla 3x3x{N_FOLDS} -- "
          f"driver nuevo, sin hermanas)")
    print("#" * 70)
    resultado = dsr_mod.deflated_sharpe_ratio(r_neto_todos.values, N_VARIANTES_DSR)
    dsr_mod.reportar(resultado)


# ============================================================
# main
# ============================================================

def main():
    df_us500 = cargar_us500()
    print(f"US500 H4: {len(df_us500)} filas, "
          f"{df_us500['fecha'].min()} -> {df_us500['fecha'].max()}\n")

    df_oro = bajar_oro_h4()
    print(f"Oro H4 (MT5): {len(df_oro)} velas, {_rango_fechas_oro(df_oro)}\n")

    folds_oro = mod.construir_bloques_walk_forward(df_oro, N_FOLDS)
    resultados = [
        correr_fold_macro(df_us500, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds_oro, start=1)
    ]
    validos = resumen_walk_forward_macro(resultados)
    r_neto_todos = analisis_pooled_test(validos)
    analisis_dsr(r_neto_todos)


if __name__ == "__main__":
    main()
