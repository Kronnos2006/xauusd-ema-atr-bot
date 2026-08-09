# Fase 3 — H3 Cross-Sectional Momentum FX

Proyecto Invenio. Fecha de inicio del experimento: **2026-08-08**.

- Fase 1 (6 estrategias ICT/SMC en MQL5): cerrada. Ninguna con PF > 1.
- Fase 2 (H1 time-series momentum + H2 Donchian en EURUSD D1): cerrada. Ninguna
  hipótesis sobrevive validación.
- Fase 3 (esta fase): H3, momentum cross-sectional en un universo de 9 monedas
  desarrolladas contra USD.

## 1. Hipótesis falsable

> Si existe persistencia relativa en los retornos de monedas desarrolladas
> contra USD, entonces un portfolio mensual que compra las 3 monedas con mayor
> retorno pasado (relativo al USD) y vende las 3 con menor retorno pasado
> debería producir retorno neto positivo, Sharpe > 0.50 y estabilidad temporal
> en el período de Validación (2015–2019), después de costos de transacción
> predefinidos.

## 2. Variantes pre-registradas (independientes, no se optimiza N)

```
H3-20  : lookback 20 días hábiles (≈1 mes)
H3-60  : lookback 60 días hábiles (≈3 meses)
H3-120 : lookback 120 días hábiles (≈6 meses)
```

## 3. Universo y tickers (yfinance)

```
EUR: EURUSD=X (directo)   GBP: GBPUSD=X (directo)
AUD: AUDUSD=X (directo)   NZD: NZDUSD=X (directo)
CHF: USDCHF=X (inverso)   JPY: USDJPY=X (inverso)
CAD: USDCAD=X (inverso)   NOK: USDNOK=X (inverso)
SEK: USDSEK=X (inverso)
```

Descarga 2003-01-01 a 2026-08-08 (buffer de warmup antes de 2005). Cada serie
se cachea en `data/{MONEDA}_d1.csv` (Date, Open, High, Low, Close).

### Decisión de datos — AUD (confirmada por el usuario, 2026-08-08)

`AUDUSD=X` en yfinance no tiene ningún dato antes de **2006-05-16** — un hueco
contiguo de 16 meses justo al arranque de Train, no capturado por el chequeo
agregado de "% de días faltantes en 2005-2019" (da 9.4%, bajo el umbral del
10%, porque el hueco no está disperso sino concentrado al inicio). Los otros
8 pares arrancan en 2003 sin este problema (peor hueco real dentro de
2005-2019: 26 días, EUR/JPY/NOK/SEK, todos el 2008-08-26 — un evento puntual
del proveedor, no un patrón).

**Decisión**: se mantiene el universo de 9 monedas. AUD queda excluida del
ranking en cualquier mes en que no tenga N días hábiles reales de historia
para esa variante (N=20 → elegible desde ~jun-2006, N=60 → ~ago-2006, N=120 →
~nov-2006). Nunca se imputa ni se fabrica un retorno para AUD en ese tramo —
`rank_and_signal_frame()` en `utils_fase3.py` simplemente la excluye ese mes
(bucket "middle" queda con 2 en vez de 3 monedas mientras dure la exclusión).
Se ve reflejado en `resultados/train/auditoria_rebalanceos_H3_N*.csv`
(columna `ret_lookback_usd` vacía para AUD en los primeros rebalanceos).

NOK y SEK, que el prompt original anticipaba como posible problema, resultaron
con la mejor cobertura del grupo (0.72% de faltantes en 2005-2019).

## 4. Convención de retorno

```
Pares directos (EUR, GBP, AUD, NZD):
    Return_moneda_t = Close_t / Close_{t-1} - 1

Pares inversos (CHF, JPY, CAD, NOK, SEK):
    Return_moneda_t = -(Close_t / Close_{t-1} - 1)
```

El retorno acumulado del lookback se calcula componiendo los retornos DIARIOS
ya con el signo ajustado — `Product(1 + r_t) - 1` sobre las últimas N
observaciones reales de esa moneda — no como un atajo vía razón de precios
sobre `1/Close`. Ambos enfoques son casi idénticos numéricamente pero no
son matemáticamente equivalentes; se implementó literalmente la fórmula de
composición diaria pedida.

## 5. Ranking y construcción del portfolio

Al cierre de cada último día hábil del mes (rebalanceo):
1. Retorno acumulado de N días por moneda (solo monedas con N observaciones
   reales — ver sección AUD arriba).
2. Ranking de mayor a menor.
3. Top 3 → LONG (+1), bottom 3 → SHORT (-1), resto → flat (0).
4. Peso igual: cada posición activa = 1/6 del portfolio (long 3×1/6=+0.5,
   short 3×1/6=-0.5, dollar-neutral aproximado).

**Timing sin lookahead**: la señal usa precios de cierre hasta e incluyendo el
día de rebalanceo t. La nueva composición **no genera retorno el día t** — el
primer retorno con la nueva composición es t+1 (próximo día hábil). El costo
de la transición se registra y resta en el día t (mismo día que se decide el
cambio), aunque la posición vieja es la que sigue generando retorno ese día.
Implementado en `utils_fase3.build_position_held()` (shift(1)+ffill sobre las
9 columnas, mismo patrón que Fase 2).

## 6. Costos

```
Majors (2 pips/lado): EUR, GBP, JPY, CHF, AUD, CAD
Minors (4 pips/lado): NZD, NOK, SEK

cost_pct_per_side[moneda] = pips_per_side[moneda] * pip_size[moneda] / close_price[moneda]
pip_size: 0.0001 para todos excepto JPY (0.01)
```

Lados pagados por transición: 0→±1 o ±1→0 = 1 lado; +1↔-1 = 2 lados;
sin cambio = 0. `costo_portfolio_día = Σ(lados_i × cost_pct_per_side_i × 1/6)`.

## 7. Split (no se toca)

```
Train      : 2005-01-01 — 2014-12-31
Validation : 2015-01-01 — 2019-12-31
Test       : 2020-01-01 — 2026-08-08   ← CONGELADO, no se ejecuta
```

`utils_fase3.DEV_CUTOFF = "2019-12-31"` — `load_dev_data()` nunca carga filas
posteriores a esa fecha.

## 8. Criterios de supervivencia en Validation (los 4, todos obligatorios)

```
A. Sharpe anualizado > 0.50
B. Retorno acumulado neto > 0
C. Al menos 3 de los 5 años de Validation con retorno neto positivo
D. max(abs(R_2015..R_2019)) / sum(abs(R_i)) ≤ 0.50   (concentración temporal)
```

Max Drawdown se reporta siempre pero no elimina en esta fase. Train se reporta
con las mismas métricas pero sin veredicto de supervivencia (el gate es solo
sobre Validation).

## 9. Qué NO hace el script

- No corre el período de Test bajo ninguna circunstancia.
- No agrega filtros (EMA, ATR, carry, VIX) para mejorar resultados.
- No cambia N, número de winners/losers, ni frecuencia de rebalanceo después
  de ver resultados.
- No combina H3-20/60/120 en un solo resultado.
- No elige el mejor N y lo presenta como "H3 funciona".
- No imputa datos faltantes silenciosamente — ver decisión de AUD arriba.
- No cambia el modelo de costos después de ver resultados.

## 10. Resultado — Validation (2026-08-08)

| Variante | Sharpe | Ret. neto | Años positivos | Concentración D | Veredicto |
|---|---|---|---|---|---|
| H3-20 | -0.09 | -1.72% | 3/5 | 0.35 | ELIMINADA |
| H3-60 | -0.86 | -14.69% | 1/5 | 0.39 | ELIMINADA |
| H3-120 | -0.27 | -4.85% | 2/5 | 0.27 | ELIMINADA |

Las 3 variantes fallan el criterio A (Sharpe > 0.50) y B (retorno neto > 0)
en Validation. El Test (2020-2026) no fue ejecutado — permanece congelado.

## Cómo correr

```bash
cd investigacion/fase3
python h3_momentum_cs.py
```

`resumen.csv` (uno por período) se reescribe reemplazando solo la fila de
cada variante — no duplica filas si se corre de nuevo.
