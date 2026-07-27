# Ruptura de estructura + retest — trigger de entrada nuevo

Índice: [[Bienvenido]] · Ver también [[Estructura de swings (HH-HL)]] · [[Metodología]] · [[Diagnóstico entrada-vs-salida]] · [[Cronología]]

## Hipótesis

A diferencia de MTF y Estructura (filtros de tendencia sobre el mismo trigger), esta variante **reemplaza el cruce EMA9/21 por completo**:

1. Reutiliza `calcular_estructura_swings` (fractal 2-2) para detectar el swing high/low confirmado más reciente.
2. Ruptura: vela M15 cierra más allá del swing (por encima del último swing high para largos / por debajo del último swing low para cortos).
3. Retest válido: ventana fija de 20 velas (~5hs) tras la ruptura, el precio vuelve a tocar la zona rota (nivel de swing ± 0.25×ATR), sin ninguna vela cerrando del lado equivocado entre ruptura y retest.
4. Confirmación de entrada — **versión simple**, elegida explícitamente sobre la versión estricta: la vela que toca la zona de retest cierra del lado correcto del nivel (NO se exige vela de rechazo/mecha). Motivo: minimizar variables nuevas en el primer test; la versión con confirmación de momentum más estricta quedó pendiente para un experimento aparte si esta resultaba prometedora.
5. Ventana (20 velas) y margen (0.25×ATR) fijos, sin barrido.
6. SL/TP igual al ya validado (ATR-based) — una sola variable nueva por vez.

## Regla de decisión del holdout (pre-registrada antes de implementar)

Candidato elegible: ≥30 trades netos de spread en holdout en vivo. "Pasa": elegible Y t-stat (`metrica_robusta`) > 2.0. Si ninguno pasa, no se lleva nada a real. Desempate entre varios: profit factor neto de spread más alto. (Esta regla se definió cuando el trigger todavía era candidato a instrumentarse en el logger — quedó sin aplicar porque no sobrevivió el filtro exploratorio previo, más barato.)

## Implementación

`calcular_rupturas_retest`/`generar_senales_retest`, extendiendo `calcular_estructura_swings` para exponer `ultimo_swing_high`/`ultimo_swing_low` (niveles crudos). Constantes `RETEST_VENTANA=20`, `RETEST_MARGEN_ATR_MULT=0.25`.

Decisión de diseño importante: a diferencia de MTF/Estructura (filtro precalculado una vez sobre el dataset completo), acá la detección de swings + escaneo de retest se recalcula desde cero dentro de cada TRAIN/TEST de cada fold — la ventana de 20 velas es lo bastante grande como para fugar información de TEST hacia TRAIN si se precalculara antes de cortar folds.

Smoke test previo (15.000 velas completas, sin split): 851 señales crudas (418 compra / 433 venta) — frecuencia base similar o mayor a la del cruce EMA9/21+trend (546-548).

## Resultado (walk-forward de 9 folds anclados, 2026-07-24)

443 trades TEST acumulados (33-62 por fold, todos por encima del piso de 30 — buena muestra), pero:

- Solo **5/9 folds rentables neto de spread** (esencialmente cara o cruz).
- **R neto TOTAL agregado NEGATIVO: -6.72R en 443 trades** (-0.015R/trade). El peor fold (Fold 5: -19.86R) pesa más que el mejor (Fold 7: +10.20R) — ni siquiera hay un fold dominante positivo que sostenga el agregado como en baseline.
- Comparado fold a fold contra baseline, el delta oscila erráticamente entre -24.23R y +16.31R sin patrón direccional consistente — mismo síntoma de inestabilidad visto en MTF/Estructura, ahora en un trigger que no comparte código de entrada con el cruce EMA9/21.

## Diagnóstico entrada vs. salida (2026-07-24)

Edge de entrada débil y no persistente: en folds 6-9 solo 1 de los 5 R:R barridos mostraba edge>0 en TRAIN (vs 4-5/5 en baseline) — el "edge" dependía de acertar exactamente un R:R. El R:R elegido en TRAIN solo se sostuvo en TEST en 4/9 folds (44%, básicamente azar). El fold que explota (Fold 5: TRAIN edge +4.2pp, TEST -10.1pp con el mismo R:R, R total -19.00R) confirma que ahí la señal falla de lado con cualquier R:R.

## Conclusión

**El problema es la entrada, no la salida** — a diferencia de baseline, un exit distinto (partial/trailing) no lo hubiera salvado. Descartado en el filtro exploratorio; por la regla de trabajo acordada ("primero el filtro barato, solo si sobrevive se invierte en extender el logger"), no se justificó instrumentar el logger en vivo para este candidato.
