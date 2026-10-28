"""Tests aislados, sin APIs, proveedores IA ni trading."""
import hashlib
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validador_datos import validate
from evaluador_modelos import evaluate
from auditor_gerencia import audit
from recolector_mercado import validated_host

class Tests(unittest.TestCase):
    def test_valido(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"data.csv"
            p.write_text("utc,bid,ask,spread_pct\n2026-10-28T00:00:00Z,100,101,1\n")
            self.assertTrue(validate(p)["valido"])

    def test_rechaza_spread(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"data.csv"
            p.write_text("utc,bid,ask,spread_pct\n2026-10-28T00:00:00Z,102,101,-1\n")
            self.assertFalse(validate(p)["valido"])

    def test_rechaza_red_no_autorizada(self):
        with self.assertRaises(ValueError):
            validated_host("https://example.com/data", set())

    def test_rechaza_red_privada(self):
        with self.assertRaises(ValueError):
            validated_host("https://127.0.0.1/data", {"127.0.0.1"})

    def test_no_acepta_bool_en_lugar_de_git(self):
        item={"model":"K", "event_id":"E1", "predicted":1, "actual":1,
              "preregistered":True,"matured":True}
        result=evaluate([item], ".")
        self.assertEqual(result["validas_descriptivas"],0)
        self.assertEqual(result["promocion"],"BLOQUEADA")

    def test_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"f"
            p.write_bytes(b"abc")
            self.assertEqual(audit([str(p)])["inputs"][0]["sha256"], hashlib.sha256(b"abc").hexdigest())

if __name__=="__main__":
    unittest.main()
