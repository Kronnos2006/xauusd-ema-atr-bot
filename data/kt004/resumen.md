# KT-004 — acierto direccional a 4 h (2024-08-01 → 2026-07-31; holdout 2026-08 → 2026-10 sin tocar)

Responde «¿predice la dirección?», no «¿es rentable?». Sin costos, deslizamiento ni tamaño de posición.

## Primario: Kronos en ETHUSDT — **NO PASA**

- Kronos 52.06 % vs «siempre sube»: 1.71 puntos; McNemar 1 cola p = 0.067167 (solo Kronos 1259, solo sube 1184), n = 4378
- Contra moneda al aire (50 %): p 1 cola = 0.003409
- Persistencia: 2117/4376 = 48.4 % · siempre sube: 2204/4378 = 50.3 %
- Regla: p < 0,05 y diferencia ≥ 2 puntos. Pasar no es ventaja ni autoriza operar.

## Secundarios (Holm, 5 pruebas)

- kronos SOLUSDT: 1.93 puntos, p 0.046642 / Holm 0.23321
- kronos BNBUSDT: -1.51 puntos, p 0.907202 / Holm 1.0
- kronos XRPUSDT: 1.7 puntos, p 0.064721 / Holm 0.258884
- timesfm ETHUSDT: -0.16 puntos, p 0.568662 / Holm 1.0
- kt001 ETHUSDT: 1.12 puntos, p 0.163745 / Holm 0.491235

## Chequeo de contaminación (Kronos ETH, descriptivo)

- Antes de 2025-10: 0.5213 · desde 2025-10: 0.5195 · alerta: False

## Agrupado 4 activos (descriptivo): 0.96 puntos, p bootstrap 0.1007

## Por activo (Kronos / siempre sube; descriptivo)

- BNBUSDT: 2236/4372 = 51.1 % / 2302/4372 = 52.6 % · acierto mínimo para cubrir 0,20 % ≈ 63.2 %
- ETHUSDT: 2279/4378 = 52.1 % / 2204/4378 = 50.3 % · acierto mínimo para cubrir 0,20 % ≈ 60.4 %
- SOLUSDT: 2270/4360 = 52.1 % / 2186/4360 = 50.1 % · acierto mínimo para cubrir 0,20 % ≈ 58.6 %
- XRPUSDT: 2233/4364 = 51.2 % / 2159/4364 = 49.5 % · acierto mínimo para cubrir 0,20 % ≈ 59.2 %
