#!/usr/bin/env python3
"""Kronnos: diagnóstico offline y reproducible de evidencia de modelos.

No interpreta ausencia como motor parado. No descarga, no importa modelos,
no usa LLM, no activa órdenes, no afirma últimas métricas.
"""
import argparse
import hashlib
import json
from pathlib import Path

MODELS=("Kronos","TimesFM","KT-001","Siempre sube")
def inspect(root,manifest):
    out={"project":"Kronnos","status":"DIAGNOSTICO_NO_CERTIFICACION",
         "trading_real":"NO_AUTORIZADO","llm_calls":0,"models":{}}
    for name in MODELS:
        record=manifest.get(name,{})
        if not isinstance(record,dict):record={}
        path=record.get("evidence_path")
        expected=record.get("sha256")
        state={"status":"NO_VERIFICADO","evidence_path":path if isinstance(path,str) else None}
        if isinstance(path,str) and path and isinstance(expected,str):
            dest=(root/path).resolve()
            try:
                dest.relative_to(root.resolve())
                if dest.is_file():
                    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
                    state["sha256"]=digest
                    state["status"]="EVIDENCIA_LOCAL_COINCIDE" if digest==expected else "HASH_INCORRECTO"
                else:state["status"]="ARCHIVO_AUSENTE"
            except (ValueError,OSError):
                state["status"]="RUTA_INVALIDA"
        out["models"][name]=state
    out["kt002_operativo"]="NO_VERIFICADO"
    out["predicciones_actuales"]="NO_VERIFICADO"
    out["promocion_permitida"]=False
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path)
    p.add_argument("--root",type=Path,default=Path("."))
    p.add_argument("--out",type=Path,default=Path("artifacts/modelos-diagnostico.json"))
    a=p.parse_args()
    manifest=json.loads(a.manifest.read_text()) if a.manifest else {}
    if not isinstance(manifest,dict):raise ValueError("Manifest invalido")
    report=inspect(a.root,manifest)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
