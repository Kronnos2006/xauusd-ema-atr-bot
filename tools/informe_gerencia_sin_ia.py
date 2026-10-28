#!/usr/bin/env python3
"""KRONNOS: informe determinista con solo Python stdlib. No usa IA ni redes."""
import argparse
import csv
import datetime as dt
import json
import pathlib
import subprocess


def git(*args):
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "NO_DISPONIBLE"


def latest_market_timestamp(path):
    if not path.is_file():
        return "NO_DISPONIBLE"
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = csv.DictReader(handle)
            last = None
            for row in rows:
                last = row
        return (last or {}).get("utc") or "NO_DISPONIBLE"
    except (OSError, UnicodeError, csv.Error):
        return "NO_DISPONIBLE"


def main():
    parser = argparse.ArgumentParser(description="Informe de gerencia sin IA")
    parser.add_argument("--output", default="artifacts/informe-gerencia.json")
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    root = pathlib.Path(__file__).resolve().parents[1]
    data = {
        "proyecto": "Kronnos",
        "generado_utc": now,
        "fuente": "repositorio_local",
        "head_sha": git("-C", str(root), "rev-parse", "HEAD"),
        "head_fecha_utc": git("-C", str(root), "log", "-1", "--format=%cI"),
        "ultimo_spread_utc": latest_market_timestamp(root / "data/mercado/spread_btcusdt.csv"),
        "llamadas_llm": 0,
        "resultados_kt002": "NO_VERIFICADO",
        "estado_h3_h4": "NO_VERIFICADO",
        "barreras_atlas": "NO_VERIFICADO",
        "operacion_real": "NO_AUTORIZADA",
    }
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
