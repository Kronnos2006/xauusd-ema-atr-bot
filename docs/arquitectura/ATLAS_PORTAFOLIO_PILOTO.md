# ATLAS Fase 6 — Portafolio simulado (piloto)

Módulo: `atlas/portafolio.py`. Recibe series de rendimientos **ya sincronizadas y netas de costos** junto con pesos hipotéticos. Calcula capital compuesto, drawdown, correlación entre estrategias y alertas por concentración, correlación alta y drawdown.

**Prohibido confundir con gestión operativa:** no ejecuta órdenes, no optimiza pesos, no asigna capital real, no valida sellos, no modela liquidez ni prueba que una estrategia tenga ventaja. Un resultado aprobado significa únicamente que no traspasa los umbrales suministrados en esta simulación.

**Siguiente trabajo:** conector de historial de simulaciones con alineación verificable por periodo, exposición por factor, escenario adverso y pruebas con estrategias preregistradas; revisión independiente antes de integración en ORION.
