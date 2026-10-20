"""
Tests de las garantias que el diseno promete. Si estos pasan, el paso 4
y el 5 estan cerrados.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from contracts import Candle, Direction, Signal, Snapshot   # noqa: E402
from signals.registry import build                          # noqa: E402


def vela(t, close=2400.0, closed=True):
    return Candle(t, close, close + 1, close - 1, close, 100.0, closed)


def velas(n, closed=True):
    t0 = datetime(2026, 1, 5, 0, 0)      # lunes
    return [vela(t0 + timedelta(minutes=15 * i), closed=closed) for i in range(n)]


def test_snapshot_rechaza_vela_en_formacion():
    try:
        Snapshot("XAUUSD", "M15", velas(3, closed=False))
    except ValueError:
        return True
    raise AssertionError("acepto una vela sin cerrar")


def test_snapshot_rechaza_desorden():
    cs = velas(3)
    try:
        Snapshot("XAUUSD", "M15", [cs[2], cs[0], cs[1]])
    except ValueError:
        return True
    raise AssertionError("acepto velas desordenadas")


def test_candle_rechaza_ohlc_imposible():
    try:
        Candle(datetime(2026, 1, 5), 10, 5, 8, 9, 1, True)   # high < low
    except ValueError:
        return True
    raise AssertionError("acepto una vela imposible")


def test_flat_si_faltan_velas():
    class Larga(build("dummy-flat").__class__):
        name, lookback = "larga", 500
    s = Larga()
    assert s(Snapshot("XAUUSD", "M15", velas(3))).direction is Direction.FLAT
    return True


def test_dayofweek_opera_lunes_y_jueves():
    s = build("dummy-dayofweek")
    lunes = Snapshot("XAUUSD", "M15", [vela(datetime(2026, 1, 5, 12))])
    jueves = Snapshot("XAUUSD", "M15", [vela(datetime(2026, 1, 8, 12))])
    martes = Snapshot("XAUUSD", "M15", [vela(datetime(2026, 1, 6, 12))])
    assert s(lunes).direction is Direction.LONG
    assert s(jueves).direction is Direction.SHORT
    assert s(martes).direction is Direction.FLAT
    return True


def test_alternating_alterna():
    s = build("dummy-alternating")
    snap = Snapshot("XAUUSD", "M15", velas(2))
    d = [s(snap).direction for _ in range(4)]
    assert d == [Direction.LONG, Direction.SHORT, Direction.LONG, Direction.SHORT]
    return True


def test_control_negativo_nunca_opera():
    s = build("dummy-flat")
    snap = Snapshot("XAUUSD", "M15", velas(5))
    assert all(s(snap).direction is Direction.FLAT for _ in range(20))
    return True


def test_signal_solo_direccion():
    sig = Signal(Direction.LONG, "x")
    assert set(vars(sig)) == {"direction", "reason"}
    return True


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fallos = 0
    for t in tests:
        try:
            t()
            print(f"  ok    {t.__name__}")
        except Exception as exc:
            fallos += 1
            print(f"  FALLA {t.__name__}: {exc}")
    print(f"\n{len(tests) - fallos}/{len(tests)} pasaron")
    sys.exit(1 if fallos else 0)
