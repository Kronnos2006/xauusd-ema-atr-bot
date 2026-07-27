"""
Hipotesis macro, fase 1: ratio oro/plata (XAUUSD/XAGUSD) como señal de
mean-reversion direccional en oro.
=============================================================================

Frase falsable: cuando el ratio XAUUSD/XAGUSD se aleja mas de X desvios
estandar de su propia media movil de Y dias habiles, el oro tiene sesgo
direccional OPUESTO al signo del z-score en las Z sesiones siguientes
(z > +X: oro caro relativo a la plata -> sesgo BAJISTA; z < -X: oro barato
relativo a la plata -> sesgo ALCISTA).

Definiciones fijas (declaradas antes de correr el walk-forward, sin barrer
variantes fuera de la grilla declarada):

- z[t] = (ratio[t] - media_movil_Y[t]) / std_movil_Y[t], ventana rolling
  con min_periods=Y (sin fuga hacia adelante: z de hoy solo usa datos
  hasta hoy).
- Un "episodio" es una racha maxima de dias consecutivos con |z[t]| > X.
  Se opera UNA sola vez por episodio (mismo criterio que DFII10/2s10s).
- Direccion: VENTA si z[t] > +X al inicio del episodio, COMPRA si
  z[t] < -X. A diferencia de DFII10/2s10s (solo compra), esta hipotesis
  es bidireccional por construccion (mean-reversion en ambos extremos).
- Entrada: al cierre de la primera sesion de oro posterior al dia en que
  el episodio arranca (D+1 -- mismo criterio que DFII10, el z-score de
  hoy recien se conoce al cierre de hoy).
- Riesgo/SL: ATR14 diario * SL_ATR_MULT (mismo multiplicador ya validado
  en el proyecto). Sin take-profit fijo.
- Salida: lo que ocurra primero entre (a) horizonte fijo de Z sesiones de
  oro despues de la entrada, evaluado al cierre (resultado_R continuo), o
  (b) el SL tocado por el lado correspondiente (low<=sl en compra,
  high>=sl en venta; resultado_R=-1.0, misma convencion que el resto del
  proyecto).
- Sin pyramiding: si hay una posicion abierta (de cualquier direccion),
  se ignoran episodios nuevos hasta que cierre.

Grilla declarada (3x2x3 = 18 combinaciones, mas ancha que la 3x3 de DFII10
porque suma el umbral X -- documentado explicitamente, no oculto: el
umbral (X) es un grado de libertad nuevo que DFII10 no tenia. Se acoto a
solo 2 valores de X para no ampliar demasiado el riesgo de comparaciones
multiples):
  Y (dias habiles de la media movil del ratio): 20, 60, 120
  X (umbral en desvios estandar): 1.5, 2.0
  Z (sesiones de horizonte de salida): 5, 10, 20

Walk-forward: 4 folds anclados -- mismo N_FOLDS que DFII10 (no copiado a
ciegas: se derivo comparando la frecuencia de este chequeo, 106-425
episodios en 17.7 años / 6-24 por año, contra la de DFII10 en su momento,
132-291 episodios en >20 años / ~6-14 por año -- orden de magnitud
comparable o mejor, ver diagnostico_frecuencia_ratio_oro_plata.py).

Fuente de datos: XAUUSD y XAGUSD diario via MT5 (mismo terminal que el
resto del proyecto), ambos derivados de D1 nativo (no resampleado de H1).

Regla de corte: una sola pasada con esta definicion. Si no sostiene edge
en la mayoria de folds sin depender de un fold dominante, se descarta sin
iterar Y/X/Z fuera de la grilla.
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # no corre main() porque __name__ != "__main__"

GRID_Y = [20, 60, 120]
GRID_X = [1.5, 2.0]
GRID_Z = [5, 10, 20]
N_FOLDS = 4  # ver docstring: derivado por comparacion de frecuencia con DFII10, no copiado a ciegas
ATR_PERIOD_DIARIO = 14


# ============================================================
# 1. Datos: XAUUSD (OHLC+ATR) + XAGUSD (close), alineados, + ratio
# ============================================================

def bajar_datos_ratio():
    mod.conectar_mt5()
    ahora = pd.Timestamp.now()
    inicio = pd.Timestamp("2004-01-01")  # amplio; el inner join recorta al solapamiento real

    oro = mod.bajar_datos_rango(mod.SYMBOL, mod.mt5.TIMEFRAME_D1, inicio, ahora)
    plata = mod.bajar_datos_rango("XAGUSD", mod.mt5.TIMEFRAME_D1, inicio, ahora)

    oro = oro.rename(columns={"time": "fecha"})
    oro["fecha"] = oro["fecha"].dt.normalize()
    plata = plata.rename(columns={"time": "fecha", "close": "plata_close"})
    plata["fecha"] = plata["fecha"].dt.normalize()

    high_low = oro["high"] - oro["low"]
    high_close = (oro["high"] - oro["close"].shift()).abs()
    low_close = (oro["low"] - oro["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    oro["atr"] = tr.rolling(ATR_PERIOD_DIARIO).mean()

    df = oro.merge(plata[["fecha", "plata_close"]], on="fecha", how="inner").sort_values("fecha").reset_index(drop=True)
    df["ratio"] = df["close"] / df["plata_close"]

    # z-score por cada Y de la grilla, precalculado UNA vez sobre la serie completa
    # (rolling hacia atras -- z[t] solo usa datos hasta t, ninguna fuga hacia
    # adelante entre folds, mismo principio que el ATR ya precalculado del resto
    # del proyecto).
    for y in GRID_Y:
        media = df["ratio"].rolling(y, min_periods=y).mean()
        std = df["ratio"].rolling(y, min_periods=y).std()
        df[f"z_{y}"] = (df["ratio"] - media) / std

    return df.reset_index(drop=True)


# ============================================================
# 2. Deteccion de episodios (por Y, X) + simulacion de trades
# ============================================================

def detectar_inicios_episodio_ratio(df, y, x):
    """Devuelve lista de (fecha_inicio, direccion) para el (Y,X) dado.
    direccion: 'venta' si z>+X, 'compra' si z<-X, al inicio de cada racha."""
    z = df[f"z_{y}"]
    extremo_alto = (z > x).fillna(False)
    extremo_bajo = (z < -x).fillna(False)

    inicios = []
    for cond, direccion in [(extremo_alto, "venta"), (extremo_bajo, "compra")]:
        inicio_episodio = cond & ~cond.shift(1, fill_value=False)
        for fecha in df.loc[inicio_episodio, "fecha"]:
            inicios.append((fecha, direccion))
    inicios.sort(key=lambda t: t[0])
    return inicios


def simular_trades_ratio(df, inicios, z_horizon):
    fechas = df["fecha"].values
    trades = []
    fin_posicion_abierta = None  # no pyramiding, sea cual sea la direccion

    for fecha_inicio, direccion in inicios:
        if fin_posicion_abierta is not None and fecha_inicio <= fin_posicion_abierta:
            continue

        idx_entrada = np.searchsorted(fechas, np.datetime64(fecha_inicio), side="right")
        if idx_entrada >= len(df):
            continue
        idx_horizonte = idx_entrada + z_horizon
        if idx_horizonte >= len(df) or pd.isna(df.loc[idx_entrada, "atr"]):
            continue

        fila_entrada = df.loc[idx_entrada]
        entrada = float(fila_entrada["close"])
        riesgo = float(fila_entrada["atr"]) * mod.SL_ATR_MULT
        sl = entrada - riesgo if direccion == "compra" else entrada + riesgo

        salida = None
        for idx in range(idx_entrada + 1, idx_horizonte + 1):
            fila = df.loc[idx]
            tocado = (fila["low"] <= sl) if direccion == "compra" else (fila["high"] >= sl)
            if tocado:
                trades.append({
                    "tipo": direccion, "entrada": entrada, "sl": sl, "riesgo": riesgo,
                    "time_entrada": fila_entrada["fecha"], "time_salida": fila["fecha"],
                    "resultado_R": -1.0, "salida": "SL_ATR",
                })
                salida = fila["fecha"]
                break
        if salida is None:
            fila_horizonte = df.loc[idx_horizonte]
            cierre = float(fila_horizonte["close"])
            resultado_R = (cierre - entrada) / riesgo if direccion == "compra" else (entrada - cierre) / riesgo
            trades.append({
                "tipo": direccion, "entrada": entrada, "sl": sl, "riesgo": riesgo,
                "time_entrada": fila_entrada["fecha"], "time_salida": fila_horizonte["fecha"],
                "resultado_R": resultado_R, "salida": "HORIZONTE",
            })
            salida = fila_horizonte["fecha"]

        fin_posicion_abierta = salida

    return pd.DataFrame(trades)


# ============================================================
# 3. Seleccion de (Y,X,Z) en TRAIN + walk-forward
# ============================================================

def elegir_mejor_combo(df_train, verbose=False):
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for y in GRID_Y:
        for x in GRID_X:
            inicios = detectar_inicios_episodio_ratio(df_train, y, x)
            for z in GRID_Z:
                td = simular_trades_ratio(df_train, inicios, z)
                metrica = mod.metrica_robusta(td) if not td.empty else float("-inf")
                detalle.append((y, x, z, len(td), metrica))
                if metrica > mejor_metrica:
                    mejor_metrica = metrica
                    mejor = (y, x, z)
    if verbose:
        for y, x, z, ntr, met in detalle:
            elegible = "OK" if ntr >= mod.MIN_TRADES_SELECCION else f"< piso ({mod.MIN_TRADES_SELECCION})"
            met_str = f"{met:.3f}" if met != float("-inf") else "-inf"
            print(f"    Y={y:>3} X={x} Z={z:>2} | trades TRAIN: {ntr:>3} ({elegible}) | t-stat R neto: {met_str}")
    return mejor, mejor_metrica


def _rango_fechas(df):
    return f"{df['fecha'].iloc[0]:%Y-%m-%d} -> {df['fecha'].iloc[-1]:%Y-%m-%d}"


def correr_fold_ratio(df, df_train, df_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN: {len(df_train)} días ({_rango_fechas(df_train)}) "
          f"| TEST: {len(df_test)} días ({_rango_fechas(df_test)})")
    print("=" * 70)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    (mejor, metrica_train) = elegir_mejor_combo(df_train, verbose=True)

    resultado = {
        "fold": fold_num, "y": None, "x": None, "z": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor is None or metrica_train == float("-inf"):
        print(f"  ❌ Ninguna combinación de la grilla llegó al piso de "
              f"{mod.MIN_TRADES_SELECCION} trades en TRAIN -- fold sin selección posible.")
        return resultado

    mejor_y, mejor_x, mejor_z = mejor
    print(f"  Elegido in-sample (TRAIN de este fold): Y={mejor_y}, X={mejor_x}, Z={mejor_z} "
          f"(t-stat R neto: {metrica_train:.3f})")

    # Evaluacion out-of-sample UNA sola vez, con (Y,X,Z) ya fijados: simular sobre
    # TRAIN+TEST junto (necesario para que el horizonte Z pueda completarse con
    # velas de TEST, y para que la deteccion de episodios en el borde TRAIN/TEST
    # no dependa de reiniciar el z-score en cero), y quedarse solo con los
    # trades cuya ENTRADA cae dentro de la ventana de TEST.
    df_train_test = pd.concat([df_train, df_test], ignore_index=True)
    inicios_completo = detectar_inicios_episodio_ratio(df_train_test, mejor_y, mejor_x)
    td_completo = simular_trades_ratio(df_train_test, inicios_completo, mejor_z)
    fecha_inicio_test = df_test["fecha"].min()
    td_test = td_completo[td_completo["time_entrada"] >= fecha_inicio_test].reset_index(drop=True)

    resultado["y"], resultado["x"], resultado["z"] = mejor_y, mejor_x, mejor_z
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
    n_compras = (td_test["tipo"] == "compra").sum()
    n_ventas = (td_test["tipo"] == "venta").sum()
    print(f"  TEST (out-of-sample) | Trades: {n_trades:<3} (compra={n_compras}, venta={n_ventas}) | "
          f"Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R | Neto de spread: {r_neto:+7.2f}R  {estado}")

    resultado.update(n_trades_test=n_trades, wr_test=wr, r_total_test=r_total,
                      r_neto_test=r_neto, rentable=rentable)
    return resultado


def resumen_walk_forward_ratio(resultados):
    print("\n" + "#" * 70)
    print("RESUMEN WALK-FORWARD -- Hipótesis ratio oro/plata (fase 1)")
    print("#" * 70)
    for r in resultados:
        if not r["n_trades_test"]:
            motivo = "sin selección posible en TRAIN" if r["y"] is None else "sin operaciones en TEST"
            print(f"Fold {r['fold']} | {motivo}")
            continue
        estado = "✅ RENTABLE" if r["rentable"] else "❌ pierde"
        print(f"Fold {r['fold']} | Y={r['y']:>3} X={r['x']} Z={r['z']:>2} | Trades: {r['n_trades_test']:<3} | "
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
        print(f"\n⚠️  {len(resultados) - len(validos)} fold(s) no fueron evaluables -- la conclusión de abajo "
              "solo cubre los folds evaluables, no la ventana completa.")

    if len(rentables_neto) == len(validos):
        print("\n✅ El edge se sostuvo en TODOS los folds evaluables -> evidencia más fuerte de que es real.")
    elif len(rentables_neto) >= len(validos) * 0.5:
        print("\n⚠️  El edge se sostuvo en algunos folds pero no en todos -> no tratarlo como robusto todavía.")
    else:
        print("\n❌ El edge NO se sostuvo en la mayoría de los folds evaluables -> según la regla de corte "
              "declarada, esta hipótesis se descarta en esta fase.")


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
        print("  Sin folds evaluables -- no hay pool de trades para calcular t-stat.")
        return
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
    df = bajar_datos_ratio()
    print(f"Ratio oro/plata diario (MT5): {len(df)} días, {_rango_fechas(df)}\n")

    folds = mod.construir_bloques_walk_forward(df, N_FOLDS)
    resultados = [
        correr_fold_ratio(df, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds, start=1)
    ]
    resumen_walk_forward_ratio(resultados)
    analisis_pooled_test(resultados)


if __name__ == "__main__":
    main()
