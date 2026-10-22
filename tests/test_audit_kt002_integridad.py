"""Pruebas sintéticas: no descargan velas ni usan resultados de mercado."""
import csv
import importlib.util
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MOD = Path(__file__).resolve().parents[1] / "tools" / "audit_kt002_integridad.py"
spec = importlib.util.spec_from_file_location("audit_kt002_integridad", MOD)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
BASE = datetime(2026, 10, 21, 0, tzinfo=timezone.utc)
COLUMNS = ["run_utc", "base_open_utc", "target_open_utc", "actual_ret", "scored_utc"]


def row(hour, scored=True):
    base = BASE + timedelta(hours=hour)
    target = base + timedelta(hours=4)
    return {
        "run_utc": (base + timedelta(hours=1, minutes=7)).isoformat(),
        "base_open_utc": base.isoformat(),
        "target_open_utc": target.isoformat(),
        "actual_ret": "0.01" if scored else "",
        "scored_utc": (target + timedelta(hours=1, minutes=7)).isoformat() if scored else "",
    }


class AuditTests(unittest.TestCase):
    def check(self, rows):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "data.csv"
            with path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            return audit.inspect(path)

    def test_normal(self):
        a = self.check([row(i) for i in range(24)])
        self.assertEqual(a["veredicto_integridad_basica"], "SIN_ANOMALIAS_ESTRUCTURALES")
        self.assertEqual(a["horas_omitidas_ultimas_24_bases"], 0)
        self.assertEqual(a["puntuadas"], 24)

    def test_missing_hour(self):
        a = self.check([row(i) for i in range(24) if i != 10])
        self.assertEqual(a["horas_omitidas_ultimas_24_bases"], 1)

    def test_duplicate(self):
        a = self.check([row(0), row(0)])
        self.assertEqual(a["duplicadas"], 1)
        self.assertEqual(a["veredicto_integridad_basica"], "REVISAR")

    def test_early_score(self):
        r = row(0)
        r["scored_utc"] = (BASE + timedelta(hours=4)).isoformat()
        self.assertEqual(self.check([r])["puntuaciones_tempranas_o_sin_fecha"], 1)

    def test_bad_target(self):
        r = row(0)
        r["target_open_utc"] = (BASE + timedelta(hours=5)).isoformat()
        self.assertEqual(self.check([r])["objetivos_con_desfase"], 1)

    def test_unscored(self):
        self.assertEqual(self.check([row(0, scored=False)])["puntuadas"], 0)


if __name__ == "__main__":
    unittest.main()
