"""Conexión estricta de resultados del laboratorio a portafolio y estrés simulado."""
from __future__ import annotations
from math import isfinite
from .portafolio import evaluar_portafolio

def conectar_historiales(historiales: dict[str, list[dict]]) -> dict[str, list[float]]:
    """Extrae retornos de capital sucesivos; obliga alineación por barra y evita rellenar huecos."""
    if not historiales:
        raise ValueError("sin historiales")
    claves = None
    salida = {}
    for nombre, filas in historiales.items():
        if not filas or any("barra" not in x or "capital_simulado" not in x for x in filas):
            raise ValueError("historial incompleto")
        ids = [x["barra"] for x in filas]
        if len(set(ids)) != len(ids) or ids != sorted(ids):
            raise ValueError("barras duplicadas o desordenadas")
        if claves is None:
            claves = ids
        elif ids != claves:
            raise ValueError("series no alineadas por barras")
        anterior = 1.0
        retiros = []
        for fila in filas:
            actual = float(fila["capital_simulado"])
            if not isfinite(actual) or actual <= 0:
                raise ValueError("capital inválido")
            retiros.append(actual / anterior - 1)
            anterior = actual
        salida[nombre] = retiros
    return salida

def evaluar_escenarios(rendimientos: dict[str,list[float]], pesos: dict[str,float],
                       choques: dict[str,dict[str,float]], **limites) -> dict:
    """Aplica choques aditivos conservadores a cada período. No modela colas reales."""
    if not choques:
        raise ValueError("se requieren escenarios")
    base = evaluar_portafolio(rendimientos, pesos, **limites)
    casos = {}
    for nombre, perturbacion in choques.items():
        if set(perturbacion) - set(rendimientos):
            raise ValueError("choque de estrategia desconocida")
        series = {}
        for estrategia, vals in rendimientos.items():
            shock = float(perturbacion.get(estrategia, 0))
            if not isfinite(shock):
                raise ValueError("choque inválido")
            series[estrategia] = [x + shock for x in vals]
        casos[nombre] = evaluar_portafolio(series, pesos, **limites)
    return {"base": base, "escenarios": casos,
            "pasa_todos": base["aprobado_riesgo"] and all(
                x["aprobado_riesgo"] for x in casos.values()),
            "advertencia": "escenarios hipotéticos; aprobación de límites no demuestra robustez de mercado"}

def ejecutar_cartera(historiales, pesos, choques, **limites):
    return evaluar_escenarios(conectar_historiales(historiales), pesos, choques, **limites)
