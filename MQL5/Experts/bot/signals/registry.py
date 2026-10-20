"""
Nombre -> estrategia. Esto es lo que hace que cambiar de estrategia sea
una linea de configuracion y no una edicion de codigo.

Para agregar una estrategia real: importala y sumala al dict. Nada mas
del bot deberia enterarse de que existe.
"""
from signals.base import Strategy
from signals.dummy import Alternating, AlwaysFlat, DayOfWeek

REGISTRY = {
    Alternating.name: Alternating,
    DayOfWeek.name: DayOfWeek,
    AlwaysFlat.name: AlwaysFlat,
}


def build(name: str, **kwargs) -> Strategy:
    if name not in REGISTRY:
        disponibles = ", ".join(sorted(REGISTRY))
        raise KeyError(f"estrategia '{name}' no registrada. Hay: {disponibles}")
    return REGISTRY[name](**kwargs)
