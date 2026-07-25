XAUUSD EMA/ATR — Proyecto de validación de estrategia

Proyecto de investigación sistemática sobre si existe un edge operable en XAUUSD (oro) vía MetaTrader 5, con foco en la validación estadística honesta antes de considerar cualquier capital real. No ejecuta órdenes. No hay capital real involucrado en ningún punto de este proyecto.

Estado actual

Sin hipótesis activa. La familia de estrategias basada en el cruce EMA9/21 fue evaluada en cinco variantes distintas y retirada tras fallar de forma convergente bajo un estándar de validación honesto (walk-forward multi-fold, separación TRAIN/TEST estricta, chequeo de que el resultado no dependa de un solo fold). D1 fue descartado como candidato siguiente por tener un techo de información estructuralmente bajo para este activo. El logger de señales en vivo (solo lectura, sin ejecución) sigue corriendo para acumular datos frescos mientras se define la próxima hipótesis.

Metodología

Todo resultado en este repo sigue esta disciplina, sin excepciones:

Train/test separado antes de tocar parámetros. Ningún parámetro se elige mirando el mismo dato que después lo confirma.
Walk-forward multi-fold, no un solo split — un split único puede mostrar el mejor caso posible por pura suerte de calendario.
Chequeo de fold dominante. Antes de confiar en un resultado agregado, se recalcula excluyendo el mejor fold. Si el signo cambia, el resultado no es real.
Diagnóstico entrada-vs-salida cuando una estrategia falla, para no rediseñar a ciegas: se fija la entrada, se barre el R:R solo en TRAIN, y se confirma en TEST.
Reglas de corte definidas antes de correr el experimento — cuántos intentos se prueban antes de descartar un enfoque, decidido de antemano, no ajustado sobre la marcha.
Commit antes de que exista dato fresco — el código de logging en vivo se congela en git antes del primer dato real, como garantía de que la lógica no se ajustó mirando resultados.

Esta metodología está empaquetada como skill reutilizable (trading-strategy-validation) para aplicarse a cualquier hipótesis futura, en este proyecto o en otros.

Resultados — hipótesis probadas
Hipótesis	Folds rentables	Resultado agregado	Veredicto
M15 baseline (cruce EMA9/21 + EMA50)	5/9	Sin el fold dominante: t≈0.6, no significativo (294 trades)	Sin edge confirmado
Filtro multi-timeframe (tendencia H1)	5/9	-3.79R neto (220 trades)	Descartada
Filtro de estructura (HH/HL)	3/9	Sin el fold dominante: -2.35R	Descartada
Trigger ruptura + retest	5/9	Agregado negativo, sin fold que lo sostenga	Descartada
H1 retuneado (SL/R:R propios)	4/9	-23.22R neto (341 trades); t-stat decayendo con más datos	Descartada
D1 (~11 años)	—	Solo 77 trades totales	Descartado por tamaño de muestra estructural

Hallazgo más informativo: el diagnóstico entrada-vs-salida mostró que el baseline M15 sí tenía un edge de entrada genuino (89% de persistencia en TEST), pero el resultado seguía concentrado en un solo fold. Intentar arreglarlo con partial close + trailing stop (probado con el mismo rigor TRAIN-elige/TEST-confirma) empeoró todo — de +14.08R en 7/9 folds pasó a -8.05R en 3/9 folds. Esto disparó la regla de corte pre-registrada y cerró el capítulo. Lectura de conjunto: el edge probablemente montaba la tendencia macro puntual del activo (XAUUSD +210% en 2016-2026), no algo que el cruce EMA predijera por sí mismo.

Detalle completo, incluyendo bugs metodológicos corregidos durante el proceso, en Informe_Proyecto_EMA_XAUUSD.md.

Estructura del repo
Scripts de backtest — walk-forward, split train/test, barrido de R:R y trailing, descuento de spread, diagnóstico entrada-vs-salida.
log_senales_demo.py — logger de señales en vivo, solo lectura. Reutiliza (import directo) la lógica de generación de señales del backtest validado, para evitar drift entre lo testeado y lo que corre en vivo. Loop cada 30s sobre M15, escribe a CSV: precio teórico, bid/ask real de MT5, spread real, y desvío en R entre ambos.
Informe_Proyecto_EMA_XAUUSD.md — informe de estado completo (rentabilidad/validación + infraestructura).

Los .log y .csv generados en vivo están en .gitignore — son datos, no código, y quedan fuera del historial de git.

Infraestructura

El logger corre como tarea programada de Windows (Task Scheduler). Tuvo un incidente de downtime (~4hs) por el modo de sesión configurado originalmente; la resolución (migración a logon tipo S4U, validado con MT5 conectando en sesión no interactiva) está documentada en el informe de estado.

Próximos pasos

El proyecto no avanza a una hipótesis nueva sin que esta tenga: (1) una frase concreta y falsable de qué señal se prueba, y (2) su propia regla de corte definida antes de tocar código — el mismo estándar que ya se aplicó en todo lo anterior.

Sin ejecución de órdenes automática. Sin capital real. Proyecto de investigación y validación únicamente.
