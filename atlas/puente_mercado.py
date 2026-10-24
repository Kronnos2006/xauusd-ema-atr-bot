"""Puente local de velas Binance ya archivadas a barras de laboratorio.

Sin red y sin modificaciones a datos: conserva SHA-256 del archivo de entrada.
La disponibilidad se limita a la hora de cierre de la vela, nunca a su apertura.
Los datos históricos no demuestran un preregistro prospectivo.
"""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .laboratorio import Barra

INTERVALOS = {"4h": timedelta(hours=4), "1d": timedelta(days=1)}

def cargar_barras(ruta: str | Path, intervalo: str = "4h", corte_utc: str | None = None) -> dict:
    if intervalo not in INTERVALOS:
        raise ValueError("intervalo no soportado")
    contenido = Path(ruta).read_bytes()
    filas = json.loads(contenido)
    corte = datetime.fromisoformat(corte_utc.replace("Z", "+00:00")) if corte_utc else None
    if corte is not None and corte.tzinfo is None:
        raise ValueError("corte requiere zona horaria")
    barras = []
    ultimo_cierre = None
    for f in filas:
        abre = datetime.fromtimestamp(int(f[0]) / 1000, tz=timezone.utc)
        cierra = abre + INTERVALOS[intervalo]
        if ultimo_cierre is not None and abre < ultimo_cierre:
            raise ValueError("barras desordenadas o duplicadas")
        ultimo_cierre = cierra
        if corte is not None and cierra > corte:
            continue
        barras.append(Barra(abre.isoformat(), cierra.isoformat(), float(f[1]), float(f[4])))
    return {"barras": barras, "sha256_origen": hashlib.sha256(contenido).hexdigest(),
            "intervalo": intervalo, "corte_utc": corte_utc,
            "n_barras_cerradas": len(barras),
            "advertencia": "archivo archivado, no garantiza hora histórica de recepción ni sello prospectivo"}
