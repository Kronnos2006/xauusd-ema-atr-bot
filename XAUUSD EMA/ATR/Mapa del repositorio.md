---
tipo: referencia
estado: vigente
actualizado: 2026-10-20
tags: [repositorio, mapa, estructura]
---

# Mapa del repositorio

Índice: [[00 Inicio]] · Uso: [[Guía de uso]]

Qué hay en cada lugar de [Kronnos2006/xauusd-ema-atr-bot](https://github.com/Kronnos2006/xauusd-ema-atr-bot). Los scripts de la raíz **no se mueven** porque las tareas programadas de la PC y los imports usan sus rutas actuales.

## Carpetas

| Carpeta | Contenido |
|---|---|
| `XAUUSD EMA/ATR/` | Esta bóveda de Obsidian: documentación, decisiones e historia |
| `tools/` | Scripts de Kronos/TimesFM: pruebas técnicas, KT-002 (`kt002_prospectivo.py`) y KT-003 (`kt003_historico.py`) |
| `data/kt002/`, `data/kt003/` | Datos y resultados de las mediciones con modelos fundacionales |
| `docs/` | Registros previos (KT-002, KT-003), preparación BTC, propuestas (`propuestas/`), evidencia (`evidencia/`) y coordinación (`coordination/`) |
| `.github/workflows/` | Automatizaciones de GitHub Actions (KT-002, KT-003) |
| `.claude/agents/` | Agentes: desconfiado, mejorador, vigía de datos, strategy-reviewer, infra-guardian |
| `.claude/skills/` | Disciplina reutilizable: hypothesis-gate, data-integrity, factor-independence, infra-ops-playbook, sync-knowledge, strategy-research |
| `research/` | Motor de experimentos reproducibles sobre `Backtest ema v4.py` (Fase 1) |
| `tests/` | Tests de determinismo y de ausencia de fuga del walk-forward |
| `investigacion/` | Fases 2–4 en Python (momentum, Donchian, cross-sectional, carry FX) |
| `estrategias/` | EA ICT/SMC en MQL5 (`0031_v3x0.mq5`) y sus resultados |
| `MQL5/Experts/` | EA visual Donchian20 y bot Python con señal enchufable (feed/broker/estado) |
| `estudios/` | Artículos de referencia (PDF) |

## Raíz: scripts por función

**Motor de backtest XAUUSD (EMA/ATR).** `Backtest ema v4.py` es la fuente de verdad de indicadores, señales y walk-forward. `backtest_ema.py`, `_v2.py` y `_v3.py` son versiones históricas inertes. Ver [[Infraestructura#Evolución de los scripts de backtest]].

**Triage de frecuencia (Fase 0 de hypothesis-gate).** `triage_frecuencia.py` y los `diagnostico_frecuencia_*.py` (DFII10, DXY, momentum DXY D1/H4, momentum XAUUSD H1 y EURUSD D1, ratio oro/plata, risk-off US500 H4, VIX, WTI, crédito GHYG/LQD, índices D1, TF_Basket_H1). También `diagnostico_cointegracion_pares.py`.

**Hipótesis (Fase 1, walk-forward).** `hipotesis_macro_*.py` (2s10s, DFII10, DXY, momentum DXY, ratio oro/plata), `hipotesis_riskoff_us500_h4*.py`, `hipotesis_carry_eurusd.py`, `hipotesis_indices_d1.py`, `event_study_eurusd.py`.

**Auditorías y potencia.** `auditoria_carry_eurusd*.py`, `metricas_dfii10.py`, `mde_trend_following_tf_basket_h1.py`, `calibracion_efecto_tf_basket_h1.py`, `correlacion_basket_tf_h1.py`, `backtest_implementacion_donchian20_salida2.py`.

**Herramientas estadísticas y de datos.** `deflated_sharpe.py` (PSR/DSR), `analizar_independencia_factores.py`, `verificar_integridad_datos.py`, `construir_dxy_sintetico*.py`, `validar_dxy_sintetico.py`, `depth_check_basket_10.py`.

**Loggers en vivo (PC, solo lectura).** `log_senales_demo.py` (EMA M15), `log_senal_macro_dfii10.py` (DFII10) y sus pruebas `log_senales_demo_test_s4u.py`, `test_s4u_conexion_mt5.py`.

**Operación de Task Scheduler (PowerShell).** `_crear_tarea_test_s4u.ps1`, `_configurar_tarea_test_s4u_endurance.ps1`, `_remediar_s4u_logger_*.ps1`, `_remediar_huerfanos_y_desplegar_autorecuperacion.ps1`, `_monitor_holdout_dfii10.ps1`. Ver [[Infraestructura]].

**MQL5 sueltos.** `EventStudyExtractor.mq5`, `MacroCalendarCheck.mq5`, `NFP_CalendarCheck.mq5`.

**Archivos de proyecto.** `CLAUDE.md` y `AGENTS.md` (reglas para Claude y Codex), `README.md`, `requirements.txt`, `registro_checksums.json` (hashes de datos), `Informe_Asesores_Estado_Proyecto.md`, `resultados_backtest.csv` y `resultados_neto_spread.csv` (históricos pre-Fase 1).

## Proyectos hermanos (otros repos)
- `estrategias-clasicas`: Seykota, Darvas, Donchian y Livermore en 15 ETF, con holdout sellado 2022–2026.
- `tsm-volscaling`: Time-Series Momentum con volatility scaling en 8 ETF (Fase 0 cerrada).
