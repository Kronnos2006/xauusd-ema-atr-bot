# Estado actual y próximos pasos

Índice: [[Bienvenido]]

## Qué sigue corriendo (2026-07-26)

- **`log_senales_demo.py`** (logger EMA M15 baseline): vía Task Scheduler (`EMA_XAUUSD_LiveSignalLogger`), ya migrada a `LogonType=S4U` y confirmada `Running`. No se invierte más tiempo de diseño ahí, pero se mantiene porque el dataset puede servir si alguna variante de M15 se revisita con evidencia nueva. Ver [[EMA baseline (M15)]] · [[Infraestructura]].
- **`log_senal_macro_dfii10.py`** (logger macro DFII10): config fija N=60/M=5, en modo logging puro, también migrado a `LogonType=S4U`. Es el holdout en vivo de la hipótesis activa. Ver [[Macro DFII10 - fase 1]].
- **Migración a `LogonType S4U`: cerrada en producción**, no solo validada en la tarea de prueba — ver [[Infraestructura]]#Migración de ambas tareas productivas a S4U (2026-07-26). La tarea de prueba sigue corriendo igual (38hs+ sin un solo reinicio, sobrevivió un segundo sleep de ~8hs) pero ya no es la única evidencia.

## Qué está pendiente

- **Correr `_remediar_huerfanos_y_desplegar_autorecuperacion.ps1` como Administrador** — el fix de auto-recuperación de IPC (commit `37c4826`) para ambos loggers está commiteado pero no desplegado: al intentar reiniciar las tareas quedaron dos procesos huérfanos (código viejo, sin supervisión de Task Scheduler) que solo se pueden matar con una PowerShell elevada. Próximo pendiente de infraestructura, con plan concreto ya escrito, no un ítem abierto. Ver [[Infraestructura]] · [[Errores y bugs corregidos]].
- **Deshabilitar la suspensión automática de Windows (`powercfg`)**, al menos con la PC enchufada — hallazgo del diagnóstico del gap S4U: el sleep recurrente del sistema es un vector de pérdida de señales que ni S4U ni `Password` resuelven (ni la auto-recuperación de IPC: durante un sleep real no hay proceso ejecutando nada que reconectar). Prioridad alta, tarea explícita. Ver [[Infraestructura]].
- **Hipótesis macro DFII10 fase 1**: acumular más datos del holdout en vivo. No se diseña la confirmación técnica de fase 2 hasta tener una lectura más sólida que la actual (t-stat marginal, p=0.059, dependiente de un fold). Ver [[Macro DFII10 - fase 1]].
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
