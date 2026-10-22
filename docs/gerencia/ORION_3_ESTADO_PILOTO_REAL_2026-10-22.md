# ORION 3.0 — Estado integrado y decisión de arquitectura

**Corte:** 2026-10-22. Responsable del registro: ChatGPT (revisor técnico externo). Los resultados abajo proceden de GitHub Actions, no de sesiones privadas de agentes.

## Hechos comprobados en este turno

| Nivel | Evidencia | Resultado y límite |
|---|---|---|
| B1: contrato sintético | [CI 39863689201](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39863689201), PR #24 | Veto simulado y cadena de evidencia en sandbox: **PASS**. Contrato propio, no software externo |
| A: documentación upstream | [CI 39861475048](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39861475048), PR #23 | README fijados por SHA y pruebas de invariantes: **PASS**. No instala aplicaciones |
| B2/B3: OpenHands REAL | [CI 39866289074](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39866289074), PR #25 | Checkout fuente OpenHands **542aa917de74d24d3f1eb7abd86622097bfff21f**, `npm ci --ignore-scripts` y compilación real **build:mock**: **PASS**. No inicia backend de agentes ni chats web privados |
| B2/B4: TradingAgents REAL | [CI 39866289074](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39866289074), PR #25 | Checkout fuente **e8f5503e9b86d5c2710b0c76b1f686703968c9df**, pip install e import de `tradingagents`: **PASS**. No ejecución de modelos privados |
| B4: rutas de riesgo | [CI 39866920746](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39866920746), PR #27 | Test upstream original `test_risk_router_path_map.py`: **PASS**. No sustituye auditoría independiente |
| B4: grafo multiagente offline | [CI 39867208325](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39867208325), PR #28 | Test upstream `test_graph_end_to_end.py -k test_a_full_run_reaches_a_logged_decision`: **PASS**, con modelos scripted y datos simulados. Comprueba coordinación end-to-end original de TradingAgents, NO rentabilidad ni uso del modelo de Claude |
| Supervisión ORION | [PR #26](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/26), [Pages 39866786491](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39866786491) | Panel móvil y visor Claude publicados: **PASS**; pestaña Operaciones enlaza verificaciones reales sin simular agentes activos |

## Resultado técnico
**OpenHands**: candidato sólido para interfaz de programación, pero requiere Node 24, numerosas dependencias y un backend/servicio separado. La compilación con backend mock comprueba viabilidad técnica mínima, no seguridad ni utilidad medible frente al panel existente.

**TradingAgents**: grafo real con analistas, debates y decisión funcionó en test upstream con respuestas simuladas y datos falsos; sus rutas de riesgo también pasaron. Esto muestra que existe **una arquitectura multiagente funcional ya implementada** y reutilizable *conceptualmente*, pero **sus gestores de riesgo internos no tienen autoridad para aprobar KT-002 ni sustituir a Desconfiado**.

**ORION**: conservar actual, sin segunda interfaz pública ni conexión automática de chats. GitHub enlaza la evidencia de pruebas; dueño trabaja desde Claude y ChatGPT. Las pruebas no habilitan agencias de IA en vivo.

## Restricciones respetadas
No se cambiaron `data/kt002/`, `data/kt003/`, archivos de modelos, cron de inferencia, preregistros, holdouts, `CLAUDE.md`, `AGENTS.md`, reglas independientes o conexiones de broker. CI usa runners temporales sin credenciales de OpenAI o Anthropic. **No se hizo trading real** ni se afirma edge.

## Recomendación de adopción (etapa C)
1. **Conservar ORION v2/3 de supervisión**, sin introducir OpenHands como segundo dashboard en producción por ahora. Se evitaría una instalación grande que no ha demostrado una mejora específica para la forma de trabajo elegida.
2. **Reutilizar contratos y patrones documentados de TradingAgents** (separación analistas/debate/riesgo, registros y rutas del grafo) para un experimento futuro **Fase 0**, sin importar ejecutores a KT-002/3. No copiar sus estrategias ni conclusiones.
3. **Mantener test real upstream en CI de piloto** para verificar compatibilidad de versiones fijadas antes de diseñar integración más estrecha.
4. **No desplegar integración automática de agentes sin una decisión posterior expresa del dueño**; hacerlo implicaría servidores, autorización, costos y claves de API adicionales, contrarios a la preferencia actual por controlar desde chats.

## Falta para afirmar que está completamente integrado
- Ejecución OpenHands de tarea de desarrollo real con LLM mock (solo se compiló interfaz).
- Integración del grafo real de TradingAgents con un modelo local/mock de ORION y un canal de informes versionados **sin tocar ciencia protegida**; por ahora solo se ejecutó su test original.
- Revisión de seguridad profunda de dependencias/paquetes de terceros, licencias transitorias, permisos y aislamiento con control de red.
- Medir costo/beneficio frente a usar directamente Claude/ChatGPT y no duplicar componentes.
- Veredictos independientes Desconfiado/Vigía, 3 informes reales, seguimiento KT-002: **bloqueos científicos del Plan Maestro sin sustituir.**

**Decisión provisional:** infraestructura de evaluación y supervisión *operativa y probada*, adopción selectiva pendiente de una mejora concreta validada. No declarar autonomía productiva o investigación científica cerrada.
