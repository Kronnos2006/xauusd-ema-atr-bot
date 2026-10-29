import hashlib,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from diagnostico_modelos_kronnos import inspect
class Tests(unittest.TestCase):
    def test_no_evidence_never_active(self):
        with tempfile.TemporaryDirectory() as d:
            r=inspect(Path(d),{})
            self.assertFalse(r["promocion_permitida"])
            self.assertTrue(all(x["status"]=="NO_VERIFICADO" for x in r["models"].values()))
    def test_valid_hash_is_only_local_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/"data.txt").write_text("sample")
            h=hashlib.sha256(b"sample").hexdigest()
            r=inspect(p,{"Kronos":{"evidence_path":"data.txt","sha256":h}})
            self.assertEqual(r["models"]["Kronos"]["status"],"EVIDENCIA_LOCAL_COINCIDE")
            self.assertEqual(r["kt002_operativo"],"NO_VERIFICADO")
    def test_tampered_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/"data.txt").write_text("bad")
            r=inspect(p,{"TimesFM":{"evidence_path":"data.txt","sha256":"0"*64}})
            self.assertEqual(r["models"]["TimesFM"]["status"],"HASH_INCORRECTO")
    def test_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            r=inspect(Path(d),{"KT-001":{"evidence_path":"../escape","sha256":"0"*64}})
            self.assertEqual(r["models"]["KT-001"]["status"],"RUTA_INVALIDA")
if __name__=="__main__":unittest.main()
