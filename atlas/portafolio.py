"""Portafolio simulado ATLAS: riesgo agregado, correlación y límites.

Entradas: rendimientos por período sincronizado, netos de costos por estrategia.
No hay órdenes, dinero, optimizador ni asignación automática de capital real.
"""
from __future__ import annotations
from math import isfinite, sqrt
from statistics import mean

def _corr(a, b):
    if len(a) < 3:
        return None
    ma, mb = mean(a), mean(b)
    va = sum((x-ma)**2 for x in a)
    vb = sum((y-mb)**2 for y in b)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/sqrt(va*vb) if va > 0 and vb > 0 else None

def evaluar_portafolio(rendimientos: dict[str, list[float]], pesos: dict[str, float],
                       limite_peso: float = .35, limite_drawdown: float = .20,
                       limite_correlacion: float = .85) -> dict:
    if not rendimientos or set(rendimientos) != set(pesos):
        raise ValueError("cada estrategia requiere rendimiento y peso")
    n = len(next(iter(rendimientos.values())))
    if n < 3 or any(len(v) != n for v in rendimientos.values()):
        raise ValueError("series desalineadas o muestra insuficiente")
    if any(not isfinite(x) or x <= -1 for v in rendimientos.values() for x in v):
        raise ValueError("rendimiento inválido")
    if any(not isfinite(p) or p < 0 for p in pesos.values()) or abs(sum(pesos.values())-1) > 1e-9:
        raise ValueError("pesos no negativos deben sumar 1")
    if not all(isfinite(z) and 0 <= z <= 1 for z in
               (limite_peso, limite_drawdown, limite_correlacion)):
        raise ValueError("límites inválidos")
    ids = sorted(rendimientos)
    ret = [sum(pesos[k]*rendimientos[k][i] for k in ids) for i in range(n)]
    capital = maximo = 1.0
    max_dd = 0.0
    for r in ret:
        capital *= 1+r
        maximo = max(maximo,capital)
        max_dd = max(max_dd,1-capital/maximo)
    pares = []
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            c = _corr(rendimientos[a],rendimientos[b])
            pares.append({"a":a,"b":b,"correlacion":round(c,6) if c is not None else None})
    alertas = []
    for k,p in pesos.items():
        if p > limite_peso:
            alertas.append(f"concentración: {k} ({p:.1%})")
    if max_dd > limite_drawdown:
        alertas.append(f"drawdown excedido: {max_dd:.1%}")
    for par in pares:
        if par["correlacion"] is not None and abs(par["correlacion"]) > limite_correlacion:
            alertas.append(f"correlación elevada: {par['a']}/{par['b']}")
    return {"periodos":n,"capital_final":round(capital,10),
            "retorno_total":round(capital-1,10),
            "drawdown_maximo":round(max_dd,10),
            "correlaciones":pares,"alertas":alertas,
            "aprobado_riesgo":not bool(alertas),
            "limitacion":"simulación de rendimientos sincronizados; no valida datos, sellos, ejecución ni rentabilidad"}
