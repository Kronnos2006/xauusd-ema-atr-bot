"""KRONNOS Riskfolio-Lib offline covariance, with fail-closed risk limits."""
import math

def analyze_returns(matrix, max_asset_weight=0.4):
    import pandas as pd
    import riskfolio as rp
    if len(matrix)<10 or not matrix or len(matrix[0])<2:
        raise ValueError("Need at least ten periods and two assets")
    n=len(matrix[0])
    if any(len(row)!=n or any(not math.isfinite(float(v)) or float(v)<=-1 for v in row) for row in matrix):
        raise ValueError("Invalid returns")
    if not (0 < max_asset_weight <=1):
        raise ValueError("Invalid asset limit")
    frame=pd.DataFrame(matrix,columns=[f"asset_{i}" for i in range(n)])
    portfolio=rp.Portfolio(returns=frame)
    portfolio.assets_stats(method_mu="hist",method_cov="hist")
    if portfolio.cov is None or portfolio.cov.shape != (n,n):
        raise ValueError("Covariance unavailable")
    equal_weight=1/n
    if equal_weight > max_asset_weight:
        raise ValueError("Concentration limit exceeded")
    return {"engine":"Riskfolio-Lib","assets":n,"observations":len(frame),
            "max_equal_weight":equal_weight,"covariance_computed":True,
            "live_trading":False}
