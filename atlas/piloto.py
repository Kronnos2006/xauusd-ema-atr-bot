"""ATLAS · piloto BTCUSDT: evalúa una predicción publicada de KT-002 en su contexto, en un punto del tiempo.

Uso:  python3 -m atlas.piloto --corte 2026-10-21T00:00:00Z [--eventos ruta.json] [--salida research/atlas/salidas]
Solo lectura de data/: no modifica KT-002, no descarga, no opera. Escribe solo en --salida.
La parte medida es determinista: la misma entrada da el mismo `huella_contenido`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from . import analitica as an
from .contradicciones import revisar
from .datos import EventosArchivo, PrediccionesKT002, SpreadArchivo, VelasArchivo
from .procedencia import Registro, t
from .tesis import huella

VERSION = "atlas-piloto-0.1"
PROHIBIDO = ("data/kt002",)  # aislamiento: jamás se escribe ahí


def obtener(corte: dt.datetime, raiz: Path = Path("."), eventos: str | None = None) -> list[Registro]:
    return (VelasArchivo(raiz / "data/mercado/btc_1d.json", "1d").obtener(corte)
            + SpreadArchivo(raiz / "data/mercado/spread_btcusdt.csv").obtener(corte)
            + PrediccionesKT002(raiz / "data/kt002/predicciones.csv").obtener(corte)
            + EventosArchivo(str(raiz / eventos) if eventos else None).obtener(corte))


def evaluar(corte: dt.datetime, raiz: Path = Path("."), eventos: str | None = None) -> dict:
    return analizar(corte, obtener(corte, raiz, eventos))


def analizar(corte: dt.datetime, registros: list[Registro]) -> dict:
    """Determinista: solo depende del corte y de los registros (se guardan como instantánea)."""
    por = lambda pre: [r for r in registros if r.tipo.startswith(pre)]
    velas, spreads, preds, evs = por("vela_1d"), por("spread"), por("prediccion"), por("evento")

    evid = [an.tendencia(velas), an.volatilidad(velas), an.volumen(velas), an.liquidez(spreads),
            *an.predictivo(preds), an.eventos(evs)]
    p = next((e for e in evid if e.modulo == "predictivo.kt001" and e.tipo != "ausente"), None)
    direccion = p.direccion if p and p.direccion else 1
    rev = revisar(direccion, evid, registros, corte)

    hechos = [e.afirmacion for e in evid if e.tipo == "hecho"]
    inferencias = [e.afirmacion for e in evid if e.tipo == "inferencia"]
    causales = [e.afirmacion for e in evid if e.tipo == "hipotesis_causal"]
    ausente = [f"{e.modulo}: {e.afirmacion}" for e in evid if e.tipo == "ausente"]
    lado = "sube" if direccion > 0 else "baja"
    tesis = {
        "id": f"TS-BTC-{corte.strftime('%Y%m%dT%H%MZ')}", "version": 1, "corte_utc": corte.isoformat(),
        "activo": "BTCUSDT", "mercado": "Binance spot", "horizonte": "4h",
        "pregunta": "¿La predicción publicada de KT-001 al corte está respaldada por evidencia independiente?",
        "hipotesis": f"BTC {lado} en las 4 h siguientes a {p.medicion['base_open_utc'] if p else 'la última vela'}, como predice KT-001",
        "mecanismo": "estadístico: modelos de series de tiempo (Kronos/TimesFM) sin mecanismo económico propuesto",
        "evidencia_favorable": rev["favor"], "evidencia_contraria": rev["contra"],
        "interpretaciones_alternativas": ["ruido de corto plazo: movimiento a 4 h comparable al desvío típico",
                                          "la predicción no supera a «siempre sube» con la muestra disponible"],
        "supuestos": ["velas y predicciones con hora de disponibilidad verificable", "costos de peor caso 0,30 % ida y vuelta"],
        "condiciones_invalidez": ["dato utilizable después del corte", "velas diarias de más de 2 días al corte"],
        "datos_faltantes": ausente, "incertidumbre": "alta: muestra predictiva pequeña" if not any(
            e.medicion.get("ventaja_demostrada") for e in evid if e.modulo.startswith("predictivo")) else "moderada",
        "efectos_noticias": causales or ["sin cobertura de noticias: no se puede evaluar"],
        "riesgos": ["sobreinterpretar n pequeño", "contaminación por información futura (controlada)"],
        "criterios_prueba": ["no aplica: piloto de evaluación, no estrategia"],
        "estado": "INCONCLUSA" if rev["conclusion"] in ("INCONCLUSA", "INSUFICIENTE") else
                  "CONTRADICCION" if rev["conclusion"] == "CONTRADICTORIA" else "INVESTIGACION",
        "contradicciones": rev, "revisiones": [],
        "explicacion_prediccion": {"hechos_comprobados": hechos, "inferencias_fundamentadas": inferencias,
                                   "hipotesis_causales_no_demostradas": causales, "informacion_ausente": ausente,
                                   "decision_de_investigacion": rev["decision_investigacion"],
                                   "naturaleza": "retrospectiva (corte histórico), no prospectiva"},
        "evidencia": [e.como_dict() for e in evid],
        "fuentes": sorted({(f["fuente"], f["hash_sha256"]) for e in evid for f in e.fuentes}, key=str),
        "version_software": VERSION,
    }
    tesis["fuentes"] = [{"fuente": a, "hash_sha256": b} for a, b in tesis["fuentes"]]
    tesis["huella_contenido"] = huella(tesis)
    return tesis


def guardar_instantanea(registros: list[Registro], tesis_id: str, salida: Path) -> Path:
    f = _destino(salida) / f"{tesis_id}.entradas.json"
    f.write_text(json.dumps([r.como_dict() for r in registros], ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return f


def cargar_instantanea(ruta: Path) -> list[Registro]:
    return [Registro(**d) for d in json.loads(Path(ruta).read_text(encoding="utf-8"))]


def _destino(salida: Path) -> Path:
    s = salida.resolve()
    partes = s.as_posix() + "/"
    if any(f"/{x}/" in partes for x in PROHIBIDO):
        raise PermissionError("ATLAS no puede escribir en data/kt002")
    s.mkdir(parents=True, exist_ok=True)
    return s


def guardar(tesis: dict, salida: Path) -> Path:
    f = _destino(salida) / f"{tesis['id']}.json"
    f.write_text(json.dumps(tesis, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return f


def main(argv=None) -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--corte", required=True)
    a.add_argument("--eventos")
    a.add_argument("--salida", default="research/atlas/salidas")
    a.add_argument("--raiz", default=".")
    a.add_argument("--desde-instantanea", help="reproduce una tesis desde sus entradas guardadas")
    o = a.parse_args(argv)
    corte = t(o.corte)
    regs = cargar_instantanea(Path(o.desde_instantanea)) if o.desde_instantanea else obtener(corte, Path(o.raiz), o.eventos)
    tesis = analizar(corte, regs)
    f = guardar(tesis, Path(o.salida))
    if not o.desde_instantanea:
        guardar_instantanea(regs, tesis["id"], Path(o.salida))
    c = tesis["contradicciones"]
    print(json.dumps({"archivo": str(f), "conclusion": c["conclusion"], "decision": c["decision_investigacion"],
                      "estado": tesis["estado"], "huella": tesis["huella_contenido"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
