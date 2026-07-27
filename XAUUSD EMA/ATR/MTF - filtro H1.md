# MTF — filtro de tendencia H1

Índice: [[Bienvenido]] · Ver también [[EMA baseline (M15)]] · [[H1 retuneado]] · [[Metodología]] · [[Cronología]]

## Hipótesis

Reemplazar el filtro de tendencia propio de M15 (close vs EMA50 en M15) por tendencia calculada en H1 (close vs EMA50 en H1), manteniendo intacto el trigger de entrada (cruce EMA9/21 en M15). Experimento de una sola variable sobre el baseline.

## Implementación

Funciones nuevas en `Backtest ema v4.py`: `bajar_datos_rango` (`mt5.copy_rates_range` anclado a fechas reales, no a N de velas), `calcular_tendencia_h1`, `alinear_h1_a_m15` (`merge_asof(direction="backward")` sobre `valido_desde = time_H1 + 1h`, para nunca usar una vela H1 todavía en formación), `generar_senales_mtf`.

Bug encontrado y corregido: `merge_asof` fallaba con `MergeError` por incompatibilidad `datetime64[s]` vs `datetime64[us]` — sumar un `Timedelta` a la columna `time` sube la resolución interna en pandas 2.x. Fix: castear ambas claves de merge a `datetime64[ns]` explícitamente.

## Resultado (walk-forward de 9 folds anclados, 2026-07-23)

- 5/9 folds rentables neto (mismo conteo que baseline), pero R total promedio cayó a **+0.11R/fold**.
- Solo 220 trades TEST acumulados (~33% menos que baseline — esperable, filtro más estricto).
- **R neto total agregado NEGATIVO: -3.79R** en 9 folds; sin el fold más fuerte, -11.31R en 193 trades.

## Conclusión

El filtro de tendencia H1 no filtró mejor el ruido de M15: filtró señales en general, sin mejorar la calidad de las que dejó pasar. Descartado — no vale la pena iterar con H4 u otro múltiplo de EMA en el mismo enfoque (close vs EMA de tendencia en timeframe mayor) sin una razón nueva para creer que cambiaría el resultado.

Nota de diagnóstico posterior: el fold que fue el peor de baseline (15/01→03/03) resultó el **mejor** fold de MTF sobre el mismo período y prácticamente el mismo pool de señales — ver [[EMA baseline (M15)]]#Diagnóstico-de-inestabilidad, evidencia de que el problema es el trigger EMA9/21, no el filtro de tendencia.
