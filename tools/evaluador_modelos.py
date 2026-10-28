#!/usr/bin/env python3
"""Kronnos: descriptiva con preregistro comprobado en Git, sin promoción."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.DEVNULL).strip()

def utc(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("timestamp sin zona")
    return d.astimezone(timezone.utc)

def verify_precommit(repo, record):
    sha, path = record["prereg_sha"], record["prereg_path"]
    if not isinstance(sha, str) or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("SHA preregistro inválido")
    if not isinstance(path, str) or not path.startswith("preregistros/") or ".." in Path(path).parts or "\\" in path:
        raise ValueError("ruta preregistro inválida")
    if git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}") != sha:
        raise ValueError("commit no comprobado")
    git(repo, "merge-base", "--is-ancestor", sha, "HEAD")
    prereg = json.loads(git(repo, "show", f"{sha}:{path}"))
    if prereg["event_id"] != record["event_id"] or prereg["model"] != record["model"]:
        raise ValueError("pre-registro de otra hipótesis")
    # %cI puede diferir de la hora de publicación de Github y no constituye sello externo.
    commit_time = utc(git(repo, "show", "-s", "--format=%cI", sha))
    published = utc(record["published_utc"])
    if not commit_time < published:
        raise ValueError("commit no anterior a publicación")
    return True

def evaluate(records, repo):
    valid, hits, excluded, seen = 0, 0, [], set()
    for i, rec in enumerate(records):
        try:
            key = (rec["model"], rec["event_id"])
            if key in seen:
                raise ValueError("duplicado")
            seen.add(key)
            pred, actual = rec["predicted"], rec["actual"]
            if type(pred) is not int or type(actual) is not int or pred not in (0, 1) or actual not in (0, 1):
                raise ValueError("etiquetas inválidas")
            if rec.get("matured") is not True:
                raise ValueError("madurez no verificada externamente")
            verify_precommit(repo, rec)
            valid += 1
            hits += pred == actual
        except (KeyError, ValueError, TypeError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            excluded.append({"indice": i, "razon": str(exc)})
    return {"validas_descriptivas": valid, "aciertos": hits, "precision": hits / valid if valid else None,
            "excluidas": excluded, "promocion": "BLOQUEADA",
            "limite": "La fecha de commit Git no es sello RFC3161; madurez y fuente de resultado requieren verificación externa; DSR ausente."}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("json")
    p.add_argument("--repo", default=".")
    args = p.parse_args()
    rows = json.loads(Path(args.json).read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        p.error("Se requiere una lista JSON")
    print(json.dumps(evaluate(rows, args.repo), ensure_ascii=False, indent=2))
