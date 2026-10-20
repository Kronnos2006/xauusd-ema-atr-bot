"""
Contratos de datos. Todo lo que cruza entre modulos pasa por aca.
Si un modulo necesita algo que no esta en estas clases, el problema
esta en el diseno, no falta un campo.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from typing import Sequence


class Direction(IntEnum):
    SHORT = -1
    FLAT = 0
    LONG = 1


@dataclass(frozen=True)
class Candle:
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    closed: bool          # False = vela en formacion. NUNCA se le pasa
                          # a una estrategia.

    def __post_init__(self):
        if self.high < self.low:
            raise ValueError(f"vela invalida en {self.time}: high < low")
        if not (self.low <= self.open <= self.high):
            raise ValueError(f"vela invalida en {self.time}: open fuera de rango")
        if not (self.low <= self.close <= self.high):
            raise ValueError(f"vela invalida en {self.time}: close fuera de rango")


@dataclass(frozen=True)
class Snapshot:
    """Lo que ve una estrategia. Solo velas CERRADAS, mas antigua primero."""
    symbol: str
    timeframe: str
    candles: Sequence[Candle]

    def __post_init__(self):
        if any(not c.closed for c in self.candles):
            raise ValueError("Snapshot contiene velas sin cerrar")
        times = [c.time for c in self.candles]
        if times != sorted(times):
            raise ValueError("velas desordenadas")
        if len(set(times)) != len(times):
            raise ValueError("velas duplicadas")

    @property
    def last(self) -> Candle:
        return self.candles[-1]

    def __len__(self):
        return len(self.candles)


@dataclass(frozen=True)
class Signal:
    """
    Lo unico que una estrategia devuelve. Sin tamano, sin stop, sin precio.
    Esas decisiones son de riesgo y ejecucion, no de la senal.
    """
    direction: Direction
    reason: str = ""      # para el log, no para la logica
