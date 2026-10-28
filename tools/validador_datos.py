#!/usr/bin/env python3
"""Validación conservadora de CSV BTC spread; falla cerrado."""
import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path

REQUIRED = ("utc", "bid", "ask", "spread_pct")

def validate(path):
    errors, count, previous = [], 0, None
    with Path(path).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not all(k in reader.fieldnames for k in REQUIRED):
            return {"valido": False, "filas": 0, "errores": ["COLUMNAS_INVALIDAS"]}
        for row in reader:
            count += 1
            try:
                ts = datetime.fromisoformat(row["utc"].replace("Z", "+00:00"))
                if ts.tzinfo is None:
                    raise ValueError("UTC sin zona")
                ts = ts.astimezone(timezone.utc)
                bid, ask = float(row["bid"]), float(row["ask"])
                spread = float(row["spread_pct"])
                if not all(map(math.isfinite, (bid, ask, spread))) or bid <= 0 or ask < bid or spread < 0:
                    raise ValueError("precios/spread inválidos")
                if previous is not None and ts <= previous:
                    raise ValueError("timestamp duplicado o desordenado")
                previous = ts
            except (ValueError, TypeError, KeyError, OverflowError) as ex:
                if len(errors) < 25:
                    errors.append({"fila": count + 1, "error": str(ex)})
    if not count:
        errors.append("SIN_FILAS")
    return {"valido": not errors, "filas": count, "errores": errors, "ultimo_utc": previous.isoformat() if previous else None}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    a = p.parse_args()
    result = validate(a.csv)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result["valido"] else 2)
