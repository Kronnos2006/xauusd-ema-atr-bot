#!/usr/bin/env python3
"""Independent, stdlib-only temporal guard for historical FreqAI CSVs.

No trading, no prospective data modifications, no access to sealed holdouts.
"""
import csv
import math


def verify_candles(rows, train_fraction=0.7, lookahead=1):
    if not 0 < train_fraction < 1:
        raise ValueError("Invalid train fraction")
    if lookahead < 1:
        raise ValueError("Lookahead must be positive")
    parsed = []
    for row in rows:
        t = int(row["time_open_ms"])
        end = int(row["time_close_ms"])
        o, h, l, c, v = (float(row[k]) for k in ("open", "high", "low", "close", "volume"))
        if not all(map(math.isfinite, (o, h, l, c, v))):
            raise ValueError("Non-finite candle")
        if not (0 < l <= min(o, c) <= max(o, c) <= h and v >= 0 and t < end):
            raise ValueError("Invalid OHLCV")
        if parsed and (t <= parsed[-1][0] or t <= parsed[-1][1]):
            raise ValueError("Overlapping, duplicated or unsorted candles")
        parsed.append((t, end))
    if len(parsed) < 500:
        raise ValueError("Insufficient bars")
    # FreqAI current experiment constructs samples i=5..len(rows)-2.
    indices = list(range(5, len(parsed) - lookahead))
    cut = int(len(indices) * train_fraction)
    if cut <= 0 or cut >= len(indices):
        raise ValueError("Invalid train/test partition")
    train = indices[:cut]
    test = indices[cut:]
    # A training label targets i + lookahead, so the last training
    # label must not use a candle belonging to the test period.
    if train[-1] + lookahead >= test[0]:
        raise ValueError("LEAKAGE: training label crosses temporal split")
    return {"rows": len(parsed), "train_samples": len(train), "test_samples": len(test),
            "split_safe": True}


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return verify_candles(csv.DictReader(f))
