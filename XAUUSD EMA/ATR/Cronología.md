# Cronología completa del proyecto

Índice: [[Bienvenido]]

Línea de tiempo desde el arranque sin control de versiones hasta hoy. Cada hito enlaza a su nota de detalle; los hashes de commit son de este mismo repo git.

## Antes de 2026-07-21 — sin control de versiones

Proyecto solo, en Python: backtest de estrategia EMA cross (9/21/50) + ATR sobre XAUUSD vía MetaTrader5. Sin git: las mejoras incrementales se guardaban a mano como archivos duplicados (`backtest_ema.py` → `backtest_ema_v2.py` → `backtest_ema_v3.py` → `Backtest ema v4.py`).

En este período también se hizo una investigación externa (no un backtest propio) que resultaría relevante meses después: un estudio con **8.693 trades reales en XAUUSD** encontrado por el usuario, que mostraba EMA9/21 en H1 con expectancy modesta (+0.115R/trade, 296 trades), timeframes lentos rindiendo mejor que M15 en oro, D1 con EMA21/50 con el mejor profit factor de los timeframes probados, y mean-reversion (RSI) con expectancy negativa en XAUUSD. Esta evidencia no se usó hasta el pivote del 2026-07-24 (ver más abajo).

## 2026-07-21 — git init y primer endurecimiento del rigor

- **`fbc3ed2`** — Initial commit: backtest EMA cross para XAUUSD. Versiones v2-v4 con mejoras incrementales (filtro de sesión, RR ratio, descuento de spread) y resultados de las últimas corridas.
- **`8ccbc12`** — Se agrega el skill `run-backtest` (corre el backtest, respalda CSVs previos) y el subagente `strategy-reviewer` (revisión de overfitting/look-ahead bias).
- **`354eea5`** — Fix `UnicodeEncodeError`: emojis en consola Windows (cp1252) colgaban el script e impedían guardar los CSV de resultados.
- **`c0ccffe`** — Se valida train/test la mejor combinación de trailing en `optimizar_trailing` (antes se elegía in-sample, sin chequear si sostenía fuera de muestra).
- **`f13c440`** — Diagnósticos de gap de entrada, sensibilidad a spread y warm-up de EMA_TREND, basados en la revisión del subagente `strategy-reviewer`. Ver [[Errores y bugs corregidos]].

## 2026-07-22 — walk-forward anclado, primer chequeo multi-timeframe, logger EMA en vivo

- **`dc5e121`** — Se deja de versionar `historial/` (backups locales redundantes con el historial de git).
- **`2e4832e`** — Cambio metodológico central del proyecto: se reemplaza el split train/test único 70/30 por **walk-forward anclado de N folds**, corrigiendo el data snooping estructural (antes se optimizaba sobre todo el dataset y el split quedaba contaminado). Se corrige también la inconsistencia de filtro de sesión entre TRAIN y TEST, y un bug real de división por cero en `descontar_spread`. Nuevo criterio de selección: t-stat sobre R neto de spread con piso de 30 trades. Ver [[Metodología]] y [[Errores y bugs corregidos]] para el detalle de cada fix.
  - **Resultado M15** (commiteado): 5/9 folds rentables, fold más fuerte concentra ~51% del R neto; sin él, t≈0.6 — no significativo. Ver [[EMA baseline (M15)]].
  - **Mismo día, chequeo adicional sin commit propio**: se corrió el mismo walk-forward sobre **H1** (mismos parámetros de M15, sin retunear) y sobre **D1**. H1 dio resultado negativo (1/9 folds rentable, -3.22R/fold promedio) — pero se aclaró que esto no evaluaba si H1 tiene edge propio, solo que la config de M15 no transfiere sin retunear (ver [[H1 retuneado]] para el retest con parámetros propios, dos días después). D1 dio solo 77 trades en 9 folds — no-medición, no un resultado (ver [[EMA baseline (M15)]]#D1). Se confirmó además con `copy_rates_range` sobre MT5 real que sí hay 11+ años de historial D1 disponible — la escasez de trades era por diseño de folds, no por falta de datos.
- **`6556356`** — Se despliega `log_senales_demo.py`, el logger en vivo del baseline M15, congelado antes de que existiera un solo dato real. Arrancado ~09:26 hora local vía Task Scheduler (`EMA_XAUUSD_LiveSignalLogger`).
- **Incidente (~15:27 a ~19:33)**: el logger cae con `STATUS_CONTROL_C_EXIT` y queda ~4hs sin reiniciarse pese a la configuración de reinicio automático — limitación de `LogonType=Interactive`. Ver [[Infraestructura]].
- **`cc47787`** — Mitigación: log de arranque + trigger cada 15 min en Task Scheduler.
- **Plan acordado con el usuario**: (1) activar el logger demo ya mismo para que el reloj de datos out-of-sample empiece a correr, (2) diseñar en paralelo una hipótesis de entrada nueva, no más tuning de salida sobre el mismo dataset.

## 2026-07-23 — tres variantes de filtro de tendencia, diagnóstico de inestabilidad

- **`6934716`** — Hipótesis **MTF (filtro de tendencia H1)**: reemplaza el filtro de tendencia M15 por H1, manteniendo el trigger en M15. Descartada: R neto agregado negativo (-3.79R en 9 folds). Ver [[MTF - filtro H1]].
- **`4220a3b`** — Hipótesis **estructura de swings (HH/HL)**: tercera definición de tendencia. Descartada: solo 3/9 folds rentables, 123% del R concentrado en un fold. Ver [[Estructura de swings (HH-HL)]].
- **Diagnóstico de inestabilidad**: se re-corren las 3 variantes con N_FOLDS=4 para descartar "muestra chica por fold" como causa de la falta de coincidencia entre folds dominantes. El patrón se sostiene e incluso empeora — confirma que el problema es el trigger EMA9/21 en sí. Ver [[EMA baseline (M15)]]#Diagnóstico-de-inestabilidad.
- **Trigger nuevo aprobado**: ruptura de estructura + retest, definición única fijada (sin menú de variantes), para probar en vez de seguir iterando filtros de tendencia. Ver [[Ruptura y retest]].

## 2026-07-24 — cierre de la familia EMA9/21, pivote a H1, hipótesis macro nueva

- **`2c8fa9b`** — Hipótesis **ruptura de estructura + retest**, implementada y corrida: 443 trades TEST, solo 5/9 folds rentables, R neto total agregado **-6.72R**. Descartada en el filtro exploratorio. Ver [[Ruptura y retest]].
- **Diagnóstico entrada-vs-salida**: corrido para Baseline y Retest. Retest confirma que su problema es la entrada. Baseline muestra el primer edge de entrada genuino del proyecto (89% de persistencia en TEST) — pero concentrado en 1 fold. Ver [[Diagnóstico entrada-vs-salida]].
- **Chequeo de partial-close/trailing en Baseline** (regla de corte pre-registrada antes de correrlo): el R neto total se da vuelta de +14.08R a -8.05R, folds rentables caen de 7/9 a 3/9. **Regla de corte disparada, sin ambigüedad.** Ver [[Diagnóstico entrada-vs-salida]].
- **`e55bed9`** — Fix operativo del logger EMA: procesa todas las velas nuevas pendientes, no solo la última (evita perder señales silenciosamente tras una caída).
- **Decisión de pivote**: siguiente paso es H1 con parámetros propios (SL/R:R retuneados específicamente, no los de M15 trasplantados), motivado por la evidencia externa de expectancy positiva en H1 (ver arriba). Regla de corte pre-registrada antes de tunear.
- **H1 retuneado — resultado (sin commit propio, documentado en memoria)**: 4/9 folds rentables (minoría), R neto total -23.22R en 341 trades, t-stat de selección decayendo con más datos (firma de edge ilusorio). **Descartado, regla de corte cumplida.** Ver [[H1 retuneado]].
- **CIERRE DEL CAPÍTULO — decisión final del usuario**: no se va a D1 (techo de información bajo: extender el histórico antes de 2008 mezclaría regímenes de mercado no comparables), se retira la **familia EMA9/21 crossover completa** (las 5 variantes fallan de forma convergente, no dispersa). Se fija la regla general para cualquier hipótesis futura: frase falsable + regla de corte propia, antes de tocar código. Ver [[Bienvenido]] y [[Metodología]].
- **`6c81b61`** — Se amplía `.gitignore` antes de publicar el repo: pycache, entornos virtuales, logs/CSVs operativos de los loggers en vivo, y archivos de config local con SID/usuario de Windows.
- **`18b3e38`** — Primera hipótesis nueva desde el cierre: **macro DFII10 fase 1** (tasas reales → sesgo alcista en oro, sin trigger técnico). Pasa el checkpoint exploratorio (3/4 folds rentables) con reservas (t-stat marginal, p=0.059). Ver [[Macro DFII10 - fase 1]].
- **`37d4987`** — Se despliega `log_senal_macro_dfii10.py`, logger en vivo de la hipótesis macro, en paralelo al logger EMA.
- **Tarde/noche — exploración de `LogonType S4U`**: backup de la tarea productiva (17:56), primer intento de registrar la tarea de prueba sin privilegios de administrador (degrada en silencio a `Interactive`), resuelto desde consola elevada (`_crear_tarea_test_s4u.ps1`, 18:08; `_configurar_tarea_test_s4u_endurance.ps1`, 18:53). Ver [[Infraestructura]] y [[Errores y bugs corregidos]].

## 2026-07-25 — validación de S4U en curso

- **00:46 UTC** — Prueba de conexión puntual bajo S4U real: exitosa (`test_s4u_conexion_mt5.py` conecta a MT5 y lee tick de XAUUSD sin errores).
- **00:54 UTC** — Arranca la prueba de resistencia de S4U (`test_s4u_endurance.log`), programada para 4 días.
- **04:59 a 15:43 UTC** — Gap sin latidos en el log de resistencia (~10h45m), causa no confirmada todavía.
- **Al momento de escribir esta documentación (~16:48 UTC)** — latidos regulares retomados; hipótesis macro DFII10 sigue en logging puro; sin hipótesis EMA activa. Ver [[Estado actual y próximos pasos]].

## 2026-07-26 — cierre de S4U en producción, herramientas de disciplina, 2s10s descartado

- **`39b836d`** — Auto-recuperación de IPC agregada a ambos loggers en vivo (EMA y macro DFII10) — hardening preventivo, no reactivo a un incidente todavía.
- **Migración de ambas tareas productivas a `LogonType S4U` confirmada y cerrada** (`EMA_XAUUSD_LiveSignalLogger` y `EMA_XAUUSD_MacroDFII10_LiveSignalLogger`, ambas `Running`) — cierra el riesgo de downtime por logoff/bloqueo de sesión que motivó toda la exploración de S4U desde el 2026-07-24. La tarea de prueba (`_TEST`) sobrevivió 38hs+ y un segundo hueco de sleep de ~8hs sin un solo reinicio, evidencia adicional de que S4U aguanta en la práctica. Ver [[Infraestructura]].
- **`b86ff28`** — Se agregan las skills `hypothesis-gate` (frase falsable + regla de corte + folds derivados del piso de 30 trades, antes de cualquier hipótesis nueva) e `infra-ops-playbook` (playbook de 5 pasos para Task Scheduler/MT5), la skill `sync-knowledge` (sincroniza git + memoria + vault sin que haga falta pedirlo) y el agente `infra-guardian` (ejecuta cambios sobre infraestructura productiva en vivo, solo tras confirmación explícita ya dada en la conversación principal). Formalizan como herramientas reusables la disciplina aprendida a los golpes en esta sesión. Ver [[Infraestructura]]#Skills y agentes de disciplina de proyecto.
- **`e00ca23`** — Segunda hipótesis macro nueva, **2s10s (empinamiento del spread de tasas 2yr-10yr)**, evaluada con `hypothesis-gate`: regla de corte más estricta que DFII10 (p<0.05 con y sin el fold más fuerte, sin zona de "pasa con reservas"), fijada antes de correr nada. **NO PASA el checkpoint**: 2/2 folds rentables pero t-stat pooled p=0.20 (p=0.42 sin el fold más fuerte) — ninguna de las dos versiones cerca de significativo. Descartado sin instrumentar logger en vivo. Ver [[Macro 2s10s - fase 1]].

## 2026-07-27 — vault a git, incidente de IPC remediado, DXY sintético y ratio oro/plata descartados

- **`0b6c621`** — El vault de Obsidian del proyecto (`XAUUSD EMA/ATR/`) se agrega a git por primera vez, junto con la resolución de una divergencia con `origin/master` (rebase limpio sobre un README creado directo en la interfaz web de GitHub).
- **`898f1c6`** — **Incidente de corte de IPC en el logger macro DFII10** (2026-07-25 16:44 UTC a 2026-07-26 03:45 UTC, ~11hs: `IPC send failed` repetido 12 veces sin reconectar, sin señales perdidas) diagnosticado y remediado: fix real de auto-recuperación desplegado vía **primera invocación real de `infra-guardian`** (con confirmación explícita del usuario citada en el prompt del agente). Huérfanos (PID 38212 EMA, PID 21432 macro — dejados por `Stop-ScheduledTask` matando el `cmd.exe` supervisor pero no el `python.exe` hijo) matados, tareas relanzadas, verificado después: PIDs nuevos con padre `cmd.exe` vivo, `SessionId=0` (S4U sin degradar), ARRANQUE fresco en ambos logs. `powercfg standby-timeout-ac` verificado en 0 (ya estaba correcto). Ver [[Infraestructura]] · [[Errores y bugs corregidos]].
- **`1019584`** — Se agrega un monitor diario de conveniencia (`XAUUSD_MacroDFII10_HoldoutMonitor`, Task Scheduler, no productivo) que avisa con un toast de Windows apenas el CSV del holdout DFII10 sume una fila nueva, para no depender de revisarlo a mano. Ver [[Macro DFII10 - fase 1]].
- **`c39de73`** — Tercera y cuarta hipótesis macro exploradas el mismo día: **DXY** queda **bloqueado antes del chequeo de frecuencia** — el broker no ofrece el índice dólar real (ICE DXY) bajo ningún símbolo (`USDX`/`DXYN`/`DXYZ`/`GDXY` son instrumentos no relacionados por coincidencia de ticker); construir un proxy sintético desde 6 pares FX queda pendiente de confirmación del usuario, no decidido unilateralmente. **Ratio oro/plata** sí pasa el screening inicial (XAUUSD/XAGUSD confirmados en MT5 real) pero es **descartado tras walk-forward completo**: 4/4 folds rentables netos (suena fuerte) pero t-stat pooled p=0.11, cae a p=0.47 sin el fold más fuerte que concentra 63% del R neto — ejemplo de conteo de folds ganadores que no sobrevive el chequeo real. Ver [[Macro DXY - fase 1]] · [[Ratio oro-plata - fase 1]].
- **`2f5a41e`** — El usuario confirma construir el DXY sintético con la fórmula real de ICE desde 6 pares FX (`EURUSD`/`USDJPY`/`GBPUSD`/`USDCAD`/`USDSEK`/`USDCHF`). Código escrito y commiteado (`construir_dxy_sintetico.py`) pero **bloqueado antes de validar**: dos intentos de bajar historial FX de MT5 quedaron colgados, dejando procesos Python huérfanos compitiendo por el canal IPC del terminal — matarlos fue denegado por el clasificador de auto-mode, no se insistió. Verificado que los loggers productivos no se vieron afectados.
- **`2047683`** — Bloqueo de conexión resuelto (el usuario liberó la conexión; diagnóstico posterior: no era un deadlock sino sincronización de historial lenta la primera vez que el terminal accede a un símbolo nuevo, ~4 min/par en el peor caso). Proxy sintético validado contra 21 valores reales de investing.com: **correlación 0.9945**, diferencia media 0.023 puntos, sin sesgo direccional. Chequeo de frecuencia comparable a DFII10 (260/200/111 vs. 291/177/132). Walk-forward de 4 folds con regla de corte fijada antes de correr (p<0.05 con y sin el fold más fuerte, corrigiendo la laxitud señalada en la nota metodológica del ratio oro/plata): **NO PASA** — 3/4 folds rentables (+27.18R, 149 trades) pero p=0.072 con todos los folds (peor que el p=0.059 marginal de DFII10) y p=0.306 sin el fold dominante (59% del R neto). **Hipótesis macro DXY descartada.** Ver [[Macro DXY - fase 1]].

## Ver también
[[Metodología]] · [[Errores y bugs corregidos]] · [[Infraestructura]] · [[Estado actual y próximos pasos]]
