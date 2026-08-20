# Criterios de cierre del enfoque completo

Índice: [[Bienvenido]] · Ver también [[Objetivo del proyecto - biblioteca de factores]] · [[Candidatos futuros]] · [[Bitácora de decisiones]]

Escrito el 2026-07-27 (revisión externa, punto 5), **antes de que haga falta** — mismo espíritu que [[Checklist paso a cuenta demo]]. Esto no es sobre cuándo se descarta UNA hipótesis (eso ya lo cubre `hypothesis-gate`) — es sobre cuándo el problema deja de ser "falta encontrar la hipótesis correcta" y pasa a ser el **diseño completo** del proyecto: XAUUSD, frecuencia macro diaria, mercado de oro. Si eso pasa, la respuesta no es "una hipótesis más", es replantear el marco.

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
- **No pivotear a intradía.** Queda anotado como opción futura (ver arriba, "qué significa replantear el marco"), no se ejecuta ahora ni se investiga en paralelo.
- **No escribir un "Protocolo de Investigación" formal completo, ni buscar auditoría externa.** Solo las piezas puntuales ya incorporadas (data dictionary, bitácora, checklist, criterios de cierre) — no un documento paraguas más grande que las une.
- **No tocar el diseño de DFII10 para "generar más señales".** Está archivado como factor (ver [[Objetivo del proyecto - biblioteca de factores]]), no en research activo — no se le agregan variantes ni triggers técnicos para intentar mejorarlo.

## Ver también
[[Objetivo del proyecto - biblioteca de factores]] · [[Candidatos futuros]] · [[Bitácora de decisiones]] · [[Checklist paso a cuenta demo]]
