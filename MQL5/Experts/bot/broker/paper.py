"""
Bróker falso en memoria. Con esto se testea la máquina de estados sin
tocar una cuenta y sin depender de que el mercado esté abierto.

Puede simular fallos a propósito: fail_next_open / fail_next_close.
Un ejecutor que solo se probó con el camino feliz no está probado.
"""
from datetime import datetime, timezone
from itertools import count
from typing import Dict, List

from broker.base import Account, Broker, Position, SymbolSpec
from contracts import Direction


class PaperBroker(Broker):

    def __init__(self, price=2400.0, connected=True, balance=10000.0,
                 spec: SymbolSpec = None):
        self._tickets = count(1000)
        self._open: Dict[int, Position] = {}
        self._price = price
        self.balance = balance
        self.connected = connected
        self.pnl_hoy = 0.0
        self._spec = spec or SymbolSpec(
            name="XAUUSD", volume_min=0.01, volume_max=100.0,
            volume_step=0.01, value_per_price_unit=100.0, digits=2)
        self.fail_next_open = False
        self.fail_next_close = False
        self.historial: List[str] = []

    def is_connected(self) -> bool:
        return self.connected

    def positions(self, symbol: str, magic: int) -> List[Position]:
        if not self.connected:
            raise ConnectionError("bróker desconectado")
        return [p for p in self._open.values()
                if p.symbol == symbol and p.magic == magic]

    def account(self) -> Account:
        return Account(self.balance, self.balance + self.pnl_hoy, "USD")

    def symbol_spec(self, symbol: str) -> SymbolSpec:
        return self._spec

    def realized_pnl_today(self, symbol: str, magic: int) -> float:
        return self.pnl_hoy

    def price(self, symbol: str) -> float:
        return self._price

    def set_price(self, price: float) -> None:
        """El runner lo llama con el cierre de cada vela. Sin esto el
        broker de papel vive en un precio fijo y los stops se calculan
        contra un numero que no existe."""
        self._price = float(price)

    def open(self, symbol, direction, volume, magic, sl=0.0, tp=0.0) -> Position:
        if not self.connected:
            raise ConnectionError("bróker desconectado")
        if self.fail_next_open:
            self.fail_next_open = False
            raise RuntimeError("orden rechazada por el bróker (simulado)")
        pos = Position(next(self._tickets), symbol, direction, volume,
                       self._price, datetime.now(timezone.utc), magic, sl, tp)
        self._open[pos.ticket] = pos
        self.historial.append(f"OPEN {direction.name} {volume} {symbol} sl={sl}")
        return pos

    def close(self, position: Position) -> bool:
        if not self.connected:
            raise ConnectionError("bróker desconectado")
        if self.fail_next_close:
            self.fail_next_close = False
            return False
        if position.ticket not in self._open:
            return False          # ya cerrada: no es un error
        del self._open[position.ticket]
        self.historial.append(f"CLOSE {position.ticket}")
        return True

    # --- solo para tests: simular que el mundo cambió sin avisar ---
    def inyectar_posicion(self, symbol, direction, volume, magic=0) -> Position:
        pos = Position(next(self._tickets), symbol, direction, volume,
                       self._price, datetime.now(timezone.utc), magic)
        self._open[pos.ticket] = pos
        return pos
