# Kronnos — Scripts deterministas en evaluación
Rama: feature/scripts-deterministas-2026-10-28; NO integrado en master. No modifica corridas ni workflows vigentes.

- tools/recolector_mercado.py: recolector manual HTTPS JSON con tamaño, tiempos, reintentos, SHA-256 y guardado sin sobrescribir. NO programado y NO ejecutado contra una fuente real; sin acceso por defecto. La URL debe ser aprobada y revisada antes de usar. No es un sustituto de ingesta institucional.
- tools/validador_datos.py: revisa CSV UTC/bid/ask/spread; sale código 2 en errores; NO modifica datos originales. Los datos antiguos podrían fallar y requieren análisis, no corrección silenciosa.
- tools/evaluador_modelos.py: calcula únicamente exactitud binaria descriptiva para entradas proporcionadas; booleanos preregistered/matured son declarativos, NO son verificación real del historial Git. Promoción siempre BLOQUEADA. No calcula DSR.
- tools/auditor_gerencia.py: SHA-256 de archivos explícitos, manifiesto JSON y resumen en GITHUB_STEP_SUMMARY. El hash por sí mismo no constituye sello externo ni custodia inmutable.
- tests/test_scripts_deterministas.py y workflow pruebas-scripts-deterministas.yml: pruebas stdlib aisladas. Solo pull_request o manual, nunca cron ni trading.
- No instalar paquetes externos ni sistemas de BlackRock o JPMC. Código de adaptación original.
- Próximo paso antes del merge: ejecutar tests, revisar seguridad del recolector (allowlist de destinos, redirects y redes privadas), y añadir comprobación real de preregistro con historial Git antes de usar el evaluador para decisiones.
- Separación deliberada: informes diarios propuestos en PR #45; estos cuatro scripts no se acoplan a KT-002 ni ATLAS hasta aprobación específica.
