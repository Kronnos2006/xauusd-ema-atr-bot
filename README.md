# Investigación cuantitativa con validación estadística honesta

Proyecto personal de investigación sistemática de trading algorítmico (XAUUSD, EURUSD, ETF y BTC) en Python y MQL5. Su objetivo es responder con rigor si existe una ventaja operable **antes** de arriesgar capital. Para eso, cada hipótesis se pre-registra, se valida fuera de muestra y se audita de forma independiente.

> **El proyecto no ejecuta órdenes ni usa capital real.** Todo es investigación y medición.

## Estado (2026-10-20)

| Línea | Estado | Resultado |
|---|---|---|
| XAUUSD técnico y macro (EMA/ATR, DFII10, DXY, 2s10s, ratio oro/plata, risk-off) | Cerrado | Sin edge que sobreviva walk-forward, fold dominante y DSR |
| EURUSD (carry, momentum, risk-off, event study NFP/CPI) | Cerrado | Sin significancia fuera de muestra |
| TF_Basket_H1 (trend following, 10 instrumentos) | Cerrado en Fase 0 | Sin efecto suficiente antes de costos |
| **KT-003** — Kronos/TimesFM en BTC 2017–2026 (diagnóstico) | Terminado y auditado | Kronos 56,8 % vs 50,9 % «siempre sube» tras el corte; **no significativo con Holm** (p 0,086). Movimientos previstos menores que los costos |
| **KT-002** — Kronos/TimesFM en BTC, prospectivo | **Activo** (cada hora) | Acumulando datos; útil en semanas |

Para hipótesis y estrategias sigue la **pausa activa**: no se abre ninguna sin una decisión explícita del usuario.

## Cómo se trabaja

- **Registro previo:** la hipótesis, la métrica, la regla de aprobado y los datos se escriben y commitean antes de ver resultados. Los cambios posteriores se documentan como enmiendas.
- **Fuera de muestra:** walk-forward anclado (TRAIN elige, TEST confirma una vez), holdouts sellados con SHA-256 y mediciones prospectivas.
- **Pruebas múltiples:** Deflated Sharpe Ratio y corrección de Holm, contando todas las variantes realmente probadas.
- **Potencia:** triage de frecuencia y MDE antes de escribir un backtest (`hypothesis-gate`).
- **Auditoría independiente:** un agente auditor (`desconfiado`) revisa cada diseño y cada resultado, y pide ejecuciones concretas hasta despejar las dudas.

## Documentación

Toda la documentación vive en la bóveda de Obsidian **`XAUUSD EMA/ATR/`**. Para abrirla, en Obsidian elegí *Open folder as vault* y seleccioná esa carpeta. Desde ahí:

- **`00 Inicio.md`** — punto de entrada.
- **`Guía de uso.md`** — cómo ver resultados, lanzar o detener procesos, proponer mejoras y leer un resultado sin engañarse.
- **`Mapa del repositorio.md`** — qué es cada archivo y carpeta.
- **`Bitácora de decisiones.md`** y **`Cronología.md`** — historia completa.

Los registros previos de las mediciones con modelos fundacionales están en `docs/` (`KT-002_registro_prospectivo.md`, `KT-003_registro_historico.md`).

## Estructura

```
XAUUSD EMA/ATR/       Bóveda de Obsidian (documentación)
tools/                Kronos/TimesFM: pruebas técnicas, KT-002, KT-003
data/kt002, kt003/    Datos y resultados de las mediciones
docs/                 Registros previos, propuestas, evidencia, coordinación
.github/workflows/    GitHub Actions (KT-002 horario, KT-003 a demanda)
.claude/agents/       Agentes: desconfiado, mejorador, vigia-datos, ...
.claude/skills/       Disciplina: hypothesis-gate, data-integrity, ...
research/, tests/     Motor de experimentos reproducibles y sus tests
investigacion/        Fases 2–4 (momentum, Donchian, carry FX)
estrategias/, MQL5/   Expert Advisors y bot modular
*.py, *.ps1 (raíz)    Backtests, triage, hipótesis, loggers y operación de la PC
```

Los scripts de la raíz no se mueven porque las tareas programadas de Windows y los imports dependen de sus rutas.

## Uso rápido

```bash
# Entorno local (backtests XAUUSD/EURUSD con MT5)
pip install -r requirements.txt
python -m unittest discover tests
python -m research.engine --config research/config.example.yaml
```

- **KT-002:** corre solo en GitHub Actions; resultados en `data/kt002/resumen.md` y en el panel en vivo.
- **KT-003:** se lanza editando `data/kt003/lanzar.txt` (`prueba` o `completo`) en `master`.
- **Mejoras a los modelos:** el mejorador propone, el desconfiado audita y el usuario decide. Ver la guía de uso.

## Coordinación entre asistentes

Claude y Codex trabajan sobre este repo con reglas compartidas (`CLAUDE.md`, `AGENTS.md`). El registro de quién hizo qué, con autor y revisor, está en `docs/coordination/CONTEXTO_COMPARTIDO.md`.

---
*Proyecto de investigación y validación únicamente. Nada de este repositorio es una recomendación de inversión.*
