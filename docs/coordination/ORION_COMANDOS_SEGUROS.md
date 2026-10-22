# ORION — Control operativo comprobable desde celular

## Comandos disponibles desde GitHub Actions
Desde ORION → Operaciones → Ejecutar verificación en GitHub, pulsar "Run workflow" o "Ejecutar flujo de trabajo" con sesión GitHub iniciada y rama master. Elegir una acción:
- **estado**: informe de estado local de ORION y última muestra versionada.
- **modelos**: resumen descriptivo predeclarado de KT-002; no rentabilidad.
- **integridad-basica**: compara registro y resumen de KT-002; si hay discrepancias, falla.
- **publicacion**: comprueba que los dos visores (ORION y Claude) conservan fuentes y publicador conjunto.

Las acciones son una lista cerrada definida en tools/orion_comandos.py. El workflow no tiene credenciales propias y requiere solo permiso contents:read. Se ejecuta en GitHub con la autenticación propia de quien tenga autorización para lanzar Actions; el sitio Pages no ejecuta código servidor.

## Resultados
Cada ejecución deja el resultado JSON en el registro del job y en su resumen. Si una comprobación falla, aparece fallo en Actions; ninguna reparación se aplica automáticamente. ORION consulta el estado público de Actions para mostrarlo, pero no se atribuye la ejecución a un agente sin evidencia.

## Límites de acceso y seguridad
- Nada de órdenes o capital real.
- Nada de editar datos, parámetros, holdouts, predicciones o agentes.
- Nada de invocar Claude ni ChatGPT; no hay acceso autenticado a sus sesiones privadas.
- Ningún test verde sustituye la revisión independiente.
- Si se requiere una acción fuera de esta lista, abrir issue [ORION] y seguir el procedimiento de revisión/PR. Para conectar agentes remotamente se requieren credenciales gestionadas en backend, autorización, límites de cuota, logs, y un adaptador oficial compatible.

## Protección Claude/ChatGPT
Cada operador usa issues y PR propios, sin force push ni sobrescritura de archivos ajenos. Visor Claude sigue en /visor y ORION en raíz; solo una publicación Pages. Leer docs/coordination/ORION_PROTOCOLO_COOPERACION.md.
