# EMA baseline (M15) — cruce EMA9/21 con filtro EMA50 + ATR

Índice: [[Bienvenido]]

## Hipótesis

Cruce EMA9/21 en M15, filtrado por tendencia (close vs EMA50 en M15), SL basado en ATR14 (1.5×ATR), TP en múltiplo R:R. Es el trigger original del proyecto, base de todas las demás variantes probadas.

## Metodología

Walk-forward anclado de 9 folds sobre 15.000 velas M15 (~2 años). Cada fold selecciona R:R / trailing / filtro de sesión usando solo su TRAIN (barrido de ~20+ combinaciones), evalúa una única vez en su TEST. Selección por `metrica_robusta` (t-stat sobre R neto de spread, piso de 30 trades/fold).

## Resultados

### Walk-forward original (commit `2e4832e`, 2026-07-22)
5/9 folds rentables neto de spread, pero el fold más fuerte concentra ~51% del R neto acumulado; sin ese fold, t≈0.6 sobre 294 trades — no significativo, indistinguible de ruido.

### Re-corrida de referencia (2026-07-23, comparando contra [[MTF - filtro H1]] y [[Estructura de swings (HH-HL)]])
5/9 folds rentables neto, R total promedio +3.94R/fold, 326 trades TEST acumulados, fold dominante 53% del R neto (consistente con el 51% anterior).

### Diagnóstico de inestabilidad (2026-07-23/24)
Se sospechó que la falta de coincidencia entre folds dominantes de las 3 variantes de tendencia era ruido de muestra chica. Se re-corrió con N_FOLDS=4 (folds ~2x más largos, 41-86 trades/fold, ya no hay problema de muestra chica). Resultado: **el patrón de inestabilidad se sostuvo e incluso empeoró** — un mismo período calendario (15/01→03/03) fue el peor fold de Baseline (-19.57R) y el mejor de MTF (+6.71R) al mismo tiempo. Confirma que el problema es el trigger EMA9/21 en sí, no el largo de fold ni el filtro de tendencia.

### Diagnóstico entrada vs. salida y chequeo de partial/trailing (2026-07-24) — regla de corte disparada
El hallazgo más informativo de todo el proyecto: Baseline mostró el primer edge de entrada genuino visto en el proyecto (89% de persistencia en TEST), pero concentrado en un solo fold — y la gestión de salida con partial/trailing, en vez de mejorarlo, lo empeoró (R neto total se dio vuelta de +14.08R a -8.05R), dando negativo por la regla de corte pre-registrada. Detalle completo, con la lectura de por qué probablemente pasó esto, en [[Diagnóstico entrada-vs-salida]].

## Conclusión

Se para el enfoque de entrada técnica pura (cruce EMA + variantes de filtro/trigger) en M15/XAUUSD tal como fue explorado. **Encuadre correcto**: esto NO es "el proyecto fracasó" — es la regla de corte pre-registrada funcionando exactamente como fue diseñada, evitando 6-7 iteraciones más de diseño sobre una premisa ya descartada con datos. Hallazgo válido: "M15 técnico puro no tiene edge confirmable".

## D1

Considerado y pospuesto (no descartado): con `copy_rates_range` sobre MT5 real se confirmó 11+ años de historial D1 disponible, pero solo 77 trades totales en 9 folds — muy por debajo del piso de 30/fold. No es falta de datos disponibles, es que 10 bloques de ~300 velas (~14 meses c/u) es una ventana demasiado corta para juntar cruces EMA9/21 suficientes en diario. Extender el histórico antes de 2008 arriesgaría mezclar regímenes de mercado no comparables (patrón oro / transición) — ver decisión final en [[Bienvenido]].

## Ver también
[[Metodología]] · [[Diagnóstico entrada-vs-salida]] · [[MTF - filtro H1]] · [[Estructura de swings (HH-HL)]] · [[Ruptura y retest]] · [[H1 retuneado]] · [[Infraestructura]] (logger `log_senales_demo.py` sigue corriendo sobre este baseline, sin cambios)
