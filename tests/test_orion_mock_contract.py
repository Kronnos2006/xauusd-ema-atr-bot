"""B1: contrato funcional sintético y protecciones."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "pilot/orion_mock_contract.py"
spec = importlib.util.spec_from_file_location("orion_mock_contract", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MockPilotTests(unittest.TestCase):
    def test_veto_end_to_end(self):
        report = m.demonstrate()
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["generated_orders"], 0)
        self.assertTrue(report["evidence_chain_valid"])
        self.assertFalse(report["external_code_executed"])
        self.assertFalse(report["scientific_approval"])
        self.assertEqual(report["events"][-1]["kind"], "blocked")

    def test_tamper_evidence_detected(self):
        e = m.Evidence()
        e.append("owner", "request", {"demo": True})
        e.events[0]["payload"]["demo"] = False
        self.assertFalse(e.verify())

    def test_restrict_writes(self):
        e = m.Evidence()
        with tempfile.TemporaryDirectory() as d:
            for name in ("data/kt002/resumen.json", "../outside.txt",
                         "docs/visor/index.html", ".github/workflows/kt002.yml"):
                with self.subTest(name=name), self.assertRaises(PermissionError):
                    m.write_synthetic(Path(d), name, "wrong", e)
            self.assertEqual(list(Path(d).rglob("*")), [])

    def test_block_real_orders(self):
        e = m.Evidence()
        for p in ({"asset": "BTC", "real_orders": False},
                  {"asset": "FAKEBTC", "real_orders": True}):
            with self.assertRaises(PermissionError):
                m.review(p, e)

    def test_non_veto_not_sci_approval(self):
        e = m.Evidence()
        status = m.review({"asset": "FAKEBTC", "real_orders": False,
                           "risk_veto": False}, e)
        self.assertEqual(status, "DOCUMENTED_ONLY")
        self.assertTrue(e.verify())
        self.assertEqual(e.events[-2]["payload"]["finding"], "NO SCIENTIFIC APPROVAL")


if __name__ == "__main__":
    unittest.main()
