# H1 retuneado — cruce EMA9/21/50 con SL/R:R propios

Índice: [[Bienvenido]] · Ver también [[EMA baseline (M15)]] · [[MTF - filtro H1]]

## Motivación (decisión de pivote, 2026-07-24)

Tras el cierre de M15 (ver [[EMA baseline (M15)]]), evidencia externa (estudio con 8.693 trades reales en XAUUSD, no un backtest propio) mostró que el cruce EMA9/21 en H1 tenía expectancy positiva modesta (+0.115R/trade, 296 trades) y que timeframes lentos rinden mejor que M15 en oro.

**Distinto de [[MTF - filtro H1]]**: no es la misma hipótesis. MTF usa H1 solo como filtro de dirección para señales que se siguen disparando en M15. Acá el trigger se corre directamente en H1. El 2026-07-22, el mismo día del walk-forward original, ya se había corrido una primera versión de esto (mismos EMA9/21/50 + ATR14 + SL 1.5×ATR, **sin retunear**, trasplantando directo los parámetros afinados para M15) y había dado resultado claramente negativo (1/9 folds rentable, -3.22R/fold promedio). Ese resultado no decía nada sobre si un cruce EMA9/21 con exit *propio* de H1 tiene edge — el ATR de una vela H1 no es comparable al de M15, así que era esperable que los parámetros de SL/TP afinados para M15 no transfirieran sin retunear. Esta hipótesis retunea SL/R:R específicamente para H1, reutilizando toda la infraestructura ya construida (walk-forward anclado, `metrica_robusta`, `diagnostico_entrada_vs_salida`) sin tocarla.

## Regla de corte (pre-registrada antes de tunear)

Alcance acotado a propósito: mantener EMA9/21/50 (mismos períodos que M15 y que el estudio externo), retunear SOLO `SL_ATR_MULT` y `RR_RATIO`, vía el mecanismo honesto ya existente (barrido en TRAIN, confirmación única en TEST) — **una sola pasada limpia, no una serie de intentos iterativos**. Si esa pasada no muestra (a) edge que sostenga en TEST en la mayoría de los folds Y (b) resultado no dominado por un solo fold de forma marcada, H1 se descarta ahí mismo y D1 pasa a ser el candidato siguiente, sin iterar ajustando parámetros sueltos.

## Regla de rango de datos

No atada a igualar los 296 trades del estudio externo (otro broker/spread/período). Atada al piso interno del proyecto: 9 folds × 30 trades/fold ≈ 270 trades como piso. Con 4 años de H1 (2022-07-24 → 2026-07-23, 23.561 velas), 811 señales base — muy por encima del piso. No hizo falta extender el rango.

## Resultado (walk-forward de 9 folds, una sola pasada, 2026-07-24) — DESCARTADO

- **Folds rentables neto de spread: 4/9** (minoría — incumple la condición (a) de la regla de corte).
- **R neto total: -23.22R en 341 trades.** Sin el mejor fold (Fold 8, +9.30R): -32.52R en 319 trades (-0.102R/trade). Ni siquiera hay un fold dominante que sostenga el agregado.
- **Señal de alerta en el propio TRAIN**: el t-stat de selección fue decayendo con más datos acumulados — de +1.54 (fold 1, TRAIN chico) a +0.51-0.89 (folds 6-9, TRAIN grande). Un edge real debería mantenerse o fortalecerse con más datos, no diluirse — patrón característico de edge ilusorio/de muestra chica, no de un edge genuino que se desvanece.
- Configuración elegida (SL 2.0×ATR, R:R 1:2.5, filtro de sesión CON) fue consistente en casi todos los folds, pero esa consistencia no se tradujo en resultado OOS consistente.

## Conclusión

H1 con EMA9/21/50 no tiene edge confirmable, ni siquiera retuneando SL/R:R. Cumple la regla de corte sin ambigüedad. Este resultado, sumado a los otros 4 fallos convergentes de la familia EMA9/21, motivó retirar la familia entera — ver decisión final en [[Bienvenido]] y [[EMA baseline (M15)]].

## Ver también
[[Metodología]] · [[Cronología]] · [[Errores y bugs corregidos]]
