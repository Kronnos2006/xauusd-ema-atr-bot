---
name: hypothesis-gate
description: Aplica la disciplina completa de validación a cualquier hipótesis nueva de trading (macro, técnica, o de cualquier otro tipo) antes de escribir o aceptar código de backtest, y audita resultados ya corridos contra la misma vara. Usar en cuanto el usuario proponga probar una señal/regla nueva, o cuando se presente un resultado de walk-forward para decidir si "pasa el checkpoint".
---

# Hypothesis Gate

Formaliza la disciplina que le costó al proyecto retirar 5 variantes de la familia EMA9/21 antes de encontrarla, y que sí funcionó para la hipótesis macro DFII10 (ver `Macro DFII10 - fase 1` en el vault). El objetivo no es burocracia — es evitar gastar iteraciones a ciegas y evitar data snooping / multiple-comparisons sin darse cuenta.

Desde 2026-07-27 el objetivo del proyecto es construir una biblioteca de factores independientes de baja correlación, no encontrar una sola señal fuerte (ver `Objetivo del proyecto - biblioteca de factores` en el vault) — esto no relaja ningún criterio de acá, si acaso lo endurece: un factor débil solo vale la pena agregarlo a la biblioteca si además de pasar este gate aporta algo no correlacionado (ver skill `factor-independence`).

## Fase 0 — Triage de frecuencia (lo primero, antes de cualquier otra cosa)

**Agregado 2026-07-27, la lección más cara de este proyecto**: la hipótesis macro DFII10 pasó el checkpoint exploratorio (Fase 1-2 completas), sobrevivió una auditoría entera de robustez (spread, look-ahead vía ALFRED, métricas duras) — y solo al final, con un power analysis que se podría haber corrido en 5 minutos, se descubrió que confirmarla con confianza estadística sólida necesitaba ~13 años más de holdout. Ese cálculo tenía que haber sido lo PRIMERO, no lo último.

Antes de escribir un solo backtest completo (antes incluso de la Fase 1 de abajo):

1. **Chequeo de frecuencia liviano**: contar episodios/año de la señal candidata sobre el histórico disponible, sin simular un solo trade todavía (mismo patrón que `diagnostico_frecuencia_dfii10.py` / `_dxy.py` / `_ratio_oro_plata.py` — reusar ese patrón, no reescribirlo).
2. **Power analysis con un tamaño de efecto TÍPICO** (no el de la hipótesis candidata, que todavía no existe) — usar `triage_frecuencia.py`, que ya trae los tamaños de efecto observados en las hipótesis macro de este proyecto (media R ≈ 0.18-0.23, std R ≈ 1.1) como referencia. Elegir el efecto de referencia por similitud de diseño con la hipótesis candidata, y decir por qué.
3. **Traducir el n necesario para 80% de poder a años**, usando la frecuencia del paso 1. Si el horizonte proyectado **supera ~5 años, se descarta ahí mismo** — no se pasa a la Fase 1, no se escribe el pipeline completo, no se gasta más tiempo. Documentar el descarte igual (frase falsable + por qué falló el triage), para que quede registrado y no se reintente sin una razón nueva.

Este triage es deliberadamente pesimista (proyecta el horizonte completo desde cero, no desde datos ya acumulados) — es correcto que lo sea, porque corre ANTES de tener ningún trade real. Si una hipótesis pasa el triage y más adelante, con datos ya acumulados, el horizonte restante recalculado da distinto, eso es normal y no invalida el triage inicial.

### Caso especial — hipótesis tipo portfolio (Sharpe), no trade discreto

**Agregado 2026-08-09, tras la discusión de H4 (carry FX, Fase 4 Invenio)**: los pasos 1-3 de arriba asumen un sistema de trades discretos con R-multiple por señal (entrada/salida, stop/target) — el caso de DFII10, DXY sintético, ratio oro/plata. Una hipótesis de **portfolio de rebalanceo periódico, siempre invertido, evaluada por Sharpe anualizado** (ej. H3 momentum cross-sectional, H4 carry FX — long/short sobre un universo, rebalanceo mensual) es dimensionalmente distinta: no tiene "trades" con R-multiple, y los tamaños de efecto catalogados en `EFECTOS_OBSERVADOS` (R-multiple por trade) NO son aplicables sin un error de unidades.

Para este caso, la potencia de un test de Sharpe con retornos ~iid depende de los **años** de datos, no de la frecuencia de rebalanceo ni de la frecuencia de muestreo de los retornos (diario vs. mensual da el mismo resultado en años — el Sharpe ya está normalizado por frecuencia, la `f` se cancela algebraicamente). Dos formas de aplicar el mismo principio, `investigacion/fase4/triage_frecuencia_h4.py`:

1. **Años necesarios dado un Sharpe típico** (mismo enfoque que el triage estándar, con el efecto expresado como Sharpe anual en vez de R-multiple): `años_necesarios = ((z_alpha+z_beta) / Sharpe_típico) ** 2`. El Sharpe típico se elige por precedente de diseño más cercano en el proyecto (ej. el Sharpe real ya observado en una hipótesis hermana con el mismo mecanismo exacto), nunca el objetivo de la propia hipótesis candidata.
2. **MDE (minimum detectable effect), preferible cuando se cuestione el Sharpe típico elegido**: da vuelta la pregunta y no depende de asumir ningún Sharpe — dados los años de datos que realmente se van a usar en la ventana de decisión (ej. Validation), `MDE = (z_alpha+z_beta) / √T_años` da el Sharpe verdadero más chico que esos años podrían distinguir del ruido con 80% de poder. Comparar el MDE contra el propio umbral de Sharpe pre-registrado en la regla de corte (Fase 1, punto 2): si el umbral está por debajo del MDE, la hipótesis pide un resultado que su propia ventana de datos no tiene forma de confirmar aunque el efecto fuera real — descartar ahí, sin necesidad de debatir qué Sharpe típico asumir.

Ni la autocorrelación débil (ACF(1) de una magnitud típica de mercados FX, ~0.05-0.15) ni el ajuste por dependencia temporal más fina (HAC, variance ratio) cierran una brecha de más de ~2x en Sharpe o de varias veces en años — esos ajustes solo importan cuando la brecha ya es chica. Si el MDE (o el horizonte en años) falla por un margen grande, no vale la pena construir el walk-forward/Monte Carlo/stress-test completo para "verlo de todas formas": foldear reduce aún más los años efectivos por fold, empeorando el problema, no resolviéndolo (mismo patrón que llevó a crear este triage tras el caso DFII10).

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
- [ ] **Deflated Sharpe Ratio (DSR)**, agregado 2026-07-27 — no reemplaza el t-stat de arriba, lo complementa con algo que el t-stat simple no corrige: cuántas variantes se probaron para llegar a este resultado. Usar `deflated_sharpe.py` (implementa Bailey & López de Prado 2014, sin scipy). Requiere estimar **N = número de variantes probadas** — contar la grilla completa evaluada en cada fold (ej. 3×3=9 combinaciones × 4 folds = 36), no solo "1 hipótesis"; si hay hipótesis hermanas de diseño similar ya descartadas (ej. otras macro diarias sobre el mismo activo), sumarlas también y decir por qué. Subestimar N invalida la corrección — ante la duda, redondear hacia arriba, no hacia abajo. Umbral: **DSR ≥ 0.95** para pasar (95% de confianza de que el Sharpe verdadero supera el esperable por puro azar de N pruebas). Ejemplo real: DFII10 con N=39 variantes estimadas dio DSR=0.37 — su Sharpe por trade (0.20) está *por debajo* del Sharpe esperado por azar con esa cantidad de intentos (0.235), algo que el t-stat simple (que no sabe cuántas variantes se probaron) no podía mostrar.
- [ ] **R neto de spread/costos**, no R teórico bruto.
- [ ] **Verificación cruzada de la fuente de datos** si es una fuente nueva (ej. comparar dos proveedores del mismo dato, como se hizo con FRED vs. home.treasury.gov para DFII10) — Y, si la fuente puede ser objeto de revisiones retroactivas (a diferencia de series de mercado como DFII10, que no lo son), verificar además contra ALFRED que el dato usado en el backtest coincide con el dato "tal como se conocía" en cada fecha histórica, no con la versión revisada de hoy.

## Veredicto

Reportar como **PASA EL CHECKPOINT** o **NO LISTO**, nunca una zona media ambigua:

- Si falla el triage de la Fase 0, es **DESCARTADO EN EL TRIAGE** — ni siquiera se evalúa la Fase 1, se documenta el descarte y se pasa al siguiente candidato.
- Si falta cualquier ítem de la Fase 1, es **NO LISTO** — no se escribe código todavía, se listan los puntos que faltan.
- Si falta cualquier chequeo de la Fase 2 sobre un resultado ya corrido, es **NO LISTO PARA DECIDIR** — se listan los chequeos pendientes antes de que el usuario tome la decisión de avanzar o no.
- Si todo está, reportar el veredicto con sus reservas explícitas aunque pase (t-stat marginal, límite de régimen conocido, etc. — "pasa el checkpoint" no es lo mismo que "sin matices", ver el precedente de macro DFII10 fase 1).
- Un "pasa" NUNCA implica automáticamente pasar a la fase siguiente (ej. agregar un trigger técnico, ir a demo/producción) — eso es una decisión nueva y aparte que el usuario tiene que tomar explícitamente, mostrándole primero qué es lo que se ganaría y qué falta (mismo estándar aplicado, no uno relajado).

## Por qué importa

Este mismo estándar es lo que evitó gastar 5-6 iteraciones más a ciegas en la familia EMA9/21, y lo que hizo que la hipótesis macro DFII10 se documentara con sus reservas en vez de venderse como más sólida de lo que es. Saltarse cualquiera de estos pasos no ahorra tiempo real — mueve el costo a después, cuando ya hay código y resultados en los que da pena tirar el trabajo.

El triage de frecuencia (Fase 0) y el DSR (Fase 2) se agregaron el 2026-07-27 por la misma razón, aplicada retroactivamente: DFII10 gastó una auditoría completa de robustez antes de que un power analysis de 5 minutos mostrara que el horizonte de confirmación era de años, no de meses; y su t-stat marginal (p=0.059) se veía "casi significativo" hasta que el DSR reveló que, contando las variantes realmente probadas, su Sharpe está por debajo de lo esperable por puro azar. Ninguno de los dos cambios es un capricho metodológico — los dos existen porque ya costaron tiempo real una vez.
