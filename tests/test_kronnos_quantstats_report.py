import unittest
from tools.kronnos_quantstats_report import quantstats_report

class QuantStatsReportTests(unittest.TestCase):
    def test_quantstats_is_really_executed(self):
        report=quantstats_report([.01,-.02,.015,.01,-.005],[.01,0,.01,0,.01])
        self.assertEqual(report["engine"],"QuantStats")
        self.assertEqual(report["count"],5)
        self.assertLess(report["max_drawdown"],0)
        self.assertFalse(report["live_trading"])
    def test_fail_closed_length(self):
        with self.assertRaises(ValueError):
            quantstats_report([.01,.02,.03],[.01,.02])
    def test_fail_closed_nan(self):
        with self.assertRaises(ValueError):
            quantstats_report([.01,float("nan"),.03],[0,.01,.02])
