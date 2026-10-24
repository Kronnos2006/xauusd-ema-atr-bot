"""Evaluación prospectiva de decisiones ATLAS, independiente de KT-002 y sin órdenes.

Input JSONL: cada línea contiene id, publicada_utc, vence_utc, direccion_modelo
(+1/-1), decision_atlas (ABSTENERSE/CONTINUAR_INVESTIGANDO), retorno_real,
puntuada_utc y opcionalmente costo_ida_vuelta. La integridad de publicación debe
validarse por fuera con SHA/commit remoto previo al vencimiento.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime


def _t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def evaluar(filas: list[dict]) -> dict:
    vistos = set()
    validas = []
    descartadas = []
    for f in filas:
        key = f.get("id")
        if not key or key in vistos:
            descartadas.append({"id": key, "motivo": "id faltante o duplicado"})
            continue
        vistos.add(key)
        try:
            if not (f.get("sello_externo_verificado") is True
                    and _t(f["publicada_utc"]) < _t(f["vence_utc"])
                    and _t(f["puntuada_utc"]) >= _t(f["vence_utc"])):
                raise ValueError("falta sello externo o ventana temporal inválida")
            direccion = int(f["direccion_modelo"])
            if direccion not in (-1, 1):
                raise ValueError("dirección inválida")
            decision = f["decision_atlas"]
            if decision not in ("ABSTENERSE", "CONTINUAR_INVESTIGANDO"):
                raise ValueError("decisión inválida")
            retorno = float(f["retorno_real"])
            costo = float(f.get("costo_ida_vuelta", 0.003))
            if costo < 0:
                raise ValueError("costo negativo")
            acierto = direccion * retorno > 0
            validas.append({"id": key, "decision": decision, "acierto": acierto,
                           "retorno_modelo_neto": direccion * retorno - costo})
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            descartadas.append({"id": key, "motivo": str(exc)})
    ab = [x for x in validas if x["decision"] == "ABSTENERSE"]
    co = [x for x in validas if x["decision"] == "CONTINUAR_INVESTIGANDO"]
    return {
        "total_proporcionado": len(filas), "validas": len(validas),
        "rechazadas_por_integridad": descartadas,
        "abstenciones": len(ab), "continuar_investigando": len(co),
        "errores_modelo_evitados": sum(not x["acierto"] for x in ab),
        "aciertos_modelo_descartados": sum(x["acierto"] for x in ab),
        "aciertos_modelo_continuados": sum(x["acierto"] for x in co),
        "errores_modelo_continuados": sum(not x["acierto"] for x in co),
        "retorno_modelo_neto_promedio": (sum(x["retorno_modelo_neto"] for x in validas) / len(validas)
                                        if validas else None),
        "retorno_condicional_continuados": (sum(x["retorno_modelo_neto"] for x in co) / len(co)
                                            if co else None),
        "nota": "CONTINUAR_INVESTIGANDO no equivale a operar. Métricas descriptivas; no demuestran edge ni rentabilidad."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--jsonl", required=True)
    a = p.parse_args()
    filas = [json.loads(s) for s in Path(a.jsonl).read_text(encoding="utf-8").splitlines() if s.strip()]
    print(json.dumps(evaluar(filas), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
