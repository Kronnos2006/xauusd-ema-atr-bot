#!/usr/bin/env python3
"""Piloto A: inspección estática reproducible de dos proyectos externos.

Nunca importa/ejecuta código de terceros; no lee KT-002/003. GitHub público solamente.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).resolve().parent / "upstreams.json"
REQUIRED = {
    "OpenHands/OpenHands": ("agent canvas", "claude code", "codex"),
    "TauricResearch/TradingAgents": ("tradingagents", "risk", "analyst"),
}

def inspect(repo, sha, readme_text):
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("Git SHA invalido")
    if not isinstance(readme_text, str) or len(readme_text) < 120:
        raise ValueError("README vacio/invalido")
    terms = REQUIRED[repo]
    evidence = {term: term in readme_text.lower() for term in terms}
    return {
        "repo": repo, "pinned_sha": sha,
        "readme_sha256": hashlib.sha256(readme_text.encode("utf-8")).hexdigest(),
        "checks": evidence, "static_claims_found": all(evidence.values()),
        "external_code_executed": False,
        "models_called": False,
        "orders_sent": False,
        "experiments_modified": False,
    }

def fetch_readme(repo, sha):
    url = f"https://raw.githubusercontent.com/{repo}/{sha}/README.md"
    req = Request(url, headers={"User-Agent": "orion-safe-pilot/1.0"})
    with urlopen(req, timeout=25) as resp:
        size = resp.headers.get("Content-Length")
        if size and int(size) > 300000:
            raise ValueError("README supera limite de seguridad")
        buf = resp.read(300001)
        if len(buf) > 300000:
            raise ValueError("README supera limite de seguridad")
        return buf.decode("utf-8")

def evaluate(manifest, loader):
    if set(manifest) != set(REQUIRED):
        raise ValueError("Fuentes no autorizadas")
    results = []
    for repo in sorted(REQUIRED):
        entry = manifest[repo]
        if set(entry) != {"commit", "license"}:
            raise ValueError("Esquema de metadatos inesperado")
        if entry["license"] not in {"MIT", "Apache-2.0"}:
            raise ValueError("Licencia desconocida, requiere revision")
        results.append(inspect(repo, entry["commit"], loader(repo, entry["commit"])))
    return {
        "pilot": "A: comprobacion estatica de upstreams fijados",
        "status": "PASS" if all(x["static_claims_found"] for x in results) else "NEEDS_REVIEW",
        "caution": "README no demuestra ejecucion real, seguridad, ni conexion de sesiones privadas",
        "upstreams": results,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--live-readmes", action="store_true",
                   help="Consultar README publicos fijados, nunca ejecutar dependencias")
    p.add_argument("--out", type=Path,
                   help="Archivo de resultado fuera del repositorio preferentemente")
    args = p.parse_args()
    if not args.live_readmes:
        p.error("Para consulta real usar --live-readmes; tests sinteticos son independientes")
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        result = evaluate(manifest, fetch_readme)
    except (ValueError, KeyError, HTTPError, URLError, UnicodeError, OSError) as exc:
        print("Piloto A no verificado:", str(exc), file=sys.stderr)
        return 2
    report = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    print(report)
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
