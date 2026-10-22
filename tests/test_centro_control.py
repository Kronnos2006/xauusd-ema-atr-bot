"""Comprobaciones del Centro de Control sin red ni credenciales."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "centro_control.py"
spec = importlib.util.spec_from_file_location("centro_control", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CentroControlTests(unittest.TestCase):
    def fixture(self, root, duplicate=False):
        for rel in ("dashboard", "docs/gerencia", "data/kt002"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        (root / "dashboard/index.html").write_text("<!doctype html><title>Test</title>", encoding="utf-8")
        team = {"areas": {"dir": {"nombre": "Dirección"}}, "miembros": [
            {"clave": "gerente", "nombre": "Gerente", "area": "dir", "reporta_a": None},
            {"clave": "auditor", "nombre": "Auditor", "area": "dir", "reporta_a": "gerente", "independiente": True}]}
        if duplicate:
            team["miembros"].append(dict(team["miembros"][1]))
        (root / "docs/gerencia/equipo.json").write_text(json.dumps(team), encoding="utf-8")
        m = lambda win: {"n": 8, "aciertos": win, "tasa": win / 8, "ic95": [0.1, 0.8]}
        summary = {"variant": "KT-002", "profitability_evaluated": False,
            "pronosticos": 40, "vencidos": 36, "horas_omitidas": 10,
            "sin_solape": {"n_vencidos": 8, "siempre_sube": m(4), "kronos": m(3),
                           "timesfm": m(2), "kt001": m(1)}}
        (root / "data/kt002/resumen.json").write_text(json.dumps(summary), encoding="utf-8")

    def test_assemble(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.fixture(root)
            obj = mod.assemble(root)
            self.assertEqual(obj["kt002"]["independientes"], 8)
            self.assertEqual(len(obj["agents"]["links"]), 1)
            self.assertEqual(obj["agents"]["independent"], ["auditor"])
            self.assertTrue(obj["meta"]["readonly"])

    def test_build(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.fixture(root)
            out = root / "dist"
            mod.build(out, root)
            self.assertTrue((out / "index.html").is_file())
            self.assertEqual(json.loads((out / "data.json").read_text())["kt002"]["pronosticos"], 40)

    def test_duplicate_agent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root, duplicate=True)
            with self.assertRaisesRegex(ValueError, "duplicadas"):
                mod.assemble(root)

    def test_bad_parent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            team=root/"docs/gerencia/equipo.json"
            data=json.loads(team.read_text());data["miembros"][1]["reporta_a"]="fantasma"
            team.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "inexistente"):
                mod.assemble(root)

    def test_no_profitability_claim(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            path=root/"data/kt002/resumen.json"
            data=json.loads(path.read_text());data["profitability_evaluated"]=True
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError):
                mod.assemble(root)


if __name__=="__main__":
    unittest.main()
