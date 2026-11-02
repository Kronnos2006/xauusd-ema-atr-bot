"""Comprobaciones del Centro de Control sin red ni credenciales."""
import importlib.util
import json
import re
import shlex
import shutil
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "centro_control.py"
spec = importlib.util.spec_from_file_location("centro_control", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CentroControlTests(unittest.TestCase):
    def test_pages_both_routes_have_all_relative_scripts(self):
        # Replay actual publication copies against a real generated artifact.
        repo = MODULE.parents[1]
        with tempfile.TemporaryDirectory() as d:
            out = Path(d)/'orion-pages'
            mod.build(out, repo, public=True)
            for route in ('orion', 'visor'):
                (out/route).mkdir()
            workflow = (repo/'.github/workflows/orion-pages.yml').read_text(encoding='utf-8')
            for line in workflow.splitlines():
                if not line.strip().startswith('cp '):
                    continue
                _, source, target = shlex.split(line.strip())
                source = source.replace('$RUNNER_TEMP/orion-pages', str(out))
                target = target.replace('$RUNNER_TEMP/orion-pages', str(out))
                source_path = Path(source) if Path(source).is_absolute() else repo/source
                shutil.copyfile(source_path, target)
            for route in (out, out/'orion'):
                html = (route/'index.html').read_text(encoding='utf-8')
                scripts = re.findall(r'<script src="\./([^"]+)"', html)
                self.assertIn('health.js', scripts)
                for asset in scripts:
                    self.assertTrue((route/asset).is_file(), str(route/asset))
                    self.assertEqual((route/asset).read_bytes(), (repo/'dashboard'/asset).read_bytes())

    def test_module_sources_missing_are_never_healthy(self):
        with tempfile.TemporaryDirectory() as d:
            result = mod.module_evidence(Path(d))
            self.assertEqual({x['name'] for x in result}, {'ORION', 'ATLAS', 'FreqAI', 'KT-002'})
            self.assertTrue(all(x['status'].startswith('NO VERIFICADO') for x in result))
            self.assertTrue(all(x['sha256'] is None for x in result))

    def test_module_hash_tracks_evidence_without_certifying_service(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); self.fixture(root)
            first = mod.module_evidence(root)
            self.assertIn('NO VERIFICADA', first[0]['status'])
            (root/'docs/gerencia/equipo.json').write_text('{}')
            self.assertNotEqual(first[0]['sha256'], mod.module_evidence(root)[0]['sha256'])

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

    def test_public_export_hides_private_office_and_descriptions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            out=root/"public"
            mod.build(out,root,public=True)
            data=json.loads((out/"data.json").read_text(encoding="utf-8"))
            self.assertNotIn("office",data["governance"]["links"])
            self.assertTrue(all(not m["description"] for m in data["agents"]["nodes"]))
            self.assertTrue(data["meta"]["readonly"])

    def test_historical_nonoverlap_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            p=root/"data/kt002/predicciones.csv"
            p.write_text(
                "base_open_utc,actual_ret,kronos_ret,timesfm_ret,kt001_ret\n"
                "2026-10-22T00:00:00+00:00,0.02,0.1,-0.1,0.2\n"
                "2026-10-22T01:00:00+00:00,-0.02,-0.1,-0.1,-0.2\n"
                "2026-10-22T04:00:00+00:00,-0.03,0.1,-0.1,-0.1\n"
                "2026-10-22T08:00:00+00:00,,0.1,-0.1,-0.1\n",
                encoding="utf-8"
            )
            points=mod.assemble(root)["kt002"]["historia"]
            self.assertEqual(len(points),2)
            self.assertEqual(points[-1]["rates"]["kronos"],0.5)
            self.assertEqual(points[-1]["rates"]["timesfm"],0.5)
            self.assertEqual(points[-1]["rates"]["siempre_sube"],0.5)

    def test_public_has_only_public_navigation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self.fixture(root)
            out=root/"public";mod.build(out,root,public=True)
            j=json.loads((out/"data.json").read_text(encoding="utf-8"))
            self.assertNotIn("office",j["governance"]["links"])
            self.assertTrue(j["governance"]["links"]["visor"].endswith("/visor/"))
            self.assertIn("github.com",j["governance"]["links"]["tasks"])

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
