# Piloto autorizado — OpenHands + TradingAgents (etapa A)

**Fecha:** 2026-10-22 · **Autorización:** dueño aprueba evaluar ambas plataformas en un piloto aislado.  
**Estado:** A = verificación estática automatizada; B = pendiente de evaluación de seguridad antes de ejecutar sistemas externos.

## Objetivo y límites
Determinar si conviene reutilizar funciones ya construidas, sin reconstruir ORION ni afectar las pruebas cuantitativas existentes. El dueño continuará controlando Claude/ChatGPT desde sus chats. Este piloto **no conecta sus sesiones web**, no habilita comercio, no expone secretos y no ejecuta agentes externos.

## Código probado
- `pilot/upstreams.json`: manifiesto de versiones por SHA completo, sin etiquetas móviles.
- `pilot/orion_upstream_check.py`: descarga **únicamente README.md público** de los dos commits anclados y comprueba marcas funcionales conocidas, licencia declarada y SHA-256 de cada texto; no importa ni ejecuta sus paquetes.
- `tests/test_orion_upstream_pilot.py`: casos sintéticos para verificar la política de fuentes permitidas, commits, permisos, ausencia de ejecución externa y rechazo de datos inconsistentes.
- `.github/workflows/orion-upstream-pilot.yml`: corre en runner temporal sin secretos, GitHub token solo `contents:read`, sin cache, sin persistencia de credenciales, sin tocar datos privados.

### Upstreams fijos
| Candidato | Git SHA observado al aprobar piloto | Licencia (metadata GitHub) | Para qué |
|---|---|---|---|
| [OpenHands](https://github.com/OpenHands/OpenHands) | `542aa917de74d24d3f1eb7abd86622097bfff21f` | MIT | Agent Canvas, coordinación de herramientas y agentes de programación |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | `e8f5503e9b86d5c2710b0c76b1f686703968c9df` | Apache-2.0 | Analistas, deliberación y supervisor de riesgo; solo patrón de estudio |

Consulta read-only local cuando haya Internet:
```bash
python -m unittest discover -s tests -p 'test_orion_upstream_pilot.py' -v
python pilot/orion_upstream_check.py --live-readmes
```
El reporte de éxito de A indica **solo que se verificaron documentos upstream**; no constituye una instalación funcional, inspección exhaustiva del código ni una certificación de seguridad.

## Matriz de compatibilidad y decisión
| Capacidad | ORION actual | OpenHands según README | TradingAgents según README | Resolución de esta fase |
|---|---|---|---|---|
| Panel móvil de estado | funciona como supervisor | Canvas de agentes programadores | no es el foco principal | conservar ORION |
| Integración agentes programadores | control desde chats manuales | soporta CLI/ACP como Claude Code y Codex | no es su finalidad | idea reutilizable, no conectar sesiones web |
| Equipo financiero jerárquico | roles declarados e independientes | genérico | roles financieros, investigación y riesgo | estudiar patrones, no otorgar veto automático |
| Auditoría independiente | reglas obligatorias | no verificada en A | no sustituye Desconfiado | mantener auditor propio |
| Backtest / experimento | KT-002/003 activos y congelados | no aplicable a propósito | trae caminos de decisiones y backtesting | **bloqueado en experimentos existentes** |
| Permisos, costo, secretos | sin backend de agentes | requiere seguridad e infraestructura adicional para usarse | requiere proveedores/credenciales para uso real | ninguna clave agregada |
| Trading real | prohibido | no aplicable | puede incorporar decisiones de trading | **prohibir broker, órdenes, API de ejecución** |

## Próxima etapa B — piloto funcional SOLO aislado
No se ha instalado ningún upstream. Antes de instalarlo:
1. Crear un **repositorio o runner desechable separado**, con red y secretos deshabilitados, acceso nulo a KT-002/003, Github Pages, broker y APIs privadas.
2. Auditar versión específica, dependencias, scripts de instalación, superficie de comandos, licencias y posible telemetría antes de dar permiso de ejecución.
3. OpenHands: ensayar en un repositorio sintético una tarea trivial de edición y revisión PR con un motor local/mock, sin Claude/ChatGPT privados. Demostrar aislamiento, evidencia, reversión y consumo.
4. TradingAgents: ensayar un ciclo únicamente ficticio con dataset sintético y respuesta no operable (análisis/riesgo/rechazo); **no invocar señales ni órdenes reales**.
5. Documentar resultados con outputs y hashes, costos reales observados, fallos y límites; decidir por separado si incorporar alguna pieza de UI/reportes. Es obligatorio mantener reproducibilidad y veto humano.

## Criterios de aceptación
- Etapa A: README fijados por SHA obtenidos, hashes generados y pruebas sintéticas en verde; si falla red o documentación, decir `NO VERIFICADO`.
- Etapa B: demostración funcional ejecutada en sandbox desechable, sin secretos ni datos reales y sin tocar el repositorio científico. **No marcar B concluida con un informe documental.**
- Adopción: solo tras aprobación técnica y de seguridad de una integración concreta, con PR separado y reversión documentada. No instalar ni desplegar automáticamente por el mero hecho de completar A.

## Reversión
Eliminar los archivos `pilot/`, prueba y workflow en un PR de reversión. No se alteraron ejecutores existentes ni Pages, por lo que no hay migración que revertir.

**Prohibiciones:** KT-002, KT-003, holdout, scripts prospectivos, `CLAUDE.md`, `AGENTS.md`, Desconfiado, normas de riesgo, trading real, secretos, credenciales Claude/ChatGPT y segundo publicador GitHub Pages.
