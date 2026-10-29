#!/usr/bin/env python3
"""Kronnos piloto de contrato de pronósticos, NO ejecuta modelos ni opera trading.
Diseño original: enseña la integración sin copiar código de Lumina.
"""
import argparse
import hashlib
import json
from pathlib import Path

ALLOWED=("Kronos","TimesFM","KT-001","Siempre sube")
def inspect(payload):
    if not isinstance(payload,dict) or not isinstance(payload.get("predictions"),list):
        raise ValueError("predictions debe ser lista")
    rows=payload["predictions"]
    seen=set()
    checked=[]
    for row in rows:
        if not isinstance(row,dict):raise ValueError("Fila no es objeto")
        model=row.get("model")
        if model not in ALLOWED:raise ValueError("Motor no aprobado")
        required=("model","prediction_id","target_utc","created_utc","artifact_sha256")
        if any(not isinstance(row.get(k),str) or not row[k] for k in required):
            raise ValueError("Campos obligatorios faltantes")
        sha=row["artifact_sha256"]
        if len(sha)!=64 or any(c not in "0123456789abcdef" for c in sha):
            raise ValueError("Hash inválido")
        key=(model,row["prediction_id"])
        if key in seen:raise ValueError("Predicción duplicada")
        seen.add(key)
        from datetime import datetime,timezone
        def dt(x):
            result=datetime.fromisoformat(x.replace("Z","+00:00"))
            if result.tzinfo is None:raise ValueError("UTC sin zona")
            return result.astimezone(timezone.utc)
        if not dt(row["created_utc"])<dt(row["target_utc"]):
            raise ValueError("Predicción posterior al objetivo")
        checked.append({"model":model,"prediction_id":row["prediction_id"],"contract":"PARSEADO_NO_AUTENTICADO"})
    return {"project":"Kronnos","rows":checked,"count":len(checked),
            "execution_verified":False,"external_preregistration_verified":False,
            "predictive_edge_demonstrated":False,"promotion_permitted":False,
            "llm_calls":0,"trading_real":"NO_AUTORIZADO"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("artifacts/piloto-ensemble-kronnos.json"))
    a=p.parse_args()
    result=inspect(json.loads(a.input.read_text(encoding="utf-8")))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+"\n"
    a.out.write_text(data,encoding="utf-8")
    print("Kronnos pilotos | contratos parseados:",result["count"],"| SHA256:",hashlib.sha256(data.encode()).hexdigest())
if __name__=="__main__":main()
