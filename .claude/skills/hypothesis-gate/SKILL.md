---
name: hypothesis-gate
description: Aplica la disciplina completa de validación a cualquier hipótesis nueva de trading (macro, técnica, o de cualquier otro tipo) antes de escribir o aceptar código de backtest, y audita resultados ya corridos contra la misma vara. Usar en cuanto el usuario proponga probar una señal/regla nueva, o cuando se presente un resultado de walk-forward para decidir si "pasa el checkpoint".
---

# Hypothesis Gate

Formaliza la disciplina que le costó al proyecto retirar 5 variantes de la familia EMA9/21 antes de encontrarla, y que sí funcionó para la hipótesis macro DFII10 (ver `Macro DFII10 - fase 1` en el vault). El objetivo no es burocracia — es evitar gastar iteraciones a ciegas y evitar data snooping / multiple-comparisons sin darse cuenta.

## Fase 1 — Antes de escribir una sola línea de código

No se abre ningún archivo de backtest nuevo, no se corre nada, hasta tener esto escrito y mostrado al usuario:

1. **Frase falsable concreta**: una oración verificable de qué señal específica se prueba y qué predice. "Probar algo macro" o "otro timeframe" NO pasa este filtro — tiene que tener la forma de "cuando [condición medible] entonces [resultado esperado] en [horizonte]". Ejemplo real que sí pasó: *"cuando DFII10 viene cayendo de forma sostenida en los últimos N días hábiles, el oro tiene sesgo alcista sostenido en las M sesiones siguientes"*.
2. **Regla de corte fijada de antemano**: qué resultado numérico específico cuenta como "pasa" y cuál como "no pasa" — decidido ANTES de ver un solo resultado. Si la regla se ajusta después de mirar los números, ya no es una regla de corte, es racionalización post-hoc.
3. **Número de folds derivado, no fijo**: el piso mínimo de trades por fold (30, convención del proyecto desde los fixes metodológicos del 22/07 — ver punto de Fase 2) es el dato fijo; el número de folds sale de ahí, no al revés. Antes de declarar cuántos folds, correr un chequeo de frecuencia (cuántos episodios/trades da la señal sobre el histórico disponible para esta hipótesis puntual) y elegir el número de folds más alto tal que el fold más chico siga respetando el piso de 30. Esto es lo que ya pasó en la práctica en este proyecto (9 folds para la familia EMA, 4 para macro DFII10) sin que nunca se dijera como regla explícita — no tomar ninguno de esos dos números como default para una hipótesis nueva; recalcularlo cada vez contra su propia frecuencia de señal. Si el piso de 30 se baja para poder tener más folds, decir explícitamente por qué y qué se pierde en confianza estadística.
4. **Si reusa una grilla de parámetros ya barrida en una fase anterior de la misma hipótesis**: marcarlo como prohibido salvo justificación explícita — ese barrido ya se gastó, repetirlo sobre el mismo tramo histórico es el mismo riesgo de multiple-comparisons que motivó todo este proceso.

Si el usuario (o un mensaje previo en la conversación) ya saltó directo a "probemos X" sin esto, el paso es frenar y pedir los 4 puntos antes de tocar código — no completarlos por tu cuenta ni asumirlos.

## Fase 2 — Al evaluar un resultado ya corrido

Cuando exista una tabla de walk-forward (o se te pida evaluar una), verificar cada uno de estos puntos explícitamente, uno por uno, no de forma global:

- [ ] **Walk-forward multi-fold real**, no un único split train/test. Un solo split no distingue un edge real de suerte en una ventana.
- [ ] **Selección de parámetros hecha en TRAIN de cada fold**, no sobre el dataset completo antes de foldear (data snooping estructural — el bug exacto que se encontró y corrigió en este proyecto, commit `2e4832e`).
- [ ] **Piso mínimo de trades por fold respetado** (o justificado si no).
- [ ] **t-stat con y sin el fold más fuerte**: no hay un porcentaje fijo de "fold dominante" (un umbral tipo ">60% del R neto" se probó y resultó inconsistente entre casos reales de este proyecto — 51% de concentración en el caso M15 sí era señal real de dependencia de un fold, y con un umbral de 60% hubiese pasado sin marcarse). La regla real es recalcular el t-stat/conclusión sacando el fold con mayor R neto y exigir que la conclusión no cambie de forma cualitativa entre "con todos los folds" y "sin el más fuerte" — si pasa con todos pero deja de sostenerse sin el mejor, reportar ambos números y marcarlo como dependiente de un fold, sea cual sea el porcentaje que represente.
- [ ] **t-stat real sobre R neto de los trades TEST**, no el conteo de "folds ganadores" (ej. "3 de 4 folds positivos" suena más fuerte de lo que es — con moneda justa eso pasa ~31% de las veces por azar). Calcular t-stat y p-value explícitamente, con aproximación normal de dos colas como mínimo, en ambas versiones (con y sin el fold más fuerte) del punto anterior.
- [ ] **R neto de spread/costos**, no R teórico bruto.
- [ ] **Verificación cruzada de la fuente de datos** si es una fuente nueva (ej. comparar dos proveedores del mismo dato, como se hizo con FRED vs. home.treasury.gov para DFII10).

## Veredicto

Reportar como **PASA EL CHECKPOINT** o **NO LISTO**, nunca una zona media ambigua:

- Si falta cualquier ítem de la Fase 1, es **NO LISTO** — no se escribe código todavía, se listan los puntos que faltan.
- Si falta cualquier chequeo de la Fase 2 sobre un resultado ya corrido, es **NO LISTO PARA DECIDIR** — se listan los chequeos pendientes antes de que el usuario tome la decisión de avanzar o no.
- Si todo está, reportar el veredicto con sus reservas explícitas aunque pase (t-stat marginal, límite de régimen conocido, etc. — "pasa el checkpoint" no es lo mismo que "sin matices", ver el precedente de macro DFII10 fase 1).
- Un "pasa" NUNCA implica automáticamente pasar a la fase siguiente (ej. agregar un trigger técnico, ir a demo/producción) — eso es una decisión nueva y aparte que el usuario tiene que tomar explícitamente, mostrándole primero qué es lo que se ganaría y qué falta (mismo estándar aplicado, no uno relajado).

## Por qué importa

Este mismo estándar es lo que evitó gastar 5-6 iteraciones más a ciegas en la familia EMA9/21, y lo que hizo que la hipótesis macro DFII10 se documentara con sus reservas en vez de venderse como más sólida de lo que es. Saltarse cualquiera de estos pasos no ahorra tiempo real — mueve el costo a después, cuando ya hay código y resultados en los que da pena tirar el trabajo.
