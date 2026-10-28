#!/usr/bin/env python3
"""Comparador conservador: sin motores externos ni trading."""
import argparse
import json
import math
from pathlib import Path

KEYS=("dataset_sha256","config_sha256","sample_id","fees_model")
METRICS=("net_return","max_drawdown","trades")
def compare(a,b,tolerance=1e-9):
    if type(tolerance) not in (int,float) or not math.isfinite(tolerance) or tolerance<0:
        raise ValueError("Tolerancia inválida")
    reasons=[]
    for key in KEYS:
        if not isinstance(a.get(key),str) or not a.get(key) or a.get(key)!=b.get(key):
            reasons.append("INPUT_MISMATCH:"+key)
    metrics={}
    for key in METRICS:
        l,r=a.get(key),b.get(key)
        if type(l) not in (int,float) or type(r) not in (int,float):
            reasons.append("MISSING_METRIC:"+key)
            continue
        if not math.isfinite(l) or not math.isfinite(r):
            reasons.append("NON_FINITE:"+key)
            continue
        delta=abs(l-r)
        metrics[key]={"left":l,"right":r,"absolute_difference":delta}
        if delta>tolerance or (key=="trades" and delta != 0):
            reasons.append("METRIC_DIVERGENCE:"+key)
    return {"comparable":not any(x.startswith("INPUT_MISMATCH") for x in reasons),
            "agreement":not reasons,"reasons":reasons,"metrics":metrics,
            "promocion":"BLOQUEADA","note":"Solo cotejo; no validación financiera ni ejecución externa."}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("engine_a");p.add_argument("engine_b");p.add_argument("--tolerance",type=float,default=1e-9)
    a=p.parse_args()
    print(json.dumps(compare(json.loads(Path(a.engine_a).read_text()),json.loads(Path(a.engine_b).read_text()),a.tolerance),indent=2))
