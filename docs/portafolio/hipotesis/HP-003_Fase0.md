# HP-003 — Fase 0: "en la apertura de los mercados es más fácil predecir" (estrategia alcista y estrategia bajista)

2026-10-21. Autor: `jefe-portafolio` (hizo la Fase 0 él mismo; sin contrataciones). Revisión pendiente: desconfiado → gerente; jefe-riesgo si avanza.
Origen: encargo de Kensy en la escalación "2026-10-21-portafolio-fase1" (el archivo de la escalación no está en el repo; se usó el texto del encargo del gerente).
Estado: **Fase 0 escrita. Veredicto de triage: DESCARTADO EN EL TRIAGE (propuesto)**, pendiente de auditoría. **Fase 1 NO iniciada.**

**Qué NO contiene**: ningún retorno de estrategia, ninguna señal, ningún resultado de predicción. Solo calendario, conteos de días por régimen (sin mirar retornos), efectos publicados por terceros y la fórmula de potencia de `hypothesis-gate`.

## 1. Idea (1 línea, sin completar lo que es de Kensy)
La apertura de una sesión es un momento en que el comportamiento del mercado es más predecible (más información acumulada de noche, más volumen, más volatilidad). Se pide una estrategia para régimen alcista y otra para bajista. Señal, horizonte, signo y definición de régimen **no están definidos** (ver sección 7).

## 2. Fundamento publicado (verificado en la fuente indicada; el resto es de memoria y se marca)

| Fuente | Qué reporta | Comparabilidad |
|---|---|---|
| Gao, Han, Li y Zhou (2018), "Market Intraday Momentum", JFE [**cita NO VERIFICADA**: el desconfiado no pudo abrirla]. Resumen con cifras: <https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/> | SPY, 1993–2013 (abstract de la revista; el blog resume una versión 1999-2012, **no verificado**): el retorno de la **primera media hora** predice el de la **última media hora**; R² ≈ **2 %** (≈4,3 % en la crisis) [**NO VERIFICADO**: solo de un blog]. Estrategia solo con la primera media hora: 6,34 %/año [**NO VERIFICADO**] (bruto, hipotético). Más fuerte en días de alta volatilidad, recesión y noticias macro | Es el caso más cercano: "la apertura predice". Es **en muestra, bruto**, un solo ETF de acciones EE. UU., período previo a la publicación |
| McLean y Pontiff (2016), JF 71(1) (ya usado en HP-002) | Las anomalías publicadas pierden ~58 % tras la publicación | Se aplica como ajuste: efecto ×0,42 |
| Literatura de periodicidad intradía (Heston, Korajczyk y Sadka 2010; Bogousslavsky 2016) | Hay patrones por hora del día | **De memoria, no reverificado hoy** |

Nota: lo publicado habla de la apertura como **predictor** de lo que pasa después (momentum intradía), no de que "sea más fácil predecir" la propia apertura. Eso es una interpretación a confirmar con Kensy (punto 7.1).

## 3. Mercados y aperturas posibles
- **Acciones/índices de EE. UU.** (apertura 13:30 UTC en verano, 14:30 en invierno): el caso con evidencia publicada.
- **Europa** (08:00 UTC Londres, 07:00 Fráncfort), **Asia** (00:00 UTC Tokio): menos literatura citada acá (no se buscó).
- **FX / oro** (el proyecto ya cerró 4 marcos): aperturas de Londres y NY; proyecto con 0/N resultados.
- **BTC**: no tiene apertura (24/7). Habría que elegir una hora arbitraria (00, 08 o 13:30 UTC): 3 sesiones x 2 regímenes = **6 contrastes** (con Bonferroni, z de 2,64 en vez de 1,96 por contraste, o sea más datos todavía).

## 4. Datos reales disponibles

| Fuente | Qué hay | Veredicto |
|---|---|---|
| `data/kt003/btcusdt_1h.csv.gz` | BTC 1 h, 2017-08-17 a 2026-10-20, 80 308 velas, **3 352 días** (3 153 con régimen calculable según la auditoría 2026-10-21; la versión previa decía 3 143) | Existe, pero es de KT-003 (solo lectura; se leyeron cierres para contar días por régimen, nada más). Sin "apertura" real |
| `data/mercado/btc_1d.json`, `btc_4h.json` | 259 velas diarias / 209 de 4 h | Muy corto |
| Índices, acciones, FX, oro **intradía** | **No hay ninguno en el repo** (solo diarios de EURUSD/divisas en `investigacion/fase2-3`). Datos MT5 intradía de los marcos anteriores viven en el terminal del usuario, no en el repo | Hay que pedirle a Kensy un export o habilitar una fuente |
| Fuentes gratuitas accesibles | Sin verificar: el proxy ya bloqueó SEC, iShares, SSGA, Farside y Binance (403). Los proveedores gratuitos de barras de 5-30 min suelen dar solo semanas o ~2 años; sin archivo largo gratuito conocido | **No se asume**; sin historia larga solo queda correr hacia adelante |

## 5. Fase 0 — frecuencia, potencia, costos

**Frecuencia**: 1 observación por día de negociación y por apertura (~252/año en acciones; 365 en BTC). Conteo de días BTC por régimen con la regla del analista (ALCISTA: cierre > MA200 y MA50 > MA200 y MA50 sube vs hace 10 días; BAJISTA: lo opuesto), cierre diario = última vela 1 h del día UTC:

| Régimen | Días | Porcentaje |
|---|---|---|
| ALCISTA | 1 123 | 35,6 % |
| BAJISTA | 926 | 29,4 % |
| LATERAL | 1 104 | 35,0 % |
| Total con régimen | 3 153 | 100 % |

**Corrección 2026-10-21 (auditoría desconfiado)**: la versión previa tenía LATERAL 1 094 y total 3 143 (porcentajes 35,7/29,5/34,8). La auditoría recontó 1 104 y 3 153; ALCISTA y BAJISTA coinciden. La regla que explica la diferencia de 10 días **no se identificó**; se adopta el conteo de la auditoría y los porcentajes se recalcularon sobre 3 153 (`python -I`, solo lectura, sin retornos). Los N de los MDE de abajo (1 123 y 926) no cambian; el de 3 143 pasa a 3 153 (MDE sin cambio al redondear).

Para acciones EE. UU. no hay conteo propio (sin datos); se **supone** alcista ~60 % y bajista ~20 % de los días, flag de supuesto.

**Potencia** (α = 0,05 dos colas, 80 %, N = 7,85 / ρ², ρ = correlación señal de apertura vs retorno posterior):

| Efecto de referencia | ρ | N total | Años (252/año) | Solo régimen alcista (~60 %) | Solo régimen bajista (~20 %) |
|---|---|---|---|---|---|
| Gao et al., R² 2 % [**NO VERIFICADO**], sin ajuste | 0,141 [**NO VERIFICADO**: derivado de ese R²] | 394 días | 1,6 | 2,6 | **7,8** |
| Con decaimiento postpublicación (ρ x 0,42) | 0,059 | 2 252 | **8,9** | **14,9** | **44,7** |
| ρ = 0,03 (más realista tras costos) | 0,030 | 8 711 | 34,6 | 57,6 | 172,8 |

El efecto de referencia es el "más cercano en diseño", no el de esta hipótesis (que no existe todavía). Se muestra con y sin ajuste porque el efecto sin ajuste es en muestra.

**MDE con los datos que existen** (potencia 80 %, ρ mínimo detectable):

| Muestra | N | MDE ρ | vs ρ con decaimiento 0,059 |
|---|---|---|---|
| BTC, todos los días con régimen, 1 apertura | 3 153 | 0,050 | detectable solo si no hay multiplicidad |
| BTC, régimen alcista | 1 123 | 0,084 | **supera** 0,059 |
| BTC, régimen bajista | 926 | 0,092 | **supera** 0,059 |
| Acciones, 13 años, bajista ~20 % | ~655 | 0,109 | **supera** |
| Acciones, 5 años, bajista ~20 % | ~252 | 0,176 | **supera** incluso el efecto sin ajuste (0,141) |

**Costos (la brecha más grande)**: el movimiento esperado bruto por operación es ≈ ρ x σ x 0,8. Con la mediana |ret| 1 h de BTC = 0,25 % (`docs/riesgo/COSTOS_BTCUSDT.md`, σ ≈ 0,37 %/h, σ de 30 min ≈ 0,26 %): ganancia esperada bruta ≈ **0,01-0,03 %** por operación (ρ 0,059 a 0,141) contra **0,30 % de ida y vuelta (base, supuesto de peor caso)**: 10 a 30 veces menos. En BTC un horizonte de 30 min a 1 h **no puede** cubrir costos (el propio documento de costos da "imposible" a 1 h). Para índices EE. UU. la brecha es mucho menor (costos de futuros/ETF del orden de 1-2 puntos básicos, **no medidos acá**, flag de supuesto), pero la ganancia bruta esperada también es del orden de 2-3 puntos básicos: margen cercano a cero, a medir con `riesgo-costos` si Kensy elige acciones.

## 6. Veredicto de triage
**DESCARTADO EN EL TRIAGE (propuesto)** para lo que hoy es accesible:
1. **BTC**: costos 10-30x mayores que la ganancia bruta esperada; sin apertura natural; 6 contrastes.
2. **Estrategia bajista en cualquier mercado**: 7,8 años (efecto sin ajustar) a 44,7 años (ajustado), contra el tope de ~5 del skill; con 5 años de datos el MDE (0,176) supera hasta el efecto publicado.
3. **Estrategia alcista**: pasa solo con el efecto publicado sin ajustar (2,6 años); con decaimiento serían 14,9 años. Y no hay datos intradía de índices en el repo, así que no puede ni calcularse un conteo real.

Lo único no cerrado: la pata alcista en un índice de acciones EE. UU., **si** Kensy acepta el efecto sin ajustar y aporta datos. Es una excepción que él decide, no el triage.

## 7. Qué tiene que definir Kensy para pasar a Fase 1 (no se completó nada de esto)
1. **Qué se predice**: ¿la apertura predice lo que viene después (como Gao et al.) o se quiere predecir la propia apertura (gap)? Cuál es el retorno a predecir.
2. **Mercado y apertura exactos**: un solo instrumento y una sola sesión (p. ej. índice de EE. UU., 13:30 UTC). Dos o más multiplican las pruebas.
3. **Frase falsable** para cada régimen: "cuando [condición medible en la apertura] entonces [resultado] en [horizonte]", con el signo fijado por él.
4. **Definición de régimen alcista/bajista**: ¿la regla del analista (MA50/MA200) u otra? Debe usar solo información disponible esa mañana.
5. **Regla de corte** numérica fijada antes de ver datos (qué IR/ρ/acierto neto de costos pasa y cuál no), y si acepta que el efecto de referencia sea el publicado sin ajustar (único caso en que alcista pasa) o el ajustado (descarta).
6. **Datos**: autorizar un export de barras intradía del instrumento (o habilitar una fuente) con al menos 5 años; si no, aceptar que solo puede correr hacia adelante (medición prospectiva = registro nuevo).
7. **Aceptar o no el triage**: si prefiere seguir con alcista, decir explícitamente que pide una excepción al tope de 5 años; si no, se registra el descarte.
8. **Costos**: quién los mide (`riesgo-costos`) y qué instrumento (futuros, ETF, CFD).
9. Folds y piso de 30 operaciones por fold los deriva el jefe-portafolio de la frecuencia real **después** de los puntos anteriores.

## 7b. Frecuencia de episodios de régimen y calidad de datos (agregado 2026-10-21, auditoría del desconfiado)

**Episodios (regla del analista, diario, 9 años)**: **23 episodios ALCISTA y 24 BAJISTA** (0 a 6 por año). Con el piso de `hypothesis-gate` de 30 trades/fold, **ES-001 y ES-002 son NO EVALUABLES**, ni siquiera en total. No se miraron retornos para contarlos. HP-003 no trae Fase 0 de frecuencia diaria propia (la de la sección 5 cuenta días, no operaciones).

**Calidad de datos de `btcusdt_1h.csv.gz`**: (i) **28 huecos > 1 h**, el mayor de **1 d 09 h**; (ii) **43 filas con marca 09:28:14 de feb-2018**, desalineadas de la grilla horaria (ya mencionadas en `docs/riesgo/COSTOS_BTCUSDT.md`); (iii) el último "día", **2026-10-20, es parcial** (última vela 14:00 UTC); (iv) el calendario de feriados usado es el **federal de pandas**, no el de NYSE ni europeos/asiáticos. Los conteos de eventos de la sección 10 difieren en 2-6 de los de la auditoría (EE. UU. 3 345 vs 3 347; hábiles 2 290 vs 2 291): las cifras son aproximadas, inocuas para el veredicto.

## 8. Qué no se hizo
No se tocó ningún resultado de rendimiento, no se probó ninguna variante (0), no se usaron datos de KT-002/KT-003 más allá de contar días por régimen en solo lectura, no se creó ningún ayudante.

## 9. Evidencia publicada vs. opinión de foros

2026-10-21. Búsqueda web hecha hoy por el investigador-cuantitativo. Cada fila se leyó en la página citada (resumen/abstract o blog), **no en el paper completo**, salvo que se diga. "n/d" = la página no lo dice. No se cita nada de memoria sin marcarlo. Sin resultados de estrategia propios, sin dinero.

### 9.1 Evidencia revisada por pares o working papers

| Trabajo (cita) | Mercado y período | Efecto | Costos / fuera de muestra / post-publicación |
|---|---|---|---|
| [**NO VERIFICADA**] Gao, Han, Li y Zhou (2018), "Market intraday momentum", *J. Financial Economics* 129(2), 394-414, doi 10.1016/j.jfineco.2018.05.009 (<https://profiles.wustl.edu/en/publications/market-intraday-momentum/>) | ETF S&P 500 **1993-2013** + 10 ETF más. El retorno de la 1.ª media hora (desde el cierre previo) predice el de la última media hora; más fuerte en días de alta volatilidad, alto volumen, recesión y noticias macro | Cifras de R² (~2 %) y 6,34 %/año vienen de un resumen de blog (Alpha Architect) sobre la versión de trabajo, 1999-2012. **Unificado 2026-10-21: Gao se cita como 1993–2013 en toda la hipótesis**; el blog dice 1999-2012 (versión de trabajo distinta; el R² no se reverificó en el paper) | Costos: n/d. Fuera de muestra: el abstract/blog dicen que es significativo dentro y fuera de muestra, sin detalle. Post-publicación: **no verificado** |
| [**NO VERIFICADA**] Li, Sakkas y Urquhart (2022), "Intraday time series momentum: global evidence and links to market characteristics", *J. Financial Markets* 57, 100619 (<https://reading-9.eprints-hosting.org/95566/1/Accepted-Version.pdf>) | 16 índices MSCI desarrollados, 1 min, **2005-10-04 a 2017-12-29** | Coeficiente agrupado 2,86 (t 7,53); significativo en 12 de 16 mercados; R² ajustado 0,63 % fuera de crisis, 1,18 % en crisis; alfas 2,6-7,5 %/año; Sharpe 1,01-1,77 en 11 de 18 carteras globales | Fuera de muestra (ventana expansiva): Clark-West rechaza en 10 de 16. **Costos: no tratados** en el texto leído. Post-2017: **no cubierto** |
| [**NO VERIFICADA**] Shen, Urquhart y Wang (2022), "Bitcoin intraday time series momentum", *Financial Review* 57(2), 319-344 (<https://research.birmingham.ac.uk/en/publications/bitcoin-intraday-time-series-momentum/>) | BTC, barras de 30 min; el tiempo se mide por volumen (no por reloj, porque BTC no cierra). Período y exchange: n/d en la página | La 1.ª media hora predice la última; más fuerte en las sesiones de más volumen o volatilidad, y en mercado bajista. "Ganancias económicas sustanciales" | Tamaño del efecto, costos y fuera de muestra: **n/d en el abstract**; hay que leer el paper. Importante: su "primera media hora" se define por volumen, no por 13:30 UTC |
| [**NO VERIFICADA**] Zarattini, Barbon y Aziz (2024), "A Profitable Day Trading Strategy for the U.S. Equity Market", Swiss Finance Institute RP 24-98 (<https://ideas.repec.org/p/chf/rpseri/rp2498.html>) | >7 000 acciones EE. UU., **2016-2023**, ORB de 5 min, filtro "Stocks in Play" | Cartera top-20: retorno neto >1 600 %, Sharpe 2,81, alfa 36 %/año (S&P 500: 198 %) | "Después de costos" según el abstract, supuestos n/d. Working paper, **sin fuera de muestra** propio; es acciones individuales, no BTC ni índices. Selección de "stocks in play" y período corto: riesgo de sobreajuste (opinión mía, no del paper) |
| Zarattini y Aziz, "Can Day Trading Really Be Profitable?", SSRN 4416622 | QQQ, ORB de 5 min; 24 % de aciertos, +0,13 R por operación, 33 %/año con apalancamiento 4x | Datos tomados **solo** del blog que lo replica (ver 9.2); el paper original no se abrió | Según ese blog: incluye comisiones, sin spread ni slippage, sin fuera de muestra |
| Eross, McGroarty, Urquhart y Wolfe (2019), "The intraday dynamics of Bitcoin", *Research in International Business and Finance* 49, 71-81 (<https://researchportal.hw.ac.uk/en/publications/the-intraday-dynamics-of-bitcoin/>) | BTC, ticks GMT del exchange líder agregados a 5 min, 4 años (fechas n/d) | **Volumen** sube durante el día y cae de ~16:00 a medianoche; **volatilidad** estable salvo picos en la apertura de las 3 bolsas globales (horas exactas n/d); **liquidez** máxima en las aperturas, mínima de madrugada | Es descriptivo (volumen/volatilidad/liquidez), **no mide retornos explotables** ni costos |
| [**NO VERIFICADA**] Baur, Cahill, Godfrey y Liu (2017), "Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume", working paper (<https://research-repository.uwa.edu.au/en/publications/bitcoin-time-of-day-day-of-week-and-month-of-year-effects-in-retu/>) | 7 exchanges, >15 millones de observaciones; período n/d | Efectos **variables en el tiempo, sin patrones consistentes ni persistentes**; concluyen que el mercado parece eficiente | Es evidencia **en contra** de un efecto horario estable en BTC |

### 9.2 Opinión de blogs, brokers y foros (evidencia débil, no peer-reviewed)

| Fuente | Qué dice | Peso |
|---|---|---|
| [**NO VERIFICADA**] Padyšák y Vojtko, Quantpedia, 2022-02-18 (<https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/>) | BTC en Gemini, datos horarios ~2015-2022: retornos más altos y significativos a las 22:00 y 23:00 UTC, más bajos a las 03:00-04:00 (no significativos). Comprar 21:00 y vender 23:00: 33 %/año, vol 20,9 %, DD -22,45 % | Regla elegida mirando los mismos datos (sesgo de minería, lo dice el propio texto); **sin costos**, un solo exchange, sin fuera de muestra. Nota: el pico está en la noche UTC, **no** en 13:30 |
| [**NO VERIFICADA**] Krueger, blog MQL5 (<https://www.mql5.com/en/blogs/post/776235>) | Réplica del ORB sobre NQ, SPX, Dow, DAX, FTSE (CFD), 2015-2026: bruto reproduce en NQ (+0,131 R); **neto de spread y slippage ≈ 0** (NQ +0,002 R) y negativo en los otros 4 (-0,04 a -0,08 R). Fuera de muestra 2021-26: a lo sumo +0,06 R en NQ. Contra dirección aleatoria hay una señal pequeña (+0,10 a +0,13 R) del orden del costo | Un blogger que vende herramientas; sin revisión. Útil como **contrapunto**, no como prueba. Costos cargados como porcentaje del riesgo inicial (supuesto del autor) |
| K33 Research, Lunde (2022) (<https://k33.com/research/archive/articles/bitcoins-downside-in-2022-has-not-occurred-during-the-european-watch>) | BTC 2022 (~240 días): caída concentrada en horas asiáticas (-41,7 %) y de EE. UU. (-25 %, siguiendo al Nasdaq); horas europeas ~planas (-1,4 %) | Un solo año bajista, definiciones de sesión n/d, sin estadística; el propio autor da la explicación como hipótesis |
| Prensa cripto (CryptoSlate, Blockworks, InvestmentNews, AMBCrypto; solo aparecieron en la búsqueda, **no se leyeron**) | Titulares: BTC se mueve con "horario de Wall Street", más volatilidad en horas de EE. UU. | **No verificado**; no usar como evidencia |
| Blog de Nguyen (Harbourfront Quant, Substack) | Resume Gao et al.; no aporta muestra, costos ni datos posteriores a 2013 | Solo resumen del paper |

### 9.3 Lectura para HP-003 (sin resultados propios)
1. **Momentum intradía** (primera media hora → última media hora) tiene respaldo revisado por pares en **acciones/índices** (Gao 2018; Li-Sakkas-Urquhart 2022, 16 países, con fuera de muestra) y un trabajo en **BTC** (Shen 2022) con tiempo medido por volumen. En ninguno de los que se pudo leer hay costos ni datos posteriores a 2017/2013. El efecto es "predecir el cierre desde el inicio", no "predecir la apertura".
2. **ORB**: solo hay evidencia en acciones/índices de EE. UU. (2016-2023); la única réplica independiente encontrada (blog) lo da en **cero neto de costos**. Sin trabajo revisado por pares sobre ORB en BTC encontrado (**no se halló, lo que no prueba que no exista**).
3. **Efectos de apertura en BTC**: lo revisado indica que volumen, volatilidad y liquidez **sí** suben en las aperturas globales (Eross 2019, descriptivo), pero que los **retornos** por hora no son estables (Baur 2017) y el único patrón horario "explotable" encontrado (Quantpedia) cae a las 22-23 UTC, es in-sample y sin costos. Más volatilidad no es lo mismo que más predictibilidad con signo; sin esa distinción la idea de la sección 1 queda sin respaldo en BTC.
4. **No se encontró** (no verificado): estudio revisado por pares que muestre un edge neto de costos, fuera de muestra y posterior a su publicación, para ORB o momentum intradía en BTC. Tampoco se verificó la caída post-publicación de Gao et al. (se aplica el ajuste genérico de McLean y Pontiff, sección 2, no una medición propia).
5. Pendiente si Kensy quiere seguir: leer completos Shen et al. (2022) y Zarattini-Barbon-Aziz (2024) para período, exchange, costos y fuera de muestra reales.

## 10. Fase 0 solo con conteos: BTC 1 h (apertura), 2026-10-21

Autor: investigador-cuantitativo. Fuente: `data/kt003/btcusdt_1h.csv.gz` (solo lectura, `python -I`), 80 308 velas únicas, 2017-08-17 a 2026-10-20 (9,2 años). **Sin signo, sin estrategia, sin predicción.** Se miró solo el tamaño |log(cierre/apertura)| por vela. Variantes probadas: 0.

**(a) Eventos** (primer tramo = vela 1 h que contiene la apertura; siguiente tramo = la vela siguiente; con datos de 1 h no se puede aislar la media hora de 13:30 UTC: es un límite del dato). Horas: EE. UU. 13:30 UTC en verano (2 209 días) y 14:30 en invierno; Europa = 08:00 hora de Londres (07:00 UTC en verano, 08:00 en invierno); Asia = 00:00 UTC (Tokio, sin horario de verano).

| Sesión | Eventos totales | Días hábiles | Fin de semana | Feriado hábil (EE. UU.) |
|---|---|---|---|---|
| EE. UU. | 3 347 [auditoría: 3 345] | 2 291 [auditoría: 2 290] | 958 | 98 (calendario federal de pandas, no el de NYSE; aproxima) |
| Europa | 3 342 | 2 385 | 957 | 0 (no se aplicó calendario europeo) |
| Asia | 3 348 | 2 390 | 958 | 0 (idem) |

BTC opera sábados, domingos y feriados: ~30 % de los eventos no son "aperturas" de bolsa. EE. UU. hábil por año: ~250 (2017: 92; 2026: 201).

**(b) Potencia/MDE de un contraste de signo** (acierto contra 50 %, bilateral 5 %, potencia 80 %): N=2 291 (EE. UU. hábil, una sesión) -> acierto mínimo detectable **52,9 %** (ρ 0,059); N=1 000 -> 54,4 %; N=500 -> 56,3 %; N=250 (1 año) -> 58,9 %. Para detectar 53 % hacen falta ~2 180 eventos, 52 % ~4 900, 51 % ~19 600. Con 3 sesiones x 2 regímenes (6 contrastes, Bonferroni z=2,64) el MDE sube: no calculado por régimen; los regímenes parten la muestra (alcista 35,6 %, bajista 29,4 % según sección 5 corregida). Confirmación posterior al 2026-10-20: ~250 eventos hábiles/año por sesión -> MDE 58,9 % tras 1 año; **~9 años** para llegar a N=2 291.

**(c) Tamaño del movimiento vs costos** (mediana de |ret|, sin signo; costo base 0,30 % ida y vuelta de `docs/riesgo/COSTOS_BTCUSDT.md`, supuesto de peor caso):

| Sesión (hábil) | Tramo 1 | Tramo 2 | Suma de los dos (mediana) |
|---|---|---|---|
| EE. UU. | 0,407 % | 0,426 % | 0,984 % |
| Europa | 0,268 % | 0,268 % | 0,603 % |
| Asia | 0,328 % | 0,289 % | 0,683 % |

Referencia: mediana de |ret| 1 h de todas las horas = 0,250 %. Fin de semana/feriado: 0,17-0,25 % por tramo, **menor** que en hábiles. Un tramo de 1 h en EE. UU. (0,41-0,43 %) es 1,4 veces el costo; Europa/Asia (0,27-0,33 %) apenas 0,9-1,1 veces. Para empatar con el costo base se necesita acierto de signo ~(m+c)/(2m): ≈87 % en EE. UU. (tramo 2) y >100 % (imposible) en Europa, con el mismo modelo simple de COSTOS (sección 3). Ventana EE. UU. mayor (ambos tramos, ~0,98 %) baja el acierto mínimo a ~65 %. Es aritmética de tamaño, no un edge medido. El movimiento sí es mayor en la apertura de EE. UU. (volatilidad, coherente con Eross 2019), pero la volatilidad no es predictibilidad con signo.

**(d) Qué cambia y qué no respecto de los marcos cerrados** (CLAUDE.md; Bitácora 2026-07-22/24 y 2026-08-04/05):
- Cambia: instrumento (BTC spot 24/7, no XAUUSD/EURUSD), clase de driver (calendario/hora del día, no macro ni técnico), costos propios (0,30 % ida y vuelta, supuesto), datos (1 h de Binance vía KT-003).
- No cambia: es un marco intradía (H1) con el mismo problema que cerró XAUUSD H1/H4 y EURUSD (0/N pasando la regla de corte, edge ilusorio al agregar datos, 2026-07-24); la búsqueda de "momento especial" sigue siendo multiplicidad (3 sesiones x 2 regímenes); el efecto publicado (Gao 2018) es acciones, bruto y sin costos; Baur 2017 halla efectos horarios inestables en BTC. Sigue vigente la PAUSA ACTIVA: abrir esto requiere decisión explícita del usuario, además de Fase 1 definida por él.

**(e) Confirmación**: la historia 2017-2026 está expuesta por KT-003; sirve solo para contar y dimensionar. Cualquier prueba de signo debe usar **solo datos posteriores a 2026-10-20**, pre-registrada antes de verlos. A ~250 eventos hábiles/año por sesión, 1 año da MDE 58,9 % (solo detecta efectos grandes).

**Veredicto Fase 0 (propuesto)**: la muestra existe (2 291 eventos hábiles EE. UU. exposición histórica), pero la prueba limpia (posterior a 2026-10-20) tarda años, el movimiento típico de 1 h cubre costos solo con acierto ~87 % (EE. UU.) o es imposible (Europa/Asia), y el marco intradía precedente está cerrado. Coincide con el descarte de la sección 6. **PENDIENTE DEL USUARIO**: sesión única, signo, régimen, horizonte, regla de corte, y si acepta confirmar solo con datos futuros.
