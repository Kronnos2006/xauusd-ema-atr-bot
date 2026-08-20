"""
Prueba puntual (no el logger productivo): intenta conectarse a MT5 y
registra el resultado en test_s4u_result.log. Pensado para correr una
sola vez bajo la tarea clonada EMA_XAUUSD_LiveSignalLogger_TEST con
LogonType=S4U, para confirmar si MT5 puede inicializarse sin sesion
interactiva antes de tocar la tarea productiva.
"""
import os
from datetime import datetime, timezone

import MetaTrader5 as mt5

DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(DIR_PROYECTO, "test_s4u_result.log")


def log(msg):
    linea = f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S} UTC | {msg}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def main():
    log(f"Arranque prueba S4U (PID sesion: {os.environ.get('SESSIONNAME', '?')})")
    ok = mt5.initialize(path=r"C:\Program Files\MetaTrader 5\terminal64.exe")
    if ok:
        info = mt5.terminal_info()
        log(f"OK conectado: {info}")
        tick = mt5.symbol_info_tick("XAUUSD")
        log(f"Tick XAUUSD: {tick}")
    else:
        log(f"FALLO conectar: {mt5.last_error()}")
    mt5.shutdown()
    log("Fin prueba S4U")


if __name__ == "__main__":
    main()
