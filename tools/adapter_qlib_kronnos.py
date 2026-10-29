#!/usr/bin/env python3
"""Kronnos: traductor determinista desde predicciones preregistradas a contrato Qlib.
No importa ni ejecuta Qlib; prohibido declarar inferencia real o promociones.
"""
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

MODELS={"Kronos","TimesFM","KT-001","Siempre sube"}
def timestamp(s):
    if not isinstance(s,str):raise ValueError("timestamp requerido")
    d=datetime.fromisoformat(s.replace("Z","+00:00"))
    if d.tzinfo is None:raise ValueError("timestamp sin zona")
    return d.astimezone(timezone.utc)
def adapt(rows):
    if not isinstance(rows,list):raise ValueError("predictions debe ser lista")
    seen=set();out=[]
    for row in rows:
        if not isinstance(row,dict):raise ValueError("registro invalido")
        if row.get("model") not in MODELS:raise ValueError("modelo no reconocido")
        if not isinstance(row.get("instrument"),str) or not row["instrument"]:raise ValueError("instrument requerido")
        if not isinstance(row.get("prediction_id"),str) or not row["prediction_id"]:raise ValueError("id requerido")
        digest=row.get("artifact_sha256")
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in "0123456789abcdef" for c in digest):raise ValueError("hash invalido")
        created=timestamp(row.get("created_utc"));target=timestamp(row.get("target_utc"))
        if created>=target:raise ValueError("lookahead temporal")
        prediction=row.get("prediction")
        if type(prediction) not in (float,int) or not -1<=prediction<=1:raise ValueError("prediccion fuera de rango [-1,1]")
        key=(row["model"],row["prediction_id"])
        if key in seen:raise ValueError("id duplicado")
        seen.add(key)
        out.append({"datetime":target.isoformat(),"instrument":row["instrument"],"score":float(prediction),
                    "model":row["model"],"prediction_id":row["prediction_id"],"source_sha256":digest})
    return sorted(out,key=lambda x:(x["datetime"],x["instrument"],x["model"],x["prediction_id"]))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",default=Path("artifacts/kronnos-qlib-contract.csv"),type=Path)
    a=p.parse_args()
    raw=json.loads(a.input.read_text(encoding="utf-8"))
    out=adapt(raw["predictions"])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["datetime","instrument","score","model","prediction_id","source_sha256"])
        w.writeheader();w.writerows(out)
    print(json.dumps({"Kronnos":"Qlib-compatible contract only","rows":len(out),"sha256":hashlib.sha256(a.output.read_bytes()).hexdigest(),"qlib_executed":False,"trading_real":False,"promotion_permitted":False}))
if __name__=="__main__":main()
