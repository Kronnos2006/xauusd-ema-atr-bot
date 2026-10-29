import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from kronnos_binance_bars import validate,download
class Tests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(len(validate([[1000,"100","110","90","105","5",1999]])),1)
    def test_bad_ohlc(self):
        with self.assertRaises(ValueError):validate([[1000,"100","99","90","105","5",1999]])
    def test_repeated(self):
        with self.assertRaises(ValueError):validate([[1000,"100","110","90","105","5",1999]]*2)
    def test_reject_arbitrary_symbol_before_network(self):
        with self.assertRaises(ValueError):download("BAD","1h",10)
if __name__=="__main__":unittest.main()
