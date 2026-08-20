"""
Hipotesis EURUSD, fase 1: carry trade real (devengo del diferencial de
tasas EUR-USD + retorno direccional), rebalanceado cada M dias habiles no
solapados.
=============================================================================
Primer candidato del nuevo marco EURUSD (2026-08-04, tras el cierre
formal del marco XAUUSD -- ver CLAUDE.md, Bitácora de decisiones.md y
Criterios de cierre del enfoque.md).

Historia de esta hipotesis (importante para no repetir el mismo error):
1. Version original (UIP/direccion): probaba si el diferencial predice la
   DIRECCION del spot EURUSD. Auditoria por capas (auditoria_carry_eurusd.py)
   confirmo signo correcto y consistente en 4 horizontes, pero correlaciones
   muy debiles (0.004-0.016) y monotonia por decil pobre y decreciente con
   el horizonte -- consistente con el "UIP puzzle" (famosamente debil en la
   literatura). Descartada ANTES de esta fase.
2. Version reformulada (esta): el carry trade real gana por DEVENGO del
   diferencial, no por prediccion de direccion. Auditoria por capas v2
   (auditoria_carry_eurusd_v2.py) dio retorno total positivo y creciente
   con el horizonte, pero con una advertencia real: los t-stats de esa
   auditoria eran sobre ventanas SOLAPADAS (autocorrelacionadas, inflan el
   t-stat) y el componente direccional dominaba sobre el devengo (al reves
   de lo esperado en la literatura de carry). Este script corrige eso:
   bloques NO solapados (walk-forward real, no ventanas rodantes).

Frase falsable (ficha hypothesis-gate, aprobada antes de este codigo):
manteniendo una posicion larga en EURUSD cuando tasa_eur > tasa_usd (con 1
mes de rezago de publicacion) y corta cuando tasa_usd > tasa_eur,
rebalanceada cada M dias habiles NO SOLAPADOS, el retorno total
(direccional + devengo) es positivo y estadisticamente distinguible de
cero en el horizonte de M dias.

Retorno de cada bloque (trade):
  retorno_direccional = signo(D) * retorno_spot_M
  carry_devengado     = |D| * (M/365) / 100   (siempre >= 0 por construccion)
  costo_spread        = spread_precio/precio_entrada, SOLO si la posicion
                         cambia de signo respecto al bloque anterior (o es
                         el primer bloque) -- si se mantiene la misma
                         direccion no hay que volver a cruzar el spread.
  retorno_neto         = retorno_direccional + carry_devengado - costo_spread

Nota sobre el spread: EURUSD en este broker mostro spread=0 en el momento
de la consulta (probablemente snapshot de mercado cerrado, no un dato
confiable). Se usa SPREAD_PUNTOS_EURUSD=15 (1.5 pips, supuesto razonable
de spread retail tipico -- documentado como supuesto, igual que
SPREAD_PUNTOS=30 para XAUUSD en Backtest ema v4.py ya lo era).

Grilla declarada (1x4, sin k -- la direccion la fija el signo de D, no es
parametro a barrer): M en {1, 5, 10, 20} dias habiles.

Walk-forward: 8 folds anclados (derivado del caso mas restrictivo, M=20:
~38 trades/fold TEST, +27% de margen sobre el piso de 30; K=16 rompe el
piso en M=20, ~20 trades/fold).

Regla de corte (fijada de antemano, ficha hypothesis-gate):
- t-stat |t| > 1.96 sobre retorno neto pooled de TEST, con y sin el fold
  de mayor retorno -- la conclusion cualitativa no puede cambiar.
- DSR >= 0.95, N = grilla x folds = 4x8 = 32 (sin sumar la auditoria
  UIP/direccion previa -- nunca paso por seleccion en TRAIN con grid
  barrido, no es una "variante" en el mismo sentido).
- Piso de 30 trades por fold (seleccion en TRAIN).
- Sin iterar la grilla ni el diseño fuera de lo declarado arriba una vez
  visto el resultado.
"""
import math
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

DIR_PROYECTO = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta"
RUTA_EUR = DIR_PROYECTO + r"\historial\eur_3m_interbank.csv"
RUTA_USD = DIR_PROYECTO + r"\historial\usd_3m_interbank.csv"
RUTA_EURUSD = DIR_PROYECTO + r"\historial\eurusd_d1.csv"

import importlib.util
spec_dsr = importlib.util.spec_from_file_location("deflated_sharpe", DIR_PROYECTO + r"\deflated_sharpe.py")
dsr_mod = importlib.util.module_from_spec(spec_dsr)
sys.modules["deflated_sharpe"] = dsr_mod
spec_dsr.loader.exec_module(dsr_mod)

REZAGO_PUBLICACION_MESES = 1
GRID_M = [1, 5, 10, 20]
N_FOLDS = 8  # derivado del caso mas restrictivo M=20 -- ~38 trades/fold, +27%
DIAS_ANIO = 365
MIN_TRADES_SELECCION = 30
SPREAD_PUNTOS_EURUSD = 15  # 1.5 pips, supuesto documentado (broker no dio spread confiable)
POINT_SIZE_EURUSD = 0.00001
N_VARIANTES_DSR = len(GRID_M) * N_FOLDS  # 32


def cargar_tasas_mensuales_con_rezago(ruta, nombre_col):
    df = pd.read_csv(ruta)
    df.columns = ["fecha", nombre_col]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df[nombre_col] = pd.to_numeric(df[nombre_col], errors="coerce")
    df["fecha_conocida"] = df["fecha"] + pd.DateOffset(months=REZAGO_PUBLICACION_MESES)
    return df[["fecha_conocida", nombre_col]].dropna()


def cargar_señal():
    df_eurusd = pd.read_csv(RUTA_EURUSD)
    df_eurusd["fecha"] = pd.to_datetime(df_eurusd["time"])

    eur = cargar_tasas_mensuales_con_rezago(RUTA_EUR, "tasa_eur")
    usd = cargar_tasas_mensuales_con_rezago(RUTA_USD, "tasa_usd")

    df = df_eurusd[["fecha", "close"]].copy()
    df = df.merge(eur.rename(columns={"fecha_conocida": "fecha"}), on="fecha", how="left")
    df = df.merge(usd.rename(columns={"fecha_conocida": "fecha"}), on="fecha", how="left")
    df["tasa_eur"] = df["tasa_eur"].ffill()
    df["tasa_usd"] = df["tasa_usd"].ffill()
    df["D"] = df["tasa_eur"] - df["tasa_usd"]
    df = df.dropna(subset=["D"]).reset_index(drop=True)
    df["posicion"] = np.sign(df["D"])
    return df


def construir_bloques_walk_forward(df, n_folds):
    """Mismo patron que Backtest ema v4.py -- bloques por CANTIDAD de filas,
    walk-forward anclado (expanding TRAIN, TEST disjunto sucesivo)."""
    n_blocks = n_folds + 1
    block_size = len(df) // n_blocks
    limites = [i * block_size for i in range(n_blocks)] + [len(df)]
    bloques = [df.iloc[limites[i]:limites[i + 1]] for i in range(n_blocks)]
    folds = []
    for k in range(1, n_blocks):
        train = pd.concat(bloques[:k])
        test = bloques[k]
        folds.append((train, test))
    return folds


def construir_trades_M(df, m):
    """Bloques NO solapados de m dias sobre TODO el historico (indices fijos,
    no dependen del fold) -- la membresia TRAIN/TEST se decide por fecha."""
    n_bloques = (len(df) - 1) // m  # asegura que idx_salida = (i+1)*m sea un índice válido
    trades = []
    pos_anterior = None
    for i in range(n_bloques):
        idx_entrada = i * m
        idx_salida = idx_entrada + m
        fila_entrada = df.iloc[idx_entrada]
        fila_salida = df.iloc[idx_salida]

        posicion = fila_entrada["posicion"]
        D = fila_entrada["D"]
        retorno_spot = fila_salida["close"] / fila_entrada["close"] - 1.0
        retorno_direccional = posicion * retorno_spot
        carry_devengado = abs(D) * (m / DIAS_ANIO) / 100.0

        hubo_flip = (pos_anterior is None) or (posicion != pos_anterior)
        costo_spread = (SPREAD_PUNTOS_EURUSD * POINT_SIZE_EURUSD / fila_entrada["close"]) if hubo_flip else 0.0

        retorno_neto = retorno_direccional + carry_devengado - costo_spread

        trades.append({
            "fecha_entrada": fila_entrada["fecha"], "fecha_salida": fila_salida["fecha"],
            "posicion": posicion, "D": D, "retorno_direccional": retorno_direccional,
            "carry_devengado": carry_devengado, "costo_spread": costo_spread,
            "retorno_neto": retorno_neto, "flip": hubo_flip,
        })
        pos_anterior = posicion

    return pd.DataFrame(trades)


def metrica_robusta_pct(trades_df):
    n = len(trades_df)
    if n < MIN_TRADES_SELECCION:
        return float("-inf")
    r = trades_df["retorno_neto"]
    std = r.std(ddof=1)
    if not std or pd.isna(std):
        return float("-inf")
    return r.mean() / (std / np.sqrt(n))


def elegir_mejor_M(trades_por_M, fecha_corte_train, verbose=False):
    mejor_m, mejor_metrica = None, float("-inf")
    detalle = []
    for m, trades in trades_por_M.items():
        train = trades[trades["fecha_entrada"] <= fecha_corte_train]
        met = metrica_robusta_pct(train)
        detalle.append((m, len(train), met))
        if met > mejor_metrica:
            mejor_metrica, mejor_m = met, m
    if verbose:
        for m, ntr, met in detalle:
            elegible = "OK" if ntr >= MIN_TRADES_SELECCION else f"< piso ({MIN_TRADES_SELECCION})"
            met_str = f"{met:.3f}" if met != float("-inf") else "-inf"
            print(f"    M={m:>2} | trades TRAIN: {ntr:>4} ({elegible}) | t-stat retorno neto: {met_str}")
    return mejor_m, mejor_metrica


def correr_fold(trades_por_M, df_señal_train, df_señal_test, fold_num, n_folds):
    print("\n" + "=" * 70)
    fecha_corte_train = df_señal_train["fecha"].max()
    fecha_fin_test = df_señal_test["fecha"].max()
    print(f"FOLD {fold_num}/{n_folds} — TRAIN hasta {fecha_corte_train.date()} "
          f"({len(df_señal_train)} días) | TEST hasta {fecha_fin_test.date()} ({len(df_señal_test)} días)")
    print("=" * 70)

    print("  Combinaciones evaluadas en TRAIN (in-sample):")
    mejor_m, metrica_train = elegir_mejor_M(trades_por_M, fecha_corte_train, verbose=True)

    resultado = {"fold": fold_num, "m": None, "n_trades_test": 0, "r_neto_test": None, "rentable": None}

    if mejor_m is None:
        print(f"  ❌ Ningún M de la grilla llegó al piso de {MIN_TRADES_SELECCION} trades en TRAIN.")
        return resultado

    print(f"  Elegido in-sample (TRAIN de este fold): M={mejor_m} (t-stat retorno neto: {metrica_train:.3f})")

    fecha_inicio_test = df_señal_test["fecha"].min()
    trades_m = trades_por_M[mejor_m]
    td_test = trades_m[(trades_m["fecha_entrada"] > fecha_corte_train) &
                        (trades_m["fecha_entrada"] <= fecha_fin_test)].reset_index(drop=True)

    resultado["m"] = mejor_m
    resultado["td_test"] = td_test

    if td_test.empty:
        print("  TEST (out-of-sample): sin operaciones.")
        return resultado

    n_trades = len(td_test)
    wr = (td_test["retorno_neto"] > 0).sum() / n_trades * 100
    r_neto = td_test["retorno_neto"].sum()
    rentable = r_neto > 0
    estado = "✅ RENTABLE" if rentable else "❌ pierde"
    print(f"  TEST (out-of-sample) | Trades: {n_trades:<4} | Win rate: {wr:5.1f}% | "
          f"R neto acumulado: {r_neto*100:+.3f}%  {estado}")

    resultado.update(n_trades_test=n_trades, r_neto_test=r_neto, rentable=rentable)
    return resultado


def resumen_walk_forward(resultados):
    print("\n" + "#" * 70)
    print("RESUMEN WALK-FORWARD -- Carry EURUSD (fase 1)")
    print("#" * 70)
    for r in resultados:
        if not r["n_trades_test"]:
            motivo = "sin selección posible en TRAIN" if r["m"] is None else "sin operaciones en TEST"
            print(f"Fold {r['fold']} | {motivo}")
            continue
        estado = "✅ RENTABLE" if r["rentable"] else "❌ pierde"
        print(f"Fold {r['fold']:>2} | M={r['m']:>2} | Trades: {r['n_trades_test']:<4} | "
              f"Retorno neto: {r['r_neto_test']*100:+.3f}%  {estado}")
    print("#" * 70)

    validos = [r for r in resultados if r["n_trades_test"]]
    if not validos:
        print("\nNingún fold generó operaciones evaluables -- hipótesis se descarta.")
        return validos

    rentables = [r for r in validos if r["r_neto_test"] > 0]
    print(f"\nFolds evaluables: {len(validos)}/{len(resultados)}")
    print(f"Folds rentables: {len(rentables)}/{len(validos)}")

    trades_totales = sum(r["n_trades_test"] for r in validos)
    r_neto_total = sum(r["r_neto_test"] for r in validos)
    print(f"Trades TEST acumulados: {trades_totales} | Retorno neto acumulado: {r_neto_total*100:+.3f}%")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    if r_neto_total != 0:
        pct_dom = fold_max["r_neto_test"] / r_neto_total * 100
        print(f"\nFold más fuerte: Fold {fold_max['fold']} ({fold_max['r_neto_test']*100:+.3f}%) "
              f"-> {pct_dom:.0f}% del retorno acumulado.")
        if pct_dom > 60:
            print("⚠️  Un solo fold concentra la mayoría del resultado.")

    return validos


def t_stat_pooled(td, etiqueta):
    r = td["retorno_neto"]
    n = len(r)
    media = r.mean()
    std = r.std(ddof=1)
    t = media / (std / math.sqrt(n))
    p_valor = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    print(f"  [{etiqueta}] n={n} | retorno medio={media*100:+.4f}% | t-stat={t:+.3f} | "
          f"p (aprox. normal, dos colas)={p_valor:.4f}")
    return t, p_valor, r


def analisis_pooled_test(validos):
    if not validos:
        return None
    print("\n" + "#" * 70)
    print("t-stat real sobre retorno neto -- trades TEST agrupados (bloques no solapados)")
    print("#" * 70)
    todos = pd.concat([r["td_test"] for r in validos], ignore_index=True)
    _, _, r_todos = t_stat_pooled(todos, f"{len(todos)} trades TEST, los {len(validos)} folds evaluables")

    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    sin_dom = pd.concat([r["td_test"] for r in validos if r["fold"] != fold_max["fold"]], ignore_index=True)
    if not sin_dom.empty:
        t_stat_pooled(sin_dom, f"{len(sin_dom)} trades TEST, sin Fold {fold_max['fold']} (el más fuerte)")

    return r_todos


def analisis_dsr(r_todos):
    if r_todos is None or r_todos.empty:
        return
    print("\n" + "#" * 70)
    print(f"Deflated Sharpe Ratio (N={N_VARIANTES_DSR}: grilla {len(GRID_M)}x{N_FOLDS})")
    print("#" * 70)
    resultado = dsr_mod.deflated_sharpe_ratio(r_todos.values, N_VARIANTES_DSR)
    dsr_mod.reportar(resultado)


def main():
    df = cargar_señal()
    print(f"Señal EURUSD carry: {len(df)} días, {df['fecha'].min().date()} -> {df['fecha'].max().date()}\n")

    trades_por_M = {m: construir_trades_M(df, m) for m in GRID_M}
    for m, t in trades_por_M.items():
        print(f"M={m}: {len(t)} bloques (trades) totales sobre todo el histórico")

    folds = construir_bloques_walk_forward(df, N_FOLDS)
    resultados = [
        correr_fold(trades_por_M, train, test, i, N_FOLDS)
        for i, (train, test) in enumerate(folds, start=1)
    ]
    validos = resumen_walk_forward(resultados)
    r_todos = analisis_pooled_test(validos)
    analisis_dsr(r_todos)


if __name__ == "__main__":
    main()
