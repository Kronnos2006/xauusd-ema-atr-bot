# HP-004 y HP-005 — Fase 0 (BTC, sin dinero)

2026-10-21 (miércoles). Autor: `jefe-portafolio` haciendo el rol de `portafolio-investigador` (no hay herramienta para convocarlo). Auditoría del desconfiado: **PENDIENTE** (no se pudo convocar). Jefe de riesgo: no aplica mientras no avance.
**Veredicto: las dos caen en el triage (propuesto). Fase 1 NO iniciada. 0 estrategias simuladas, 0 holdouts abiertos.**
Qué NO contiene: ningún retorno de estrategia ni de señal. Solo calendario, conteo de cambios de señal, volatilidad diaria de BTC (parámetro de potencia), turnover (costo) y la correlación entre pesos y retorno (parámetro de potencia, no rendimiento).

## Datos usados (reales, en el repo)
`data/kt003/btcusdt_1h.csv.gz`: 80.308 velas 1h, 2017-08-17 a 2026-10-20 → 3.352 cierres diarios, 9,17 años, vol anual 67 %. Anomalía: 43 filas tienen marca de tiempo fuera de la hora exacta (ej. 2018-02-09 09:28:14); el resample diario las absorbe, pero conviene que `vigia-datos` lo mire. `data/mercado` solo tiene ~259 días (1d) y 209 velas 4h: insuficiente, no se usó. Script: scratchpad de sesión (no se versiona).

## HP-004 — Momentum de series de tiempo en BTC (largo/fuera con cruce de medias)
- Idea: BTC queda largo cuando su tendencia de 20–200 días es alcista y fuera cuando no. Fundamento: Moskowitz, Ooi y Pedersen (2012, JFE) para futuros; Liu y Tsyvinski (2021, RFS) para cripto [citas de memoria, NO verificadas hoy]. Ya cerrados en este proyecto: TF_Basket_H1 y XAUUSD técnico (sin edge); lo que cambia: instrumento BTC y horizonte diario, pero sigue siendo trend following.
- Frecuencia (solo estado de la señal): cruce 20/100 = 34 cambios (3,8 por año); cruce 50/200 = 18 cambios (2,1 por año). Largo ~52 % del tiempo. Piso de 30 operaciones por fold: 20/100 apenas llega en todo el período, inalcanzable por fold (ya lo anticipaba ES-001).
- Potencia (80 %, una cola 5 %, días independientes, contraste días-largo vs días-fuera): MDE = 0,31 %/día ≈ **Sharpe 1,67**. Efecto plausible: Sharpe 0,3–0,5 publicado × 0,42 (McLean-Pontiff 2016, de HP-002) = 0,13–0,21. Años necesarios: 102 (efecto 0,5) a ~640 (0,2). Hay 9,2.
- Costos 0,30 % ida y vuelta: 0,3–0,6 % por año; son chicos frente al efecto, **el problema no es el costo sino la potencia**.
- Veredicto: **DESCARTADA en el triage (propuesto)**: MDE 1,67 vs efecto 0,13–0,21; muestra 10–60 veces menor a la necesaria; menos de 30 ops por fold.

## HP-005 — BTC con escala por volatilidad (volatility-managed): exposición = 40 % / vol 30d, tope 1, rebalanceo semanal
- Idea: reducir exposición cuando la vol realizada sube mejora el Sharpe respecto de mantener BTC. Fundamento: Moreira y Muir (2017, JF) en acciones [de memoria, NO verificada]; en cripto no se citó evidencia verificada. Tiene lógica propia (la vol persiste, el retorno esperado no sube con ella) y no es un marco cerrado del proyecto.
- Frecuencia: rebalanceo semanal, ~474 decisiones en 9,1 años; no hay problema de conteo.
- Costos: turnover 3,05 veces el capital por año → 0,46 % por año a 0,15 % por lado. Despreciable.
- Potencia (contraste de Sharpe estrategia vs mantener; correlación entre ambos 0,94; SE 0,12): **MDE = 0,29 de diferencia de Sharpe**. Efecto plausible: +0,1–0,2 en acciones × 0,42 = 0,04–0,08. Años necesarios: 76 (Δ 0,1), 19 (Δ 0,2), ~300 (Δ 0,05). Hay 9,1.
- Veredicto: **DESCARTADA en el triage (propuesto)** como hipótesis de Sharpe. Nota: lo que sí se mediría con potencia de sobra es otra cosa, la reducción de la volatilidad y del peor drawdown (objetivo de riesgo, no de retorno). Eso sería una medición descriptiva (no dinero ni edge) y requiere decisión de Kensy/gerente; no se propone como hipótesis.

## Qué falta
1. Auditoría del desconfiado (verificar citas, que el MDE use los supuestos correctos y que la correlación de HP-005 no cuente como mirar resultados).
2. Aceptación de Kensy del descarte, o decisión sobre la medición descriptiva de vol/drawdown.
3. Nada de Fase 1: se pide solo si Kensy no acepta el descarte.

## Correcciones tras auditoría del desconfiado (2026-10-21, gerente)
- **Declaración corregida:** la "correlación 0,94" de HP-005 se derivó de una serie de retornos de la estrategia (solo como parámetro de potencia). Se reconoce acá; con correlación a priori 0,8 el MDE sube (peor para la hipótesis). El descarte no depende de ese valor.
- **Etiqueta corregida:** el "Sharpe 1,67" de HP-004 es el MDE de un contraste de medias días-largo vs días-fuera con días independientes, NO el MDE del Sharpe de la estrategia contra cero (≈0,82). Con 34 cambios hay ~35 tramos, no 3.352 días independientes: la potencia real es peor. El descarte se mantiene.
- Todas las citas (Moskowitz-Ooi-Pedersen 2012, Liu-Tsyvinski 2021, Moreira-Muir 2017, McLean-Pontiff 2016) y el factor 0,42 siguen NO VERIFICADOS.
- Script de verificación del desconfiado versionado en `HP-004_HP-005_verificacion_desconfiado.py`. Las 43 marcas de tiempo irregulares de btcusdt_1h quedan para vigia-datos.
- Estado: descarte propuesto; auditoría con puntos MEDIOS ya corregidos en el texto (re-confirmación del desconfiado pendiente) y aceptación de Kensy pendiente.
