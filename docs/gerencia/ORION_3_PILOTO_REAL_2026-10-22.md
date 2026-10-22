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
