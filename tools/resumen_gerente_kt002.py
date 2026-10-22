#!/usr/bin/env python3
"""Resumen compacto y SOLO LECTURA para el gerente: no usa API, modelos ni Claude."""
import argparse
import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOUR = timedelta(hours=1)


def utc(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timestamp sin zona horaria")
    return d.astimezone(timezone.utc)


def report(csv_path, summary_path):
    rows = list(csv.DictReader(Path(csv_path).open(encoding="utf-8-sig", newline="")))
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    errors = []
    bases = []
    for i, row in enumerate(rows, 2):
        try:
            base = utc(row["base_open_utc"])
            bases.append(base)
            if utc(row["target_open_utc"]) != base + 4 * HOUR:
                errors.append(f"fila {i}: horizonte distinto de 4 h")
            if utc(row["run_utc"]) < base + HOUR:
                errors.append(f"fila {i}: pronostico antes del cierre")
            if row.get("actual_ret", "").strip():
                if not row.get("scored_utc") or utc(row["scored_utc"]) < base + 5 * HOUR:
                    errors.append(f"fila {i}: puntuacion prematura o sin fecha")
        except (KeyError, ValueError) as exc:
            errors.append(f"fila {i}: {exc}")
    if not bases:
        errors.append("no hay predicciones")
    unique = set(bases)
    if len(unique) != len(bases):
        errors.append("bases duplicadas")
    n_scored = sum(bool(x.get("actual_ret", "").strip()) for x in rows)
    if summary.get("pronosticos") != len(rows) or summary.get("vencidos") != n_scored:
        errors.append("resumen no coincide con CSV (puede ser una publicación intermedia)")
    latest = max(bases) if bases else None
    missing24 = sum(latest - i * HOUR not in unique for i in range(24)) if latest else 24
    nonoverlap = summary.get("sin_solape", {})
    def score(key):
        d = nonoverlap.get(key, {})
        return f'{d.get("aciertos", "?")}/{d.get("n", "?")}'
    flags = " | ".join(errors[:3]) if errors else "sin discrepancias basicas en snapshot"
    text = [
        f"KT-002 snapshot: {len(rows)} pronosticos; {n_scored} puntuados; ultima base {latest.isoformat() if latest else 'ninguna'}",
        f"Ultimas 24 bases: {missing24} huecos; duplicados: {len(bases)-len(unique)}.",
        f"Sin solape: siempre sube {score('siempre_sube')}; Kronos {score('kronos')}; TimesFM {score('timesfm')}; KT-001 {score('kt001')}.",
        f"Control: {flags}. Auditoria independiente pendiente; no prueba ventaja ni rentabilidad.",
        "Pendientes privados: ordenes y escalaciones de la Oficina deben consultarse en Claude.",
    ]
    return {"lines": text, "errors": errors, "missing24": missing24}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="data/kt002/predicciones.csv")
    ap.add_argument("--summary", default="data/kt002/resumen.json")
    args = ap.parse_args()
    result = report(args.csv, args.summary)
    print("\n".join(result["lines"]))
    raise SystemExit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
