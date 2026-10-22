"""Pruebas de presentación del observatorio, sin datos de mercado."""
import importlib.util
import unittest
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "tools" / "observatorio_kt002.py"
spec = importlib.util.spec_from_file_location("observatorio_kt002", p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def snapshot():
    def row(wins, p=None):
        d = {"n": 8, "aciertos": wins, "tasa": wins / 8,
             "ic95": [0.1, 0.8]}
        if p is not None:
            d["mcnemar_vs_sube"] = {"p": p}
        return d
    return {
        "variant": "KT-002", "updated_utc": "2026-10-22T14:08:40Z",
        "pronosticos": 39, "vencidos": 35, "profitability_evaluated": False,
        "horas_omitidas": 10, "todos_solapados": {"n_vencidos": 35},
        "sin_solape": {
            "n_vencidos": 8, "siempre_sube": row(4), "kronos": row(3, 1.0),
            "timesfm": row(2, .625), "kt001": row(1, .375)}
    }


class ObservatorioTests(unittest.TestCase):
    def test_normal(self):
        s, issues = mod.render(snapshot())
        self.assertFalse(issues)
        self.assertIn("3/8", s)
        self.assertIn("no dictamen del auditor", s)

    def test_bad_count(self):
        data = snapshot()
        data["sin_solape"]["kronos"]["aciertos"] = 10
        _, issues = mod.render(data)
        self.assertTrue(any("Conteos" in x for x in issues))

    def test_profitability_flag(self):
        data = snapshot()
        data["profitability_evaluated"] = True
        _, issues = mod.render(data)
        self.assertTrue(any("profitability_evaluated" in x for x in issues))

    def test_bad_rate(self):
        data = snapshot()
        data["sin_solape"]["kronos"]["tasa"] = .99
        _, issues = mod.render(data)
        self.assertTrue(any("Tasa" in x for x in issues))


if __name__ == "__main__":
    unittest.main()
