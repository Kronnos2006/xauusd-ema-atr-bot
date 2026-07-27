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

## Ver también
[[Infraestructura]] · [[EMA baseline (M15)]] (contexto de por qué se buscó una hipótesis fuera de la familia EMA9/21) · [[Cronología]]
