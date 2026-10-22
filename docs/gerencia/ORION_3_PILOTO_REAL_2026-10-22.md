# ORION 3.0 — B2 a B4: pruebas de componentes reales (sin integración productiva)

**Fecha:** 2026-10-22. **Versión propuesta:** smoke funcional de upstreams anclados; sin cambiar ORION público.

## Por qué NO fusionamos código de terceros en ORION
OpenHands Agent Canvas requiere Node >=24 y una colección amplia de dependencias JS. Su propia infraestructura de pruebas e2e usa LLM simulados, navegador y varios servicios. No se puede equiparar su README con un controlador de sesiones privadas de Claude/ChatGPT. El costo de incorporar un segundo panel y una segunda pila no está justificado aún.

TradingAgents v0.7.0 exige Python >=3.11, LangGraph y varios conectores de proveedores (`langchain-openai`, `langchain-anthropic`, `yfinance`, etc.). Su importación carga configuración y entorno; **no está permitido usar sus rutas de ejecución financiera real**. La separación del entorno es obligatoria.

## Experimento funcional aprobado (sin datos reales)
En `.github/workflows/orion-framework-smoke.yml`, dos trabajos **independientes**, ejecutados en runners Linux desechables de GitHub, sin checkout del laboratorio, sin credenciales, sin conexión con broker ni monto real.

1. **B2 — Inventario inicial de superficie técnica:** comprueba commits completos y metadatos oficiales `package.json` y `pyproject.toml`, versión, licencia y cantidad de dependencias directas. Es una inspección básica de arquitectura; **NO equivale a auditoría de vulnerabilidades ni cadena de suministro**.
2. **B3 — OpenHands real:** descarga el repo público al runner, verifica SHA, instala dependencias con `npm ci --ignore-scripts`, compila el frontend en modo `VITE_MOCK_API=true`, verifica que existan archivos de build. **No ejecuta el backend de agentes ni una sesión LLM.**
3. **B4 — TradingAgents real:** descarga repo público al otro runner, verifica SHA, instala paquete con pip, importa `tradingagents` y `DEFAULT_CONFIG`, comprueba versión 0.7.0. **No ejecuta debate real, proveedores LLM, backtests, datos BTC ni órdenes.**

La instalación y compilación de código de terceros solo ocurre en runners temporales que no tienen `data/kt002/`, `data/kt003/` ni `CLAUDE.md`. Cualquier dependencia maliciosa puede tener acceso a la red del runner; **el resultado no es garantía de seguridad** y no se proporcionan claves. La política no incluye descargar secretos ni almacenar salidas privadas.

## Criterios para evaluar el resultado
- Ambos trabajos con conclusión `success` y logs accesibles.
- Si falla compilación, dependencia, espacio o tiempo, registrar causa; no ocultar fallo ni considerarlo que prueba incompatibilidad esencial.
- Comparar tamaño, mantenimiento y costos de operación; ORION sigue siendo panel único y los chats son canales de trabajo.
- Solo adoptar código fuente de terceros después de una propuesta separada, permiso mínimo, escaneo más profundo, atribución de licencia y pruebas con datos sintéticos.
- La ejecución del frontend mock y el import real son **pruebas parciales**, no ciclo completo multiagente. Un ciclo real con modelos privados costaría y requeriría nuevos permisos que el dueño no concedió.

## Restricciones intocables
Sin cambios a `KT-002`, `KT-003`, preregistros, holdouts, `kt002.yml`, `guardia.yml`, visor Claude, `CLAUDE.md`, `AGENTS.md`, API privadas, claves, broker, órdenes o capital real. Auditor/riesgo conservan vetos. No conectar Google ni el gateway.

## Reversión
Se puede eliminar este workflow y este documento mediante PR normal. Nada se desplegó al sitio, ni se añadió infraestructura de ejecución permanente.

## Fuentes fijadas
- OpenHands `542aa917de74d24d3f1eb7abd86622097bfff21f`, README y `package.json` con version 1.31.0.
- TradingAgents `e8f5503e9b86d5c2710b0c76b1f686703968c9df`, README y `pyproject.toml` version 0.7.0.

**Estado de ejecución:** pendiente del resultado del workflow del PR; actualizar solo tras leer jobs/logs.

## Ejecución observada — 2026-10-22

[GitHub Actions #39866289074](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39866289074) concluyó **success**, con DOS jobs completados en verde:
- **openhands-sandbox:** repositorio OpenHands fijado por SHA descargado, Node 24 y metadatos comprobados, `npm ci --ignore-scripts`, `npm run build:mock` y artefacto de compilación presente. **Front-end real, API simulada**; no backend de agentes en ejecución.
- **tradingagents-sandbox:** repositorio TradingAgents fijado por SHA descargado, paquete instalado mediante pip e importación de `tradingagents` y `DEFAULT_CONFIG` con versión 0.7.0. No se ejecutaron agentes de análisis ni decisiones de trading.

**Valor de B2–B4 alcanzado:** compatibilidad técnica inicial e instalación/compilación real reproducible. **No alcanzado:** auditoría completa de dependencias, seguridad de cadena de suministro, debate financiero multiagente offline y prueba end-to-end de colaboración con Claude/ChatGPT. Estas tareas siguen pendientes de evaluación posterior. Ni el CI verde ni un paquete instalable son prueba de valor cuantitativo.

**Decisión de integración acotada:** ORION podrá mostrar enlaces a estas ejecuciones y sus límites, pero no importar el runtime de OpenHands/TradingAgents ni activar cuentas, claves o trading. El dueño mantendrá control desde ambos chats.

[PR #25](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/25) integrado tras CI verde.

## Ampliación de prueba en el software original

El piloto ejecuta también el test upstream `tests/test_risk_router_path_map.py` de TradingAgents mediante pytest (sin claves). Comprueba que las rutas del debate y las rutas de revisión de riesgo conducen a destinos válidos y que el debate finaliza según el límite configurado.

Esta es una **prueba real del código del upstream**, no una simulación creada por ORION. **No equivale a que Desconfiado haya aprobado**, ni garantiza que una propuesta de TradingAgents sea segura o científicamente válida; la autoridad del auditor independiente y la prohibición de órdenes reales permanecen fuera de ese framework.

La instalación de `pytest` se realiza únicamente en el runner efímero, sin credenciales, sin copiar datasets y sin habilitar un servicio permanente.

## B4 — Prueba del grafo completo SIN LLM externo

Tras comprobar las rutas del debate financiero, se incorpora la prueba oficial upstream `tests/test_graph_end_to_end.py::test_a_full_run_reaches_a_logged_decision` (variantes free-text y structured). Esta prueba sustituye el proveedor de modelos por un `ScriptedModel` y los accesos a datos por respuestas sintéticas mediante monkeypatch/fixtures, comprobando que analistas, investigación, decisión y registro del resultado ejecuten su flujo sin servicios externos.

**Interpretación válida si el CI pasa:** TradingAgents v0.7.0 efectivamente puede ejecutar un recorrido de su grafo multiagente con entradas ficticias y modelos simulados, sin gastar tokens de Claude/OpenAI. **No demuestra** predicción rentable, calidad de razonamiento de los LLM, cumplimiento de nuestro veto independiente Desconfiado ni interoperabilidad directa de las sesiones privadas de ambos chats.

La ruta ejecutada se verifica mediante los tests del upstream, no por una simulación nuestra que finja ejecutar TradingAgents. El grafo se conserva solo dentro del runner desechable sin compartir datos con KT-002/KT-003.
