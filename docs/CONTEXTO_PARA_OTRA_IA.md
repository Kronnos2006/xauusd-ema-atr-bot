# Contexto completo del proyecto (para ChatGPT u otra IA)

Actualizado: 2026-10-22. Dueño: Kensy (Costa Rica, UTC−6). Repositorio público: https://github.com/Kronnos2006/xauusd-ema-atr-bot · Visor: https://kronnos2006.github.io/xauusd-ema-atr-bot/visor/

## 1. Qué es
Proyecto personal de **investigación cuantitativa de trading** con rigor estadístico. Objetivo final: encontrar una ventaja real y operable antes de arriesgar dinero. **Reglas de fondo: sin órdenes ni capital real; toda hipótesis se registra antes de ver datos; un auditor independiente revisa todo.**

## 2. Historia
- 2026-07/08: marcos sobre XAUUSD (técnico, macro, intradía), EURUSD (carry, momentum, event study NFP/CPI) y un basket de trend following → **todos cerrados sin ventaja** que sobreviva walk-forward y costos.
- Un intento de forward test con $20 reales (Donchian 20) se canceló en su propio filtro de costos (Sharpe neto −0,27). **Nunca se usó capital real.**
- Desde 2026-10-16: modelos fundacionales de series temporales sobre **BTCUSDT**.

## 3. Mediciones activas (BTC)
- **Modelos:** Kronos-small y TimesFM 2.5 (versiones fijadas) y su combinación 50/50 (KT-001). Predicen la dirección de BTC a 4 h.
- **KT-002 (prospectivo, en vivo):** GitHub Actions cada hora (`.github/workflows/kt002.yml`) → `data/kt002/`. Cuenta solo una predicción cada 4 h ("sin solape"). Al 2026-10-22: 37 predicciones; sin solape n=7: siempre sube 4, Kronos 3, TimesFM 2, KT-001 1. **Sin valor estadístico aún** (hacen falta ~100 para una idea y ~780 para distinguir 55 % de 50 %).
- **KT-003 (histórico 2017–2026, terminado):** 2 928 días. Post corte jul-2024 (n=842): Kronos 56,8 %, TimesFM 48,7 %, KT-001 55,5 %, siempre sube 50,9 %. McNemar con Holm: **no significativo** (Kronos p=0,086). La historia BTC ya está expuesta: confirmar solo con datos posteriores al 2026-10-20.
- **Costos:** comisión Binance 0,10 % por lado; spread medido ≈ 1 centavo (`data/mercado/spread_btcusdt.csv`). Ida y vuelta ≈ 0,20 % (el marco de riesgo usa 0,30 % por prudencia). A 24 h hace falta ~60 % de acierto para empatar.

## 4. Hipótesis descartadas (2026-10-21)
HP-001 (copiar "mejores ideas" de 13F), HP-002 (flujos de ETF de BTC), HP-003 (efecto de apertura de mercados), HP-007 (día de la semana): sin potencia estadística o los costos superan la ganancia posible. HP-006 (volatilidad en anuncios FOMC/CPI, solo medir) en revisión. Detalle: `docs/portafolio/`.

## 5. Organización (agentes de Claude, archivos en `.claude/agents/`)
Dueño → **Gerente** (decide lo operativo, informe diario 6:30 a. m.) → jefes:
- Investigación (mejorador), **Auditoría (desconfiado, independiente)**, **Analista de mercado (independiente;** ayudantes tendencia, macro, ballenas**)**, Datos (vigía), Operaciones, **Riesgo (independiente,** + costos**)**, Portafolio (+ réplica, investigador, estratega), Desarrollo (+ diseñador, programador, integrador, reparador), Documentación, Innovación (+ noticias), Recursos de IA (catálogo de ayudantes), Disciplina.
- Cada jefe contrata sus ayudantes (`docs/gerencia/CONTRATACION.md`). Lista viva: `docs/gerencia/equipo.json`.
- Hipótesis que el desconfiado y el gerente descartan → descarte automático. Solo las que pasan van al dueño.
- **Decide solo el dueño:** dinero real u órdenes, holdouts, borrar datos, cambiar un experimento en curso, cambiar reglas, vetos en disputa.

## 6. Automatización
- GitHub Actions: KT-002 (cada hora), **guardia** (`guardia.yml`: revisa KT-002, relanza, guarda velas y régimen de BTC en `data/mercado/`, mide spread), KT-003 (manual).
- Tareas programadas de Claude: informe diario del gerente, vigía de respaldo cada 4 h.
- Paneles: Oficina del dueño (privada en Claude: órdenes, decisiones, informes) y visor público (enlace arriba).
- Conectores: CoinMarketCap, Crypto.com, TinyFish. Coordinación con Codex: `docs/coordination/CONTEXTO_COMPARTIDO.md`.

## 7. Método (no negociable)
`hypothesis-gate`: Fase 0 (frecuencia y potencia con datos reales) → Fase 1 (frase falsable, regla de corte, folds; la define el dueño) → walk-forward anclado (TRAIN elige, TEST confirma una vez), mínimo 30 operaciones por fold, t con y sin el fold dominante, DSR ≥ 0,95 contando todas las variantes probadas, costos incluidos.

## 8. Archivos clave
`CLAUDE.md` (reglas), `docs/gerencia/` (estructura, decisiones, informe diario, propuesta de organización), `docs/KT-002_registro_prospectivo.md`, `docs/KT-003_registro_historico.md`, `docs/riesgo/MARCO_DE_RIESGO.md`, `docs/portafolio/LIBRO_DE_ESTRATEGIAS.md`, `docs/analisis/` (informes diarios del analista), bóveda Obsidian en `XAUUSD EMA/ATR/`.

## 9. Cómo ayudar
Proponer ideas o revisar métodos respetando las reglas: nada de dinero real; toda idea nueva con registro previo y potencia estadística; no repetir marcos cerrados sin decir qué cambia.
