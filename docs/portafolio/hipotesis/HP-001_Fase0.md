# HP-001 — Fase 0: "mejores ideas" de gestores grandes vía 13F, copiadas con retraso real

2026-10-21. Autor: `portafolio-investigador` (pedido del `jefe-portafolio`, convocado por el gerente). Revisión: jefe-portafolio → desconfiado → gerente; jefe-riesgo si avanza.
Estado: **Fase 0 escrita. Veredicto de triage: DESCARTADO EN EL TRIAGE (propuesto)**, pendiente de auditoría.
Relación con PF-001: es una variante concreta de PF-001 (copia en papel de 13F). Usa el mismo calendario de datos y la misma fórmula de potencia; lo que agrega es un efecto de referencia externo, con fuente.

**Qué NO contiene**: ningún retorno, precio, señal ni resultado de la estrategia. Solo calendarios de publicación, conteos de períodos, efectos publicados por terceros y la fórmula de potencia de `hypothesis-gate` (caso portfolio/Sharpe).

## 1. Idea (1 línea)
Cada trimestre, tomar de los 13F de gestores grandes la posición en la que cada uno muestra más convicción ("best idea": mayor sobrepeso frente al índice), comprarla en papel al día hábil siguiente a la **fecha real de presentación** del 13F y medir su exceso de retorno frente a un índice de acciones de EE. UU.

## 2. Fundamento y fuentes (verificables)

| Fuente | Qué reporta | Tamaño de efecto | Comparabilidad con HP-001 |
|---|---|---|---|
| Cohen, Polk y Silli (2008, LSE FMG Discussion Paper 624; versión con tablas presentada en 2011), "Best Ideas". <https://eprints.lse.ac.uk/24471> · versión con tablas: <https://www.lse.ac.uk/Events/Events-Assets/PDF/2017/2017-LT01/20110224-Christopher-Polk-Best-Ideas.pdf> | Las "mejores ideas" de fondos mutuos de EE. UU. superan al mercado | 39–127 pb/mes según benchmark. Tabla 2 (1985–2007, 276 meses): alfa 6 factores 82 pb/mes (t=4,38); alfa 4 factores 40 pb/mes (t=1,86); alfa frente a la cartera propia 53 pb (t=2,85) | **Parcial**: miden en la **fecha real de tenencia, no en la de publicación** (el texto dice "as of the true holding date"); son fondos mutuos, no 13F; brutos de costos; muestra que termina en 2007 |
| Griffin y Xu (2009), RFS 22(7):2331-2370, doi:10.1093/rfs/hhp026. <https://ideas.repec.org/a/oup/rfinst/v22y2009i7p2331-2370.html> | Tenencias 13F de 306 hedge funds, 1980–2004 | Selección de acciones: +1,32 %/año frente a fondos mutuos, "marginalmente significativo", concentrado en 1999–2000; desaparece con ponderación igual. Las compras y tenencias agregadas **no predicen** retornos | **Alta** (13F, gestores grandes): es el precedente más parecido y es **débil** |
| Aragon, Hertzel y Shi (2013), JFQA 48(5):1499-1518. <https://ideas.repec.org/a/cup/jfinqa/v48y2013i05p1499-1518_00.html> | Las posiciones bajo tratamiento confidencial del 13F rinden alfa positivo durante el período confidencial | Significativo (el resumen no da magnitud) | En contra de HP-001: lo mejor justamente **no se ve** en el 13F público a tiempo |
| McLean y Pontiff (2016), JF 71(1), "Does Academic Research Destroy Stock Return Predictability?" <https://afajof.org/issue/volume-71-issue-1/> | Decaimiento de anomalías publicadas | −26 % fuera de muestra, −58 % después de la publicación | Para ajustar los efectos de arriba a 2013–2026 |

**Lógica económica**: un gestor con información pone más peso donde más cree (Cohen et al.); el 13F hace pública esa convicción. Por qué no desaparecería del todo: el retraso de hasta 45 días y el costo de procesar miles de filings limitan el arbitraje. Por qué sí podría desaparecer: el dato es gratuito y masivo desde 2013 (agregadores como WhaleWisdom lo venden), y el retraso legal se come justo la parte del efecto que Cohen et al. miden en la fecha de tenencia.

**Traducción del efecto publicado a IR anual** (IR ≈ t / √años; mismo enfoque del skill para portfolio):

| Referencia | IR anual implícito | Tras ajuste McLean-Pontiff post-publicación (×0,42) |
|---|---|---|
| Cohen et al., alfa 6 factores (t=4,38, 23 años) | 0,91 | 0,38 |
| Cohen et al., alfa vs cartera propia (t=2,85) | 0,59 | 0,25 |
| Cohen et al., alfa 4 factores (t=1,86) | 0,39 | 0,16 |
| Griffin y Xu, 13F hedge funds (SUPUESTO: "marginalmente significativo" leído como t ≈ 1,7–2 sobre 25 años; el t exacto no se verificó en el texto) | ≈ 0,34–0,40 | ≈ 0,14–0,17 |
| Precedente del proyecto (H3 momentum, TF_Basket) | 0,20–0,23 | — |

Nota: ninguno de estos números incluye el retraso real de publicación ni costos; ambos solo pueden bajar el efecto. El rango razonable para HP-001 es **IR ≈ 0,15–0,40**, con 0,91 como cota optimista que el desconfiado debería rechazar por no comparable (fecha de tenencia, sin decaimiento).

## 3. Revisión de lo ya cerrado
- No repite ningún marco cerrado: los cuatro cerrados son técnicos/macro sobre FX, oro y un basket; ninguno usa tenencias institucionales. Salida 2 fue implementación de Donchian.
- Sí comparte el **problema estructural** de H3 momentum y TF_Basket: diseño portfolio evaluado por Sharpe con pocos años. Lo que cambia es la fuente del edge (información de gestores, no precio), no la potencia.

## 4. Datos disponibles (con fecha real de publicación)

| Fuente | Conteo real | Cómo se contó |
|---|---|---|
| SEC DERA "Form 13F Data Sets" <https://www.sec.gov/dera/data/form-13f> | **54 archivos**: 43 trimestres calendario de presentación (2013 T2 → 2023 T4), 1 de transición (ene–feb 2024) y 10 ventanas de 3 meses que terminan en feb/may/ago/nov (mar 2024 → ago 2026). Cobertura declarada "July 2013 – August 2026" | Consultado el 2026-10-21 vía WebFetch. Las ventanas van por **fecha de presentación**, lo que ayuda a no mirar el futuro |
| Períodos de reporte cubiertos | **53 trimestres de reporte** (2013 T2 → 2026 T2) = **13,0 años** = 53 rebalanceos posibles | Derivado del rango anterior |
| Filings 13F en texto (EDGAR, ~1999 → 2013) | ~14 años más, sin estructura XML | No contado hoy: `www.sec.gov` y `efts.sec.gov` **bloqueados desde el entorno** (proxy 403 por bash; la búsqueda EFTS quedó sin permiso). Pendiente para `portafolio-replica` |
| Cantidad de gestores por trimestre | **No contado** | Mismo bloqueo. No cambia la potencia (que depende de años), pero sí la regla de selección |
| Precios con empresas deslistadas | No disponible gratis (ver PF-001 §2.3) | Riesgo de sesgo al alza |

## 5. Fase 0 — frecuencia, potencia, costos

**Frecuencia**: 4 rebalanceos/año; 53 en la historia XML; ~107 si se suma el texto desde 1999 (con riesgo de parseo).

**Potencia** (α=0,05 dos colas, 80 %, z=2,80; `MDE = 2,80/√años`, `años = (2,80/IR)²`):

| Ventana de datos | Años | MDE (IR anual) |
|---|---|---|
| XML 2013 T2 – 2026 T2, toda la historia en una sola prueba | 13,0 | **0,78** |
| Texto + XML 1999 – 2026 | ~27 | 0,54 |
| Si se reserva 40 % como TEST (XML) | 5,2 | 1,23 |

| IR supuesto | Años necesarios | Comparación con el límite de ~5 años del skill |
|---|---|---|
| 0,16 (Cohen 4F ajustado) | 307 | falla |
| 0,20 (precedente del proyecto) | 196 | falla |
| 0,38 (Cohen 6F ajustado, el más favorable defendible) | 54 | falla |
| 0,59 (Cohen vs cartera propia, sin ajuste) | 22,5 | falla |
| 0,91 (Cohen 6F, sin ajuste ni retraso; no comparable) | 9,5 | falla |

Lectura: **incluso el efecto más optimista publicado (0,91), que no corresponde al diseño, necesita 9,5 años solo de TEST**. El MDE de la ventana XML completa (0,78) está **2 a 5 veces por encima** del rango razonable (0,15–0,40). El ajuste por autocorrelación o HAC no cierra una brecha de ese tamaño (skill, caso portfolio).

**Costos**: `riesgo-costos` solo midió BTCUSDT (`docs/riesgo/COSTOS_BTCUSDT.md`); **no hay costos medidos para acciones de EE. UU.** Pendiente de encargo. Con rotación trimestral de una cartera concentrada el costo anual sería chico frente al efecto, pero no cambia el veredicto: el triage ya falla por potencia antes de restar costos.

## 6. Veredicto de triage
**DESCARTADO EN EL TRIAGE (propuesto)**: el horizonte para 80 % de poder supera ampliamente ~5 años con cualquier efecto de referencia defendible (54–307 años) y aun con la cota optimista no comparable (9,5 años). Se documenta para que no se reintente sin una razón nueva (por ejemplo, una fuente que dé decenas de años de 13F estructurados con fecha real de presentación, o un diseño de evento con mucha más n independiente).

Solo reabriría el caso que el usuario acepte una prueba **descriptiva prospectiva** (no confirmatoria), lo cual es otra cosa y requeriría registro propio.

## 7. Borrador de Fase 1 (no se completa; solo opciones)

| Punto | Estado | Opciones para decidir |
|---|---|---|
| Frase falsable | **A DEFINIR POR KENSY** | (a) "Las best ideas de los N gestores más grandes, compradas al día hábil siguiente al FILING_DATE y mantenidas un trimestre, tienen exceso de retorno > 0 frente a [índice]"; (b) igual pero frente al resto de la cartera del mismo gestor (control de estilo, como Cohen et al.) |
| Métrica primaria | **A DEFINIR POR KENSY** | IR frente a S&P 500 total return · alfa 4 factores · exceso frente a la cartera propia del gestor |
| Universo y selección de gestores | **A DEFINIR POR KENSY** | Top N (20/50/100) por valor reportado en el filing anterior · solo hedge funds (requiere clasificación externa) · todos los filers |
| Definición de "best idea" | **A DEFINIR POR KENSY** | Mayor peso absoluto · mayor sobrepeso vs. peso en el índice (Cohen et al.) · mayor aumento trimestral |
| Regla de corte | **A DEFINIR POR KENSY** | p. ej. IR TEST > umbral con t ≥ 1,65 unilateral y DSR ≥ 0,95; el umbral tiene que estar **por encima del MDE** del TEST, si no la prueba no es informativa |
| Folds | **A DEFINIR POR KENSY** | Derivados de la historia: con 53 trimestres y piso de 30 rebalanceos por fold cabe **1 fold** de TEST (o 2 si se cuentan acciones-trimestre, que no son independientes) |
| N de variantes | **A DEFINIR POR KENSY** | Cada combinación (selección × definición × métrica) suma al N del DSR. Ejemplo: 3 × 3 × 1 = 9 |
| Costos | Pendiente `riesgo-costos` | Encargo de costos de acciones de EE. UU. |

Variantes contadas en este documento: **0 probadas** (no se calculó nada). Diseños considerados por escrito: 1 (HP-001). Descartados sin probar: copia de 13D de activistas (Brav, Jiang, Partnoy y Thomas, 2008) por ser evento de anuncio, no cartera grande; queda anotado.

## 8. Por qué podría fallar (aunque la potencia alcanzara)
1. **Retraso**: Cohen et al. miden en la fecha de tenencia; el 13F llega hasta 45 días después, y gestores con mejor información piden confidencialidad (Aragon et al.).
2. **Decaimiento post-publicación** (McLean y Pontiff) y masificación de la copia de 13F desde ~2013.
3. **Sesgo de supervivencia** por falta de precios de deslistadas gratuitos.
4. **Solo largos**: el 13F no muestra cortos ni coberturas; la best idea puede ser una pata de un par.
5. Precedente directo en 13F (Griffin y Xu) ya es débil y concentrado en 1999–2000.
