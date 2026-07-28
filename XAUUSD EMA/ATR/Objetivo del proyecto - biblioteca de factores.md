# Objetivo del proyecto — biblioteca de factores

Índice: [[Bienvenido]] · Ver también [[Criterios de cierre del enfoque]] · [[Candidatos futuros]] · [[Macro DFII10 - fase 1]]

## Cambio de objetivo (2026-07-27) — el más importante de esta ronda de revisión

**Objetivo anterior**: encontrar una señal fuerte para operar (una hipótesis que pase el checkpoint con margen y vaya a demo).

**Objetivo nuevo**: construir una biblioteca de factores independientes de baja correlación que, combinados, puedan producir un edge robusto — ningún factor individual necesita ser fuerte por sí solo si aporta algo que los demás no aportan.

## Por qué el cambio

Después de 4 hipótesis macro evaluadas (DFII10, 2s10s, ratio oro/plata, DXY sintético) con la misma disciplina de walk-forward, ninguna produjo un edge individual lo bastante fuerte como para justificar operar sola. DFII10 es el caso más informativo: pasa el checkpoint exploratorio con reservas (t-stat marginal, p=0.059), sobrevive una auditoría completa de robustez (spread, look-ahead, métricas duras), pero el power analysis mostró que confirmar esa señal sola con confianza estadística sólida necesitaría ~13 años más de datos — un plazo que hace inviable tratarla como candidata a "la" señal del proyecto.

Esto no invalida el trabajo hecho — al contrario, es exactamente el tipo de resultado que la disciplina de este proyecto está diseñada para producir con honestidad: **un efecto real, pero económicamente débil quizás combinado con otros, no una señal ganadora aislada**. Insistir en encontrar una sola señal fuerte en un mercado (oro) y frecuencia (macro diario) donde ya se agotaron 4 intentos con resultados marginales/débiles de forma consistente es la señal de que el objetivo original estaba mal planteado, no de que falte "una hipótesis más".

## Qué implica en la práctica

- **DFII10 se reclasifica**: de "hipótesis activa, en holdout esperando confirmación" a **"factor archivado — efecto real pero económicamente débil"**. Sigue con monitoreo pasivo (el logger en vivo y el monitor de holdout continúan corriendo, sin costo), pero **sin research activo** — no se invierte más tiempo de diseño en confirmarla sola. Ver [[Macro DFII10 - fase 1]] para el detalle completo de por qué.
- **Ninguna hipótesis nueva se evalúa ya con la pregunta "¿esto solo alcanza para operar?"** — la pregunta correcta pasa a ser "¿esto aporta algo que los factores ya archivados no aportan?" (ver [[factor-independence]] skill).
- **El triage de frecuencia se vuelve el primer filtro de cualquier candidato nuevo** (ver `hypothesis-gate` actualizado): si el horizonte de confirmación proyectado supera ~5 años, se descarta antes de gastar tiempo en el pipeline completo — la lección directa y más cara de DFII10.
- **El proyecto tiene un presupuesto explícito y una fecha de replanteo**, no una búsqueda indefinida — ver [[Criterios de cierre del enfoque]].

## Qué NO cambia

- La disciplina de validación (walk-forward anclado, TRAIN elige/TEST confirma, piso de trades, t-stat con y sin fold dominante, verificación de fuente de datos) sigue exactamente igual — se refuerza, no se relaja.
- El resto de las hipótesis ya cerradas (familia EMA9/21, 2s10s, ratio oro/plata, DXY sintético) mantienen su veredicto tal como está documentado — este cambio es de objetivo hacia adelante, no una reevaluación retroactiva.

## Ver también
[[Criterios de cierre del enfoque]] · [[Candidatos futuros]] · [[Macro DFII10 - fase 1]] · [[Metodología]]
