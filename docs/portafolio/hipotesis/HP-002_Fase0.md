# HP-002 — Fase 0: flujos de ETF spot de bitcoin como señal de presión de precio sobre BTC

2026-10-21. Autor: `portafolio-investigador` (pedido del `jefe-portafolio`, convocado por el gerente). Revisión: jefe-portafolio → desconfiado → gerente; jefe-riesgo si avanza.
Estado: **Fase 0 escrita. Veredicto de triage: DESCARTADO EN EL TRIAGE (propuesto)**, pendiente de auditoría.
Relación con PF-001: es la pata "flujos de ETF de BTC" de PF-001. No toca KT-002/KT-003 (mediciones descriptivas de modelos de series de tiempo sobre BTCUSDT); usaría otra señal sobre el mismo activo, así que si alguna vez avanzara habría que revisar independencia con `factor-independence`.

**Qué NO contiene**: ningún retorno, precio, señal ni resultado. Solo calendario de negociación, efectos publicados por terceros y la fórmula de potencia de `hypothesis-gate` (caso portfolio/Sharpe).

## 1. Idea (1 línea)
El flujo neto diario agregado de los ETF spot de BTC en EE. UU. (creaciones menos rescates, publicado por los emisores a T+1) anticipa el retorno de BTC en los días siguientes: por **reversión** (presión de demanda no fundamental, como en Brown et al.) o por **continuación** (demanda persistente, como sugiere FalconX). El signo no se elige mirando datos: lo fija el usuario.

## 2. Fundamento y fuentes (verificables)

| Fuente | Qué reporta | Tamaño de efecto | Comparabilidad con HP-002 |
|---|---|---|---|
| Brown, Davies y Ringgenberg (2021), "ETF Arbitrage, Non-Fundamental Demand, and Return Predictability", Review of Finance 25(4):937-972, doi:10.1093/rof/rfaa027. <https://repository.arizona.edu/handle/10150/661294> · resumen con detalle: <https://cxoadvisory.com/equity-premium/predictable-etf-driven-price-distortions> | Los flujos de creación/rescate señalan demanda no fundamental; cartera corta en ETF de alto flujo y larga en bajo flujo | 1,1–2,0 %/mes en exceso (abstract); alfa 4 factores 5–13 %/año bruto, ~1 200 ETF, 2007–2015, rebalanceo semanal o mensual | **Mecanismo sí, diseño no**: es un corte transversal de ~1 200 ETF; con BTC hay un solo subyacente (los 11+ ETF tienen el mismo NAV), así que solo queda la versión de serie de tiempo |
| Versión preliminar AEA 2018 del mismo trabajo. <https://aeaweb.org/conference/2018/preliminary/paper/HGzHsdRe> | Acciones ordenadas por actividad de arbitraje de ETF, decil 1 − decil 10 | 0,611 %/mes (t=2,50); alfa 4F 0,602 %/mes (t=2,20) | Parcial: nivel acción, no un único activo |
| Polyzos y Mazur (2025), "Spot Bitcoin ETFs: The Effect of Fund Flows on Bitcoin Price Formation", Journal of Alternative Investments 27(4):110-123, doi:10.3905/jai.2025.1.239. <https://zuscholars.zu.ac.ae/works/7267> | Flujos netos y **nivel** de precio de BTC | R² = 95 % en **niveles** (probablemente espurio entre series no estacionarias); no reporta efecto predictivo sobre retornos | Baja: no sirve como efecto de referencia |
| FalconX (2024), "What Can Spot ETF Flows Tell Us About the Trajectory of Bitcoin Prices?" (industria, **no revisado por pares**). <https://www.falconx.io/newsroom/what-can-spot-etf-flows-tell-us-about-the-trajectory-of-bitcoin-prices-a-preliminary-statistical-investigation> | ~10 meses de datos diarios desde 2024-01-11 | Correlación contemporánea semanal 0,30; Granger flujos→precio p=0,004; coeficiente VAR del flujo del día anterior 0,027 sin error estándar | Media en diseño, baja en calidad: contemporáneo, muestra corta, sin fuera de muestra |
| McLean y Pontiff (2016), JF 71(1). <https://afajof.org/issue/volume-71-issue-1/> | Decaimiento post-publicación de anomalías | −58 % | Ajuste del efecto de Brown et al. |

**Lógica económica**: los flujos de ETF son demanda de inversores de corto plazo que los participantes autorizados trasladan al subyacente; si es demanda no fundamental, el precio sube de más y revierte (Brown et al.). Por qué persistiría: los límites al arbitraje en cripto (sin market maker que provea liquidez 24/7 con los mismos costos) y que el dato llega después del cierre de EE. UU. Por qué podría no existir: el flujo de ETF de BTC es público, seguido por todo el mercado y comentado a diario; además BTC cotiza 24/7 y la mayor parte del movimiento ocurre fuera del horario de los ETF (Polyzos y Mazur).

**Traducción del efecto publicado a IR anual** (IR ≈ t/√años):

| Referencia | IR anual implícito | Tras ×0,42 (McLean-Pontiff) |
|---|---|---|
| Brown et al. preliminar, exceso D1−D10 (t=2,50; SUPUESTO: 9 años, 2007–2015, tomado del período de la versión publicada) | 0,83 | 0,35 |
| Brown et al. preliminar, alfa 4F (t=2,20) | 0,73 | 0,31 |
| Precedente del proyecto (H3, TF_Basket) | 0,20–0,23 | — |
| BTC, específico | **No hay efecto predictivo publicado y revisado por pares** | — |

Para una regla de timing diaria, IR ≈ ρ·√252, con ρ la correlación entre la señal de hoy y el retorno de mañana. IR 0,35 equivale a ρ ≈ 0,022.

## 3. Revisión de lo ya cerrado
- No repite ningún marco cerrado (ninguno usó flujos de fondos). El único trabajo previo sobre BTC es KT-002/KT-003 (descriptivo, modelos de series de tiempo); no es una estrategia ni usa flujos.
- Comparte con el event study EURUSD el patrón de "efecto citado de un contexto distinto": allí la referencia (8 pips) resultó ~3 veces mayor que lo observado. Acá la referencia viene de un corte transversal de ETF de acciones aplicado a un solo activo cripto.

## 4. Datos disponibles (con fecha real de publicación)

| Fuente | Conteo real | Notas |
|---|---|---|
| Flujos/acciones en circulación de ETF spot BTC (sitios de los emisores: IBIT, FBTC, etc.) | Desde **2024-01-11**. Días hábiles NYSE hasta 2026-10-20: **696** (= **2,77 años**) | Contado con `pandas.bdate_range` menos 28 feriados NYSE (incluye el cierre del 2025-01-09). Los emisores publican el dato de T después del cierre o a la mañana de T+1; la fecha de conocimiento es esa, no T |
| Archivo histórico oficial de flujos diarios | **No existe en un solo lugar**: cada emisor publica tenencias del día; el histórico agregado lo arman terceros no oficiales (p. ej. Farside), que PF-001 dejó fuera | `portafolio-replica` tendría que reconstruir por emisor con checksum |
| Variante transversal (Brown et al.) sobre ETF de acciones de EE. UU. | Acciones en circulación diarias **sin archivo histórico gratuito** (CRSP/Bloomberg son pagos); N-PORT solo da tenencias trimestrales públicas | Sin datos históricos: solo podría correr hacia adelante |
| Precio BTC | `data/kt003/btcusdt_1h.csv.gz` (2017-08 a 2026-10, registro KT-003) | Pertenece a KT-003: no se tocó; reusarlo requeriría permiso |

## 5. Fase 0 — frecuencia, potencia, costos

**Frecuencia**: 1 observación por día hábil de EE. UU.; **696 hasta hoy**, ~252 por año más.

**Potencia** (α=0,05 dos colas, 80 %, z=2,80):

| Ventana | Años | MDE IR anual | MDE ρ diaria |
|---|---|---|---|
| Toda la historia (2024-01-11 → 2026-10-20), una sola prueba | 2,77 | **1,68** | **0,106** |
| Si se reserva 40 % como TEST | 1,11 | 2,66 | 0,168 |

| IR supuesto | Años necesarios | vs. ~5 años del skill |
|---|---|---|
| 0,20 (precedente del proyecto) | 196 | falla |
| 0,31–0,35 (Brown et al. ajustado) | 64–82 | falla |
| 0,73–0,83 (Brown et al. sin ajuste, no comparable) | 11,4–14,7 | falla |

Lectura: el MDE de toda la historia (1,68) está **~5 veces por encima** del efecto de referencia ajustado (0,35) y **2 veces por encima** incluso del efecto sin ajustar de otro diseño (0,83). Esperar no lo arregla a tiempo: con IR 0,35 harían falta ~64 años.

**Costos** (`docs/riesgo/COSTOS_BTCUSDT.md`, riesgo-costos, estado PARCIAL): ida y vuelta base **0,30 %** (estrés 0,60 %); a 24 h la mediana de |retorno| es 1,47 % y empatar exige ~60 % de acierto (~70 % con estrés), y el umbral reciente (2023–2026) es más duro (63–66 %). Una regla diaria que cambie de posición seguido paga ~0,30 % por cambio; con 100 cambios/año serían ~30 %/año de costo, frente a un efecto de referencia de pocos puntos de IR. **El efecto esperado no supera los costos** salvo con una regla de muy baja rotación, lo que reduce todavía más la n efectiva.

## 6. Veredicto de triage
**DESCARTADO EN EL TRIAGE (propuesto)**: 2,77 años de historia; horizonte para 80 % de poder de 64–196 años con efectos defendibles y 11–15 años aun con el efecto no comparable sin ajustar. Además, costos BTC altos frente al movimiento típico. La variante transversal (Brown et al.) no tiene datos históricos gratuitos.

Única salida razonable: una **medición descriptiva prospectiva** (p. ej. registrar flujo y retorno posterior sin regla de trading), que es otro tipo de registro y requiere decisión aparte; no confirmaría nada en menos de varias décadas si el efecto es del tamaño publicado.

## 7. Borrador de Fase 1 (no se completa; solo opciones)

| Punto | Estado | Opciones para decidir |
|---|---|---|
| Signo esperado | **A DEFINIR POR KENSY** | Reversión (Brown et al.) · continuación (FalconX) · bilateral (pierde poder) |
| Frase falsable | **A DEFINIR POR KENSY** | p. ej. "Cuando el flujo neto agregado de ETF spot BTC del día T, conocido al publicarse en T+1, está en el [quintil superior/inferior] de los últimos N días, el retorno de BTC en las H horas siguientes es [menor/mayor] que su media" |
| Señal | **A DEFINIR POR KENSY** | Flujo en US$ · flujo en % de activos · flujo en BTC · z-score de N días (cada uno suma al N de variantes) |
| Horizonte H | **A DEFINIR POR KENSY** | 1 día · 3–4 días (pico del impulso en FalconX) · 1 semana |
| Métrica primaria | **A DEFINIR POR KENSY** | Sharpe de la regla neto de costos · correlación de Spearman señal-retorno · acierto balanceado |
| Regla de corte | **A DEFINIR POR KENSY** | Umbral numérico; debe quedar **por encima del MDE** del tramo TEST o la prueba no informa |
| Folds | **A DEFINIR POR KENSY** | Con 696 días y piso de 30 operaciones por fold caben varios folds si hay muchas operaciones, pero la potencia no depende de los folds sino de los años (2,77) |
| Fuente de flujos | **A DEFINIR POR KENSY** | Solo emisores oficiales (reconstruir) · aceptar un agregador no oficial (contradice PF-001) |
| N de variantes | **A DEFINIR POR KENSY** | Señal × horizonte × signo; p. ej. 3 × 3 × 1 = 9 |

Variantes contadas en este documento: **0 probadas** (no se calculó nada). Diseños considerados por escrito: 2 (HP-002a serie de tiempo BTC; HP-002b transversal sobre ETF de acciones, descartada por falta de datos históricos gratuitos).

## 8. Por qué podría fallar (aunque la potencia alcanzara)
1. **Retraso de información**: BTC cotiza 24/7 y el flujo se conoce después del cierre de EE. UU.; la mayor parte del ajuste puede ocurrir antes de que el dato sea público.
2. **Causalidad inversa**: el flujo sigue al precio (Polyzos y Mazur: suba de BTC → volumen anormal en ETF); una correlación contemporánea no es predicción.
3. **Régimen único**: toda la muestra es el período de lanzamiento y adopción de los ETF (2024–2026).
4. **Costos** BTC altos frente al movimiento diario (ver §5).
5. **Efecto de referencia ajeno**: el único efecto revisado por pares viene de un corte transversal de ETF de acciones, no de un activo único.
