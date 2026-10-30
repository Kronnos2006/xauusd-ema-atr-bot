#!/usr/bin/env python3
"""Kronnos daily reporting: stdlib only, read-only, no LLM or orders."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

def git(root,*args):
    try:
        return subprocess.check_output(["git","-C",str(root),*args],text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):
        return "NO_DISPONIBLE"

def inspect_market(path):
    if not path.is_file():
        return {"valid":False,"reason":"NO_DISPONIBLE"}
    from validador_datos import validate
    result=validate(path)
    result["sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result

def file_state(root, path):
    file = root / path
    return {"path": path, "present": file.is_file(),
            "sha256": hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else None}

def inspect_modules(root):
    from diagnostico_modelos_kronnos import inspect
    models = inspect(root, {})
    return {
        "kronnos": {"kt002_operativo": "NO_VERIFICADO",
                    "modelos": models["models"],
                    "proximos": ["Verificar ultima corrida KT-002", "Comprobar inferencias reales Kronos y TimesFM"]},
        "orion": {"estado": "PARCIAL",
                  "reporte_script": file_state(root, "tools/informe_gerencia_sin_ia.py"),
                  "lineage": file_state(root, "tools/lineage_kronnos.py"),
                  "auditor": file_state(root, "tools/auditor_gerencia.py"),
                  "servicio_operativo": "NO_VERIFICADO"},
        "atlas": {"estado": "BLOQUEADO",
                  "p0_guard": file_state(root, "tools/atlas_p0_guard.py"),
                  "rfc3161_verifier": file_state(root, "tools/atlas_verificador_evidencias.py"),
                  "confirmatorio": file_state(root, "atlas/evidencia_confirmatoria.py"),
                  "pr42": "PENDIENTE_REVISION_REMOTA",
                  "custodia_independiente": "NO_VERIFICADO",
                  "promocion_permitida": False},
    }

def generate(root):
    market=inspect_market(root/"data/mercado/spread_btcusdt.csv")
    return {"proyecto":"Kronnos","generated_utc":datetime.now(timezone.utc).isoformat(),
            "head_sha":git(root,"rev-parse","HEAD"),
            "market_data":market,
            "kronnos_kt002":"NO_VERIFICADO",
            "h3_h4":"NO_VERIFICADO",
            "atlas":"NO_VERIFICADO",
            "trading_real":"NO_AUTORIZADO",
            "llm_calls_by_this_script":0,
            "modulos": inspect_modules(root)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="artifacts/informe-gerencia.json")
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    result=generate(root)
    dest=root/args.output
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("### Kronnos — Informe determinista\n")
            f.write("- Commit: `"+str(result["head_sha"])+"`\n")
            f.write("- Mercado válido: "+str(result["market_data"].get("valid",result["market_data"].get("valido",False)))+"\n")
            f.write("- KT-002, H3/H4 y ATLAS: NO_VERIFICADO\n")
            f.write("- Trading: NO_AUTORIZADO\n")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["market_data"].get("valido") else 2

if __name__=="__main__":
    raise SystemExit(main())
