#!/usr/bin/env python3
"""Auditoría solo lectura para KT-002. No pronostica, no descarga datos ni escribe en el repositorio."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOUR = timedelta(hours=1)


def parse_utc(value):
    if not value:
        return None
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Marca de tiempo sin zona horaria")
    return stamp.astimezone(timezone.utc)


def inspect(path):
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    errors = []
    bases = []
    scored = 0
    early_scores = 0
    bad_targets = 0
    late_forecasts = 0
    incomplete = 0
    for idx, row in enumerate(rows, 2):
        try:
            base = parse_utc(row["base_open_utc"])
            target = parse_utc(row["target_open_utc"])
            run = parse_utc(row["run_utc"])
            score_time = parse_utc(row.get("scored_utc"))
            if not base or not target or not run:
                raise ValueError("Falta timestamp obligatorio")
            bases.append(base)
            if target != base + 4 * HOUR:
                bad_targets += 1
            # Vela base cerrada al cabo de una hora: pronóstico posterior.
            if run < base + HOUR:
                late_forecasts += 1  # etiqueta histórica: predicción antes de cierre
            has_actual = bool(row.get("actual_ret", "").strip())
            if has_actual:
                scored += 1
                if score_time is None or score_time < target + HOUR:
                    early_scores += 1
            elif score_time is not None:
                incomplete += 1
        except (ValueError, KeyError) as exc:
            errors.append(f"fila {idx}: {exc}")
    count = Counter(bases)
    unique = sorted(count)
    dup = sum(n - 1 for n in count.values() if n > 1)
    missing_all = []
    if unique:
        present = set(unique)
        current = unique[0]
        while current <= unique[-1]:
            if current not in present:
                missing_all.append(current.isoformat())
            current += HOUR
        # Ventana fija de 24 horas terminada en la última base; NO "ahora".
        first = unique[-1] - 23 * HOUR
        missing24 = [t.isoformat() for i in range(24) if (t := first + i * HOUR) not in present]
    else:
        missing24 = []
    return {
        "fuente": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "filas": len(rows),
        "puntuadas": scored,
        "bases_unicas": len(unique),
        "duplicadas": dup,
        "primera_base_utc": unique[0].isoformat() if unique else None,
        "ultima_base_utc": unique[-1].isoformat() if unique else None,
        "horas_omitidas_acumuladas": len(missing_all),
        "horas_omitidas_ultimas_24_bases": len(missing24),
        "horas_omitidas_ultimas_24_bases_utc": missing24,
        "objetivos_con_desfase": bad_targets,
        "pronosticos_antes_de_cierre_base": late_forecasts,
        "puntuaciones_tempranas_o_sin_fecha": early_scores,
        "filas_sin_retorno_real_pero_con_fecha_puntuacion": incomplete,
        "errores_estructura": errors,
        "veredicto_integridad_basica": "REVISAR" if (dup or bad_targets or late_forecasts or early_scores or incomplete or errors) else "SIN_ANOMALIAS_ESTRUCTURALES",
        "limites": "No verifica inferencia real, hora de publicación, logs de Actions, tasas de acierto ni rentabilidad.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="data/kt002/predicciones.csv")
    args = parser.parse_args()
    print(json.dumps(inspect(args.csv), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
