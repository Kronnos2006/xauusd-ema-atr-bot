"""KRONNOS VectorBT offline backtesting adapter. Synthetic data only in tests."""
import math

def evaluate(prices, entries, exits, fees=0.001):
    import numpy as np
    import vectorbt as vbt
    if len(prices) < 10 or len(prices)!=len(entries) or len(prices)!=len(exits):
        raise ValueError("Need aligned, sufficiently long series")
    if not 0<=fees<1:
        raise ValueError("Invalid fee")
    a=np.array(prices,dtype=float)
    if not np.all(np.isfinite(a)) or np.any(a<=0):
        raise ValueError("Invalid prices")
    pf=vbt.Portfolio.from_signals(a,entries=np.asarray(entries,dtype=bool),
                                  exits=np.asarray(exits,dtype=bool),
                                  fees=fees,freq="1h",init_cash=10000)
    return {"engine":"vectorbt","total_return":float(pf.total_return()),
            "trade_count":int(pf.trades.count()),"trading_real":False,
            "holdout_used":False}
