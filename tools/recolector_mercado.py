#!/usr/bin/env python3
"""Descarga HTTP de snapshots explícitos: no corre por cron, sin trading ni LLM."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def collect(url, output, max_bytes=2_000_000, retries=2):
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.username or p.password:
        raise ValueError("Solo URL HTTPS válida sin credenciales")
    out = Path(output)
    if out.exists():
        raise FileExistsError("No sobrescribir snapshot existente")
    body = None
    for attempt in range(retries + 1):
        try:
            with urlopen(Request(url, headers={"User-Agent": "Kronnos-research/1.0"}), timeout=12) as response:
                if response.status != 200:
                    raise RuntimeError("Respuesta HTTP no satisfactoria")
                body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ValueError("Respuesta excede límite")
            break
        except (HTTPError, URLError, TimeoutError) as exc:
            if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == retries:
                raise RuntimeError("Fuente no disponible") from exc
            time.sleep(min(2 ** attempt, 4))
    # Verificar JSON antes de publicar. No almacenar llaves ni tokens.
    json.loads(body)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    try:
        with tmp.open("xb") as f:
            f.write(body)
        os.replace(tmp, out)
    finally:
        tmp.unlink(missing_ok=True)
    return {"bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(), "archivo": str(out)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="HTTPS fuente de JSON sin credenciales")
    ap.add_argument("--output", required=True, help="Archivo nuevo, nunca sobrescrito")
    args = ap.parse_args()
    print(json.dumps(collect(args.url, args.output), ensure_ascii=False))
