# Fase 2 — H1 (Time-Series Momentum) + H2 (Donchian Breakout)

Proyecto Invenio. La Fase 1 (6 estrategias ICT/SMC en MQL5, backtest 10 años,
`estrategias/outputs/estrategias_registro.md`) cerró con las 6 estrategias
descartadas (PF < 1). Esta fase prueba dos hipótesis de momentum/breakout,
en Python, sobre EURUSD D1.

## Regla no negociable: el período de Test está congelado

```
Train      : 2005-01-01 — 2014-12-31
Validation : 2015-01-01 — 2019-12-31
Test       : 2020-01-01 — 2026-08-08   ← NO se corre hasta decisión final
```

`utils.load_dev_data()` corta los datos en 2019-12-31 — el período de Test
no se carga en memoria durante el desarrollo, no es solo una convención que
haya que recordar respetar. Solo se habilita cuando H1 o H2 sobrevivan
Validation y el usuario decida explícitamente gastar el único intento sobre
Test.

## Datos

- Fuente: `historial/eurusd_d1.csv` (datos reales MT5, 2000-01-03 en
  adelante), congelados en una copia local en `data/eurusd_d1.csv` la primera
  vez que corre cualquiera de los dos scripts. Si ese archivo no existe, cae a
  `yfinance` (`EURUSD=X`) como fallback.
- El warm-up de los lookbacks (hasta 252 días para H1) usa datos anteriores a
  2005-01-01 cuando están disponibles (2000-2004), en vez de arrancar Train
  con casi un año sin señal por falta de historia. Esto no es look-ahead:
  toda la información usada es estrictamente anterior a cada barra.
- `_check_gaps()` avisa si hay huecos > 5 días de calendario en la serie
  (no bloquea la corrida, solo informa).

## Costos

```
Spread + slippage : 1.5 pips por lado = 0.00015
Round trip         : 0.0003
```

Se aplican como ajuste adverso al precio efectivo de entrada y de salida de
cada trade (`entry_eff`/`exit_eff` en `utils._extract_trades`), y también
como resta de retorno en los días de flip para el cálculo diario del equity
(aproximación en espacio de retorno, despreciable frente al 0.03% de costo).

## Sizing — nota importante sobre una ambigüedad de la especificación

H1 y H2 no definen un stop-loss (la única salida es señal opuesta), así que
"riesgo fijo: 1% de equity por trade" no puede interpretarse como distancia a
un stop (no hay stop). Se interpretó como **notional expuesto = 1% de equity**
por trade: `retorno_equity_diario = 0.01 * retorno_neto_del_precio`.

Esto afecta directamente la magnitud de **Max Drawdown %** y **Retorno
total %** — con un factor de exposición distinto, ambos escalan
proporcionalmente. **No afecta** Profit Factor, Win Rate, expectancy (pips y
%) ni Sharpe anualizado (Sharpe = media/desvío, el factor de escala se
cancela). Si esta interpretación no es la que se quería, es el único punto
del script que habría que ajustar — está aislado en `RISK_FRACTION` en
`utils.py`.

## H1 — Time-Series Momentum

Para cada N en [20, 60, 120, 252] (hipótesis independientes, **nunca** se
elige el mejor N para declarar "H1 funciona"):

```
r_t = Close[t] / Close[t-N] - 1
r_t > 0  -> LONG al Open de t+1
r_t < 0  -> SHORT al Open de t+1
r_t == 0 (o sin historia suficiente) -> mantener posición anterior (flat si
                                         todavía no hubo ninguna señal)
Salida: señal opuesta. Una sola posición a la vez, siempre en mercado tras
la primera señal.
```

## H2 — Donchian Breakout (N=20)

```
Upper[t] = max(High[t-20 : t-1])   # excluye la barra actual
Lower[t] = min(Low[t-20 : t-1])
Close[t] > Upper[t] -> LONG al Open de t+1
Close[t] < Lower[t] -> SHORT al Open de t+1
si ninguna condición -> mantener posición anterior
Salida: señal opuesta.
```

## Qué NO hace el script (por diseño, no por omisión)

- No agrega filtros (EMA, RSI, sesión, ATR) para mejorar resultados.
- No ajusta N ni el período de Donchian después de ver resultados.
- No corre el período de Test bajo ninguna circunstancia (ver arriba).
- No combina H1 y H2 en un solo resultado.
- No elige el mejor N de H1 como "el resultado de H1".

## Métricas y veredicto por hipótesis/período

Por cada combinación (H1-N20/60/120/252, H2-D20) × (Train, Validation), en
`resultados/<periodo>/<label>_*`:

- `_metrics.txt`: trades cerrados, win rate, PF, expectancy (% y pips), max
  drawdown %, Sharpe anualizado, retorno total %, veredicto.
- `_equity.png`: curva de equity (base 100, rebasada al inicio del período).
- `_dist_trades.png`: histograma de retornos por trade.
- `_retorno_anual.csv`: retorno por año calendario (detecta concentración
  temporal).
- `resumen.csv` (uno por período): todas las combinaciones en una tabla.

Un trade que sigue abierto al cierre del período (sin señal de reversión
todavía) se excluye de las estadísticas de trades cerrados y se reporta
aparte (`trades_abiertos_excluidos`) — no se fuerza su cierre con el último
precio disponible para no sesgar PF/expectancy con un resultado no realizado.

Criterios de veredicto (pre-registrados, aplicados automáticamente en
`utils.report_period`, no elegidos después de ver el número):

| PF | Veredicto |
|---|---|
| < 0.90 | fuerte candidato a eliminar |
| 0.90 – 1.10 | inconcluso |
| 1.10 – 1.20 | candidato a investigación |
| > 1.20 y expectancy > 0 | candidato fuerte |

## Cómo correr

```bash
cd investigacion/fase2
python h1_momentum.py
python h2_donchian.py
```

Ambos son idempotentes — vuelven a escribir `resumen.csv` reemplazando solo
la fila de cada label, no duplican filas si se corren de nuevo.

## Resultado final — FASE 2 CERRADA (2026-08-08)

Ninguna hipótesis sobrevive validación.

H1-N120 fue el único candidato con PF > 1.20 en ambos períodos, pero fue eliminado
por falta de estabilidad temporal:
- 2016 (70% de la muestra, 16 trades): PF 0.38, -804 pips
- El resultado positivo agregado (PF 1.82) depende de 4 trades aislados en años
  con 1–2 operaciones
- Bootstrap CI90%: [0.585, 4.727] — no robusto estadísticamente

El Test (2020–2026) NO fue ejecutado. Permanece congelado.

Regla pre-registrada aplicada:
"Si H1 y H2 fracasan, no se agregan filtros. Se busca una nueva explicación
económica/estadística concreta antes de definir H3."
