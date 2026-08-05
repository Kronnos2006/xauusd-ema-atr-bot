# Risk-off US500 H4 → EURUSD — fase 1 (H2 del marco EURUSD)

## Descartada (2026-08-04) — edge negativo, no pasa el checkpoint

Índice: [[Bienvenido]] · Ver también [[Plan de investigación EURUSD]] · [[Bitácora de decisiones]] · [[hypothesis-gate]] · [[Risk-off US500 H4 - fase 1]] (versión XAUUSD, mismo driver)

## Contexto

H2 del marco EURUSD (ver `Plan de investigación EURUSD.md`), tras el descarte de H1 (carry diferencial de tasas). Mismo driver ya usado en el marco XAUUSD (Risk-off US500 → XAUUSD, positivo pero no significativo: t=+1.525/p=0.1271, DSR=0.1806) — acá el target y el mecanismo de transmisión son distintos: caída en acciones → fortalecimiento del dólar como refugio → EURUSD baja (no "oro sube por refugio", sino "dólar sube por refugio, y como EUR es la contraparte, EURUSD cae").

## Hipótesis (frase falsable)

Cuando el retorno del US500 en la vela H4 cerrada **cae** más de k desvíos estándar de su propia distribución histórica (std sobre la serie completa disponible, 2012-08-06+, sin rolling) — direccional por diseño, solo caídas cuentan — el **EURUSD tiene sesgo BAJISTA** (el dólar se fortalece como refugio, EUR se deprecia relativo) en las M velas H4 siguientes.

**Grilla declarada (3×3, sin resweepeo)**: k∈{0.75, 1.0, 1.25} × M∈{1, 2, 3} velas H4.

Dirección **siempre VENTA EURUSD** — fijada por la frase falsable, no un parámetro de la grilla (mismo patrón que la versión XAUUSD, donde la dirección era siempre COMPRA; acá es siempre VENTA por el signo opuesto de la relación dólar-EUR vs. dólar-oro).

## Triage de frecuencia (Fase 0) — ya medido, mismo driver

Idéntico al de la versión XAUUSD (la frecuencia depende solo de US500, no del target): 62.89 episodios/año (k=1.25), horizonte proyectado 3.05 años (ref. DFII10) / **4.87 años** (ref. conservadora) — pasa con el mismo margen fino de antes. Verificado que EURUSD H4 cubre sin huecos la ventana 2012-08-06 → 2026-08-04 (21769 velas).

## Folds — reusa la derivación ya hecha (mismo driver, misma distribución temporal)

**K=8 folds** (fold mínimo real 36 trades a k=1.25, +20% de margen sobre el piso de 30 — ver [[Risk-off US500 H4 - fase 1]] para el detalle completo de la distribución real por K).

## Regla de corte (pre-registrada)

- \|t-stat\| > 1.96 sobre R neto de TEST, con y sin el fold de mayor R neto.
- **DSR ≥ 0.95**, N = **144** (esta grilla 3×3×8=72 + la versión XAUUSD del mismo driver, otras 72 — confirmado por el usuario: el driver es el mismo US500 aunque el mecanismo de transmisión y el target difieran, y eso cuenta para el conteo de variantes).
- Spread real (EURUSD, `SPREAD_PUNTOS_EURUSD=15`, mismo supuesto documentado que en `hipotesis_carry_eurusd.py` — este broker no dio un spread live confiable en la consulta).
- Entrada D+1 (primera vela H4 de EURUSD tras el inicio del episodio), riesgo = ATR14 H4 (EURUSD) × `SL_ATR_MULT`, salida = horizonte M o SL. Sin pyramiding.

## Chequeo de no-reuso de grilla

La forma de la grilla (k, M) es idéntica a la versión XAUUSD, pero el pipeline de simulación es distinto (target EURUSD, dirección opuesta, ATR de EURUSD no de oro) — no es un resweepeo de la misma combinación ya evaluada, es el mismo diseño aplicado a un mercado distinto. Documentado para que quede trazable, no para justificarlo sin más.

## Resultado (2026-08-04)

Script: `hipotesis_riskoff_us500_h4_eurusd.py`.

**❌ NO PASA EL CHECKPOINT** — edge negativo, sin ambigüedad de signo.

| Métrica | Valor |
|---|---|
| Folds evaluables | 8/8 |
| Folds rentables | 3/8 (37.5%) |
| Trades TEST acumulados | 701 |
| R neto acumulado | -32.02R |
| t-stat pooled (todos los folds) | -1.849 (p=0.0644) |
| t-stat sin el fold más fuerte (Fold 1, +4.77R) | -2.245 (p=0.0248) |
| DSR (N=144) | 0.0000 |

Con todos los folds no cruza \|t\|>1.96 (queda marginal), pero sin el fold que más ayuda se vuelve significativamente negativo — en ningún caso el resultado es positivo. DSR confirma sin matices (Sharpe observado ya negativo, -0.0699).

Segunda vez que el driver US500 (risk-off) se prueba: en XAUUSD dio positivo-no-significativo (t=+1.525), acá dio negativo (t=-1.849/-2.245). Dos resultados distintos con el mismo driver, ninguno pasando el corte — no hay un patrón limpio de "funciona en un lado sí y en el otro no", ambos fallan por razones distintas.

## Estado

**Cerrada — no pasa.** H2 del marco EURUSD descartada. Ver [[Plan de investigación EURUSD]] (van 2/4 hipótesis del presupuesto) y [[Bitácora de decisiones]].

## Ver también
[[Plan de investigación EURUSD]] · [[Bitácora de decisiones]] · [[hypothesis-gate]] · [[Risk-off US500 H4 - fase 1]]
