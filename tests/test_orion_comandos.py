import importlib.util
import tempfile
import unittest
from pathlib import Path

P=Path(__file__).resolve().parents[1]/"tools"/"orion_comandos.py"
spec=importlib.util.spec_from_file_location("orion_comandos",P)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class OrionCommandsTests(unittest.TestCase):
    def test_allowed(self):
        for action in ("estado","modelos","integridad-basica"):
            self.assertTrue(mod.command_spec(action)[0].startswith("tools/"))

    def test_block_unsafe(self):
        for action in ("git push", "shell", "kt002_prospectivo", "claude", "", "../"):
            with self.assertRaises(ValueError):
                mod.command_spec(action)

    def test_viewer_missing_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"Faltan"):
                mod.publication_check(Path(tmp))

    def test_publication_requires_both_viewers_and_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for path in ("dashboard/index.html","docs/visor/index.html",
                        ".github/workflows/orion-pages.yml"):
                target=root/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text("placeholder",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"incompleta"):
                mod.publication_check(root)
            (root/".github/workflows/orion-pages.yml").write_text(
                "cp docs/visor/index.html\ncmp docs/visor/index.html\nactions/deploy-pages@v4",
                encoding="utf-8"
            )
            self.assertIn("verificada",mod.publication_check(root))


if __name__=="__main__":
    unittest.main()
