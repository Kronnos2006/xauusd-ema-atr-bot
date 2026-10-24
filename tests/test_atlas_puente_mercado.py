import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from atlas.puente_mercado import cargar_barras

class TestPuenteMercado(unittest.TestCase):
    def test_filtra_vela_abierta_y_deja_huella(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td)/"btc.json"
            ms = int(datetime(2026,10,24,tzinfo=timezone.utc).timestamp()*1000)
            p.write_text(json.dumps([[ms, 100, 101, 99, 101, 20],
                                     [ms+14400000, 101, 103, 100, 102, 21]]))
            r = cargar_barras(p, "4h", "2026-10-24T04:00:00Z")
            self.assertEqual(r["n_barras_cerradas"], 1)
            self.assertEqual(r["barras"][0].cierre, 101.0)
            self.assertEqual(len(r["sha256_origen"]), 64)
    def test_duplicado_no_permitido(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"btc.json"
            p.write_text(json.dumps([[0,100,100,100,100,1],[0,100,100,100,100,1]]))
            with self.assertRaises(ValueError):
                cargar_barras(p)
if __name__ == "__main__":
    unittest.main()
