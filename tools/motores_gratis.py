#!/usr/bin/env python3
"""Kronnos: control de motores open-source sin servicios comerciales.
Por defecto solo verifica requisitos. No envía órdenes ni genera backtests falsos.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess

def inspect_engine(engine, path=None):
    if engine == "lean":
        dotnet = shutil.which("dotnet")
        root = Path(path).resolve() if path else None
        solution = root / "QuantConnect.Lean.sln" if root else None
        return {"engine":"LEAN","method":"source_build_no_paid_cli",
                "dotnet_available": bool(dotnet),
                "solution_present":bool(solution and solution.is_file()),
                "ready_to_build": bool(dotnet and solution and solution.is_file()),
                "live_trading":"DISABLED","paid_cli":"NOT_USED"}
    if engine == "nautilus":
        # Import comprobado por otro proceso para no cargar extensiones en el auditor.
        try:
            p=subprocess.run(["python3","-c","import nautilus_trader; print(nautilus_trader.__version__)"],
                             check=False,capture_output=True,text=True,timeout=15)
            version=p.stdout.strip() if p.returncode==0 else None
        except (OSError,subprocess.TimeoutExpired):
            version=None
        return {"engine":"NAUTILUS","method":"local_python_wheel",
                "installed":version is not None,"version":version,
                "stable_1x":bool(version and version.startswith("1.")),
                "live_trading":"DISABLED","paid_service":"NOT_REQUIRED"}
    raise ValueError("Motor no soportado")

def main():
    p=argparse.ArgumentParser(description="Diagnóstico gratuito y de solo lectura")
    p.add_argument("--engine",choices=["lean","nautilus"],required=True)
    p.add_argument("--source-dir",help="Solo para LEAN: código fuente existente")
    a=p.parse_args()
    result=inspect_engine(a.engine,a.source_dir)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
