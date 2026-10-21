# Libro de estrategias

Lleva: `jefe-portafolio`. Creado 2026-10-21. Sin dinero real ni órdenes.
Estados: idea · en diseño · registrada · corriendo · descartada · aprobada. ("en auditoría" = en diseño con auditoría del desconfiado en curso.)

**Hoy no hay ninguna estrategia aprobada.** Última revisión semanal: 2026-10-21 (miércoles).

## Activas

| ID | Nombre | Estado | Fase hypothesis-gate | Auditorías | Por qué / próximo paso |
|---|---|---|---|---|---|
| HP-003 | "En la apertura de los mercados es más fácil predecir": estrategia alcista y estrategia bajista (encargo de Kensy, 2026-10-21) | idea → Fase 0 escrita, triage propone descarte | Fase 0 (`hipotesis/HP-003_Fase0.md`): bajista 7,8–44,7 años necesarios; alcista 2,6 (efecto sin ajustar) a 14,9 años (ajustado); BTC: costo 0,30 % vs ganancia bruta ~0,01–0,03 %; sin datos intradía de índices en el repo | desconfiado: pendiente · jefe-riesgo: no aplica mientras no avance | Autor `jefe-portafolio`. 0 variantes, 0 resultados. Fase 1 NO iniciada: espera las definiciones de Kensy (lista en sección 7 del documento) o su aceptación del descarte. |
| ES-001 | BTC spot largo en régimen ALCISTA (filtro del analista, diario) | **borrador** | Previa a Fase 1; depende de HP-003 (propone descarte) | desconfiado: no enviado · jefe-riesgo: no enviado | `estrategias/ES-001.md`. Autor `portafolio-estratega`, 2026-10-21. No simulable sin registro previo, Fase 1 de Kensy, desconfiado y OK de riesgo. 0 resultados. Riesgo: piso de 30 ops/fold probablemente inalcanzable |
| ES-002 | BTC spot en régimen BAJISTA: fuera / reducir exposición (superposición sobre ES-001) | **borrador** | Previa a Fase 1; depende de HP-003 (pata bajista, 7,8–44,7 años) | desconfiado: no enviado · jefe-riesgo: no enviado | `estrategias/ES-002.md`. Sin cortos (requerirían decisión del usuario y cambio del marco). 0 resultados |

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
| PF-001 Copia en papel de portafolios grandes (paraguas) | descartada 2026-10-21 en Fase 0, aceptado por Kensy | Ninguna pata alcanza potencia (13F MDE 0,78; N-PORT 1,10; flujos BTC 1,68; ETF diario sin historia). 0 resultados calculados | `hipotesis/PF-001_Fase0_borrador.md`, `INVENTARIO_DATOS.md` |
| HP-001 "Best ideas" 13F con FILING_DATE | descartada 2026-10-21 en Fase 0, aceptado por Kensy | MDE IR 0,78 vs efecto ajustado 0,15–0,40; 54–307 años necesarios | `hipotesis/HP-001_Fase0.md` |
| HP-002 Flujos de ETF spot BTC | descartada 2026-10-21 en Fase 0, aceptado por Kensy | MDE IR 1,68 vs ~0,35; 64–196 años; costos 0,30 %. Solo queda, si se quiere, una medición descriptiva prospectiva (registro aparte) | `hipotesis/HP-002_Fase0.md` |
| XAUUSD walk-forward (técnico + macro, diario e intradía) | descartada 2026-08-04 | 0/3 walk-forwards intradía + 0/8 macro diaria; DFII10 insuficiente (DSR 0.37) | `XAUUSD EMA/ATR/Bitácora de decisiones.md` |
| EURUSD walk-forward (carry + momentum) | descartada 2026-08-04 | H1 t=+0.75 (colapsa sin fold fuerte), H2 t=−1.85; H3/H4 caen en triage | `XAUUSD EMA/ATR/Plan de investigación EURUSD.md` |
| EURUSD event study NFP/CPI | descartada 2026-08-05 | Efecto 2–3 pips vs MDE 4.35; falla screen in-sample | `Bitácora de decisiones.md` |
| TF_Basket_H1 (10 instrumentos) | descartada 2026-08-06 en Fase 0 | Donchian 20 t≈−0.04; MA 10/50 t≈0.93, Sharpe implícito 0.229 < 0.3 antes de costos | `XAUUSD EMA/ATR/TF_Basket_H1 — Fase 0.md` |
| Salida 2: Donchian 20 a forward con capital acotado | descartada 2026-08-06 en filtro de implementación | Sharpe neto −0.27, drag de swaps 603.7 % del bruto; nunca se desplegó capital | `Bitácora de decisiones.md` |

## Asignación de riesgo

Sin estrategias aprobadas: nada que asignar. Los límites los fija `jefe-riesgo` (`docs/riesgo/`).
