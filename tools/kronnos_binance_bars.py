#!/usr/bin/env python3
"""Kronnos: capturar barras SPOT Binance desde endpoint fijo; no trading."""
import argparse,csv,hashlib,json,urllib.request
from datetime import datetime,timezone
from pathlib import Path
BASE="https://api.binance.com/api/v3/klines"
SYMBOLS={"BTCUSDT","ETHUSDT"}
INTERVALS={"1h","4h","1d"}
def validate(raw):
    if not isinstance(raw,list) or not raw:raise ValueError("Sin barras")
    output=[];previous=-1
    for bar in raw:
        if not isinstance(bar,list) or len(bar)<7:raise ValueError("Barra incompleta")
        t=int(bar[0]);o,h,l,c,v=map(float,bar[1:6]);end=int(bar[6])
        if not(previous<t and l<=min(o,c)<=max(o,c)<=h and v>=0 and end>t):
            raise ValueError("OHLCV o tiempo invalido")
        previous=t
        output.append(dict(time_open_ms=t,open=o,high=h,low=l,close=c,volume=v,time_close_ms=end))
    return output
def download(symbol,interval,limit):
    if symbol not in SYMBOLS or interval not in INTERVALS or not 2<=limit<=500:raise ValueError("Parametros no permitidos")
    from urllib.parse import urlencode
    url=BASE+"?"+urlencode(dict(symbol=symbol,interval=interval,limit=limit))
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"KronnosResearch/1.0"}),timeout=15) as r:
        return validate(json.load(r))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--symbol",default="BTCUSDT",choices=sorted(SYMBOLS))
    p.add_argument("--interval",default="1h",choices=sorted(INTERVALS))
    p.add_argument("--limit",type=int,default=24)
    p.add_argument("--output",type=Path,default=Path("artifacts/binance-btcusdt-1h.csv"))
    a=p.parse_args();rows=download(a.symbol,a.interval,a.limit)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    report={"source":BASE,"symbol":a.symbol,"interval":a.interval,"rows":len(rows),
            "retrieved_utc":datetime.now(timezone.utc).isoformat(),
            "sha256":hashlib.sha256(a.output.read_bytes()).hexdigest(),
            "historical_data_only":True,"source_receipt_independent":False,
            "prediction_executed":False,"promotion_permitted":False,"trading_real":False}
    a.output.with_suffix(".manifest.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
