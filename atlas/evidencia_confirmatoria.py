"""ATLAS: comprobaciones de evidencia, sin permisos de promoción.

Las fuentes y censos son artefactos congelados, nunca listas de resultados
suministradas al evaluador. La comprobación de autenticidad del origen GitHub
debe realizarse por un verificador externo independiente.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from .laboratorio import Barra, Senal, instante


def _sha(contenido: bytes) -> str:
    return hashlib.sha256(contenido).hexdigest()


def _leer_json_fijado(ruta: str | Path, sha256: str):
    """Verifica el SHA de *bytes* antes de abrir el documento."""
    if not isinstance(sha256, str) or len(sha256) != 64:
        raise ValueError("SHA256 faltante o malformado")
    try:
        int(sha256, 16)
    except ValueError as exc:
        raise ValueError("SHA256 inválido") from exc
    datos = Path(ruta).read_bytes()
    if _sha(datos) != sha256.lower():
        raise ValueError("contenido distinto del SHA256 anclado")
    return json.loads(datos)


def censar_variantes(ruta: str | Path, sha256: str) -> dict:
    """Censo auditable: rechaza huecos, duplicados y totales elegidos a mano.

    El anclaje externo y la exhaustividad histórica siguen siendo tareas
    de auditoría: un SHA proporcionado por el invocador NO es un ancla confiable.
    """
    doc = _leer_json_fijado(ruta, sha256)
    if not isinstance(doc, dict) or doc.get("schema") != "atlas-variantes-v1":
        raise ValueError("schema de censo desconocido")
    variantes = doc.get("variantes")
    if not isinstance(variantes, list) or not variantes:
        raise ValueError("censo vacío")
    ids = []
    for v in variantes:
        if not isinstance(v, dict) or not isinstance(v.get("id"), str) or not v["id"].strip():
            raise ValueError("variante sin identificador")
        if not isinstance(v.get("preregistro"), str) or not v["preregistro"].strip():
            raise ValueError("variante sin preregistro")
        ids.append(v["id"])
    if len(set(ids)) != len(ids):
        raise ValueError("variantes duplicadas")
    if "n_total" in doc and doc["n_total"] != len(ids):
        raise ValueError("N_total declarado incompatible con entradas")
    return {"n_total": len(ids), "sha256": sha256.lower(), "variantes": tuple(ids),
            "estado": "CENSO_LOCAL_NO_CERTIFICADO"}


def reconstruir_operaciones(barras: list[Barra], senales: list[Senal],
                           costo_lado: float = 0.0015) -> list[dict]:
    """Cierra operaciones desde cambios reales de posición y las barras.

    Usa el mismo retorno open→close intrabar y costo por cambio de posición
    del simulador v2. No infiere PnL a partir de retornos aportados por usuario.
    Posiciones continuas acumulan sus resultados multiplicativamente.
    No permite posiciones abiertas sin liquidar ni barras superpuestas.
    """
    from math import isfinite
    if len(barras) < 2 or not isfinite(costo_lado) or not 0 <= costo_lado < 1:
        raise ValueError("entrada inválida")
    tiempos = [(instante(b.apertura_utc), instante(b.cierre_utc)) for b in barras]
    if any(tiempos[i][1] > tiempos[i+1][0] for i in range(len(tiempos)-1)):
        raise ValueError("barras duplicadas, solapadas o desordenadas")
    if len({s.id for s in senales}) != len(senales):
        raise ValueError("señales duplicadas")
    if not all(s.sello_externo_verificado for s in senales):
        raise ValueError("señales sin sello verificado")
    orden = sorted(senales, key=lambda s: instante(s.publicada_utc))
    if len({instante(s.publicada_utc) for s in orden}) != len(orden):
        raise ValueError("señales de publicación simultánea ambiguas")
    posicion, factor, actual, salida = 0, 1.0, None, []
    for i in range(1, len(barras)):
        elegibles = [s for s in orden if instante(s.publicada_utc) <= tiempos[i-1][1]]
        s = elegibles[-1] if elegibles else None
        nueva = s.posicion if s else 0
        if nueva != posicion and posicion != 0:
            factor *= (1 - costo_lado)  # salida de la posición anterior
            salida.append({"senal": actual, "retorno_neto": factor-1, "cierre_barra": i-1})
            factor, actual = 1.0, None
        if nueva != posicion and nueva != 0:
            factor = 1 - costo_lado  # entrada
            actual = s.id
        posicion = nueva
        cambio = barras[i].cierre / barras[i].apertura - 1
        f = 1 + posicion*cambio
        if f <= 0:
            raise ValueError("factor no válido en barra")
        if posicion:
            factor *= f
        if i == len(barras)-1 and posicion:
            factor *= (1 - costo_lado)
            salida.append({"senal": actual, "retorno_neto": factor-1, "cierre_barra": i})
    if any(not isfinite(op["retorno_neto"]) or op["retorno_neto"] <= -1 for op in salida):
        raise ValueError("operaciones inválidas")
    return salida


def preparar_evidencia(ruta_barras: str | Path, sha_barras: str,
                      ruta_censo: str | Path, sha_censo: str,
                      senales: list[Senal], repo: str,
                      referencias: dict[str, tuple[str, str]],
                      obtener_anclas=None, leer_git=None,
                      costo_lado: float = 0.0015) -> dict:
    """Cálculo reproducible descriptivo, sin posibilidad de aprobación."""
    crudo = _leer_json_fijado(ruta_barras, sha_barras)
    if not isinstance(crudo, list):
        raise ValueError("se esperaban barras JSON")
    barras = [Barra(**x) for x in crudo]
    censo = censar_variantes(ruta_censo, sha_censo)
    from .sello_preregistro import verificar_sello
    if not senales or len({s.id for s in senales}) != len(senales):
        raise ValueError("señales vacías o duplicadas")
    verificadas = []
    for s in senales:
        ref = referencias.get(s.id)
        if not ref or not verificar_sello(s, repo, ref[0], ref[1],
                                          obtener_anclas, leer_git):
            raise ValueError("sello externo no verificable")
        # Nunca confiar en el booleano que suministra el invocador.
        verificadas.append(Senal(s.id, s.publicada_utc, s.posicion,
                                 s.preregistro, True))
    ops = reconstruir_operaciones(barras, verificadas, costo_lado)
    return {"operaciones": ops, "n_total": censo["n_total"],
            "sha_barras": sha_barras, "sha_censo": sha_censo,
            "estado": "DESCRIPTIVO_NO_CONFIRMATORIO",
            "promocion_permitida": False}


def preparar_evidencia_encadenada(ruta_barras: str | Path, sha_barras: str,
                                  ruta_intentos: str | Path, ancla_intentos: dict,
                                  senales: list[Senal], repo: str,
                                  referencias: dict[str, tuple[str, str]],
                                  obtener_anclas=None, leer_git=None,
                                  costo_lado: float = 0.0015) -> dict:
    """Calcula retornos de señales selladas, N de eventos encadenados.

    El invocador NO proporciona N ni retornos. El ancla de intentos ha de
    proceder de una custodia externa autenticada antes de llamarse aquí.
    Hasta contar con esa infraestructura y un backtest prospectivo, ningún
    resultado de esta función es confirmatorio.
    """
    from .censo_variantes import verificar_censo
    from .sello_preregistro import verificar_sello
    registro = verificar_censo(ruta_intentos, ancla_intentos)
    crudo = _leer_json_fijado(ruta_barras, sha_barras)
    if not isinstance(crudo, list):
        raise ValueError("dataset de barras inválido")
    barras = [Barra(**x) for x in crudo]
    if not senales or len({s.id for s in senales}) != len(senales):
        raise ValueError("señales vacías o duplicadas")
    selladas = []
    for s in senales:
        ref = referencias.get(s.id)
        if not ref or not verificar_sello(s, repo, ref[0], ref[1],
                                          obtener_anclas, leer_git):
            raise ValueError("sello remoto no verificable")
        selladas.append(Senal(s.id, s.publicada_utc, s.posicion,
                              s.preregistro, True))
    ops = reconstruir_operaciones(barras, selladas, costo_lado)
    return {"n_total": registro["n_total"], "operaciones": ops,
            "sha_barras": sha_barras, "ultimo_hash_censo": registro["ultimo_hash"],
            "estado": "DESCRIPTIVO_PROCEDENCIA_PARCIAL",
            "promocion_permitida": False}
