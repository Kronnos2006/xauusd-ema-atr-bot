"""
Tests de la máquina de estados. El escenario que importa de verdad es
test_sobrevive_a_reinicio: matar el bot con posición abierta y que la
reconozca al volver.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from broker.paper import PaperBroker            # noqa: E402
from contracts import Direction                 # noqa: E402
from state import Action, PositionManager       # noqa: E402

SYM, MAGIC = "XAUUSD", 20260905


def nuevo(**kw):
    b = PaperBroker()
    return b, PositionManager(b, SYM, volume=0.01, magic=MAGIC, **kw)


def test_arranca_plano():
    _, pm = nuevo()
    assert pm.direccion_actual() is Direction.FLAT
    return True


def test_abre_desde_plano():
    _, pm = nuevo()
    d = pm.procesar(Direction.LONG)
    assert d.action is Action.ABRIR
    assert pm.direccion_actual() is Direction.LONG
    return True


def test_no_reentra_con_la_misma_senal():
    """El defecto de dummy-dayofweek: doce velas SHORT, una sola operación."""
    b, pm = nuevo()
    pm.procesar(Direction.SHORT)
    for _ in range(11):
        d = pm.procesar(Direction.SHORT)
        assert d.action is Action.NADA
    assert len([x for x in b.historial if x.startswith("OPEN")]) == 1
    return True


def test_da_vuelta():
    _, pm = nuevo()
    pm.procesar(Direction.LONG)
    d = pm.procesar(Direction.SHORT)
    assert d.action is Action.DAR_VUELTA
    assert pm.direccion_actual() is Direction.SHORT
    return True


def test_cierra_con_flat():
    _, pm = nuevo()
    pm.procesar(Direction.LONG)
    d = pm.procesar(Direction.FLAT)
    assert d.action is Action.CERRAR
    assert pm.direccion_actual() is Direction.FLAT
    return True


def test_sobrevive_a_reinicio():
    """EL test que importa: el bot muere con posición abierta y revive."""
    b, pm = nuevo()
    pm.procesar(Direction.LONG)
    del pm                                    # el proceso muere
    pm2 = PositionManager(b, SYM, volume=0.01, magic=MAGIC)   # revive
    assert pm2.direccion_actual() is Direction.LONG, "no reconoció la posición"
    assert pm2.procesar(Direction.LONG).action is Action.NADA
    return True


def test_ignora_posiciones_ajenas():
    """Una operación abierta a mano (otro magic) no se toca."""
    b, pm = nuevo()
    ajena = b.inyectar_posicion(SYM, Direction.SHORT, 0.5, magic=999)
    assert pm.direccion_actual() is Direction.FLAT
    pm.procesar(Direction.LONG)
    assert ajena.ticket in b._open, "cerró una posición que no era suya"
    return True


def test_detecta_estado_imposible():
    b, pm = nuevo()
    b.inyectar_posicion(SYM, Direction.LONG, 0.01, magic=MAGIC)
    b.inyectar_posicion(SYM, Direction.LONG, 0.01, magic=MAGIC)
    try:
        pm.reconciliar()
    except RuntimeError:
        return True
    raise AssertionError("no detectó dos posiciones simultáneas")


def test_falla_de_apertura_no_miente():
    b, pm = nuevo()
    b.fail_next_open = True
    try:
        pm.procesar(Direction.LONG)
    except RuntimeError:
        assert pm.direccion_actual() is Direction.FLAT
        return True
    raise AssertionError("se tragó el rechazo del bróker")


def test_shorts_deshabilitados():
    _, pm = nuevo(permitir_shorts=False)
    d = pm.procesar(Direction.SHORT)
    assert d.action is Action.NADA
    assert pm.direccion_actual() is Direction.FLAT
    return True


def test_desconexion_no_se_silencia():
    b, pm = nuevo()
    b.connected = False
    try:
        pm.direccion_actual()
    except ConnectionError:
        return True
    raise AssertionError("reportó estado con el bróker caído")


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
