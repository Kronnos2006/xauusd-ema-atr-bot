# Macro Momentum DXY H4 — fase 1 (retorno intrasesión, sin trigger técnico)

## Descartada (2026-08-04) — no pasa el checkpoint, sin ambigüedad de fold marginal

Índice: [[Bienvenido]] · Ver también [[Macro Momentum DXY - fase 1]] (hermana diaria, descartada 2026-08-03) · [[Candidatos futuros]] · [[Objetivo del proyecto - biblioteca de factores]] · [[hypothesis-gate]] · [[Bitácora de decisiones]]

## Contexto

Primer candidato tras el levantamiento de la restricción de intradía (2026-08-04, ver [[Bitácora de decisiones]] y `CLAUDE.md`), motivado por el cierre 0/8 de la ronda de candidatos macro-diarios (ver [[Candidatos futuros]]). Mecanismo: rebalanceos FX intrasesión (aperturas de Londres/Nueva York) se trasladan mecánicamente al precio del oro dentro de la misma sesión — distinto del mecanismo de la versión diaria (movimientos cierre-a-cierre, overnight/multi-sesión). Confirmado explícitamente por el usuario como hipótesis genuinamente distinta, no una variante de menor granularidad del trigger diario ya descartado.

## Hipótesis (frase falsable)

Cuando el retorno del DXY sintético en la vela H4 cerrada supera k desvíos estándar — calculados sobre su propia distribución histórica **rolling de 252 días hábiles** (no el std de la serie completa, a diferencia de la versión diaria) — en valor absoluto, el oro (XAUUSD) tiene sesgo direccional **inverso** al signo de ese movimiento en las M velas H4 siguientes.

**Grilla declarada (3×3, sin resweepeo)**: k∈{0.75, 1.0, 1.25} × M∈{1, 2, 3} velas H4.

## Triage de frecuencia (Fase 0) — con datos reales, no estimados

Medido con `diagnostico_frecuencia_momentum_dxy_h4.py` sobre `historial/dxy_sintetico_h4.csv` (construido con `construir_dxy_sintetico_h4.py`, misma fórmula ICE que la versión D1), restringido a histórico de oro en MT5 (2004-06-11+, 22.1 años; XAUUSD H4 confirmado disponible desde la misma fecha).

| k | Episodios | Episodios/año |
|---|---|---|
| 0.75 | 5197 | 345.89 |
| 1.00 | 4077 | 271.35 |
| 1.25 | 3064 | 203.93 |

La estimación inicial del usuario (~250-400/año) queda confirmada por datos reales, con el extremo más exigente de la grilla (k=1.25) un poco por debajo del piso estimado (204 vs. 250).

Power analysis con el ep/año más restrictivo (k=1.25 = 203.93, el que fija el caso peor de la grilla):

| Referencia de efecto típico | n necesario (80% poder) | Horizonte proyectado |
|---|---|---|
| DFII10 completo (media R=0.230, std R=1.135) | 192 | 0.94 años |
| DXY sintético media (0.182) + std DFII10 (conservador) | 306 | 1.50 años |

**✅ Pasa el triage con margen amplio** en ambos escenarios (muy por debajo del límite de 5 años) — a diferencia de la versión diaria, que ya pasaba pero con más ajuste (4.1 años).

## Folds — derivados de la distribución real, no de frecuencia/K

Chequeo empírico (no asumido uniforme) de episodios por fold sobre el caso más restrictivo (k=1.25, 3064 episodios): **el primer episodio real recién aparece en 2009-02-26**, no en 2004 — los primeros ~4.7 años de histórico post-warmup no producen ni un episodio a k=1.25. La distribución NO es uniforme en el tiempo, igual que ya se vio con otras hipótesis del proyecto — dividir episodios totales/K a ciegas hubiera sido engañoso acá.

| K folds | Fold mínimo | Fold máximo | Margen sobre piso de 30 |
|---|---|---|---|
| 16 | 40 | 303 | +33% |
| 24 | 34 | 202 | +13% (margen fino) |
| 32 | 10 | 164 | **rompe el piso** |
| 40 | 10 | 134 | **rompe el piso** |

**K=16 folds** — mismo número que la versión diaria (coincidencia, no reusado a ciegas: se llegó a él por el mismo criterio, margen sólido sobre el piso de 30, no por copiar el valor). Fold mínimo real: 40 trades (+33% de margen), igual de holgado que el criterio ya aplicado en la hermana diaria (+43%).

## Regla de corte (pre-registrada, igual que la versión diaria)

- \|t-stat\| > 1.96 (α=0.05, dos colas) sobre R neto de TEST, calculado con todos los folds y sin el fold de mayor R neto — la conclusión cualitativa no debe cambiar entre ambos.
- **DSR ≥ 0.95**, contando como N: la grilla completa de esta hipótesis (3×3=9 combinaciones × 16 folds = 144) **más las hipótesis hermanas ya evaluadas sobre DXY sintético** (versión diaria: 2×3=6 combinaciones × 16 folds = 96; versión nivel/caída sostenida de [[Macro DXY - fase 1]]) — subestimar N invalida la corrección, ante la duda se redondea hacia arriba.
- Selección de (k, M) en TRAIN de cada fold, confirmación única en TEST. Umbral congelado en TRAIN (mismo criterio que la versión diaria — el std rolling en cada punto de TEST solo puede usar historia disponible hasta ese punto, no el std calculado con el dataset completo).
- Spread real (`descontar_spread`, `SPREAD_PUNTOS=30`, misma constante del resto del proyecto). H4 tiene más señales que D1 — confirmar que el spread no se vuelve proporcionalmente más caro dado el horizonte de M velas H4 más corto (1-3 velas ≈ 4-12hs) que el de la versión diaria (1-5 sesiones).

## Chequeo de no-reuso de grilla

Confirmado por el usuario: mecanismo distinto (intrasesión Londres/NY vs. cierre-a-cierre overnight), no una variante de menor granularidad del trigger diario ya descartado el 2026-08-03. La grilla (k∈{0.75,1.0,1.25}×M∈{1,2,3} sobre H4) no se solapa con la ya barrida (k∈{0.75,1.0}×M∈{1,3,5} sobre D1).

## Resultado (2026-08-04)

Script: `hipotesis_macro_momentum_dxy_h4.py` (mismo patrón que la hermana diaria, ATR14 en H4, std rolling causal de 252 días hábiles para el umbral).

**❌ NO PASA EL CHECKPOINT** — descartada limpia, en la dirección peor (edge negativo, no solo "no significativo").

| Métrica | Valor |
|---|---|
| Folds evaluables | 13/16 (folds 1-3 sin selección posible en TRAIN — caen casi enteros dentro del warm-up del std rolling de 252 días, reportado explícitamente, no silenciado) |
| Folds rentables (neto de spread) | 3/13 (23%) |
| Trades TEST acumulados | 3049 |
| R neto acumulado | -112.41R |
| t-stat pooled (todos los folds evaluables) | -2.862 (p=0.0042) |
| t-stat sin el fold más fuerte (Fold 6, +11.20R) | -3.266 (p=0.0011) — se vuelve más negativo |
| Deflated Sharpe Ratio (N=276: esta grilla 3×3×16=144 + Momentum DXY diario 2×3×16=96 + DXY nivel/caída sostenida 3×3×4=36) | 0.0000 |

Regla de corte pre-registrada: \|t\|>1.96. Ambos t-stats la superan ampliamente, pero en signo negativo — pierde neto de spread con alta confianza estadística. Sin el fold más fuerte la conclusión se sostiene (empeora). El Sharpe observado (-0.0518) ya es negativo, así que el DSR descarta sin necesidad de invocar la corrección por multiple-comparisons.

Bug encontrado y corregido durante la corrida: `elegir_mejor_km` podía devolver `None` cuando ningún combo de la grilla llegaba al piso de 30 trades en TRAIN, y el código no lo manejaba (`TypeError` al desempaquetar) — pasa en los folds 1-3, donde el TRAIN es más corto que el warm-up del std rolling. Corregido para reportar "sin selección posible" en vez de crashear.

Por la regla de corte fijada de antemano, **no se resweepea la grilla ni se prueba la dirección contraria** ahora que se vio el resultado — eso sería la racionalización post-hoc que `hypothesis-gate` existe para evitar. El mecanismo intrasesión, tal como está definido acá (retorno H4 vs. std rolling de 252 días), queda cerrado; una hipótesis nueva sobre este mismo mecanismo necesitaría una razón *nueva*, no derivada de este resultado, y entraría de nuevo por Fase 0.

## Estado

**Cerrada.** Segundo candidato consecutivo de "momentum DXY" (diario y H4) descartado con edge negativo. Ver [[Bitácora de decisiones]] para el registro consolidado.

## Ver también
[[Macro Momentum DXY - fase 1]] · [[Macro DXY - fase 1]] · [[Candidatos futuros]] · [[Objetivo del proyecto - biblioteca de factores]] · [[hypothesis-gate]] · [[Bitácora de decisiones]]
