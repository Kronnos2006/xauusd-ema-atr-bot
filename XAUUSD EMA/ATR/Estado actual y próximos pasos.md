# Estado actual y próximos pasos

Índice: [[00 Inicio]] · [[Bienvenido]]

## Actualización 2026-10-20 — modelos fundacionales en BTC

**Qué corre ahora**
- [[KT-002 — Acierto prospectivo BTC|KT-002]]: cada hora en GitHub Actions, predice la dirección de BTC a 4 h con Kronos, TimesFM y KT-001 y puntúa al vencer. Descriptivo, sin órdenes.
- Informe diario del [[Gerencia y mesa directiva|gerente]] (6:52 a. m.): revisa todo, convoca jefes solo si hace falta y rinde cuentas en ≤ 5 líneas. Ver [[Automatizaciones]].
- Panel en vivo con BTC y las predicciones encima. Ver [[Guía de uso]].

**Qué se cerró**
- [[KT-003 — Diagnóstico histórico BTC|KT-003]] (2017–2026, 2928 días): Kronos 56,8 % vs 50,9 % de «siempre sube» después del corte, **no significativo con Holm** (p 0,086). TimesFM 48,7 %. Sin fuga ni memorización; los movimientos previstos son menores que el costo de operar.

**Qué está pendiente**
- Propuestas del [[Agentes del proyecto#Mejorador|mejorador]]: KT-004 (confirmar Kronos con datos prospectivos de KT-002) y KT-005 (ajuste de TimesFM). La primera versión de KT-004 fue rechazada por el desconfiado y se está corrigiendo. Ninguna se ejecuta sin el OK del usuario.
- Revisión cruzada de Codex sobre KT-002/KT-003, pendiente.
- La PAUSA ACTIVA para hipótesis de trading sigue vigente.


## PAUSA ACTIVA (reafirmada 2026-08-06)

Los tres marcos originales del proyecto están cerrados desde 2026-08-04/05 (ver [[Cierre formal del proyecto - 2026-08-05]]). El 2026-08-06 el usuario reabrió investigación con un cuarto marco, **TF_Basket_H1** (trend following Donchian/MA, basket de 10 instrumentos) — descartado en Fase 0 sin llegar a walk-forward: Donchian 20 sin edge (t≈0), MA 10/50 no significativo y con Sharpe implícito por debajo del objetivo antes de costos. Ver [[TF_Basket_H1 — Fase 0]]. **Ningún marco abierto de nuevo** — próxima decisión de investigación pendiente del usuario. El resto de esta nota (desde 2026-07-26) queda como registro histórico previo a la pausa.

## Qué sigue corriendo (2026-07-26)

- **`log_senales_demo.py`** (logger EMA M15 baseline): vía Task Scheduler (`EMA_XAUUSD_LiveSignalLogger`), ya migrada a `LogonType=S4U` y confirmada `Running`. No se invierte más tiempo de diseño ahí, pero se mantiene porque el dataset puede servir si alguna variante de M15 se revisita con evidencia nueva. Ver [[EMA baseline (M15)]] · [[Infraestructura]].
- **`log_senal_macro_dfii10.py`** (logger macro DFII10): config fija N=60/M=5, en modo logging puro, también migrado a `LogonType=S4U`. Es el holdout en vivo de la hipótesis activa. Ver [[Macro DFII10 - fase 1]].
- **Migración a `LogonType S4U`: cerrada en producción**, no solo validada en la tarea de prueba — ver [[Infraestructura]]#Migración de ambas tareas productivas a S4U (2026-07-26). La tarea de prueba sigue corriendo igual (38hs+ sin un solo reinicio, sobrevivió un segundo sleep de ~8hs) pero ya no es la única evidencia.

## Qué está pendiente

- **Objetivo del proyecto redefinido (2026-07-27)**: de "encontrar una señal fuerte" a "construir una biblioteca de factores independientes de baja correlación". Ver [[Objetivo del proyecto - biblioteca de factores]] y [[Criterios de cierre del enfoque]].
- **DFII10 archivado, no en research activo**: el power analysis mostró que confirmarla sola necesitaría ~105 trades adicionales, ~13 años más de holdout — un plazo que la descalifica como candidata a señal individual, aunque sigue siendo candidata a la biblioteca de factores. El logger en vivo y el monitor de holdout siguen corriendo (monitoreo pasivo, sin costo). Ver [[Macro DFII10 - fase 1]].
- **Pipeline de candidatos vacío (2026-08-03)**: los 8 candidatos de [[Candidatos futuros]] quedaron todos cerrados en esta ronda (6 descartados en triage de frecuencia, Momentum DXY descartado tras walk-forward completo, GLD sin fuente, COT descarte estructural, XAUEUR/XAUGBP reclasificado como técnica de auditoría). **Hace falta una ronda nueva de generación de candidatos** antes de seguir — no queda nada evaluable pendiente en la lista actual.
- Ver [[Checklist paso a cuenta demo]] para los criterios objetivos de cuándo cualquier factor (o combinación) pasaría a demo.

## Resuelto (2026-08-03)

- **Momentum DXY sintético 1d**: cerrada, no en curso. Único de 8 candidatos que pasó el triage de frecuencia (horizonte 4.1 años) y el test de driver económico, pero descartada tras walk-forward completo de 16 folds — 6/16 rentables neto de spread, R neto acumulado -17.20R, t-stat pooled -0.986 (p=0.32), sin el fold más fuerte -1.195 (p=0.23). No es un caso marginal como DFII10: el signo es negativo y lejos de \|t\|>1.96. Ver [[Macro Momentum DXY - fase 1]].
- **Triage de frecuencia real corrido sobre los 8 candidatos de [[Candidatos futuros]]** (datos descargados de FRED, MT5 y home.treasury.gov, no estimados): 6 descartados por horizonte proyectado de 12.9-33.2 años, GLD sin fuente verificable, COT con descarte estructural por cadencia semanal, XAUEUR/XAUGBP reclasificado (no es candidato con mecanismo propio). Detalle completo en [[Candidatos futuros]].

## Resuelto (2026-07-27)

- **Huérfanos matados y fix de auto-recuperación de IPC (commit `37c4826`) ya desplegado y verificado en producción**, vía primera invocación real de `infra-guardian`. Ver [[Infraestructura]] · [[Errores y bugs corregidos]].
- **`powercfg standby-timeout-ac`**: verificado en 0 (ya estaba correcto, no fue necesario cambiarlo — contrario a lo asumido antes de verificar).
- **Repo sincronizado con GitHub**: divergencia con `origin/master` (un README creado directo en la interfaz web) resuelta con rebase limpio; los 5 commits pendientes de esta sesión más el vault de Obsidian (agregado a git por primera vez) ya están pusheados. `git`/`origin` quedaron 0/0.
- **Hipótesis macro DXY fase 1 (proxy sintético)**: cerrada, no en curso. Proxy validado (correlación 0.9945 vs. investing.com), pero la hipótesis descartada tras walk-forward completo — 3/4 folds rentables netos pero t-stat pooled no significativo (p=0.072 con todos los folds, p=0.31 sin el fold dominante que concentra 59% del R neto). Ver [[Macro DXY - fase 1]].
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
