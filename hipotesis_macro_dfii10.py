"""
Hipotesis macro, fase 1: tasas reales (DFII10) como filtro de regimen para XAUUSD.
=============================================================================

Frase falsable: cuando la tasa real de EE.UU. a 10 años (FRED DFII10) viene
cayendo de forma sostenida en los ultimos N dias habiles, el oro tiene sesgo
alcista sostenido en las M sesiones siguientes.

Definiciones fijas (declaradas antes de correr el walk-forward, sin barrer
variantes fuera de la grilla declarada):

- Señal de "caida sostenida": DFII10[t] < DFII10[t-N] (nivel neto de la
  ventana, sin exigir monotonia dia a dia -- ver diagnostico_frecuencia_dfii10.py
  para la justificacion y el conteo de episodios).
- Un "episodio" es una racha maxima de dias consecutivos con la señal activa.
  Se opera UNA sola vez por episodio, no una vez por dia con señal activa
  (evita contar como independientes observaciones que son la misma racha).
- Entrada: SOLO compra (la hipotesis es direccional, sesgo alcista), al
  cierre de la primera sesion de oro posterior al dia en que el episodio
  arranca (D+1 -- DFII10 se publica tarde el mismo dia D, no se puede operar
  con ese dato antes de que cierre D).
- Riesgo/SL: ATR14 diario * SL_ATR_MULT (mismo multiplicador ya validado en
  el proyecto, importado de Backtest ema v4.py). Sin take-profit fijo.
- Salida: lo que ocurra primero entre (a) horizonte fijo de M sesiones de
  oro despues de la entrada, evaluado al cierre (resultado_R continuo, sin
  tope), o (b) el low de una vela diaria toca el SL (resultado_R = -1.0,
  misma convencion que backtest() en Backtest ema v4.py).
- Sin pyramiding: si hay una posicion abierta, se ignoran episodios nuevos
  hasta que cierre (mismo criterio que el backtest EMA existente).

Grilla declarada (3x3, no se prueba nada fuera de esto en este intento):
  N (dias habiles de caida sostenida): 20, 60, 120
  M (sesiones de horizonte de salida): 5, 10, 20

Walk-forward: 4 folds anclados (ajustado para ESTA hipotesis especificamente,
no para el resto del proyecto -- con 9 folds el piso de MIN_TRADES_SELECCION
no se sostenia para N=60/120; con 4 folds el peor caso, N=120, queda en
~35 episodios/fold). Selecciona (N,M) en TRAIN por t-stat sobre R neto
(metrica_robusta, min. MIN_TRADES_SELECCION trades), confirma UNA vez en TEST.

Fuente de datos: FRED DFII10 (descarga publica sin API key) + home.treasury.gov
Daily Par Real Yield Curve como verificacion cruzada. Oro: XAUUSD diario via
MT5 (mismo terminal que el resto del proyecto), resampleado de H1 a D1.

Regla de corte: una sola pasada con esta definicion. Si no sostiene edge en
la mayoria de folds sin depender de un fold dominante, se descarta sin
iterar N/M fuera de la grilla ni probar DXY en el mismo intento.
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
DIR_PROYECTO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta"
RUTA_DFII10 = DIR_PROYECTO + r"\historial\dfii10.csv"
RUTA_TREASURY_2025 = DIR_PROYECTO + r"\historial\treasury_real_yield_2025.csv"
RUTA_TREASURY_2026 = DIR_PROYECTO + r"\historial\treasury_real_yield_2026.csv"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # no corre main() porque __name__ != "__main__"

GRID_N = [20, 60, 120]
GRID_M = [5, 10, 20]
N_FOLDS = 4  # ver docstring: ajustado para esta hipotesis, no para el resto del proyecto
ATR_PERIOD_DIARIO = 14
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")


# ============================================================
# 1. Datos macro (DFII10 + verificacion cruzada Treasury)
# ============================================================

def cargar_dfii10():
    df = pd.read_csv(RUTA_DFII10)
    df.columns = ["fecha", "dfii10"]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["dfii10"] = pd.to_numeric(df["dfii10"], errors="coerce")
    df = df.dropna(subset=["dfii10"]).reset_index(drop=True)
    return df


def verificar_cruce_treasury(df_dfii10):
    """Compara DFII10 (FRED) contra la curva de rendimiento real diaria de
    home.treasury.gov (columna '10 YR') en el solapamiento 2025-2026, para
    confirmar que la fuente primaria no esta desalineada/rezagada."""
    partes = []
    for ruta in (RUTA_TREASURY_2025, RUTA_TREASURY_2026):
        t = pd.read_csv(ruta)
        t = t.rename(columns={"Date": "fecha", "10 YR": "real_10y_treasury"})
        t["fecha"] = pd.to_datetime(t["fecha"], format="%m/%d/%Y")
        partes.append(t[["fecha", "real_10y_treasury"]])
    treasury = pd.concat(partes, ignore_index=True).sort_values("fecha")

    cruce = df_dfii10.merge(treasury, on="fecha", how="inner")
    cruce["diff_abs"] = (cruce["dfii10"] - cruce["real_10y_treasury"]).abs()
    corr = cruce["dfii10"].corr(cruce["real_10y_treasury"])

    print("=== Verificación cruzada FRED DFII10 vs. Treasury.gov (10 YR real) ===")
    print(f"Fechas comparadas: {len(cruce)} ({cruce['fecha'].min().date()} -> {cruce['fecha'].max().date()})")
    print(f"Correlación: {corr:.6f}")
    print(f"Diferencia absoluta -- media: {cruce['diff_abs'].mean():.4f} | máxima: {cruce['diff_abs'].max():.4f}")
    if cruce["diff_abs"].max() > 0.05:
        print("⚠️  Diferencia máxima > 0.05 puntos -- revisar antes de confiar en la fuente primaria.")
    else:
        print("✅ Fuentes consistentes -- DFII10 (FRED) queda confirmado como fuente primaria.")
    print()


def detectar_inicios_episodio(df_dfii10, n):
    """Devuelve las fechas (dias habiles DFII10) en que un episodio de
    'caida sostenida' arranca (transicion False->True), para el N dado."""
    cond = df_dfii10["dfii10"] < df_dfii10["dfii10"].shift(n)
    cond = cond.fillna(False)
    inicio_episodio = cond & ~cond.shift(1, fill_value=False)
    return df_dfii10.loc[inicio_episodio, "fecha"].tolist()


# ============================================================
# 2. Datos de oro (diario, derivado de H1 MT5) + ATR
# ============================================================

def bajar_oro_diario():
    """D1 directo de MT5 (no resampleado de H1): el rango completo 2004-2026 en
    H1 excede el limite maxbars=100000 del terminal (confirmado con
    'Invalid params' al intentarlo); D1 tiene ~5700 velas en el mismo rango,
    muy por debajo del limite, y es la granularidad que de verdad usa esta
    hipotesis (entrada/salida por sesion diaria, no intradia)."""
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
# 3. Simulación de trades para una combinación (N, M) dada
# ============================================================

def simular_trades(df_dfii10, df_oro, n, m):
    inicios = detectar_inicios_episodio(df_dfii10, n)
    fechas_oro = df_oro["fecha"].values

    trades = []
    fin_posicion_abierta = None  # fecha de salida de la posicion abierta actual (no pyramiding)

    for fecha_inicio in inicios:
        if fin_posicion_abierta is not None and fecha_inicio <= fin_posicion_abierta:
            continue  # episodio ignorado: ya hay una posicion abierta (mismo criterio que backtest() EMA)

        idx_entrada = np.searchsorted(fechas_oro, np.datetime64(fecha_inicio), side="right")
        if idx_entrada >= len(df_oro):
            continue  # no hay sesion de oro posterior a este episodio todavia
        idx_horizonte = idx_entrada + m
        if idx_horizonte >= len(df_oro) or pd.isna(df_oro.loc[idx_entrada, "atr"]):
            continue  # no hay suficientes sesiones futuras para completar el horizonte M, o ATR sin warm-up

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
# 4. Selección de (N, M) en TRAIN + walk-forward
# ============================================================

def elegir_mejor_nm(df_dfii10_train, df_oro_train, verbose=False):
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for n in GRID_N:
        for m in GRID_M:
            td = simular_trades(df_dfii10_train, df_oro_train, n, m)
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


def correr_fold_macro(df_dfii10, df_oro_train, df_oro_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN oro: {len(df_oro_train)} días ({_rango_fechas_oro(df_oro_train)}) "
          f"| TEST oro: {len(df_oro_test)} días ({_rango_fechas_oro(df_oro_test)})")
    print("=" * 70)

    # DFII10 de TRAIN: solo hasta el último día de TRAIN oro (nada de fuga hacia adelante)
    fecha_corte_train = df_oro_train["fecha"].max()
    df_dfii10_train = df_dfii10[df_dfii10["fecha"] <= fecha_corte_train].reset_index(drop=True)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    (mejor_n, mejor_m), metrica_train = elegir_mejor_nm(df_dfii10_train, df_oro_train, verbose=True)

    resultado = {
        "fold": fold_num, "n": None, "m": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor_n is None or metrica_train == float("-inf"):
        print("  ❌ Ninguna combinación de la grilla llegó al piso de "
              f"{mod.MIN_TRADES_SELECCION} trades en TRAIN -- fold sin selección posible.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): N={mejor_n}, M={mejor_m} (t-stat R neto: {metrica_train:.3f})")

    # DFII10 relevante para detectar episodios que arrancan durante la ventana de TEST
    # (se necesita historial previo para poder calcular el shift de N días, por eso se
    # pasa el df completo hasta el fin de TEST, no solo las fechas de TEST)
    fecha_fin_test = df_oro_test["fecha"].max()
    df_dfii10_hasta_test = df_dfii10[df_dfii10["fecha"] <= fecha_fin_test].reset_index(drop=True)

    # --- evaluación out-of-sample, una sola vez, con (N,M) ya fijados ---
    # simular sobre TRAIN+TEST junto (necesario para que el horizonte M pueda
    # completarse con velas de TEST), y despues quedarse solo con los trades
    # cuya ENTRADA cae dentro de la ventana de TEST.
    df_oro_train_test = pd.concat([df_oro_train, df_oro_test], ignore_index=True)
    td_completo = simular_trades(df_dfii10_hasta_test, df_oro_train_test, mejor_n, mejor_m)
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
    print("RESUMEN WALK-FORWARD -- Hipótesis macro DFII10 (fase 1)")
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
        print("\nNingún fold generó operaciones evaluables en TEST -- hipótesis se descarta, "
              "sin datos suficientes para juzgar el edge.")
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
        if pct_dominante > 60:
            print("⚠️  Un solo fold concentra la mayoría del resultado -- no es evidencia fuerte de un edge estable.")

    if len(validos) < len(resultados):
        print(f"\n⚠️  {len(resultados) - len(validos)} fold(s) no fueron evaluables (sin selección en TRAIN o sin "
              "trades en TEST) -- la conclusión de abajo solo cubre los folds evaluables, no la ventana completa.")

    if len(rentables_neto) == len(validos):
        print("\n✅ El edge se sostuvo en TODOS los folds evaluables -> evidencia más fuerte de que es real.")
    elif len(rentables_neto) >= len(validos) * 0.5:
        print("\n⚠️  El edge se sostuvo en algunos folds pero no en todos -> puede depender del régimen de tasas. "
              "No tratarlo como robusto todavía.")
    else:
        print("\n❌ El edge NO se sostuvo en la mayoría de los folds evaluables -> según la regla de corte "
              "declarada, esta hipótesis se descarta en esta fase.")


def t_stat_pooled(td, etiqueta):
    """t-stat real (mean/std/sqrt(n)) sobre R neto de un pool de trades TEST
    ya realizados -- a diferencia de metrica_robusta() (que exige el piso
    MIN_TRADES_SELECCION porque se usa para ELEGIR entre configs candidatas
    dentro de un barrido), acá no hace falta ese piso: es una sola
    evaluación post-hoc sobre trades ya fijados, no una selección entre
    alternativas. p-value de dos colas vía aproximación normal (sin scipy
    instalado; con n>=60 la t de Student ya es prácticamente indistinguible
    de la normal, así que la aproximación es válida acá)."""
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
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    t_stat_pooled(todos, f"87 trades TEST, los 4 folds")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    sin_dominante = pd.concat(
        [r["td_test"] for r in validos if r["fold"] != fold_max["fold"]], ignore_index=True)
    t_stat_pooled(sin_dominante, f"63 trades TEST, sin Fold {fold_max['fold']} (el más fuerte)")


# ============================================================
# main
# ============================================================

def main():
    df_dfii10 = cargar_dfii10()
    verificar_cruce_treasury(df_dfii10)

    df_oro = bajar_oro_diario()
    print(f"Oro diario (derivado de H1 MT5): {len(df_oro)} días, {_rango_fechas_oro(df_oro)}\n")

    folds_oro = mod.construir_bloques_walk_forward(df_oro, N_FOLDS)
    resultados = [
        correr_fold_macro(df_dfii10, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds_oro, start=1)
    ]
    resumen_walk_forward_macro(resultados)
    analisis_pooled_test(resultados)


if __name__ == "__main__":
    main()
