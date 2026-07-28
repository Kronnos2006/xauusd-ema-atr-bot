# Estado actual y próximos pasos

Índice: [[Bienvenido]]

## Qué sigue corriendo (2026-07-26)

- **`log_senales_demo.py`** (logger EMA M15 baseline): vía Task Scheduler (`EMA_XAUUSD_LiveSignalLogger`), ya migrada a `LogonType=S4U` y confirmada `Running`. No se invierte más tiempo de diseño ahí, pero se mantiene porque el dataset puede servir si alguna variante de M15 se revisita con evidencia nueva. Ver [[EMA baseline (M15)]] · [[Infraestructura]].
- **`log_senal_macro_dfii10.py`** (logger macro DFII10): config fija N=60/M=5, en modo logging puro, también migrado a `LogonType=S4U`. Es el holdout en vivo de la hipótesis activa. Ver [[Macro DFII10 - fase 1]].
- **Migración a `LogonType S4U`: cerrada en producción**, no solo validada en la tarea de prueba — ver [[Infraestructura]]#Migración de ambas tareas productivas a S4U (2026-07-26). La tarea de prueba sigue corriendo igual (38hs+ sin un solo reinicio, sobrevivió un segundo sleep de ~8hs) pero ya no es la única evidencia.

## Qué está pendiente

- **Hipótesis macro DFII10 fase 1**: acumular más datos del holdout en vivo. A la fecha (2026-07-27) el CSV de salida (`senal_macro_dfii10_live.csv`) sigue en 0 episodios desde que arrancó el 2026-07-23 — esperable dada la baja frecuencia de episodios N=60, no un síntoma de falla. No se diseña la confirmación técnica de fase 2 hasta tener una lectura más sólida que la actual (t-stat marginal, p=0.059, dependiente de un fold). Ver [[Macro DFII10 - fase 1]].

## Resuelto (2026-07-27)

- **Huérfanos matados y fix de auto-recuperación de IPC (commit `37c4826`) ya desplegado y verificado en producción**, vía primera invocación real de `infra-guardian`. Ver [[Infraestructura]] · [[Errores y bugs corregidos]].
- **`powercfg standby-timeout-ac`**: verificado en 0 (ya estaba correcto, no fue necesario cambiarlo — contrario a lo asumido antes de verificar).
- **Repo sincronizado con GitHub**: divergencia con `origin/master` (un README creado directo en la interfaz web) resuelta con rebase limpio; los 5 commits pendientes de esta sesión más el vault de Obsidian (agregado a git por primera vez) ya están pusheados. `git`/`origin` quedaron 0/0.
- **Hipótesis macro DXY fase 1**: usuario confirmó construir el proxy sintético (fórmula ICE desde 6 pares FX), código listo (`construir_dxy_sintetico.py`), pero **bloqueada de nuevo por un problema de conexión MT5** — dos procesos Python quedaron colgados intentando bajar el historial de los pares FX, y matarlos requiere una acción que el clasificador de auto-mode denegó. Pendiente de que el usuario libere la conexión. Ver [[Macro DXY - fase 1]].
- **Ratio oro/plata fase 1**: cerrada, no en curso. Descartada tras walk-forward completo — 4/4 folds rentables netos pero t-stat pooled no significativo (p=0.11, cae a p=0.47 sin el fold dominante que concentra 63% del R neto). Ver [[Ratio oro-plata - fase 1]].
- **Hipótesis macro 2s10s fase 1**: cerrada, no en curso. Descartada en el filtro exploratorio (p=0.20, p=0.42 sin el fold más fuerte) — no se instrumentó logger en vivo. No se retoma salvo una razón nueva y específica (ej. otra definición de "empinamiento", otro horizonte). Ver [[Macro 2s10s - fase 1]].
- **Familia EMA9/21 crossover**: no se retoma salvo que aparezca una razón nueva y específica para creer que en otro contexto (timeframe, instrumento) sí andaría distinto — no "probar una vez más por las dudas". Ver [[EMA baseline (M15)]].
- **D1**: pospuesto, no descartado formalmente — pero con un techo de información bajo (extender el histórico antes de 2008 mezclaría regímenes de mercado no comparables) que lo hace improbable de resolver con confianza en ningún plazo razonable. Candidato lógico solo si el resto de las vías se agotan.

## Regla general para cualquier hipótesis futura

Fijada el 2026-07-24 tras el cierre de la familia EMA9/21, como práctica estándar del proyecto de acá en adelante (no algo puntual de esa familia). Antes de arrancar CUALQUIER exploración nueva:

1. **Una frase concreta y falsable** de qué señal específica se va a probar. Una categoría amplia ("macro/fundamental", "otro timeframe") no alcanza — tiene que ser una hipótesis puntual, como la de [[Macro DFII10 - fase 1]].
2. **Su propia regla de corte**, fijada ANTES de correr o construir nada.

Esto es exactamente lo que evitó gastar 5-6 iteraciones más a ciegas en el capítulo EMA9/21 — ver el detalle de por qué en [[Metodología]].

**Desde 2026-07-26 esto ya no depende de acordarse de pedirlo**: la skill `.claude/skills/hypothesis-gate/SKILL.md` aplica esta regla (y el resto del checklist de walk-forward/t-stat/fold dominante) automáticamente ante cualquier hipótesis nueva o resultado a evaluar. Ver [[Infraestructura]]#Skills y agentes de disciplina de proyecto.

## Herramientas de disciplina de proyecto (2026-07-26)

Además de `run-backtest`/`strategy-reviewer`, el proyecto suma `hypothesis-gate`, `infra-ops-playbook`, `infra-guardian` y `sync-knowledge` — formalizan como skills/agente reusable lo que costó aprender a los golpes esta sesión (validación de hipótesis, playbook de Task Scheduler/MT5, cambios seguros sobre infra en vivo, sincronización memoria/vault/git). Detalle completo en [[Infraestructura]]#Skills y agentes de disciplina de proyecto.

## Ver también
[[Bienvenido]] · [[Macro DFII10 - fase 1]] · [[Infraestructura]] · [[Metodología]]
