"""
Gestion de riesgo (paso 6).

Tres cosas, y ninguna la decide la estrategia:

  1. Cuanto operar    -> % fijo del balance arriesgado, derivado del stop.
                         Nunca un lote fijo: un lote fijo arriesga el doble
                         cuando la volatilidad se duplica.
  2. Donde esta el stop -> obligatorio. Sin stop no se abre. Punto.
  3. Cuando parar     -> tope de perdida diaria que apaga el bot.

Es una capa de decision pura: no manda ordenes, solo autoriza o rechaza.
Se prueba entera con el broker de papel.
"""
from dataclasses import dataclass
from typing import Optional, Sequence

from broker.base import Broker, SymbolSpec
from contracts import Candle, Direction


# ---------------------------------------------------------------- ATR

def atr(candles: Sequence[Candle], periodo: int = 14) -> float:
    """True Range promedio. Es la medida de volatilidad con la que se
    dimensiona el stop, para que el riesgo en dinero sea constante aunque
    el mercado cambie de regimen."""
    if len(candles) < periodo + 1:
        raise ValueError(f"ATR({periodo}) necesita {periodo+1} velas, "
                         f"hay {len(candles)}")
    trs = []
    for prev, cur in zip(candles[-periodo-1:-1], candles[-periodo:]):
        trs.append(max(cur.high - cur.low,
                       abs(cur.high - prev.close),
                       abs(cur.low - prev.close)))
    return sum(trs) / periodo


# ---------------------------------------------------------------- config

@dataclass(frozen=True)
class RiskConfig:
    riesgo_por_operacion: float = 0.005   # 0.5% del balance
    atr_periodo: int = 14
    atr_multiplo_stop: float = 2.0
    ratio_tp: float = 0.0                 # 0 = sin take profit
    perdida_diaria_max: float = 0.02      # 2% del balance -> apaga el bot
    volumen_max_absoluto: float = 1.0     # tope duro, pase lo que pase

    def __post_init__(self):
        if not 0 < self.riesgo_por_operacion <= 0.05:
            raise ValueError("riesgo_por_operacion fuera de (0, 0.05]. "
                             "Arriesgar mas del 5% por operacion no es "
                             "una configuracion, es un error.")
        if self.atr_multiplo_stop <= 0:
            raise ValueError("atr_multiplo_stop debe ser > 0")
        if not 0 < self.perdida_diaria_max <= 0.20:
            raise ValueError("perdida_diaria_max fuera de (0, 0.20]")


@dataclass(frozen=True)
class Orden:
    """Autorizacion para abrir. Si volume es 0, NO se abre."""
    volume: float
    sl: float
    tp: float
    riesgo_dinero: float
    distancia_stop: float
    motivo: str = ""


class RiskManager:

    def __init__(self, broker: Broker, symbol: str, config: RiskConfig):
        self.broker = broker
        self.symbol = symbol
        self.cfg = config
        self._apagado_por: Optional[str] = None

    # ------------------------------------------------ interruptor diario

    @property
    def apagado(self) -> bool:
        return self._apagado_por is not None

    @property
    def razon_apagado(self) -> Optional[str]:
        return self._apagado_por

    def revisar_perdida_diaria(self, magic: int) -> bool:
        """True si se puede seguir operando. Una vez apagado, se queda
        apagado: no se re-arma solo si el PnL mejora."""
        if self.apagado:
            return False
        cuenta = self.broker.account()
        pnl = self.broker.realized_pnl_today(self.symbol, magic)
        limite = -abs(cuenta.balance * self.cfg.perdida_diaria_max)
        if pnl <= limite:
            self._apagado_por = (
                f"perdida diaria {pnl:.2f} alcanzo el tope {limite:.2f} "
                f"({self.cfg.perdida_diaria_max:.1%} de {cuenta.balance:.2f})")
            return False
        return True

    # ------------------------------------------------ dimensionamiento

    def dimensionar(self, direccion: Direction, candles: Sequence[Candle],
                    magic: int) -> Orden:
        if direccion is Direction.FLAT:
            return Orden(0.0, 0.0, 0.0, 0.0, 0.0, "direccion FLAT")

        if not self.revisar_perdida_diaria(magic):
            return Orden(0.0, 0.0, 0.0, 0.0, 0.0,
                         self._apagado_por or "apagado")

        spec: SymbolSpec = self.broker.symbol_spec(self.symbol)
        cuenta = self.broker.account()
        precio = self.broker.price(self.symbol)

        distancia = atr(candles, self.cfg.atr_periodo) * self.cfg.atr_multiplo_stop
        if distancia <= 0:
            return Orden(0.0, 0.0, 0.0, 0.0, 0.0, "ATR cero: sin volatilidad")

        riesgo_dinero = cuenta.balance * self.cfg.riesgo_por_operacion
        perdida_por_lote = distancia * spec.value_per_price_unit
        if perdida_por_lote <= 0:
            return Orden(0.0, 0.0, 0.0, 0.0, distancia, "spec invalida")

        bruto = riesgo_dinero / perdida_por_lote
        bruto = min(bruto, self.cfg.volumen_max_absoluto)
        volumen = spec.normalizar(bruto)

        if volumen <= 0:
            return Orden(0.0, 0.0, 0.0, 0.0, distancia,
                         f"volumen calculado {bruto:.4f} < minimo "
                         f"{spec.volume_min}: la cuenta es chica para este "
                         f"stop. NO se opera.")

        es_long = direccion is Direction.LONG
        sl = precio - distancia if es_long else precio + distancia
        tp = 0.0
        if self.cfg.ratio_tp > 0:
            objetivo = distancia * self.cfg.ratio_tp
            tp = precio + objetivo if es_long else precio - objetivo

        return Orden(volumen, round(sl, spec.digits), round(tp, spec.digits),
                     volumen * perdida_por_lote, distancia,
                     f"riesgo {self.cfg.riesgo_por_operacion:.2%} "
                     f"(~{volumen * perdida_por_lote:.2f} {cuenta.currency}), "
                     f"stop {distancia:.2f}")
