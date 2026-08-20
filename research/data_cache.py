"""Snapshot local de datos OHLC, keyed por symbol+timeframe+rango.

Resuelve el bloqueador principal de determinismo del motor: hoy
`bajar_datos_rango()` en "Backtest ema v4.py" pega en vivo al terminal MT5 en
cada corrida, sin caché -- imposible garantizar "mismos datos" entre
corridas. Este módulo antepone un chequeo de archivo local: si ya existe un
snapshot para esa clave (symbol, timeframe, rango de fechas), lo lee de ahí
y nunca vuelve a tocar MT5; si no existe, llama a `bajar_datos_rango()` una
única vez, lo persiste como CSV y lo devuelve.

No modifica `bajar_datos_rango()` -- lo envuelve. Los scripts de hipótesis
que la llaman directo (fuera de `research/`) siguen funcionando exactamente
igual, sin caché.
"""

import hashlib
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from research._engine_loader import cargar_engine

DEFAULT_CACHE_DIR = Path(__file__).resolve().parent.parent / "data_snapshots"

_TIMEFRAME_LABELS = {"M15": "TIMEFRAME_M15", "H1": "TIMEFRAME_H1"}


def _resolver_timeframe(engine, timeframe_label):
    if timeframe_label not in _TIMEFRAME_LABELS:
        raise ValueError(
            f"timeframe_label desconocido: {timeframe_label!r}. "
            f"Válidos: {sorted(_TIMEFRAME_LABELS)}"
        )
    return getattr(engine.mt5, _TIMEFRAME_LABELS[timeframe_label])


def _nombre_snapshot(symbol, timeframe_label, date_from, date_to):
    return f"{symbol}_{timeframe_label}_{date_from:%Y-%m-%d}_{date_to:%Y-%m-%d}.csv"


def _sha256_de_archivo(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def get_or_fetch(symbol, timeframe_label, date_from, date_to, cache_dir=None):
    """Devuelve (df, content_hash, cache_path) para symbol+timeframe_label+rango.

    `date_from`/`date_to` deben ser `datetime.date` o `datetime.datetime`
    (mismo tipo que espera `bajar_datos_rango`).
    """
    if not isinstance(date_from, (date, datetime)) or not isinstance(date_to, (date, datetime)):
        raise TypeError("date_from/date_to deben ser date o datetime")

    cache_dir = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
    cache_path = cache_dir / _nombre_snapshot(symbol, timeframe_label, date_from, date_to)

    if not cache_path.exists():
        engine = cargar_engine()
        timeframe = _resolver_timeframe(engine, timeframe_label)
        df = engine.bajar_datos_rango(symbol, timeframe, date_from, date_to)
        cache_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_path, index=False)

    df = pd.read_csv(cache_path, parse_dates=["time"])
    content_hash = _sha256_de_archivo(cache_path)
    return df, content_hash, cache_path
