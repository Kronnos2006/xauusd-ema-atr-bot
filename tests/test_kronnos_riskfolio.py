import unittest
from tools.kronnos_riskfolio import analyze_returns

class RiskfolioTests(unittest.TestCase):
    def setUp(self):
        self.matrix=[[0.001*(i%5-2),0.002*((i*3)%7-3),0.001*((i*2)%9-4)] for i in range(50)]
    def test_riskfolio_real_calculation(self):
        result=analyze_returns(self.matrix)
        self.assertTrue(result["covariance_computed"])
        self.assertEqual(result["engine"],"Riskfolio-Lib")
        self.assertFalse(result["live_trading"])
    def test_concentration_limit(self):
        with self.assertRaises(ValueError):
            analyze_returns(self.matrix,max_asset_weight=0.2)
    def test_fails_for_nonfinite(self):
        self.matrix[0][0]=float("nan")
        with self.assertRaises(ValueError):
            analyze_returns(self.matrix)
