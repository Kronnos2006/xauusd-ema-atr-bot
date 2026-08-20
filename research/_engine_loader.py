"""Carga "Backtest ema v4.py" por ruta de archivo (mismo mecanismo
importlib.util.spec_from_file_location que ya usan hipotesis_macro_dfii10.py
y hermanos), para no depender de que el archivo esté en un paquete
importable ni de renombrarlo/moverlo.
"""

import importlib.util
import sys
from pathlib import Path

_RUTA_ENGINE = Path(__file__).resolve().parent.parent / "Backtest ema v4.py"
_MODULE_NAME = "backtest_ema_v4_engine"

_cached_module = None


def cargar_engine():
    """Devuelve el módulo "Backtest ema v4.py" ya importado (cacheado tras la primera llamada)."""
    global _cached_module
    if _cached_module is not None:
        return _cached_module

    if "MetaTrader5" not in sys.modules:
        try:
            import MetaTrader5  # noqa: F401
        except ImportError:
            fixtures_dir = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
            sys.path.insert(0, str(fixtures_dir))
            import mt5_stub
            sys.modules["MetaTrader5"] = mt5_stub

    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _RUTA_ENGINE)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = modulo
    spec.loader.exec_module(modulo)
    _cached_module = modulo
    return modulo
