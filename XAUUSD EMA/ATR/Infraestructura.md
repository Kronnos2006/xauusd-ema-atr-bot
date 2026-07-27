# Infraestructura — scripts, loggers en vivo y Task Scheduler

Índice: [[Bienvenido]] · Ver también [[Cronología]] · [[Errores y bugs corregidos]]

## Evolución de los scripts de backtest

Antes del 2026-07-21 el proyecto no tenía control de versiones: mejoras incrementales se guardaban a mano como archivos duplicados (`backtest_ema.py`, `backtest_ema_v2.py`, `backtest_ema_v3.py`, hasta `Backtest ema v4.py`). Desde el `git init` (commit `fbc3ed2`), todo el desarrollo pasó a vivir como historial de commits sobre `Backtest ema v4.py`, sin más copias `_v2`/`_v3` sueltas. Ver [[Cronología]] para el detalle completo de cada commit.

Dos herramientas de apoyo, agregadas el mismo día (commit `8ccbc12`):
- `.claude/skills/run-backtest/SKILL.md`: corre `Backtest ema v4.py`, respalda CSVs previos en `historial/` (ignorado por git) y resume resultado nuevo vs. anterior.
- `.claude/agents/strategy-reviewer.md`: subagente para revisar overfitting/look-ahead bias en la estrategia. Su revisión motivó directamente el fix de señales sesgadas en warm-up y los diagnósticos de gap/spread (commit `f13c440`) — ver [[Errores y bugs corregidos]].

## Skills y agentes de disciplina de proyecto (2026-07-26, commit `4d8f894`)

Formalizan como herramientas reusables la disciplina que este proyecto aprendió a los golpes (familia EMA9/21, migración S4U, incidente de IPC), para que no dependa de repetirla a mano cada vez. `run-backtest`/`strategy-reviewer` (arriba) quedaron sin cambios.

- **`.claude/skills/hypothesis-gate/SKILL.md`** (auto-disparo): antes de escribir código de una hipótesis nueva, exige frase falsable + regla de corte + número de folds *derivado* del piso de 30 trades/fold contra la frecuencia real de la señal (no un número fijo — 9 folds para EMA y 4 para macro DFII10 fueron resultado de ese cálculo, no una convención a repetir). Al evaluar un resultado ya corrido, exige t-stat real sobre R neto (no conteo de "folds ganadores" ni R crudo) calculado **con y sin el fold más fuerte** — sin un porcentaje fijo de "fold dominante" (se probó un umbral de 60% y resultó inconsistente con el caso M15, donde 51% de concentración sí era señal real de dependencia). Veredicto siempre binario: PASA EL CHECKPOINT / NO LISTO.
- **`.claude/skills/infra-ops-playbook/SKILL.md`** (auto-disparo): playbook de 5 pasos para Task Scheduler + MT5 — verificar elevación antes de intentar (sin buscar atajos si falta), backup antes de mutar una tarea, desregistrar+re-registrar en vez de mutar, distinguir sleep de caída real vía Event Log (`Power-Troubleshooter` ID 1 vs. `System` 6005/6006/6008), y verificar el resultado real después del cambio (PID/ParentProcessId, `LastTaskResult`, `LogonType` real, línea ARRANQUE nueva) en vez de asumir éxito por exit code 0.
- **`.claude/agents/infra-guardian.md`** (invocación explícita, solo tras confirmación ya dada en la conversación principal): ejecuta cambios sobre infraestructura productiva en vivo. Paso 0 es un gate obligatorio — si su propio prompt no trae una cita clara de la confirmación del usuario para *esa* acción puntual, no ejecuta nada. Registra estado antes, ejecuta solo lo confirmado, y verifica estado después contra lo esperado, reportando discrepancias como hallazgo (no las esconde en un "salió bien"). Deliberadamente sin herramienta para preguntar directamente — fuerza que la confirmación pase por acá antes de invocarlo, la lección directa del incidente de procesos huérfanos de esta sesión (ver [[Errores y bugs corregidos]]). **Primera invocación real: 2026-07-27**, remediando exactamente ese incidente (huérfanos + fix de IPC) — ver [[Errores y bugs corregidos]]#Corte de IPC sin auto-recuperación.
- **`.claude/skills/sync-knowledge/SKILL.md`** (auto-disparo): después de un incidente de infra resuelto, un fix desplegado a un logger en producción, o un checkpoint de hipótesis, sincroniza sin que haga falta pedirlo: commit de git, nota de memoria interna (`project`, con Por qué importa/Cómo aplicar), y el archivo correspondiente de este vault. Aclara explícitamente que este vault vive en `Nueva carpeta/XAUUSD EMA/ATR/`, no en el conectado por defecto al MCP de Librarian (son proyectos distintos).

## Loggers en vivo

Dos loggers corren en paralelo, ambos en **modo lectura pura** (no ejecutan órdenes): sirven para acumular holdout genuinamente out-of-sample, no para operar.

### `log_senales_demo.py` — logger EMA M15 baseline

Congelado ANTES de que existiera un solo dato en vivo (commit `6556356`, 2026-07-22), a propósito, para dejar timestamp verificable de que no se ajustó nada mirando resultados — ver [[Metodología]]#Commit-antes-de-que-exista-dato-fresco. Cualquier fix futuro va en commit aparte, para poder filtrar por fecha qué filas del CSV son pre-fix y cuáles post-fix.

Reutiliza `calcular_indicadores`/`generar_senales` de `Backtest ema v4.py` (import directo del módulo) para que la señal en vivo no pueda desviarse de la lógica validada por walk-forward. Registra spread/precio real de MT5 en el momento de cada señal (no solo el close teórico), para medir después el gap de ejecución real vs. el supuesto fijo de 30 puntos del backtest.

Tarea de Task Scheduler `EMA_XAUUSD_LiveSignalLogger`, arrancada 2026-07-22 ~09:26 hora local. Logs: `senales_demo_live.log` (arranques/errores/reconexiones), `log_senales_demo_stdout.log` (actividad).

Sigue corriendo sin cambios ni extensiones desde que la familia EMA9/21 fue retirada (2026-07-24) — no cuesta nada mantenerlo y el dataset puede servir si alguna variante se revisita con evidencia nueva.

Fix aplicado (commit `e55bed9`, 2026-07-24): si el proceso estaba caído más de un ciclo M15, antes procesaba solo la última vela y perdía señales en velas intermedias silenciosamente. Ver [[Errores y bugs corregidos]].

### `log_senal_macro_dfii10.py` — logger Macro DFII10

Ver hipótesis en [[Macro DFII10 - fase 1]]. Mismo modo de logging puro, misma disciplina, desplegado commit `37d4987` (2026-07-24). Reutiliza `detectar_inicios_episodio()` de `hipotesis_macro_dfii10.py`. Config fija (N=60, M=5), no se re-selecciona en vivo. Tarea de Task Scheduler propia, migrada a `LogonType S4U` junto con la tarea EMA (ver [[#Migración de ambas tareas productivas a S4U (2026-07-26)]]).

Incluye un resguardo explícito contra un riesgo de arranque en frío (backfillear un episodio viejo como señal fresca) — ver [[Errores y bugs corregidos]].

**Incidente de corte de IPC (2026-07-25 16:44 UTC a 2026-07-26 03:45 UTC, ~11hs)**: falló en repetir `IPC send failed` (código -10001) cada hora, 12 veces seguidas, sin reconectar — el reintento existente no cubría este tipo de falla porque no lanza excepción. Sin señales perdidas (CSV de salida seguía vacío, sin episodio pendiente durante la ventana). Causa del corte en sí no investigada más a fondo (retorno decreciente): coincide con que la máquina salía de un sleep largo esa noche más la actividad de migración a S4U en curso. Fix real (lo que faltaba, no solo "a monitorear") en [[Errores y bugs corregidos]].

## Incidente de estabilidad del logger EMA (2026-07-22) y mitigaciones

Detectado por chequeo manual de PID (no por el logger): el proceso terminó con `STATUS_CONTROL_C_EXIT` (0xC000013A) sin excepción capturada, quedando **~4hs caído sin reiniciarse** (~15:27 a ~19:33) pese a tener `RestartCount=999`/`RestartInterval=1min` bien configurados en Task Scheduler. Causa: limitación conocida de tareas con `LogonType=Interactive` ("solo con sesión iniciada") — el reinicio automático no es confiable cuando se interrumpe la sesión interactiva (bloqueo/desconexión). El CSV seguía en 0 señales al detectarlo, pero fue un near-miss real: pudo perderse una señal genuina sin forma de saberlo.

**Mitigaciones aplicadas (commit `cc47787`)**:
- Log de "ARRANQUE" en `senales_demo_live.log` en cada inicio del proceso, para que cortes futuros sean visibles como gap entre dos líneas ARRANQUE, sin depender de chequeo manual de PID.
- Trigger adicional cada 15 min en Task Scheduler (relanza si no está corriendo; no-op si ya corre, gracias a `MultipleInstances=IgnoreNew`) — cubre caídas del proceso mientras la sesión de Windows siga iniciada (aunque bloqueada), pero **no cubre un logoff completo de la sesión**.

Propuesta inicial del usuario tras el incidente: cambiar la tarea a `LogonType=Password` ("Run whether user is logged on or not") — cubriría también el logoff completo, pero requiere guardar la contraseña de Windows a mano en el diálogo nativo de Task Scheduler (no scripteable por seguridad).

## Diagnóstico y resolución vía S4U (2026-07-24/25)

Antes de comprometerse a `Password`, se evaluó `LogonType S4U` (Service-for-User) como alternativa: no requiere guardar contraseña y corre sin sesión interactiva completa. Riesgo a verificar: MT5 es una app GUI, existía la posibilidad de que en sesión no-interactiva el script no pudiera conectarse a la terminal.

**Backup previo**: antes de tocar la configuración, se respaldó la tarea productiva (`task_backup_20260724_175648.xml`, 2026-07-24 17:56) — confirmado que corresponde a la tarea real con `LogonType=InteractiveToken`. Este XML quedó excluido de git (contiene el SID de usuario de Windows) al ampliar el `.gitignore` (commit `6c81b61`) antes de publicar el repo.

**Intento fallido sin elevación**: un primer intento de registrar la tarea de prueba con `LogonType S4U` desde una consola de PowerShell sin privilegios de administrador no lanzó ningún error explícito, pero la tarea quedó registrada silenciosamente con `LogonType=Interactive` en vez de `S4U` — un fallo de degradación silenciosa, no una excepción capturable. (Este intento no dejó rastro en archivos del repo por no haber lanzado excepción alguna; documentado acá según lo reportado directamente en la sesión de trabajo.)

**Resuelto reintentando desde una consola de PowerShell elevada (como Administrador)**. Scripts de prueba resultantes (no productivos, prefijo `_` y sufijo `_TEST`/`_test_s4u`, sin tocar la tarea productiva):
- `_crear_tarea_test_s4u.ps1`: crea la tarea `EMA_XAUUSD_LiveSignalLogger_TEST` con `New-ScheduledTaskPrincipal -UserId 'josem' -LogonType S4U -RunLevel Limited`, ejecuta una vez `test_s4u_conexion_mt5.py`.
- `test_s4u_conexion_mt5.py` / `test_s4u_result.log`: **prueba puntual exitosa** (2026-07-25 00:46 UTC) — conectó a MT5 (`TerminalInfo(connected=True, trade_allowed=True, ...)`) y leyó tick de XAUUSD sin errores bajo S4U real (esta vez sí, confirmado por el log).
- `_configurar_tarea_test_s4u_endurance.ps1`: reconfigura la misma tarea para correr `log_senales_demo_test_s4u.py` cada 15 min durante 4 días (prueba de resistencia, no solo de conexión puntual).

**Prueba de resistencia en curso**: iniciada 2026-07-25 00:54 UTC, configurada para 4 días (el acuerdo original había sido 24hs — el cambio a 4 días no quedó documentado en ningún commit ni nota; causa desconocida, no se fabrica una explicación). `test_s4u_endurance.log` registró latidos (`LATIDO | conectado=True`) cada ~5 min desde el arranque hasta las 04:59 UTC, con un **gap sin latidos entre 04:59 y 15:43 UTC** (~10h45m), y latidos regulares retomados desde entonces.

**Diagnóstico del gap (resuelto, 2026-07-25)**: causa benigna confirmada por evidencia cruzada, no por asunción:
- Event Log de Windows (`Microsoft-Windows-Power-Troubleshooter`, ID 1): el sistema se suspendió (sleep) de 2026-07-25T05:01:19 UTC a 2026-07-25T15:43:31 UTC — coincide casi al segundo con el gap del log.
- `LastBootUpTime` del sistema (2026-07-24 18:13:38) es anterior al arranque del test y no hubo ningún reinicio en el medio.
- El proceso de la tarea de prueba (SessionId 0, coherente con S4U) tiene el mismo PID y `CreationDate` desde el arranque — no fue matado ni relanzado por Task Scheduler; cero eventos en el Task Scheduler Operational log durante toda la ventana del gap.
- El heartbeat de `log_senales_demo_test_s4u.py` ya se loguea incondicionalmente cada 300s (no depende de tick fresco ni de señal) — el silencio se debe enteramente a que ningún proceso ejecuta instrucciones durante un sleep de Windows, no a un defecto del script.

**Conclusión**: S4U se mantuvo estable antes, durante y después del sleep (mismo PID, mismo SessionId 0, sin degradación a Interactive). El gap no fue una falla de S4U — la pregunta de LogonType queda contestada.

**Hallazgo colateral (más relevante que el gap en sí)**: la suspensión automática de esta PC es recurrente, no un incidente aislado del fin de semana — se registró otro evento de sleep el día anterior (2026-07-24, 05:14→13:56 UTC, ~8h42m). Es un vector de pérdida de señales que **ni S4U ni `Password` resuelven** — es configuración de energía de Windows, ortogonal al LogonType de la tarea, y afecta también ahora mismo a los dos loggers productivos (`LogonType=Interactive`), no solo al test.

## Migración de ambas tareas productivas a S4U (2026-07-26)

Aplicado y confirmado: `Get-ScheduledTask` muestra `LogonType=S4U` tanto en `EMA_XAUUSD_LiveSignalLogger` como en `EMA_XAUUSD_MacroDFII10_LiveSignalLogger`, ambas `Running`. Cierra el riesgo de downtime por logoff/bloqueo de sesión que motivó toda la exploración de S4U (ver [[Errores y bugs corregidos]]).

**Evidencia de que S4U aguanta en la práctica, no solo en la prueba puntual**: la tarea de prueba `EMA_XAUUSD_LiveSignalLogger_TEST` lleva corriendo desde 2026-07-25 00:54:33 UTC (38hs+ al momento de escribir esto) con una sola línea de "ARRANQUE" en todo su log — nunca la relanzó Task Scheduler. Sobrevivió un segundo hueco de latidos de ~8hs (2026-07-26 06:14→14:22 UTC, mismo patrón de sleep del sistema ya diagnosticado el día anterior) sin necesitar reinicio: mismo PID, sin nueva línea de ARRANQUE.

**Bloqueo nuevo al desplegar código sobre tareas ya S4U**: `Stop-ScheduledTask` puede matar el `cmd.exe` que Task Scheduler supervisa pero dejar el `python.exe` hijo corriendo huérfano (sin proceso padre), y ese huérfano después no se puede matar con `Stop-Process` desde una PowerShell no elevada (S4U corre con un token distinto al de la sesión interactiva — "Acceso denegado"). Pasó exactamente esto al intentar desplegar el fix de auto-recuperación de IPC (ver [[Errores y bugs corregidos]]): quedó `_remediar_huerfanos_y_desplegar_autorecuperacion.ps1` listo para correr como Administrador.

## Remediación de huérfanos y despliegue del fix de IPC (2026-07-27, resuelto)

Ejecutado vía agente `infra-guardian` (primera invocación real, con confirmación explícita del usuario citada en el prompt del agente). Huérfanos (PID 38212 EMA, 21432 macro) matados, tareas relanzadas, verificado después: PIDs nuevos con padre `cmd.exe` vivo, `SessionId=0` (S4U sin degradar), ARRANQUE fresco en ambos logs. `powercfg standby-timeout-ac` verificado en 0 (ya estaba así, no requirió cambio). Detalle completo en [[Errores y bugs corregidos]]#Corte de IPC sin auto-recuperación.

## Pendiente

- Dejar correr el endurance test (`EMA_XAUUSD_LiveSignalLogger_TEST`) hasta el final no es urgente ni aporta información nueva sobre S4U (la pregunta ya quedó contestada), pero tampoco cuesta nada cortarlo.

## Ver también
[[Macro DFII10 - fase 1]] · [[EMA baseline (M15)]] · [[Errores y bugs corregidos]] · [[Metodología]] · [[Estado actual y próximos pasos]]
