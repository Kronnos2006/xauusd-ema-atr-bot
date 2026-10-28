import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from atlas_p0_guard import check, CHECKS

class AtlasP0GuardTests(unittest.TestCase):
    def test_empty_blocks_everything(self):
        report=check({})
        self.assertFalse(report["promocion_permitida"])
        self.assertEqual(sum(x["estado"]=="BLOQUEADO" for x in report["controles"]),5)
    def test_forged_manifest_never_promotes(self):
        fields={f for _,items in CHECKS for f in items}
        doc={f:("a"*64 if f.endswith("_sha256") else True if f.endswith(("independent","review")) else 74 if f=="n_variants" else "fake") for f in fields}
        report=check(doc)
        self.assertFalse(report["promocion_permitida"])
        self.assertFalse(report["cierre_p0_autorizado"])
        self.assertEqual(len(report["controles"]),5)
    def test_bool_as_variant_count_rejected(self):
        self.assertIn("n_variants",check({"n_variants":True})["controles"][0]["faltantes"])
    def test_malformed_data_rejected(self):
        with self.assertRaises(ValueError):check([])

if __name__=="__main__":unittest.main()
