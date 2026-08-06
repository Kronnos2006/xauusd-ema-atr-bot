# TF_Basket_H1 — Trend Following (Donchian/MA)

## Descartado en el triage (2026-08-06) — confirmado por el usuario, marco cerrado

Índice: [[Bienvenido]] · Ver también [[Cierre formal del proyecto - 2026-08-05]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]] · [[Bitácora de decisiones]]

Cuarto marco de investigación del proyecto (tras XAUUSD walk-forward, EURUSD walk-forward y EURUSD event study, todos cerrados el 2026-08-04/05), y el primero descartado íntegramente en Fase 0 — nunca llegó a Fase 1 ni a walk-forward. De las 6 señales pre-registradas, 4 no pasaron el triage de frecuencia inicial; de las 2 que sobrevivieron (Donchian 20, MA 10/50), ninguna mostró edge viable en el panel cruzado Moskowitz-style con efecto empírico propio: Donchian 20 sin edge real (t≈-0.04, prácticamente cero), MA 10/50 con edge chico y no significativo (t≈0.93, p=0.35) cuyo Sharpe de portfolio implícito (0.229) ya queda por debajo del objetivo de la hipótesis (Sharpe>0.3) **antes de restar costos de transacción**. Horizonte necesario para 80% de poder: 149.3 años — no es problema de muestra ni de método, es la respuesta real de los instrumentos disponibles. Detalle completo de las tres corridas de Fase 0 más abajo.

**Nota (2026-08-06, mismo día del cierre)**: pese a este descarte, el usuario decidió llevar Donchian 20 a un forward test operativo con capital real acotado ($20) — **Decisión Salida 2**, no una reapertura de esta investigación. La razón nueva no es evidencia empírica distinta (el resultado de arriba se mantiene sin cambios), es un cambio de encuadre explícito: literatura de trend following como respaldo en vez del edge medido en este basket, con el backtest usado como filtro de costos de implementación (no de edge) y salvaguardas operativas (red line de drawdown, capital acotado al 10%, puntos de decisión fijos, el signo del P&L no decide continuidad). Ver `CLAUDE.md` → "FASE FORWARD TEST ACTIVA" y [[Bitácora de decisiones]] (fila "Decisión Salida 2") para las condiciones completas.

## Apertura del marco (2026-08-06)

Reapertura explícita de investigación, decidida por el usuario tras la pausa activa fijada en [[Cierre formal del proyecto - 2026-08-05]]. Primer marco desde el cierre de los tres anteriores (XAUUSD walk-forward, EURUSD walk-forward, EURUSD event study) — cambio de fondo respecto a los tres: pasa de driver macro a señal técnica de tendencia (Donchian/MA), y de instrumento único a basket diversificado de 10 activos.

## Estado del gate (`hypothesis-gate`): Fase 0 completa (2026-08-06) — DESCARTADO EN EL TRIAGE

Tres corridas sucesivas de Fase 0, cada una corrigiendo la limitación de la anterior: (1) efecto DFII10 prestado → 2/6 señales pasaban, pero el efecto no era de diseño equivalente; (2) efecto derivado del Sharpe objetivo de la ficha → las 2 señales sobrevivientes DESCARTAN por un problema estructural (87.2 años, invariante a la frecuencia — no un problema de datos); (3) panel cruzado instrumento×día Moskowitz-style con efecto empírico propio (no prestado ni derivado circularmente) → **DESCARTADO EN EL TRIAGE para las dos señales**, con datos reales, no un artefacto del método de cálculo. Ver "Veredicto Fase 0" más abajo para el resultado final y la recomendación.

## Fase 0 — Resultado del triage de frecuencia (2026-08-06)

Script: `diagnostico_frecuencia_tf_basket_h1.py`. Ventana 2010-01-01 → hoy (2026-08-06), D1, los 10 instrumentos del basket. Episodio = flip de dirección (Donchian: breakout N-días con `shift(1)` sin look-ahead; MA cruce: cambio de signo de `MA_rápida - MA_lenta`).

### Flips totales por instrumento × señal

| Instrumento | Donchian20 | Donchian55 | Donchian100 | MA50/200 | MA20/100 | MA10/50 |
|---|---|---|---|---|---|---|
| EURUSD | 135 | 46 | 24 | 28 | 56 | 123 |
| USDJPY | 140 | 37 | 25 | 23 | 52 | 122 |
| GBPUSD | 143 | 40 | 27 | 27 | 51 | 127 |
| XAUUSD | 125 | 47 | 23 | 25 | 49 | 99 |
| XAGUSD | 139 | 53 | 23 | 25 | 67 | 119 |
| TLT | 132 | 46 | 23 | 25 | 47 | 114 |
| LQD | 134 | 41 | 31 | 23 | 47 | 111 |
| GDX | 129 | 49 | 27 | 29 | 67 | 91 |
| XLE | 129 | 53 | 28 | 24 | 58 | 116 |
| NVDA | 112 | 40 | 19 | 15 | 52 | 124 |

### Basket agregado (suma de flips de los 10 instrumentos) y power analysis

Efecto de referencia: DFII10 (macro diario), media R=0.230, std R=1.135 — **única hipótesis del proyecto con media_R y std_R completos**, usada a falta de un precedente de diseño equivalente (evento macro direccional vs. sistema de flips de tendencia continuo). Esto es una limitación real del triage, no una equivalencia de diseño — señalada explícitamente, no asumida en silencio. n necesario para 80% de poder (α=0.05, dos colas): **192**.

| Señal | Flips totales | Ep/año basket | Horizonte proyectado | Veredicto |
|---|---|---|---|---|
| Donchian 20 | 1318 | 79.9 | 2.4 años | **PASA** |
| MA 10/50 | 1146 | 69.9 | 2.7 años | **PASA** |
| MA 20/100 | 546 | 33.7 | 5.7 años | DESCARTA (marginal, justo sobre el límite de 5) |
| Donchian 55 | 452 | 27.7 | 6.9 años | DESCARTA |
| Donchian 100 | 250 | 15.5 | 12.4 años | DESCARTA |
| MA 50/200 | 244 | 15.4 | 12.4 años | DESCARTA |

**Descartadas en el triage** (no pasan a Fase 1, no se construye pipeline para ellas): Donchian 55, Donchian 100, MA 50/200 — horizonte muy por encima del límite de 5 años. MA 20/100 también descarta, pero por margen estrecho (5.7 vs. 5.0) — a diferencia de las otras tres, un efecto de referencia distinto podría voltear este resultado; no se reintenta sin razón nueva, pero es el caso menos concluyente de los cuatro.

**Pasan el triage**: Donchian 20 y MA 10/50 — únicas dos señales que siguen a Fase 1 (derivar folds) con este diseño.

### Dos supuestos de este triage, explícitos (no confirmados aún)

1. **Unidad de agregación**: la frecuencia se calculó sumando los flips de los 10 instrumentos como una sola muestra pooled ("aplicado a un basket diversificado" se interpretó como sistema evaluado a nivel portfolio, no 10 pruebas independientes). Si en cambio la evaluación fuera por instrumento, cada combinación individual tiene mucha menos frecuencia (ver tabla de arriba) y probablemente ninguna pasaría el triage sola.
2. **Efecto de referencia (DFII10)**: es un diseño macro-diario de evento, no de sistema de tendencia con flips frecuentes — la forma de la distribución de retornos por trade en trend following (muchas pérdidas chicas, pocas ganancias grandes) suele ser distinta a la de un bet direccional macro. Se usó por ser el único precedente calibrado del proyecto con datos reales, no porque sea el más parecido en diseño.

**No tocar el pipeline de backtest hasta confirmar estos dos supuestos y derivar el número de folds** (Fase 1 punto 3, pendiente) — ver "Pendiente antes de tocar código" más abajo.

## Fase 0 — Recálculo con efecto derivado de la ficha (2026-08-06) — DESCARTA

Supuesto 1 (pooling a nivel basket) confirmado por el usuario, citando Moskowitz et al. (2012) como precedente. Supuesto 2 (efecto DFII10 prestado) reemplazado por un efecto derivado de la propia hipótesis:

- Retorno esperado anual = Sharpe objetivo (0.3) × vol objetivo cartera (15%) = **4.5%**
- `media_r` por trade = retorno anual / ep-año
- `std_r` por trade, derivado del escalamiento estándar de Sharpe (`Sharpe_anual = Sharpe_trade × √N`, asumiendo trades i.i.d.): `std_r = media_r × √N / Sharpe_anual`

Script: `mde_trend_following_tf_basket_h1.py` (reusa `n_necesario_80_poder()` de `triage_frecuencia.py`).

| Señal | N (ep/año) | media_r/trade | std_r/trade | n necesario | Horizonte | Veredicto |
|---|---|---|---|---|---|---|
| Donchian 20 | 79.91 | 0.0563% | 1.678% | 6969 | **87.2 años** | DESCARTA |
| MA 10/50 | 69.89 | 0.0644% | 1.794% | 6096 | **87.2 años** | DESCARTA |

**Las dos señales dan exactamente el mismo horizonte (87.2 años) — no es casualidad.** Es un resultado algebraico: cuando `std_r` se deriva escalando por `√N` desde un Sharpe anual fijo, la N se cancela al traducir `n_necesario` a años. Queda:

**años_necesarios = ((z_α+z_β) / Sharpe_objetivo)² = ((1.96+0.84) / 0.3)² ≈ 87.2 años**

— independiente de la frecuencia de trading. Ninguna variante de señal (más rápida o más lenta) cambia este número mientras el Sharpe objetivo y el método de derivar `std_r` se mantengan iguales. Por la regla del proyecto (horizonte > 5 años → descartar en el triage), esto sería **DESCARTADO EN EL TRIAGE** para las dos señales — el peor resultado del proyecto hasta ahora (17× el límite; DFII10, el peor caso previo, dio ~13 años).

**Por qué pasa esto**: confirmar un Sharpe anual de 0.3 vía t-test estándar (sobre trades, meses, o cualquier período, con escalamiento raíz-de-tiempo) siempre necesita ~87 años de track record — es un hecho estructural conocido en trend following/CTAs, no un artefacto de este cálculo. Moskowitz et al. (2012), la referencia citada para aprobar el pooling, no confirman su resultado con 87 años de un único track record: lo consiguen con un panel instrumento×período (cada instrumento-mes como observación quasi-independiente, no una serie ya promediada), y porque combinar ~58 instrumentos poco correlacionados empuja el Sharpe del portfolio *por encima* del Sharpe de cualquier instrumento individual — es esa suba de Sharpe (no el pooling en sí) la que acorta los años necesarios.

**Decisión del usuario (2026-08-06)**: no descartar el marco todavía — rediseñar el test como panel cruzado instrumento×período. En curso, ver siguiente sección.

## Rediseño a panel cruzado (Moskowitz-style) — EN CURSO

Paso 1 (empírico, hecho): correlación real entre los 10 instrumentos del basket, para estimar cuántos "bets" genuinamente independientes hay. Script: `correlacion_basket_tf_h1.py`. Retornos D1, 2010-2026, 4149 días comunes a los 10 instrumentos.

- **Correlación promedio (pares, off-diagonal): 0.1415**
- **N efectivo (fórmula N/(1+(N-1)ρ̄), N=10): 4.40** — de los 10 instrumentos "nominales" del basket, el equivalente en bets independientes es ~4.4, no 10.
- Clusters visibles en la matriz: XAUUSD/XAGUSD/GDX correlacionados (0.67-0.78), TLT/LQD (0.64), EURUSD/GBPUSD (0.63), USDJPY anti-correlacionado con la mayoría. NVDA es el instrumento más independiente del basket (correlación ~0.10-0.14 con el resto).
- Correlación promedio excluyendo NVDA: 0.1513 (prácticamente igual) — NVDA no es el único factor de diversificación, el basket ya tiene bastante estructura de por sí.

**Paso 2 (hecho, 2026-08-06)**: por decisión del usuario, calibración empírica con los datos ya descargados en vez de una referencia académica. Script: `calibracion_efecto_tf_basket_h1.py`. Diseño: retorno diario de la estrategia de señal (`dirección[t-1] × retorno_diario[t]`), normalizado por la vol propia de cada instrumento (unidades "R", mismo concepto que `media_R`/`std_R` del resto del proyecto), pooleado como panel instrumento×día (2010-2026, sin costos, sin sizing — chequeo liviano, no walk-forward). La correlación cruzada entre instrumentos en el mismo día se corrige escalando el N naive (10 instrumentos/día) al N efectivo (4.40, de la matriz de correlación real de arriba).

| Señal | media_R/día | t naive (10 indep., sobreestimado) | t corregido (N_eff=4.40) | p corregido | Sharpe individual anual | Sharpe portfolio implícito (N_eff=4.4) | n necesario (80% poder) | Horizonte |
|---|---|---|---|---|---|---|---|---|
| Donchian 20 | -0.00030 | -0.061 | -0.040 | 0.968 | -0.005 | -0.010 | 88.6M | 79.875 años |
| MA 10/50 | +0.00689 | +1.408 | +0.934 | 0.350 | +0.109 | **+0.229** | 165.593 | **149.3 años** |

**Donchian 20: sin edge detectable, gross de costos.** Efecto prácticamente cero (levemente negativo). No es un problema de tamaño de muestra — con 42.055 observaciones (18.504 efectivas) el t-stat es -0.04, no hay nada que confirmar. **DESCARTADO.**

**MA 10/50: edge positivo pero chico, no significativo con los datos disponibles, e insuficiente incluso en el punto estimado.** t corregido=0.93 (p=0.35, muy lejos de significativo con los ~16.5 años disponibles). El Sharpe de portfolio implícito por diversificación (0.229) **ya queda por debajo del objetivo de la hipótesis (Sharpe>0.3) antes de descontar spread/swap/slippage** — los costos reales solo pueden empeorar este número, nunca mejorarlo. Horizonte para 80% de poder: 149.3 años, ~30× el límite de 5 años del proyecto. **DESCARTADO.**

## Veredicto Fase 0 (panel Moskowitz-style, 2026-08-06): DESCARTADO EN EL TRIAGE

Con el diseño correcto (panel instrumento×día, corrección por correlación cruzada real, efecto empírico propio en vez de prestado o asumido), **ninguna de las dos señales sobrevivientes del triage original muestra un edge viable** — Donchian 20 no tiene edge (t≈0, gross), y MA 10/50 tiene un edge modesto que ni siquiera alcanza el Sharpe objetivo en el punto estimado antes de costos, y necesitaría ~149 años de datos para confirmarse con 80% de poder. Esto no es un problema de diseño del test (ya corregido: pooling correcto, N efectivo, efecto propio) — es la respuesta real de los datos.

**Recomendación**: cerrar TF_Basket_H1 en Fase 0, documentado igual que DFII10/Momentum DXY, sin construir el pipeline de walk-forward — los costos de transacción (todavía no restados) solo empeorarían el resultado de MA 10/50, nunca lo mejorarían.

**Confirmado por el usuario (2026-08-06): marco cerrado en el triage.** No se construyó pipeline de backtest, walk-forward ni folds — el marco no pasó de Fase 0. Sin candidatos pendientes en esta ronda (las 6 señales pre-registradas quedan todas descartadas: 4 en el triage de frecuencia inicial, 2 en el panel Moskowitz-style). No se reintenta este basket/familia de señales sin una razón nueva y específica (ej. otro objetivo de Sharpe, otro basket con menor correlación interna, otra familia de señales). Ver fila correspondiente en [[Bitácora de decisiones]].

## Hipótesis (frase falsable)

SI un sistema trend following (familia Donchian 20/55/100 días + MA cruce 50/200, 20/100, 10/50) aplicado a un basket diversificado genera Sharpe neto OOS > 0.3 en el período 2010-2026, ENTONCES existe un edge explotable en este universo con esta infraestructura.

- **Variable independiente**: dirección de tendencia (señal Donchian/MA)
- **Variable dependiente**: retorno ajustado por riesgo del basket

## Basket (aprobado)

EURUSD, USDJPY, GBPUSD, XAUUSD, XAGUSD, TLT, LQD, GDX, XLE, NVDA

## Familia de señales (pre-registrada, sin optimización posterior)

- Donchian 20 días
- Donchian 55 días
- Donchian 100 días
- MA cruce 50/200 días
- MA cruce 20/100 días
- MA cruce 10/50 días

**Tras el triage de Fase 0 (2026-08-06)**: 4 de las 6 no pasaron el triage inicial de frecuencia; las 2 sobrevivientes (Donchian 20, MA 10/50) tampoco pasaron el panel Moskowitz-style con efecto empírico propio — **las 6 quedan descartadas, ninguna llega a Fase 1**. Ver "Veredicto Fase 0" arriba para el cierre formal. La lista de arriba se deja completa como registro de lo pre-registrado originalmente (no se reescribe retroactivamente).

## Sizing

Vol objetivo 8% por posición, 15% por cartera.

## Costos

Spread + swap reales del terminal + slippage estimado.

## Regla de corte (definitiva, 2026-08-06 — decisión del usuario)

Las cuatro condiciones deben cumplirse a la vez (AND), ninguna es solo diagnóstica:

**Sharpe neto OOS > 0.3 Y DSR ≥ 0.95 Y t pooled > 1.96 Y ≥60% folds rentables.**

Resuelve el conflicto original entre la frase falsable (Sharpe>0.3) y la regla de corte dada por separado (DSR/t/folds) — ambas eran el gate, no una sustituía a la otra. El umbral de DSR se alinea al estándar ya usado en el resto del proyecto (0.95, no el 0.5 propuesto inicialmente), precisamente porque este marco prueba más combinaciones (60: 6 señales × 10 instrumentos) que cualquier hipótesis anterior (9-39 variantes) — más variantes probadas exige más corrección por multiple-comparisons, no menos.

## Pendiente antes de tocar código (bloqueante, `hypothesis-gate`) — cerrado sin pipeline

Todos los puntos de esta lista quedaron sin efecto: el marco se cerró en Fase 0 (2026-08-06, ver "Veredicto Fase 0" y header de cierre arriba), nunca llegó a necesitar folds, walk-forward, ni una unidad de evaluación para el pipeline. Se deja el historial de lo que estaba pendiente en cada momento como registro de cómo avanzó el gate, no como trabajo a retomar:

1. ~~Fase 0 — triage de frecuencia~~ Hecho (2026-08-06) — 2 de 6 señales sobrevivieron el triage inicial.
2. ~~Confirmar los dos supuestos del triage~~ Confirmados por el usuario (pooling aprobado, efecto DFII10 reemplazado por uno derivado de la ficha y luego por uno empírico).
3. ~~Fase 1, punto 3 — número de folds~~ Nunca llegó a correrse — el marco se descartó en Fase 0 antes de este paso.
4. ~~Unidad de evaluación para el walk-forward~~ Sin objeto — no se construyó walk-forward.

## Ver también
[[Cierre formal del proyecto - 2026-08-05]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]] · [[Candidatos futuros]]
