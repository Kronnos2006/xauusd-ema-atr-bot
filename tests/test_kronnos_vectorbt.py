import unittest
from tools.kronnos_vectorbt import evaluate

class BacktestTests(unittest.TestCase):
    def test_offline_vectorbt(self):
        prices=[100+i for i in range(30)]
        entries=[i==2 for i in range(30)]
        exits=[i==20 for i in range(30)]
        result=evaluate(prices,entries,exits)
        self.assertEqual(result["engine"],"vectorbt")
        self.assertGreaterEqual(result["trade_count"],1)
        self.assertFalse(result["trading_real"])
    def test_rejects_misaligned(self):
        with self.assertRaises(ValueError):
            evaluate([1]*30,[True]*29,[False]*30)
    def test_rejects_bad_prices(self):
        with self.assertRaises(ValueError):
            evaluate([1]*29+[float("nan")],[False]*30,[False]*30)
