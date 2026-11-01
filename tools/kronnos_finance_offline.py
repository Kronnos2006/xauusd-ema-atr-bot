#!/usr/bin/env python3
"""KRONNOS offline risk and return checks. Research only; no broker or network."""
import math
from statistics import mean, stdev

def metrics(returns, benchmark, annualization=365, cost_per_period=0.0):
    if len(returns) != len(benchmark) or len(returns) < 3:
        raise ValueError("At least 3 aligned observations required")
    if annualization <= 0 or cost_per_period < 0:
        raise ValueError("Invalid annualization or cost")
    a = [float(x) for x in returns]
    b = [float(x) for x in benchmark]
    if any(not math.isfinite(x) or x <= -1 for x in a + b) or not math.isfinite(cost_per_period):
        raise ValueError("Invalid returns or cost")
    net = [x-cost_per_period for x in a]
    if any(x <= -1 for x in net):
        raise ValueError("Cost produces impossible return")
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for x in net:
        equity *= (1+x)
        peak = max(peak,equity)
        max_dd = max(max_dd, 1-equity/peak)
    benchmark_equity = math.prod(1+x for x in b)
    vol = stdev(net)
    sharpe = mean(net)/vol * math.sqrt(annualization) if vol > 0 else None
    return {"observations":len(net),"net_total_return":equity-1,
            "benchmark_total_return":benchmark_equity-1,
            "max_drawdown":max_dd,"annualized_sharpe":sharpe,
            "assumption":"simple period returns, fixed cost per period, no trading"}

def exposure_guard(weights, max_gross=1.0, max_single=0.4):
    """Fail closed on leverage, concentration and invalid portfolio weights."""
    w=[float(x) for x in weights]
    if not w or any(not math.isfinite(x) for x in w) or not (0 < max_single <= max_gross):
        raise ValueError("Invalid weights or limits")
    gross=sum(abs(x) for x in w)
    if gross>max_gross+1e-12 or max(abs(x) for x in w)>max_single+1e-12:
        raise ValueError("Risk limit exceeded")
    return {"gross":gross,"net":sum(w),"max_single":max(abs(x) for x in w),
            "permitted_for_live_trading":False}
