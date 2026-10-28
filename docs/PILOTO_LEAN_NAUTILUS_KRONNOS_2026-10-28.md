# Kronnos — Piloto motores: aislamiento y contrato de comparación
Fecha 2026-10-28. PR experimental, sin fusión automática y sin trading.
## Decisión
LEAN primero como candidato de comparación real, NautilusTrader segundo. **NO instalados**. En este PR hay únicamente un ensayo de contrato con una muestra sintética y dos implementaciones locales equivalentes (clon declarado explícitamente); sirve para verificar CI e intercambio de métricas pero NO demuestra independencia.
## Requisitos públicos
- https://github.com/QuantConnect/Lean : herramienta LEAN CLI y Docker, comando de backtest `lean backtest`, también permite live, prohibido en este piloto. Recursos/datos del backtesting requieren revisión de CLI, versión, licencias y fuente.
- https://github.com/nautechsystems/nautilus_trader : estable v1 y v2 RC tienen APIs no intercambiables; v2 no recomendada para trading de dinero real. No usar --pre sin fijar versión/entorno.
## Diseño del ensayo siguiente
1. Mantener sandbox separado del proyecto en GitHub Actions manual, sin secretos ni acceso a cuentas.
2. Preparar muestra histórica congelada de precio+timestamp, indicar instrumento/horizonte/fees/slippage; SHA-256.
3. Ejecutar estrategia buy-hold FIXA en LEAN Docker con versiones fijas y datos permitidos, sin optimizar parámetros.
4. Convertir JSON de salida a contrato `comparador_motores.py`: dataset_sha256, config_sha256, sample_id, fees_model, net_return, max_drawdown, trades.
5. Contrastar contra una implementación independiente, registrar diferencias y evidencia; SOLO DESCRIPTIVO.
6. Repetir con Nautilus stable v1 (o v2 fijada si se verifica compatibilidad) únicamente si LEAN alcanza reproducibilidad.
## Límites
- El fixture no ejecuta LEAN, ni Nautilus, ni demuestra viabilidad para producción o rentabilidad.
- No modifica KT-002 ni ATLAS. Toda promoción está bloqueada hasta DSR, sellado externo y pruebas independientes.
- Prohibido conectar API keys, utilizar live, o descargar datos propietarios sin permiso.
