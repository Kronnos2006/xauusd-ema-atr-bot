"""Puertas estadísticas estrictas, sin estrategias ni acceso a datos de mercado."""
from __future__ import annotations
from math import isfinite, sqrt
from statistics import mean, stdev
from deflated_sharpe import deflated_sharpe_ratio

MIN_OPERACIONES = 30
UMBRAL_DSR = 0.95

def validar_n_total(n_real: int, n_declarado: int) -> int:
    """Rechaza tanto reducción como inflación: el censo es entrada inmutable de auditoría."""
    if isinstance(n_real, bool) or isinstance(n_declarado, bool) or not isinstance(n_real, int) or not isinstance(n_declarado, int):
        raise ValueError("N_total debe ser entero")
    if n_real < 1 or n_declarado != n_real:
        raise ValueError(f"N_total inconsistente: censo={n_real}, declarado={n_declarado}")
    return n_real

def _t_stat(valores: list[float]):
    if len(valores) < 2:
        return None
    sd = stdev(valores)
    return mean(valores) * sqrt(len(valores)) / sd if sd > 0 else None

def evaluar_folds_operaciones(folds: list[list[float]], n_real: int, n_declarado: int,
                              umbral: float = UMBRAL_DSR) -> dict:
    """Solo retornos netos por operación; folds con menos de 30 NO cuentan."""
    n = validar_n_total(n_real, n_declarado)
    if umbral != UMBRAL_DSR:
        raise ValueError("el umbral DSR es fijo (0.95)")
    salida, validos = [], []
    for i, x in enumerate(folds):
        if any(not isfinite(r) or r <= -1 for r in x):
            raise ValueError("retornos netos inválidos")
        ok = len(x) >= MIN_OPERACIONES
        salida.append({"fold":i, "operaciones":len(x), "estado":"VALIDO" if ok else "INVALIDO",
                       "motivo":None if ok else "menos de 30 operaciones"})
        if ok:
            validos.append((i,x))
    if not validos:
        return {"folds":salida,"estado":"INVALIDO","dsr":None,"t_stat":None,
                "t_stat_sin_dominante":None,"fold_dominante":None,"n_total":n,
                "promocion_permitida":False,"pasa_barreras_estadisticas":False}
    # Dominante: fold que aporta mayor estadístico |suma neta|, convención explícita.
    dominante = max(validos,key=lambda z:abs(sum(z[1])))[0]
    con = [r for _,v in validos for r in v]
    sin = [r for j,v in validos if j != dominante for r in v]
    try:
        dsr = deflated_sharpe_ratio(con,n)["deflated_sharpe_ratio"]
        if not isfinite(dsr):
            dsr = None
    except (ValueError,ZeroDivisionError,OverflowError):
        dsr = None
    # Esta API acepta retornos y N proporcionados por el invocador: NO prueba procedencia.\n    # El DSR descriptivo puede ser alto con datos ficticios, pero nunca se etiqueta\n    # como una barrera superada. La evaluación confirmatoria continúa cerrada.\n    aprobado = dsr is not None and dsr >= UMBRAL_DSR
    return {"folds":salida,"estado":"EVALUABLE" if dsr is not None else "INVALIDO",
            "dsr":dsr,"umbral_dsr":UMBRAL_DSR,"t_stat":_t_stat(con),
            "t_stat_sin_dominante":_t_stat(sin),"fold_dominante":dominante,
            "n_total":n,"promocion_permitida":False,"pasa_barreras_estadisticas":False,\n            "dsr_descriptivo_supera_umbral":aprobado,
            "advertencia":"retornos y N_total no verificados externamente: solo análisis descriptivo; ninguna promoción"}
