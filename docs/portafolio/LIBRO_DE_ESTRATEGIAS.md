# Libro de estrategias

Lleva: `jefe-portafolio`. Creado 2026-10-21. Sin dinero real ni órdenes.
Estados: idea · en diseño · registrada · corriendo · descartada · aprobada. ("en auditoría" = en diseño con auditoría del desconfiado en curso.)

**Hoy no hay ninguna estrategia aprobada.**

## Activas

| ID | Nombre | Estado | Fase hypothesis-gate | Auditorías | Por qué / próximo paso |
|---|---|---|---|---|---|
| PF-001 | Copia en papel de portafolios grandes (13F / N-PORT / ETF / flujos ETF BTC) con retraso real y costos. **Paraguas**: sus variantes concretas son HP-001 (pata 13F) y HP-002 (pata flujos ETF BTC) | en auditoría — triage propone descarte | Fase 0 en borrador (`hipotesis/PF-001_Fase0_borrador.md`); inventario entregado (`INVENTARIO_DATOS.md`, parcial: SEC/emisores 403 desde el proxy) | desconfiado: pendiente · jefe-riesgo: pendiente | Aprobada por el usuario 2026-10-21 solo como diseño. Ninguna pata alcanza potencia: 13F MDE 0,78 (HP-001), N-PORT 1,10 (~6,5 años, sin verificar primera mano), ETF diario sin historia (solo prospectivo), flujos BTC 1,68 (HP-002). Si el desconfiado confirma HP-001 y HP-002, PF-001 se cierra como "descartada en Fase 0" sin tocar datos. 0 resultados calculados. |
| HP-001 | "Best ideas" de gestores grandes vía 13F, con FILING_DATE real (pata 13F de PF-001) | en auditoría — triage propone descarte | Fase 0 escrita (`hipotesis/HP-001_Fase0.md`): MDE 0,78 (13 años XML) vs IR de literatura ajustado 0,15–0,40; 54–307 años necesarios | desconfiado: en curso · jefe-riesgo: no aplica mientras no avance | Autor `portafolio-investigador`, revisó `jefe-portafolio` 2026-10-21 (cuentas verificadas, coherente con PF-001). 0 variantes probadas. Fase 1 no se completa si se confirma el descarte. Pendiente si avanzara: conteo de fondos (requiere acceso a sec.gov) y costos de acciones EE. UU. |
| HP-002 | Flujos de ETF spot BTC como presión de precio (pata flujos BTC de PF-001) | en auditoría — triage propone descarte | Fase 0 escrita (`hipotesis/HP-002_Fase0.md`): MDE 1,68 (696 días, 2,77 años) vs IR ajustado ~0,35; 64–196 años necesarios; costos BTC 0,30 % ida y vuelta | desconfiado: en curso · jefe-riesgo: no aplica mientras no avance | Autor `portafolio-investigador`, revisó `jefe-portafolio` 2026-10-21 (cuentas verificadas). 0 variantes probadas. No toca KT-002/KT-003. Única salida: medición descriptiva prospectiva, que sería un registro nuevo y decisión aparte. |

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
