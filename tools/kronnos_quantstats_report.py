#!/usr/bin/env python3
"""Offline QuantStats metrics for previously simulated simple returns."""
import math

def quantstats_report(net_returns, benchmark_returns, periods=365):
    import pandas as pd
    import quantstats as qs
    if len(net_returns) != len(benchmark_returns) or len(net_returns) < 3:
        raise ValueError("Need aligned returns, n>=3")
    a=[float(v) for v in net_returns]
    b=[float(v) for v in benchmark_returns]
    if any(not math.isfinite(x) or x <= -1 for x in a+b):
        raise ValueError("Non-finite/impossible returns")
    idx=pd.date_range("2020-01-01",periods=len(a),freq="D",tz="UTC")
    s=pd.Series(a,index=idx)
    benchmark=pd.Series(b,index=idx)
    return {"engine":"QuantStats","count":len(a),
            "net_total_return":float(qs.stats.comp(s)),
            "benchmark_total_return":float(qs.stats.comp(benchmark)),
            "max_drawdown":float(qs.stats.max_drawdown(s)),
            "sharpe":float(qs.stats.sharpe(s,periods=periods)),
            "live_trading":False}
