# HP-006 y HP-007 — Fase 0 (BTC, sin dinero)

2026-10-21. Autor: `portafolio-investigador`. Auditoría del desconfiado: **PENDIENTE**. Jefe de riesgo: no aplica mientras no avance.
**Veredicto propuesto: las dos caen en el triage. Fase 1 NO iniciada. 0 estrategias simuladas, 0 holdouts abiertos, 0 retornos de señal calculados.**
Qué se calculó (solo parámetros de potencia, no rendimiento): conteo de días por día de semana, desvío diario de BTC y coeficiente de variación del |retorno 1h|, ambos de la serie sin condicionar a ninguna señal. Citas de memoria, NO verificadas. Calendario de FOMC/CPI: conteos aproximados, sin verificar fechas oficiales (no hay fuente en el repo).

## Datos (reales)
`data/kt003/btcusdt_1h.csv.gz`: 80.307 retornos 1h, 2017-08-17 a 2026-10-20; 3.351 retornos diarios, 9,17 años; desvío diario 3,53 %; CV del |ret 1h| = 1,42. `data/mercado` (~259 días) y `data/kt002` (24 pronósticos, 20 vencidos) son insuficientes. Confirmación solo con datos posteriores a 2026-10-20.

## HP-006 — La volatilidad de BTC sube en la hora de los anuncios FOMC y CPI de EE. UU. (medición descriptiva, no se opera)
- Frase falsable (borrador): en las horas de anuncio FOMC/CPI posteriores al 2026-10-20, la media del |retorno 1h| de BTC es al menos 1,5 veces la media del mismo horario en días sin anuncio.
- Fundamento: la volatilidad responde a anuncios macro (Andersen, Bollerslev, Diebold y Vega 2003, en FX; Lucca y Moench 2015, en acciones, por el drift pre-FOMC) [no verificadas]. Qué cambia respecto del cierre EURUSD NFP/CPI: es BTC, mide volatilidad y no dirección, y no hay operación; igual comparte la familia "evento macro", así que el efecto empírico de EURUSD (3 veces menor que la literatura) pide cautela.
- Eventos: FOMC ~75 en la historia (8/año), CPI ~110 (12/año). Hacia adelante desde 2026-10-21: FOMC 8/año, CPI 12/año, juntos 20/año.
- Potencia (80 %, una cola 5 %, delta con CV 1,42): MDE de la razón −1 = 2,49 × 1,42 / √N. N=12: 1,02; N=20: 0,79; N=30: 0,65; N=75: 0,41; N=110: 0,34. Para detectar +0,5 hacen falta N≈50 (2,5 años de FOMC+CPI juntos); para +0,3 (plausible si BTC reacciona menos), N≈139 (≈7 años).
- Costos: 0 (no se opera). Utilidad económica: solo reduciría riesgo alrededor de eventos, es decir un objetivo de riesgo, no de retorno; no hay efecto en retorno que comparar con 0,30 %.
- Veredicto propuesto: **DESCARTADA como hipótesis con confirmación** (2,5 a 7 años de espera con efecto grande dudoso, y la historia 2017–2026 ya fue vista y solo serviría de exploración). Alternativa para Kensy: registro prospectivo pasivo del calendario (como medición descriptiva, aparte), sin conclusión antes de N≥50.
- Por qué podría fallar: el efecto puede ser menor que 1,5×; BTC opera 24 h y otras noticias contaminan; CV real mayor con colas pesadas; fechas de calendario mal registradas.

## HP-007 — Estacionalidad semanal de BTC (un día de la semana rinde distinto)
- Frase falsable (borrador): el retorno medio de un día de la semana fijado antes de mirar difiere del resto en al menos 0,15 % diario en datos posteriores al 2026-10-20.
- Fundamento: efectos de calendario en acciones (Cross 1973; French 1980) y reportes en cripto [de memoria, no verificados]; sin mecanismo económico claro para BTC (24/7), y los efectos de calendario tienden a desaparecer. Escoger el día mirando datos sería minería: 7 días = 7 variantes, el día debe fijarlo Kensy. **PENDIENTE DEL USUARIO.**
- Conteo: ~479 observaciones por día de semana (478–479) en 9,17 años.
- Potencia (un día contra el resto, 80 %, una cola 5 %): MDE = 0,43 % por día; con corrección por 7 variantes (Bonferroni) 0,57 %. Efecto plausible 0,10–0,20 % × 0,42 (McLean-Pontiff, no verificado) ≈ 0,04–0,08 %. Años necesarios para 0,15 % sin corrección: ~77; para 0,06 %: ~480. Hay 9,2 años en total, y ninguno posterior al corte.
- Costos 0,30 % ida y vuelta: operar un día por semana = 52 vueltas/año × 0,30 % = 15,6 % al año contra una ganancia bruta esperada de 0,15 % × 52 = 7,8 % como mucho. El costo supera el efecto aun con el efecto sin ajustar.
- Veredicto propuesto: **DESCARTADA** (potencia 3–10 veces insuficiente y costo mayor que el efecto).
- Por qué podría fallar: todo lo anterior; además, el efecto puede cambiar de signo por régimen.

## Revisadas y no abiertas
- Régimen del analista como filtro descriptivo de KT-002: KT-002 tiene 24 pronósticos (4 sin solape vencidos) y existe un solo informe del analista (`docs/analisis/2026-10-21.md`). Las observaciones efectivas son los cambios de régimen (pocos por año), no las horas; faltan años de datos. No se abre. Sería un cruce posterior a hacer cuando KT-002 tenga cientos de pronósticos sin solape y varios cambios de régimen, con N fijado de antemano.
- Flujos de ETF hacia adelante: ya descartada en HP-002 (MDE IR 1,68); nada nuevo.

## Resumen
Ninguna de las dos tiene potencia ni margen sobre costos con los datos disponibles. Recomendación: ninguna pasa a Fase 1. 0 variantes probadas, 0 resultados. Pendiente: auditoría del desconfiado y aceptación de Kensy.

## Auditoría del desconfiado y decisión del gerente (2026-10-21)
- Desconfiado: números reproducidos (80.307 retornos 1h, MDE, años); sin resultados de señal ni holdouts; veredicto **DUDAS ABIERTAS**.
- **HP-007: descarte por potencia (~77 años, costo 15,6 %/año > ganancia bruta 7,8 %/año) sin objeción. Gerente coincide: DESCARTADA.**
- **HP-006: 2 puntos MEDIOS abiertos.** (1) Los conteos FOMC (~75) y CPI (~110) son aproximados: falta calendario oficial citable (Fed/BLS) para fijar los N. (2) No se calculó ninguna señal con la historia 2017–2026, así que descartar por "historia ya vista" es débil; con N≈185 el MDE sería ≈0,18. Estado: **descarte provisional, NO cerrado**. Pendiente: calendario oficial y aclarar por escrito si la historia queda vedada o si se pre-registra primero una medición pasiva hacia adelante. No se escala a Kensy como hipótesis que pasa el triage.
- Citas (Andersen 2003, Lucca-Moench 2015, Cross 1973, French 1980, McLean-Pontiff) NO VERIFICADAS.
