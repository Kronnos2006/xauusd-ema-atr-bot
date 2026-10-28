import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from lineage_kronnos import build_manifest, verify, write_new
from comparador_motores import compare

class TestLineage(unittest.TestCase):
    def test_reproducible_and_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            f = root / "market.json"
            f.write_bytes(b'{"p":1}')
            m = build_manifest(root, ["market.json"], "v1", "a"*40)
            self.assertTrue(verify(root, m))
            self.assertEqual(m, build_manifest(root, ["market.json"], "v1", "a"*40))
            f.write_bytes(b'{"p":2}')
            self.assertFalse(verify(root, m))

    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)/"base"
            root.mkdir()
            with self.assertRaises(ValueError):
                build_manifest(root, ["../bad"], "v1", "a"*40)

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            file = Path(d)/"m.json"
            write_new(file, {"x": 1})
            with self.assertRaises(FileExistsError):
                write_new(file, {"x": 2})

class TestComparison(unittest.TestCase):
    def test_agreement(self):
        a = {"dataset_sha256": "a"*64, "config_sha256": "b"*64,
             "sample_id": "sealed-v1", "fees_model": "flat", "net_return": .2,
             "max_drawdown": -.1, "trades": 42}
        self.assertTrue(compare(a, dict(a))["agreement"])
        b = dict(a)
        b["dataset_sha256"] = "x"*64
        self.assertFalse(compare(a, b)["comparable"])
        self.assertEqual(compare(a, b)["promocion"], "BLOQUEADA")

if __name__ == "__main__":
    unittest.main()
