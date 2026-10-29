#!/usr/bin/env python3
"""Kronnos -> FreqAI research bridge: strictly historical features, no broker."""
import argparse,csv,hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path

FIELDS=("date","open","high","low","close","volume")
def convert(source:Path,target:Path):
    data=list(csv.DictReader(source.open(newline="")))
    if len(data)<3: raise ValueError("Se requieren al menos 3 velas")
    prior=-1; output=[]
    for row in data:
        t=int(row["time_open_ms"]); end=int(row["time_close_ms"])
        o,h,l,c,v=(float(row[k]) for k in ("open","high","low","close","volume"))
        if not all(math.isfinite(x) for x in (o,h,l,c,v)): raise ValueError("Dato no finito")
        if not (t>prior and end>t and 0<l<=min(o,c)<=max(o,c)<=h and v>=0):
            raise ValueError("OHLCV o cronologia incorrecta")
        if end >= int(datetime.now(timezone.utc).timestamp()*1000):
            raise ValueError("Vela no cerrada o del futuro")
        output.append(dict(date=datetime.fromtimestamp(t/1000,timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                           open=o,high=h,low=l,close=c,volume=v))
        prior=t
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(output)
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    manifest={"format":"freqtrade_ohlcv_csv_staging","rows":len(output),"sha256":digest,
              "input_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
              "freqai_runtime_executed":False,"training_executed":False,
              "prospective_predictions":False,"promotion_permitted":False,"trading_real":False}
    target.with_suffix(".manifest.json").write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
    return manifest
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(convert(a.input,a.output),sort_keys=True))
