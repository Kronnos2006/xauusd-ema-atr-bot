# Errores y bugs corregidos

Índice: [[Bienvenido]] · Ver también [[Metodología]] · [[Cronología]]

Todos los errores metodológicos y de código detectados en el proyecto, con su causa y su fix. Ordenados cronológicamente.

## `UnicodeEncodeError` al imprimir en consola Windows (2026-07-21, commit `354eea5`)

**Síntoma**: el script se colgaba al imprimir emojis en consola Windows (codepage cp1252), lo cual impedía que se guardaran los CSV de resultados.

**Fix**: `sys.stdout.reconfigure(encoding="utf-8")` al arranque de `Backtest ema v4.py`.

## Señales sesgadas durante el warm-up de EMA_TREND (2026-07-21, commit `f13c440`)

**Síntoma**: `generar_senales` no filtraba señales durante las primeras 50 velas (warm-up de EMA_TREND), generando señales sesgadas hacia el primer precio de la serie.

**Fix**: filtrar explícitamente señales durante el warm-up. Detectado en la revisión del subagente [[Infraestructura|strategy-reviewer]] (mismo pase de revisión que motivó `diagnostico_gap_entrada` y `sensibilidad_spread`, agregados en el mismo commit).

## Barrido de trailing evaluado in-sample (2026-07-21, commit `c0ccffe`)

**Síntoma**: `optimizar_trailing` elegía y reportaba la mejor combinación de trailing sobre el dataset completo, sin chequear si el resultado se sostenía fuera de muestra — la misma inconsistencia que ya existía para el TP fijo antes de `validacion_train_test`.

**Fix**: correr la combinación ganadora por separado en train (70%) y test (30%), igual que ya se hacía para el TP fijo.

## Data snooping estructural: optimización antes de separar train/test (2026-07-22, commit `2e4832e`)

**Síntoma**: el pipeline original optimizaba los barridos de R:R/trailing/filtro de sesión sobre *todo* el dataset, y el split train/test 70/30 se aplicaba recién después — para ese punto el "test" ya estaba contaminado indirectamente, porque los parámetros que se iban a evaluar ya se habían elegido mirando esos mismos datos.

**Fix**: reordenar `main()` para que el split (y más adelante, el walk-forward de folds) ocurra *antes* de cualquier optimización, y que cada fold seleccione parámetros usando exclusivamente su propio TRAIN.

## Inconsistencia TRAIN sin filtro de sesión vs. TEST con filtro (2026-07-22, commit `2e4832e`)

**Síntoma**: el filtro de sesión horaria se decidía comparando resultados *sin* filtrar aplicados sobre todo el dataset, pero después el R:R y el trailing se tuneaban y evaluaban ya *con* el filtro aplicado — el barrido de R:R/trailing optimizaba sobre un conjunto de trades distinto al que después se evaluaba en TEST.

**Fix**: dentro de cada fold, el filtro de sesión se decide primero (comparando con/sin filtro sobre el TRAIN, con el R:R por defecto como referencia) y *recién después* se tunea R:R/trailing sobre el TRAIN ya filtrado de la misma forma que se va a evaluar en TEST.

## Bug de división por cero en la variante de trailing (2026-07-22, commit `2e4832e`)

**Síntoma**: `descontar_spread` usaba el campo `sl` (que se mueve con el trailing a medida que el trade avanza) para calcular el riesgo, en vez del riesgo original de entrada — en trades que terminaban cerrando en break-even, `sl` podía terminar igual al precio de entrada, dividiendo por cero.

**Impacto**: no afectaba al TP fijo (`backtest()`, que nunca muta `sl`), solo a la variante con trailing.

**Fix**: usar el riesgo original de entrada (fijado al abrir el trade), no el `sl` actual.

## Criterio de selección sensible a outliers: "mejor R total crudo" (2026-07-22, commit `2e4832e`)

**Síntoma**: el barrido de parámetros elegía la combinación con mayor R total crudo, lo cual premia a un ganador que depende de 2-3 trades grandes por varianza/outliers, y además ignora por completo el costo del spread.

**Fix**: nuevo criterio `metrica_robusta` — t-stat sobre R **neto de spread**, con piso de 30 trades (`MIN_TRADES_SELECCION`) para no premiar un ganador espurio de muestra chica. Ver [[Metodología]].

## `MergeError` por incompatibilidad de resolución datetime64 (2026-07-23, hipótesis MTF)

**Síntoma**: al implementar `alinear_h1_a_m15`, `pd.merge_asof` fallaba con `MergeError: incompatible merge keys dtype('<M8[s]') vs dtype('<M8[us]')` — sumar un `Timedelta` a la columna `time` (para calcular `valido_desde = time_H1 + 1h`) sube la resolución interna del datetime64 en pandas 2.x, dejando de matchear con la columna `time` de M15.

**Fix**: castear ambas claves de merge a `datetime64[ns]` explícitamente antes del `merge_asof`. Ver [[MTF - filtro H1]].

## Downtime de ~4hs del logger EMA no detectado ni reiniciado (2026-07-22)

**Síntoma**: el proceso terminó con `STATUS_CONTROL_C_EXIT` (0xC000013A) sin excepción capturada por el script, y quedó ~4hs caído sin que Task Scheduler lo reiniciara pese a tener `RestartCount=999`/`RestartInterval=1min` configurados — limitación conocida de tareas con `LogonType=Interactive` cuando se interrumpe la sesión interactiva.

**Fix**: ver [[Infraestructura]] para el detalle completo (log de arranque + trigger cada 15 min + exploración posterior de S4U).

## Logger EMA perdía señales en velas intermedias tras una caída (2026-07-24, commit `e55bed9`)

**Síntoma**: si el proceso estaba caído más de un ciclo M15 (reinicios de Windows, cortes de sesión), el logger procesaba solo la última vela al reconectar — una señal ocurrida en una vela intermedia durante el downtime se perdía silenciosamente, sin quedar registrada ni logueada como error.

**Fix**: procesar todas las velas nuevas pendientes desde la última procesada, no solo la más reciente.

## Riesgo de arranque en frío del logger macro DFII10 (2026-07-24, `log_senal_macro_dfii10.py`)

**Síntoma potencial**: al primer arranque del logger, sin este resguardo, un episodio DFII10 iniciado semanas o meses atrás podría haberse tomado como señal "pendiente de entrada" con el precio de hoy — lo cual no es la misma regla que se validó en el walk-forward (entrada al cierre de la sesión siguiente al *día real* de la señal, no semanas después).

**Fix**: en el primer arranque (`ultima_fecha_dfii10_procesada is None`), el logger explícitamente **no** backfillea ningún episodio histórico como pendiente — solo fija el punto de partida (`estado_macro_dfii10.json`) y empieza a observar episodios nuevos desde el próximo ciclo en adelante. Registrado en el propio código (`log_senal_macro_dfii10.py`, función `ciclo`) y confirmado en el log de arranque real: *"Primer arranque: fijando punto de partida en 2026-07-23 00:00:00 sin backfillear episodios historicos como pendientes."*

## Intento de `LogonType S4U` sin elevación degradaba en silencio a `Interactive` (2026-07-24)

**Síntoma**: un primer intento de registrar la tarea de prueba con `LogonType S4U` desde una consola de PowerShell sin privilegios de administrador no dio error explícito, pero la tarea quedó registrada con `LogonType=Interactive` en vez de `S4U` — un fallo silencioso, no una excepción.

**Fix**: repetir el registro de la tarea desde una consola de PowerShell elevada (como Administrador). Confirmado como resuelto: la prueba de conexión puntual (`test_s4u_conexion_mt5.py`) conectó correctamente a MT5 bajo S4U real, y la prueba de resistencia subsiguiente mostró latidos regulares. Ver [[Infraestructura]] para el detalle completo del incidente y la prueba de resistencia.

*Nota: este incidente no dejó rastro en archivos del repo (no lanzó una excepción registrada en ningún log) — el detalle de la causa/fix está documentado acá según lo reportado directamente en la sesión de trabajo correspondiente, no reconstruido desde logs.*

## Corte de IPC sin auto-recuperación en los loggers EMA y macro (2026-07-25/26, commit `37c4826`)

**Síntoma**: el logger macro DFII10 no pudo bajar datos de oro (`IPC send failed`, -10001) cada hora durante ~11hs seguidas (2026-07-25 16:44 UTC a 2026-07-26 03:45 UTC) sin reconectar ni una vez. El logger EMA tiene el mismo defecto de fondo aunque no se vio expresado igual de visible (además no logueaba el fallo en absoluto — ver abajo). Sin señales perdidas en este incidente puntual (confirmado contra el CSV de salida).

**Causa raíz**: la variable `conectado` de ambos loggers solo se reseteaba a `False` dentro del `except Exception` del loop principal. Un fallo de `copy_rates_range`/`copy_rates_from_pos` (IPC roto) no lanza excepción, solo devuelve `None` — el logger seguía "creyéndose" conectado y nunca volvía a llamar `mt5.initialize()`. Bug adicional en `log_senales_demo.py`: `obtener_velas_cerradas()` no logueaba nada cuando `rates is None`, a diferencia de la versión macro — ese fallo ahí era totalmente silencioso.

**Fix**: ambos loggers cuentan fallos de IPC consecutivos y, al superar un umbral (3 en el macro ~3hs, 20 en el EMA ~10min, proporcional al `POLL_SEGUNDOS` de cada uno), fuerzan `mt5.shutdown()` + `conectado = False` para reconectar en el siguiente ciclo, en vez de repetir el mismo error indefinidamente. Se agregó también el log que faltaba en `log_senales_demo.py`.

**Bloqueo de despliegue encontrado al aplicar el fix**: ver [[Infraestructura]]#Migración de ambas tareas productivas a S4U (2026-07-26) — `Stop-ScheduledTask` dejó los dos procesos productivos huérfanos (código viejo, sin supervisión), y matarlos requiere una PowerShell elevada por el token S4U.

**Remediado y verificado (2026-07-27, vía agente `infra-guardian`, primera invocación real)**: huérfanos confirmados por línea de comando (PID 38212 EMA, PID 21432 macro, ambos con proceso padre `cmd.exe` ya muerto) y matados con `_remediar_huerfanos_y_desplegar_autorecuperacion.ps1`. Ambas tareas relanzadas con `Start-ScheduledTask` (no hizo falta desregistrar/re-registrar — seguían con `LogonType=S4U` intacto). Verificado después: PIDs nuevos (34916 EMA, 24068 macro) con padre `cmd.exe` vivo y supervisado, `SessionId=0` (sin degradación a Interactive), línea "ARRANQUE" fresca en ambos logs (2026-07-27 15:54:10 UTC), y `LastTaskResult=267009` (`SCHED_S_TASK_RUNNING` — valor esperado para un proceso de ejecución continua que sigue vivo en el momento de la consulta, no un código de error). `powercfg standby-timeout-ac` ya estaba en 0, no requirió cambio. **El código con auto-recuperación de IPC (commit `37c4826`/`39b836d`) ya corre en producción en ambos loggers**, no solo commiteado.

## Ver también
[[Metodología]] · [[Cronología]] · [[Infraestructura]]
