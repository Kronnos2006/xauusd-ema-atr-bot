#!/usr/bin/env python3
"""Kronnos: ensemble experimental con pesos iguales predefinidos, sin trading."""
import argparse,hashlib,json,math
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
MODELS=("Kronos","TimesFM","KT-001","Siempre sube","FreqAI")
def utc(value):
    d=datetime.fromisoformat(value.replace("Z","+00:00"))
    if d.tzinfo is None:raise ValueError("UTC requerido")
    return d.astimezone(timezone.utc)
def combine(payload,min_models=2):
    if not isinstance(payload,dict) or not isinstance(payload.get("predictions"),list):
        raise ValueError("predictions es lista requerida")
    if type(min_models)!=int or min_models<2 or min_models>len(MODELS):raise ValueError("min_models fuera de rango")
    groups=defaultdict(dict);seen=set()
    for row in payload["predictions"]:
        if not isinstance(row,dict) or row.get("model") not in MODELS:raise ValueError("modelo no permitido")
        for key in ("instrument","prediction_id","target_utc","created_utc","artifact_sha256"):
            if not isinstance(row.get(key),str) or not row[key]:raise ValueError("campo requerido "+key)
        sha=row["artifact_sha256"]
        if len(sha)!=64 or any(x not in "0123456789abcdef" for x in sha):raise ValueError("SHA inválido")
        score=row.get("prediction")
        if type(score) not in (int,float) or not math.isfinite(score) or score < -1 or score > 1:
            raise ValueError("prediction debe ser puntuación finita [-1,1]")
        created,target=utc(row["created_utc"]),utc(row["target_utc"])
        if created>=target:raise ValueError("Predicción posterior al objetivo")
        instrument=row["instrument"]
        key=(row["model"],row["prediction_id"])
        if key in seen:raise ValueError("ID duplicado")
        seen.add(key)
        group=(instrument,target.isoformat())
        if row["model"] in groups[group]:raise ValueError("Dos predicciones del mismo modelo al mismo objetivo")
        groups[group][row["model"]]={"score":float(score),"id":row["prediction_id"],"sha256":sha,"created_utc":created.isoformat()}
    results=[]
    for (instrument,target),models in sorted(groups.items()):
        if len(models)<min_models:continue
        score=sum(x["score"] for x in models.values())/len(models)
        results.append({"instrument":instrument,"target_utc":target,"score":score,"direction":"UP" if score>0 else "DOWN" if score<0 else "NEUTRAL",
        "n_models":len(models),"models":{k:models[k] for k in MODELS if k in models},
        "weighting":"EQUAL_FIXED","status":"EXPLORATORY_NOT_PREREGISTERED"})
    return {"project":"Kronnos","ensemble":results,"n_groups":len(results),
    "weights_optimized":False,"models_executed_here":False,
    "source_hashes_authenticated":False,"predictive_edge_demonstrated":False,
    "promotion_permitted":False,"trading_real":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True)
    p.add_argument("--out",type=Path,default=Path("artifacts/ensemble-kronnos.json"))
    p.add_argument("--min-models",type=int,default=2);a=p.parse_args()
    result=combine(json.loads(a.input.read_text(encoding="utf-8")),a.min_models)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    a.out.write_text(data,encoding="utf-8")
    print(json.dumps({"groups":result["n_groups"],"sha256":hashlib.sha256(data.encode()).hexdigest(),
        "trading_real":False,"promotion_permitted":False}))
if __name__=="__main__":main()
