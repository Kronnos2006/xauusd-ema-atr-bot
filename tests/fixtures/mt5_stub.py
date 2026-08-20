"""Stub de MetaTrader5 para poder importar "Backtest ema v4.py" y sus
funciones puras (calcular_indicadores, generar_senales, backtest,
metrica_robusta, construir_bloques_walk_forward, etc.) en un entorno sin el
paquete real MetaTrader5 (Windows-only, no instalable en este sandbox Linux).

No reemplaza al paquete real en producción -- ahí sigue corriendo contra el
terminal MT5 real en Windows. Esto solo satisface el `import MetaTrader5 as
mt5` a nivel de módulo para poder testear el resto del pipeline, que no
llama a ninguna función de mt5.* fuera de bajar_datos/bajar_datos_rango/
conectar_mt5.

Genera velas OHLC sintéticas pero deterministas (misma clave -> mismos
datos), para poder probar data_cache.py sin depender de un broker real.
"""

import numpy as np

TIMEFRAME_M15 = 15
TIMEFRAME_H1 = 60

_RATE_DTYPE = [
    ("time", "i8"),
    ("open", "f8"),
    ("high", "f8"),
    ("low", "f8"),
    ("close", "f8"),
    ("tick_volume", "i8"),
    ("spread", "i4"),
    ("real_volume", "i8"),
]

call_log = []  # cada llamada a copy_rates_* se registra acá para poder espiar en tests


def _reset_call_log():
    call_log.clear()


def _velas_sinteticas(n, seed, timeframe_seconds, start_epoch=1_700_000_000):
    rng = np.random.default_rng(seed)
    precios = 2000.0 + np.cumsum(rng.normal(0, 1.0, size=n))
    rates = np.zeros(n, dtype=_RATE_DTYPE)
    rates["time"] = start_epoch + np.arange(n) * timeframe_seconds
    rates["open"] = precios
    rates["high"] = precios + np.abs(rng.normal(0, 0.5, size=n))
    rates["low"] = precios - np.abs(rng.normal(0, 0.5, size=n))
    rates["close"] = precios + rng.normal(0, 0.2, size=n)
    rates["tick_volume"] = 100
    rates["spread"] = 30
    rates["real_volume"] = 0
    return rates


def initialize(path=None):
    return True


def last_error():
    return (0, "stub: sin error")


def terminal_info():
    return {"stub": True}


def shutdown():
    return None


def copy_rates_from_pos(symbol, timeframe, start_pos, n_velas):
    call_log.append(("copy_rates_from_pos", symbol, timeframe, start_pos, n_velas))
    seed = abs(hash((symbol, timeframe, n_velas))) % (2**32)
    return _velas_sinteticas(n_velas, seed, timeframe * 60)


def copy_rates_range(symbol, timeframe, date_from, date_to):
    call_log.append(("copy_rates_range", symbol, timeframe, str(date_from), str(date_to)))
    dias = max((date_to - date_from).days, 1)
    velas_por_dia = max(int(24 * 60 * 60 / (timeframe * 60)), 1)
    n = dias * velas_por_dia
    seed = abs(hash((symbol, timeframe, str(date_from), str(date_to)))) % (2**32)
    return _velas_sinteticas(n, seed, timeframe * 60)
