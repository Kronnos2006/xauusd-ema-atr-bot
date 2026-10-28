import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from atlas_verificador_evidencias import check
class Tests(unittest.TestCase):
    def test_missing(self):
        r=check("/missing","/missing","/missing","2026-01-01T00:00:00Z")
        self.assertFalse(r["promocion_permitida"])
        self.assertEqual(r["firma_rfc3161"],"NO_VERIFICADA")
    def test_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[Path(d)/x for x in ("data","token","ca")]
            for p in paths:p.write_text("fake")
            with patch("atlas_verificador_evidencias.openssl",return_value=(False,"signature error")):
                r=check(*paths,"2026-01-01T00:00:00Z")
            self.assertEqual(r["integridad"],"NO_VERIFICADA")
    def test_future(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[Path(d)/x for x in ("data","token","ca")]
            for p in paths:p.write_text("fake")
            with patch("atlas_verificador_evidencias.openssl",side_effect=[(True,"ok"),(True,"Time stamp: Oct 29 00:00:00 2026 GMT")]):
                r=check(*paths,"2026-10-28T00:00:00Z")
            self.assertNotEqual(r["anterior_al_evento"],"CONFIRMADO")
            self.assertFalse(r["promocion_permitida"])
if __name__=="__main__":unittest.main()
