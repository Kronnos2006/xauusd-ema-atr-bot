#!/usr/bin/env python3
"""Kronnos: ingesta HTTPS aislada DESHABILITADA por defecto, sin trading."""
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
from urllib.request import build_opener, HTTPRedirectHandler, ProxyHandler, Request

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def validated_host(url, allowed):
    p = urlsplit(url)
    if p.scheme != "https" or not p.hostname or p.hostname not in allowed or p.username or p.password or p.port not in (None, 443):
        raise ValueError("HTTPS host no autorizado")
    addresses = socket.getaddrinfo(p.hostname, 443, type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(x[4][0]).is_global for x in addresses):
        raise ValueError("IP no global bloqueada")
    return url

def collect(url, output, allowed_hosts=(), max_bytes=2_000_000, retries=2, isolated=False):
    # DNS puede cambiar entre comprobación y conexión (rebinding).
    # La comprobación local no sustituye el bloqueo de egreso de red del runner.
    if not isolated:
        raise PermissionError("INGESTA_DESHABILITADA: requiere runner con egreso restringido")
    validated_host(url, set(allowed_hosts))
    opener = build_opener(ProxyHandler({}), NoRedirect)
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
    with out.open("xb") as handle:
        handle.write(body)
        handle.flush()
        os.fsync(handle.fileno())
    return {"archivo": str(out), "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--allow-host", action="append", default=[])
    a = p.parse_args()
    p.error("La ingesta externa permanece deshabilitada hasta disponer de sandbox de red con egreso restringido")
