# Kronnos — Fase 2: Binance público + Qlib sandbox
Se consulta Binance SPOT BTCUSDT 1h en modo solo lectura, sin claves ni órdenes. Esta conexión es distinta del conector de ChatGPT: GitHub Actions hace su propia consulta a api.binance.com, con host fijo y lista blanca.
`python3 tools/kronnos_binance_bars.py --symbol BTCUSDT --interval 1h --limit 24`
Salida: CSV OHLCV y manifest con SHA256, UTC de obtención, símbolo e intervalo. No prueba recibo independiente de datos ni preregistro temporal; sus barras pueden incluir una vela en curso. Un dataset descargado después de un evento nunca prueba pronóstico prospectivo.
Instalación real de pyqlib en runner efímero Ubuntu 22.04 Python 3.10 para comprobar compatibilidad sin afectar la rama principal ni versiones del entorno de KT-002.
**No se han ejecutado factores Alpha158, estrategia real ni motor de backtest.** No alterar ATLAS PR42; no se autoriza trading.
