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

def inspect_kt002(root, now=None, max_age_h=3.0):
    """Lee data/kt002 y recalcula: sin evidencia => NO_VERIFICADO; nunca inventa metricas."""
    now = now or datetime.now(timezone.utc)
    pred, res = root / "data/kt002/predicciones.csv", root / "data/kt002/resumen.json"
    if not pred.is_file() or not res.is_file():
        return {"estado": "NO_VERIFICADO", "motivo": "faltan predicciones.csv o resumen.json"}
    rows = list(csv.DictReader(pred.open(encoding="utf-8")))
    summ = json.loads(res.read_text(encoding="utf-8"))
    if not rows:
        return {"estado": "NO_VERIFICADO", "motivo": "predicciones.csv vacio"}
    last = datetime.fromisoformat(rows[-1]["run_utc"].replace("Z", "+00:00"))
    edad = round((now - last).total_seconds() / 3600, 2)
    vencidas = [r for r in rows if r.get("actual_ret")]
    sin = [r for r in vencidas if datetime.fromisoformat(r["base_open_utc"]).hour % 4 == 0]
    def tasa(m):
        h = [int(r[m + "_hit"]) for r in sin if r.get(m + "_hit") in ("0", "1")]
        return {"aciertos": sum(h), "n": len(h)}
    up = [int(float(r["actual_ret"]) > 0) for r in sin if float(r["actual_ret"]) != 0]
    metricas = {m: tasa(m) for m in ("kronos", "timesfm", "kt001")}
    metricas["siempre_sube"] = {"aciertos": sum(up), "n": len(up)}
    s = summ.get("sin_solape", {})
    coincide = (summ.get("pronosticos") == len(rows) and summ.get("vencidos") == len(vencidas)
                and all(s.get(m, {}).get("aciertos") == metricas[m]["aciertos"] for m in metricas))
    estado = "INCONSISTENTE" if not coincide else ("ATRASADO" if edad > max_age_h else "VERIFICADO")
    return {"estado": estado, "ultimo_registro_utc": last.isoformat(), "horas_desde_ultimo": edad,
            "pronosticos": len(rows), "vencidos": len(vencidas), "sin_solape": metricas,
            "resumen_coincide_con_csv": coincide, "horas_omitidas": summ.get("horas_omitidas")}

def inspect_modules(root):
    from diagnostico_modelos_kronnos import inspect
    models = inspect(root, {})
    kt002 = inspect_kt002(root)
    return {
        "kronnos": {"kt002_operativo": kt002["estado"], "kt002": kt002,
                    "modelos": models["models"]},
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
            "kronnos_kt002":inspect_kt002(root)["estado"],
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
            f.write("- KT-002: "+str(result["kronnos_kt002"])+"\n")
            f.write("- H3/H4 y ATLAS: NO_VERIFICADO\n")
            f.write("- Trading: NO_AUTORIZADO\n")
    print(json.dumps(result,ensure_ascii=False))
    return 0 if result["market_data"].get("valido") else 2

if __name__=="__main__":
    raise SystemExit(main())
