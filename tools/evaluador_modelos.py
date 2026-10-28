#!/usr/bin/env python3
"""Kronnos: evaluación descriptiva, nunca validación de preregistro ni promoción."""
import argparse
import json
from pathlib import Path

def evaluate(records, repo="."):
    # El commit SHA y la fecha de committer pueden falsificarse. No usarlos
    # como prueba de pre-registro. Se requiere sello externo independiente.
    excluded = []
    for i, record in enumerate(records):
        excluded.append({"indice": i, "razon": "PRE_REGISTRO_EXTERNO_NO_VERIFICADO"})
    return {"validas_descriptivas": 0, "aciertos": 0, "precision": None,
            "excluidas": excluded, "promocion": "BLOQUEADA",
            "limite": "El historial Git no constituye prueba temporal independiente. Verificar sello RFC3161, evento y madurez por una fuente independiente antes de contar cualquier operación."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("json")
    p.add_argument("--repo", default=".")
    a = p.parse_args()
    records = json.loads(Path(a.json).read_text(encoding="utf-8"))
    if not isinstance(records, list):
        p.error("Se requiere una lista JSON")
    print(json.dumps(evaluate(records, a.repo), indent=2, ensure_ascii=False))
