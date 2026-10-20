"""
Logger en vivo -- hipótesis macro DFII10 fase 1 (tasas reales), modo LOGGING PURO.
=============================================================================

Misma disciplina que `log_senales_demo.py`: NO ejecuta órdenes, solo registra
qué habría hecho la regla ya validada por walk-forward (ver
`hipotesis_macro_dfii10.py` y la memoria del proyecto:
`project_hipotesis_macro_dfii10_fase1.md`) contra datos genuinamente nuevos
hacia adelante -- el objetivo de este logger es evitar que la "confirmación"
de la hipótesis dependa de otra vuelta de análisis retrospectivo sobre el
mismo tramo 2003-2026 (mismo riesgo de multiple-comparisons que ya se evitó
en el resto del proyecto).

Config fija (la que ganó el walk-forward, N=60/M=5 elegido en TRAIN en 3 de
4 folds -- no se vuelve a barrer la grilla acá, es observación forward de
UNA sola config ya elegida):
  N = 60 días hábiles de caída sostenida en DFII10
  M = 5 sesiones de horizonte de salida (o SL por ATR, lo que ocurra primero)

Misma lógica de detección de episodios que el backtest (importada de
`hipotesis_macro_dfii10.py`, no reimplementada, para que no haya drift entre
lo que se backtesteó y lo que se loggea en vivo -- mismo criterio que ya se
sigue en `log_senales_demo.py`).

Sin pyramiding: como en el backtest, mientras haya una posición "abierta"
(en el sentido de este logger de solo-lectura) se ignoran episodios nuevos.

USO:
    python "log_senal_macro_dfii10.py"
    (Ctrl+C para cortar limpio)
"""
import importlib.util
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

import pandas as pd

DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))
BACKTEST_PATH = os.path.join(DIR_PROYECTO, "Backtest ema v4.py")
HIPOTESIS_PATH = os.path.join(DIR_PROYECTO, "hipotesis_macro_dfii10.py")

CSV_SALIDA = os.path.join(DIR_PROYECTO, "senal_macro_dfii10_live.csv")
LOG_ERRORES = os.path.join(DIR_PROYECTO, "senal_macro_dfii10_live.log")
ESTADO_PATH = os.path.join(DIR_PROYECTO, "estado_macro_dfii10.json")
DFII10_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFII10"

N_FIJO = 60   # config ganadora del walk-forward (elegida en TRAIN en 3/4 folds) -- fija, no se vuelve a elegir acá
M_FIJO = 5
DIAS_LOOKBACK_ORO = 400   # margen de sobra sobre N=60 dias habiles + warm-up de ATR14
POLL_SEGUNDOS = 3600      # DFII10 y el cierre diario de oro no cambian mas rapido que 1 vez/dia -- 1h alcanza de sobra

spec_bt = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec_bt)
sys.modules["backtest_ema_v4"] = mod
spec_bt.loader.exec_module(mod)

spec_hip = importlib.util.spec_from_file_location("hipotesis_macro_dfii10", HIPOTESIS_PATH)
hip = importlib.util.module_from_spec(spec_hip)
sys.modules["hipotesis_macro_dfii10"] = hip
spec_hip.loader.exec_module(hip)  # no corre main(); reusa detectar_inicios_episodio() sin reimplementarla


def log_evento(msg):
    linea = f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC | {msg}"
    print(linea, file=sys.stderr)
    with open(LOG_ERRORES, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def asegurar_csv():
    if not os.path.exists(CSV_SALIDA):
        columnas = [
            "evento", "fecha_evento_utc", "fecha_inicio_episodio", "fecha_entrada",
            "entrada", "sl", "riesgo", "fecha_salida", "resultado_R", "motivo_salida",
        ]
        pd.DataFrame(columns=columnas).to_csv(CSV_SALIDA, index=False)


def cargar_estado():
    if os.path.exists(ESTADO_PATH):
        with open(ESTADO_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"ultima_fecha_dfii10_procesada": None, "episodio_pendiente": None, "posicion_abierta": None}


def guardar_estado(estado):
    with open(ESTADO_PATH, "w", encoding="utf-8") as f:
        json.dump(estado, f, indent=2, default=str)


def registrar_evento(evento, **campos):
    fila = {
        "evento": evento, "fecha_evento_utc": datetime.now(timezone.utc),
        "fecha_inicio_episodio": None, "fecha_entrada": None, "entrada": None,
        "sl": None, "riesgo": None, "fecha_salida": None, "resultado_R": None, "motivo_salida": None,
    }
    fila.update(campos)
    pd.DataFrame([fila]).to_csv(CSV_SALIDA, mode="a", header=False, index=False)
    print(f"[{fila['fecha_evento_utc']:%Y-%m-%d %H:%M:%S} UTC] {evento} | {campos}")


def descargar_dfii10():
    urllib.request.urlretrieve(DFII10_URL, os.path.join(DIR_PROYECTO, "historial", "dfii10.csv"))
    df = pd.read_csv(os.path.join(DIR_PROYECTO, "historial", "dfii10.csv"))
    df.columns = ["fecha", "dfii10"]
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["dfii10"] = pd.to_numeric(df["dfii10"], errors="coerce")
    return df.dropna(subset=["dfii10"]).reset_index(drop=True)


def intentar_conectar():
    """Version resiliente de mod.conectar_mt5(): esa hace quit() si falla,
    lo cual mataria este proceso de fondo. Igual que en log_senales_demo.py."""
    ruta_terminal = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mod.mt5.initialize(path=ruta_terminal):
        log_evento(f"No se pudo conectar a MT5: {mod.mt5.last_error()}")
        return False
    return True


def bajar_oro_reciente():
    """No usa mod.bajar_datos_rango() a proposito: esa hace quit() si
    copy_rates_range falla, lo cual mataria este proceso de fondo. Igual
    criterio que log_senales_demo.py -- llama a la API de mt5 directo y
    devuelve None en vez de cortar el proceso, para reintentar en el
    siguiente ciclo."""
    fecha_desde = pd.Timestamp.now() - pd.Timedelta(days=DIAS_LOOKBACK_ORO)
    rates = mod.mt5.copy_rates_range(mod.SYMBOL, mod.mt5.TIMEFRAME_D1, fecha_desde, pd.Timestamp.now())
    if rates is None or len(rates) == 0:
        log_evento(f"No se pudieron bajar datos de oro: {mod.mt5.last_error()}")
        return None
    diario = pd.DataFrame(rates)
    diario["fecha"] = pd.to_datetime(diario["time"], unit="s").dt.normalize()
    diario = mod.calcular_indicadores(diario)  # reusa la misma formula de ATR14 del proyecto, sin reimplementarla
    return diario.reset_index(drop=True)


def ciclo(estado):
    df_dfii10 = descargar_dfii10()
    df_oro = bajar_oro_reciente()
    if df_oro is None or df_oro.empty:
        return estado, False  # bajar_oro_reciente ya loggeo el motivo; se reintenta en el proximo ciclo

    # --- 1. posicion abierta: chequear SL o cierre por horizonte M ---
    pos = estado.get("posicion_abierta")
    if pos is not None:
        fecha_entrada = pd.Timestamp(pos["fecha_entrada"])
        velas_desde_entrada = df_oro[df_oro["fecha"] > fecha_entrada].reset_index(drop=True)
        cerrada = False
        for i, fila in velas_desde_entrada.iterrows():
            if fila["low"] <= pos["sl"]:
                registrar_evento(
                    "SALIDA", fecha_inicio_episodio=pos["fecha_inicio_episodio"],
                    fecha_entrada=pos["fecha_entrada"], entrada=pos["entrada"], sl=pos["sl"],
                    riesgo=pos["riesgo"], fecha_salida=str(fila["fecha"]), resultado_R=-1.0,
                    motivo_salida="SL_ATR")
                estado["posicion_abierta"] = None
                cerrada = True
                break
            if i + 1 >= M_FIJO:  # M-esima sesion desde la entrada alcanzada sin tocar el SL antes
                resultado_R = (float(fila["close"]) - pos["entrada"]) / pos["riesgo"]
                registrar_evento(
                    "SALIDA", fecha_inicio_episodio=pos["fecha_inicio_episodio"],
                    fecha_entrada=pos["fecha_entrada"], entrada=pos["entrada"], sl=pos["sl"],
                    riesgo=pos["riesgo"], fecha_salida=str(fila["fecha"]), resultado_R=resultado_R,
                    motivo_salida="HORIZONTE")
                estado["posicion_abierta"] = None
                cerrada = True
                break
        if not cerrada:
            pos["sesiones_transcurridas"] = len(velas_desde_entrada)
            estado["posicion_abierta"] = pos

    # --- 2. episodio pendiente de entrada: confirmar D+1 si ya cerro una vela de oro posterior ---
    pendiente = estado.get("episodio_pendiente")
    if pendiente is not None and estado.get("posicion_abierta") is None:
        fecha_inicio = pd.Timestamp(pendiente["fecha_inicio"])
        velas_post = df_oro[df_oro["fecha"] > fecha_inicio]
        if not velas_post.empty:
            fila_entrada = velas_post.iloc[0]
            if not pd.isna(fila_entrada["atr"]):
                entrada = float(fila_entrada["close"])
                riesgo = float(fila_entrada["atr"]) * mod.SL_ATR_MULT
                sl = entrada - riesgo
                nueva_pos = {
                    "fecha_inicio_episodio": str(fecha_inicio), "fecha_entrada": str(fila_entrada["fecha"]),
                    "entrada": entrada, "sl": sl, "riesgo": riesgo, "sesiones_transcurridas": 0,
                }
                registrar_evento(
                    "ENTRADA", fecha_inicio_episodio=str(fecha_inicio), fecha_entrada=str(fila_entrada["fecha"]),
                    entrada=entrada, sl=sl, riesgo=riesgo)
                estado["posicion_abierta"] = nueva_pos
            estado["episodio_pendiente"] = None

    # --- 3. detectar episodios nuevos (solo si no hay posicion abierta ni pendiente: sin pyramiding) ---
    # Primer arranque (ultima_procesada is None): NO se backfillea ningun episodio historico como
    # "pendiente" -- entrar hoy con precio de hoy sobre una señal de hace semanas/meses no es lo
    # mismo que la regla validada (D+1 del dia real de la señal). Solo se fija el punto de partida
    # y se observa hacia adelante desde el proximo ciclo.
    ultima_procesada = estado.get("ultima_fecha_dfii10_procesada")
    if ultima_procesada is None:
        log_evento(f"Primer arranque: fijando punto de partida en {df_dfii10['fecha'].iloc[-1]} "
                    f"sin backfillear episodios historicos como pendientes.")
    elif estado.get("posicion_abierta") is None and estado.get("episodio_pendiente") is None:
        inicios = hip.detectar_inicios_episodio(df_dfii10, N_FIJO)
        nuevos = [f for f in inicios if pd.Timestamp(f) > pd.Timestamp(ultima_procesada)]
        if nuevos:
            fecha_inicio = nuevos[-1]  # el mas reciente, por si hubo mas de uno en el gap entre ciclos
            estado["episodio_pendiente"] = {"fecha_inicio": str(fecha_inicio)}
            registrar_evento("EPISODIO_DETECTADO", fecha_inicio_episodio=str(fecha_inicio))
            log_evento(f"Episodio nuevo detectado (N={N_FIJO}): inicio {fecha_inicio}. "
                       f"Entrada planificada al cierre de la siguiente sesion de oro.")

    if not df_dfii10.empty:
        estado["ultima_fecha_dfii10_procesada"] = str(df_dfii10["fecha"].iloc[-1])

    return estado, True


def main():
    asegurar_csv()
    print(f"[MACRO DFII10] Logger en vivo arrancado -- N={N_FIJO}, M={M_FIJO} (config ganadora del walk-forward).")
    print(f"Salida: {CSV_SALIDA} | Poll: cada {POLL_SEGUNDOS}s | Modo LOGGING PURO -- no envía órdenes.\n")
    log_evento("ARRANQUE del logger macro DFII10 (nuevo proceso)")

    estado = cargar_estado()
    conectado = False
    fallos_consecutivos = 0
    UMBRAL_RECONEXION = 3  # fallos de IPC seguidos (a POLL_SEGUNDOS=3600, ~3hs) antes de forzar shutdown+initialize

    while True:
        try:
            if not conectado:
                conectado = intentar_conectar()

            if conectado:
                estado, oro_ok = ciclo(estado)
                guardar_estado(estado)
                if oro_ok:
                    fallos_consecutivos = 0
                else:
                    fallos_consecutivos += 1
                    if fallos_consecutivos >= UMBRAL_RECONEXION:
                        log_evento(f"{fallos_consecutivos} fallos de IPC seguidos -- forzando "
                                   f"mt5.shutdown()+initialize() para recuperar la conexion.")
                        mod.mt5.shutdown()
                        conectado = False
                        fallos_consecutivos = 0
        except Exception as e:
            log_evento(f"Error en el loop: {e!r}")
            conectado = False  # fuerza reconexión en la próxima vuelta
            fallos_consecutivos = 0

        time.sleep(POLL_SEGUNDOS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCortado por el usuario.")
