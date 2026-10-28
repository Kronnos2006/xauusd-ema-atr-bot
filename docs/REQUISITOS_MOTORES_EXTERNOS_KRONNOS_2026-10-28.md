# Kronnos — Requisitos verificados de ejecución de motores externos
Fecha: 2026-10-28. Estado: preflight en PR, sin ejecución de motores reales.

## Bloqueos
1. LEAN CLI oficial documenta que `lean backtest` requiere pertenecer a una organización en un plan pago; también requiere Docker y dataset compatible. Fuente https://www.quantconnect.com/docs/v2/lean-cli/api-reference/lean-backtest y https://www.quantconnect.com/docs/v2/lean-cli/key-concepts/getting-started . No se intentó acceder a cuenta ni instalar CLI en GitHub.
2. NautilusTrader necesita elegir versión Python y API estable, y dataset compatible. Fuente https://github.com/nautechsystems/nautilus_trader . No instalado ni ejecutado: fijar versión exacta tras validación de compatibilidad.
3. Misma muestra congelada, convenciones de timestamp, volumen, fees, slippage, órdenes y granularidad obligatorios. No usar CSV de spread como barras OHLC sin transformación explícita.
4. Convertir salida genuina de cada motor con procedencia: run_id, versión, SHA del artefacto, dataset SHA, config SHA, sample_id, fees_model, trades, returns, max drawdown.
5. tools/preflight_motores.py comprueba metadatos y divergencia. **No certifica autenticidad de motores externos por sí solo**. Validar Actions logs o auditor independiente y las salidas originales.

## Decisión de implementación
El preflight puede correr en GitHub sin redes, credenciales ni broker. Se evita activar un backtest comercial no autorizado o fabricar una segunda salida como si fuera NautilusTrader. Sin demostración de backtests reales no se cierra validación externa.
No modificar KT-002, ATLAS ni permitir trading real.
