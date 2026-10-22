# ORION — Contrato de cooperación operativa de Claude y ChatGPT

Este documento registra cómo gestionar solicitudes sin modificar las reglas de Claude, ChatGPT o del auditor independiente.

## Capacidades actuales
- Un único publicador de Pages contiene ORION y el visor de Claude.
- ORION muestra métricas publicadas, GitHub Actions, incidencias y tareas públicas con prefijo [ORION].
- GitHub Issues permite solicitar trabajo con sesión autenticada.
- Una solicitud NO inicia automáticamente agentes ni equivale a una aprobación.

## Procedimiento para ambos operadores
1. Consultar Issues con prefijo [ORION] y revisar estado y evidencia.
2. Buscar PR abiertos y commit base antes de editar.
3. Respetar propiedad de rutas descrita en docs/coordination/ORION_PROTOCOLO_COOPERACION.md.
4. Al tomar una tarea, comentar INICIO: operador real, archivos previstos, commit base y riesgos.
5. Crear rama individual, PR con pruebas, alcance y reversión. No usar force push ni editar ramas del otro operador.
6. Al entregar, comentar ENTREGA: PR, CI, pasos pendientes y límites de verificación.
7. Ante edición concurrente, comentar BLOQUEADO POR CONFLICTO, enlazar ambos PR y resolver sin eliminar funciones.
8. Conservar independencia de Desconfiado, Riesgo y Analista. No aprobarse a sí mismo ni fingir evidencia de sesiones ajenas.
9. Cerrar solicitud solo después de integración, revisión necesaria y verificación operativa.

## Límites obligatorios
Ninguna solicitud pública autoriza órdenes ni dinero real, cambios a KT-002 o KT-003, datos científicos, preregistros, holdouts, reglas, secretos ni Oficina privada. No publicar datos privados en Issues o Pages.

GitHub Pages es estático: no puede activar ni autenticar sesiones privadas de Claude/ChatGPT. El control directo requiere conectores autorizados y servicio autenticado con mínimo privilegio, confirmación por acción y bitácora de eventos. Esta capacidad NO está implementada.

## Aceptación
Verificar publicación conjunta, cola [ORION] de issues con enlaces reales, acceso a plantilla autenticada, CI y ninguna modificación de archivos científicos protegidos.
