"""Fixture CI sintético reproducible; nunca presentar como datos Binance."""
import csv,math,sys
from pathlib import Path
out=Path(sys.argv[1]);out.parent.mkdir(parents=True,exist_ok=True)
with out.open("w",newline="") as f:
    w=csv.writer(f);w.writerow(("time_open_ms","open","high","low","close","volume","time_close_ms"))
    p=100.0
    for i in range(160):
        old=p;p*=1+0.003*math.sin(i*.38)+0.0004*math.cos(i*.91)
        lo=min(old,p)*.999;hi=max(old,p)*1.001
        t=(1700000000+i*3600)*1000
        w.writerow((t,old,hi,lo,p,10+math.sin(i)**2,t+3599999))
