"""Pruebas unitarias stdlib para scripts de investigación, sin red ni órdenes."""
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validador_datos import validate
from evaluador_modelos import evaluate
from auditor_gerencia import audit

class TestKronnosScripts(unittest.TestCase):
    def test_csv_valido(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spread.csv"
            f.write_text("utc,bid,ask,spread_pct\n2026-10-28T00:00:00Z,100,101,1\n")
            self.assertTrue(validate(f)["valido"])

    def test_rechaza_precio_y_fecha(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "spread.csv"
            f.write_text("utc,bid,ask,spread_pct\n2026-10-28T00:00:00Z,102,101,0\n")
            self.assertFalse(validate(f)["valido"])

    def test_rechaza_duplicados(self):
        item = {"model": "K", "event_id": "E1", "predicted": 1, "actual": 1,
                "preregistered": True, "matured": True}
        r = evaluate([item, item])
        self.assertEqual(r["validas_descriptivas"], 1)
        self.assertEqual(len(r["excluidas"]), 1)
        self.assertEqual(r["promocion"], "BLOQUEADA")

    def test_omite_no_verificados(self):
        self.assertEqual(evaluate([{"model":"K", "event_id":"a", "predicted":1, "actual":1}])["validas_descriptivas"], 0)

    def test_hash_contenido(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "a.txt"
            f.write_bytes(b"abc")
            self.assertEqual(audit([str(f)])["inputs"][0]["sha256"],
                             "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

if __name__ == "__main__":
    unittest.main()
