# Risk-off US500 H4 — fase 1 (renta variable como driver de refugio)

## No pasa el checkpoint (2026-08-04) — positivo pero sin significancia estadística

Índice: [[Bienvenido]] · Ver también [[Candidatos futuros]] · [[Objetivo del proyecto - biblioteca de factores]] · [[hypothesis-gate]] · [[Bitácora de decisiones]] · [[Criterios de cierre del enfoque]]

## Contexto

Tercer candidato de la ronda intradía (2026-08-04), y el primero con un **driver externo distinto de DXY** — DXY quedó excluido como driver tras 2 fallos consecutivos (ver [[Criterios de cierre del enfoque]], NO HACER). Mecanismo: caída intradía en renta variable (risk-off) → flujo hacia oro como refugio — el mecanismo flight-to-safety más documentado económicamente, sin solapar con tasas ([[Macro DFII10 - fase 1]], archivado) ni con divisas (DXY, excluido). Comparado contra el spread de crédito HY/IG (ratio GHYG/LQD), que se descartó en el triage de Fase 0 (31.83 ep/año, horizonte 6.03-9.61 años, supera el límite de 5 — ver [[Candidatos futuros]]).

## Hipótesis (frase falsable)

Cuando el retorno del US500 en la vela H4 cerrada **cae** más de k desvíos estándar de su propia distribución histórica (std sobre la serie completa disponible, 2012-08-06+, sin rolling — mismo patrón de Fase 0 que el resto de los candidatos, no el rolling especial que solo se usó para Momentum DXY H4) — **direccional por diseño, solo caídas cuentan, una suba de US500 no es la condición testeada** — el oro (XAUUSD) tiene sesgo **alcista** en las M velas H4 siguientes.

**Grilla declarada (3×3, sin resweepeo)**: k∈{0.75, 1.0, 1.25} × M∈{1, 2, 3} velas H4.

A diferencia de los candidatos DXY (dirección determinada por el signo del retorno disparador — compra o venta según hacia dónde se mueve DXY), acá la dirección de la operación es **siempre COMPRA** — no es un parámetro de la grilla, está fijado por la frase falsable (risk-off → refugio, nunca al revés).

## Triage de frecuencia (Fase 0) — con datos reales

Medido sobre `historial/us500_h4.csv` (US500, CFD de este broker, 16897 velas H4). Historia real desde 2012-08-06 — **no es un límite de `maxbars` del pipeline** (como pasó con XAUUSD H1), es que el broker no tiene el instrumento antes de esa fecha. 14.0 años disponibles, menos que los 22.1 de los candidatos DXY.

| k | Episodios | Episodios/año |
|---|---|---|
| 0.75 | 1517 | 108.41 |
| 1.00 | 1140 | 81.47 |
| 1.25 | 880 | 62.89 |

Power analysis con el ep/año más restrictivo (k=1.25 = 62.89):

| Referencia de efecto típico | n necesario (80% poder) | Horizonte proyectado |
|---|---|---|
| DFII10 completo (media R=0.230, std R=1.135) | 192 | 3.05 años |
| DXY sintético media (0.182) + std DFII10 (conservador) | 306 | **4.87 años** |

**✅ Pasa el triage, pero con margen mucho más fino** que los candidatos DXY H4 (0.94-1.50 años) o XAUUSD H1 (0.38-0.60 años) — con la referencia conservadora, a solo ~0.13 años del límite de 5 que dispara el criterio 1 de [[Criterios de cierre del enfoque]] ("horizonte sistemáticamente largo").

## Folds — derivados de la distribución real

Chequeo empírico sobre el caso más restrictivo (k=1.25, 880 episodios, 2012-08-23 → 2026-07-29):

| K folds | Fold mínimo | Fold máximo | Margen sobre piso de 30 |
|---|---|---|---|
| 8 | 36 | 194 | +20% |
| 10 | 32 | 163 | +7% (margen fino) |
| 12 | 30 | 167 | 0% (justo en el piso) |
| 14 | 17 | 125 | **rompe el piso** |
| 16 | 10 | 126 | **rompe el piso** |

**K=8 folds** — menos que los 16 usados en los candidatos DXY, consecuencia directa de tener 14 años de historia (no 22) y menor frecuencia (63/año vs. 200+/año). Fold mínimo real: 36 trades (+20% de margen) — margen más ajustado que en los candidatos anteriores, pero sólido.

## Regla de corte (pre-registrada)

- \|t-stat\| > 1.96 (α=0.05, dos colas) sobre R neto de TEST, con todos los folds y sin el fold de mayor R neto — la conclusión cualitativa no debe cambiar.
- **DSR ≥ 0.95**, N = esta grilla (3×3×8=**72**, no 24 — error de cálculo corregido tras correr el script, que sí usó el N correcto) — **sin sumar hermanas de DXY o crédito**: el driver (renta variable) es genuinamente nuevo en este proyecto, sin variantes de diseño similar ya evaluadas que deban contarse.
- Selección de (k, M) en TRAIN de cada fold, confirmación única en TEST.
- Spread real (`descontar_spread`, `SPREAD_PUNTOS=30`).
- Entrada D+1 (primera vela H4 de oro tras el inicio del episodio), riesgo = ATR14 H4 × `SL_ATR_MULT`, salida = horizonte M o SL, lo que ocurra primero. Sin pyramiding. Mismo patrón que los candidatos DXY, dirección fija (compra) en vez de determinada por signo.

## Chequeo de no-reuso de grilla

N/A — primer candidato de este driver (renta variable) en el proyecto. No hay grilla previa que se solape.

## Resultado (2026-08-04)

Script: `hipotesis_riskoff_us500_h4.py` (mismo patrón que las hipótesis DXY, std del umbral congelado en TRAIN por fold — no el std de la serie completa que usó solo el chequeo de Fase 0 —, ATR14 H4, dirección fija compra).

**❌ NO PASA EL CHECKPOINT** — resultado positivo pero sin significancia estadística, dependiente en buena parte de un solo fold.

| Métrica | Valor |
|---|---|
| Folds evaluables | 8/8 |
| Folds rentables (neto de spread) | 5/8 (62.5%) |
| Trades TEST acumulados | 802 |
| R neto acumulado | +34.87R |
| t-stat pooled (todos los folds) | +1.525 (p=0.1271) |
| t-stat sin el fold más fuerte (Fold 8, +15.62R = 45% del total) | +0.921 (p=0.3570) |
| Deflated Sharpe Ratio (N=72: grilla 3×3×8) | 0.1806 |

Regla de corte pre-registrada: \|t\|>1.96. Ni con todos los folds ni sin el más fuerte se cruza el umbral — más débil incluso que el precedente marginal de DFII10 (p=0.059, DSR=0.37). Casi la mitad del R neto depende de un solo fold (Fold 8); sin él, el R/trade promedio cae de +0.043 a +0.028. El DSR (0.18) confirma que, contando las 72 variantes de la grilla, el Sharpe observado está muy por debajo del esperable con esa cantidad de intentos.

Por la regla de corte fijada de antemano, no se resweepea la grilla ni se ajusta el diseño ahora que se vio el resultado.

## Estado

**Cerrada — no pasa.** Primer candidato de esta ronda con resultado positivo (no negativo como los dos DXY), pero insuficiente para pasar la barra estadística. Ver [[Bitácora de decisiones]] para el registro consolidado y [[Candidatos futuros]] para la tabla comparativa de la ronda.

## Ver también
[[Candidatos futuros]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]] · [[hypothesis-gate]] · [[Bitácora de decisiones]]
