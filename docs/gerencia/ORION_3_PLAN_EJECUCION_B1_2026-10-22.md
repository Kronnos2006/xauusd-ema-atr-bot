# ORION 3.0 — Ejecución del plan, etapa B1

**Fecha:** 2026-10-22. **Estado:** ejecutable mock, no motor de OpenHands/TradingAgents todavía.

## Objetivo
Probar los **contratos mínimos** que necesitamos antes de integrar un agente ajeno: una tarea técnica con alcance de archivos controlado; una revisión financiera sintética; veto independiente no anulable; evidencia verificable y reversión. El dueño conserva control por sus chats, no hay OAuth, servidores, API externas ni trading real.

## Qué se ejecuta realmente
`.github/workflows/orion-pilot-b1.yml` hace checkout parcial SOLO de `pilot/orion_mock_contract.py` y sus pruebas; confirma la ausencia de `data/kt002`, `data/kt003`, visor de Claude y workflow de KT-002, luego corre:
- `python -m unittest discover -s tests -p 'test_orion_mock_contract.py' -v`
- `python pilot/orion_mock_contract.py`

El programa crea un directorio temporal y redacta un documento ficticio en `workspace/nota.txt`, registra SHA-256, genera un análisis sobre **FAKEBTC** (inventado), exige revisión por riesgo y registra su veto. Todo queda representado mediante eventos con hashes encadenados. Al finalizar se destruye el espacio temporal. **No crea PR real ni ejecuta programas de terceros.**

## Criterios de aceptación B1
1. Pruebas verdes.
2. Alguien que intente escribir `data/kt002`, `data/kt003`, visor de Claude, workflows o fuera del workspace recibe `PermissionError`.
3. Ningún parámetro admite órdenes reales.
4. El veto bloquea entrega, incluso cuando el supuesto desarrollador completó su documento.
5. Modificar un evento después de crearlo invalida su hash de cadena.
6. Datos restringidos ausentes en el checkout de CI.

**Limitación:** hashes encadenados en memoria prueban detección de cambios casuales, **no certifican firmas inmutables ni identidades externas**. Los roles son simulados por un script y **no son instancias reales de Claude ni ChatGPT**.

## Estado del plan global
- **A:** validación documental de upstream OpenHands/TradingAgents, CI verde.
- **B1:** protocolo funcional mock ejecutado en Actions con casos sintéticos (pendiente de CI hasta su corrida correspondiente).
- **B2:** inspección de scripts/dependencias y análisis de amenazas de cada upstream fijado; **no completada**.
- **B3:** ejecutar **OpenHands real** en entorno desechable y sin credenciales, solo después de aprobar B2.
- **B4:** ejecutar **TradingAgents real** con dataset sintético y proveedor simulado/offline tras aprobar B2; no conectar brokers, capital ni modelos reales.
- **C:** comparar costo operativo, seguridad, utilidad y mantenimiento para decidir una integración opcional en ORION, por PR separado.

## Condiciones de integración
Cero regresiones del panel y del visor de Claude. Auditor Desconfiado y jefe de riesgo mantienen veto original, independiente del prototipo. No se edita ningún archivo de los experimentos KT-002/KT-003. Los pilotos no son evidencia de ventaja estadística ni de viabilidad económica.

## Enlaces
- [Plan Maestro](PLAN_MAESTRO_EJECUCION_2026-10-22.md)
- [Piloto A de upstreams](PILOTO_OPENHANDS_TRADINGAGENTS_2026-10-22.md)
- [Repositorios comparados](REPOS_SIMILARES_ORION_LAB_2026-10-22.md)
