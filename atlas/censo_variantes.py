"""Censo de intentos ATLAS: cadena de eventos solo-anexar, fail-closed.

Cada evaluación real genera un evento de intento incluso cuando fracasa; no se
puede eliminar intentos sin cambiar la huella final. Un ancla obtenida por el
mismo invocador NO demuestra que el registro histórico sea exhaustivo.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

CERO = "0"*64
SCHEMA = "atlas-intentos-v1"


def _json(x) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _hash(x) -> str:
    return hashlib.sha256(_json(x)).hexdigest()


def construir_evento(anterior: str, intento_id: str, variante_id: str,
                     preregistro: str, ejecutado_utc: str) -> dict:
    """Constructor puro: no escribe ni autoriza variantes."""
    if len(anterior) != 64 or any(c not in "0123456789abcdef" for c in anterior):
        raise ValueError("hash anterior inválido")
    if not all(isinstance(v, str) and v.strip()
               for v in (intento_id, variante_id, preregistro)):
        raise ValueError("identificador de intento/variante/pre-registro ausente")
    from .laboratorio import instante
    instante(ejecutado_utc)
    cuerpo = {"schema": SCHEMA, "anterior": anterior, "intento_id": intento_id,
              "variante_id": variante_id, "preregistro": preregistro,
              "ejecutado_utc": ejecutado_utc}
    return {**cuerpo, "hash": _hash(cuerpo)}


def verificar_censo(registro: str | Path, ancla: dict) -> dict:
    """Verifica snapshot completo frente a ancla externa YA autenticada.

    Exige SHA del archivo, cuenta exacta de líneas y hash del último evento;
    no tolera registros vacíos, reordenamiento, eventos duplicados ni fechas
    posteriores al corte de evidencia.
    """
    from .laboratorio import instante
    if not isinstance(ancla, dict) or set(("sha256", "lineas", "ultimo_hash",
                                           "corte_utc")) - set(ancla):
        raise ValueError("ancla externa incompleta")
    contenido = Path(registro).read_bytes()
    if hashlib.sha256(contenido).hexdigest() != ancla["sha256"]:
        raise ValueError("archivo no coincide con ancla SHA256")
    try:
        corte = instante(ancla["corte_utc"])
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("corte temporal inválido") from exc
    lineas = contenido.decode("utf-8").splitlines()
    if not lineas or len(lineas) != ancla["lineas"]:
        raise ValueError("censo truncado, vacío o con líneas extras")
    prev, vistos, eventos = CERO, set(), []
    for n, raw in enumerate(lineas, 1):
        try:
            ev = json.loads(raw)
            if not isinstance(ev, dict) or set(ev) != {
                    "schema", "anterior", "intento_id", "variante_id",
                    "preregistro", "ejecutado_utc", "hash"}:
                raise ValueError("schema inválido")
            if ev["schema"] != SCHEMA or ev["anterior"] != prev:
                raise ValueError("cadena rota")
            cuerpo = {k:v for k,v in ev.items() if k != "hash"}
            if _hash(cuerpo) != ev["hash"]:
                raise ValueError("evento modificado")
            if not all(isinstance(ev[k], str) and ev[k].strip()
                       for k in ("intento_id", "variante_id", "preregistro")):
                raise ValueError("identidad incompleta")
            if ev["intento_id"] in vistos:
                raise ValueError("intento repetido")
            if instante(ev["ejecutado_utc"]) > corte:
                raise ValueError("intento posterior al corte")
            vistos.add(ev["intento_id"])
            prev = ev["hash"]
            eventos.append(ev)
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            raise ValueError(f"evento {n} inválido: {exc}") from exc
    if prev != ancla["ultimo_hash"]:
        raise ValueError("último hash no coincide con el ancla")
    return {"n_total": len(eventos), "ultimo_hash": prev,
            "variantes": sorted({e["variante_id"] for e in eventos}),
            "estado": "CADENA_LOCAL_VERIFICADA_CUSTODIA_EXTERNA_PENDIENTE"}


def conciliar_con_inventario_externo(registro: str | Path, ancla: dict,
                                    ids_externos: list[str], *, autenticado: bool = False) -> dict:
    """Comparación estricta contra inventario externo. No autentica al proveedor.

    El argumento autenticado SOLO puede venir de una capa de confianza independiente;
    esta función nunca emite certificado de custodia ni abre confirmatorio.
    """
    if autenticado is not True:
        raise ValueError("inventario externo sin autenticacion independiente")
    if not isinstance(ids_externos, list) or not ids_externos or any(
            not isinstance(i, str) or not i for i in ids_externos):
        raise ValueError("inventario externo invalido")
    if len(set(ids_externos)) != len(ids_externos):
        raise ValueError("identificadores repetidos en inventario externo")
    reporte = verificar_censo(registro, ancla)
    ids_locales = [json.loads(line)["intento_id"]
                   for line in Path(registro).read_text(encoding="utf-8").splitlines()]
    faltantes = sorted(set(ids_externos) - set(ids_locales))
    sobrantes = sorted(set(ids_locales) - set(ids_externos))
    if faltantes or sobrantes:
        raise ValueError(f"censo incompleto: faltantes={len(faltantes)}, sobrantes={len(sobrantes)}")
    return {**reporte, "n_total": len(ids_externos),
            "estado": "CONCILIADO_SIN_CERTIFICACION_DE_CUSTODIA",
            "promocion_permitida": False}
