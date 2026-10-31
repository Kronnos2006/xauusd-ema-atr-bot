# ESTADO — leer esto primero (único archivo de arranque)

**Para cualquier IA (Claude, ChatGPT, Codex):** este archivo reemplaza leer `CLAUDE.md`, `docs/gerencia/`, `docs/coordination/` y las bitácoras al empezar. Abrí otro documento **solo si la tarea lo pide**. Así se gasta lo mínimo en tokens.
Al terminar una tarea, actualizá la sección **«Qué estamos haciendo»** con una línea (fecha, quién, qué, PR/commit). La parte automática la escribe un script; no la edites.

Dueño: Kronnos (Kronnos2006). Hora local: Costa Rica (UTC−6).

## Reglas que no cambian
1. **Sin dinero real ni órdenes.** No hay estrategia aprobada.
2. **No tocar** KT-002 (`tools/kt002_prospectivo.py`, `kt002.yml`, `data/kt002/`), holdouts sellados ni experimentos en curso.
3. **Nunca cancelar, reiniciar ni relanzar** corridas de GitHub Actions. Solo la guardia relanza KT-002.
4. Toda idea nueva pasa por `hypothesis-gate` (Fase 0 → Fase 1 → walk-forward, ≥30 ops/fold, DSR ≥ 0,95).
5. **Scripts primero, IA solo para analizar** (`docs/POLITICA_SCRIPTS_PRIMERO_2026-10-28.md`). Lo repetitivo (vigilar, contar, informar) lo hace un script en GitHub Actions con 0 llamadas a IA.
6. Cambios a workflows o código: rama + PR; integra el dueño.
7. Decide solo el dueño: dinero, holdouts, borrar datos, cambiar reglas o un experimento en curso.

## Qué estamos haciendo (manual, 1 línea por cambio, lo más nuevo arriba)
- **2026-10-31 · Claude:** **KT-004 NO PASA** (run 41116143211, recalculado desde el CSV). Kronos/ETH 52,06 % vs «siempre sube» 50,3 %: +1,71 pts, McNemar 1 cola p = 0,067 (regla: p < 0,05 y ≥ 2 pts). Secundarios Holm: ninguno < 0,05. Sin señal de memoria (52,1 % antes vs 52,0 % después de 2025-10). Para cubrir 0,20 % de costos haría falta ≈ 60 %. El holdout 2026-08→10 queda cerrado. Kronos a 4 h descartado como predictor de dirección en cripto, salvo una enmienda nueva.
- **2026-10-30 · Claude:** PR #76 (informe sin IA verifica KT-002 desde `predicciones.csv`; quita el falso P0) y PR #77 (KT-004 Enmienda A + código; no corre hasta aprobar). #75 (pre-registro KT-004 y plan secuencial KT-002) ya en master.
- **Mandato propuesto (lo confirma el dueño al integrar este PR):** Claude = investigación y metodología (KT-004, plan secuencial, scripts de análisis). ChatGPT = coordinación e infraestructura (workflows, ORION, ATLAS). Sin solapes; cada uno revisa al otro. Revoca en forma acotada la política del 27-oct.
- **2026-10-30 · Claude:** creado este archivo + `tools/generar_estado.py` + `estado.yml` (se actualiza solo cada día). Tareas programadas de Claude (gerente diario 06:30 y vigía cada 4 h) **siguen activas, pendiente de que el dueño confirme apagarlas**: su parte mecánica ya la hacen la guardia, `informe-gerencia-sin-ia.yml` y este script.
- **2026-10-29 · ChatGPT:** PR #61–#72 fusionados: Qlib (instalado), FreqAI (entrenamiento LightGBM con velas reales de Binance Vision), combinador de predicciones a pesos iguales (#67), informe gerencial sin IA con Kronnos + ORION + ATLAS (#65, #66).
- **2026-10-27 · Dueño:** política «retiro operativo de Claude» (`docs/coordination/POLITICA_OPERATIVA_SIN_CLAUDE_2026-10-27.md`). El 30-oct el dueño volvió a pedir a Claude que trabaje: **las dos IA pueden trabajar**, coordinando por este archivo y PR.

## Frentes y pendientes (prioridad)
| # | Frente | Estado | Siguiente paso |
|---|---|---|---|
| 1 | **KT-002** (Kronos, TimesFM, KT-001 vs «siempre sube», BTC 4 h) | Corriendo cada hora desde 2026-10-20 | Solo dejar acumular. Hacen falta ~100 sin solape para una idea y ~780 para distinguir 55 % de 50 % |
| 2 | Informe sin IA ↔ KT-002 | Integrado (#76) | — |
| 2b | **KT-004** (ETH/SOL/BNB/XRP, 2024-08→2026-07, primario Kronos/ETH) | **Terminado: NO PASA** (+1,71 pts, p = 0,067) | Cerrado. Holdout sin abrir |
| 2c | Plan secuencial KT-002 (200/400/600/780, O'Brien-Fleming) | En master | Script de cortes después |
| 3 | Combinador (#67) y FreqAI | Código integrado, sin predicciones reales medidas | Alimentar con predicciones reales y medir **contra «siempre sube»**; registrar el protocolo antes de ver resultados |
| 4 | ATLAS PR #42 (H3 DSR, H4 custodia) | Borrador, bloqueado | No fusionar hasta cerrar H3/H4 (`docs/coordination/ESTADO_CANONICO_ORION_ATLAS.md`) |
| 5 | Qlib, NautilusTrader, LEAN | Instalados o pendientes | **No agregar más herramientas** hasta que una muestre que mejora algo |
| 6 | Otros repos: `estrategias-clasicas` (Enmienda 01), `tsm-volscaling` (Fase 0 cerrada, Fase 1 sin empezar) | En pausa | Retomar solo si el dueño lo pide |

## Qué hace cada cosa (automático vs IA)
- **Script / Actions, 0 IA:** `kt002.yml` (predicciones cada hora), `guardia.yml` (salud de KT-002, velas y spread, abre aviso si falla), `informe-gerencia-sin-ia.yml` (informe diario 06:30), `estado.yml` (este archivo).
- **IA, solo a pedido del dueño:** analizar resultados, revisar métodos, auditar (rol `desconfiado`), redactar pre-registros. Los roles siguen en `.claude/agents/` pero **no corren solos**.

## Estado automático
<!-- AUTO:INICIO (lo escribe tools/generar_estado.py; no editar a mano) -->
_Generado 2026-10-30 18:45 UTC · 0 llamadas a IA_

### KT-002 (BTC, dirección a 4 h, prospectivo)
- Pronósticos: 234 · vencidos: 230 · horas omitidas: 11 · actualizado: 2026-10-30T18:07 UTC
- Último registro: 2026-10-30T18:07 UTC (hace 0.6 h)
- **Sin solape (lo que cuenta), n = 57:**
  - Siempre sube (referencia): 26/57 = 45.6 %
  - Kronos: 28/57 = 49.1 % (IC95 36.6 %–61.7 %; p vs sube = 0.8601)
  - TimesFM: 26/57 = 45.6 % (IC95 33.4 %–58.4 %; p vs sube = 1.0)
  - KT-001 50/50: 25/57 = 43.9 % (IC95 31.8 %–56.7 %; p vs sube = 1.0)
- Veredicto automático: ningún modelo supera a «siempre sube». Sin ventaja demostrada.

### GitHub Actions y PR
- kt002.yml: 7/9 verdes en las últimas 10 · última cancelled 2026-10-30T13:07
- guardia.yml: 9/10 verdes en las últimas 10 · última success 2026-10-30T18:07
- informe-gerencia-sin-ia.yml: 3/3 verdes en las últimas 10 · última success 2026-10-30T18:08
- kronnos-ensemble.yml: 2/2 verdes en las últimas 10 · última success 2026-10-30T00:39
- PR abiertos: #42 (borrador) ATLAS: barreras estadísticas DSR, ≥30 operaciones y sello re
- Avisos «guardia» abiertos: 0

### Últimos cambios no rutinarios
- 2026-10-30 · Claude · Gerente 2026-10-30: informe del analista, seguimiento ORION y decisiones
- 2026-10-29 · Kronnos2006 · Merge pull request #72 from Kronnos2006/feature/kronnos-freqai-real-binance-vision-2026102
- 2026-10-29 · Kronnos2006 · ci(Kronnos): train native FreqAI on checksum verified Binance historical data
- 2026-10-29 · Kronnos2006 · feat(Kronnos): native FreqAI model evaluate on historical Binance CSV
- 2026-10-29 · Kronnos2006 · feat(Kronnos): fetch Binance Vision public historical BTC 1h checksum verified
- 2026-10-29 · Kronnos2006 · Merge pull request #71 from Kronnos2006/feature/kronnos-freqai-native-fit-20261029
- 2026-10-29 · Kronnos2006 · fix(Kronnos): serialize numpy hit count to int
- 2026-10-29 · Kronnos2006 · ci: execute native FreqAI fit smoke test
<!-- AUTO:FIN -->
