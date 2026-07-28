# Proyecto: Backtest EMA/ATR XAUUSD

Backtest de estrategias técnicas (y ahora macro) sobre XAUUSD vía MetaTrader5, en Python, con una disciplina de walk-forward anclado (TRAIN elige parámetros, TEST confirma una sola vez) construida para evitar data snooping. Proyecto solo, sin control de versiones hasta el 2026-07-21.

## Objetivo del proyecto (actualizado 2026-07-27)

**Ya no es "encontrar una señal fuerte para operar" — es construir una biblioteca de factores independientes de baja correlación que, combinados, puedan producir un edge robusto.** Ver [[Objetivo del proyecto - biblioteca de factores]] para el porqué completo y [[Criterios de cierre del enfoque]] para el presupuesto explícito de esta búsqueda.

## Estado actual (2026-07-25)

**Familia EMA9/21 crossover: RETIRADA por completo.** 5 variantes evaluadas con la misma disciplina, las 5 fallan de forma convergente (no dispersa). El problema se diagnosticó como el trigger de entrada en sí (cruce EMA9/21), no el timeframe, no el filtro de tendencia, no la salida. No se retoma salvo razón nueva y específica.

**D1: pospuesto, no descartado formalmente**, pero con techo de información bajo (77 trades en 11 años; extender el histórico antes de 2008 mezclaría regímenes de mercado no comparables). No es cuestión de esperar más.

**Sin hipótesis activa en research (2026-07-27).** [[Macro DFII10 - fase 1]] (tasas reales de EE.UU. → sesgo direccional en oro) pasó el checkpoint exploratorio con reservas (t-stat marginal, p=0.059) y sobrevivió una auditoría completa de robustez, pero quedó **reclasificada como factor archivado** — el power analysis mostró que confirmarla sola necesitaría ~13 años más de holdout. Sigue en monitoreo pasivo (logger en vivo + aviso de holdout), candidata a la biblioteca de factores, sin research activo. Ver [[Objetivo del proyecto - biblioteca de factores]].

**Infraestructura**: dos loggers en vivo corriendo en paralelo (EMA M15 baseline + Macro DFII10), ambos en modo lectura pura. Incidente de estabilidad de Task Scheduler (2026-07-22) parcialmente mitigado; prueba de `LogonType S4U` en curso para resolverlo del todo.

## Cómo está organizada esta documentación

- **[[Cronología]]** — línea de tiempo completa, desde los archivos sueltos `_v2`/`_v3`/`v4` hasta hoy, con fechas y commits.
- **[[Metodología]]** — la disciplina de validación (walk-forward, chequeo de fold dominante, reglas de corte, etc.) y el porqué de cada práctica.
- **[[Errores y bugs corregidos]]** — todos los bugs metodológicos y de código encontrados, con causa y fix.
- **[[Diagnóstico entrada-vs-salida]]** — el hallazgo más informativo del proyecto: por qué se cerró la familia EMA9/21 con datos, no por cansancio.
- **[[Infraestructura]]** — scripts de backtest, loggers en vivo, el incidente de Task Scheduler y la resolución vía S4U.
- **[[Estado actual y próximos pasos]]** — qué sigue corriendo, qué está pendiente, y la regla general para cualquier hipótesis futura.
- **[[Checklist paso a cuenta demo]]** — los nueve criterios objetivos, con umbrales numéricos, que cualquier hipótesis tiene que cumplir antes de pasar a demo. Escrito antes de que haga falta, no bajo presión.
- **[[Data Dictionary]]** — cada archivo de datos del proyecto: qué es, de dónde sale, con qué frecuencia se actualiza, cómo se verifica.
- **[[Bitácora de decisiones]]** — tabla de una línea por decisión importante del proyecto, de punta a punta (complementa a [[Cronología]], que es narrativa).
- **[[Criterios de cierre del enfoque]]** — cuándo el problema deja de ser "falta una hipótesis más" y pasa a ser el diseño completo (mercado/frecuencia) del proyecto.
- **[[Candidatos futuros]]** — próximos factores a explorar, priorizados por frecuencia y racional económico, todos sujetos al triage de `hypothesis-gate` antes de entrar al pipeline.

### Hipótesis probadas

| Hipótesis | Resultado | Nota |
|---|---|---|
| EMA9/21 baseline (M15) | Único hallazgo con edge de entrada real (89% folds sostienen en TEST), pero descartado tras fallar el chequeo de concentración por fold | [[EMA baseline (M15)]] |
| Filtro de tendencia MTF (H1) | Descartado — menos señales, sin mejor selectividad, R neto negativo | [[MTF - filtro H1]] |
| Filtro de tendencia por estructura (HH/HL) | Descartado — peor que baseline y MTF, 123% del R concentrado en 1 fold | [[Estructura de swings (HH-HL)]] |
| Trigger ruptura de estructura + retest | Descartado — R neto agregado negativo, sin fold dominante que lo sostenga | [[Ruptura y retest]] |
| H1 con SL/R:R propios (retuneado) | Descartado — minoría de folds rentables, t-stat decayendo con más datos (firma de edge ilusorio) | [[H1 retuneado]] |
| Macro DFII10 fase 1 | **Archivado** — efecto real (pasa checkpoint, sobrevive auditoría) pero económicamente débil; necesitaría ~13 años más para confirmación sólida sola | [[Macro DFII10 - fase 1]] |
| Macro 2s10s fase 1 (empinamiento del spread) | Descartado — no pasa checkpoint exploratorio, p=0.20 (p=0.42 sin el fold más fuerte) | [[Macro 2s10s - fase 1]] |
| Macro DXY fase 1 (proxy sintético, 6 pares FX) | Descartado — 3/4 folds rentables pero p=0.072 con todos los folds, p=0.31 sin el fold más fuerte (59% del R neto) | [[Macro DXY - fase 1]] |
| Ratio oro/plata fase 1 | Descartado — 4/4 folds rentables pero t-stat pooled no significativo (p=0.11, p=0.47 sin el fold más fuerte que concentra 63% del R neto) | [[Ratio oro-plata - fase 1]] |

## Reglas del proyecto (principios acumulados)

- **Antes de cualquier hipótesis nueva**: definir una frase falsable concreta + su propia regla de corte, ambas ANTES de correr o construir nada.
- **Walk-forward anclado siempre**: cada fold selecciona parámetros solo con su TRAIN, evalúa una única vez en su TEST.
- **Criterio de selección**: t-stat sobre R neto de spread, con piso de 30 trades por fold — evita premiar un ganador espurio de muestra chica.
- **Datos ya "mirados" no se vuelven a recortar de otra forma** para buscar confirmación — la única confirmación honesta final es con datos nuevos hacia adelante (holdout en vivo).
- **No operar en real** con ninguna hipótesis hasta pasar checkpoint exploratorio + holdout en vivo con régimen de decisión pre-registrado.

Detalle y porqué de cada regla en [[Metodología]].
