# Instrucciones de proyecto

Proyecto de investigación estadística cuantitativa vía MT5. Sin ejecución de órdenes, sin capital real.

## Estado (desde 2026-08-05, reafirmado 2026-08-06): PAUSA ACTIVA — ningún marco abierto

Los tres marcos originales de este proyecto están **cerrados**. El 2026-08-06 el usuario reabrió investigación con un cuarto marco (TF_Basket_H1, trend following técnico) que también quedó cerrado, esta vez en Fase 0 sin llegar a walk-forward — ver detalle abajo. No hay ninguna hipótesis en curso. La próxima acción de investigación requiere una decisión nueva y explícita del usuario, no la continuación automática de lo último que se probó — no abrir ninguna hipótesis nueva de trading (macro, técnica, o de cualquier otro tipo) sin esa decisión.

**Próxima decisión pendiente (del usuario)**: revisar si el enfoque macro en FX/oro (o técnico, tras el cierre de TF_Basket_H1) es el diseño adecuado, o si el patrón acumulado de cuatro marcos cerrados es evidencia de que hace falta un cambio más de fondo (instrumento, clase de driver, horizonte, objetivo del proyecto). Ver `XAUUSD EMA/ATR/Cierre formal del proyecto - 2026-08-05.md` para el resumen de los tres primeros cierres y `XAUUSD EMA/ATR/TF_Basket_H1 — Fase 0.md` para el cuarto.

### El cuarto marco cerrado (2026-08-06)

- **TF_Basket_H1** (trend following Donchian/MA, basket diversificado de 10 instrumentos: EURUSD, USDJPY, GBPUSD, XAUUSD, XAGUSD, TLT, LQD, GDX, XLE, NVDA) — cerrado en **Fase 0**, nunca llegó a walk-forward. De las 6 señales pre-registradas, 4 no pasaron el triage de frecuencia inicial; de las 2 sobrevivientes (Donchian 20, MA 10/50), ninguna mostró edge viable en un panel cruzado Moskowitz-style con efecto empírico propio (corrigiendo por correlación real entre instrumentos, N_efectivo=4.40 de 10): Donchian 20 sin edge (t≈-0.04), MA 10/50 no significativo (t≈0.93, p=0.35) con Sharpe de portfolio implícito (0.229) ya por debajo del objetivo de la hipótesis (Sharpe>0.3) antes de restar costos de transacción. Detalle completo en `XAUUSD EMA/ATR/TF_Basket_H1 — Fase 0.md`.

### Los tres marcos originales cerrados

- **XAUUSD walk-forward** (técnico + biblioteca de factores macro, diario e intradía) — cerrado 2026-08-04. 0/3 walk-forwards completos pasando la regla de corte en la ronda intradía (Momentum DXY H4 con edge negativo significativo, Risk-off US500 positivo pero sin significancia), sumado al 0/8 de la ronda macro-diaria previa y al fallo de DFII10 (el mejor resultado del proyecto, y aun así insuficiente). Activó el criterio 4 de `XAUUSD EMA/ATR/Criterios de cierre del enfoque.md`. Detalle en `XAUUSD EMA/ATR/Bitácora de decisiones.md` (fila 2026-08-04, "Cierre formal del marco XAUUSD").
- **EURUSD walk-forward** (FX carry + momentum, factores macro con frecuencia suficiente, folds con piso 30 trades) — cerrado 2026-08-04, sin gastar el presupuesto completo (2/4 hipótesis con walk-forward). H1 (carry): t=+0.754 (p=0.4507), colapsa a t=-0.180 sin el fold más fuerte. H2 (risk-off US500): t=-1.849 (p=0.064), t=-2.245 (p=0.025) sin el fold más fuerte. H3 (VIX-sorpresa) y el candidato explorado para H4 (NFP-sorpresa) descartados en el triage de Fase 0. Detalle completo: `XAUUSD EMA/ATR/Plan de investigación EURUSD.md`.
- **EURUSD event study** (sorpresa macro NFP/CPI, t-test de ventana fija por release, no walk-forward de trades) — cerrado 2026-08-05. 178/178 eventos evaluados, sin descartes por datos. Efecto observado 2-3 pips en las tres ventanas (1h/4h/24h) vs. MDE del propio diseño (4.35 pips) y efecto citado en literatura (Andersen et al. 2003, 8 pips) — efecto real ~3 veces menor que la referencia citada. Las tres ventanas fallan el screen in-sample (t≥1.65 unilateral) por márgenes amplios, ninguna llega a evaluación OOS. Detalle en `Bitácora de decisiones.md` (fila 2026-08-05).

El vault de investigación (Obsidian) sigue en `XAUUSD EMA/ATR/` como **registro histórico completo de los tres marcos** — no se reactiva ningún enfoque sin una decisión explícita nueva del usuario. La disciplina de validación (`hypothesis-gate`, walk-forward anclado, DSR, `factor-independence`, `data-integrity`) queda intacta para cuando se retome investigación, sea cual sea el marco que se decida después.

## Disciplina obligatoria antes de cualquier backtest nuevo (no cambia con el marco, ni durante la pausa)

Cualquier hipótesis nueva pasa primero por `.claude/skills/hypothesis-gate/SKILL.md`: Fase 0 (triage de frecuencia + power analysis, con datos reales, no estimados) antes de escribir código; Fase 1 (frase falsable + regla de corte + folds derivados de la distribución real) antes de tocar el pipeline. No completar los puntos de Fase 1 por cuenta propia si el usuario no los dio explícitamente — frenar y pedirlos. Walk-forward anclado (TRAIN elige parámetros, TEST confirma una sola vez), piso de 30 trades/fold, t-stat con y sin el fold dominante, DSR ≥ 0.95 contando todas las variantes de grilla realmente probadas.
