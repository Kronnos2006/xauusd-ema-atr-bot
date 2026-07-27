"""
Hipotesis macro, fase 1: empinamiento del spread 2s10s como filtro de
regimen para XAUUSD.
=============================================================================

Frase falsable: cuando el spread 2s10s (FRED T10Y2Y, 10 anios - 2 anios,
nominal) viene empinandose (steepening) de forma sostenida en los ultimos
N dias habiles, el oro tiene sesgo alcista sostenido en las M sesiones
siguientes.

Definiciones fijas (declaradas antes de correr el walk-forward, sin barrer
variantes fuera de la grilla declarada -- mismo patron que
hipotesis_macro_dfii10.py, adaptado a la direccion opuesta: aca se busca
empinamiento, no caida):

- Senial de "empinamiento sostenido": spread[t] > spread[t-N] (nivel neto
  de la ventana, sin exigir monotonia dia a dia -- ver
  chequeo_frecuencia_2s10s.py para la justificacion y el conteo de
  episodios).
- Un "episodio" es una racha maxima de dias consecutivos con la senial
  activa. Se opera UNA sola vez por episodio, no una vez por dia con
  senial activa.
- Entrada: SOLO compra (hipotesis direccional, sesgo alcista), al cierre
  de la primera sesion de oro posterior al dia en que el episodio arranca
  (D+1 -- el spread del dia D recien se conoce completo al cierre de D).
- Riesgo/SL: ATR14 diario * SL_ATR_MULT (mismo multiplicador ya validado
  en el proyecto, importado de Backtest ema v4.py). Sin take-profit fijo.
- Salida: lo que ocurra primero entre (a) horizonte fijo de M sesiones de
  oro despues de la entrada, evaluado al cierre (resultado_R continuo,
  sin tope), o (b) el low de una vela diaria toca el SL (resultado_R =
  -1.0, misma convencion que backtest() en Backtest ema v4.py).
- Sin pyramiding: si hay una posicion abierta, se ignoran episodios
  nuevos hasta que cierre.

Grilla declarada (3x3, no se prueba nada fuera de esto en este intento --
misma grilla de valores que uso DFII10, primera vez que se aplica a este
dato, no es reusar un barrido ya hecho sobre 2s10s):
  N (dias habiles de empinamiento sostenido): 20, 60, 120
  M (sesiones de horizonte de salida): 5, 10, 20

Walk-forward: 2 folds anclados. Derivado del chequeo de frecuencia previo
(chequeo_frecuencia_2s10s.py / derivar_folds_2s10s.py) contra el piso fijo
de MIN_TRADES_SELECCION=30 episodios/fold: con la grilla completa, N=120
(77 episodios totales en la ventana 2004-2026) es el cuello de botella --
con 3 folds cae a 16 episodios en el peor fold, bajo el piso; con 2 folds
el peor caso da 31, arriba del piso. Decision del usuario (no del agente):
mantener la grilla completa {20,60,120} y aceptar K=2 en vez de acotar la
grilla para ganar folds.

RESERVA METODOLOGICA EXPLICITA, valida desde antes de correr nada (no
post-hoc): con solo 2 folds, el chequeo de "sin fold dominante" pierde
casi todo su sentido (mayoria = ambos folds a la vez, no hay margen
intermedio) y el walk-forward tiene mucho menos poder estadistico que los
4 folds usados para DFII10. Cualquier resultado de esta hipotesis debe
leerse con esa limitacion en mente, no solo si "pasa" el numero.

Fuente de datos: FRED T10Y2Y (descarga publica sin API key) + curva de
rendimiento nominal (Par Yield Curve) de home.treasury.gov como
verificacion cruzada (columnas "2 Yr" y "10 Yr", spread calculado a mano).
Oro: XAUUSD diario via MT5 (mismo terminal que el resto del proyecto).

Regla de corte, fijada de antemano (mas estricta que la usada para
DFII10, decision explicita del usuario -- sin zona de "pasa con
reservas"):
  (a) mayoria de folds evaluables rentables netos de spread, Y
  (b) t-stat pooled sobre R neto de TEST con p<0.05, Y
  (c) ese p sigue <0.05 al sacar el fold mas fuerte (sin el).
Si falla cualquiera de las tres, NO PASA. Una sola pasada con esta
definicion -- si no sostiene, se descarta sin iterar N/M fuera de la
grilla ni probar otra definicion de "empinamiento" en el mismo intento.
"""
import importlib.util
import math
import sys

import numpy as np
import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
DIR_PROYECTO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta"
RUTA_T10Y2Y = DIR_PROYECTO + r"\historial\t10y2y.csv"
RUTA_TREASURY_NOMINAL_2025 = DIR_PROYECTO + r"\historial\treasury_nominal_yield_2025.csv"
RUTA_TREASURY_NOMINAL_2026 = DIR_PROYECTO + r"\historial\treasury_nominal_yield_2026.csv"

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # no corre main() porque __name__ != "__main__"

GRID_N = [20, 60, 120]
GRID_M = [5, 10, 20]
N_FOLDS = 2  # ver docstring: derivado del chequeo de frecuencia, no un default
ATR_PERIOD_DIARIO = 14
INICIO_DATOS_ORO_MT5 = pd.Timestamp("2004-06-11")  # mismo limite que DFII10


# ============================================================
# 1. Datos macro (T10Y2Y + verificacion cruzada Treasury nominal)
# ============================================================

def cargar_t10y2y():
    df = pd.read_csv(RUTA_T10Y2Y)
    df.columns = ["fecha", "spread"]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["spread"] = pd.to_numeric(df["spread"], errors="coerce")
    df = df.dropna(subset=["spread"]).reset_index(drop=True)
    return df


def verificar_cruce_treasury(df_t10y2y):
    """Compara T10Y2Y (FRED) contra el spread 10yr-2yr calculado a mano con
    la curva de rendimiento NOMINAL diaria (Par Yield Curve) de
    home.treasury.gov, en el solapamiento 2025-2026, para confirmar que la
    fuente primaria no esta desalineada/rezagada."""
    partes = []
    for ruta in (RUTA_TREASURY_NOMINAL_2025, RUTA_TREASURY_NOMINAL_2026):
        t = pd.read_csv(ruta)
        t = t.rename(columns={"Date": "fecha", "2 Yr": "y2", "10 Yr": "y10"})
        t["fecha"] = pd.to_datetime(t["fecha"], format="%m/%d/%Y")
        t["spread_treasury"] = pd.to_numeric(t["y10"], errors="coerce") - pd.to_numeric(t["y2"], errors="coerce")
        partes.append(t[["fecha", "spread_treasury"]])
    treasury = pd.concat(partes, ignore_index=True).sort_values("fecha").dropna()

    cruce = df_t10y2y.merge(treasury, on="fecha", how="inner")
    cruce["diff_abs"] = (cruce["spread"] - cruce["spread_treasury"]).abs()
    corr = cruce["spread"].corr(cruce["spread_treasury"])

    print("=== Verificación cruzada FRED T10Y2Y vs. Treasury.gov (10 Yr - 2 Yr nominal) ===")
    print(f"Fechas comparadas: {len(cruce)} ({cruce['fecha'].min().date()} -> {cruce['fecha'].max().date()})")
    print(f"Correlación: {corr:.6f}")
    print(f"Diferencia absoluta -- media: {cruce['diff_abs'].mean():.4f} | máxima: {cruce['diff_abs'].max():.4f}")
    if cruce["diff_abs"].max() > 0.05:
        print("⚠️  Diferencia máxima > 0.05 puntos -- revisar antes de confiar en la fuente primaria.")
    else:
        print("✅ Fuentes consistentes -- T10Y2Y (FRED) queda confirmado como fuente primaria.")
    print()


def detectar_inicios_episodio(df_spread, n):
    """Devuelve las fechas en que un episodio de 'empinamiento sostenido'
    arranca (transicion False->True), para el N dado."""
    cond = df_spread["spread"] > df_spread["spread"].shift(n)
    cond = cond.fillna(False)
    inicio_episodio = cond & ~cond.shift(1, fill_value=False)
    return df_spread.loc[inicio_episodio, "fecha"].tolist()


# ============================================================
# 2. Datos de oro (diario via MT5) + ATR
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
# 3. Simulación de trades para una combinación (N, M) dada
# ============================================================

def simular_trades(df_spread, df_oro, n, m):
    inicios = detectar_inicios_episodio(df_spread, n)
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
# 4. Selección de (N, M) en TRAIN + walk-forward
# ============================================================

def elegir_mejor_nm(df_spread_train, df_oro_train, verbose=False):
    mejor = None
    mejor_metrica = float("-inf")
    detalle = []
    for n in GRID_N:
        for m in GRID_M:
            td = simular_trades(df_spread_train, df_oro_train, n, m)
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


def correr_fold_macro(df_spread, df_oro_train, df_oro_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN oro: {len(df_oro_train)} días ({_rango_fechas_oro(df_oro_train)}) "
          f"| TEST oro: {len(df_oro_test)} días ({_rango_fechas_oro(df_oro_test)})")
    print("=" * 70)

    fecha_corte_train = df_oro_train["fecha"].max()
    df_spread_train = df_spread[df_spread["fecha"] <= fecha_corte_train].reset_index(drop=True)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    (mejor_n, mejor_m), metrica_train = elegir_mejor_nm(df_spread_train, df_oro_train, verbose=True)

    resultado = {
        "fold": fold_num, "n": None, "m": None, "n_trades_test": 0,
        "wr_test": None, "r_total_test": None, "r_neto_test": None, "rentable": None,
    }

    if mejor_n is None or metrica_train == float("-inf"):
        print("  ❌ Ninguna combinación de la grilla llegó al piso de "
              f"{mod.MIN_TRADES_SELECCION} trades en TRAIN -- fold sin selección posible.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): N={mejor_n}, M={mejor_m} (t-stat R neto: {metrica_train:.3f})")

    fecha_fin_test = df_oro_test["fecha"].max()
    df_spread_hasta_test = df_spread[df_spread["fecha"] <= fecha_fin_test].reset_index(drop=True)

    df_oro_train_test = pd.concat([df_oro_train, df_oro_test], ignore_index=True)
    td_completo = simular_trades(df_spread_hasta_test, df_oro_train_test, mejor_n, mejor_m)
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
    print("RESUMEN WALK-FORWARD -- Hipótesis macro 2s10s (fase 1)")
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
        return None

    rentables_neto = [r for r in validos if r["r_neto_test"] and r["r_neto_test"] > 0]
    print(f"\nFolds evaluables: {len(validos)}/{len(resultados)}")
    print(f"Folds rentables (neto de spread): {len(rentables_neto)}/{len(validos)}")

    trades_totales = sum(r["n_trades_test"] for r in validos)
    r_neto_total = sum(r["r_neto_test"] for r in validos)
    print(f"Trades TEST acumulados: {trades_totales} | R neto acumulado: {r_neto_total:+.2f}R")

    mayoria_rentable = len(rentables_neto) > len(validos) / 2

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    if r_neto_total != 0:
        pct_dominante = fold_max["r_neto_test"] / r_neto_total * 100
        print(f"\nFold más fuerte: Fold {fold_max['fold']} ({fold_max['r_neto_test']:+.2f}R neto) "
              f"-> {pct_dominante:.0f}% del R neto acumulado.")

    print("\n⚠️  RECORDATORIO (fijado antes de correr nada): con N_FOLDS=2 el chequeo de "
          "'sin fold dominante' tiene casi nulo poder de discriminación -- leer el resultado "
          "con esa reserva, no solo el número de folds rentables.")

    return {"mayoria_rentable": mayoria_rentable, "validos": validos, "fold_max_num": fold_max["fold"]}


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
        return None, None
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    n_todos = len(todos)
    t_todos, p_todos = t_stat_pooled(todos, f"{n_todos} trades TEST, los {len(validos)} folds")

    if len(validos) < 2:
        print("  (menos de 2 folds evaluables -- no se puede calcular 'sin el fold más fuerte')")
        return p_todos, None

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    sin_dominante = pd.concat(
        [r["td_test"] for r in validos if r["fold"] != fold_max["fold"]], ignore_index=True)
    if sin_dominante.empty:
        return p_todos, None
    n_sin = len(sin_dominante)
    t_sin, p_sin = t_stat_pooled(sin_dominante, f"{n_sin} trades TEST, sin Fold {fold_max['fold']} (el más fuerte)")
    return p_todos, p_sin


def veredicto_final(resumen, p_todos, p_sin):
    print("\n" + "#" * 70)
    print("VEREDICTO (regla de corte fijada de antemano, hypothesis-gate)")
    print("#" * 70)
    if resumen is None or p_todos is None:
        print("❌ NO PASA -- sin datos suficientes para evaluar la regla de corte.")
        return

    cond_a = resumen["mayoria_rentable"]
    cond_b = p_todos < 0.05
    cond_c = (p_sin is not None) and (p_sin < 0.05)

    print(f"(a) Mayoría de folds rentables netos de spread: {'✅' if cond_a else '❌'}")
    print(f"(b) t-stat pooled (todos los folds) p<0.05: {'✅' if cond_b else '❌'} (p={p_todos:.4f})")
    if p_sin is not None:
        print(f"(c) t-stat pooled sin el fold más fuerte p<0.05: {'✅' if cond_c else '❌'} (p={p_sin:.4f})")
    else:
        print("(c) t-stat pooled sin el fold más fuerte: no calculable (menos de 2 folds evaluables) -> ❌")

    if cond_a and cond_b and cond_c:
        print("\n✅ PASA EL CHECKPOINT EXPLORATORIO.")
    else:
        print("\n❌ NO PASA EL CHECKPOINT EXPLORATORIO -- hipótesis se descarta en esta fase, "
              "sin iterar N/M fuera de la grilla ni redefinir 'empinamiento' en este mismo intento.")


# ============================================================
# main
# ============================================================

def main():
    df_spread = cargar_t10y2y()
    verificar_cruce_treasury(df_spread)

    df_oro = bajar_oro_diario()
    print(f"Oro diario (MT5): {len(df_oro)} días, {_rango_fechas_oro(df_oro)}\n")

    folds_oro = mod.construir_bloques_walk_forward(df_oro, N_FOLDS)
    resultados = [
        correr_fold_macro(df_spread, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds_oro, start=1)
    ]
    resumen = resumen_walk_forward_macro(resultados)
    p_todos, p_sin = analisis_pooled_test(resultados)
    veredicto_final(resumen, p_todos, p_sin)


if __name__ == "__main__":
    main()
