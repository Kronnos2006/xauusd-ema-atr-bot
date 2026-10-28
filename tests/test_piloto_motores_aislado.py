import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from piloto_motores_aislado import run

class TestMotorContract(unittest.TestCase):
    def test_fixture_only(self):
        r=run()
        self.assertEqual(r["status"],"CONTRACT_ONLY")
        self.assertEqual(r["engine_b"],"LOCAL_REFERENCE_CLONE_NOT_EXTERNAL")
        self.assertTrue(r["comparison"]["agreement"])
        self.assertEqual(r["comparison"]["promocion"],"BLOQUEADA")
        self.assertEqual(r["operacion_real"],"NO_AUTORIZADA")

if __name__=="__main__":
    unittest.main()
