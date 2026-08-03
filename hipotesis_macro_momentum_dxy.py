"""
Hipotesis macro, fase 1: momentum DXY de muy corto plazo (1 dia) como señal
direccional para XAUUSD.
=============================================================================

Frase falsable (ficha hypothesis-gate, aprobada antes de este codigo):
cuando el retorno diario del DXY sintetico supera k desvios estandar
(calculado sobre su propia distribucion historica) en valor absoluto, el
oro tiene sesgo direccional INVERSO al signo del movimiento del dolar
(DXY sube -> oro sesgo bajista / venta; DXY baja -> oro sesgo alcista /
compra) en las M sesiones siguientes.

Distinto de la hipotesis DXY ya descartada (nivel/caida sostenida a
N=20/60/120 dias) -- esta mide el RETORNO de 1 dia, no el nivel. Comparte
la fuente de datos (dxy_sintetico.csv) pero es un diseño de señal nuevo,
nunca antes barrido.

Definiciones fijas (declaradas antes de correr el walk-forward):

- Señal: |retorno_1d(DXY sintetico)| > k * std(retorno_1d). El std usado
  para el umbral es el std calculado SOLO sobre el TRAIN de cada fold
  (congelado en la fecha de corte de TRAIN, igual que N/M se seleccionan
  en TRAIN) -- NO el std del historico completo. Esto es una decision de
  diseño que la ficha de hypothesis-gate no cerro explicitamente: usar el
  std global (con datos futuros) para definir el umbral operativo en
  folds tempranos seria look-ahead sutil (el mismo tipo de fuga que ya
  se audito para DFII10, aunque de una naturaleza distinta -- acá es el
  PARAMETRO del umbral, no el dato de la señal en si). Se resuelve igual
  que el resto del proyecto resuelve la seleccion de hiperparametros:
  todo lo que se "conoce" para operar en TEST viene de TRAIN, sin excepcion.
- Un "episodio" es una racha maxima de dias consecutivos con la señal
  activa. Se opera UNA sola vez por episodio (mismo criterio DFII10).
- Direccion: VENTA si el retorno que dispara el episodio es positivo
  (dolar sube), COMPRA si es negativo (dolar baja) -- fijada por la frase
  falsable, no elegida por el barrido (no es un parametro de la grilla).
- Entrada: al cierre de la primera sesion de oro posterior al dia en que
  el episodio arranca (D+1, mismo criterio DFII10 -- evita operar con
  informacion del mismo dia D antes de que cierre).
- Riesgo/SL: ATR14 diario * SL_ATR_MULT (constante ya validada del
  proyecto, importada de Backtest ema v4.py). Sin take-profit fijo.
- Salida: lo que ocurra primero entre (a) horizonte fijo de M sesiones,
  evaluado al cierre (resultado_R continuo), o (b) el SL tocado por una
  vela diaria (resultado_R = -1.0).
- Sin pyramiding.

Grilla declarada (2x3, NO se prueba nada fuera de esto -- N=1 dia ya
quedo fijado en el triage de frecuencia, no se resweepea):
  k (desvios estandar del retorno 1d): 0.75, 1.0
  M (sesiones de horizonte de salida): 1, 3, 5

Walk-forward: 16 folds anclados (derivados en el chequeo de distribucion
temporal de episodios -- min. 43 trades/fold, ~43% de margen sobre el
piso de 30; el maximo mecanico K=18 se descarto por margen cero, ver
distribucion_folds_momentum_dxy.py). Selecciona (k,M) en TRAIN por
t-stat sobre R neto (metrica_robusta, min. MIN_TRADES_SELECCION trades),
confirma UNA sola vez en TEST.

Regla de corte (fijada de antemano, ficha hypothesis-gate):
- t-stat |t| > 1.96 sobre R neto pooled de TEST, con y sin el fold de
  mayor R neto -- la conclusion cualitativa no puede cambiar entre ambos.
- Piso de 30 trades por fold.
- R neto de spread real (SPREAD_PUNTOS=30, misma constante de todo el
  proyecto, via descontar_spread).
- Sin iterar la grilla ni el diseño de señal fuera de lo declarado arriba
  una vez visto el resultado -- el resultado es el resultado.
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
DIR_PROYECTO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta"
RUTA_DXY = DIR_PROYECTO + r"\historial\dxy_sintetico.csv"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # no corre main() porque __name__ != "__main__"

GRID_K = [0.75, 1.0]
GRID_M = [1, 3, 5]
N_FOLDS = 16  # derivado en distribucion_folds_momentum_dxy.py -- min 43 trades/fold
ATR_PERIOD_DIARIO = 14
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")


# ============================================================
# 1. Datos DXY sintetico
# ============================================================

def cargar_dxy():
    df = pd.read_csv(RUTA_DXY).rename(columns={"time": "fecha"})
    df["fecha"] = pd.to_datetime(df["fecha"])
    df = df[df["fecha"] >= INICIO_DATOS_ORO_MT5].reset_index(drop=True)
    df["retorno_1d"] = df["dxy_sintetico"].pct_change(1)
    return df


def detectar_inicios_episodio(df_dxy, k, std_congelado):
    """Devuelve lista de (fecha_inicio, signo_retorno) para cada episodio.
    std_congelado viene de TRAIN -- nunca se recalcula con datos de TEST."""
    cond = (df_dxy["retorno_1d"].abs() > k * std_congelado).fillna(False)
    inicio_episodio = cond & ~cond.shift(1, fill_value=False)
    sub = df_dxy.loc[inicio_episodio, ["fecha", "retorno_1d"]]
    return list(zip(sub["fecha"], np.sign(sub["retorno_1d"])))


# ============================================================
# 2. Datos de oro (diario, MT5) + ATR
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
# 3. Simulacion de trades para una combinacion (k, M) dada
# ============================================================

def simular_trades(df_dxy_ref, df_oro, k, m, std_congelado):
    inicios = detectar_inicios_episodio(df_dxy_ref, k, std_congelado)
    fechas_oro = df_oro["fecha"].values

    trades = []
    fin_posicion_abierta = None

    for fecha_inicio, signo in inicios:
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
        tipo = "venta" if signo > 0 else "compra"  # DXY sube -> venta oro; DXY baja -> compra oro
        sl = entrada - riesgo if tipo == "compra" else entrada + riesgo

        salida = None
        for idx in range(idx_entrada + 1, idx_horizonte + 1):
            fila = df_oro.loc[idx]
            toco_sl = (fila["low"] <= sl) if tipo == "compra" else (fila["high"] >= sl)
            if toco_sl:
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
            resultado_R = (cierre_h - entrada) / riesgo if tipo == "compra" else (entrada - cierre_h) / riesgo
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

def elegir_mejor_km(df_dxy_train, df_oro_train, verbose=False):
    std_train = df_dxy_train["retorno_1d"].std()
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for k in GRID_K:
        for m in GRID_M:
            td = simular_trades(df_dxy_train, df_oro_train, k, m, std_train)
            metrica = mod.metrica_robusta(td) if not td.empty else float("-inf")
            detalle.append((k, m, len(td), metrica))
            if metrica > mejor_metrica:
                mejor_metrica = metrica
                mejor = (k, m)
    if verbose:
        for k, m, ntr, met in detalle:
            elegible = "OK" if ntr >= mod.MIN_TRADES_SELECCION else f"< piso ({mod.MIN_TRADES_SELECCION})"
            met_str = f"{met:.3f}" if met != float("-inf") else "-inf"
            print(f"    k={k:.2f} M={m:>2} | trades TRAIN: {ntr:>3} ({elegible}) | t-stat R neto: {met_str}")
    return mejor, mejor_metrica, std_train


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
    (mejor_k, mejor_m), metrica_train, std_train = elegir_mejor_km(df_dxy_train, df_oro_train, verbose=True)

    resultado = {
        "fold": fold_num, "k": None, "m": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor_k is None or metrica_train == float("-inf"):
        print("  ❌ Ninguna combinación de la grilla llegó al piso de "
              f"{mod.MIN_TRADES_SELECCION} trades en TRAIN -- fold sin selección posible.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): k={mejor_k:.2f}, M={mejor_m} "
          f"(t-stat R neto: {metrica_train:.3f}, std_train retorno_1d={std_train:.5f})")

    fecha_fin_test = df_oro_test["fecha"].max()
    df_dxy_hasta_test = df_dxy[df_dxy["fecha"] <= fecha_fin_test].reset_index(drop=True)

    # Evaluacion out-of-sample, UNA sola vez, con (k,M) ya fijados y el
    # std CONGELADO de TRAIN (no se recalcula con datos de TEST).
    df_oro_train_test = pd.concat([df_oro_train, df_oro_test], ignore_index=True)
    td_completo = simular_trades(df_dxy_hasta_test, df_oro_train_test, mejor_k, mejor_m, std_train)
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
    print(f"  TEST (out-of-sample) | Trades: {n_trades:<3} | Win rate: {wr:5.1f}% | "
          f"R total: {r_total:+7.2f}R | Neto de spread: {r_neto:+7.2f}R  {estado}")

    resultado.update(n_trades_test=n_trades, wr_test=wr, r_total_test=r_total,
                      r_neto_test=r_neto, rentable=rentable)
    return resultado


def resumen_walk_forward_macro(resultados):
    print("\n" + "#" * 70)
    print("RESUMEN WALK-FORWARD -- Hipótesis macro Momentum DXY (fase 1)")
    print("#" * 70)
    for r in resultados:
        if not r["n_trades_test"]:
            motivo = "sin selección posible en TRAIN" if r["k"] is None else "sin operaciones en TEST"
            print(f"Fold {r['fold']} | {motivo}")
            continue
        estado = "✅ RENTABLE" if r["rentable"] else "❌ pierde"
        print(f"Fold {r['fold']:>2} | k={r['k']:.2f} M={r['m']:>2} | Trades: {r['n_trades_test']:<3} | "
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
    return t, p_valor


def analisis_pooled_test(validos):
    if not validos:
        return
    print("\n" + "#" * 70)
    print("t-stat real sobre R neto -- trades TEST agrupados (no conteo de folds)")
    print("#" * 70)
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    t_stat_pooled(todos, f"{len(todos)} trades TEST, los {len(validos)} folds evaluables")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    sin_dominante = pd.concat(
        [r["td_test"] for r in validos if r["fold"] != fold_max["fold"]], ignore_index=True)
    if not sin_dominante.empty:
        t_stat_pooled(sin_dominante, f"{len(sin_dominante)} trades TEST, sin Fold {fold_max['fold']} (el más fuerte)")


# ============================================================
# main
# ============================================================

def main():
    df_dxy = cargar_dxy()
    print(f"DXY sintético: {len(df_dxy)} filas, "
          f"{df_dxy['fecha'].min().date()} -> {df_dxy['fecha'].max().date()}\n")

    df_oro = bajar_oro_diario()
    print(f"Oro diario (MT5): {len(df_oro)} días, {_rango_fechas_oro(df_oro)}\n")

    folds_oro = mod.construir_bloques_walk_forward(df_oro, N_FOLDS)
    resultados = [
        correr_fold_macro(df_dxy, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds_oro, start=1)
    ]
    validos = resumen_walk_forward_macro(resultados)
    analisis_pooled_test(validos)


if __name__ == "__main__":
    main()
