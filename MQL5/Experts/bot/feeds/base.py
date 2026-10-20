"""
Abstraccion de fuente de datos.

El punto de esto: el bot corre igual con datos sinteticos en Linux, con
un CSV historico, o contra MT5 en Windows. Solo cambia el feed.
Si tu logica depende de que el feed sea MT5, la logica esta mal.
"""
from abc import ABC, abstractmethod
from typing import Iterator, Optional

from contracts import Snapshot


class Feed(ABC):

    @abstractmethod
    def stream(self) -> Iterator[Optional[Snapshot]]:
        """
        Emite un Snapshot cuando cierra una vela nueva.
        Puede emitir None mientras espera: significa "vivo, sin novedad".
        Los feeds de replay nunca emiten None.
        """
