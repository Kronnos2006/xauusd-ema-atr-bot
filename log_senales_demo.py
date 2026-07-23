"""
Logger de señales en vivo para EMA9/21/50 + ATR sobre XAUUSD (M15) vía MT5.
=============================================================================

Modo LOGGING PURO -- NO ejecuta órdenes. Corre en loop, detecta cruces de
EMA sobre velas M15 ya CERRADAS usando exactamente la misma lógica que
`Backtest ema v4.py` (calcular_indicadores / generar_senales importadas de
ahí, no reimplementadas, para que no haya drift entre lo que se backtesteó
y lo que se loggea en vivo), y registra cada señal en un CSV con:

- el precio "teórico" que asume el backtest (close de la vela de señal)
- el precio/spread REAL de mercado en el momento en que el script detecta
  la señal (bid/ask real de MT5)

Eso permite comparar después, con datos reales y no supuestos, el spread
real contra el fijo de 30 puntos que usa el backtest de Python, y el gap
entre "entrar al close de la vela" (lo que simula el backtest) y el precio
realmente operable en el momento en que la señal está disponible -- el
mismo sesgo que ya se había diagnosticado con `diagnostico_gap_entrada`,
ahora medido con datos de mercado reales en vez de velas históricas.

No loggea con el filtro de sesión horaria aplicado: registra TODAS las
señales (EMA9/21 cross + filtro EMA50) y guarda una columna
`en_sesion_liquida` aparte, para poder filtrar por sesión en el análisis
posterior sin tener que decidir eso de antemano en el logger.

Pensado para correr desatendido en una terminal aparte durante semanas:
si se cae la conexión a MT5 o hay un error transitorio, lo loggea en
`senales_demo_live.log` y reintenta en el siguiente ciclo en vez de cortar
el proceso.

USO:
    python "log_senales_demo.py"
    (Ctrl+C para cortar limpio)

No hace falta MT5 en modo demo específicamente -- el logger es de solo
lectura, funciona igual conectado a una cuenta demo o real, porque nunca
manda órdenes. La decisión de operar manualmente cada señal loggeada (o
no) queda en vos.
"""
import importlib.util
import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd

BACKTEST_PATH = r"C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\Backtest ema v4.py"
DIR_PROYECTO = os.path.dirname(BACKTEST_PATH)
CSV_SALIDA = os.path.join(DIR_PROYECTO, "senales_demo_live.csv")
LOG_ERRORES = os.path.join(DIR_PROYECTO, "senales_demo_live.log")

POLL_SEGUNDOS = 30       # cada cuánto chequea si apareció una vela M15 nueva cerrada
N_VELAS_CONTEXTO = 300   # velas de historia para calcular EMA/ATR con margen de sobra sobre el warm-up

spec = importlib.util.spec_from_file_location("backtest_ema_v4", BACKTEST_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["backtest_ema_v4"] = mod
spec.loader.exec_module(mod)  # define funciones/constantes; NO corre main() porque __name__ != "__main__"


def log_error(msg):
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
    """Version resiliente de mod.conectar_mt5(): esa hace quit() si falla,
    lo cual mataria este proceso de fondo. Acá solo devuelve False y se
    reintenta en el proximo ciclo del loop."""
    ruta_terminal = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    if not mod.mt5.initialize(path=ruta_terminal):
        log_error(f"No se pudo conectar a MT5: {mod.mt5.last_error()}")
        return False
    print(f"Conectado a MT5: {mod.mt5.terminal_info()}")
    return True


def obtener_ultima_vela_cerrada():
    """Trae las ultimas N_VELAS_CONTEXTO velas M15 YA CERRADAS (pos=1 salta
    la vela en formacion) y corre la misma logica de indicadores/señales
    del backtest. Devuelve la fila de la vela cerrada mas reciente."""
    rates = mod.mt5.copy_rates_from_pos(mod.SYMBOL, mod.TIMEFRAME, 1, N_VELAS_CONTEXTO)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = mod.calcular_indicadores(df)
    mod.USE_SESSION_FILTER = False  # se loggean TODAS las señales; el filtro de sesion se aplica despues, en el analisis
    df = mod.generar_senales(df)
    return df.iloc[-1]


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
    print(f"Logger de señales EMA{mod.EMA_FAST}/{mod.EMA_SLOW}/{mod.EMA_TREND} + ATR{mod.ATR_PERIOD} arrancado.")
    print(f"Símbolo: {mod.SYMBOL} | Timeframe: M15 | Poll: cada {POLL_SEGUNDOS}s | Salida: {CSV_SALIDA}")
    print("Modo LOGGING PURO -- no envía órdenes. Ctrl+C para cortar.\n")
    # Se registra el arranque en el log de errores/eventos (no solo excepciones) para que
    # los cortes del proceso (ej: STATUS_CONTROL_C_EXIT por cierre de sesion/consola, no
    # capturable como excepcion de Python) queden visibles como un gap entre un "ARRANQUE"
    # y el siguiente, en vez de depender de chequear el PID a mano para notarlos.
    log_error("ARRANQUE del logger (nuevo proceso)")

    conectado = False
    ultima_vela_procesada = None

    while True:
        try:
            if not conectado:
                conectado = intentar_conectar()

            if conectado:
                vela = obtener_ultima_vela_cerrada()
                if vela is not None and vela["time"] != ultima_vela_procesada:
                    if vela["senal_compra"] or vela["senal_venta"]:
                        procesar_senal(vela)  # si tira excepcion, NO se marca la vela como procesada -> se reintenta
                    ultima_vela_procesada = vela["time"]

        except Exception as e:
            log_error(f"Error en el loop: {e!r}")
            conectado = False  # fuerza reconexión en la próxima vuelta

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
