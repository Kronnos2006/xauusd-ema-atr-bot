#!/usr/bin/env python3
"""Kronnos: public historical Binance Vision SPOT monthly BTCUSDT 1h, SHA256 checked."""
import argparse,csv,hashlib,io,json,re,urllib.request,zipfile
from pathlib import Path
def fetch(month="2025-09", output=Path("artifacts/binance-historical.csv")):
    if not re.fullmatch(r"20[12][0-9]-(0[1-9]|1[0-2])",month):
        raise ValueError("Mes invalido")
    filename=f"BTCUSDT-1h-{month}.zip"
    base=f"https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/{filename}"
    def get(url):
        with urllib.request.urlopen(url,timeout=25) as res:
            value=res.read(8_000_001)
            if len(value)>8_000_000:raise ValueError("Archivo demasiado grande")
            return value
    packed=get(base)
    checksum=get(base+".CHECKSUM").decode().strip().split()[0].lower()
    digest=hashlib.sha256(packed).hexdigest()
    if not re.fullmatch(r"[0-9a-f]{64}",checksum) or checksum!=digest:
        raise ValueError("Binance CHECKSUM incorrecto")
    with zipfile.ZipFile(io.BytesIO(packed)) as zipped:
        if zipped.namelist()!=[filename.replace(".zip",".csv")]:
            raise ValueError("ZIP contenido inesperado")
        raw=zipped.read(zipped.namelist()[0])
        if len(raw)>6_000_000:raise ValueError("CSV demasiado grande")
    rows=[];last=-1
    for fields in csv.reader(io.StringIO(raw.decode())):
        if len(fields)<7:raise ValueError("Campos insuficientes")
        start=int(fields[0]);end=int(fields[6])
        if start>10**14:start//=1000;end//=1000 # 2025+ SPOT microseconds
        o,h,l,c,v=map(float,fields[1:6])
        if not(last<start<end and 0<l<=min(o,c)<=max(o,c)<=h and v>=0):
            raise ValueError("Barra invalida")
        if end-start>3_600_000:raise ValueError("Intervalo inesperado")
        rows.append(dict(time_open_ms=start,open=o,high=h,low=l,close=c,volume=v,time_close_ms=end))
        last=start
    if len(rows)<500:raise ValueError("Datos insuficientes")
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    manifest={"source":base,"archive_sha256":digest,"csv_sha256":hashlib.sha256(output.read_bytes()).hexdigest(),
      "rows":len(rows),"dataset":"BINANCE_SPOT_HISTORICAL","external_preregistration_verified":False,
      "predictions_prospective":False,"promotion_permitted":False,"trading_real":False}
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps(manifest,sort_keys=True))
    return manifest
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--month",default="2025-09")
    p.add_argument("--output",type=Path,default=Path("artifacts/binance-historical.csv"))
    a=p.parse_args();fetch(a.month,a.output)
