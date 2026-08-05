# Criterios de cierre del enfoque completo

Índice: [[Bienvenido]] · Ver también [[Objetivo del proyecto - biblioteca de factores]] · [[Candidatos futuros]] · [[Bitácora de decisiones]]

Escrito el 2026-07-27 (revisión externa, punto 5), **antes de que haga falta** — mismo espíritu que [[Checklist paso a cuenta demo]]. Esto no es sobre cuándo se descarta UNA hipótesis (eso ya lo cubre `hypothesis-gate`) — es sobre cuándo el problema deja de ser "falta encontrar la hipótesis correcta" y pasa a ser el **diseño completo** del proyecto: XAUUSD, frecuencia macro diaria, mercado de oro. Si eso pasa, la respuesta no es "una hipótesis más", es replantear el marco.

## CIERRE FORMAL DEL MARCO (2026-08-04)

**Criterio 4 disparado — marco XAUUSD cerrado.** Patrón sistemático de resultados: **0/3 walk-forwards completos pasando la regla de corte pre-registrada** en la ronda intradía —

- Momentum DXY sintético H4: t=-2.862 (p=0.0042) — edge **negativo**, estadísticamente significativo (ver [[Macro Momentum DXY H4 - fase 1]]).
- Risk-off vía US500 H4: t=+1.525 (p=0.1271), sin el fold más fuerte t=+0.921 (p=0.3570) — positivo pero sin significancia, DSR=0.1806 (ver [[Risk-off US500 H4 - fase 1]]).
- Más 2 candidatos que ni siquiera llegaron a walk-forward: Momentum propio XAUUSD H1 (descartado por marco) y spread de crédito GHYG/LQD (descartado en el triage de Fase 0). Ver [[Candidatos futuros]].

Sumado a la ronda macro-diaria previa (0/8 candidatos viables, 2026-08-03) y al fallo de DFII10 (marginal, p=0.059, DSR=0.37 — el mejor resultado de todo el proyecto y aun así insuficiente), el patrón es consistente en ambas frecuencias (diaria e intradía) y en todos los drivers probados (tasas, DXY, crédito, renta variable, price action propio): ninguno pasa la barra. Esto es exactamente lo que el criterio 4 (y en la práctica también el 1 y el 3) fueron diseñados para capturar.

**Decisión del usuario (2026-08-04)**: el marco "XAUUSD + biblioteca de factores macro (diario e intradía)" queda **cerrado**. Nuevo marco: **EURUSD, FX carry + momentum, factores macro con frecuencia suficiente** — ver `CLAUDE.md` para el detalle y [[Bitácora de decisiones]] para el registro de la decisión. El proceso de validación (`hypothesis-gate`, walk-forward anclado, DSR, reglas de corte pre-registradas) **no cambia** — se traslada intacto al nuevo marco.

Este documento queda como **registro histórico del marco XAUUSD** desde acá en adelante — los cuatro criterios de abajo no se reactivan sin una decisión explícita nueva del usuario sobre un enfoque distinto.

## Los cuatro criterios

Cualquiera de los cuatro, por sí solo, es motivo para parar y replantear — no hace falta que se cumplan todos a la vez.

### 1. Horizonte de confirmación sistemáticamente largo

**Si el power analysis (triage de frecuencia, Fase 0 de `hypothesis-gate`) muestra que CUALQUIER hipótesis del diseño actual (macro diario, oro) requiere más de 5-7 años de confirmación, el problema es el diseño (frecuencia demasiado baja para el tamaño de efecto que este mercado/instrumento parece dar), no la hipótesis puntual.**

Ya hay un precedente real de esto: DFII10, con el mejor resultado de las 4 hipótesis macro probadas hasta ahora, necesitaría ~13 años más de holdout para 80% de poder. Si el próximo candidato da un horizonte similar (y no hay ninguna razón de diseño para esperar que sea distinto — la frecuencia de eventos macro diarios en un solo instrumento es lo que es), ese patrón repetido es la señal, no la excepción.

### 2. Espacio de búsqueda agotado

**Si al listar las próximas 5 hipótesis candidatas, con racional económico distinto entre sí y frecuencia adecuada, no aparecen 5 candidatos genuinamente no solapados (ver `factor-independence` para qué significa "no solapado"), el espacio de búsqueda dentro de "macro diario + oro" se agotó.**

No es lo mismo tener 5 nombres en una lista (ver [[Candidatos futuros]]) que tener 5 mecanismos económicos realmente distintos — varios candidatos de la lista actual (DXY, spread de tasas, breakevens de inflación) son, en el fondo, expresiones del mismo régimen de política monetaria. Si al depurar por racional independiente la lista se achica a 1-2, es la misma señal que el criterio 1 pero desde el lado de la oferta de hipótesis, no de la confirmación estadística.

### 3. Patrón sistemático de falla TRAIN→TEST

**Si múltiples hipótesis distintas (no solo variantes de la misma) fallan con el MISMO patrón — señal con edge aparente en TRAIN que se diluye o desaparece en TEST, de forma consistente — eso apunta a algo estructural en contra, no a mala suerte hipótesis por hipótesis.**

Ya hay un antecedente de este patrón dentro de la familia EMA9/21 (5 variantes fallando de forma convergente motivó cerrar la familia entera, no seguir iterando variante por variante — ver [[Bitácora de decisiones]], 2026-07-24). Este criterio extiende esa misma lógica un nivel arriba: si pasa de nuevo entre familias de hipótesis distintas (no solo dentro de una), es la señal de que el patrón no es de la familia, es del enfoque completo.

### 4. Presupuesto explícito

**Máximo 4 hipótesis más, o 6 meses de calendario (desde 2026-07-27), lo que llegue primero, antes de reconsiderar explícitamente si "XAUUSD + macro diario" es el marco correcto.**

Esto no es "parar de trabajar en 6 meses" — es un punto de checkpoint obligatorio, no automático: al llegar a cualquiera de los dos límites, se hace explícitamente la pregunta "¿seguimos con este marco?" en vez de seguir por inercia. Fecha límite de calendario: **2027-01-27**. Contador de hipótesis: se lleva en [[Bitácora de decisiones]] (contar desde este cambio de objetivo en adelante, no las 4 macro ya evaluadas antes de este criterio).

## Qué significa "replantear el marco" (si se dispara cualquier criterio)

No está decidido de antemano qué se haría — eso sería fijar la respuesta antes de tener la pregunta real. Opciones que quedarían sobre la mesa, sin comprometerse a ninguna ahora: cambiar de instrumento, subir la frecuencia (intradía — ver NO HACER abajo, es una opción anotada, no descartada para siempre), aceptar la biblioteca de factores tal como esté en ese momento aunque sea chica, o pausar el proyecto. La decisión, si llega el momento, es del usuario — este documento define CUÁNDO se activa la pregunta, no la respuesta.

## NO HACER (descartado a propósito en esta etapa, 2026-07-27 — no es una lista de pendientes, es una lista de límites deliberados)

- **Nada de modelos de ML ni optimización de pesos de portfolio.** La regla de combinación de `factor-independence` (pesos iguales, risk-parity como mucho) es la única permitida — no se reconsidera esto dentro del presupuesto actual.
- ~~No pivotear a intradía.~~ **Derogado 2026-08-04** — ver [[Bitácora de decisiones]]. Se habilitan H4/H1 sobre XAUUSD (motivo: triage de frecuencia agotó el universo macro-diario, ronda 2026-08-03, 0/8 candidatos viables).
- **No escribir un "Protocolo de Investigación" formal completo, ni buscar auditoría externa.** Solo las piezas puntuales ya incorporadas (data dictionary, bitácora, checklist, criterios de cierre) — no un documento paraguas más grande que las une.
- **No tocar el diseño de DFII10 para "generar más señales".** Está archivado como factor (ver [[Objetivo del proyecto - biblioteca de factores]]), no en research activo — no se le agregan variantes ni triggers técnicos para intentar mejorarlo.
- **No probar más variantes de DXY sintético como driver de oro (agregado 2026-08-04).** Tres diseños distintos sobre el mismo driver fallaron: nivel/caída sostenida ([[Macro DXY - fase 1]], p=0.072), momentum diario ([[Macro Momentum DXY - fase 1]], t=-0.986/p=0.324), y momentum H4 ([[Macro Momentum DXY H4 - fase 1]], t=-2.862/p=0.0042 — edge **negativo** y estadísticamente significativo, no solo "no significativo"). Dos fallos consecutivos de momentum (diario y H4, mecanismos distintos, mismo driver) con el segundo mostrando un edge negativo real es evidencia de que el problema es el **driver** (DXY sintético como predictor de oro), no el diseño puntual de cada intento — mismo tipo de patrón que ya cerró la familia EMA9/21 completa el 2026-07-24 (variantes distintas fallando de forma convergente, ver criterio 3 de arriba). No se prueban variantes nuevas de DXY (otro k, otro M, otra ventana, otro timeframe) sin una razón *nueva* que no sea "ajustar el diseño hasta que funcione" — eso sería la misma racionalización post-hoc que `hypothesis-gate` existe para evitar.

## Ver también
[[Objetivo del proyecto - biblioteca de factores]] · [[Candidatos futuros]] · [[Bitácora de decisiones]] · [[Checklist paso a cuenta demo]]
