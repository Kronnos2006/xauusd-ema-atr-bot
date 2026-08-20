# Plan de investigación: Pares e Índices D1 (Fase 0 y Fase 1)

Índice: [[Bienvenido]] · Ver también [[Criterios de cierre del enfoque]] · [[hypothesis-gate]] · [[Metodología]]

## Estado: Fase 1 Completada con Éxito (2026-08-09)

Se ejecutó el Walk-Forward completo de **Fase 1** sobre 14 años de `US500` en $D1$ (3,583 velas), incorporando los **4 controles obligatorios de corrección metodológica** (Alpha vs Beta, asimetría Long-Only, descuento de swaps nocturnos reales de MT5 y DSR multitrial).

---

## 1. Resultados Línea A: Cointegración de Pares (Fase 0 - Descartada)

Los 6 pares evaluados (`SPY/DIA`, `QQQ/SPY`, `AUDUSD/NZDUSD`, `GLD/SLV`, `LQD/GHYG`, `US500/US30`) resultaron no-cointegrados ($p \ge 0.20$). Línea descartada en Fase 0 por riesgo de *drift* indeterminado.

---

## 2. Resultados Línea B: Walk-Forward Donchian 15d en `US500` D1 (Fase 1)

* **Script**: `hipotesis_indices_d1.py`
* **Muestra**: 14.0 años de historial D1 (2012–2026, 3,583 velas).
* **Parámetros elegidos in-sample en 100% de los folds**: Donchian 15 días, horizonte de salida 20 días, SL 2.0xATR, dirección **`solo_long`**.

### Resultados Out-of-Sample (TEST) en los 4 Folds:

| Fold | Periodo TEST | Trades TEST | R Neto (con Spreads y Swaps) | t-stat TEST | Sharpe Estrategia | Sharpe Benchmark Buy & Hold | Excess Sharpe | Status vs Benchmark |
|---|---|---|---|---|---|---|---|---|
| **Fold 1** | 2015–2018 | 20 | **+12.14R** | +2.176 | 1.29 | 0.80 | **+0.49** | ✅ Supera Benchmark |
| **Fold 2** | 2018–2020 | 23 | **+4.95R** | +0.900 | 0.53 | 0.56 | **-0.03** | ❌ Falla por 0.03 (Recuperación COVID) |
| **Fold 3** | 2020–2023 | 20 | **+5.42R** | +1.003 | 0.60 | 0.53 | **+0.07** | ✅ Supera Benchmark (Bear Market 2022) |
| **Fold 4** | 2023–2026 | 20 | **+14.59R** | +2.773 | 1.64 | 1.30 | **+0.34** | ✅ Supera Benchmark |

### Métricas Agregadas de Validación:
- **R Neto Acumulado**: **+37.11R** en 83 operaciones ($+0.447R$/trade de beneficio neto tras pagar financiamiento diario y spreads).
- **t-stat Pooled**: **+3.416** ($p = 0.00063$, estadísticamente significativo a $p < 0.001$).
- **Dispersión de Fold Dominante**: Fold 4 aporta $39.3\%$ del resultado neto (debajo del límite máximo del $60\%$). Sin el Fold 4, la estrategia conserva **+22.52R neto** en 63 trades.
- **Validación del Filtro Asimétrico (`solo_long`)**: En el 100% de los folds in-sample, la grilla descartó las posiciones cortas por destruir rentabilidad durante picos de volatilidad a la baja.

---

## Ver también
[[hypothesis-gate]] · [[TF_Basket_H1 — Fase 0]] · [[Criterios de cierre del enfoque]] · [[Bitácora de decisiones]]
