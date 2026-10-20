"""
Bróker real de MetaTrader 5. Solo Windows con MT5 instalado.

Cada retcode se trata explícitamente. Un ejecutor que solo mira
'retcode == DONE' te va a mentir el día que el bróker devuelva REQUOTE
o PRICE_OFF y vos creas que la orden entró.
"""
from datetime import datetime, timezone
from typing import List

from broker.base import Account, Broker, Position, SymbolSpec
from contracts import Direction

# retcodes que significan "no entró, pero reintentar tiene sentido"
REINTENTABLES = {10004, 10021, 10018, 10027}   # REQUOTE, PRICE_OFF, MARKET_CLOSED, AUTOTRADING_DISABLED
FATALES = {10019, 10014, 10015, 10016, 10013}  # NO_MONEY, INVALID_VOLUME, INVALID_PRICE, INVALID_STOPS, INVALID_REQUEST


class Mt5Broker(Broker):

    def __init__(self, deviation=20, filling=None):
        try:
            import MetaTrader5 as mt5
        except ImportError as exc:
            raise RuntimeError(
                "MetaTrader5 no disponible. Usá --broker paper."
            ) from exc
        self.mt5 = mt5
        if not mt5.initialize():
            raise RuntimeError(f"initialize() falló: {mt5.last_error()}")
        self.deviation = deviation
        self.filling = filling if filling is not None else mt5.ORDER_FILLING_IOC

    def is_connected(self) -> bool:
        return self.mt5.terminal_info() is not None

    def positions(self, symbol: str, magic: int) -> List[Position]:
        if not self.is_connected():
            raise ConnectionError("terminal MT5 no responde")
        raw = self.mt5.positions_get(symbol=symbol)
        if raw is None:
            raw = ()
        return [
            Position(
                ticket=p.ticket, symbol=p.symbol,
                direction=Direction.LONG if p.type == self.mt5.POSITION_TYPE_BUY
                          else Direction.SHORT,
                volume=p.volume, price_open=p.price_open,
                time_open=datetime.fromtimestamp(p.time, tz=timezone.utc),
                magic=p.magic)
            for p in raw if p.magic == magic
        ]

    def _enviar(self, req: dict) -> None:
        r = self.mt5.order_send(req)
        if r is None:
            raise RuntimeError(f"order_send devolvió None: {self.mt5.last_error()}")
        if r.retcode == self.mt5.TRADE_RETCODE_DONE:
            return
        if r.retcode in FATALES:
            raise RuntimeError(f"orden rechazada (fatal) retcode={r.retcode}: {r.comment}")
        if r.retcode in REINTENTABLES:
            raise RuntimeError(f"orden no ejecutada (reintentable) retcode={r.retcode}: {r.comment}")
        raise RuntimeError(f"retcode inesperado {r.retcode}: {r.comment}")

    def account(self) -> Account:
        info = self.mt5.account_info()
        if info is None:
            raise ConnectionError("account_info() devolvio None")
        return Account(info.balance, info.equity, info.currency)

    def symbol_spec(self, symbol: str) -> SymbolSpec:
        s = self.mt5.symbol_info(symbol)
        if s is None:
            raise RuntimeError(f"symbol_info({symbol}) devolvio None. "
                               f"Revisa el sufijo del broker (XAUUSD.m, etc.)")
        # valor de 1.0 de volumen por 1.0 de movimiento de precio
        vppu = (s.trade_tick_value / s.trade_tick_size) if s.trade_tick_size else 0.0
        return SymbolSpec(symbol, s.volume_min, s.volume_max, s.volume_step,
                          vppu, s.digits)

    def realized_pnl_today(self, symbol: str, magic: int) -> float:
        from datetime import time as _time
        hoy = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0,
                                                 microsecond=0)
        deals = self.mt5.history_deals_get(hoy, datetime.now(timezone.utc))
        if deals is None:
            return 0.0
        return sum(d.profit + d.commission + d.swap for d in deals
                   if d.symbol == symbol and d.magic == magic)

    def price(self, symbol: str) -> float:
        tick = self.mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"sin tick para {symbol}")
        return (tick.bid + tick.ask) / 2.0

    def open(self, symbol, direction, volume, magic, sl=0.0, tp=0.0) -> Position:
        tick = self.mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"sin tick para {symbol}")
        es_long = direction is Direction.LONG
        self._enviar({
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(volume),
            "type": self.mt5.ORDER_TYPE_BUY if es_long else self.mt5.ORDER_TYPE_SELL,
            "price": tick.ask if es_long else tick.bid,
            "deviation": self.deviation,
            "sl": float(sl),
            "tp": float(tp),
            "magic": magic,
            "comment": "bot",
            "type_time": self.mt5.ORDER_TIME_GTC,
            "type_filling": self.filling,
        })
        abiertas = self.positions(symbol, magic)
        if not abiertas:
            raise RuntimeError("order_send dijo DONE pero no hay posición")
        return abiertas[-1]

    def close(self, position: Position) -> bool:
        tick = self.mt5.symbol_info_tick(position.symbol)
        if tick is None:
            return False
        era_long = position.direction is Direction.LONG
        try:
            self._enviar({
                "action": self.mt5.TRADE_ACTION_DEAL,
                "position": position.ticket,
                "symbol": position.symbol,
                "volume": float(position.volume),
                "type": self.mt5.ORDER_TYPE_SELL if era_long else self.mt5.ORDER_TYPE_BUY,
                "price": tick.bid if era_long else tick.ask,
                "deviation": self.deviation,
                "magic": position.magic,
                "comment": "bot close",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.filling,
            })
            return True
        except RuntimeError:
            return False
