"""
Prueba de resistencia (endurance) de la tarea clonada bajo LogonType=S4U.
=============================================================================

Es una copia de `log_senales_demo.py` con dos unicos cambios: escribe a
archivos de salida separados (para no mezclar datos con el logger
productivo) y agrega un latido periodico en el log, independiente de si
aparece o no una señal, para poder confirmar despues que el proceso
estuvo vivo y con MT5 conectado durante toda la ventana de prueba, no
solo al momento del ultimo chequeo.

La logica de deteccion de señales (calcular_indicadores / generar_senales)
se importa igual que en el logger productivo, sin reimplementar nada, para
que este test mida exactamente el mismo codigo bajo una sesion S4U en vez
de Interactive -- ver `log_senales_demo.py` para el detalle del enfoque.

USO (pensado para correr bajo la tarea Task Scheduler
EMA_XAUUSD_LiveSignalLogger_TEST con LogonType=S4U, no interactivamente):
    python "log_senales_demo_test_s4u.py"
"""
import importlib.util
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
DIR_PROYECTO = os.path.dirname(BACKTEST_PATH)
CSV_SALIDA = os.path.join(DIR_PROYECTO, "senales_demo_live_TEST.csv")
LOG_ERRORES = os.path.join(DIR_PROYECTO, "test_s4u_endurance.log")

POLL_SEGUNDOS = 30       # cada cuanto chequea si aparecio una vela M15 nueva cerrada
N_VELAS_CONTEXTO = 300   # velas de historia para calcular EMA/ATR con margen de sobra sobre el warm-up
LATIDO_CADA_SEGUNDOS = 300  # 5 min -- suficiente resolucion para detectar huecos en 24hs sin inflar el log

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # define funciones/constantes; NO corre main() porque __name__ != "__main__"


def log_evento(msg):
    linea = f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC | {msg}"
    print(linea, file=sys.stderr)
    with open(LOG_ERRORES, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def asegurar_csv():
    if not os.path.exists(CSV_SALIDA):
        columnas = [
            "timestamp_vela", "timestamp_deteccion_utc", "tipo",
            "close_vela", "ema_fast", "ema_slow", "ema_trend", "atr",
            "riesgo_teorico", "sl_teorico", "en_sesion_liquida",
            "bid_real", "ask_real", "spread_real_puntos",
            "precio_ref_real", "gap_vs_close_R",
        ]
        pd.DataFrame(columns=columnas).to_csv(CSV_SALIDA, index=False)


def intentar_conectar():
    ruta_terminal = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mod.mt5.initialize(path=ruta_terminal):
        log_evento(f"No se pudo conectar a MT5: {mod.mt5.last_error()}")
        return False
    print(f"Conectado a MT5: {mod.mt5.terminal_info()}")
    return True


def obtener_velas_cerradas():
    rates = mod.mt5.copy_rates_from_pos(mod.SYMBOL, mod.TIMEFRAME, 1, N_VELAS_CONTEXTO)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = mod.calcular_indicadores(df)
    mod.USE_SESSION_FILTER = False
    df = mod.generar_senales(df)
    return df


def procesar_senal(vela):
    tipo = "compra" if vela["senal_compra"] else "venta"
    close_vela = float(vela["close"])
    riesgo = float(vela["atr"]) * mod.SL_ATR_MULT
    sl_teorico = close_vela - riesgo if tipo == "compra" else close_vela + riesgo

    hora = vela["time"].hour
    en_sesion = mod.SESSION_START_HOUR <= hora < mod.SESSION_END_HOUR

    tick = mod.mt5.symbol_info_tick(mod.SYMBOL)
    info = mod.mt5.symbol_info(mod.SYMBOL)
    if tick is None or info is None:
        raise RuntimeError("symbol_info_tick/symbol_info devolvió None (¿símbolo no sincronizado en Market Watch?)")

    point = info.point
    bid, ask = tick.bid, tick.ask
    spread_real_puntos = (ask - bid) / point
    precio_ref_real = ask if tipo == "compra" else bid

    signo = 1 if tipo == "compra" else -1
    gap_vs_close_R = signo * (precio_ref_real - close_vela) / riesgo

    fila = {
        "timestamp_vela": vela["time"],
        "timestamp_deteccion_utc": datetime.now(timezone.utc),
        "tipo": tipo,
        "close_vela": close_vela,
        "ema_fast": float(vela["ema_fast"]), "ema_slow": float(vela["ema_slow"]), "ema_trend": float(vela["ema_trend"]),
        "atr": float(vela["atr"]),
        "riesgo_teorico": riesgo,
        "sl_teorico": sl_teorico,
        "en_sesion_liquida": en_sesion,
        "bid_real": bid, "ask_real": ask, "spread_real_puntos": spread_real_puntos,
        "precio_ref_real": precio_ref_real,
        "gap_vs_close_R": gap_vs_close_R,
    }
    pd.DataFrame([fila]).to_csv(CSV_SALIDA, mode="a", header=False, index=False)
    print(f"[{fila['timestamp_deteccion_utc']:%Y-%m-%d %H:%M:%S} UTC] SEÑAL {tipo.upper()} "
          f"| vela {vela['time']} | close {close_vela:.2f} | spread real {spread_real_puntos:.1f}pts "
          f"| gap vs close: {gap_vs_close_R:+.3f}R")


def main():
    asegurar_csv()
    print(f"[TEST S4U] Logger de señales EMA{mod.EMA_FAST}/{mod.EMA_SLOW}/{mod.EMA_TREND} + ATR{mod.ATR_PERIOD} arrancado.")
    print(f"Símbolo: {mod.SYMBOL} | Timeframe: M15 | Poll: cada {POLL_SEGUNDOS}s | Salida: {CSV_SALIDA}")
    print("Modo LOGGING PURO -- no envía órdenes. Ctrl+C para cortar.\n")
    log_evento(f"ARRANQUE del logger TEST S4U (nuevo proceso, PID sesion: {os.environ.get('SESSIONNAME', '?')})")

    conectado = False
    ultima_vela_procesada = None
    ultimo_latido = 0.0

    while True:
        try:
            if not conectado:
                conectado = intentar_conectar()

            if conectado:
                df = obtener_velas_cerradas()
                if df is not None:
                    if ultima_vela_procesada is None:
                        velas_nuevas = df.iloc[[-1]]
                    else:
                        velas_nuevas = df[df["time"] > ultima_vela_procesada]
                    for _, vela in velas_nuevas.iterrows():
                        if vela["senal_compra"] or vela["senal_venta"]:
                            procesar_senal(vela)
                        ultima_vela_procesada = vela["time"]

            ahora = time.monotonic()
            if ahora - ultimo_latido >= LATIDO_CADA_SEGUNDOS:
                log_evento(f"LATIDO | conectado={conectado} | ultima_vela_procesada={ultima_vela_procesada}")
                ultimo_latido = ahora

        except Exception as e:
            log_evento(f"Error en el loop: {e!r}")
            conectado = False

        time.sleep(POLL_SEGUNDOS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCortado por el usuario.")
    finally:
        try:
            mod.mt5.shutdown()
        except Exception:
            pass
