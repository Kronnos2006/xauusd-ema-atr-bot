# Macro DFII10 — fase 1 (tasas reales, sin trigger técnico)

Índice: [[Bienvenido]] · Ver también [[Metodología]] · [[Errores y bugs corregidos]]

## Contexto

Primera hipótesis nueva desde el retiro de la familia EMA9/21 crossover (ver [[Bienvenido]]). Cumple la regla del proyecto de definir frase falsable + regla de corte propias antes de arrancar.

## Hipótesis (frase falsable)

Caída sostenida de N días en DFII10 (tasa real de EE.UU. a 10 años, TIPS) → sesgo alcista en M sesiones de oro. Es una hipótesis puramente macro, sin trigger técnico de confirmación en esta fase 1 — la fase 2 (si se llega) agregaría confirmación técnica de entrada.

## Metodología

1. **Chequeo de frecuencia previo**: 291/177/132 episodios para N=20/60/120 días, restringido a la ventana real de datos disponible en MT5.
2. **Walk-forward de 4 folds** (ajustado para esta hipótesis por el piso de 30 trades/fold — con episodios más escasos que cruces EMA, 4 folds en vez de los 9 habituales) sobre grilla 3×3 (barrido de N × M).
3. **Verificación cruzada de la fuente de datos**: FRED DFII10 vs. home.treasury.gov, para descartar error de dato macro.

Config final (N=60, M=5) es la ganadora del walk-forward exploratorio — fija para el logger en vivo, no se vuelve a elegir mirando datos nuevos.

## Resultado (2026-07-24)

**Pasa el checkpoint** (3/4 folds rentables, sin fold dominante que concentre el resultado), pero con reservas documentadas:

- **t-stat pooled marginal: p=0.059** — cerca del umbral convencional (0.05) pero no lo cruza limpiamente.
- **Sin el fold más fuerte, p cae a 0.30** — la significancia depende sustancialmente de un solo fold.
- **Un fold perdedor está ligado a un régimen de tasas ascendente identificable (2013-2017)** — posible régimen-dependencia, no ruido puro, pero tampoco confirma que la hipótesis funcione "siempre".

**Conclusión: no lista para fase 2 ni demo.** No se lleva a ejecución ni se diseña la confirmación técnica de fase 2 todavía — necesita más evidencia antes de invertir en la siguiente capa.

## Holdout en vivo (logger, commit `37d4987`, 2026-07-24)

Se desplegó `log_senal_macro_dfii10.py` en modo **logging puro** (misma disciplina que el logger EMA — no ejecuta órdenes), para que la próxima confirmación venga de datos genuinamente nuevos hacia adelante y no de otra vuelta de análisis retrospectivo sobre el mismo tramo 2003-2026 (evita reabrir el riesgo de comparaciones múltiples ya evitado en el resto del proyecto).

Reutiliza `detectar_inicios_episodio()` de `hipotesis_macro_dfii10.py` sin reimplementarla. Config fija (N=60, M=5, la ganadora del walk-forward). Desplegado como tarea de Task Scheduler (`LogonType Interactive`, mismo patrón que la tarea EMA productiva) — ver [[Infraestructura]].

Punto de partida del logger: 2026-07-23, sin backfillear episodios históricos como pendientes (`estado_macro_dfii10.json`) — resguardo deliberado contra tomar un episodio viejo como señal fresca al primer arranque, ver [[Errores y bugs corregidos]].

**Sin episodios acumulados aún (verificado 2026-07-27)**: `senal_macro_dfii10_live.csv` sigue con 0 filas de datos, ~4 días desde el arranque — esperable dada la baja frecuencia de episodios N=60 (piso de referencia ~132-291 episodios en más de 20 años de historia), no un síntoma de falla.

**Monitor de conveniencia agregado (2026-07-27)**: tarea diaria de Task Scheduler (`XAUUSD_MacroDFII10_HoldoutMonitor`, ver [[Infraestructura]]) avisa con una notificación toast apenas el CSV sume una fila nueva — así el usuario no tiene que revisar el archivo a mano mientras se acumulan los episodios necesarios para volver a evaluar el checkpoint.

## Auditoría de robustez (2026-07-27) — antes de seguir acumulando holdout

Cuatro verificaciones adicionales sobre los 87 trades TEST del walk-forward, pedidas explícitamente antes de invertir más tiempo esperando datos nuevos.

### 1. Costos de transacción — confirmado, ya estaban incluidos

`descontar_spread` (con `SPREAD_PUNTOS=30`, la misma constante que usa toda la familia EMA9/21, sin override en el script de DFII10) ya se aplicaba desde el resultado original — no fue necesario "descubrir" un costo nuevo. Recalculado en `metricas_dfii10.py`: **n=87, t=+1.887, p=0.0591** (pooled) y **n=63, t=+1.034, p=0.3011** (sin Fold 4, que concentra 51% del R neto). Idéntico a lo ya documentado — la hipótesis sobrevive este chequeo sin cambios, porque nunca estuvo evaluada en bruto.

### 2. Look-ahead por revisión de datos (ALFRED) — confirmado, sin contaminación

Comparado el valor DFII10 "tal como se publicó entonces" (ALFRED, `vintage_date` ~10 días después de cada fecha, tiempo suficiente para que el dato ya estuviera publicado) contra el valor actual de FRED, en 9 fechas: los 7 inicios de episodio de la muestra espaciada N=60 (2003-03-31, 2005-10-19, 2009-07-31, 2014-02-07, 2017-07-31, 2022-08-03, 2026-04-28) más 2 puntos de comparación t-60 días hábiles (2013-11-15, 2022-05-11). **Coincidencia exacta en las 9 fechas, sin ninguna diferencia.** Consistente con que DFII10 es una serie calculada directamente de la curva de rendimiento real del Tesoro (metodología de mercado, publicada una sola vez), no sujeta a revisión tipo benchmark como PBI o nómina no agrícola. La hipótesis sobrevive este chequeo — no hay look-ahead bias por datos revisados.

### 3. Métricas duras (`metricas_dfii10.py`, sobre los 87 trades TEST, neto de spread)

Traducción de R-múltiplos a curva de equity asumiendo 1% de riesgo de capital por trade (convención de reporte, no un tamaño de posición ya decidido para el proyecto), trades ordenados cronológicamente (los 4 folds TEST son bloques disjuntos y consecutivos, así que concatenarlos en orden preserva el orden real).

| Métrica | Valor |
|---|---|
| Período cubierto | 17.4 años (87 trades) |
| Trades/año | 5.01 |
| Win rate | 54.0% |
| Expectancy | +0.230R/trade |
| Profit factor | 1.67 |
| Sharpe anualizado (1% riesgo/trade) | 0.453 |
| Sortino anualizado | 1.388 |
| CAGR equivalente (1% riesgo/trade, compuesto) | +1.12%/año |
| Máximo drawdown | -6.09% |
| Equity final (desde 1.0) | 1.214 |

El drawdown es bajo y el profit factor >1, pero el Sharpe anualizado (0.45) está lejos del umbral típico de "edge fuerte" (≥1) y el CAGR equivalente a 1% de riesgo es modesto (+1.12%/año) — consistente con una señal débil y marginal, no con un edge robusto disfrazado de p-value alto.

### 4. Power analysis — el hallazgo más importante de esta auditoría

Con el efecto ya observado (media R neto = +0.230, desvío = 1.135), el tamaño de muestra necesario para 80% de poder estadístico a α=0.05 (dos colas) es **n=192**. Con 87 trades ya acumulados, faltan **105 trades adicionales**. A la frecuencia esperada de episodios N=60 (~8/año, ver `diagnostico_frecuencia_dfii10.py`), eso son **~13.1 años adicionales** de holdout en vivo — no 2, no 5: más de una década.

**Esto cambia el marco de la decisión**: seguir acumulando holdout pasivamente al ritmo actual no es un plan viable para llegar a una confirmación estadísticamente sólida en un plazo razonable. O se acepta operar (si se opera) con una lectura estadística que probablemente seguirá siendo marginal por muchos años, o se reconsidera si esta hipótesis puntual (N=60, M=5) es el mejor uso del tiempo de holdout, dado el tamaño de efecto ya observado.

**Ningún punto de esta auditoría mata la hipótesis por sí solo** (spread ya incluido, sin look-ahead, drawdown/profit factor razonables) — pero el power analysis deja claro que "esperar a que se acumulen más datos" tiene un horizonte de tiempo mucho más largo de lo que parecía antes de calcularlo explícitamente.

## Ver también
[[Infraestructura]] · [[EMA baseline (M15)]] (contexto de por qué se buscó una hipótesis fuera de la familia EMA9/21) · [[Cronología]] · [[Checklist paso a cuenta demo]]
