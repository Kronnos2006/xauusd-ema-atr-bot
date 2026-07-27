# Estructura de swings (HH/HL) — filtro de tendencia

Índice: [[Bienvenido]] · Ver también [[EMA baseline (M15)]] · [[MTF - filtro H1]] · [[Metodología]] · [[Cronología]]

## Hipótesis

Tercera definición de "tendencia" (tras M15-EMA y [[MTF - filtro H1]]), probada con la misma infraestructura de walk-forward: swing highs/lows con fractal fijo `SWING_L=SWING_R=2` (ventana de 5 velas, no tuneado por fold), clasificados como Higher-High/Higher-Low (alcista) o Lower-High/Lower-Low (bajista) contra el swing confirmado inmediatamente anterior del mismo tipo. El trigger de entrada (cruce EMA9/21 M15) no cambia.

## Anti-lookahead

Un swing en la barra `i` recién se confirma en `i+SWING_R` (`shift(SWING_R)`) — mismo principio que `valido_desde` de MTF, pero posicional en barras en vez de por tiempo de calendario, sin necesitar `merge_asof` (todo vive en M15). Warm-up calculado dinámicamente: la fila donde se confirmó el 2º swing de cada tipo, con piso en `EMA_TREND`. Verificado sano: 2º swing confirmado en la fila 18, muy por debajo del piso de 50.

Función nueva: `calcular_estructura_swings`, `generar_senales_estructura`.

## Resultado (walk-forward de 9 folds anclados, 2026-07-23)

- **3/9 folds rentables neto** (vs 5/9 de baseline y de MTF) — peor que las otras dos variantes.
- R total promedio +1.39R/fold, pero **123% del R neto concentrado en un solo fold** (Fold 9); sin ese fold, resultado neto negativo (-2.35R en 90 trades).
- Solo 107 trades TEST acumulados (vs 325 baseline, 219 MTF) — el filtro de 5 velas es mucho más restrictivo que los otros dos, sin mejorar la calidad de lo que deja pasar.

## Conclusión

Descartada. Junto con baseline y MTF, forma parte del insight acumulado: ninguna definición de "tendencia" probada logra filtrar el ruido del cruce EMA9/21 M15 de forma que sostenga un edge no dominado por 1 fold. Esto apuntó a que el problema no está en el filtro de tendencia sino en el trigger de entrada mismo — motivó probar un trigger nuevo en vez de una cuarta variante de filtro, ver [[Ruptura y retest]].
