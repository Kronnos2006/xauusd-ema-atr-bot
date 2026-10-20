"""
Senales sin edge, a proposito.

Sirven para probar que el resto del bot funciona SIN que la estrategia
sea una variable. Si algo falla con estas, el problema no es la senal.

No las conectes a capital real. No es una advertencia de forma: alternar
compra y venta pierde exactamente el costo de transaccion por operacion.
"""
from contracts import Direction, Signal, Snapshot
from signals.base import Strategy


class Alternating(Strategy):
    """Alterna long/short en cada vela. Maxima frecuencia, cero logica.
    Util para estresar el ejecutor y medir costos reales."""

    name = "dummy-alternating"
    lookback = 1

    def __init__(self):
        self._next = Direction.LONG

    def _evaluate(self, snapshot: Snapshot) -> Signal:
        current = self._next
        self._next = Direction.SHORT if current == Direction.LONG else Direction.LONG
        return Signal(current, "alterna")


class DayOfWeek(Strategy):
    """Long los lunes, short los jueves, plano el resto.
    Baja frecuencia: util para verificar la maquina de estados en varios dias."""

    name = "dummy-dayofweek"
    lookback = 1

    def _evaluate(self, snapshot: Snapshot) -> Signal:
        day = snapshot.last.time.weekday()   # 0 = lunes
        if day == 0:
            return Signal(Direction.LONG, "lunes")
        if day == 3:
            return Signal(Direction.SHORT, "jueves")
        return Signal(Direction.FLAT, "otro dia")


class AlwaysFlat(Strategy):
    """Nunca opera. El control negativo: si con esto aparecen operaciones,
    hay un bug en el ejecutor."""

    name = "dummy-flat"
    lookback = 1

    def _evaluate(self, snapshot: Snapshot) -> Signal:
        return Signal(Direction.FLAT, "control negativo")
