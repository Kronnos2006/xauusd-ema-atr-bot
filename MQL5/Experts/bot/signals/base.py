"""
La interfaz enchufable. Cambiar de estrategia = cambiar una linea de config.

Reglas que la clase base HACE CUMPLIR, no sugiere:
  - la estrategia solo ve velas cerradas (lo garantiza Snapshot)
  - la estrategia solo devuelve direccion
  - si no tiene suficientes velas, devuelve FLAT en vez de fallar
"""
from abc import ABC, abstractmethod

from contracts import Direction, Signal, Snapshot


class Strategy(ABC):

    name: str = "sin-nombre"

    @property
    @abstractmethod
    def lookback(self) -> int:
        """Cuantas velas cerradas necesita como minimo."""

    @abstractmethod
    def _evaluate(self, snapshot: Snapshot) -> Signal:
        """Implementa esto. No lo llames directo."""

    def __call__(self, snapshot: Snapshot) -> Signal:
        if len(snapshot) < self.lookback:
            return Signal(Direction.FLAT,
                          f"{len(snapshot)}/{self.lookback} velas")
        signal = self._evaluate(snapshot)
        if not isinstance(signal, Signal):
            raise TypeError(f"{self.name} devolvio {type(signal)}, no Signal")
        return signal
