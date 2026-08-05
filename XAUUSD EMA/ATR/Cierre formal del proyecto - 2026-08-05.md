# Cierre formal del proyecto (2026-08-05)

Índice: [[Bienvenido]] · Ver también [[Bitácora de decisiones]] · [[Criterios de cierre del enfoque]] · [[Plan de investigación EURUSD]] · `CLAUDE.md`

## Estado: PAUSA ACTIVA — ningún marco abierto

Los tres marcos de investigación que existieron en este proyecto están **cerrados**. No hay ninguna hipótesis en curso ni ningún marco vigente al momento de este documento. Esto no es un cierre parcial ni una pausa "hasta la próxima idea que aparezca" — es un punto de checkpoint explícito: la próxima acción de investigación requiere una decisión nueva y deliberada del usuario, no la continuación automática de lo que había.

## Resumen de los tres marcos

| Marco | Estado | Resultado clave |
|---|---|---|
| **XAUUSD walk-forward** (técnico + biblioteca de factores macro, diario e intradía) | **CERRADO 2026-08-04** | 0/3 walk-forwards completos pasando la regla de corte en la ronda intradía (Momentum DXY H4 t=-2.862 p=0.0042, edge negativo significativo; Risk-off US500 H4 t=+1.525 p=0.1271, positivo sin significancia), sumado al 0/8 de la ronda macro-diaria previa y al fallo de DFII10 (el mejor resultado del proyecto, t marginal p=0.059, y aun así insuficiente) |
| **EURUSD walk-forward** (carry + momentum, factores macro con frecuencia suficiente) | **CERRADO 2026-08-04** | H1 (carry diferencial de tasas): t=+0.754 (p=0.4507), colapsa a t=-0.180 sin el fold más fuerte — cambia de signo. H2 (risk-off US500 H4): t=-1.849 (p=0.064) pooled, t=-2.245 (p=0.025) sin el fold más fuerte. H3 (VIX-sorpresa) y el candidato explorado para H4 (NFP-sorpresa) descartados en el triage de Fase 0, sin llegar a walk-forward |
| **EURUSD event study** (sorpresa macro NFP/CPI, metodología distinta — t-test de ventana fija, no walk-forward de trades) | **CERRADO 2026-08-05** | 178/178 eventos evaluados, sin descartes por datos. Efecto observado 2-3 pips en las tres ventanas (1h/4h/24h) vs. MDE del propio diseño de 4.35 pips y efecto citado en literatura (Andersen et al. 2003) de 8 pips — **efecto real observado ~3 veces menor que el citado como referencia**, ni siquiera se acerca al piso estadísticamente detectable. Las tres ventanas fallan el screen in-sample (t≥1.65 unilateral) por márgenes amplios, ninguna llega a evaluación OOS |

Detalle completo de cada marco, con las cifras de cada hipótesis individual, en [[Bitácora de decisiones]] y en las notas de fase de cada hipótesis (enlazadas desde ahí).

## Patrón acumulado a través de los tres marcos

No es un patrón de "mala suerte hipótesis por hipótesis" — es consistente a través de dos instrumentos (XAUUSD, EURUSD), dos frecuencias (diaria e intradía) y dos metodologías (walk-forward de trades, event study de ventana fija): ningún diseño probado hasta ahora, con ningún driver macro probado (tasas reales, DXY, crédito, renta variable, VIX, carry, sorpresas de calendario), produjo un edge que pase la regla de corte pre-registrada con márgenes claros. Los resultados más fuertes del proyecto entero (DFII10 p=0.059, H2 EURUSD p=0.064) son marginales, no robustos — y el resto falla por márgenes amplios, no ajustados.

## Qué significa la pausa, en la práctica

- No se abre ninguna hipótesis nueva de trading (macro, técnica, o de cualquier otro tipo) sin que el usuario tome primero la decisión pendiente (ver abajo).
- La disciplina de validación ya construida (`hypothesis-gate`, walk-forward anclado, triage de Fase 0, DSR, `factor-independence`, `data-integrity`) queda intacta y no se descarta — si el proyecto retoma investigación, retoma con el mismo rigor, no desde cero.
- El código y los scripts de cada hipótesis quedan en el repo como registro reusable (walk-forward de EURUSD, extractor de calendario MT5, pipeline de event study) — no se borra nada, por si una decisión futura reabre alguno de estos caminos con una razón nueva.
- Cualquier infraestructura en vivo que siga corriendo (loggers pasivos, si los hay) no está automáticamente afectada por este documento — un cambio de estado de infraestructura es una decisión operativa aparte, no implícita en este cierre.

## Próxima decisión pendiente (del usuario, no del asistente)

**Revisar si el enfoque macro en FX/oro (factores macro observables, frecuencia diaria o intradía, walk-forward u event study) es el diseño adecuado, o si el patrón acumulado de tres marcos cerrados es evidencia de que hace falta un cambio más de fondo** — de instrumento, de clase de driver (no macro), de horizonte, o de objetivo del proyecto en sí. Esta pregunta no tiene una respuesta implícita en este documento a propósito — es la pregunta que el usuario tiene que responder antes de que se reabra cualquier trabajo de investigación nuevo.

## Ver también
[[Bitácora de decisiones]] · [[Criterios de cierre del enfoque]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Plan de investigación EURUSD]] · `CLAUDE.md`
