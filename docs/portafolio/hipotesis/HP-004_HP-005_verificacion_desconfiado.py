import pandas as pd,numpy as np
from scipy.stats import norm
d=pd.read_csv('data/kt003/btcusdt_1h.csv.gz')
print(d.columns.tolist(),len(d))
tc=[c for c in d.columns if 'time' in c.lower() or 'date' in c.lower()][0]
t=pd.to_datetime(d[tc],utc=True,errors='coerce',format='mixed')
print(t.min(),t.max(),t.isna().sum(), t.duplicated().sum(), (t.dt.minute!=0).sum())
s=d.set_index(t)['close'].resample('1D').last().dropna()
print(len(s),len(s)/365.25)
r=np.log(s).diff().dropna()
print('vol',r.std()*365**.5, 'sd d',r.std())
for a,b in[(20,100),(50,200),(10,50)]:
    sig=(s.rolling(a).mean()>s.rolling(b).mean())[b-1:]
    print(a,b,(sig.astype(int).diff().abs()>0).sum()-0, sig.mean())
z=norm.ppf(.95)+norm.ppf(.8)
n=len(r)
# two-sample diff of means long vs out, sd daily
sd=r.std();n1=n/2
mde=z*sd*np.sqrt(2/n1);print('mde/day',mde, 'sharpe-ish',mde/sd*365**.5)
print('ac1',r.autocorr(1),'abs',r.abs().autocorr(1))
# one-sample sharpe of long-only: MDE
print('1samp', z*sd/np.sqrt(n)/sd*365**.5, 'sr se', 365**.5/np.sqrt(n))
