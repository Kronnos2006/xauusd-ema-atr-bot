#!/usr/bin/env python3
"""Adaptador de resultados REALES de FreqAI al contrato Kronnos (sin órdenes).
No fabrica pronósticos y no autentica por sí mismo la ejecución de FreqAI.
"""
import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

def parse_utc(value):
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("timestamp UTC Z requerido")
    t=datetime.fromisoformat(value.replace("Z","+00:00"))
    return t.astimezone(timezone.utc)

def convert(csv_bytes, manifest, *, now_utc=None):
    sha=hashlib.sha256(csv_bytes).hexdigest()
    if manifest.get("csv_sha256")!=sha:
        raise ValueError("SHA256 de CSV no coincide con manifiesto")
    if manifest.get("producer")!="FreqAI" or not manifest.get("run_id"):
        raise ValueError("productor y run_id obligatorios")
    created=parse_utc(manifest.get("created_utc"))
    if now_utc is not None and created>now_utc:
        raise ValueError("manifiesto desde el futuro")
    lines=csv_bytes.decode("utf-8-sig").splitlines()
    reader=csv.DictReader(lines)
    expected={"instrument","prediction_id","created_utc","target_utc","prediction"}
    if set(reader.fieldnames or ())!=expected:
        raise ValueError("esquema exacto de CSV requerido")
    rows=[]
    seen=set()
    for row in reader:
        if not row["instrument"] or not row["prediction_id"] or row["prediction_id"] in seen:
            raise ValueError("instrumento o ID inválido/duplicado")
        seen.add(row["prediction_id"])
        t0=parse_utc(row["created_utc"])
        t1=parse_utc(row["target_utc"])
        if not created<=t0<t1:
            raise ValueError("predicción futura, anticipada o con tiempo incongruente")
        if now_utc is not None and t0>now_utc:
            raise ValueError("predicción no observada aún")
        v=float(row["prediction"])
        if not math.isfinite(v) or not -1<=v<=1:
            raise ValueError("score fuera de [-1,1]")
        rows.append({"model":"FreqAI","instrument":row["instrument"],
                     "prediction_id":row["prediction_id"],
                     "created_utc":row["created_utc"],"target_utc":row["target_utc"],
                     "prediction":v,"artifact_sha256":sha})
    if not rows:
        raise ValueError("CSV vacío")
    return {"predictions":rows,"source_verification":"HASH_MATCH_ONLY_NOT_EXECUTION_ATTESTATION",
            "producer_run_id":manifest["run_id"],"trading_real":False,
            "promotion_permitted":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    data=convert(args.csv.read_bytes(),json.loads(args.manifest.read_text()),
                 now_utc=datetime.now(timezone.utc))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"predictions":len(data["predictions"]),"promotion_permitted":False}))
if __name__=="__main__":
    main()
