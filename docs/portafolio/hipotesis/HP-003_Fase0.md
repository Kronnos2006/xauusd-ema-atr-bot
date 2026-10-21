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
| Gao, Han, Li y Zhou (2018), "Market Intraday Momentum", JFE. Resumen con cifras: <https://alphaarchitect.com/2014/08/attention-prop-traders-the-first-half-hour-of-trading-predicts-the-last-half-hour/> | SPY, 1999-01-04 a 2012-12-31: el retorno de la **primera media hora** predice el de la **última media hora**; R² ≈ **2 %** (≈4,3 % en la crisis). Estrategia solo con la primera media hora: 6,34 %/año (bruto, hipotético). Más fuerte en días de alta volatilidad, recesión y noticias macro | Es el caso más cercano: "la apertura predice". Es **en muestra, bruto**, un solo ETF de acciones EE. UU., período previo a la publicación |
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
| `data/kt003/btcusdt_1h.csv.gz` | BTC 1 h, 2017-08-17 a 2026-10-20, 80 308 velas, **3 352 días** (3 143 con régimen calculable) | Existe, pero es de KT-003 (solo lectura; se leyeron cierres para contar días por régimen, nada más). Sin "apertura" real |
| `data/mercado/btc_1d.json`, `btc_4h.json` | 259 velas diarias / 209 de 4 h | Muy corto |
| Índices, acciones, FX, oro **intradía** | **No hay ninguno en el repo** (solo diarios de EURUSD/divisas en `investigacion/fase2-3`). Datos MT5 intradía de los marcos anteriores viven en el terminal del usuario, no en el repo | Hay que pedirle a Kensy un export o habilitar una fuente |
| Fuentes gratuitas accesibles | Sin verificar: el proxy ya bloqueó SEC, iShares, SSGA, Farside y Binance (403). Los proveedores gratuitos de barras de 5-30 min suelen dar solo semanas o ~2 años; sin archivo largo gratuito conocido | **No se asume**; sin historia larga solo queda correr hacia adelante |

## 5. Fase 0 — frecuencia, potencia, costos

**Frecuencia**: 1 observación por día de negociación y por apertura (~252/año en acciones; 365 en BTC). Conteo de días BTC por régimen con la regla del analista (ALCISTA: cierre > MA200 y MA50 > MA200 y MA50 sube vs hace 10 días; BAJISTA: lo opuesto), cierre diario = última vela 1 h del día UTC:

| Régimen | Días | Porcentaje |
|---|---|---|
| ALCISTA | 1 123 | 35,7 % |
| BAJISTA | 926 | 29,5 % |
| LATERAL | 1 094 | 34,8 % |
| Total con régimen | 3 143 | |

Para acciones EE. UU. no hay conteo propio (sin datos); se **supone** alcista ~60 % y bajista ~20 % de los días, flag de supuesto.

**Potencia** (α = 0,05 dos colas, 80 %, N = 7,85 / ρ², ρ = correlación señal de apertura vs retorno posterior):

| Efecto de referencia | ρ | N total | Años (252/año) | Solo régimen alcista (~60 %) | Solo régimen bajista (~20 %) |
|---|---|---|---|---|---|
| Gao et al., R² 2 %, sin ajuste | 0,141 | 394 días | 1,6 | 2,6 | **7,8** |
| Con decaimiento postpublicación (ρ x 0,42) | 0,059 | 2 252 | **8,9** | **14,9** | **44,7** |
| ρ = 0,03 (más realista tras costos) | 0,030 | 8 711 | 34,6 | 57,6 | 172,8 |

El efecto de referencia es el "más cercano en diseño", no el de esta hipótesis (que no existe todavía). Se muestra con y sin ajuste porque el efecto sin ajuste es en muestra.

**MDE con los datos que existen** (potencia 80 %, ρ mínimo detectable):

| Muestra | N | MDE ρ | vs ρ con decaimiento 0,059 |
|---|---|---|---|
| BTC, todos los días con régimen, 1 apertura | 3 143 | 0,050 | detectable solo si no hay multiplicidad |
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

## 8. Qué no se hizo
No se tocó ningún resultado de rendimiento, no se probó ninguna variante (0), no se usaron datos de KT-002/KT-003 más allá de contar días por régimen en solo lectura, no se creó ningún ayudante.
