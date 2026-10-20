"""
Puerto de bróker. Misma idea que los feeds: el bot corre igual contra un
bróker falso en memoria o contra MT5 real. Si tu lógica depende de que
sea MT5, la lógica está mal.

REGLA CENTRAL: el estado de las posiciones lo tiene el BRÓKER, no el bot.
El bot nunca cree lo que él mismo guardó en un archivo. Pregunta.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List

from contracts import Direction


@dataclass(frozen=True)
class Account:
    balance: float
    equity: float
    currency: str = "USD"


@dataclass(frozen=True)
class SymbolSpec:
    """Lo que el broker exige del volumen y como se convierte a dinero."""
    name: str
    volume_min: float
    volume_max: float
    volume_step: float
    # cuanto vale 1.0 de volumen por cada 1.0 de movimiento de precio
    value_per_price_unit: float
    digits: int = 2

    def normalizar(self, volume: float) -> float:
        """
        Ajusta al step y a los limites del broker.

        Redondea SIEMPRE HACIA ABAJO. Redondear al mas cercano suena
        inocente y es un sesgo sistematico a arriesgar de mas: la mitad
        de las operaciones excederian el presupuesto de riesgo. Con floor,
        el riesgo real es <= al configurado, nunca mayor.

        Devuelve 0 si no llega al minimo del broker: mejor no operar que
        mandar un volumen que sera rechazado, o peor, uno que arriesga
        el triple de lo que pediste.
        """
        if volume < self.volume_min:
            return 0.0
        pasos = int((volume - self.volume_min) / self.volume_step + 1e-9)
        v = self.volume_min + pasos * self.volume_step
        v = min(v, self.volume_max)
        decimales = max(0, len(str(self.volume_step).split(".")[-1]))
        return round(v, decimales)


@dataclass(frozen=True)
class Position:
    ticket: int
    symbol: str
    direction: Direction
    volume: float
    price_open: float
    time_open: datetime
    magic: int = 0
    sl: float = 0.0
    tp: float = 0.0


class Broker(ABC):
    """Solo lo que la máquina de estados necesita. Nada más."""

    @abstractmethod
    def positions(self, symbol: str, magic: int) -> List[Position]:
        """Posiciones abiertas AHORA, según el bróker."""

    @abstractmethod
    def open(self, symbol: str, direction: Direction, volume: float,
             magic: int, sl: float = 0.0, tp: float = 0.0) -> Position: ...

    @abstractmethod
    def close(self, position: Position) -> bool: ...

    @abstractmethod
    def is_connected(self) -> bool: ...

    @abstractmethod
    def account(self) -> Account: ...

    @abstractmethod
    def symbol_spec(self, symbol: str) -> SymbolSpec: ...

    @abstractmethod
    def realized_pnl_today(self, symbol: str, magic: int) -> float:
        """PnL cerrado de HOY. Es lo que alimenta el tope de perdida diaria."""

    @abstractmethod
    def price(self, symbol: str) -> float: ...
