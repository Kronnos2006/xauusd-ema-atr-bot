# Plan de investigación — Marco EURUSD
*Iniciado: 2026-08-04*

Índice: [[Bienvenido]] · Ver también [[Bitácora de decisiones]] · [[Criterios de cierre del enfoque]] (marco XAUUSD, cerrado 2026-08-04) · `CLAUDE.md`

## Objetivo
Validar si el pipeline puede detectar factores macro con edge estadístico real en EURUSD.
Presupuesto: máximo 4 hipótesis con walk-forward completo o hasta 2027-02-04, lo que llegue primero.

**Presupuesto consumido: 2/4 con walk-forward completo (H1, H2), H4 no gastada — ver cierre formal abajo.**

## CIERRE FORMAL DEL MARCO (2026-08-04)

**Cerrado — el triage eliminó todos los candidatos restantes por el mismo problema estructural.** 0/2 walk-forwards completos pasando el corte (H1 carry, H2 risk-off US500), más los candidatos restantes evaluados (H3 VIX-sorpresa, WTI, NFP-sorpresa) fallando todos en el triage de frecuencia — por dos motivos que se repiten: **frecuencia insuficiente** (el driver publica/actualiza con un techo de frecuencia bajo, sin importar el diseño) o **mecanismo ya incorporado en el precio** (niveles observables, no sorpresas — el problema que motivó reformular H3).

**Decisión deliberada**: se cierra el marco sin gastar la 4ª hipótesis del presupuesto — no se fuerza una hipótesis débil solo para agotar el número. El presupuesto es un límite máximo, no un objetivo a cumplir.

Nuevo marco: a definir. Ver [[Bitácora de decisiones]] para el registro de la decisión.

## Hipótesis evaluadas

### H1 — Carry diferencial de tasas (EZ 3M − US 3M)
- Estado: DESCARTADA
- Resultado: t=+0.754 (p=0.45), colapsa a -0.180 sin fold dominante
- Lección: carry en spot FX requiere cobrar swap overnight — no disponible en este diseño

### H2 — Risk-off US500 H4 → EURUSD
- Estado: DESCARTADA
- Resultado: 3/8 folds rentables, R neto -32.02R en 701 trades; t=-1.849 (p=0.064) pooled, t=-2.245 (p=0.025) sin el fold más fuerte; DSR=0.0000 (N=144)
- Lección: mismo driver (US500) que en XAUUSD dio positivo-no-significativo; acá dio negativo — ningún resultado pasa el corte con este driver en ninguno de los dos targets

### H3 — VIX como sorpresa (rolling std) → EURUSD
- Estado: DESCARTADA EN EL TRIAGE (Fase 0, no llegó a walk-forward)
- Resultado: 22.37 ep/año (k=1.25, N=60, el caso más restrictivo) → horizonte 8.58 años (ref. DFII10) / 13.68 años (ref. conservadora)
- Nota: WTI petróleo → EURUSD se exploró antes de reformular a VIX-sorpresa — dio 34.40 ep/año (k=1.25), horizonte 5.58-8.90 años, fronterizo — no se persiguió más (driver indirecto, relación inestable) y no consumió un slot de hipótesis propio
- Lección: el problema no era el driver puntual, era que se probaban NIVELES ya incorporados en el precio, no sorpresas — la reformulación a "sorpresa" (rolling std) no alcanzó de todos modos por frecuencia insuficiente

### H4 — NO GASTADA (decisión deliberada)
- Candidato explorado en triage antes de decidir no gastar el slot: NFP-sorpresa vía reacción de precio (proxy de sorpresa sin datos de consenso, que no están disponibles) — 12.07 ep/año (frecuencia fija por calendario, sin grilla de k), horizonte 15.91-25.35 años — el peor resultado de frecuencia de todo el proyecto (peor que CPI-sorpresa estimado en la ronda XAUUSD, 8-12.75 años)
- Se cierra el marco sin gastar H4 formalmente — ver "Cierre formal del marco" arriba

## Criterios de cierre del marco EURUSD
El marco se replantea si se cumple cualquiera de estas condiciones:
- 4 hipótesis con walk-forward completo sin pasar el corte
- Patrón sistemático: mismo tipo de falla en hipótesis distintas
- Triage elimina todos los candidatos restantes
- Fecha límite: 2027-02-04

## Reglas vigentes
- Toda hipótesis pasa hypothesis-gate antes de cualquier backtest
- No probar variantes de hipótesis ya descartadas
- Commit + vault + bitácora después de cada resultado
- No relajar umbrales estadísticos después de ver resultados

## Ver también
[[Bitácora de decisiones]] · [[Criterios de cierre del enfoque]] · `CLAUDE.md`
