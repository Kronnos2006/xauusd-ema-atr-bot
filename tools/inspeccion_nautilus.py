#!/usr/bin/env python3
"""Inspeccion de paquete instalado, sin iniciar un motor ni brokers."""
import importlib
import json
from pathlib import Path
from importlib import metadata
import sys
def main():
    importlib.import_module("nautilus_trader")
    version=metadata.version("nautilus_trader")
    result={"engine":"NAUTILUS","version":version,"installed":True,
            "stable_1x":version.startswith("1."),"backtest_executed":False,
            "broker_connections":0,"trading_real":"NO_AUTORIZADO"}
    output=Path("artifacts/nautilus-inspeccion.json")
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
    print(json.dumps(result))
    return 0 if result["stable_1x"] else 2
if __name__=="__main__":
    sys.exit(main())
