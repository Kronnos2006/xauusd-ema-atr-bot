#!/usr/bin/env python3
"""Evaluación descriptiva prospectiva de predicciones cerradas; NO calcula DSR ni promueve."""
import argparse
import json
from pathlib import Path

def evaluate(records):
    seen, errors, valid, hits = set(), [], 0, 0
    for i, r in enumerate(records):
        try:
            key = (r["model"], r["event_id"])
            if key in seen:
                raise ValueError("duplicado")
            seen.add(key)
            pred, actual = r["predicted"], r["actual"]
            if type(pred) is not int or type(actual) is not int or pred not in (0, 1) or actual not in (0, 1):
                raise ValueError("etiquetas binarias 0/1 obligatorias")
            if not r.get("preregistered", False) or not r.get("matured", False):
                raise ValueError("pre-registro o resultado maduro sin verificar")
            # Banderas informativas NO sustituyen comprobación Git y timestamp externo.
            valid += 1
            hits += (pred == actual)
        except (KeyError, ValueError, TypeError) as exc:
            errors.append({"indice": i, "motivo": str(exc)})
    return {"validas_descriptivas": valid, "aciertos": hits, "precision": hits / valid if valid else None,
            "excluidas": errors, "promocion": "BLOQUEADA",
            "advertencia": "Pre-registro y madurez deben verificarse externamente en Git. No DSR, no significancia."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("json", help="Arreglo de predicciones con model,event_id,predicted,actual,preregistered,matured")
    a = p.parse_args()
    data = json.loads(Path(a.json).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("Se requiere una lista JSON")
    print(json.dumps(evaluate(data), ensure_ascii=False, indent=2))
