"""
Tests de riesgo. Los que importan son los que verifican que el modulo
DICE QUE NO: cuenta chica, tope diario alcanzado, ATR cero.
Un gestor de riesgo que solo se probo autorizando no esta probado.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from broker.base import SymbolSpec                      # noqa: E402
from broker.paper import PaperBroker                    # noqa: E402
from contracts import Candle, Direction                 # noqa: E402
from risk import Orden, RiskConfig, RiskManager, atr    # noqa: E402

SYM, MAGIC = "XAUUSD", 20260905


def velas(n=30, close=2400.0, rango=10.0):
    t0 = datetime(2026, 1, 5)
    out = []
    for i in range(n):
        c = close + i * 0.1
        out.append(Candle(t0 + timedelta(minutes=15 * i),
                          c, c + rango / 2, c - rango / 2, c, 100.0, True))
    return out


def armar(balance=10000.0, cfg=None, spec=None, price=2400.0):
    b = PaperBroker(price=price, balance=balance, spec=spec)
    return b, RiskManager(b, SYM, cfg or RiskConfig())


def test_atr_es_positivo_y_coherente():
    a = atr(velas(30, rango=10.0), 14)
    assert 9.0 < a < 11.0, f"ATR raro: {a}"
    return True


def test_atr_exige_suficientes_velas():
    try:
        atr(velas(5), 14)
    except ValueError:
        return True
    raise AssertionError("calculo ATR sin velas suficientes")


def test_riesgo_en_dinero_respeta_el_porcentaje():
    _, rm = armar(balance=10000.0, cfg=RiskConfig(riesgo_por_operacion=0.005))
    o = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert o.volume > 0
    # 0.5% de 10000 = 50. Redondeo al step puede desviar un poco, no mas.
    assert 35.0 <= o.riesgo_dinero <= 55.0, o.riesgo_dinero
    return True


def test_mas_volatilidad_menos_volumen():
    """La prueba de que no es lote fijo."""
    _, rm = armar()
    tranquilo = rm.dimensionar(Direction.LONG, velas(rango=5.0), MAGIC)
    agitado = rm.dimensionar(Direction.LONG, velas(rango=20.0), MAGIC)
    assert agitado.volume < tranquilo.volume, (tranquilo.volume, agitado.volume)
    return True


def test_stop_obligatorio_y_del_lado_correcto():
    _, rm = armar(price=2400.0)
    largo = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    corto = rm.dimensionar(Direction.SHORT, velas(), MAGIC)
    assert largo.sl < 2400.0, "stop de un largo debe estar abajo"
    assert corto.sl > 2400.0, "stop de un corto debe estar arriba"
    assert largo.sl != 0 and corto.sl != 0, "sin stop no se opera"
    return True


def test_take_profit_respeta_el_ratio():
    _, rm = armar(price=2400.0, cfg=RiskConfig(ratio_tp=2.0))
    o = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert abs((o.tp - 2400.0) / (2400.0 - o.sl) - 2.0) < 0.05
    return True


def test_cuenta_chica_no_opera():
    """Balance minusculo: el volumen no llega al minimo del broker.
    Tiene que devolver 0, no redondear para arriba."""
    _, rm = armar(balance=20.0)
    o = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert o.volume == 0.0, o
    assert "minimo" in o.motivo
    return True


def test_tope_diario_apaga():
    b, rm = armar(balance=10000.0, cfg=RiskConfig(perdida_diaria_max=0.02))
    assert rm.dimensionar(Direction.LONG, velas(), MAGIC).volume > 0
    b.pnl_hoy = -250.0                       # -2.5% > tope de 2%
    o = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert o.volume == 0.0
    assert rm.apagado and "perdida diaria" in rm.razon_apagado
    return True


def test_apagado_no_se_rearma_solo():
    """Aunque el PnL mejore, el bot no vuelve solo. Lo reinicia una persona."""
    b, rm = armar()
    b.pnl_hoy = -500.0
    rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert rm.apagado
    b.pnl_hoy = +1000.0
    assert rm.dimensionar(Direction.LONG, velas(), MAGIC).volume == 0.0
    return True


def test_flat_no_dimensiona():
    _, rm = armar()
    assert rm.dimensionar(Direction.FLAT, velas(), MAGIC).volume == 0.0
    return True


def test_config_rechaza_riesgo_absurdo():
    for kw in ({"riesgo_por_operacion": 0.5}, {"riesgo_por_operacion": 0.0},
               {"perdida_diaria_max": 0.9}, {"atr_multiplo_stop": 0}):
        try:
            RiskConfig(**kw)
        except ValueError:
            continue
        raise AssertionError(f"acepto config absurda: {kw}")
    return True


def test_volumen_se_normaliza_al_step():
    spec = SymbolSpec("XAUUSD", 0.01, 100.0, 0.01, 100.0, 2)
    _, rm = armar(spec=spec)
    o = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert abs(round(o.volume / 0.01) * 0.01 - o.volume) < 1e-9, o.volume
    return True


def test_tope_absoluto_de_volumen():
    _, rm = armar(balance=10_000_000.0,
                  cfg=RiskConfig(volumen_max_absoluto=0.5))
    o = rm.dimensionar(Direction.LONG, velas(), MAGIC)
    assert o.volume <= 0.5, o.volume
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
    print(f"\n{len(tests)-fallos}/{len(tests)} pasaron")
    sys.exit(1 if fallos else 0)
