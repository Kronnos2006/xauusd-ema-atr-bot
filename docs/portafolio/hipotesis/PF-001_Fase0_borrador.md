# PF-001 — Fase 0 (BORRADOR): copia en papel de portafolios grandes con datos públicos

2026-10-21. Autor: `jefe-portafolio`. Estado: **BORRADOR**, sin auditar (desconfiado y jefe-riesgo pendientes).
Autorización: decisión del usuario 2026-10-21 (`docs/gerencia/decisiones.md`): simulación en papel con datos públicos de portafolios grandes; primero Fase 0 y registro previo; **no se calculan resultados antes**.

**Qué NO contiene este documento**: ningún retorno, precio ni resultado. Los números de abajo salen solo de calendarios de publicación (cuántos años de datos existen) y de la fórmula de potencia de `hypothesis-gate` (caso portfolio/Sharpe). La Fase 1 (frase falsable, regla de corte, folds) **no está escrita**: la tiene que dar el usuario.

## 1. Fuentes públicas candidatas, con fecha real de publicación

| Fuente | Qué publica | Período del dato → fecha en que se conoce | Historia estructurada disponible | Frecuencia de cambio de cartera |
|---|---|---|---|---|
| SEC EDGAR — Form 13F-HR (y "Form 13F Data Sets" de DERA) | Posiciones largas en acciones/opciones de EE. UU. de gestores con >US$100M, al cierre del trimestre | Plazo legal: 45 días tras el cierre del trimestre. **Se usa la fecha real de presentación de cada filing**, no 45 días fijos (muchos presentan el último día; algunos antes; enmiendas 13F-HR/A después) | Data Sets XML desde 2013 T2 (DERA indica "July 2013 – August 2026"). Filings en texto en EDGAR desde ~1999 (requieren parseo, más riesgo de error) | Trimestral (4 rebalanceos/año) |
| SEC — Form N-PORT (fondos y ETF registrados) | Tenencias completas mensuales; solo el tercer mes de cada trimestre es público | ~60 días tras el cierre del trimestre | Data sets desde ~2019 T4 (a verificar por `portafolio-replica`) | Trimestral público |
| Emisores de ETF (iShares, SPDR, etc.) | Tenencias diarias en su web | T+1 | Sin archivo histórico oficial gratuito: solo sirve hacia adelante (prospectivo) | Diaria |
| Emisores de ETF spot de BTC (IBIT, FBTC, etc.) | BTC en custodia / acciones en circulación diarias; el flujo se deriva por diferencia | T+1 (web del emisor; agregadores no oficiales quedan fuera) | Desde 2024-01-11 (~2,8 años al 2026-10-21) | Diaria |

Fuente del calendario 13F: [SEC DERA Form 13F Data Sets](https://www.sec.gov/dera/data/form-13f). Las demás fechas las tiene que confirmar `portafolio-replica` con enlace y checksum (skill `data-integrity`).

## 2. Riesgos de mirar el futuro y de sesgo (se fijan antes de ver datos)

1. **Fecha de conocimiento = FILING_DATE de cada presentación** (y de cada enmienda por separado). Entrada en papel al día hábil siguiente al filing, nunca en la fecha del período.
2. **Selección de fondos por regla conocida en esa fecha** (ej. top N por valor reportado en el filing previo), nunca "los fondos famosos de hoy" (sesgo de supervivencia).
3. **Precios con empresas deslistadas**: las fuentes gratuitas suelen no tenerlas. Si no hay precios de deslistadas, el resultado queda sesgado al alza y hay que declararlo o descartar la fuente. Punto abierto para `portafolio-replica` y el desconfiado.
4. **Tratamiento confidencial** (posiciones omitidas que aparecen después) y cambios de CUSIP: el dato a usar es el "tal como se presentó", no el corregido.
5. 13F no muestra cortos, efectivo ni derivados fuera de EE. UU.: la copia replica solo la parte larga declarada.
6. **Costos**: los mide `riesgo-costos` (comisión, spread, impacto); el diseño no se evalúa sin ellos.

## 3. Potencia estimable sin mirar retornos (caso portfolio, `hypothesis-gate`)

Fórmulas del skill, α = 0,05 dos colas, 80 % de poder (z = 2,80):
`MDE = 2,80 / √años` · `años necesarios = (2,80 / Sharpe_típico)²`.

| Fuente | Años de historia usable | MDE (Sharpe o IR anual) con TODA la historia en una sola prueba |
|---|---|---|
| 13F Data Sets XML (2013 T2 – 2026 T2) | ~13 | **0,78** |
| 13F texto + XML (1999 – 2026) | ~27 | 0,54 |
| N-PORT (2019 T4 – 2026 T2) | ~6,5 | 1,10 |
| Flujos ETF spot BTC (2024-01-11 – hoy) | ~2,8 | **1,68** |

Años necesarios según el efecto de referencia (sin mirar datos):

| Sharpe/IR típico asumido | Años para 80 % de poder |
|---|---|
| 0,20 (precedente del proyecto: H3 momentum FX ~0,20; TF_Basket ~0,23) | 196 |
| 0,30 | 87 |
| 0,50 | 31 |
| 0,80 | 12 |

Lectura honesta (preliminar): con el efecto de referencia que el skill obliga a usar (el precedente más cercano del proyecto, ~0,20), **todas las variantes superan el límite de ~5 años y caerían DESCARTADAS EN EL TRIAGE**. Separar TRAIN/TEST empeora el MDE (menos años por tramo). Flujos de ETF BTC no tienen historia suficiente para ninguna prueba confirmatoria: solo servirían como medición prospectiva descriptiva.

Única vía que podría cambiar esto: que el `portafolio-investigador` documente, **con fuente verificable y sin mirar nuestros datos**, un efecto de referencia de diseño parecido (copia de 13F con retraso real y costos, medido como exceso sobre índice) bastante mayor que 0,20, y que el desconfiado acepte que es comparable. Sin eso, la recomendación es registrar el descarte.

## 4. Lo que falta (en orden)

1. `portafolio-replica`: inventario real (fondos por trimestre, % con FILING_DATE, enmiendas, huecos, cobertura de precios con deslistadas). Sin descargar precios de retornos todavía.
2. `portafolio-investigador`: efecto de referencia externo verificable (o confirmar que no existe).
3. Desconfiado y jefe-riesgo: auditoría de este borrador.
4. **Usuario (Fase 1, no la completa Portafolio)**: frase falsable; métrica (Sharpe absoluto o exceso/IR vs. un índice, y cuál); regla de corte numérica; universo y regla de selección de fondos; número de folds (sale del piso de datos por tramo).

## 5. Veredicto provisorio de Fase 0

**NO LISTO**: inventario real pendiente. Con el efecto de referencia del proyecto (0,20), el triage proyecta descarte; queda abierto solo si aparece un efecto de referencia externo válido.
