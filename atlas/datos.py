"""ATLAS · adaptadores de datos (solo lectura).

Patrón de tres pasos adaptado de OpenBB-finance/OpenBB@78020ee,
openbb_platform/core/openbb_core/provider/abstract/fetcher.py (transform_query → extract_data → transform_data).
Cada adaptador devuelve Registros con procedencia; ante un fallo devuelve cobertura_faltante, nunca datos inventados.
KT-002 se lee en modo solo lectura: ATLAS jamás escribe en data/kt002.
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
from pathlib import Path

from .procedencia import Registro, cobertura_faltante, iso, sha256_bytes, t

BINANCE = "Binance spot BTCUSDT (data-api.binance.vision), copia del repo"
LIC_BINANCE = "datos públicos de mercado de Binance; uso según sus términos"
DUR = {"1d": dt.timedelta(days=1), "4h": dt.timedelta(hours=4), "1h": dt.timedelta(hours=1)}


class FalloProveedor(Exception):
    pass


def _leer(ruta: Path) -> bytes:
    try:
        return Path(ruta).read_bytes()
    except OSError as e:
        raise FalloProveedor(f"no se pudo leer {ruta}: {e}") from e


class VelasArchivo:
    """Velas [open_ms, o, h, l, c, v] guardadas por la guardia. Utilizable = cierre de la vela."""

    def __init__(self, ruta: str, intervalo: str, activo: str = "BTCUSDT"):
        self.ruta, self.intervalo, self.activo = Path(ruta), intervalo, activo

    def transform_query(self, corte: dt.datetime) -> dict:
        if self.intervalo not in DUR:
            raise ValueError(f"intervalo no soportado: {self.intervalo}")
        return {"corte": corte}

    def extract_data(self, q: dict) -> tuple[list, str]:
        raw = _leer(self.ruta)
        try:
            return json.loads(raw), sha256_bytes(raw)
        except ValueError as e:
            raise FalloProveedor(f"JSON inválido en {self.ruta}") from e

    def transform_data(self, q: dict, data: tuple[list, str]) -> list[Registro]:
        filas, h = data
        out = []
        for f in filas:
            abre = dt.datetime.fromtimestamp(int(f[0]) / 1000, dt.timezone.utc)
            cierra = abre + DUR[self.intervalo]
            if cierra > q["corte"]:
                continue  # vela no cerrada al corte: información futura
            out.append(Registro(BINANCE, f"{self.ruta}#{int(f[0])}", self.activo, f"vela_{self.intervalo}",
                                {"o": float(f[1]), "h": float(f[2]), "l": float(f[3]), "c": float(f[4]), "v": float(f[5])},
                                iso(abre), iso(cierra), None, iso(cierra), "validado", h, LIC_BINANCE))
        return out

    def obtener(self, corte: dt.datetime) -> list[Registro]:
        try:
            q = self.transform_query(corte)
            return self.transform_data(q, self.extract_data(q))
        except FalloProveedor as e:
            return [cobertura_faltante(BINANCE, self.activo, f"vela_{self.intervalo}", str(e))]


class SpreadArchivo:
    def __init__(self, ruta: str, activo: str = "BTCUSDT"):
        self.ruta, self.activo = Path(ruta), activo

    def obtener(self, corte: dt.datetime) -> list[Registro]:
        try:
            raw = _leer(self.ruta)
        except FalloProveedor as e:
            return [cobertura_faltante(BINANCE, self.activo, "spread", str(e))]
        h, out = sha256_bytes(raw), []
        for r in csv.DictReader(io.StringIO(raw.decode())):
            u = t(r["utc"])
            if u and u <= corte:
                out.append(Registro(BINANCE, f"{self.ruta}#{r['utc']}", self.activo, "spread",
                                    {"spread_pct": float(r["spread_pct"])}, r["utc"], r["utc"], None, r["utc"],
                                    "validado", h, LIC_BINANCE))
        return out or [cobertura_faltante(BINANCE, self.activo, "spread", "sin mediciones de spread antes del corte")]


PRED_CAMPOS = ("run_utc", "base_open_utc", "base_close", "target_open_utc", "kronos_ret", "timesfm_ret", "kt001_ret")
PUNT_CAMPOS = ("actual_close4", "actual_ret", "kronos_hit", "timesfm_hit", "kt001_hit")


class PrediccionesKT002:
    """Lee data/kt002/predicciones.csv SIN modificarlo. Una predicción es utilizable desde run_utc; su
    puntuación (resultado real) solo desde scored_utc: antes del corte se oculta (evita look-ahead)."""

    def __init__(self, ruta: str = "data/kt002/predicciones.csv", activo: str = "BTCUSDT"):
        self.ruta, self.activo = Path(ruta), activo

    def obtener(self, corte: dt.datetime) -> list[Registro]:
        try:
            raw = _leer(self.ruta)
        except FalloProveedor as e:
            return [cobertura_faltante("KT-002", self.activo, "prediccion", str(e))]
        h, out = sha256_bytes(raw), []
        for r in csv.DictReader(io.StringIO(raw.decode())):
            run = t(r["run_utc"])
            if not run or run > corte:
                continue
            v = {k: r[k] for k in PRED_CAMPOS}
            s = t(r.get("scored_utc"))
            if s and s <= corte:
                v.update({k: r[k] for k in PUNT_CAMPOS})
                v["scored_utc"] = r["scored_utc"]
            else:
                v.update({k: "" for k in PUNT_CAMPOS})  # resultado aún no conocido al corte
            out.append(Registro("KT-002 (Kronos-small, TimesFM 2.5, KT-001)", f"{self.ruta}#{r['base_open_utc']}",
                                self.activo, "prediccion", v, r["base_open_utc"], r["run_utc"], None, r["run_utc"],
                                "validado", h, "propio (ORION)"))
        return out or [cobertura_faltante("KT-002", self.activo, "prediccion", "sin predicciones antes del corte")]


class EventosArchivo:
    """Eventos o noticias verificados en JSON: [{fuente, url, evento_utc, publicado_utc, tipo, hecho, direccion}].
    Sin archivo: se declara la ausencia de cobertura (no 'no hubo noticias')."""

    def __init__(self, ruta: str | None, activo: str = "BTCUSDT"):
        self.ruta, self.activo = (Path(ruta) if ruta else None), activo

    def obtener(self, corte: dt.datetime) -> list[Registro]:
        if not self.ruta:
            return [cobertura_faltante("noticias/macro", self.activo, "evento", "no hay fuente de eventos con fecha de publicación verificable configurada")]
        try:
            raw = _leer(self.ruta)
            items = json.loads(raw)
        except (FalloProveedor, ValueError) as e:
            return [cobertura_faltante("noticias/macro", self.activo, "evento", str(e))]
        h, out = sha256_bytes(raw), []
        for e in items:
            pub, ocurr = t(e.get("publicado_utc")), t(e.get("evento_utc"))
            if (pub is not None and pub > corte) or (ocurr is not None and ocurr > corte):
                continue  # publicado u ocurrido después del corte
            out.append(Registro(e.get("fuente", "?"), e.get("url", "-"), self.activo, "evento",
                                {"tipo": e.get("tipo"), "hecho": e.get("hecho"), "direccion": int(e.get("direccion", 0))},
                                e.get("evento_utc"), e.get("publicado_utc"), None, e.get("publicado_utc"),
                                "sin_validar", h, e.get("licencia", "desconocida")))
        return out
