#!/usr/bin/env python3
"""Kronnos: valida procedencia, esquema y coincidencia sin inventar ejecución de motores."""
import argparse
import hashlib
import json
from pathlib import Path
from comparador_motores import compare

def load_record(path):
    data=Path(path).read_bytes()
    x=json.loads(data)
    if not isinstance(x,dict): raise ValueError("JSON debe ser objeto")
    if x.get("engine") not in {"LEAN","NAUTILUS"}: raise ValueError("Motor inválido")
    if not x.get("engine_version") or not x.get("run_id"):
        raise ValueError("Versión y run_id obligatorios")
    if x.get("mode")!="backtest" or x.get("synthetic") is not False:
        raise ValueError("Se requiere backtest real sobre muestra congelada, no fixture")
    if x.get("source_artifact_sha256") is None:
        raise ValueError("Falta huella de artefacto original")
    return x,hashlib.sha256(data).hexdigest()

def preflight(a,b):
    left,lhash=load_record(a);right,rhash=load_record(b)
    if left["engine"]==right["engine"]:raise ValueError("Resultados de motores distintos obligatorios")
    report=compare(left,right)
    report["inputs"]=[{"engine":left["engine"],"file_sha256":lhash,"version":left["engine_version"]},
                      {"engine":right["engine"],"file_sha256":rhash,"version":right["engine_version"]}]
    report["promotion"]="BLOQUEADA"
    report["validated_external_execution"]=False
    report["warning"]="Los metadatos proporcionados no prueban por sí mismos que el motor realmente se ejecutó. Auditar logs y artefactos originales."
    return report

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--lean",required=True)
    p.add_argument("--nautilus",required=True)
    p.add_argument("--output",default="artifacts/contraste-motores.json")
    a=p.parse_args()
    report=preflight(a.lean,a.nautilus)
    f=Path(a.output);f.parent.mkdir(parents=True,exist_ok=True)
    f.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))
    raise SystemExit(0 if report["agreement"] else 2)
