"""
Feed real de MetaTrader 5. Solo corre en Windows con MT5 instalado.
El import es perezoso a proposito: el resto del bot no debe romperse
en una maquina sin MT5.

CLAVE: descarta siempre la ultima vela que devuelve copy_rates_from_pos,
porque esta en formacion. Operar sobre ella es la causa numero uno de
backtests que no se replican en vivo.
"""
import time
from datetime import datetime, timezone
from typing import Iterator, Optional

from contracts import Candle, Snapshot
from feeds.base import Feed

_TF = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 16385, "H4": 16388, "D1": 16408}


class Mt5Feed(Feed):

    def __init__(self, symbol="XAUUSD", timeframe="M15", window=100,
                 poll_seconds=5):
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise RuntimeError(
                "MetaTrader5 no esta disponible. Instalalo en Windows con "
                "'pip install MetaTrader5', o usa SyntheticFeed/CsvFeed."
            ) from exc
        self._mt5 = mt5
        self.symbol, self.timeframe = symbol, timeframe
        self.window, self.poll_seconds = window, poll_seconds
        if not mt5.initialize():
            raise RuntimeError(f"initialize() fallo: {mt5.last_error()}")
        if not mt5.symbol_select(symbol, True):
            raise RuntimeError(f"symbol_select({symbol}) fallo")

    def _fetch(self):
        # +1 porque descartamos la ultima (en formacion)
        rates = self._mt5.copy_rates_from_pos(
            self.symbol, _TF[self.timeframe], 0, self.window + 1)
        if rates is None or len(rates) < self.window + 1:
            return None
        return [
            Candle(datetime.fromtimestamp(r["time"], tz=timezone.utc),
                   float(r["open"]), float(r["high"]), float(r["low"]),
                   float(r["close"]), float(r["tick_volume"]), closed=True)
            for r in rates[:-1]          # <-- se descarta la vela viva
        ]

    def stream(self) -> Iterator[Optional[Snapshot]]:
        """
        Emite un Snapshot cuando cierra una vela nueva, y None en cada
        sondeo intermedio. El None NO es un error: es "sigo vivo, nada
        nuevo". Sin el, el runner se queda mudo hasta 15 minutos en M15
        y no se distingue de un proceso colgado.
        """
        last_time = None
        while True:
            candles = self._fetch()
            if candles and candles[-1].time != last_time:
                last_time = candles[-1].time
                yield Snapshot(self.symbol, self.timeframe, candles)
            else:
                yield None
            time.sleep(self.poll_seconds)

    def close(self):
        self._mt5.shutdown()
