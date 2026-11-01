import unittest
from tools.kronnos_finance_offline import metrics, exposure_guard

class FinanceOfflineTests(unittest.TestCase):
    def test_net_costs_and_benchmark(self):
        r=metrics([0.02,-0.01,0.03],[0.01,0.0,0.01],cost_per_period=0.002)
        self.assertEqual(r["observations"],3)
        self.assertLess(r["net_total_return"],metrics([0.02,-0.01,0.03],[0.01,0,0.01])["net_total_return"])
        self.assertGreater(r["max_drawdown"],0)
    def test_rejects_misalignment(self):
        with self.assertRaises(ValueError):
            metrics([0.1]*4,[0.1]*3)
    def test_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            metrics([0.1,float("nan"),0.1],[0.1]*3)
    def test_concentration_rejected(self):
        with self.assertRaisesRegex(ValueError,"Risk limit"):
            exposure_guard([0.7,0.1])
    def test_limits_and_no_live(self):
        result=exposure_guard([0.35,0.3,0.2])
        self.assertFalse(result["permitted_for_live_trading"])
        self.assertAlmostEqual(result["gross"],0.85)
    def test_total_leverage_rejected(self):
        with self.assertRaises(ValueError):
            exposure_guard([0.35,0.35,0.35])

if __name__ == "__main__":
    unittest.main()
