"""
Backtest EMA Cross + ATR para XAUUSD en MetaTrader 5
=====================================================

PASO 1 del bot nuevo: validar la estrategia con datos reales antes de
escribir una sola línea de MQL5.

Estrategia:
- EMA rápida (9) cruza EMA lenta (21) -> señal de entrada
- Filtro de tendencia: precio debe estar del lado correcto de la EMA 50
- Stop Loss: basado en ATR (volatilidad), no un número fijo en pips
- Take Profit: múltiplo del SL (Risk:Reward configurable)

REQUISITOS (correr en tu PC Windows con MT5 abierto):
    pip install MetaTrader5 pandas numpy

USO:
    python backtest_ema_xauusd.py
"""

import sys
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# CONFIGURACIÓN - andá ajustando estos valores
# ============================================================
SYMBOL = "XAUUSD"
TIMEFRAME = mt5.TIMEFRAME_M15     # M15 para empezar; después probamos M5, H1
N_VELAS = 15000                    # cuántas velas históricas bajar (subido para más robustez)

HTF_TIMEFRAME = mt5.TIMEFRAME_H1   # timeframe mayor para el filtro de tendencia MTF
TIMEFRAME_DELTA = {                # duración de una vela por timeframe (para alinear MTF sin lookahead)
    mt5.TIMEFRAME_M15: pd.Timedelta(minutes=15),
    mt5.TIMEFRAME_H1: pd.Timedelta(hours=1),
}
BUFFER_DIAS_HTF = 14               # margen calendario hacia atrás al bajar el timeframe mayor (fines de semana/feriados)

USE_SESSION_FILTER = False      # solo operar en horario de mayor liquidez (Londres/NY)
SESSION_START_HOUR = 8            # hora GMT de inicio (ajustar según tu servidor MT5)
SESSION_END_HOUR = 20             # hora GMT de fin

EMA_FAST = 9
EMA_SLOW = 21
EMA_TREND = 50

SWING_L = 2     # barras a la izquierda para confirmar un swing high/low (fractal fijo, no tuneado por fold)
SWING_R = 2     # barras a la derecha -- también el retraso de confirmación (no se puede saber antes)

RETEST_VENTANA = 20            # velas para buscar el retest despues de una ruptura de swing (~5hs en M15), fijo, sin barrido
RETEST_MARGEN_ATR_MULT = 0.25  # margen de la zona de retest, en multiplos del ATR de la vela de ruptura, fijo, sin barrido

ATR_PERIOD = 14
SL_ATR_MULT = 1.5                 # Stop Loss = 1.5x ATR
RR_RATIO = 2.0                    # Take Profit = 2x el riesgo (1:2)

SPREAD_PUNTOS = 30                # spread aproximado en puntos (ajustar a tu broker)


def conectar_mt5():
    ruta_terminal = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mt5.initialize(path=ruta_terminal):
        print("ERROR: no se pudo conectar a MT5:", mt5.last_error())
        quit()
    print("Conectado a MT5:", mt5.terminal_info())


def bajar_datos(symbol, timeframe, n_velas):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_velas)
    if rates is None or len(rates) == 0:
        print(f"ERROR: no se pudieron bajar datos de {symbol}. ¿Está el símbolo visible en Market Watch?")
        quit()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def bajar_datos_rango(symbol, timeframe, date_from, date_to):
    """Como bajar_datos, pero anclado a un rango de fechas real (mt5.copy_rates_range)
    en vez de un N de velas -- evita asumir cuántas velas hay por día con mercado
    cerrado fines de semana/feriados."""
    rates = mt5.copy_rates_range(symbol, timeframe, date_from, date_to)
    if rates is None or len(rates) == 0:
        print(f"ERROR: no se pudieron bajar datos de {symbol} en el rango {date_from} -> {date_to}.")
        quit()
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df


def calcular_indicadores(df):
    df["ema_fast"] = df["close"].ewm(span=EMA_FAST, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=EMA_SLOW, adjust=False).mean()
    df["ema_trend"] = df["close"].ewm(span=EMA_TREND, adjust=False).mean()

    # ATR
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_PERIOD).mean()

    return df


def generar_senales(df, use_session_filter=None):
    df["cruce_alcista"] = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1))
    df["cruce_bajista"] = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1))

    df["senal_compra"] = df["cruce_alcista"] & (df["close"] > df["ema_trend"])
    df["senal_venta"] = df["cruce_bajista"] & (df["close"] < df["ema_trend"])

    filtro_sesion = USE_SESSION_FILTER if use_session_filter is None else use_session_filter
    if filtro_sesion:
        hora = df["time"].dt.hour
        en_sesion = (hora >= SESSION_START_HOUR) & (hora < SESSION_END_HOUR)
        df["senal_compra"] = df["senal_compra"] & en_sesion
        df["senal_venta"] = df["senal_venta"] & en_sesion

    # EMA_TREND recién es representativa (no sesgada hacia el primer precio
    # de la serie) después de su propio período de warm-up.
    warmup = df.index < EMA_TREND
    df.loc[warmup, "senal_compra"] = False
    df.loc[warmup, "senal_venta"] = False

    return df


def calcular_tendencia_h1(df_h1):
    """Tendencia del timeframe mayor (mismo criterio close-vs-EMA_TREND que ya
    usa el proyecto en M15, aplicado un nivel arriba). No reutiliza
    calcular_indicadores: no hacen falta ema_fast/ema_slow/atr en H1, y
    calcularlos generaría colisión de nombres de columna al mergear con M15."""
    df_h1 = df_h1.copy()
    df_h1["ema_trend_h1"] = df_h1["close"].ewm(span=EMA_TREND, adjust=False).mean()
    df_h1["tendencia_alcista_h1"] = df_h1["close"] > df_h1["ema_trend_h1"]
    df_h1["tendencia_bajista_h1"] = df_h1["close"] < df_h1["ema_trend_h1"]

    # warm-up de la EMA_TREND propia de H1, aplicado ANTES de exponer las
    # columnas -- si se dejara para después del merge, las primeras filas de
    # M15 (todo el TRAIN del fold 1) heredarían una tendencia H1 no representativa.
    warmup_h1 = df_h1.index < EMA_TREND
    df_h1.loc[warmup_h1, "tendencia_alcista_h1"] = False
    df_h1.loc[warmup_h1, "tendencia_bajista_h1"] = False

    # instante desde el cual esta vela H1 es información ya conocida (su close
    # real) -- en MT5 "time" es siempre el open de la vela.
    df_h1["valido_desde"] = df_h1["time"] + TIMEFRAME_DELTA[HTF_TIMEFRAME]

    return df_h1[["valido_desde", "tendencia_alcista_h1", "tendencia_bajista_h1"]]


def alinear_h1_a_m15(df_m15, df_h1_tendencia):
    """Pega a cada vela M15 la tendencia de la última vela H1 que ya cerró
    ANTES de que esa vela M15 abra (merge_asof backward sobre valido_desde) --
    nunca usa una vela H1 todavía en formación en el instante de la señal."""
    df_m15_ordenado = df_m15.sort_values("time")
    df_h1_ordenado = df_h1_tendencia.sort_values("valido_desde")

    # la suma de Timedelta a "time" en calcular_tendencia_h1 puede dejar
    # valido_desde con una resolución de datetime64 distinta a la de "time" en
    # M15 (p.ej. [s] vs [us]) -- merge_asof exige que ambas claves matcheen
    # exactamente en dtype, no solo en tipo lógico.
    df_m15_ordenado = df_m15_ordenado.assign(time=df_m15_ordenado["time"].astype("datetime64[ns]"))
    df_h1_ordenado = df_h1_ordenado.assign(valido_desde=df_h1_ordenado["valido_desde"].astype("datetime64[ns]"))

    df_mtf = pd.merge_asof(
        df_m15_ordenado, df_h1_ordenado,
        left_on="time", right_on="valido_desde",
        direction="backward",
    )

    # filas M15 anteriores a la primera vela H1 disponible (con warm-up
    # completo) no matchean -> quedan NaN; tratarlas como "sin tendencia
    # confirmada" (False), no como True/False mezclado con NaN (eso sube el
    # dtype de la columna a object y rompe el & con cruce_alcista/bajista).
    df_mtf["tendencia_alcista_h1"] = df_mtf["tendencia_alcista_h1"].fillna(False).astype(bool)
    df_mtf["tendencia_bajista_h1"] = df_mtf["tendencia_bajista_h1"].fillna(False).astype(bool)

    df_mtf = df_mtf.reset_index(drop=True)
    assert len(df_mtf) == len(df_m15), (
        f"alinear_h1_a_m15 cambió el número de filas ({len(df_mtf)} vs {len(df_m15)}) "
        "-- construir_bloques_walk_forward necesita el mismo largo para cortar los "
        "mismos boundaries de folds que el baseline."
    )
    return df_mtf


def generar_senales_mtf(df, use_session_filter=None):
    """Misma señal que generar_senales (mismo trigger EMA9/21), pero el filtro
    de tendencia deja de ser propio de M15 (close vs EMA50 M15) y pasa a ser la
    tendencia de H1 ya alineada por alinear_h1_a_m15. Experimento de una sola
    variable: qué timeframe define la tendencia, nada más cambia."""
    df["cruce_alcista"] = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1))
    df["cruce_bajista"] = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1))

    df["senal_compra"] = df["cruce_alcista"] & df["tendencia_alcista_h1"]
    df["senal_venta"] = df["cruce_bajista"] & df["tendencia_bajista_h1"]

    filtro_sesion = USE_SESSION_FILTER if use_session_filter is None else use_session_filter
    if filtro_sesion:
        hora = df["time"].dt.hour
        en_sesion = (hora >= SESSION_START_HOUR) & (hora < SESSION_END_HOUR)
        df["senal_compra"] = df["senal_compra"] & en_sesion
        df["senal_venta"] = df["senal_venta"] & en_sesion

    # mismo warm-up posicional que generar_senales: además de proteger la
    # tendencia (ya cubierto por el warm-up propio de H1), protege contra
    # cruces espurios de EMA9/21 M15 en sus propias primeras velas.
    warmup = df.index < EMA_TREND
    df.loc[warmup, "senal_compra"] = False
    df.loc[warmup, "senal_venta"] = False

    return df


def calcular_estructura_swings(df):
    """Tendencia definida por estructura de swings (Higher-High/Higher-Low =
    alcista, Lower-High/Lower-Low = bajista) en vez de por una EMA. Un swing
    en la barra i recién se puede CONFIRMAR en la barra i+SWING_R (una vez
    vistas las SWING_R barras siguientes) -- todo el desplazamiento de abajo
    existe para que ninguna fila use información de barras que todavía no
    "vivió" en ese punto del dataset."""
    df = df.copy()

    # --- 1. detección vectorizada (todavía no es "usable", ver paso 2) ---
    vecinos_high = pd.concat(
        [df["high"].shift(k) for k in list(range(1, SWING_L + 1)) + list(range(-1, -SWING_R - 1, -1))],
        axis=1,
    )
    ventana_high_completa = vecinos_high.notna().all(axis=1)
    swing_high_raw = (df["high"] > vecinos_high.max(axis=1)) & ventana_high_completa

    vecinos_low = pd.concat(
        [df["low"].shift(k) for k in list(range(1, SWING_L + 1)) + list(range(-1, -SWING_R - 1, -1))],
        axis=1,
    )
    ventana_low_completa = vecinos_low.notna().all(axis=1)
    swing_low_raw = (df["low"] < vecinos_low.min(axis=1)) & ventana_low_completa

    # --- 2. confirmación desplazada SWING_R barras: el valor detectado en la
    # fila i queda reubicado en la fila i+SWING_R, que solo depende de barras
    # <= i+SWING_R -- mismo principio que "valido_desde" en calcular_tendencia_h1,
    # acá posicional en barras en vez de en tiempo de calendario ---
    swing_high_confirmado = df["high"].where(swing_high_raw).shift(SWING_R)
    swing_low_confirmado = df["low"].where(swing_low_raw).shift(SWING_R)

    # --- 3. clasificación HH/LH y HL/LL sobre los pocos miles de swings
    # confirmados (barato, no hace falta vectorizar esto), + forward-fill ---
    def _clasificar(serie_confirmada, etiqueta_sube, etiqueta_baja):
        estado = pd.Series(np.nan, index=df.index, dtype=object)
        ultimo = None
        for idx, precio in serie_confirmada.dropna().items():
            if ultimo is not None:
                if precio > ultimo:
                    estado.loc[idx] = etiqueta_sube
                elif precio < ultimo:
                    estado.loc[idx] = etiqueta_baja
                # empate exacto: no se etiqueta -- no confirma ni rompe la
                # tendencia, puede ser solo resolución de tick del broker
            ultimo = precio
        return estado.ffill()

    estado_high_ff = _clasificar(swing_high_confirmado, "HH", "LH")
    estado_low_ff = _clasificar(swing_low_confirmado, "HL", "LL")

    df["tendencia_alcista_estructura"] = ((estado_high_ff == "HH") & (estado_low_ff == "HL")).fillna(False).astype(bool)
    df["tendencia_bajista_estructura"] = ((estado_high_ff == "LH") & (estado_low_ff == "LL")).fillna(False).astype(bool)

    # niveles crudos del ultimo swing high/low confirmado (forward-fill), expuestos
    # para reutilizar en calcular_rupturas_retest -- no es tendencia, es el precio
    # del swing en si, para poder comparar close/low/high contra el nivel roto.
    df["ultimo_swing_high"] = swing_high_confirmado.ffill()
    df["ultimo_swing_low"] = swing_low_confirmado.ffill()

    # --- 4. warm-up dependiente de datos: recién hay estructura clasificable
    # después del 2º swing confirmado de cada tipo (nada fijo como EMA_TREND) ---
    primer_valido_high = estado_high_ff.first_valid_index()
    primer_valido_low = estado_low_ff.first_valid_index()
    primer_valido = max(
        primer_valido_high if primer_valido_high is not None else len(df),
        primer_valido_low if primer_valido_low is not None else len(df),
    )
    warmup_estructura = max(EMA_TREND, primer_valido)
    print(f"Estructura de swings: warm-up calculado = {warmup_estructura} barras "
          f"(EMA_TREND={EMA_TREND}, 2º swing confirmado de cada tipo en fila {primer_valido}).")

    warmup = df.index < warmup_estructura
    df.loc[warmup, "tendencia_alcista_estructura"] = False
    df.loc[warmup, "tendencia_bajista_estructura"] = False

    return df


def generar_senales_estructura(df, use_session_filter=None):
    """Misma señal que generar_senales (mismo trigger EMA9/21), pero el filtro
    de tendencia deja de ser una EMA (M15 o H1) y pasa a ser estructura de
    swings (HH/HL vs LH/LL) ya calculada por calcular_estructura_swings.
    Tercera variante del mismo experimento de una sola variable."""
    df["cruce_alcista"] = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1))
    df["cruce_bajista"] = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1))

    df["senal_compra"] = df["cruce_alcista"] & df["tendencia_alcista_estructura"]
    df["senal_venta"] = df["cruce_bajista"] & df["tendencia_bajista_estructura"]

    filtro_sesion = USE_SESSION_FILTER if use_session_filter is None else use_session_filter
    if filtro_sesion:
        hora = df["time"].dt.hour
        en_sesion = (hora >= SESSION_START_HOUR) & (hora < SESSION_END_HOUR)
        df["senal_compra"] = df["senal_compra"] & en_sesion
        df["senal_venta"] = df["senal_venta"] & en_sesion

    # mismo warm-up posicional que generar_senales: protege contra cruces
    # espurios de EMA9/21 M15 en sus propias primeras velas (independiente de
    # cuál sea la fuente de tendencia).
    warmup = df.index < EMA_TREND
    df.loc[warmup, "senal_compra"] = False
    df.loc[warmup, "senal_venta"] = False

    return df


def calcular_rupturas_retest(df):
    """
    Trigger de entrada nuevo: ruptura de un swing confirmado (mismo fractal
    2-2 de calcular_estructura_swings) + retest de la zona rota. A
    diferencia de las variantes MTF/estructura, esto NO es un filtro de
    tendencia sobre el cruce EMA9/21 -- reemplaza el trigger por completo.

    Version SIMPLE de confirmacion (elegida sobre la version estricta con
    vela de rechazo, para minimizar variables nuevas en este primer test):
    la vela que toca la zona de retest confirma con solo cerrar del lado
    correcto del nivel roto.

    Ventana de retest (RETEST_VENTANA) y margen de zona (RETEST_MARGEN_ATR_MULT)
    quedan fijos, sin barrido -- mismo motivo.
    """
    df = calcular_estructura_swings(df)  # reutiliza la deteccion de swings ya construida; solo se usan los niveles, no la clasificacion HH/HL

    n = len(df)
    close = df["close"].to_numpy()
    low = df["low"].to_numpy()
    high = df["high"].to_numpy()
    atr = df["atr"].to_numpy()
    swing_high = df["ultimo_swing_high"].to_numpy()
    swing_low = df["ultimo_swing_low"].to_numpy()

    senal_compra = np.zeros(n, dtype=bool)
    senal_venta = np.zeros(n, dtype=bool)

    for i in range(1, n):
        # --- ruptura alcista: el cierre cruza por encima del ultimo swing high confirmado ---
        if not np.isnan(swing_high[i]) and not np.isnan(swing_high[i - 1]) and not np.isnan(atr[i]):
            if close[i] > swing_high[i] and close[i - 1] <= swing_high[i - 1]:
                nivel = swing_high[i]
                margen = RETEST_MARGEN_ATR_MULT * atr[i]
                for j in range(i + 1, min(i + RETEST_VENTANA + 1, n)):
                    if low[j] <= nivel + margen:
                        if close[j] > nivel:
                            senal_compra[j] = True
                        break  # un solo intento de retest -- confirmado o no, el evento se resuelve aca
                    if close[j] < nivel:
                        break  # cerro del lado equivocado antes de llegar a la zona -> ruptura invalidada

        # --- ruptura bajista: simetrico ---
        if not np.isnan(swing_low[i]) and not np.isnan(swing_low[i - 1]) and not np.isnan(atr[i]):
            if close[i] < swing_low[i] and close[i - 1] >= swing_low[i - 1]:
                nivel = swing_low[i]
                margen = RETEST_MARGEN_ATR_MULT * atr[i]
                for j in range(i + 1, min(i + RETEST_VENTANA + 1, n)):
                    if high[j] >= nivel - margen:
                        if close[j] < nivel:
                            senal_venta[j] = True
                        break
                    if close[j] > nivel:
                        break

    df["senal_compra"] = senal_compra
    df["senal_venta"] = senal_venta
    return df


def generar_senales_retest(df, use_session_filter=None):
    """Wrapper con la misma firma que generar_senales/_mtf/_estructura, para
    poder correr este trigger nuevo con la misma infra de folds (correr_fold
    recibe train_raw.copy()/test_raw.copy() de forma independiente por fold,
    asi que la deteccion de swings y el escaneo de retest quedan
    autocontenidos dentro de cada fold, sin fuga de informacion entre
    TRAIN/TEST de folds distintos)."""
    df = calcular_rupturas_retest(df)

    filtro_sesion = USE_SESSION_FILTER if use_session_filter is None else use_session_filter
    if filtro_sesion:
        hora = df["time"].dt.hour
        en_sesion = (hora >= SESSION_START_HOUR) & (hora < SESSION_END_HOUR)
        df["senal_compra"] = df["senal_compra"] & en_sesion
        df["senal_venta"] = df["senal_venta"] & en_sesion

    return df


def backtest(df, point_value=0.01, rr_ratio=None, sl_atr_mult=None):
    """
    Simula operaciones una a la vez (no pyramiding).
    Devuelve lista de trades con resultado en R (múltiplos de riesgo).

    `rr_ratio`/`sl_atr_mult` opcionales: si se pasan, tienen precedencia
    sobre los globals RR_RATIO/SL_ATR_MULT. Quien no los pasa obtiene el
    comportamiento de siempre (lee el global) -- retrocompatible con
    cualquier call-site existente.
    """
    rr = RR_RATIO if rr_ratio is None else rr_ratio
    sl_mult = SL_ATR_MULT if sl_atr_mult is None else sl_atr_mult

    trades = []
    posicion_abierta = None  # dict con datos de la posición

    for i in range(len(df)):
        row = df.iloc[i]

        # --- gestionar posición abierta ---
        if posicion_abierta is not None:
            tipo = posicion_abierta["tipo"]
            sl = posicion_abierta["sl"]
            tp = posicion_abierta["tp"]

            if tipo == "compra":
                if row["low"] <= sl:
                    trades.append({**posicion_abierta, "resultado_R": -1.0, "salida": "SL", "time_salida": row["time"]})
                    posicion_abierta = None
                elif row["high"] >= tp:
                    trades.append({**posicion_abierta, "resultado_R": rr, "salida": "TP", "time_salida": row["time"]})
                    posicion_abierta = None
            elif tipo == "venta":
                if row["high"] >= sl:
                    trades.append({**posicion_abierta, "resultado_R": -1.0, "salida": "SL", "time_salida": row["time"]})
                    posicion_abierta = None
                elif row["low"] <= tp:
                    trades.append({**posicion_abierta, "resultado_R": rr, "salida": "TP", "time_salida": row["time"]})
                    posicion_abierta = None

        # --- abrir nueva posición si no hay una abierta ---
        if posicion_abierta is None and not pd.isna(row["atr"]):
            riesgo = row["atr"] * sl_mult

            if row["senal_compra"]:
                entrada = row["close"]
                sl = entrada - riesgo
                tp = entrada + riesgo * rr
                posicion_abierta = {
                    "tipo": "compra", "entrada": entrada, "sl": sl, "tp": tp,
                    "time_entrada": row["time"]
                }
            elif row["senal_venta"]:
                entrada = row["close"]
                sl = entrada + riesgo
                tp = entrada - riesgo * rr
                posicion_abierta = {
                    "tipo": "venta", "entrada": entrada, "sl": sl, "tp": tp,
                    "time_entrada": row["time"]
                }

    return pd.DataFrame(trades)


def mostrar_resultados(trades_df):
    if trades_df.empty:
        print("No se generaron operaciones con esta configuración.")
        return

    n_trades = len(trades_df)
    ganadoras = (trades_df["resultado_R"] > 0).sum()
    perdedoras = (trades_df["resultado_R"] < 0).sum()
    win_rate = ganadoras / n_trades * 100
    r_total = trades_df["resultado_R"].sum()
    r_promedio = trades_df["resultado_R"].mean()

    # drawdown en términos de R acumulado
    equity_curve = trades_df["resultado_R"].cumsum()
    running_max = equity_curve.cummax()
    drawdown = equity_curve - running_max
    max_drawdown_R = drawdown.min()

    print("\n" + "=" * 50)
    print(f"RESULTADOS BACKTEST — {SYMBOL} — EMA {EMA_FAST}/{EMA_SLOW}/{EMA_TREND}")
    print("=" * 50)
    print(f"Total operaciones:     {n_trades}")
    print(f"Ganadoras:             {ganadoras}")
    print(f"Perdedoras:            {perdedoras}")
    print(f"Win rate:              {win_rate:.1f}%")
    print(f"R:R configurado:       1:{RR_RATIO}")
    print(f"R total acumulado:     {r_total:.2f}R")
    print(f"R promedio por trade:  {r_promedio:.3f}R")
    print(f"Máximo drawdown:       {max_drawdown_R:.2f}R")
    print("=" * 50)

    # Punto de equilibrio (win rate mínimo necesario para no perder, dado el R:R)
    breakeven_wr = 1 / (1 + RR_RATIO) * 100
    print(f"\nWin rate de equilibrio con R:R 1:{RR_RATIO} -> {breakeven_wr:.1f}%")
    if win_rate > breakeven_wr:
        print(f"✅ Tu win rate ({win_rate:.1f}%) está POR ENCIMA del equilibrio ({breakeven_wr:.1f}%) -> estrategia rentable en este período")
    else:
        print(f"❌ Tu win rate ({win_rate:.1f}%) está POR DEBAJO del equilibrio ({breakeven_wr:.1f}%) -> no rentable en este período")


def backtest_con_rr(df, rr_ratio):
    """Igual que backtest() pero permite variar el R:R sin tocar la entrada."""
    return backtest(df, rr_ratio=rr_ratio)


MIN_TRADES_SELECCION = 30   # piso de trades para que una config sea elegible en un barrido


def metrica_robusta(trades_df):
    """
    Estadístico tipo t sobre el resultado NETO de spread:
    mean(R_neto) / (std(R_neto)/sqrt(n)).

    Dos razones para no usar R total bruto acá:
    1. A diferencia del R total crudo, esta métrica no puede quedar
       dominada por una sola racha o un trade con TP enorme: exige que el
       edge sea consistente en relación a su propia variabilidad y al
       número de observaciones.
    2. El costo del spread en R depende de qué tan ajustado esté el SL
       (costo_R = spread / riesgo) -- una config puede verse mejor en
       bruto y ser peor en neto. Seleccionar sobre R neto evita elegir
       una configuración que en la práctica (con spread real) es peor.

    Exige un mínimo de MIN_TRADES_SELECCION trades: con muestras muy
    chicas el t-stat es inestable y puede quedar inflado por azar (un
    barrido de ~20-30 combinaciones sobre el mismo TRAIN ya de por sí
    aumenta el riesgo de que gane una configuración espuria; permitir que
    gane con n=3-5 lo empeora).
    """
    n = len(trades_df)
    if n < MIN_TRADES_SELECCION:
        return float("-inf")
    r_neto = descontar_spread(trades_df)["resultado_R_neto"]
    std = r_neto.std(ddof=1)
    if not std or pd.isna(std):
        return float("-inf")
    return r_neto.mean() / (std / np.sqrt(n))


def diagnostico_entrada_vs_salida(df, verbose=True):
    """
    Corre la MISMA señal de entrada con distintos R:R.
    Si el win rate se mantiene parecido en todos los R:R pero ninguno
    supera el punto de equilibrio -> el problema es la ENTRADA (la señal
    no predice dirección con fiabilidad suficiente).
    Si algún R:R sí supera el equilibrio -> el problema es la SALIDA
    (la entrada tiene algo de edge, pero el R:R/gestión actual lo desperdicia).
    """
    if verbose:
        print("\n" + "#" * 60)
        print("DIAGNÓSTICO: ¿el problema es la ENTRADA o la SALIDA?")
        print("#" * 60)

    resultados = []
    for rr in [1.0, 1.5, 2.0, 2.5, 3.0]:
        trades_df = backtest_con_rr(df, rr)
        if trades_df.empty:
            continue
        n = len(trades_df)
        wr = (trades_df["resultado_R"] > 0).sum() / n * 100
        r_total = trades_df["resultado_R"].sum()
        breakeven = 1 / (1 + rr) * 100
        edge = wr - breakeven
        tstat = metrica_robusta(trades_df)
        resultados.append((rr, n, wr, breakeven, r_total, edge, tstat))
        if verbose:
            estado = "✅ RENTABLE" if edge > 0 else "❌ pierde"
            print(f"R:R 1:{rr:<4} | Trades: {n:<4} | Win rate: {wr:5.1f}% | Equilibrio: {breakeven:5.1f}% | Edge: {edge:+5.1f}pp | R total: {r_total:+7.2f}R | t-stat(neto): {tstat:+.2f}  {estado}")

    if verbose:
        print("#" * 60)
        mejores = [r for r in resultados if r[5] > 0]
        if mejores:
            print(f"\n✅ Hay edge real en la entrada: {len(mejores)} de {len(resultados)} configuraciones de R:R son rentables.")
            print("   -> El problema NO es la señal de entrada en sí, es cómo gestionás la salida.")
            print("   -> Conviene enfocar el trabajo en break-even, trailing stop, o partial close.")
        else:
            print("\n❌ Ninguna configuración de R:R fue rentable con esta entrada.")
            print("   -> El problema está en la ENTRADA: la señal EMA+filtro no predice dirección de forma fiable.")
            print("   -> Conviene mejorar el filtro de entrada antes de optimizar la salida.")

    return resultados


def elegir_mejor_rr(resultados, default_rr=RR_RATIO):
    """Elige el R:R con mejor estadístico t (metrica_robusta), no el de
    mayor R total crudo -- así una sola racha o un trade con TP enorme no
    puede ganar el barrido por azar. `resultados` debe venir SOLO de datos
    de TRAIN — nunca de TEST, para no contaminar la validación posterior."""
    if not resultados:
        return default_rr
    mejor = max(resultados, key=lambda r: r[6])
    return mejor[0]


PARTIAL_TP_R = 1.5      # R al que se cierra el 50% de la posición
TRAIL_ATR_MULT = 1.5    # distancia del trailing stop en múltiplos de ATR


def backtest_partial_trailing(df):
    """
    Gestión de salida combinada:
    1. Se abre la posición completa (100%) con SL basado en ATR.
    2. Al llegar a PARTIAL_TP_R -> se cierra el 50% (ganancia asegurada)
       y el SL del 50% restante se mueve a break-even (precio de entrada).
    3. El 50% restante se gestiona con trailing stop basado en ATR:
       el SL sigue al precio a una distancia de TRAIL_ATR_MULT * ATR.
    4. Resultado final del trade = promedio ponderado 50%/50% en R.
    """
    trades = []
    pos = None

    for i in range(len(df)):
        row = df.iloc[i]

        if pos is not None:
            tipo = pos["tipo"]
            riesgo = pos["riesgo"]

            if tipo == "compra":
                pos["max_precio"] = max(pos["max_precio"], row["high"])

                # --- parte 1: aún no se tomó la ganancia parcial ---
                if not pos["parcial_tomado"]:
                    nivel_parcial = pos["entrada"] + riesgo * PARTIAL_TP_R
                    if row["low"] <= pos["sl"]:
                        # SL golpeado antes de llegar al parcial -> pérdida completa
                        trades.append({**pos, "resultado_R": -1.0, "salida": "SL_total"})
                        pos = None
                        continue
                    if row["high"] >= nivel_parcial:
                        pos["parcial_tomado"] = True
                        pos["r_parcial"] = PARTIAL_TP_R
                        pos["sl"] = pos["entrada"]  # break-even para el resto

                # --- parte 2: ya se tomó la ganancia parcial, trailing en el resto ---
                if pos is not None and pos["parcial_tomado"]:
                    nuevo_sl = pos["max_precio"] - row["atr"] * TRAIL_ATR_MULT
                    if nuevo_sl > pos["sl"]:
                        pos["sl"] = nuevo_sl  # el SL solo sube, nunca baja

                    if row["low"] <= pos["sl"]:
                        r_resto = (pos["sl"] - pos["entrada"]) / riesgo
                        r_final = 0.5 * pos["r_parcial"] + 0.5 * r_resto
                        trades.append({**pos, "resultado_R": r_final, "salida": "trailing"})
                        pos = None

            elif tipo == "venta":
                pos["min_precio"] = min(pos["min_precio"], row["low"])

                if not pos["parcial_tomado"]:
                    nivel_parcial = pos["entrada"] - riesgo * PARTIAL_TP_R
                    if row["high"] >= pos["sl"]:
                        trades.append({**pos, "resultado_R": -1.0, "salida": "SL_total"})
                        pos = None
                        continue
                    if row["low"] <= nivel_parcial:
                        pos["parcial_tomado"] = True
                        pos["r_parcial"] = PARTIAL_TP_R
                        pos["sl"] = pos["entrada"]

                if pos is not None and pos["parcial_tomado"]:
                    nuevo_sl = pos["min_precio"] + row["atr"] * TRAIL_ATR_MULT
                    if nuevo_sl < pos["sl"]:
                        pos["sl"] = nuevo_sl

                    if row["high"] >= pos["sl"]:
                        r_resto = (pos["entrada"] - pos["sl"]) / riesgo
                        r_final = 0.5 * pos["r_parcial"] + 0.5 * r_resto
                        trades.append({**pos, "resultado_R": r_final, "salida": "trailing"})
                        pos = None

        if pos is None and not pd.isna(row["atr"]):
            riesgo = row["atr"] * SL_ATR_MULT

            if row["senal_compra"]:
                entrada = row["close"]
                pos = {
                    "tipo": "compra", "entrada": entrada, "sl": entrada - riesgo,
                    "riesgo": riesgo, "max_precio": entrada,
                    "parcial_tomado": False, "r_parcial": 0.0,
                    "time_entrada": row["time"]
                }
            elif row["senal_venta"]:
                entrada = row["close"]
                pos = {
                    "tipo": "venta", "entrada": entrada, "sl": entrada + riesgo,
                    "riesgo": riesgo, "min_precio": entrada,
                    "parcial_tomado": False, "r_parcial": 0.0,
                    "time_entrada": row["time"]
                }

    return pd.DataFrame(trades)


def comparar_salida_fija_vs_combinada(df, rr_ratio=2.0):
    print("\n" + "#" * 60)
    print(f"COMPARACIÓN: TP fijo (1:{rr_ratio}) vs Partial Close + Trailing")
    print("#" * 60)

    fija = backtest_con_rr(df, rr_ratio)
    combinada = backtest_partial_trailing(df)

    for nombre, td in [(f"TP fijo 1:{rr_ratio}", fija), ("Partial+Trailing", combinada)]:
        if td.empty:
            print(f"{nombre}: sin operaciones")
            continue
        n = len(td)
        wr = (td["resultado_R"] > 0).sum() / n * 100
        r_total = td["resultado_R"].sum()
        r_prom = td["resultado_R"].mean()
        print(f"{nombre:<20} | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R | R promedio: {r_prom:+.3f}R")

    print("#" * 60)
    if not combinada.empty and not fija.empty:
        if combinada["resultado_R"].sum() > fija["resultado_R"].sum():
            print("\n✅ La gestión combinada (partial + trailing) mejora el resultado vs TP fijo.")
        else:
            print("\n❌ El TP fijo sigue siendo mejor que partial+trailing en este período/config.")


def backtest_trailing_con_mult(df, trail_mult, partial_r):
    """Igual que backtest_partial_trailing pero permite variar los parámetros sin tocar globals de forma permanente."""
    global TRAIL_ATR_MULT, PARTIAL_TP_R
    orig_trail, orig_partial = TRAIL_ATR_MULT, PARTIAL_TP_R
    TRAIL_ATR_MULT = trail_mult
    PARTIAL_TP_R = partial_r
    trades_df = backtest_partial_trailing(df)
    TRAIL_ATR_MULT, PARTIAL_TP_R = orig_trail, orig_partial
    return trades_df


def optimizar_trailing(df, verbose=True):
    if verbose:
        print("\n" + "#" * 60)
        print("BARRIDO: distintas distancias de trailing y niveles de parcial")
        print("#" * 60)

    mejor = None
    for partial_r in [1.5, 2.0, 2.5]:
        for trail_mult in [1.5, 2.0, 2.5, 3.0, 4.0]:
            td = backtest_trailing_con_mult(df, trail_mult, partial_r)
            if td.empty:
                continue
            n = len(td)
            wr = (td["resultado_R"] > 0).sum() / n * 100
            r_total = td["resultado_R"].sum()
            tstat = metrica_robusta(td)
            if verbose:
                print(f"Parcial 1:{partial_r} | Trailing {trail_mult}x ATR | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R | t-stat(neto): {tstat:+.2f}")
            if mejor is None or tstat > mejor[3]:
                mejor = (partial_r, trail_mult, r_total, tstat)

    if verbose:
        print("#" * 60)
        if mejor:
            print(f"\n🏆 Mejor combinación (in-sample, criterio t-stat): Parcial 1:{mejor[0]} + Trailing {mejor[1]}x ATR -> R total: {mejor[2]:+.2f}R (t-stat {mejor[3]:+.2f})")
            print("   Esta selección debe hacerse SOLO con datos de TRAIN — la confirmación con")
            print("   datos nunca vistos ocurre después, en la etapa de validación final.")
        else:
            print("\nNinguna combinación de trailing produjo operaciones.")

    return mejor


def validacion_train_test(train_df, test_df, rr_ratio):
    """
    Corre el TP fijo elegido (rr_ratio, seleccionado usando SOLO train_df en
    una etapa previa) sobre TRAIN y TEST por separado. TEST debe ser un
    tramo que no participó en ninguna selección de parámetros -- si el
    resultado se sostiene ahí, el edge probablemente es real y no overfitting.
    """
    print("\n" + "#" * 60)
    print(f"VALIDACIÓN TRAIN/TEST (TP fijo 1:{rr_ratio}) — ¿se sostiene el edge?")
    print("#" * 60)

    for nombre, sub_df in [("TRAIN (in-sample)", train_df), ("TEST (out-of-sample)", test_df)]:
        td = backtest_con_rr(sub_df, rr_ratio)
        if td.empty:
            print(f"{nombre}: sin operaciones")
            continue
        n = len(td)
        wr = (td["resultado_R"] > 0).sum() / n * 100
        r_total = td["resultado_R"].sum()
        breakeven = 1 / (1 + rr_ratio) * 100
        estado = "✅ RENTABLE" if wr > breakeven else "❌ pierde"
        print(f"{nombre:<22} | Trades: {n:<4} | Win rate: {wr:5.1f}% | Equilibrio: {breakeven:5.1f}% | R total: {r_total:+7.2f}R  {estado}")

    print("#" * 60)
    print("Si TEST también da rentable -> el edge probablemente es real, no solo ruido de la muestra.")
    print("Si TEST da negativo -> lo visto en TRAIN puede haber sido suerte (overfitting).")


def descontar_spread(trades_df, spread_puntos=SPREAD_PUNTOS, point_size=0.01):
    """
    Resta el costo del spread a cada trade, expresado en R.
    El spread se paga siempre (ganes o pierdas), así que se descuenta
    de TODOS los trades, no solo de los perdedores.

    El riesgo (denominador de costo_R) tiene que ser el riesgo ORIGINAL de
    entrada, no la distancia actual entrada-sl: en los trades de
    backtest_partial_trailing() el campo "sl" se va moviendo (a
    break-even y después con el trailing), así que en un trade que cierra
    justo en break-even, entrada-sl da 0 y el costo del spread se
    indefine (división por cero). Esos trades sí guardan el riesgo
    original sin mutar en la columna "riesgo"; se usa esa si está.
    """
    td = trades_df.copy()
    spread_precio = spread_puntos * point_size
    if "riesgo" in td.columns:
        riesgo = td["riesgo"]
    else:
        riesgo = (td["entrada"] - td["sl"]).abs()
    costo_R = spread_precio / riesgo
    td["resultado_R_neto"] = td["resultado_R"] - costo_R
    return td


def resumen_neto_vs_bruto(df, rr_ratio=2.5):
    """Corre la config ganadora (TP fijo, rr_ratio) y compara resultado bruto vs neto de spread."""
    print("\n" + "#" * 60)
    print(f"RENTABILIDAD NETA DE SPREAD (TP fijo 1:{rr_ratio}, spread={SPREAD_PUNTOS} puntos)")
    print("#" * 60)

    td = backtest_con_rr(df, rr_ratio)
    if td.empty:
        print("Sin operaciones.")
        return

    td = descontar_spread(td)
    n = len(td)

    wr_bruto = (td["resultado_R"] > 0).sum() / n * 100
    r_bruto = td["resultado_R"].sum()

    wr_neto = (td["resultado_R_neto"] > 0).sum() / n * 100
    r_neto = td["resultado_R_neto"].sum()

    costo_total_R = r_bruto - r_neto

    print(f"Trades: {n}")
    print(f"BRUTO (sin spread) | Win rate: {wr_bruto:5.1f}% | R total: {r_bruto:+7.2f}R")
    print(f"NETO  (con spread) | Win rate: {wr_neto:5.1f}% | R total: {r_neto:+7.2f}R")
    print(f"Costo total del spread: {costo_total_R:.2f}R ({costo_total_R/n:.4f}R por trade en promedio)")
    print("#" * 60)

    if r_neto > 0:
        print(f"✅ Sigue siendo rentable después de descontar spread: {r_neto:+.2f}R")
    else:
        print(f"❌ El spread se come toda la ventaja — no rentable en la práctica")

    td.to_csv("resultados_neto_spread.csv", index=False)
    print("\nDetalle guardado en resultados_neto_spread.csv")


def diagnostico_gap_entrada(df):
    """
    Cuantifica el sesgo de ejecución de backtest(): las entradas se simulan
    al close de la vela de señal, pero en real solo se puede operar recién
    en la vela siguiente (open + slippage). Mide, en unidades de R (riesgo =
    ATR * SL_ATR_MULT), cuánto se movió el precio entre ese close "de mentira"
    y el open real disponible al momento de poder operar.
    """
    print("\n" + "#" * 60)
    print("DIAGNÓSTICO: magnitud del gap close(señal) -> open(vela siguiente)")
    print("#" * 60)

    señal = df["senal_compra"] | df["senal_venta"]
    riesgo = df["atr"] * SL_ATR_MULT
    open_siguiente = df["open"].shift(-1)
    gap_R = ((open_siguiente - df["close"]).abs() / riesgo)[señal].dropna()

    if gap_R.empty:
        print("Sin señales para medir.")
        return

    print(f"Señales medidas: {len(gap_R)}")
    print(f"Gap medio:    {gap_R.mean():.3f}R")
    print(f"Gap mediana:  {gap_R.median():.3f}R")
    print(f"Gap p90:      {gap_R.quantile(0.90):.3f}R")
    print(f"Gap máximo:   {gap_R.max():.3f}R")
    print("#" * 60)
    print("Comparar esto contra el R promedio por trade reportado arriba: si el gap")
    print("típico es del mismo orden (o mayor) que el R promedio, el resultado del")
    print("backtest depende del fill imposible al close de la vela de señal.")


def sensibilidad_spread(df, rr_ratio=2.5, spreads=(30, 50, 80)):
    """Repite resumen_neto_vs_bruto para varios spreads, para ver qué tan
    sensible es la rentabilidad neta a un spread real más ancho que el
    configurado (SPREAD_PUNTOS), o a comisión/slippage no modelados."""
    print("\n" + "#" * 60)
    print(f"SENSIBILIDAD AL SPREAD (TP fijo 1:{rr_ratio})")
    print("#" * 60)

    td = backtest_con_rr(df, rr_ratio)
    if td.empty:
        print("Sin operaciones.")
        return
    n = len(td)
    r_bruto = td["resultado_R"].sum()
    print(f"Trades: {n} | BRUTO (sin spread): {r_bruto:+7.2f}R")

    for spread in spreads:
        tdn = descontar_spread(td, spread_puntos=spread)
        r_neto = tdn["resultado_R_neto"].sum()
        estado = "✅ RENTABLE" if r_neto > 0 else "❌ pierde"
        print(f"Spread {spread:>3} puntos | NETO: {r_neto:+7.2f}R  {estado}")

    print("#" * 60)


def comparar_con_sin_filtro_sesion(df_base, rr_ratio, verbose=True, fn_generar_senales=generar_senales):
    """Compara el resultado con y sin filtro de sesión horaria, mismo TP fijo.
    Devuelve True si conviene usar el filtro de sesión, según el estadístico
    t (metrica_robusta) obtenido en df_base (debe ser SOLO train)."""
    global USE_SESSION_FILTER
    if verbose:
        print("\n" + "#" * 60)
        print(f"COMPARACIÓN: con vs sin filtro de sesión horaria (TP fijo 1:{rr_ratio})")
        print("#" * 60)

    tstat_por_opcion = {}
    for activar, nombre in [(False, "SIN filtro de sesión"), (True, "CON filtro de sesión")]:
        USE_SESSION_FILTER = activar
        df2 = fn_generar_senales(df_base.copy())
        td = backtest_con_rr(df2, rr_ratio)
        USE_SESSION_FILTER = False  # restaurar
        if td.empty:
            if verbose:
                print(f"{nombre}: sin operaciones")
            tstat_por_opcion[activar] = float("-inf")
            continue
        n = len(td)
        wr = (td["resultado_R"] > 0).sum() / n * 100
        r_total = td["resultado_R"].sum()
        tstat = metrica_robusta(td)
        tstat_por_opcion[activar] = tstat
        if verbose:
            print(f"{nombre:<22} | Trades: {n:<4} | Win rate: {wr:5.1f}% | R total: {r_total:+7.2f}R | t-stat(neto): {tstat:+.2f}")

    if verbose:
        print("#" * 60)
    return tstat_por_opcion[True] > tstat_por_opcion[False]


def construir_bloques_walk_forward(df, n_folds):
    """
    Genera `n_folds` folds de walk-forward ANCLADO (expanding window): el
    histórico se parte en n_folds+1 bloques cronológicos contiguos y
    disjuntos. En el fold k, TRAIN es todo lo anterior al bloque k
    (bloques 0..k-1 concatenados) y TEST es el bloque k.

    A diferencia de un único split 70/30, cada TEST acá es un tramo
    disjunto y sucesivo del histórico -- cada fold evalúa un período de
    mercado distinto (un régimen de tendencia, una corrección, etc.) en vez
    de depender de si el último 30% del histórico fue representativo.
    """
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


def _rango_fechas(df):
    return f"{df['time'].iloc[0]:%Y-%m-%d} -> {df['time'].iloc[-1]:%Y-%m-%d}"


def correr_fold(train_raw, test_raw, fold_num, n_folds, fn_generar_senales=generar_senales):
    """
    Corre un fold completo de walk-forward: selecciona R:R, trailing y
    filtro de sesión usando SOLO train_raw (in-sample), y evalúa esa
    combinación UNA sola vez sobre test_raw (out-of-sample). Nada de lo que
    pasa acá vuelve a tocar test_raw para elegir parámetros.
    """
    print("\n" + "=" * 60)
    print(f"FOLD {fold_num}/{n_folds} — TRAIN: {len(train_raw)} velas ({_rango_fechas(train_raw)}) "
          f"| TEST: {len(test_raw)} velas ({_rango_fechas(test_raw)})")
    print("=" * 60)

    # El filtro de sesión se decide PRIMERO, con el R:R por defecto como
    # referencia, y recién después se tunean R:R y trailing sobre el TRAIN
    # ya filtrado. Si se hiciera al revés (tunear todo sin filtro y decidir
    # el filtro al final), el trailing/RR quedarían optimizados sobre un
    # conjunto de trades distinto al que después se evalúa en TEST.
    train_sin_filtro = fn_generar_senales(train_raw.copy())
    usar_filtro_sesion = comparar_con_sin_filtro_sesion(
        train_sin_filtro, RR_RATIO, verbose=False, fn_generar_senales=fn_generar_senales)

    train = fn_generar_senales(train_raw.copy(), use_session_filter=usar_filtro_sesion)

    resultados_rr = diagnostico_entrada_vs_salida(train, verbose=False)
    mejor_rr = elegir_mejor_rr(resultados_rr)

    mejor_trailing = optimizar_trailing(train, verbose=False)

    detalle_trailing = ""
    if mejor_trailing:
        detalle_trailing = f" | trailing: parcial 1:{mejor_trailing[0]} / {mejor_trailing[1]}x ATR"
    print(f"Parámetros elegidos in-sample (TRAIN de este fold): R:R 1:{mejor_rr} | "
          f"filtro sesión: {'CON' if usar_filtro_sesion else 'SIN'}{detalle_trailing}")

    # --- evaluación out-of-sample, una sola vez, con los parámetros ya fijados ---
    test = fn_generar_senales(test_raw.copy(), use_session_filter=usar_filtro_sesion)

    resultado = {
        "fold": fold_num, "n_train": len(train_raw), "n_test": len(test_raw),
        "rr": mejor_rr, "filtro_sesion": usar_filtro_sesion, "trailing": mejor_trailing,
        "n_trades_test": 0, "wr_test": None, "r_total_test": None,
        "r_neto_test": None, "rentable": None, "trades_test_df": pd.DataFrame(),
    }

    td_test = backtest_con_rr(test, mejor_rr)
    if td_test.empty:
        print("TEST (out-of-sample): sin operaciones.")
        return resultado

    n = len(td_test)
    wr = (td_test["resultado_R"] > 0).sum() / n * 100
    r_total = td_test["resultado_R"].sum()
    breakeven = 1 / (1 + mejor_rr) * 100
    r_neto = descontar_spread(td_test)["resultado_R_neto"].sum()
    rentable = wr > breakeven
    estado = "✅ RENTABLE" if rentable else "❌ pierde"
    print(f"TEST (out-of-sample) | Trades: {n:<4} | Win rate: {wr:5.1f}% | Equilibrio: {breakeven:5.1f}% | "
          f"R total: {r_total:+7.2f}R | Neto de spread: {r_neto:+7.2f}R  {estado}")

    if mejor_trailing:
        partial_r, trail_mult = mejor_trailing[0], mejor_trailing[1]
        td_trail = backtest_trailing_con_mult(test, trail_mult, partial_r)
        if not td_trail.empty:
            n_t = len(td_trail)
            r_total_t = td_trail["resultado_R"].sum()
            estado_t = "✅ RENTABLE" if r_total_t > 0 else "❌ pierde"
            print(f"  (trailing OOS)      | Trades: {n_t:<4} | R total: {r_total_t:+7.2f}R  {estado_t}")

    resultado.update(n_trades_test=n, wr_test=wr, r_total_test=r_total, r_neto_test=r_neto,
                      rentable=rentable, trades_test_df=td_test)
    return resultado


def resumen_walk_forward(resultados_folds):
    print("\n" + "#" * 60)
    print("RESUMEN WALK-FORWARD (cada fold = un período de mercado distinto)")
    print("#" * 60)
    for r in resultados_folds:
        filtro = "CON filtro" if r["filtro_sesion"] else "SIN filtro"
        if not r["n_trades_test"]:
            print(f"Fold {r['fold']} | R:R 1:{r['rr']} | {filtro} | TEST: sin operaciones")
            continue
        estado = "✅ RENTABLE" if r["rentable"] else "❌ pierde"
        print(f"Fold {r['fold']} | R:R 1:{r['rr']} | {filtro} | Trades: {r['n_trades_test']:<4} | "
              f"Win rate: {r['wr_test']:5.1f}% | R total: {r['r_total_test']:+7.2f}R | "
              f"Neto spread: {r['r_neto_test']:+7.2f}R  {estado}")

    print("#" * 60)
    validos = [r for r in resultados_folds if r["n_trades_test"]]
    rentables = [r for r in validos if r["rentable"]]
    rentables_neto = [r for r in validos if r["r_neto_test"] and r["r_neto_test"] > 0]

    if not validos:
        print("\nNingún fold generó operaciones en TEST.")
        return

    print(f"\nFolds rentables (bruto):        {len(rentables)}/{len(validos)}")
    print(f"Folds rentables (neto de spread): {len(rentables_neto)}/{len(validos)}")

    r_total_prom = sum(r["r_total_test"] for r in validos) / len(validos)
    trades_totales = sum(r["n_trades_test"] for r in validos)
    print(f"R total promedio por fold: {r_total_prom:+.2f}R | Trades TEST acumulados: {trades_totales}")

    # --- ¿el resultado agregado depende de un solo fold dominante? ---
    r_neto_total = sum(r["r_neto_test"] for r in validos)
    fold_max = max(validos, key=lambda r: r["r_neto_test"])
    if r_neto_total != 0:
        pct_dominante = fold_max["r_neto_test"] / r_neto_total * 100
        r_neto_sin_dominante = r_neto_total - fold_max["r_neto_test"]
        trades_sin_dominante = trades_totales - fold_max["n_trades_test"]
        print(f"\nFold más fuerte: Fold {fold_max['fold']} ({fold_max['r_neto_test']:+.2f}R neto) "
              f"-> {pct_dominante:.0f}% del R neto acumulado.")
        print(f"Sin ese fold: {r_neto_sin_dominante:+.2f}R neto en {trades_sin_dominante} trades "
              f"({r_neto_sin_dominante/trades_sin_dominante:+.3f}R/trade en promedio).")
        if pct_dominante > 60:
            print("⚠️  Un solo fold concentra la mayoría del resultado -- el agregado no es evidencia")
            print("   fuerte de un edge estable, aunque varios folds individuales den positivo.")

    if len(rentables) == len(validos):
        print("\n✅ El edge se sostuvo en TODOS los folds out-of-sample -> evidencia más fuerte de que es real,")
        print("   no depende de un único período/régimen de mercado.")
    elif len(rentables) >= len(validos) * 0.5:
        print("\n⚠️  El edge se sostuvo en algunos folds pero no en todos -> puede depender del régimen de")
        print("   mercado (tendencia vs rango, rally vs corrección). No lo trates como robusto todavía.")
    else:
        print("\n❌ El edge NO se sostuvo en la mayoría de los folds -> el resultado de un solo split")
        print("   70/30 anterior probablemente fue suerte de muestra (overfitting a un período puntual).")

    print("\nOjo: dentro de cada fold se siguen probando ~20 combinaciones (R:R x trailing x filtro de")
    print("sesión) sobre el TRAIN de ese fold antes de evaluar en su TEST. El criterio de selección ya")
    print("es un estadístico t (no R total crudo) para reducir el riesgo de un ganador espurio, pero la")
    print("búsqueda greedy en sí sigue estando presente en cada fold -- si el edge se sostiene en todos")
    print("los folds con esto, recién ahí conviene bajar más historial de MT5 para un test final nuevo.")


def comparar_variantes_walk_forward(resultados_a, resultados_b,
                                     nombre_a="Baseline (trend M15)", nombre_b="MTF (trend H1)"):
    """Compara fold a fold dos corridas de walk-forward sobre la MISMA partición
    de folds (misma cantidad de folds, mismos boundaries). Muestra también los
    parámetros in-sample elegidos por cada variante: RR/trailing/filtro de
    sesión pueden diferir legítimamente entre baseline y MTF en el mismo fold,
    y sin mostrarlos una diferencia de resultado se puede malinterpretar como
    "la tendencia H1 es mejor" cuando en realidad también cambió el RR elegido."""
    print("\n" + "#" * 60)
    print(f"COMPARACIÓN FOLD A FOLD: {nombre_a}  vs  {nombre_b}")
    print("#" * 60)

    for ra, rb in zip(resultados_a, resultados_b):
        estado_a = "sin trades" if not ra["n_trades_test"] else ("✅" if ra["rentable"] else "❌")
        estado_b = "sin trades" if not rb["n_trades_test"] else ("✅" if rb["rentable"] else "❌")
        r_neto_a = ra["r_neto_test"] or 0.0
        r_neto_b = rb["r_neto_test"] or 0.0
        delta = r_neto_b - r_neto_a
        print(f"\nFold {ra['fold']}:")
        print(f"  {nombre_a:<22} | R:R 1:{ra['rr']} | filtro sesión: {'CON' if ra['filtro_sesion'] else 'SIN'} | "
              f"trades: {ra['n_trades_test']:<4} | neto: {r_neto_a:+7.2f}R  {estado_a}")
        print(f"  {nombre_b:<22} | R:R 1:{rb['rr']} | filtro sesión: {'CON' if rb['filtro_sesion'] else 'SIN'} | "
              f"trades: {rb['n_trades_test']:<4} | neto: {r_neto_b:+7.2f}R  {estado_b}")
        print(f"  delta ({nombre_b} - {nombre_a}): {delta:+7.2f}R")

    # mismo chequeo de "fold dominante" que resumen_walk_forward, aplicado a la
    # variante MTF -- ese % de concentración es el criterio real de si esta
    # hipótesis mejoró algo (no solo si el R total subió).
    validos_b = [r for r in resultados_b if r["n_trades_test"]]
    if validos_b:
        r_neto_total_b = sum(r["r_neto_test"] for r in validos_b)
        fold_max_b = max(validos_b, key=lambda r: r["r_neto_test"])
        if r_neto_total_b != 0:
            pct_dominante_b = fold_max_b["r_neto_test"] / r_neto_total_b * 100
            print(f"\n[{nombre_b}] Fold más fuerte: Fold {fold_max_b['fold']} -> "
                  f"{pct_dominante_b:.0f}% del R neto acumulado.")
            print("(comparar este % contra el reportado arriba para el baseline en su propio resumen_walk_forward)")

    print("#" * 60)


def main():
    conectar_mt5()
    df_m15 = bajar_datos(SYMBOL, TIMEFRAME, N_VELAS)
    df_m15 = calcular_indicadores(df_m15)

    diagnostico_gap_entrada(generar_senales(df_m15.copy()))

    # --- datos del timeframe mayor para el filtro de tendencia MTF ---
    date_from_htf = df_m15["time"].min() - pd.Timedelta(days=BUFFER_DIAS_HTF)
    date_to_htf = df_m15["time"].max() + pd.Timedelta(hours=1)
    df_h1 = bajar_datos_rango(SYMBOL, HTF_TIMEFRAME, date_from_htf, date_to_htf)
    df_h1_tendencia = calcular_tendencia_h1(df_h1)
    df_mtf = alinear_h1_a_m15(df_m15, df_h1_tendencia)

    staleness_max = (df_mtf["time"] - df_mtf["valido_desde"]).max()
    print(f"\nAlineación MTF H1->M15: staleness máximo observado entre vela M15 y su H1 matcheada: {staleness_max}")

    # --- estructura de swings (HH/HL vs LH/LL) para el filtro de tendencia --
    # vive enteramente en M15, sin merge -> mismo largo/índice que df_m15.
    df_estructura = calcular_estructura_swings(df_m15)

    N_FOLDS = 9  # 10 bloques de ~1500 velas c/u -> mas poder estadistico que 4 folds

    folds_baseline = construir_bloques_walk_forward(df_m15, N_FOLDS)
    folds_mtf = construir_bloques_walk_forward(df_mtf, N_FOLDS)
    folds_estructura = construir_bloques_walk_forward(df_estructura, N_FOLDS)
    print(f"\nWalk-forward anclado: {N_FOLDS} folds sobre {len(df_m15)} velas totales "
          f"(TRAIN crece {len(df_m15)//(N_FOLDS+1)} velas por fold, TEST fijo de {len(df_m15)//(N_FOLDS+1)} velas c/u)")

    print("\n" + "=" * 60)
    print("VARIANTE BASELINE (filtro de tendencia propio de M15)")
    print("=" * 60)
    resultados_baseline = [
        correr_fold(train_raw, test_raw, i, N_FOLDS)
        for i, (train_raw, test_raw) in enumerate(folds_baseline, start=1)
    ]
    resumen_walk_forward(resultados_baseline)

    print("\n" + "=" * 60)
    print("VARIANTE MTF (filtro de tendencia de H1)")
    print("=" * 60)
    resultados_mtf = [
        correr_fold(train_raw, test_raw, i, N_FOLDS, fn_generar_senales=generar_senales_mtf)
        for i, (train_raw, test_raw) in enumerate(folds_mtf, start=1)
    ]
    resumen_walk_forward(resultados_mtf)

    print("\n" + "=" * 60)
    print("VARIANTE ESTRUCTURA (filtro de tendencia por swings HH/HL vs LH/LL)")
    print("=" * 60)
    resultados_estructura = [
        correr_fold(train_raw, test_raw, i, N_FOLDS, fn_generar_senales=generar_senales_estructura)
        for i, (train_raw, test_raw) in enumerate(folds_estructura, start=1)
    ]
    resumen_walk_forward(resultados_estructura)

    print("\n" + "=" * 60)
    print("VARIANTE RETEST (trigger nuevo: ruptura de swing + retest, sin EMA9/21)")
    print("=" * 60)
    resultados_retest = [
        correr_fold(train_raw, test_raw, i, N_FOLDS, fn_generar_senales=generar_senales_retest)
        for i, (train_raw, test_raw) in enumerate(folds_baseline, start=1)
    ]
    resumen_walk_forward(resultados_retest)

    comparar_variantes_walk_forward(resultados_baseline, resultados_mtf)
    comparar_variantes_walk_forward(resultados_baseline, resultados_estructura,
                                     nombre_b="Estructura (trend HH/HL)")
    comparar_variantes_walk_forward(resultados_mtf, resultados_estructura,
                                     nombre_a="MTF (trend H1)", nombre_b="Estructura (trend HH/HL)")
    comparar_variantes_walk_forward(resultados_baseline, resultados_retest,
                                     nombre_b="Retest (ruptura+retest)")

    mt5.shutdown()


if __name__ == "__main__":
    main()