"""ATLAS · análisis independientes y deterministas. Cada módulo emite su evidencia por separado
(no se ponen de acuerdo); el texto describe hechos e inferencias, nunca órdenes.

Tipos de evidencia: hecho | inferencia | hipotesis_causal | ausente. Dirección: +1 alcista, -1 bajista, 0 neutra.
"""
from __future__ import annotations

import dataclasses as dc
import datetime as dt
import math
import statistics

from .procedencia import Registro, t

# Regla de ATLAS, alineada con el preregistro de KT-002 (Enmienda A: «ninguna p se interpreta como prueba de
# edge»): los datos descriptivos de KT-002 NUNCA bastan. Una señal predictiva cuenta como respaldo solo si hay un
# estudio confirmatorio aprobado (desconfiado + propietario) y registrado aparte, pasado en `aprobaciones`.
ESTUDIOS_CONFIRMATORIOS: dict[str, str] = {}   # modelo -> id del estudio aprobado; hoy vacío
COSTO_IDA_VUELTA = 0.0030      # peor caso de docs/riesgo/MARCO_DE_RIESGO.md
SPREAD_MAX_PCT = 0.05          # % sobre el precio medio; por encima, liquidez insuficiente para la tesis


@dc.dataclass
class Evidencia:
    modulo: str
    afirmacion: str
    tipo: str
    direccion: int
    medicion: dict
    fuentes: list

    def como_dict(self):
        return dc.asdict(self)


def _fuentes(regs: list[Registro]) -> list:
    vistos = {}
    for r in regs:
        vistos.setdefault((r.fuente, r.hash_sha256), {"fuente": r.fuente, "hash_sha256": r.hash_sha256,
                                                       "ultimo_utilizable_utc": r.utilizable_utc})
        vistos[(r.fuente, r.hash_sha256)]["ultimo_utilizable_utc"] = max(
            vistos[(r.fuente, r.hash_sha256)]["ultimo_utilizable_utc"] or "", r.utilizable_utc or "")
    return list(vistos.values())


def _ausente(modulo, regs, motivo):
    return Evidencia(modulo, f"sin datos: {motivo}", "ausente", 0, {}, _fuentes(regs))


def tendencia(velas: list[Registro]) -> Evidencia:
    """Reglas fijas del analista-tendencia (MA50/MA200 diarias, pendiente de MA50 a 10 velas)."""
    ok = [r for r in velas if r.calidad == "validado"]
    if len(ok) < 210:
        return _ausente("tecnico.tendencia", velas, f"{len(ok)} velas diarias cerradas (< 210)")
    c = [r.valor["c"] for r in ok]
    ma = lambda n, fin=None: sum(c[-n if fin is None else -n - fin: None if fin is None else -fin]) / n
    m50, m200, m50p = ma(50), ma(200), ma(50, 10)
    if c[-1] > m200 and m50 > m200 and m50 > m50p:
        reg, d = "ALCISTA", 1
    elif c[-1] < m200 and m50 < m200 and m50 < m50p:
        reg, d = "BAJISTA", -1
    else:
        reg, d = "LATERAL", 0
    return Evidencia("tecnico.tendencia", f"Régimen diario {reg} (cierre {c[-1]:.0f}, MA50 {m50:.0f}, MA200 {m200:.0f})",
                     "hecho", d, {"regimen": reg, "cierre": c[-1], "ma50": round(m50, 2), "ma200": round(m200, 2),
                                  "ma50_hace_10": round(m50p, 2)}, _fuentes(ok))


def volatilidad(velas: list[Registro]) -> Evidencia:
    ok = [r for r in velas if r.calidad != "faltante"]
    if len(ok) < 31:
        return _ausente("tecnico.volatilidad", velas, "menos de 31 velas diarias")
    c = [r.valor["c"] for r in ok][-31:]
    ret = [c[i] / c[i - 1] - 1 for i in range(1, len(c))]
    vol = statistics.stdev(ret) * math.sqrt(365)
    mov4h = statistics.stdev(ret) / math.sqrt(6)  # desvío típico aproximado a 4 h
    return Evidencia("tecnico.volatilidad", f"Volatilidad anualizada 30 d {vol:.1%}; movimiento típico a 4 h ≈ {mov4h:.2%}",
                     "hecho", 0, {"vol_30d_anual": round(vol, 4), "mov_tipico_4h": round(mov4h, 5)}, _fuentes(ok))


def volumen(velas: list[Registro]) -> Evidencia:
    ok = [r for r in velas if r.calidad != "faltante"]
    if len(ok) < 21:
        return _ausente("tecnico.volumen", velas, "menos de 21 velas")
    v = [r.valor["v"] for r in ok]
    rel = v[-1] / (sum(v[-21:-1]) / 20)
    return Evidencia("tecnico.volumen", f"Volumen de la última vela {rel:.2f}× el promedio de 20", "hecho", 0,
                     {"volumen_relativo_20": round(rel, 3)}, _fuentes(ok))


def liquidez(spreads: list[Registro], corte: dt.datetime | None = None, max_edad=dt.timedelta(hours=6)) -> Evidencia:
    ok = [r for r in spreads if r.calidad == "validado"]
    if not ok:
        return _ausente("mercado.liquidez", spreads, "sin mediciones de spread antes del corte")
    if corte is not None and corte - t(ok[-1].utilizable_utc) > max_edad:
        return _ausente("mercado.liquidez", spreads, f"último spread {ok[-1].utilizable_utc}: más de {max_edad} antes del corte")
    s = ok[-1].valor["spread_pct"]
    return Evidencia("mercado.liquidez", f"Spread más reciente {s:.5f} % ({ok[-1].utilizable_utc})", "hecho", 0,
                     {"spread_pct": s, "medido_utc": ok[-1].utilizable_utc, "insuficiente": s > SPREAD_MAX_PCT}, _fuentes(ok))


def _mcnemar_p(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def historial_modelo(preds: list[Registro], modelo: str, aprobaciones: dict | None = None) -> dict:
    """Acierto sin solape (base cada 4 h) usando SOLO resultados conocidos al corte. Descriptivo."""
    filas = [r.valor for r in preds if r.calidad != "faltante" and r.valor.get("actual_ret")]
    filas = [f for f in filas if t(f["base_open_utc"]).astimezone(dt.timezone.utc).hour % 4 == 0]
    hit = [int(float(f[f"{modelo}_hit"])) for f in filas if f.get(f"{modelo}_hit") not in ("", None)]
    sube = [1 if float(f["actual_ret"]) > 0 else 0 for f in filas if f.get(f"{modelo}_hit") not in ("", None)]
    b = sum(1 for h, s in zip(hit, sube) if h == 1 and s == 0)
    c = sum(1 for h, s in zip(hit, sube) if h == 0 and s == 1)
    p = _mcnemar_p(b, c)
    estudio = (aprobaciones if aprobaciones is not None else ESTUDIOS_CONFIRMATORIOS).get(modelo)
    return {"n_sin_solape": len(hit), "aciertos": sum(hit), "siempre_sube_aciertos": sum(sube),
            "mcnemar_p_descriptivo": round(p, 4), "estudio_confirmatorio": estudio, "ventaja_demostrada": bool(estudio)}


def predictivo(preds: list[Registro], aprobaciones: dict | None = None) -> list[Evidencia]:
    ok = sorted((r for r in preds if r.calidad != "faltante"), key=lambda r: t(r.utilizable_utc))
    if not ok:
        return [_ausente("predictivo", preds, "sin predicciones publicadas antes del corte")]
    ult = ok[-1].valor
    out = []
    for m in ("kronos", "timesfm", "kt001"):
        ret = float(ult[f"{m}_ret"])
        h = historial_modelo(ok, m, aprobaciones)
        d = 1 if ret > 0 else -1 if ret < 0 else 0
        out.append(Evidencia(f"predictivo.{m}",
                             f"{m} predice {ret:+.3%} a 4 h desde {ult['base_open_utc']}; historial al corte: "
                             f"{h['aciertos']}/{h['n_sin_solape']} sin solape (siempre sube {h['siempre_sube_aciertos']}), "
                             f"McNemar p={h['mcnemar_p_descriptivo']} (descriptivo, no prueba ventaja)", "inferencia", d,
                             {"ret_predicho": ret, "base_open_utc": ult["base_open_utc"], "run_utc": ult["run_utc"], **h},
                             _fuentes(ok)))
    return out


def eventos(evs: list[Registro]) -> Evidencia:
    ok = [r for r in evs if r.calidad != "faltante" and r.utilizable_utc]  # sin hora verificable: excluido
    if not ok:
        return _ausente("noticias.eventos", evs, (evs[0].nota if evs and evs[0].calidad == "faltante"
                                                  else "ningún evento con hora de publicación verificable"))
    dirs = [r.valor["direccion"] for r in ok]
    return Evidencia("noticias.eventos", f"{len(ok)} eventos antes del corte ({sum(1 for x in dirs if x > 0)} a favor, "
                     f"{sum(1 for x in dirs if x < 0)} en contra); relación causal NO demostrada", "hipotesis_causal",
                     0, {"n": len(ok), "a_favor": sum(1 for x in dirs if x > 0), "en_contra": sum(1 for x in dirs if x < 0),
                         "excluidos_sin_hora": sum(1 for r in evs if r.calidad != "faltante" and not r.utilizable_utc),
                         "hechos": [r.valor["hecho"] for r in ok]}, _fuentes(ok))
