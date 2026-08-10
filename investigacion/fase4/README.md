# Fase 4 — H4 Carry FX

Proyecto Invenio. Fecha de inicio del experimento: **2026-08-09**.

**Estado: DESCARTADO EN EL TRIAGE DE FRECUENCIA (Fase 0 de `hypothesis-gate`), antes de escribir el pipeline de backtest.** No se descargó el archivo del BIS, no se corrió ningún backtest, no existe código de simulación de trades.

## Hipótesis falsable (pre-registrada, no evaluada)

> Si los diferenciales de tasas de política monetaria entre bancos centrales de países desarrollados y la Fed compensan al inversor por mantener posiciones en monedas de mayor rendimiento, entonces un portfolio mensual que compra las 3 monedas con mayor diferencial positivo (high-carry) y vende las 3 con mayor diferencial negativo (low-carry) contra USD debería producir retorno neto positivo, Sharpe > 0.50 y estabilidad temporal en el período de Validación (2015–2019), después de costos de transacción predefinidos.

Variante pre-registrada única: `H4-carry`, señal = `tasa_moneda_i - tasa_USD` al último día hábil de cada mes, sin parámetro libre de lookback.

## Por qué se descarta acá — triage de frecuencia (Fase 0)

`hypothesis-gate` exige, antes de escribir un solo backtest, un power analysis con un tamaño de efecto típico proyectado a años de datos necesarios; si supera ~5 años, se descarta sin pasar a Fase 1. Script: `triage_frecuencia_h4.py`.

H4 no es un sistema de trades discretos (a diferencia de DFII10, DXY sintético, ratio oro/plata, que sí tienen catalogados tamaños de efecto R-multiple por trade en `triage_frecuencia.EFECTOS_OBSERVADOS`). Es un portfolio de rebalanceo mensual, siempre invertido, evaluado por Sharpe anualizado. Para un test de Sharpe con retornos ~iid, la potencia depende de los **años** de datos, no de la frecuencia de rebalanceo (el propio Sharpe ya está normalizado por frecuencia):

```
años_necesarios = ((z_alpha + z_beta) / Sharpe_típico) ** 2      [alpha=0.05, poder=0.80, dos colas]
```

**Tamaño de efecto típico usado**: el precedente de diseño más cercano en este proyecto es **H3** (momentum cross-sectional FX, Fase 3, cerrada 2026-08-08) — comparte exactamente el mismo mecanismo (9 monedas, buckets 3 long/3 short/3 flat, rebalanceo mensual, mismo modelo de costos). Los 3 Sharpe anualizados de H3 en Train (2005–2014) fueron +0.111, +0.276 y −0.215 — rango [−0.22, +0.28], magnitud promedio ≈0.20. Se usa `Sharpe_típico=0.20` en vez de los efectos R-multiple de las hipótesis basadas en trades (no son comparables dimensionalmente a un Sharpe de portfolio).

| Sharpe típico usado | Años necesarios (80% poder) | vs. límite (5 años) |
|---|---|---|
| 0.20 (precedente H3, Train) | **197 años** | falla por ~39x |
| 0.50 (objetivo propio de H4 — solo contraste, no válido como efecto "típico" per Fase 0) | **32 años** | falla por ~6x |

Incluso usando el propio objetivo optimista de H4 (Sharpe>0.50) como si fuera el efecto real — algo que la Fase 0 prohíbe explícitamente porque el efecto de la hipótesis candidata "todavía no existe" — el horizonte necesario (32 años) supera ampliamente los 5 años de Validación, e incluso los 15 años combinados de Train+Validation del diseño pre-registrado.

**Lectura importante, no exclusiva de H4**: este resultado es un problema estructural de *cualquier* portfolio de rebalanceo mensual evaluado por Sharpe sobre una sola ventana de Validación de 5 años en este universo de FX — no algo específico del carry. La potencia de un test de Sharpe escala con años de datos, no con el número de posiciones o de monedas en el universo. H3 (mismo mecanismo) ya cerró con Sharpe negativo en Validation en las 3 variantes; este triage sugiere que, incluso si hubiera existido una señal real de magnitud típica de este proyecto (~0.20-0.30), la ventana de 5 años no tenía potencia estadística para distinguirla del ruido — consistente con, pero no prueba de, que el resultado negativo de H3 haya sido más ruido que señal real.

## Revisión del usuario (2026-08-09) y reformulación con MDE

El usuario cuestionó el cálculo de "años necesarios", con razón en varios puntos: (1) depende de asumir un Sharpe típico (0.20) que es una hipótesis, no un hecho conocido; (2) el backtest tiene riesgo adicional de multiple-testing/selección de modelos, no capturado acá; (3) el mercado no es estacionario — 15 años de historia no son necesariamente 15 años de la misma distribución; (4) la ACF(1) negativa encontrada empíricamente en los retornos diarios de H3 (−0.09 a −0.12 en Train, −0.03 a −0.05 en Validation) no alcanza para descartar dependencia temporal más compleja (multi-lag, heterocedasticidad, clustering de volatilidad) sin un análisis más completo (PACF, HAC, variance ratio).

Los puntos (2) y (3) no rescatan a H4 — ambos añaden riesgo, no lo quitan. El punto (4) es válido como objeción metodológica a la profundidad del chequeo, pero la brecha en cuestión (ver tabla de MDE abajo) es demasiado grande (>2x en Sharpe) para que ajustes finos por dependencia temporal la cierren.

El punto (1) es el importante, y se resuelve dando vuelta la pregunta para no depender de ningún Sharpe asumido: en vez de "¿cuántos años hacen falta para detectar un Sharpe de X?", **¿cuál es el Sharpe verdadero más chico que los años realmente disponibles podrían distinguir del ruido?** (minimum detectable effect, MDE = `(z_alpha+z_beta)/√T`, función `mde_sharpe()` en `triage_frecuencia_h4.py`):

| Ventana | T (años) | Sharpe mínimo detectable (80% poder, α=0.05) |
|---|---|---|
| Validation 2015–2019 (la ventana real de decisión, criterio A) | 5 | **1.253** |
| Train 2005–2014 | 10 | 0.886 |
| Train+Validation combinados (no es como está diseñado el gate) | 15 | 0.723 |

El propio criterio A pre-registrado de H4 (Sharpe > 0.50) queda **por debajo del MDE en las tres ventanas** — incluso con los 15 años combinados. Es decir: el diseño de H4, tal como está pre-registrado, pide un resultado que sus propios datos no tienen forma de confirmar aunque el efecto fuera exactamente el que se busca. Esta versión no requiere ningún supuesto sobre el Sharpe real de H4 ni sobre H3 — solo el número de años disponibles, que es un dato fijo del diseño.

## Veredicto final

**Se mantiene el descarte** (confirmado por el usuario 2026-08-09 tras la revisión anterior), ahora apoyado en el MDE además del cálculo original de años-necesarios. Lo que cambiaría esta conclusión no es un ajuste fino de la dependencia temporal de este mismo diseño, sino un diseño que genere más años-equivalentes de información independiente (ver "Próximo paso" abajo).

## Qué no se hizo (correctamente, por el triage)

- No se descargó el archivo del BIS.
- No se escribió `h4_carry_fx.py` ni `utils_fase4.py`.
- No se corrió ningún backtest de Train, Validation ni Test.
- No se evaluaron los criterios A–D.

## Próximo paso

Decisión del usuario — no se reintenta esta hipótesis (ni ningún diseño de portfolio de rebalanceo mensual similar en este universo) sin una razón nueva explícita. Opciones típicas que cambiarían el resultado del triage (a discutir, ninguna implementada):
- Cambiar el diseño para generar más años-equivalentes de datos independientes (ej. universo mucho más amplio de monedas/activos con panel cruzado, si la correlación real entre ellos lo permite — ver el ajuste por N_efectivo que ya se usó en TF_Basket_H1).
- Bajar el umbral de Sharpe objetivo (pero un objetivo más bajo es un objetivo menos interesante económicamente, y no cambia que 5 años sigue siendo poca potencia salvo que el Sharpe típico real fuera mucho más alto de lo que este proyecto ha observado hasta ahora).
- Aceptar este patrón (H3 y H4 con el mismo problema estructural de potencia) como evidencia adicional para la decisión pendiente más amplia sobre el enfoque del proyecto (ver `CLAUDE.md`, sección "Próxima decisión pendiente").
