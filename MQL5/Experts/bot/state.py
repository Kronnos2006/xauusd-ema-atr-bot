"""
Máquina de estados y reconciliación (paso 8).

El problema que resuelve: el bot puede morir en cualquier momento —
corte de luz, reinicio de Windows, crash de MT5 — y al revivir tiene que
saber qué posiciones tiene abiertas. La respuesta NUNCA sale de un archivo
propio: sale de preguntarle al bróker.

También resuelve el defecto que viste con dummy-dayofweek: la señal dice
SHORT en las doce velas del jueves, pero solo la primera debe abrir algo.
La señal es dirección deseada; esta clase la traduce a acción.
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from broker.base import Broker, Position
from contracts import Direction


class Action(Enum):
    NADA = auto()          # ya estamos como queremos
    ABRIR = auto()
    CERRAR = auto()
    DAR_VUELTA = auto()    # cerrar y abrir al reves


@dataclass(frozen=True)
class Decision:
    action: Action
    direction: Direction
    reason: str


class PositionManager:
    """
    magic identifica NUESTRAS posiciones. Sin esto, el bot podría cerrar
    una operación que abriste vos a mano. El filtro por magic es lo que
    hace que convivan.
    """

    def __init__(self, broker: Broker, symbol: str, volume: float,
                 magic: int = 20260905, permitir_shorts: bool = True):
        if volume <= 0:
            raise ValueError("volume debe ser > 0")
        self.broker = broker
        self.symbol = symbol
        self.volume = volume
        self.magic = magic
        self.permitir_shorts = permitir_shorts

    # ---------- reconciliación ----------

    def reconciliar(self) -> List[Position]:
        """
        Se llama SIEMPRE al arrancar, y de nuevo antes de cada decisión.
        Es barato y es la única fuente de verdad.
        """
        posiciones = self.broker.positions(self.symbol, self.magic)
        if len(posiciones) > 1:
            # Estado inesperado: nunca deberíamos tener dos. No adivinamos.
            raise RuntimeError(
                f"{len(posiciones)} posiciones abiertas con magic={self.magic} "
                f"en {self.symbol}. Revisar a mano antes de seguir: "
                + ", ".join(str(p.ticket) for p in posiciones))
        return posiciones

    def posicion_actual(self) -> Optional[Position]:
        pos = self.reconciliar()
        return pos[0] if pos else None

    def direccion_actual(self) -> Direction:
        pos = self.posicion_actual()
        return pos.direction if pos else Direction.FLAT

    # ---------- decisión ----------

    def decidir(self, deseada: Direction) -> Decision:
        """
        Traduce 'dirección deseada' a 'qué hacer'. Es una función pura de
        (estado real, dirección deseada). No ejecuta nada.
        """
        if deseada is Direction.SHORT and not self.permitir_shorts:
            deseada = Direction.FLAT

        actual = self.direccion_actual()

        if actual is deseada:
            return Decision(Action.NADA, deseada, f"ya en {actual.name}")
        if actual is Direction.FLAT:
            return Decision(Action.ABRIR, deseada, f"abrir {deseada.name}")
        if deseada is Direction.FLAT:
            return Decision(Action.CERRAR, Direction.FLAT,
                            f"cerrar {actual.name}")
        return Decision(Action.DAR_VUELTA, deseada,
                        f"dar vuelta {actual.name} -> {deseada.name}")

    # ---------- ejecución ----------

    def aplicar(self, decision: Decision, orden=None) -> bool:
        """
        Ejecuta la decisión. Devuelve True si el estado final coincide con
        el deseado. Verifica contra el bróker, no asume que salió bien.
        """
        if decision.action is Action.NADA:
            return True

        if decision.action in (Action.CERRAR, Action.DAR_VUELTA):
            pos = self.posicion_actual()
            if pos and not self.broker.close(pos):
                return False

        if decision.action in (Action.ABRIR, Action.DAR_VUELTA):
            vol = orden.volume if orden else self.volume
            sl = orden.sl if orden else 0.0
            tp = orden.tp if orden else 0.0
            if vol <= 0:
                # riesgo dijo que no. Quedamos planos y es un resultado
                # valido, no un fallo.
                return self.direccion_actual() is Direction.FLAT
            self.broker.open(self.symbol, decision.direction, vol,
                             self.magic, sl, tp)

        return self.direccion_actual() is decision.direction

    def procesar(self, deseada: Direction, orden=None) -> Decision:
        """
        Reconciliar -> decidir -> aplicar. Es lo que llama el runner.

        orden viene de RiskManager.dimensionar(). Si es None se usa el
        volumen fijo del constructor (solo para tests y replay).
        Si trae volume 0, riesgo VETO la apertura.
        """
        decision = self.decidir(deseada)
        if decision.action is Action.ABRIR and orden is not None and orden.volume <= 0:
            return Decision(Action.NADA, Direction.FLAT,
                            f"vetado por riesgo: {orden.motivo}")
        if decision.action is not Action.NADA:
            ok = self.aplicar(decision, orden)
            if not ok:
                return Decision(decision.action, decision.direction,
                                decision.reason + " [FALLO]")
        return decision
