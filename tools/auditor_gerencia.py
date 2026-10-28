#!/usr/bin/env python3
"""Manifiesto reproducible de ficheros y reporte Markdown para GITHUB_STEP_SUMMARY."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path

def audit(paths):
    entries = []
    for name in sorted(set(paths)):
        p = Path(name)
        if not p.is_file():
            raise FileNotFoundError(name)
        b = p.read_bytes()
        entries.append({"path": p.as_posix(), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    return {"generated_utc": datetime.now(timezone.utc).isoformat(), "inputs": entries,
            "llm_calls_for_this_run": 0, "promotion": "BLOQUEADA"}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("files", nargs="+")
    p.add_argument("--output", default="artifacts/auditoria.json")
    args = p.parse_args()
    result = audit(args.files)
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("### Kronnos - Auditoría sin IA\n")
            f.write(f"- Archivos verificados: {len(result['inputs'])}\n")
            f.write("- Promoción: BLOQUEADA\n")
    print(json.dumps(result, ensure_ascii=False))
