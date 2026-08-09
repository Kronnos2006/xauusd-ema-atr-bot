# Registro de estrategias — 0031 (EA Invenio, EURUSD M5)

## Backtest de referencia de este registro

- **EA**: `0031_v320.mq5` (Strategy Lab, `InpStrategyMode` aísla una estrategia por corrida). Fix de sizing en `0031_v321` (mismo archivo fuente, `#property version "3.21"`): `InpRiskUSD` fijo → `InpRiskPct` (% de equity actual).
- **Símbolo/TF**: EURUSD M5
- **Período**: 2005.01.01 – 2015.01.01 (10 años)
- **Modelo**: Every tick | Depósito: $100 | Calidad histórica: 99%
- **Reportes crudos**: `estrategias/resultados_v320/*.htm` + `*_trades.csv` por estrategia

> Nota: esta tabla reemplaza cualquier veredicto previo basado en el período corto
> (ene–ago 2026, ~7 meses) que pudiera existir en memoria de sesiones anteriores.
> Ese período no se volvió a correr acá — si en algún momento se retoma, comparar
> ambos horizontes explícitamente en vez de asumir que uno invalida al otro.

## Mapeo InpStrategyMode → estrategia (por run)

| Run | InpStrategyMode | Estrategia |
|---|---|---|
| 1 | 1 | Judas |
| 2 | 2 | Venom |
| 3 | 3 | Bernd |
| 4 | 4 | LonClose |
| 5 | 5 | SilverBullet |
| 6 | 6 | CRT |
| 7 | 0 (STRAT_ALL) | Todas combinadas |

## Resultado por estrategia

| Estrategia | Trades | PF | Net Profit | Expectancy/trade | Win Rate | Max DD | Veredicto |
|---|---|---|---|---|---|---|---|
| Judas | 488 | 0.85 | -$47.66 | -$0.10 | 31.8% | 60.0% | **DESCARTADA** |
| Venom | 297 | 0.89 | -$20.91 | -$0.07 | 33.3% | 37.8% | **DESCARTADA** |
| Bernd | 122 | 0.72 | -$24.20 | -$0.20 | 29.5% | 27.2% | **DESCARTADA** |
| LonClose | 0 | — | $0.00 | — | — | — | **DESCARTADA (bug de diseño, no de edge)** |
| SilverBullet | 317 | 0.84 | -$34.40 | -$0.11 | 32.2% | 49.5% | **DESCARTADA** |
| CRT (sizing $ fijo) | 168 | 0.43 | -$94.74 | -$0.56 | 12.5% | 94.7% | muestra truncada por ruina de cuenta en 2005 |
| CRT (sizing % equity, re-test) | 378 | 0.56 | -$75.92 | -$0.20 | 11.1% | 82.0% | **DESCARTADA** (muestra completa 2005–2014, confirma sin edge) |

## Razones de descarte

**Judas, Venom, Bernd, SilverBullet**: PF<1, expectancy negativa, R-multiple promedio negativo, consistente a lo largo de casi todos los años del período, en ambos lados (long/short). Muestra suficiente (122-488 trades) — no es un problema de tamaño de muestra. No hay una hipótesis de mejora razonable identificada (no es un horario específico, no es un solo año outlier, no depende de una sola operación).

**LonClose**: la ventana de entrada (12:30–13:30 UTC) está contenida dentro de la ventana en la que `g_lon_high/g_lon_low` (el nivel de Londres) todavía se está actualizando (08:00–13:30 UTC). El nivel usado para detectar el sweep siempre incluye el high/low de la vela que se está evaluando, por lo que un sweep es estructuralmente imposible. Decisión del usuario (2026-08-07): descartar sin invertir en rediseñar la ventana.

**CRT**: dos hallazgos separados, ambos ya confirmados:
1. Con riesgo fijo ($1/trade sobre $100 de depósito), la cuenta se arruinó en 2005 y quedó sin poder operar los 9 años restantes por margen insuficiente — la muestra de 168 trades no representaba el período completo.
2. Corregido el sizing a % de equity (`InpRiskPct`, ver `0031_v321`), CRT operó los 10 años completos (378 trades, todos los años excepto 2008) y el resultado se mantuvo negativo: PF 0.56, win rate 11.1%, expectancy -$0.20/trade, drawdown 82%. La corrección de sizing descarta la hipótesis de que la ruina temprana estaba ocultando un edge real — no lo estaba.

## Estado del EA

Ninguna de las 6 estrategias sobrevive el filtro inicial en este período de 10 años. `STRAT_ALL` (corrida combinada) no se vuelve a evaluar por separado porque en la corrida original quedó dominada casi por completo por la ruina de CRT (168 de 170 trades eran CRT) — sin ninguna estrategia individual con edge, no hay expectativa de que la combinación lo tenga.

**Próxima decisión pendiente del usuario**: no queda ninguna estrategia en `STRAT_MODE` con evidencia de edge en este horizonte. Antes de escribir código nuevo, definir una hipótesis nueva (con frase falsable + regla de corte) pasa primero por el mismo triage que ya se aplicó acá.

## ⛔ RAMA TIME-SERIES MOMENTUM — CERRADA FORMALMENTE (2026-08-08)

**Conclusión:** H1 (Momentum, 4 valores de N) y H2 (Donchian 20) probados en Python
con datos D1 EURUSD 2005–2019. Ninguna hipótesis sobrevive validación.

H1-N120 fue eliminado por concentración temporal extrema, no por PF bajo:
- PF Validation 1.82 depende de 4 trades en años de 1 sola operación
- 2016 (70% de la muestra): PF 0.38
- Bootstrap CI90%: [0.585, 4.727]

**El Test (2020–2026) no fue ejecutado. Sigue congelado.**

**Demo:** sigue en pausa. No se activa ningún EA sin hipótesis nueva aprobada.

### H1 — Time-Series Momentum en EURUSD D1
**Estado:** ❌ FALSADA

| N | Train PF | Validation PF | Veredicto |
|---|---|---|---|
| 20 | 1.33 | 0.62 | Eliminada — Validation < 1.10 |
| 60 | 1.06 | 0.66 | Eliminada — Validation < 1.10 |
| 120 | 1.67 | 1.82* | Eliminada — PF espurio, sin estabilidad temporal |
| 252 | 0.53 | 0.43 | Eliminada — ambos períodos negativos |

*H1-N120: 23 trades en Validation. Año 2016 (16 trades, 70% de muestra): PF 0.38.
Bootstrap CI90%: [0.585, 4.727]. 18.5% de remuestreos tienen PF ≤ 1.0.

### H2 — Donchian Breakout en EURUSD D1
**Estado:** ❌ FALSADA

| N | Train PF | Validation PF | Veredicto |
|---|---|---|---|
| 20 | 1.27 | 0.79 | Eliminada — Validation < 1.10 |

---

### Regla aplicada
> FASE 2 cerrada. No se agregan filtros para rescatar ninguna hipótesis.
> La próxima hipótesis (H3) requiere una explicación económica o estadística
> concreta antes de codificar nada. Debe presentarse con frase falsable + regla
> de corte para aprobación antes de implementar.

## Roadmap completo

> Nota: esta sección no existía en el archivo antes de este commit — la
> reconstruyo con lo que está confirmado en este registro. Si había más filas
> previstas (Fase 3 ya esbozada, ideas paralelas, etc.) que no quedaron
> documentadas acá, corregir/completar.

```
FASE 1 ✅  6 estrategias ICT/SMC (MQL5, EURUSD M5) — CERRADA. Ninguna sobrevive backtest 10 años (PF<1).
FASE 2 ✅  H1 (Momentum D1) + H2 (Donchian D1) — CERRADA. Ninguna sobrevive validación.
FASE 3 ⏳  Pendiente de definir — requiere explicación económica/estadística nueva antes de codificar (frase falsable + regla de corte).
```
