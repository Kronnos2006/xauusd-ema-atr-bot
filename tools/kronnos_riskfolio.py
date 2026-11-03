"""Riskfolio covariance adapter; offline, no trading or promotion authorization."""
import math


def analyze_returns(matrix, max_asset_weight=0.25, weights=None):
    """Aligned daily returns; partial risk gates, never the complete risk framework."""
    if not isinstance(matrix, (list, tuple)) or len(matrix)<60:
        raise ValueError('Need 60 daily periods')
    if not isinstance(matrix[0], (list, tuple)) or not 2<=len(matrix[0])<=8:
        raise ValueError('Need two to eight assets')
    n=len(matrix[0])
    if any(not isinstance(row, (list, tuple)) or len(row)!=n or any(type(v) not in (float,int) or not math.isfinite(v) or v<=-1 for v in row) for row in matrix):
        raise ValueError('Invalid returns')
    if not math.isfinite(max_asset_weight) or not 0<max_asset_weight<=0.25:
        raise ValueError('Cannot relax 25% per-position limit')
    w=[1/n]*n if weights is None else list(weights)
    if len(w)!=n or any(type(x) not in (float,int) or not math.isfinite(x) or x<0 for x in w):
        raise ValueError('Invalid weights; shorts prohibited')
    if sum(w)>1+1e-12 or max(w)>max_asset_weight+1e-12 or sum(w)<=0:
        raise ValueError('Exposure or concentration limit exceeded')
    import numpy as np
    import pandas as pd
    import riskfolio as rp
    frame=pd.DataFrame(matrix[-60:],columns=[f'asset_{i}' for i in range(n)])
    if (frame.std() <= 0).any():
        raise ValueError('Constant assets have no defined correlation')
    portfolio=rp.Portfolio(returns=frame)
    portfolio.assets_stats(method_mu='hist',method_cov='hist')
    cov=np.asarray(portfolio.cov,dtype=float)
    corr=frame.corr().to_numpy()
    if cov.shape!=(n,n) or not np.isfinite(cov).all() or not np.isfinite(corr).all():
        raise ValueError('Covariance/correlation unavailable')
    active=[i for i in range(n) if w[i]>0]
    c=corr[np.ix_(active,active)]
    eigen=np.linalg.eigvalsh(c)
    if eigen.min() < -1e-8:
        raise ValueError('Invalid correlation matrix')
    effective=float(eigen.sum()**2/np.square(eigen).sum())
    mean_corr=float((c.sum()-len(active))/(len(active)*(len(active)-1))) if len(active)>1 else 1.0
    if len(active)>1 and (effective<2-1e-10 or mean_corr>0.5+1e-12):
        raise ValueError('Diversification limits exceeded')
    remaining=set(active)
    while remaining:
        component={remaining.pop()}
        while True:
            linked={j for j in remaining if any(corr[i,j]>0.70 for i in component)}
            if not linked: break
            component.update(linked)
            remaining.difference_update(linked)
        if sum(w[i] for i in component)>0.25+1e-12:
            raise ValueError('Correlated group exceeds 25%')
    annual_vol=math.sqrt(max(0.0,float(np.array(w)@cov@np.array(w)))*365)
    if annual_vol>0.10+1e-12:
        raise ValueError('Annualized volatility exceeds 10%')
    return {'engine':'Riskfolio-Lib','assets':n,'observations':len(matrix),
            'risk_window_daily':60,'gross':sum(w),'max_weight':max(w),
            'annualized_volatility':annual_vol,'mean_correlation':mean_corr,
            'effective_assets':effective,'covariance_computed':True,
            'full_risk_framework_verified':False,'promotion_permitted':False,'live_trading':False}
