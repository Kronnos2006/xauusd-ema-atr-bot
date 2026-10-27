# Kronnos / ORION — política operativa (2026-10-27)

Decisión del propietario: Claude deja de participar en la operación, coordinación, ejecución y revisión del proyecto. ChatGPT es el coordinador designado, sujeto a validación de evidencia y aprobación del propietario.

## Reglas
- No enviar nuevas órdenes ni tareas a Claude ni activar Claude Code, sus hooks, agentes o automatizaciones.
- No fusionar PRs de Claude sin nueva revisión independiente y autorización explícita del propietario. PR #44 se cierra sin fusión.
- Conservar commits, hashes, datos, resultados, pruebas y evidencia histórica; no reescribir ni borrar el historial por motivos cosméticos.
- Auditar y retirar tokens, secretos, claves SSH, OAuth Apps, GitHub Apps, colaboradores y runners que concedan acceso a Claude/Anthropic. Revocar y rotar credenciales desde la cuenta del propietario; no afirmar que está completado sin evidencia.
- Migrar cualquier workflow dependiente de Claude a herramientas controladas por el propietario antes de desactivarlo; mantener pruebas prospectivas KT-002 y bloqueos ATLAS. No utilizar credenciales nuevas sin aprobación.
- Mantener `promocion_permitida=False`, sin trading real ni promoción de hipótesis sin controles confirmatorios y aprobación del propietario.
- Autoría por evidencia: nunca atribuir a ChatGPT el trabajo histórico de Claude; no eliminar trazabilidad ni sellos.

## Estado de retiro
Esta política documenta la decisión, no certifica que accesos externos hayan sido revocados. Pendiente auditoría de GitHub Settings (collaborators, secrets, deploy keys, Actions, GitHub Apps), dispositivos locales (Termux/Claude Code) y toda otra cuenta conectada.

Operated-By: ChatGPT
Requested-By: propietario, 2026-10-27
