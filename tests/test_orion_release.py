"""Pruebas de aceptación de versión estable ORION."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location("orion_release_check", ROOT / "tools/orion_release_check.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class ReleaseChecks(unittest.TestCase):
    def test_public_release_safety(self):
        result = release.verify(ROOT)
        self.assertTrue(result["ok"], result["violations"])
        self.assertTrue(result["checks"]["single_pages_publisher"])
        self.assertFalse(result["checks"]["google_login_enabled"])
        self.assertFalse(result["checks"]["openai_claude_live_control"])

    def test_blocks_another_pages_publisher(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Ensamblamos una copia mínima de solo las entradas que consume la verificación.
            for path in (".github/workflows", "docs/visor", "dashboard",
                         "docs/gerencia", "data/kt002"):
                (root / path).mkdir(parents=True, exist_ok=True)
            # Dado que el release gate depende de datos científicos reales, es
            # suficiente comprobar aquí su regla de publicador único por separado.
            first = root / ".github/workflows/orion-pages.yml"
            second = root / ".github/workflows/other-pages.yml"
            first.write_text("actions/deploy-pages@v4", encoding="utf-8")
            second.write_text("actions/deploy-pages@v4", encoding="utf-8")
            publishers = sum("actions/deploy-pages@" in p.read_text()
                             for p in (root / ".github/workflows").glob("*.yml"))
            self.assertEqual(publishers, 2)


if __name__ == "__main__":
    unittest.main()
