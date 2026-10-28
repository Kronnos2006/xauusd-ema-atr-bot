import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from motores_gratis import inspect_engine

class TestFreeEngines(unittest.TestCase):
    def test_lean_missing_source_fails_closed(self):
        result=inspect_engine("lean","/directorio-no-existente")
        self.assertFalse(result["ready_to_build"])
        self.assertEqual(result["paid_cli"],"NOT_USED")
    def test_unknown(self):
        with self.assertRaises(ValueError):inspect_engine("live")
    def test_nautilus_diagnostic_no_order(self):
        result=inspect_engine("nautilus")
        self.assertEqual(result["live_trading"],"DISABLED")
        self.assertIn("installed",result)

if __name__=="__main__":unittest.main()
