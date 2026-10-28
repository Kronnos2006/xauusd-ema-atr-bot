# Kronnos: motores sin plan de pago
Fecha 2026-10-28. Preparado para evaluar instalación local sin suscripción, sin trading.

## LEAN sin CLI de pago
La documentación actual de QuantConnect exige organización de pago para ejecutar `lean backtest` vía CLI: https://www.quantconnect.com/docs/v2/lean-cli/api-reference/lean-backtest .
Pero el motor base es open source, y su documentación describe compilarlo directamente con dotnet y ejecutar Launcher sin utilizar LEAN CLI: https://www.quantconnect.com/docs/v2/lean-engine/getting-started .
Ruta alternativa:
1. Revisar la licencia, versión y datos de fuente permitida en https://github.com/QuantConnect/Lean .
2. Clonar `QuantConnect/Lean` a un sandbox local separado del sistema principal; fijar commit SHA auditado, no usar `main` flotante. Requiere SDK .NET compatible con el commit elegido (los comandos de documentación histórica pueden estar obsoletos).
3. Compilar con `dotnet build QuantConnect.Lean.sln`, luego configurar `Launcher/config.json` para Backtesting, algoritmo sin conexión de brokerage y ruta a datos de prueba.
4. Ejecutar Launcher según la ruta del binario y framework que realmente genere la compilación. Guardar SHA dataset, logs y versión de LEAN. Nunca ejecutar modo live.
5. Confirmar datos gratuitos compatibles, esquema y permisos de uso. No asumir disponibilidad de datasets de QuantConnect gratuitos.
6. `python3 tools/motores_gratis.py --engine lean --source-dir ./Lean` valida requisitos, NO compila ni ejecuta un backtest.
No descargar motor ni activar el workflow automáticamente por costo de CPU/datos.

## NautilusTrader sin suscripción
https://nautilustrader.io/docs/latest/getting_started/installation/
NautilusTrader estable 1.x en PyPI se instala sin plan pagado, pero su API difiere de los ejemplos actuales 2.x prerelease. Usar v1 fijada y sus ejemplos de versión correspondiente, no `--pre` ni código 2.x mezclado. Crear entorno virtual; instalar `nautilus_trader==VERSION_VERIFICADA` y registrar SHA de la wheel/lock. El preflight `python3 tools/motores_gratis.py --engine nautilus` detecta versión y no ejecuta estrategias.

## Lo realmente integrado
Script de diagnóstico read-only, pruebas unitarias y workflow de CI sin redes externas ni instalación de motores.
El proyecto **NO** ha ejecutado backtests independientes ni validado retornos. El contrato PR #50 sigue separado y no sustituye sellado temporal, costo transaccional, controles #42, ni validación H3/H4.
P0 siguiente: una muestra congelada OHLCV con licencia y tiempo homogéneo, backtest de estrategia fija a través del motor real, exportar artefactos y cotejar. Sin acceso a broker, sin secrets.
