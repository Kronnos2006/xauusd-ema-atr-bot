# KRONNOS — Política de automatización primero (28-10-2026)

## Mandato
1. **Scripts antes que IA**: operaciones rutinarias se ejecutan con Python (stdlib cuando sea posible), comandos Git, reglas, GitHub Actions, funciones estadísticas deterministas y los modelos locales ya aprobados.
2. **IA por excepción, nunca por defecto**: no invocar LLMs en cron, guardia, ingestión, cotejo de predicciones, DSR, cálculos financieros, sellos o informes periódicos. Solo revisión de anomalías no resueltas por reglas o análisis estratégico solicitado, con presupuesto y autorización explícitos.
3. **Sin operar dinero real**. La investigación y simulación permanecen separadas de ejecución en vivo. Ninguna promoción se automatiza sin barreras de validez y revisión humana.
4. **Conservar trazabilidad**: no borrar histórico de autores/herramientas. Sin nuevas dependencias, claves, tareas o coordinación con Claude.
5. **Fallo seguro**: datos ausentes, estado desconocido, sellos no verificables y fold con menos de 30 operaciones = NO VALIDADO. No extrapolar.
6. **No interferencia**: no reiniciar, cancelar o reprogramar KT-002 desde la guardia. La guardia únicamente observa y alerta.
7. **Evidencia Git**: cada informe muestra fuentes, hora UTC, SHA y distinción entre comprobado, pendiente y no disponible.

## Rutas de implementación
- Reutilizar los pipelines existentes antes de crear otros.
- Consolidar procesos horarios compatibles para evitar duplicación, manteniendo independencia de evidencias si el protocolo lo exige.
- Guardar secretos únicamente en GitHub Secrets con permisos mínimos y token read-only para informes.
- Cachear dependencias/datos cuando proceda; medir tiempos, minutos Actions, API y tokens de IA = 0 en ruta normal.
- Guardar informes como artefactos; evitar commits por cada informe si generan loops innecesarios.
- Mantener los bloqueos estadísticos ATLAS PR #42 sin declarar promoción hasta superar DSR ≥ 0.95, mínimo 30 operaciones/fold, contraste con/sin fold dominante y preregistro temporal comprobado.
- H3/H4 continúan bloqueadas hasta superar las mismas barreras correspondientes.

## Criterios de aceptación
- Corrida rutinaria sin invocar proveedores de LLM, con registro explícito de 0 llamadas.
- Informe generado por script, con pruebas de funcionamiento y sin inventar métricas.
- Sin modificación de schedules actuales, pipeline KT-002, trading real o sellos externos en este PR.
- Revisión de costos y de permisos antes de activar una nueva automatización.
