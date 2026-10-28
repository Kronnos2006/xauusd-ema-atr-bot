#!/usr/bin/env python3
"""Kronnos: snapshot de JSON local o HTTPS explícitamente autorizada. Sin cron."""
import argparse
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler, Request

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def validated_host(url, allowed):
    p = urlsplit(url)
    if (p.scheme != "https" or p.hostname not in allowed or p.username
            or p.password or p.port not in (None, 443)):
        raise ValueError("HTTPS host no autorizado")
    ips = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
    if not ips or any(not ipaddress.ip_address(a[4][0]).is_global for a in ips):
        raise ValueError("Destino privado/no global bloqueado")
    return url

def collect(url, output, allowed_hosts=(), max_bytes=2_000_000, retries=2):
    """Solo destinos públicos en allowlist; revalidar seguridad de transporte antes de producción."""
    validated_host(url, set(allowed_hosts))
    opener = build_opener(NoRedirect)
    body = None
    for attempt in range(retries + 1):
        try:
            with opener.open(Request(url, headers={"User-Agent": "Kronnos-research/1.0"}), timeout=12) as response:
                if response.status != 200:
                    raise ValueError("HTTP no satisfactorio")
                body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ValueError("Respuesta demasiado grande")
            break
        except (HTTPError, URLError, TimeoutError) as exc:
            if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == retries:
                raise RuntimeError("Fuente no disponible") from exc
            time.sleep(min(2**attempt, 4))
    json.loads(body)
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Creación exclusiva: nunca sobrescribir snapshots ni archivos preexistentes.
    with out.open("xb") as handle:
        handle.write(body)
        handle.flush()
        os.fsync(handle.fileno())
    return {"archivo": str(out), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--allow-host", action="append", default=[], help="Hostname HTTPS público explícitamente aprobado")
    a = p.parse_args()
    if not a.allow_host:
        p.error("Sin --allow-host no se habilita acceso de red")
    print(json.dumps(collect(a.url, a.output, a.allow_host), ensure_ascii=False))
