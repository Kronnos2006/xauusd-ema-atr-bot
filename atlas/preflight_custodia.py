"""H4: preflight de ensayos ATLAS, cerrado hasta custodia externa real.

Nunca interpreta un booleano, una ruta local o un hash auto-declarado
como prueba de registro externo. Solo produce diagnósticos.
"""
import hashlib
import json
from datetime import datetime, timezone


def _canonico(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def huella_definicion(definicion: dict) -> str:
    """SHA-256 de la definición completa, con claves requeridas inmutables."""
    obligatorias = {"hipotesis", "familia", "parametros", "codigo_sha", "datos_ref"}
    if not isinstance(definicion, dict) or not obligatorias.issubset(definicion):
        raise ValueError("definicion incompleta")
    if not all(isinstance(definicion[k], str) and definicion[k].strip()
               for k in ("hipotesis", "familia", "codigo_sha")):
        raise ValueError("identidad de definicion invalida")
    if (not isinstance(definicion["parametros"], dict)
            or not isinstance(definicion["datos_ref"], dict)
            or not definicion["datos_ref"].get("hash_datos")):
        raise ValueError("parametros o hash de datos ausentes")
    return hashlib.sha256(_canonico(definicion)).hexdigest()


def preflight_sin_custodia(definicion: dict, intento_id: str,
                          recibo: dict | None = None) -> dict:
    """Diagnóstico nunca habilitante; recibo autodeclarado NO es autenticación.

    La integración real debe leer y verificar el recibo de un proveedor
    separado, comprobar la hora de sellado y no aceptar un dict del cliente.
    """
    h = huella_definicion(definicion)
    if not isinstance(intento_id, str) or not intento_id.strip():
        raise ValueError("intento_id invalido")
    if recibo is not None:
        if not isinstance(recibo, dict) or recibo.get("intento_id") != intento_id:
            raise ValueError("recibo sin identidad correspondiente")
        if recibo.get("hash_definicion") != h:
            raise ValueError("definicion cambiada sin nuevo intento")
    return {"estado": "INCONCLUSA", "causa": "custodia externa no autenticada",
            "intento_id": intento_id, "hash_definicion": h,
            "ejecucion_permitida": False, "promocion_permitida": False}
