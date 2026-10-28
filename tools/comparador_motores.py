#!/usr/bin/env python3
"""Comparación read-only entre motores; exige misma corrida y supuestos."""
import argparse
import json
import math
from pathlib import Path

KEYS = ("dataset_sha256", "config_sha256", "sample_id", "fees_model")
METRICS = ("net_return", "max_drawdown", "trades")

def compare(a, b, tolerance=1e-9):
    reasons = []
    for key in KEYS:
        if not a.get(key) or a.get(key) != b.get(key):
            reasons.append("INPUT_MISMATCH:" + key)
    metrics = {}
    for key in METRICS:
        left, right = a.get(key), b.get(key)
        if type(left) not in (int, float) or type(right) not in (int, float):
            reasons.append("MISSING_METRIC:" + key)
            continue
        if not math.isfinite(left) or not math.isfinite(right):
            reasons.append("NON_FINITE:" + key)
            continue
        diff = abs(left - right)
        metrics[key] = {"left": left, "right": right, "absolute_difference": diff}
        if diff > tolerance:
            reasons.append("METRIC_DIVERGENCE:" + key)
    return {"comparable": not any(x.startswith("INPUT_MISMATCH") for x in reasons),
            "agreement": len(reasons) == 0, "reasons": reasons,
            "metrics": metrics, "promocion": "BLOQUEADA",
            "note": "Solo cotejo entre resultados proporcionados. No ejecuta LEAN/NautilusTrader, ni valida métodos de mercado."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("engine_a")
    p.add_argument("engine_b")
    p.add_argument("--tolerance", type=float, default=1e-9)
    args = p.parse_args()
    if not math.isfinite(args.tolerance) or args.tolerance < 0:
        p.error("Tolerancia inválida")
    a = json.loads(Path(args.engine_a).read_text(encoding="utf-8"))
    b = json.loads(Path(args.engine_b).read_text(encoding="utf-8"))
    print(json.dumps(compare(a, b, args.tolerance), ensure_ascii=False, indent=2))
