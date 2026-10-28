# Kronnos — Integración de patrones de repos externos (sin trade real)
Fecha: 2026-10-28. Estado: PR en borrador basado en #46, basado en #45.

## Alcance realmente implementado
- `tools/lineage_kronnos.py`: manifiesto estable SHA-256 (contenido, nombres relativos, versión modelo, git sha). Inspirado en la idea de procedencia y transformaciones reproducibles publicada por Two Sigma Memento. **No instala ni importa Memento**. La hora deliberadamente no se introduce dentro del hash para repetirlo. No es sello RFC3161 ni custodia externa.
- `tools/comparador_motores.py`: interfaz canónica para cotejar resultados proporcionados por simuladores externos bajo dataset/config/horizonte/costos idénticos. NO ejecuta ni instala LEAN o NautilusTrader, NO valida fills por sí solo.
- `tests/test_lineage_engines.py`: pruebas de determinismo, mutación, rutas y acuerdos.
- Son adaptadores mínimos, 0 dependencias nuevas, 0 invocaciones LLM, 0 credenciales, 0 workflows schedule.

## Candidatos externos y decisiones
1. Two Sigma Memento: referencia de procedencia Python, licencia Apache-2.0; enfoque Memento-light antes de integrar dependencia externa. https://github.com/twosigma/memento
2. QuantConnect LEAN: motor Python/C# Apache-2.0; requiere entorno y dataset comparables. No instalado ni probado; piloto aislado más adelante. https://github.com/QuantConnect/Lean
3. NautilusTrader: motor Rust/Python LGPL-3.0. API v1 estable distinta de v2 prerelease, cuya documentación requiere Python 3.13-3.14; no integrar dependencia hasta especificar API/versión y probar. https://github.com/nautechsystems/nautilus_trader
4. Goldman Sachs gs-quant: estudiar riesgos sin depender de credenciales institucionales; sin instalación.
5. CCXT: no integrar hasta tener requerimiento read-only y revisión de seguridad en fuentes.
6. ArcticDB BSL 1.1 puede restringir producción: NO instalar por ahora.

## Política de validación y seguridad
- No alterar KT-002, guardia, ATLAS, H3/H4 ni los PRs de barreras estadísticas.
- Comparación de estrategias solo con muestras congeladas y métricas definidas; DSR, preregistro externo y validación estadística siguen obligatorios; NO promoción automática.
- Revisar cadena de suministro, licencias y costes antes de instalar repos de terceros; preferir versiones y hashes fijados.
- GitHub CI aislado evalúa scripts, no sistema financiero real.
- Si manifiestos cambian, fallar cerrado; ninguna estrategia se habilita por igualdad de SHA o coincidencia de métricas.

## Progreso
Implementación parcial real: contratos y validaciones locales. NO es instalación de los motores externos, ni migración completa del proyecto. Próximo paso: piloto LEAN o NautilusTrader en entorno aislado cuando PR #42 y #45/#46 sean compatibles y se congele muestra.
