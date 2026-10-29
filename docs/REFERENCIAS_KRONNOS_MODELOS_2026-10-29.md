# Kronnos — catálogo aprobado de referencias y reutilización

Fecha: 2026-10-29. Propietario aprueba estudiar y probar componentes de software similar, sin alterar conclusiones científicas. Se preservan nombres y ubicaciones explícitos para no inventar comparaciones posteriores.

| Proyecto | Repositorio | Uso candidato | Control |
|---|---|---|---|
| Lumina Capital AI Hedge Fund Engine | https://github.com/ramuza0113-sketch/lumina-ai-hedge-fund | Arquitectura de separación análisis/ejecución, factores, ensemble, guardián de riesgo, observabilidad | Licencia CC BY-NC 4.0; **no copiar código** ni desplegar en contexto comercial sin licencia apropiada. Claims de README no verificados operativamente |
| Microsoft Qlib | https://github.com/microsoft/qlib | Experimentos cuantitativos, Alpha158, factores | Evaluar contratos, dependencia y licencia antes de integrar |
| Freqtrade / FreqAI | https://github.com/freqtrade/freqtrade | Retraining, feature pipelines, fallos y observación | Aislar capacidades; no conectar broker |
| Kronos | https://github.com/shiyu-coder/Kronos | Inferencia financiera OHLCV | No declarar activo sin prueba |
| TimesFM | https://github.com/google-research/timesfm | Pronóstico temporal | Verificar restricciones de pesos/versiones antes de usar |
| Amazon Chronos | https://github.com/amazon-science/chronos-forecasting | Modelo candidato posterior al preregistro | No agregar a N retrospectivamente sin censo |
| NautilusTrader | https://github.com/nautechsystems/nautilus_trader | Motor de backtest independiente | Solo sandbox |
| LEAN | https://github.com/QuantConnect/Lean | Segunda simulación independiente | Solo sandbox |

## Decisiones Kronnos
1. Conservar KT-002, KT-001, Kronos, TimesFM, Siempre sube, ATLAS y ORION.
2. Tomar ideas de Lumina de arquitectura y patrones generales, no replicar sus archivos ni agentes LLM.
3. Priorizar adaptadores de modelos y contratos de predicción **sin cambiar modelos existentes**, con métricas de trazabilidad, origen, datos, timestamps y hash.
4. Ejecutar pruebas offline sin brokers, sin claves, sin inferencias falsas ni costes de tokens.
5. Diferenciar: verificación de formato != modelo instalado != ejecución real != precisión fuera de muestra.
6. ATLAS PR42/H3/H4 permanecen bloqueados hasta cumplir todas las barreras.
7. Documentar licencia concreta de cada componente antes de copiar o integrar código ajeno.

## Observación Lumina
README inspeccionado en GitHub el 2026-10-29: se presenta como Lumina Capital AI Hedge Fund Engine v6.4.8; licencia LICENSE CC BY-NC 4.0 verificada. El README y las discusiones describen TimesFM, Qlib Alpha158, LightGBM, agentes y riesgos; esas son **afirmaciones del proyecto**, no auditoría de resultados.
