"""Laboratorio ATLAS: backtest determinista sobre barras ya cerradas.

Research/paper only. Las señales son hipótesis inmutables con timestamps verificables.
La señal disponible durante la barra i se ejecuta recién en apertura de i+1.
Sin órdenes reales, acceso a bolsa, credenciales ni escritura en KT-002.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Sequence


def instante(valor: str) -> datetime:
    d = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("se exige zona horaria explícita")
    return d.astimezone(timezone.utc)


@dataclass(frozen=True)
class Barra:
    apertura_utc: str
    cierre_utc: str
    apertura: float
    cierre: float

    def __post_init__(self):
        if instante(self.apertura_utc) >= instante(self.cierre_utc):
            raise ValueError("barra sin intervalo válido")
        if not all(isfinite(x) and x > 0 for x in (self.apertura, self.cierre)):
            raise ValueError("precio inválido")


@dataclass(frozen=True)
class Senal:
    id: str
    publicada_utc: str
    posicion: int  # -1 corta, 0 efectivo, +1 larga
    preregistro: str
    sello_externo_verificado: bool = False

    def __post_init__(self):
        if self.posicion not in (-1, 0, 1) or not self.id or not self.preregistro:
            raise ValueError("señal inválida")
        instante(self.publicada_utc)


def simular(barras: Sequence[Barra], senales: Sequence[Senal],
            costo_lado: float = 0.0015, capital_inicial: float = 1.0) -> dict:
    """Señales consumidas desde el cierre de barra anterior; operación en siguiente apertura.

    Rendimiento de la posición open->close; sin overnight, para no inventar precios
    ni el costo de huecos entre barras. Costo por entrada y salida en cada barra.
    Benchmark buy-and-hold intrabar con idéntica convención y costos.
    El resultado no es rentabilidad de una cartera ejecutable.
    """
    if not (isfinite(costo_lado) and 0 <= costo_lado < 1):
        raise ValueError("costo inválido")
    if not (isfinite(capital_inicial) and capital_inicial > 0):
        raise ValueError("capital inválido")
    if len(barras) < 2:
        raise ValueError("mínimo dos barras")
    tiempos = [(instante(b.apertura_utc), instante(b.cierre_utc)) for b in barras]
    if any(tiempos[i][1] > tiempos[i + 1][0] for i in range(len(barras) - 1)):
        raise ValueError("barras solapadas o sin orden cronológico")
    if len({s.id for s in senales}) != len(senales):
        raise ValueError("IDs de señales duplicados")
    autorizadas = sorted((s for s in senales if s.sello_externo_verificado),
                        key=lambda s: instante(s.publicada_utc))
    if len(autorizadas) != len(senales):
        raise ValueError("señal sin sello externo verificable")
    efectivo, referencia = capital_inicial, capital_inicial
    maximo, peor_caida = efectivo, 0.0
    historial = []
    for i in range(1, len(barras)):
        # La publicación debe preceder o coincidir con el cierre anterior:
        # no basta con publicarse justo antes de la apertura actual.
        corte = tiempos[i - 1][1]
        elegibles = [s for s in autorizadas if instante(s.publicada_utc) <= corte]
        s = elegibles[-1] if elegibles else None
        posicion = s.posicion if s else 0
        cambio = barras[i].cierre / barras[i].apertura - 1
        # Retorno neto por operación independiente, con costo efectivo en ambos lados.
        factor = (1 + posicion * cambio) * (1 - costo_lado) ** (2 * abs(posicion))
        benchmark_factor = (1 + cambio) * (1 - costo_lado) ** 2
        if factor <= 0 or benchmark_factor <= 0:
            raise ValueError("pérdida excede capital: modelo lineal no válido")
        efectivo *= factor
        referencia *= benchmark_factor
        maximo = max(maximo, efectivo)
        peor_caida = max(peor_caida, (maximo - efectivo) / maximo)
        historial.append({"barra": i, "senal": s.id if s else None,
                          "posicion": posicion, "retorno_bruto": posicion * cambio,
                          "capital_simulado": round(efectivo, 12),
                          "benchmark_capital": round(referencia, 12)})
    return {"periodos": len(historial), "capital_final_simulado": round(efectivo, 12),
            "capital_benchmark": round(referencia, 12),
            "retorno_neto_simulado": round(efectivo / capital_inicial - 1, 12),
            "retorno_benchmark": round(referencia / capital_inicial - 1, 12),
            "max_drawdown_simulado": round(peor_caida, 12),
            "historial": historial,
            "limitaciones": "intrabar, sin financiación/borrow, gaps ni ejecución real; no demuestra ventaja"}
