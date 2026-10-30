import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from informe_gerencia_sin_ia import generate,inspect_modules
class Tests(unittest.TestCase):
    def test_missing_evidence_never_promotes(self):
        with tempfile.TemporaryDirectory() as folder:
            r=inspect_modules(Path(folder))
            self.assertEqual(r["kronnos"]["kt002_operativo"],"NO_VERIFICADO")
            self.assertFalse(r["atlas"]["promocion_permitida"])
            self.assertEqual(r["orion"]["servicio_operativo"],"NO_VERIFICADO")
    def test_output_includes_three_modules(self):
        r=generate(Path(__file__).resolve().parents[1])
        self.assertEqual(set(r["modulos"]),{"kronnos","orion","atlas"})
        self.assertFalse(r["modulos"]["atlas"]["promocion_permitida"])
if __name__=="__main__":unittest.main()
