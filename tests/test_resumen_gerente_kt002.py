"""Pruebas del resumen de gerente, con entradas sintéticas."""
import csv
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "resumen_gerente_kt002.py"
spec = importlib.util.spec_from_file_location("resumen_gerente_kt002", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
T = datetime(2026, 10, 22, 0, tzinfo=timezone.utc)
FIELDS = ["run_utc", "base_open_utc", "target_open_utc", "actual_ret", "scored_utc"]


def sample(hour, premature=False):
    base = T + timedelta(hours=hour)
    target = base + timedelta(hours=4)
    return {
        "run_utc": (base + timedelta(hours=1, minutes=7)).isoformat(),
        "base_open_utc": base.isoformat(),
        "target_open_utc": target.isoformat(),
        "actual_ret": "0.02",
        "scored_utc": (target + (timedelta(minutes=30) if premature else timedelta(hours=1))).isoformat(),
    }


class CompactReportTests(unittest.TestCase):
    def run_report(self, rows, reported=None):
        with tempfile.TemporaryDirectory() as td:
            a, b = Path(td) / "p.csv", Path(td) / "r.json"
            with a.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, FIELDS)
                w.writeheader()
                w.writerows(rows)
            b.write_text(json.dumps({"pronosticos": len(rows) if reported is None else reported,
                                     "vencidos": len(rows), "sin_solape": {}}))
            return mod.report(a, b)

    def test_normal(self):
        out = self.run_report([sample(i) for i in range(24)])
        self.assertEqual(out["errors"], [])
        self.assertEqual(out["missing24"], 0)
        self.assertEqual(len(out["lines"]), 5)

    def test_bad_snapshot(self):
        out = self.run_report([sample(0)], reported=2)
        self.assertTrue(any("no coincide" in x for x in out["errors"]))

    def test_early_score(self):
        out = self.run_report([sample(0, premature=True)])
        self.assertTrue(any("prematura" in x for x in out["errors"]))

    def test_duplicate(self):
        out = self.run_report([sample(0), sample(0)])
        self.assertIn("bases duplicadas", out["errors"])


if __name__ == "__main__":
    unittest.main()
