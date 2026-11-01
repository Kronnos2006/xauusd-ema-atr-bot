import unittest
from tools.kronnos_freqai_temporal_guard import verify_candles


def candles(n=700):
    out = []
    for i in range(n):
        t = 1_700_000_000_000 + i * 3_600_000
        out.append({"time_open_ms": t, "time_close_ms": t + 3_599_999,
                    "open": 100, "high": 102, "low": 99, "close": 101, "volume": 10})
    return out


class TemporalGuardTests(unittest.TestCase):
    def test_detects_label_overlap_in_original_70_30_split(self):
        with self.assertRaisesRegex(ValueError, "LEAKAGE"):
            verify_candles(candles())

    def test_purged_split_is_temporally_safe(self):
        outcome = verify_candles(candles(), purge=1)
        self.assertTrue(outcome["split_safe"])
        self.assertGreater(outcome["train_samples"], 0)

    def test_rejects_duplicate_candles(self):
        data = candles()
        data[5] = data[4].copy()
        with self.assertRaises(ValueError):
            verify_candles(data)

    def test_rejects_future_or_out_of_order(self):
        data = candles()
        data[6] = data[3].copy()
        with self.assertRaises(ValueError):
            verify_candles(data)

    def test_rejects_nonfinite(self):
        data = candles()
        data[8]["close"] = float("nan")
        with self.assertRaises(ValueError):
            verify_candles(data)


if __name__ == "__main__":
    unittest.main()
