# Investigación de repositorios similares — ORION y Laboratorio Cuantitativo

**Corte:** 2026-10-22. **Método:** búsqueda pública de código abierto, lectura de README/documentación oficiales y comprobación de metadatos de GitHub (licencia, última actividad, repositorio no archivado). Comparación documental, **sin ejecutar ni instalar software externo**, sin pruebas independientes de seguridad. No es recomendación de operar dinero real.

## Pregunta
¿Qué soluciones ya construidas pueden acelerar un laboratorio de investigación cuantitativa auditada con agentes especializados, supervisión humana, registro de evidencia y un centro de control visual, **sin sustituir los chats de Claude y ChatGPT** ni modificar los experimentos activos?

## Decisión resumida

**No aparece un único repositorio comprobado que resuelva de forma directa y segura TODAS nuestras exigencias a la vez**: adquisición prospectiva 1h BTC, KT-002/003 congelados, independencia de Desconfiado/Analista/Riesgo, trazabilidad estricta, control desde los chats existentes y ORION móvil. Pero hay piezas **mucho más maduras** que conviene conocer y evaluar en un piloto aislado.

- **Control de agentes y tareas:** [OpenHands](https://github.com/OpenHands/OpenHands) es el punto de comparación principal. Su Agent Canvas soporta distintos backends/CLI de agentes, incluyendo Claude Code y Codex; no equivale a vincular las conversaciones privadas de chatgpt.com y claude.ai. Mantenerlo como referencia; adoptar solo si el dueño decide ampliar el alcance de ORION.
- **Arquitectura de analistas y riesgo financiero:** [TradingAgents](https://github.com/TauricResearch/TradingAgents) es el candidato más cercano al organigrama financiero. **Solo usar sus patrones de debate/roles y evidencia**, no su ruta de órdenes ni sus decisiones automáticas.
- **I+D cuantitativo futuro:** [Microsoft RD-Agent](https://github.com/microsoft/RD-Agent) automatiza formulación y prueba de ideas de investigación; útil como diseño para **Fase 0 separada**, NO para tocar KT-002/KT-003 ni lanzar optimizaciones post hoc.
- **Investigación cuantitativa reproducible:** [Microsoft Qlib](https://github.com/microsoft/qlib) contiene datos, modelos y flujo experimental; estudiarlo para un laboratorio futuro aislado.
- **Proveniencia e informes financieros:** [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) enfatiza cálculo determinista, provenance y flujo multiagente, más orientado a research y finanzas de acciones.

## Comparación verificada

| Proyecto | Capa parecida | Ventaja para nosotros | Límite / riesgo | GitHub (corte 2026-10-22) |
|---|---|---|---|---|
| **OpenHands / Agent Canvas** | centro de agentes de programación, tareas, automatización | ejemplos de interfaz, arquitectura de backend-agente y coordinación | integrar sus agentes requeriría procesos externos, permisos y quizá costos; no conecta chats web ya abiertos | [MIT, activo](https://github.com/OpenHands/OpenHands), ~91.6k estrellas; actividad 22-oct |
| **TradingAgents** | roles analista técnico/fundamental, gestor investigador, riesgo | diseño de jerarquías, análisis en paralelo, debate, checkpoint y fuentes punto-en-el-tiempo | es marco de **investigación**, nunca adoptar ejecución/órdenes en nuestro entorno | [Apache-2.0, activo](https://github.com/TauricResearch/TradingAgents), ~113k estrellas; actividad 16-oct |
| **RD-Agent** | fábrica de hipótesis cuantitativas y agentes de I+D | diseño de Fase 0, hipótesis y evaluación automatizada separada | busca mejorar modelos; la optimización puede contaminar un experimento prospectivo activo | [MIT, activo](https://github.com/microsoft/RD-Agent), ~15k estrellas; actividad 21-oct |
| **Qlib** | datos, modelos, experimentos cuantitativos | infraestructura de investigación y reproducibilidad | no integra por sí solo chat de Claude/ChatGPT ni establece gobernanza independiente | [MIT, activo](https://github.com/microsoft/qlib), ~49.6k estrellas; actividad 22-oct |
| **FinRobot** | informes financieros y múltiples agentes | separación modelo/herramienta/cálculo, fuentes y revisión | más enfocado en análisis de acciones, valoración y finanzas corporativas que en la serie BTC/4h | [Apache-2.0, activo](https://github.com/AI4Finance-Foundation/FinRobot), ~8.3k estrellas; actividad 28-sep |
| **NautilusTrader** | pruebas cuantitativas y simulación determinista | referencia para backtesting/eventos/costos en *investigaciones nuevas* | incluye ejecución en vivo; **prohibido conectar brokers u órdenes**; licencia LGPL requiere revisión | [LGPL-3.0, activo](https://github.com/nautechsystems/nautilus_trader), ~30.6k estrellas; actividad 22-oct |
| **Agency** | supervisor multiagente con Claude Code/Codex y fichas Markdown | coordinación ligera, agentes persistentes y revisión de propuestas | AGPL-3.0 requiere examen legal antes de integrar código; escala/seguridad no auditadas | [AGPL-3.0](https://github.com/christag/agency), ~74 estrellas; última actividad marzo |
| **Cortex** | dashboard de equipos/roles/costos y adaptadores | UI de observabilidad y registros de agentes | ~0 estrellas en metadatos consultados, madurez no contrastada, no exponer públicamente | [MIT](https://github.com/omarnagy91/cortex), actividad abril |
| **ForgeFlow** | permisos, auditorías, orquestación multiagente | patrones de aprobación, presupuestos, registros y resiliencia | proyecto pequeño (~7 estrellas): sus afirmaciones técnicas no son certificación externa | [Apache-2.0](https://github.com/JoelJohnsonThomas/ForgeFlow), actividad julio |

**Cifras de popularidad y fechas**: son una fotografía del 22-oct, no prueba de calidad, seguridad ni mantenimiento futuro. Las licencias se refieren a metadatos GitHub, deben comprobarse por ruta/archivo antes de copiar.

## Cuánto se parece cada uno a la meta (comparación cualitativa, no puntuación científica)

- **OpenHands: ALTO** para gestión de agentes programadores + consola; **BAJO** para auditoría cuantitativa especializada.
- **TradingAgents: ALTO** en división financiera analista-investigación-riesgo; **MEDIO/BAJO** en controles de independencia estricta.
- **RD-Agent: ALTO** para hipótesis y experimentación de investigación; **INCOMPATIBLE** con manipulación de un KT-002 preregistrado.
- **FinRobot: MEDIO/ALTO** para investigación verificable e informes, con otro foco de activos.
- **Qlib: ALTO** para motor de estudio cuantitativo, **BAJO** para gestión chat/móvil.
- **Agency / Cortex: MEDIO** para observabilidad; menor escala pública verificada.

## Qué podemos reutilizar sin romper lo existente

1. **Ahora, sin instalaciones:** mejorar documentación de roles, protocolo de entregas (INICIO/ENTREGA), registro de evidencia, fecha de datos, alertas y criterios de auditoría. Usar *ideas de arquitectura* sin copiar código.
2. **Prueba aislada y sin datos sensibles (futura, sujeta a revisión):** clonar OpenHands en un repo/sandbox distinto; probar solo con proyectos de juguete, permisos sin escritura de KT-002. Evaluar comparando contra ORION y costos.
3. **Prueba de investigación Fase 0 independiente (futura, con autorización):** configurar TradingAgents / RD-Agent / Qlib con datasets sintéticos o de acceso público en un entorno **separado**. No importar dataset reservado, no utilizar holdouts, no reoptimizar KT-002.
4. **Pruebas de calidad que faltan:** exigir tres informes genuinos consecutivos del analista con UTC y fuentes; dictamen real del Desconfiado; ensayar recuperación de fallos sin tocar experimento. Ningún framework tercero reemplaza estos requisitos.

## Decisión de adopción / no adopción

**Recomendación:** conservar ORION actual como **panel estable de supervisión** y la forma de control desde ambos chats. No sustituir ni copiar archivos de OpenHands/TradingAgents en el repo actual. Crear un *piloto pequeño, separado, reversible*, únicamente cuando exista necesidad clara de nuevas funciones.

**No adoptar ahora:** workflows de ejecución en brokers, trading en vivo, agentes autoejecutores, Google OAuth, secretos en frontend, optimizadores en KT-002, repos con poca evidencia de mantenimiento o licencia incompatible sin revisión.

**Evaluación obligatoria antes de incorporar código:**
- Compatibilidad de licencia, terceros y obligaciones de distribución.
- Pruebas reproducibles, estado de issues y cambios recientes, vulnerabilidades y dependencias.
- Seguridad de ejecución de agentes, aislamiento, permisos mínimos, costo y secretos.
- Capacidad de trabajar por PR respetando autoridad exclusiva del dueño y auditoría independiente.
- Riesgo de look-ahead, data leakage, edición de experimentos y estadísticas espurias.
- Reversión sencilla: **sin migrar el único publicador de Pages ni borrar el visor de Claude**.

## Fuentes primarias (consulta 2026-10-22)

- OpenHands: https://github.com/OpenHands/OpenHands y README/Agent Canvas.
- TradingAgents: https://github.com/TauricResearch/TradingAgents y README/CHANGELOG (incluye mejoras de integridad punto-en-el-tiempo).
- Microsoft RD-Agent: https://github.com/microsoft/RD-Agent y docs de Quant Agent.
- Microsoft Qlib: https://github.com/microsoft/qlib y documentación de componentes.
- FinRobot: https://github.com/AI4Finance-Foundation/FinRobot, descripción de v0/v1/v2.
- NautilusTrader: https://github.com/nautechsystems/nautilus_trader y https://nautilustrader.io/open-source/.
- Agency: https://github.com/christag/agency.
- Cortex: https://github.com/omarnagy91/cortex.
- ForgeFlow: https://github.com/JoelJohnsonThomas/ForgeFlow.

**Grado de certeza:** alto respecto a presencia de repos y sus descripciones/licencias/metadatos públicos, **limitado** para funcionalidad end-to-end, seguridad, calidad de código y adecuación a nuestros datos, que no se ejecutaron.
