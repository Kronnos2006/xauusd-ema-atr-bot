"""
Feed sintetico y de CSV. Corre en cualquier lado, sin bróker, sin MT5.
Es con lo que probas los pasos 4 a 10 antes de tocar una cuenta.
"""
import csv
import random
from datetime import datetime, timedelta
from typing import Iterator, List

from contracts import Candle, Snapshot
from feeds.base import Feed


def _walk(n: int, start_price: float, start_time: datetime,
          minutes: int, seed: int) -> List[Candle]:
    rng = random.Random(seed)
    candles, price, t = [], start_price, start_time
    for _ in range(n):
        o = price
        drift = rng.gauss(0, start_price * 0.0015)
        c = max(o + drift, 0.01)
        h = max(o, c) + abs(rng.gauss(0, start_price * 0.0004))
        l = min(o, c) - abs(rng.gauss(0, start_price * 0.0004))
        candles.append(Candle(t, o, h, l, c, rng.uniform(50, 500), closed=True))
        price, t = c, t + timedelta(minutes=minutes)
    return candles


class SyntheticFeed(Feed):
    """Random walk. NO tiene edge y no debe tenerlo: sirve para verificar
    que el bot no 'encuentra' senal donde no hay."""

    def __init__(self, symbol="XAUUSD", timeframe="M15", n=500,
                 window=100, start_price=2400.0, seed=42):
        self.symbol, self.timeframe = symbol, timeframe
        self.window = window
        minutes = int(timeframe[1:]) if timeframe.startswith("M") else 60
        self._candles = _walk(n, start_price,
                              datetime(2026, 1, 5, 0, 0), minutes, seed)

    def stream(self) -> Iterator[Snapshot]:
        for i in range(self.window, len(self._candles) + 1):
            yield Snapshot(self.symbol, self.timeframe,
                           self._candles[i - self.window:i])


class CsvFeed(Feed):
    """CSV con columnas: time,open,high,low,close,volume.
    time en ISO 8601. Solo velas cerradas."""

    def __init__(self, path, symbol="XAUUSD", timeframe="M15", window=100):
        self.symbol, self.timeframe, self.window = symbol, timeframe, window
        with open(path, newline="") as fh:
            self._candles = [
                Candle(datetime.fromisoformat(r["time"]),
                       float(r["open"]), float(r["high"]),
                       float(r["low"]), float(r["close"]),
                       float(r.get("volume", 0)), closed=True)
                for r in csv.DictReader(fh)
            ]

    def stream(self) -> Iterator[Snapshot]:
        for i in range(self.window, len(self._candles) + 1):
            yield Snapshot(self.symbol, self.timeframe,
                           self._candles[i - self.window:i])
