"""El verificador de integridad de KT-002 debe detectar alteraciones (pruebas negativas). Solo lectura."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import kt002_integridad as ki  # noqa: E402
import kt002_prospectivo as kt  # noqa: E402

REAL = Path(__file__).resolve().parent.parent / "data" / "kt002"


def fila(base_h, pred=0.01, actual=None, hit=None, objetivo_h=None):
    b = pd.Timestamp("2026-10-20T00:00:00Z") + pd.Timedelta(hours=base_h)
    t = b + pd.Timedelta(hours=4 if objetivo_h is None else objetivo_h)
    r = {"base_open_utc": b.isoformat(), "target_open_utc": t.isoformat(), "base_close": "100"}
    for m in ki.MODELOS:
        r[f"{m}_ret"] = str(pred)
        r[f"{m}_hit"] = "" if hit is None else hit
    r["actual_close4"] = "" if actual is None else str(100 * (1 + actual))
    r["actual_ret"] = "" if actual is None else str(actual)
    return r


class Actuales(unittest.TestCase):
    def test_sano(self):
        df = pd.DataFrame([fila(0, actual=0.02, hit="1"), fila(1), fila(2, actual=-0.01, hit="0")])
        self.assertEqual(ki.actuales(df, kt), [])

    def test_detecta_duplicado_objetivo_y_acierto_alterado(self):
        df = pd.DataFrame([fila(0, actual=0.02, hit="0"), fila(0), fila(3, objetivo_h=5)])
        v = " | ".join(ki.actuales(df, kt))
        self.assertIn("duplicadas", v)
        self.assertIn("objetivo distinto de 4 h", v)
        self.assertIn("kronos_hit no coincide", v)

    def test_huecos(self):
        df = pd.DataFrame([fila(0), fila(1), fila(4)])
        self.assertEqual(len(ki.huecos(df)), 2)


class Resumen(unittest.TestCase):
    def test_resumen_real_reproducible_y_alteracion_detectada(self):
        with tempfile.TemporaryDirectory() as d:
            for f in ("predicciones.csv", "resumen.json"):
                shutil.copy(REAL / f, Path(d) / f)
            viejo = ki.DATA
            try:
                ki.DATA = Path(d)
                self.assertEqual(ki.resumen_reproducible(Path(kt.__file__))[0], [])
                r = json.loads((Path(d) / "resumen.json").read_text())
                r["sin_solape"]["kronos"]["aciertos"] += 1
                (Path(d) / "resumen.json").write_text(json.dumps(r))
                self.assertTrue(ki.resumen_reproducible(Path(kt.__file__))[0])
            finally:
                ki.DATA = viejo
                os.environ.pop("KT002_OUT", None)


if __name__ == "__main__":
    unittest.main()
