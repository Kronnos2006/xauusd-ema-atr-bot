#!/usr/bin/env python3
"""Conciliación conservadora de datos de mercado con última versión remota.
Solo se ejecuta en checkout efímero de Actions, nunca sobre KT-002.
"""
import csv
import io
import json
from pathlib import Path
import sys

FILES = ("spread_btcusdt.csv", "tendencia.json", "btc_1d.json", "btc_4h.json")

def merge_spread(remote: str, local: str) -> str:
    def parse(txt):
        return list(csv.reader(io.StringIO(txt))) if txt.strip() else []
    a, b = parse(remote), parse(local)
    if not a:
        return local
    if not b:
        return remote
    if a[0] != b[0] or not a[0] or a[0][0] != "utc":
        raise ValueError("cabeceras de spread incompatibles")
    rows = {}
    for row in a[1:] + b[1:]:
        if not row:
            continue
        if len(row) != len(a[0]) or not row[0]:
            raise ValueError("fila spread inválida")
        if row[0] in rows and rows[row[0]] != row:
            raise ValueError("conflicto de valores para igual UTC")
        rows[row[0]] = row
    sio = io.StringIO(newline="")
    w = csv.writer(sio, lineterminator="\n")
    w.writerow(a[0])
    w.writerows(rows[k] for k in sorted(rows))
    return sio.getvalue()

def merge_json(name: str, remote: str, local: str, remote_trend: str, local_trend: str) -> str:
    if not local.strip():
        return remote
    if not remote.strip():
        return local
    newer = json.loads(local_trend).get("generado_utc", "") >= json.loads(remote_trend).get("generado_utc", "") if remote_trend.strip() and local_trend.strip() else False
    json.loads(remote)
    json.loads(local)
    return local if newer else remote

def run(root: Path, snapshot: Path):
    remote_trend = (root / "tendencia.json").read_text() if (root / "tendencia.json").exists() else ""
    local_trend = (snapshot / "tendencia.json").read_text() if (snapshot / "tendencia.json").exists() else ""
    for name in FILES:
        target, source = root / name, snapshot / name
        remote = target.read_text() if target.exists() else ""
        local = source.read_text() if source.exists() else ""
        if name.endswith(".csv"):
            result = merge_spread(remote, local)
        else:
            result = merge_json(name, remote, local, remote_trend, local_trend)
        if result:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result)

if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]))
