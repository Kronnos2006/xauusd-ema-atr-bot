# Data Dictionary

Índice: [[Bienvenido]] · Ver también [[Infraestructura]] · [[data-integrity]]

Cada archivo de datos del proyecto: qué es, de dónde sale, con qué frecuencia se actualiza, y cómo se verifica. Escrito el 2026-07-27 (revisión externa, punto 4) — mantener al día cuando se agregue una fuente de datos nueva, no dejar que se desactualice.

## Datos macro crudos (`historial/`, ignorados por git)

| Archivo | Columnas | Fuente | Frecuencia | Verificación |
|---|---|---|---|---|
| `dfii10.csv` | `observation_date, DFII10` | FRED, serie `DFII10` (tasa real TIPS 10 años), descarga pública sin API key | Diaria (días hábiles) | Cruzada contra home.treasury.gov (correlación 1.000000, ver [[Macro DFII10 - fase 1]]); sin revisión retroactiva confirmada vía ALFRED (9 fechas, 2003-2026, coincidencia exacta); continuidad verificada (`verificar_integridad_datos.py`, 0 huecos >7d, 0 duplicados) |
| `t10y2y.csv` | `observation_date, T10Y2Y` | FRED, serie `T10Y2Y` (spread 10Y-2Y nominal) | Diaria | Cruzada contra Treasury nominal (ver [[Macro 2s10s - fase 1]]). Hipótesis descartada — dato ya no en uso activo, se conserva por trazabilidad |
| `treasury_real_yield_2025.csv` / `_2026.csv` | `Date, 5 YR, 7 YR, 10 YR, 20 YR, 30 YR` | home.treasury.gov, Daily Par Real Yield Curve | Diaria | Fuente de verificación cruzada para DFII10 (columna `10 YR`), no fuente primaria de ninguna hipótesis |
| `treasury_nominal_yield_2025.csv` / `_2026.csv` | `Date, 1 Mo ... 30 Yr` (14 tenors) | home.treasury.gov, Daily Par Yield Curve (nominal) | Diaria | Fuente de verificación cruzada para T10Y2Y |
| `dxy_sintetico.csv` | `time, EURUSD, USDJPY, GBPUSD, USDCAD, USDSEK, USDCHF, dxy_sintetico` | MT5 (6 pares FX, cierre D1) + fórmula ICE aplicada en `construir_dxy_sintetico.py` | Diaria | Validado contra 21 valores reales de investing.com (correlación 0.9945, ver [[Macro DXY - fase 1]]) — no es dato de mercado directo, es una construcción propia, documentada como tal |

## Precios (MT5, no persistidos en archivo — se bajan on-demand)

| Símbolo | Uso | Frecuencia | Verificación |
|---|---|---|---|
| `XAUUSD` | Activo principal de todas las hipótesis (entrada/salida, ATR) | D1/H1/M15 según hipótesis | Historial confirmado desde 2004-06-11 vía `copy_rates_range` |
| `XAGUSD` | Ratio oro/plata | D1 | Historial confirmado desde 2008-11-07 (más corto que XAUUSD, define el rango usable del ratio) |
| `EURUSD, USDJPY, GBPUSD, USDCAD, USDSEK, USDCHF` | Componentes del DXY sintético | D1 | Historial confirmado desde 2000-01-03 (6902 días solapados) |

## Datos operativos generados en vivo (raíz del proyecto, ignorados por git salvo lo indicado)

| Archivo | Columnas / estructura | Generado por | Frecuencia | Notas |
|---|---|---|---|---|
| `senales_demo_live.csv` | `timestamp_vela, timestamp_deteccion_utc, tipo, close_vela, ema_fast/slow/trend, atr, riesgo_teorico, sl_teorico, en_sesion_liquida, bid_real, ask_real, spread_real_puntos, precio_ref_real, gap_vs_close_R` | `log_senales_demo.py` | Por señal EMA9/21 M15 detectada | Familia EMA9/21 retirada — el dataset se conserva por si se revisita con evidencia nueva, sin research activo |
| `senal_macro_dfii10_live.csv` | `evento, fecha_evento_utc, fecha_inicio_episodio, fecha_entrada, entrada, sl, riesgo, fecha_salida, resultado_R, motivo_salida` | `log_senal_macro_dfii10.py` | Por episodio DFII10 detectado (~8/año esperado) | Holdout en vivo de un factor archivado — monitoreo pasivo, ver [[Macro DFII10 - fase 1]] |
| `estado_macro_dfii10.json` | `ultima_fecha_dfii10_procesada, episodio_pendiente, posicion_abierta` | `log_senal_macro_dfii10.py` | Se actualiza cada ciclo del logger | Estado interno del logger, no un dato analítico |
| `estado_monitor_dfii10.json` | `conteo, ultima_revision` | `_monitor_holdout_dfii10.ps1` | Diaria | Estado del monitor de conveniencia (toast), no productivo |
| `senales_demo_live.log` / `senal_macro_dfii10_live.log` | Texto, líneas de evento (ARRANQUE, errores de IPC, etc.) | Ambos loggers | Por evento | Log operativo, ver [[Errores y bugs corregidos]] para el historial de incidentes que motivaron su formato |

## Resultados de backtest (raíz y `historial/`, ignorados por git salvo el `.gitkeep` de la carpeta)

| Archivo | Columnas | Generado por |
|---|---|---|
| `resultados_backtest*.csv` | `tipo, entrada, sl, tp, time_entrada, resultado_R, salida, time_salida` | `Backtest ema v4.py` (familia EMA9/21) |
| `resultados_neto_spread*.csv` | Igual + `resultado_R_neto` | `descontar_spread()` aplicado sobre lo anterior |

## Metadatos de integridad (raíz, versionados en git a propósito)

| Archivo | Qué guarda | Generado por |
|---|---|---|
| `registro_checksums.json` | SHA256 + tamaño + fecha de última verificación, por archivo de `historial/` | `verificar_integridad_datos.py` (skill `data-integrity`) — versionado en git para que el historial de checksums sobreviva aunque los datos crudos no |

## Ver también
[[Infraestructura]] · [[data-integrity]] · [[Bitácora de decisiones]]
