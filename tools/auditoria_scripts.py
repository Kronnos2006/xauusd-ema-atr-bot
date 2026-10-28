#!/usr/bin/env python3
"""Auditoría estática conservadora de los scripts scripts-first de Kronnos."""
import ast
import hashlib
import json
from pathlib import Path
import sys

NAMES=("recolector_mercado","validador_datos","evaluador_modelos","auditor_gerencia",
       "lineage_kronnos","comparador_motores","informe_gerencia_sin_ia")
FORBIDDEN_IMPORTS={"openai","anthropic","google.generativeai","ccxt","requests",
                   "subprocess32","MetaTrader5"}
FORBIDDEN_CALLS={"eval","exec","compile"}
def inspect(root):
    findings=[]
    hashes={}
    for name in NAMES:
        path=Path(root)/"tools"/(name+".py")
        if not path.exists():
            findings.append({"file":name,"problem":"FILE_MISSING"})
            continue
        data=path.read_bytes()
        hashes[path.name]=hashlib.sha256(data).hexdigest()
        try:
            tree=ast.parse(data,filename=str(path))
        except SyntaxError as e:
            findings.append({"file":name,"problem":"SYNTAX_ERROR","line":e.lineno})
            continue
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for x in node.names:
                    if x.name in FORBIDDEN_IMPORTS or x.name.split(".")[0] in ("openai","anthropic","ccxt"):
                        findings.append({"file":name,"problem":"FORBIDDEN_IMPORT","line":node.lineno})
            if isinstance(node,ast.ImportFrom):
                if node.module and (node.module in FORBIDDEN_IMPORTS or node.module.split(".")[0] in ("openai","anthropic","ccxt")):
                    findings.append({"file":name,"problem":"FORBIDDEN_IMPORT","line":node.lineno})
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in FORBIDDEN_CALLS:
                findings.append({"file":name,"problem":"DYNAMIC_EXECUTION","line":node.lineno})
    return {"status":"PASS" if not findings else "FAIL","issues":findings,"sha256":hashes,
            "scope":"Análisis AST básico; NO demuestra ausencia de riesgos dinámicos, operaciones externas o fallos de seguridad."}

if __name__=="__main__":
    root=Path(__file__).resolve().parents[1]
    report=inspect(root)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    sys.exit(0 if report["status"]=="PASS" else 2)
