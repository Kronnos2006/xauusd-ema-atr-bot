# Plan maestro de ejecución — Laboratorio cuantitativo autónomo y auditado

**Fecha:** 2026-10-22 (Costa Rica)  
**Patrocinador:** dueño del proyecto. Autorización conversacional del 2026-10-22 para ejecutar la visión por etapas.  
**Coordinación de esta revisión:** ChatGPT, revisor externo.  
**Repositorio:** Kronnos2006/xauusd-ema-atr-bot.

## Objetivo verificable
Lograr un laboratorio de investigación en el que la adquisición de datos, las mediciones descriptivas, la auditoría técnica, los informes y el seguimiento sean trazables, recuperables y reproducibles. **No se promete obtener una estrategia rentable.**

## Restricciones y autoridades
- Investigación sin capital real ni órdenes. No activar trading ni cuentas operativas.
- No alterar KT-002, KT-003, sus parámetros, código, datos históricos publicados ni reglas pre-registradas mediante esta autorización genérica; cualquier cambio en un experimento activo exige su procedimiento específico y aprobación exclusiva del dueño.
- No abrir holdouts ni reescribir registros, no force push.
- Hipótesis: Fase 0 antes de Fase 1; el dueño define Fase 1; auditoría independiente, walk-forward y costos en diseños nuevos.
- El gerente dirige operaciones pero no invalida los vetos de auditoría/riesgo ni modifica el trabajo independiente del analista.
- Los informes de ChatGPT son **externos**, no equivalen al veredicto del auditor `desconfiado`.
- Cambios de software nuevos: preferir rama, pruebas y pull request; sin fusionar código de alto impacto sin revisión.

## Fase 1 — Auditoría verificable (prioridad actual)
**Responsables propuestos:** operaciones, vigía de datos, auditor independiente; coordinación del gerente.
- Evidencia: [auditoría externa](../coordination/AUDITORIA_EXTERNA_2026-10-22.md), [seguimiento #1](https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/1).
- Ya verificado en la lectura del CSV: 37 filas, 33 puntuadas, 0 bases duplicadas, 24/24 bases en la última ventana de 24 horas hasta 2026-10-22T11:00Z, 0 evaluaciones registradas antes del cierre objetivo.
- **Pendiente:** historial real de GitHub Actions, logs de fallos, consistencia de publicación y veredicto del auditor.
- **Cierre:** evidencia rastreable con hashes/URLs/IDs, problemas categorizados, auditor independiente firma su veredicto. No inferir resultados de producción solo del código.

## Fase 2 — Confiabilidad de operaciones
**Responsables propuestos:** jefe-operaciones, vigía y desarrollo; auditor revisa.
- Diseñar diagnóstico no intrusivo para interrupciones de inferencia, huecos, commits no publicados, concurrencia y alertas de la guardia.
- Añadir tests de integridad en un entorno aislado, sin afectar las corridas o resultados actuales.
- Antes de desplegar cualquier cambio a `kt002.yml`, `guardia.yml` o al script activo, identificar si cambia el experimento y seguir aprobación correspondiente.
- **Cierre:** tests documentados, recuperación verificada y diagnóstico de fallos sin duplicados.

## Fase 3 — Gobierno del equipo y calidad de informes
**Responsables propuestos:** gerente, documentación; revisión separada por auditor/analista/riesgo.
- Cada afirmación externa de mercado con fuente, URL, UTC de observación, UTC de consulta y caducidad explícita.
- Informes deben distinguir: confirmado, provisional, inconsistente, no verificado.
- Cada decisión operativa con responsable, evidencia, revisión, estado y motivos. Las decisiones reservadas se escalan.
- No editar el análisis independiente; solicitar al propio analista anexos versionados.
- **Cierre:** comprobar varios informes consecutivos frente a un checklist acordado, sin sustitución de evidencia por opiniones.

## Fase 4 — Medición prospectiva KT-002
- Mantener configuración fija: Kronos, TimesFM, KT-001 y benchmark «siempre sube».
- Métrica primaria interpretativa: subconjunto no solapado, con incertidumbre y dependencia residual reconocidas; mostrar también cobertura y horas omitidas.
- Evitar selección adaptativa por régimen u optimización retrospectiva.
- **Cierre:** informe descriptivo con muestra y limitaciones suficientes para decidir, no prueba automática de rentabilidad.

## Fase 5 — Investigación de hipótesis nuevas
- Registrar variantes y potencia sobre datos reales en Fase 0 antes de backtests.
- Fase 1 solo con definición explícita del dueño. Walk-forward anclado, costos, DSR, multiplicidad, fold dominante y mínimo 30 trades/fold.
- Comparar referencia ingenua y rentabilidad neta. Registrar tanto fracasos como hallazgos.
- **Cierre:** aceptar/rechazar con evidencia y auditoría, nunca declarar una ventaja por tasa de acierto aislada.

## Fase 6 — Oficina del Dueño
- Preparar diseño del tablero con salud técnica, cobertura de datos, experimentos, evidencias, revisiones, riesgos y escalaciones.
- La Oficina privada en Claude requiere su acceso/conector adecuado; GitHub por sí solo no puede certificar su estado.
- **Cierre:** trazabilidad entre cada mensaje del tablero, los archivos fuente y decisiones autorizadas.

## Forma de ejecución
1. Leer evidencia existente; no repetir experimentos.
2. Registrar cada nueva tarea en un issue con responsable sugerido y condición de cierre.
3. En software, crear rama y PR; exigir pruebas y revisión independiente antes de fusionar.
4. Reportar estado **hecho / en curso / bloqueado / no verificado**, sin declarar terminado lo no inspeccionado.
5. Detener y escalar casos reservados exclusivamente al dueño.

## Qué significa éxito
Una plataforma técnica auditable que detecta fallos, conserva evidencia y permite decidir con rigor si existe o no una ventaja operable. Un resultado científico negativo, bien demostrado, también es un resultado válido.

## Estado de ejecución inicial
- [x] Auditoría documental en `docs/coordination/AUDITORIA_EXTERNA_2026-10-22.md`.
- [x] Issue de hallazgos #1.
- [x] Comprobación retrospectiva de integridad básica de las 37 filas publicadas (lectura, sin nuevas inferencias).
- [ ] Revisión de logs de Actions y auditoría independiente.
- [ ] Tests adicionales de integridad en rama y PR.
- [ ] Anexos verificables del analista.
- [ ] Diseño e integración de la Oficina del Dueño.
