"""Validación temporal del laboratorio ATLAS, sin optimización ni operaciones.

Los folds separan períodos de calibración y prueba; los resultados del holdout
son descriptivos, nunca habilitan promoción automática de estrategias.
"""
from __future__ import annotations

from dataclasses import dataclass
from .laboratorio import Barra, Senal, instante, simular
from .barreras_estadisticas import evaluar_folds_operaciones, MIN_OPERACIONES, UMBRAL_DSR


@dataclass(frozen=True)
class Fold:
    entrenamiento_inicio: int
    entrenamiento_fin: int
    prueba_inicio: int
    prueba_fin: int


def construir_folds(n: int, entrenamiento: int, prueba: int, paso: int,
                    embargo: int = 1) -> list[Fold]:
    if min(entrenamiento, prueba, paso, embargo + 1) <= 0 or n < entrenamiento + embargo + prueba:
        raise ValueError("configuración temporal insuficiente")
    folds = []
    inicio = 0
    while inicio + entrenamiento + embargo + prueba <= n:
        fin_ent = inicio + entrenamiento
        inicio_pr = fin_ent + embargo
        folds.append(Fold(inicio, fin_ent, inicio_pr, inicio_pr + prueba))
        inicio += paso
    return folds


def evaluar_fuera_muestra(barras: list[Barra], senales: list[Senal],
                          entrenamiento: int, prueba: int, paso: int,
                          embargo: int = 1, costo_lado: float = 0.0015) -> dict:
    """Señales externas congeladas. Entrenamiento no ajusta parámetros: NO es walk-forward completo."""
    if not barras:
        raise ValueError("sin barras")
    for i, b in enumerate(barras):
        if i and instante(barras[i - 1].cierre_utc) > instante(b.apertura_utc):
            raise ValueError("barras desordenadas")
    folds = construir_folds(len(barras), entrenamiento, prueba, paso, embargo)
    salidas = []
    for f in folds:
        bloque = barras[f.prueba_inicio - 1:f.prueba_fin]
        # No se permite usar señales que se publiquen después del cierre de prueba.
        cierre_final = instante(barras[f.prueba_fin - 1].cierre_utc)
        candidatas = [s for s in senales if instante(s.publicada_utc) <= cierre_final]
        resultado = simular(bloque, candidatas, costo_lado=costo_lado)
        salidas.append({
            "entrenamiento": [f.entrenamiento_inicio, f.entrenamiento_fin],
            "embargo": [f.entrenamiento_fin, f.prueba_inicio],
            "prueba": [f.prueba_inicio, f.prueba_fin],
            "retorno_neto": resultado["retorno_neto_simulado"],
            "retorno_referencia": resultado["retorno_benchmark"],
            "max_drawdown": resultado["max_drawdown_simulado"],
            "periodos": resultado["periodos"],
        })
    return {"folds": salidas, "total_folds": len(salidas),
            "superan_referencia": sum(x["retorno_neto"] > x["retorno_referencia"] for x in salidas),
            "metodologia": "evaluación fuera de muestra de señales fijas; sin entrenamiento automático ni estadística confirmatoria",
            "restriccion": "ninguna promoción automática, ni afirmación de rentabilidad"}


def evaluar_confirmatorio(folds_operaciones: list[list[float]], n_total_real: int,
                          n_total_declarado: int, senales: list[Senal],
                          repo: str, referencias: dict[str,tuple[str,str]],
                          obtener_anclas=None, leer_git=None) -> dict:
    """Puerta estricta adicional. No usa los folds de barras retrospectivos como resultado confirmatorio.

    Los retornos por operación deben provenir de una fuente pre-registrada y auditada;
    este método no genera señales, variantes ni métricas de ningún experimento.
    """
    # FAIL-CLOSED: los retornos recibidos y N_total son parámetros arbitrarios.
    # Un sello de señales NO demuestra procedencia de retornos ni censo exhaustivo.
    # No se calculará DSR confirmatorio ni se autorizará promoción hasta que
    # ambas entradas se deriven de artefactos inmutables auditables.
    raise ValueError(
        "confirmatorio bloqueado: falta vincular retornos a señales selladas "
        "y derivar N_total de un censo independiente verificable"
    )
