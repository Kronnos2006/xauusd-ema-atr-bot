import random
import math
import statistics
import unittest
from tools.kronnos_riskfolio import analyze_returns


class RiskfolioTests(unittest.TestCase):
    def setUp(self):
        rng=random.Random(20261101)
        self.matrix=[[rng.uniform(-.001,.001) for _ in range(4)] for _ in range(90)]

    def test_actual_library_and_risk_window(self):
        r=analyze_returns(self.matrix)
        self.assertTrue(r['covariance_computed'])
        self.assertEqual(r['risk_window_daily'],60)
        self.assertLessEqual(r['annualized_volatility'],.10)
        self.assertGreaterEqual(r['effective_assets'],2)
        for key in ['promotion_permitted','full_risk_framework_verified','live_trading']:
            self.assertFalse(r[key])

    def test_cannot_relax_framework(self):
        for limit in [.4,float('nan'),float('inf'),0]:
            with self.assertRaises(ValueError): analyze_returns(self.matrix,limit)

    def test_partial_exposure_leaves_cash(self):
        r=analyze_returns(self.matrix,weights=[.1]*4)
        self.assertAlmostEqual(r['gross'],.4)
        self.assertAlmostEqual(r['max_weight'],.1)

    def test_covariance_risk_matches_independent_sample_calculation(self):
        daily=[sum(row)/4 for row in self.matrix[-60:]]
        expected=statistics.stdev(daily)*math.sqrt(365)
        self.assertAlmostEqual(analyze_returns(self.matrix)['annualized_volatility'],expected,places=10)

    def test_older_history_does_not_change_fixed_risk_window(self):
        changed=[[.2]*4 for _ in range(30)]+self.matrix[-60:]
        self.assertAlmostEqual(analyze_returns(changed)['annualized_volatility'],
                               analyze_returns(self.matrix)['annualized_volatility'])

    def test_exposure_short_and_concentration(self):
        for w in [[.4,.2,.2,.2],[.25]*5,[-.1,.2,.2,.2],[0]*4,[float('nan')]*4]:
            with self.assertRaises(ValueError): analyze_returns(self.matrix,weights=w)

    def test_history_and_nonfinite(self):
        with self.assertRaises(ValueError): analyze_returns(self.matrix[:59])
        for v in [float('nan'),float('inf'),-1,True]:
            m=[row[:] for row in self.matrix];m[0][0]=v
            with self.assertRaises(ValueError): analyze_returns(m)

    def test_gross_exposure_is_separate_from_single_position_limit(self):
        m=[row+row for row in self.matrix]
        with self.assertRaisesRegex(ValueError,'Exposure'):
            analyze_returns(m,weights=[.2]*8)

    def test_shape_and_position_count(self):
        for m in [[[.001]*9]*60, [[.001]]*60, [None]*60, self.matrix[:59]+[[.001]]]:
            with self.assertRaises(ValueError): analyze_returns(m)

    def test_correlation_and_constant_assets(self):
        for m in [[[row[0]]*4 for row in self.matrix],[[0]*4]*90]:
            with self.assertRaises(ValueError): analyze_returns(m)

    def test_high_volatility_rejected(self):
        with self.assertRaises(ValueError): analyze_returns([[v*100 for v in row] for row in self.matrix])

    def test_correlated_cluster_rejected(self):
        m=[row[:] for row in self.matrix]
        for row in m: row[1]=row[0]
        with self.assertRaises(ValueError): analyze_returns(m)


if __name__=='__main__': unittest.main()
