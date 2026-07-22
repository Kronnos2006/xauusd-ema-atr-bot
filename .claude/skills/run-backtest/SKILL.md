---
name: run-backtest
description: Corre el backtest EMA/ATR activo (Backtest ema v4.py), respalda los CSV de resultados anteriores y resume el resultado nuevo comparado con la corrida previa.
disable-model-invocation: true
---

# Run Backtest

Corre la estrategia EMA cross + ATR sobre XAUUSD (`Backtest ema v4.py`) y compara el resultado con la corrida anterior.

## Pasos

1. Confirmar que MetaTrader 5 esté abierto y logueado — el script se conecta vía `mt5.initialize()`. Si falla con "no se pudo conectar a MT5", avisar al usuario que abra el terminal antes de reintentar.

2. Respaldar los CSV existentes antes de correr nada, para no perder la corrida anterior:
   - Crear la carpeta `historial/` si no existe.
   - Copiar `resultados_backtest.csv` -> `historial/resultados_backtest_<YYYYMMDD_HHMMSS>.csv`
   - Copiar `resultados_neto_spread.csv` -> `historial/resultados_neto_spread_<YYYYMMDD_HHMMSS>.csv`
   - Si alguno de los dos no existe todavía, omitir su backup sin error.

3. Ejecutar `python "Backtest ema v4.py"` y capturar toda la salida de consola.

4. De la salida, extraer:
   - Resultado del backtest principal (trades, win rate, R total)
   - Comparación con/sin filtro de sesión horaria
   - Mejor combinación de la optimización de trailing (parcial + multiplicador ATR)
   - Validación train/test (¿se sostiene el edge en el 30% final o parece overfitting?)
   - Resumen neto vs bruto de spread (¿sigue rentable después de descontar el spread?)

5. Si había una corrida anterior respaldada en el paso 2, comparar R total y win rate viejo vs nuevo, y señalar si mejoró, empeoró o se mantuvo estable.

6. Presentar todo en una tabla o lista corta. No pegar la salida cruda de la consola salvo que el usuario la pida explícitamente.
