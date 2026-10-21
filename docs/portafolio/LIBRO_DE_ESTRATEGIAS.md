# Libro de estrategias

Lleva: `jefe-portafolio`. Creado 2026-10-21. Sin dinero real ni órdenes.
Estados: idea · en diseño · registrada · corriendo · descartada · aprobada.

**Hoy no hay ninguna estrategia aprobada.**

## Activas

| ID | Nombre | Estado | Fase hypothesis-gate | Auditorías | Por qué / próximo paso |
|---|---|---|---|---|---|
| PF-001 | Copia en papel de portafolios grandes (13F / ETF / flujos ETF BTC) con retraso real y costos | en diseño | Fase 0 en borrador (`hipotesis/PF-001_Fase0_borrador.md`) | desconfiado: pendiente · jefe-riesgo: pendiente | Aprobada por el usuario 2026-10-21 solo como diseño. Falta: inventario real de `portafolio-replica`, efecto de referencia, y Fase 1 (frase falsable, regla de corte, folds) que da el usuario. No se calculó ningún resultado. |

## Mediciones descriptivas (no son estrategias; registro aparte, no las toca Portafolio)

| ID | Qué | Estado | Dónde |
|---|---|---|---|
| KT-002 | Kronos/TimesFM BTCUSDT prospectivo, horario | corriendo (descriptivo) | `docs/KT-002_registro_prospectivo.md` |
| KT-003 | Kronos/TimesFM BTCUSDT histórico 2017–2026 | registrada (descriptivo, se lanza a mano) | `docs/KT-003_registro_historico.md` |
| KT-004 | Confirmación prospectiva de acierto balanceado | en diseño (v2 vuelve al mejorador por MEDIOS del desconfiado) | `docs/propuestas/KT-004_propuesta.md` |
| KT-005 | Ajuste TimesFM con log-retornos | en diseño (v1 sin auditar) | `docs/propuestas/KT-005_propuesta.md` |

## Descartadas (historial; no se reabren sin razón nueva y decisión del usuario)

| Nombre | Estado | Por qué | Dónde |
|---|---|---|---|
| XAUUSD walk-forward (técnico + macro, diario e intradía) | descartada 2026-08-04 | 0/3 walk-forwards intradía + 0/8 macro diaria; DFII10 insuficiente (DSR 0.37) | `XAUUSD EMA/ATR/Bitácora de decisiones.md` |
| EURUSD walk-forward (carry + momentum) | descartada 2026-08-04 | H1 t=+0.75 (colapsa sin fold fuerte), H2 t=−1.85; H3/H4 caen en triage | `XAUUSD EMA/ATR/Plan de investigación EURUSD.md` |
| EURUSD event study NFP/CPI | descartada 2026-08-05 | Efecto 2–3 pips vs MDE 4.35; falla screen in-sample | `Bitácora de decisiones.md` |
| TF_Basket_H1 (10 instrumentos) | descartada 2026-08-06 en Fase 0 | Donchian 20 t≈−0.04; MA 10/50 t≈0.93, Sharpe implícito 0.229 < 0.3 antes de costos | `XAUUSD EMA/ATR/TF_Basket_H1 — Fase 0.md` |
| Salida 2: Donchian 20 a forward con capital acotado | descartada 2026-08-06 en filtro de implementación | Sharpe neto −0.27, drag de swaps 603.7 % del bruto; nunca se desplegó capital | `Bitácora de decisiones.md` |

## Asignación de riesgo

Sin estrategias aprobadas: nada que asignar. Los límites los fija `jefe-riesgo` (`docs/riesgo/`).
