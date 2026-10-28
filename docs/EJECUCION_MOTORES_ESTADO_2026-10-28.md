# Kronnos — Preparación de ejecución real
Fecha 2026-10-28. No confundir prueba de instalación con backtest.

- En el runtime de esta sesión, Python 3.13.5: `nautilus_trader` no instalado, `dotnet` ausente, `docker` ausente. Intento `pip index versions nautilus_trader`: falló por resolución DNS; NO se obtuvo paquete. 
- GitHub Actions nuevo smoke de instalación de NautilusTrader estable 1.x usando runner Ubuntu 22.04 y Python 3.11, sin secrets, 12 min timeout y evidencia pip freeze. Instalación solo en runner efímero. NO corre backtest.
- El workflow debe confirmar `success` y mostrar versión antes de admitir instalación como comprobada.
- Sin datos históricos OHLCV homologados ni salida real de dos motores no se puede afirmar que comparador haya realizado validación independiente.
- Para LEAN se necesita runner .NET compatible y código del motor fijado, compilación desde código fuente, dataset con licencia y backtest aislado. No instalados hoy.
- Mantener salida sin ordenes ni credenciales, H3/H4 bloqueados, ATLAS PR42 independiente.
- Referencia de requisitos: https://nautilustrader.io/docs/latest/getting_started/installation/ (1.x estable y 2.x rc diferentes) y https://github.com/QuantConnect/Lean .
