"""ATLAS · procedencia y disponibilidad temporal de cada dato.

Ideas adaptadas, sin copiar código:
- frescura medida desde que el dato fue utilizable: Ruixing0328/multi-agent-investment-research-system@635289c,
  data_platform/freshness.py (classify_freshness);
- "sin cobertura" no es "vacío": TauricResearch/TradingAgents@e8f5503, dataflows/date_window.py (coverage_gap).
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt
import hashlib

CALIDADES = ("validado", "sin_validar", "corregido", "contradictorio", "faltante")


def t(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    x = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return x if x.tzinfo else x.replace(tzinfo=dt.timezone.utc)


def iso(x: dt.datetime | None) -> str | None:
    return x.astimezone(dt.timezone.utc).isoformat() if x else None


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dc.dataclass(frozen=True)
class Registro:
    """Un dato con su procedencia. `utilizable_utc` es desde cuándo podía usarse de verdad."""
    fuente: str
    identificador: str            # URL, ruta o id
    activo: str
    tipo: str                     # vela | prediccion | evento | spread
    valor: object
    evento_utc: str | None        # cuándo ocurrió
    publicado_utc: str | None     # cuándo lo publicó la fuente
    recibido_utc: str | None      # cuándo lo recibió ORION (None = no registrado)
    utilizable_utc: str | None    # None = sin disponibilidad temporal verificable
    calidad: str = "sin_validar"
    hash_sha256: str | None = None
    licencia: str = "desconocida"
    nota: str = ""

    def __post_init__(self):
        if self.calidad not in CALIDADES:
            raise ValueError(f"calidad inválida: {self.calidad}")

    def utilizable_en(self, corte: dt.datetime) -> bool:
        u = t(self.utilizable_utc)
        return u is not None and u <= corte

    def como_dict(self) -> dict:
        return dc.asdict(self)


def cobertura_faltante(fuente: str, activo: str, tipo: str, motivo: str) -> Registro:
    """Ausencia declarada: no es evidencia de que no pasó nada."""
    return Registro(fuente=fuente, identificador="-", activo=activo, tipo=tipo, valor=None, evento_utc=None,
                    publicado_utc=None, recibido_utc=None, utilizable_utc=None, calidad="faltante",
                    nota=f"sin cobertura: {motivo} (no es ausencia de {tipo})")


def frescura(reg: Registro, corte: dt.datetime, limite: dt.timedelta) -> str:
    """fresco | viejo | faltante | futuro, medido desde utilizable_utc."""
    u = t(reg.utilizable_utc)
    if reg.calidad == "faltante" or u is None:
        return "faltante"
    if u > corte:
        return "futuro"
    return "viejo" if corte - u > limite else "fresco"


def discrepancia(a: Registro, b: Registro, tolerancia_rel: float) -> dict | None:
    """Si dos fuentes difieren, se conservan ambas (nunca se elige una arbitrariamente)."""
    va, vb = float(a.valor), float(b.valor)
    if abs(va - vb) <= tolerancia_rel * max(abs(va), abs(vb), 1e-12):
        return None
    return {"tipo": "discrepancia_fuentes", "fuentes": [a.fuente, b.fuente], "valores": [va, vb],
            "registros": [a.como_dict(), b.como_dict()]}
