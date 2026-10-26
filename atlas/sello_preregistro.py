"""Sello remoto GitHub. Nunca confía en un booleano de Senal ni en fechas del propio commit.

Exige (a) commit con blob verificable en el árbol git y (b) una ejecución de
GitHub Actions observada por servidor antes de publicada_utc, para ese SHA.
Sin ejecución anterior: fallo cerrado (aunque git committer date sea anterior).
"""
from __future__ import annotations
import json
import re
import subprocess
from datetime import datetime,timezone
from .laboratorio import instante,Senal

_SHA = re.compile(r"^[0-9a-f]{40}$")
_REPO = re.compile(r"^[\w.-]+/[\w.-]+$")
def verificar_sello(senal: Senal, repo: str, commit: str, ruta: str,
                    obtener_anclas=None, leer_git=None) -> bool:
    """Anclas: [{head_sha, created_at, status}] procedentes de GitHub API Actions.

    Inyectables solo para tests. Ninguna fecha autodeclarada se toma como sello.
    """
    if not _REPO.fullmatch(repo) or not _SHA.fullmatch(commit) or ruta.startswith("/") or ".." in ruta.split("/"):
        raise ValueError("referencia de sello inválida")
    leer_git = leer_git or (lambda sha,path: subprocess.check_output(
        ["git","show",f"{sha}:{path}"],timeout=10))
    try:
        contenido = leer_git(commit,ruta)
        doc = json.loads(contenido)
        if not isinstance(doc, dict) or doc.get("id") != senal.preregistro:
            return False
        # El ID solo no vincula una predicción concreta a su preregistro.
        if (doc.get("senal_id") != senal.id
                or doc.get("posicion") != senal.posicion
                or doc.get("publicada_utc") != senal.publicada_utc):
            return False
    except (OSError,ValueError,subprocess.SubprocessError):
        return False
    # ATLAS está aislado de red: la capa de auditoría suministra observaciones
    # obtenidas de GitHub Actions. Sin un proveedor externo: fallo cerrado.
    if obtener_anclas is None:
        return False
    try:
        runs=obtener_anclas(repo,commit)
        pub=instante(senal.publicada_utc)
        return any(isinstance(r,dict) and r.get("head_sha")==commit and isinstance(r.get("created_at"),str) and r.get("status")=="completed" and r.get("conclusion")=="success" and instante(r["created_at"])<pub for r in runs)
    except (OSError,KeyError,ValueError,TimeoutError,TypeError,AttributeError):
        return False
