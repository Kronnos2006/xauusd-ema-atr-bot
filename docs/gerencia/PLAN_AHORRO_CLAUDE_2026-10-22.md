# Plan de ahorro de uso de Claude — 2026-10-22

**Propósito:** quitar trabajo repetitivo a los agentes Claude, sin bajar estándares estadísticos, sin alterar la independencia del auditor ni de riesgo, y sin tocar la medición KT-002.

## Distribución de responsabilidades
| Actividad | Ejecuta | Usa Claude |
|---|---|---|
| KT-002: inferencia y registro | GitHub Actions existente | No |
| Guardia y colección de velas | GitHub Actions existente | No |
| Tests sintéticos de integridad del CSV | GitHub Actions, PR #3 | No |
| Revisión de código, informes técnicos, PRs | ChatGPT a pedido del dueño / desarrolladores | No |
| Auditoría metodológica independiente y vetos | `desconfiado` | Sí, en hitos |
| Decisiones operativas y escalaciones | `gerente` | Sí, breve |
| Interpretación especializada de mercado | `analista` y ayudantes | Sí, solo cuando aporta valor; no cambiar sus reglas sin autorización |
| Aprobación de Fase 1 y decisiones reservadas | Dueño | Según el caso |

## Política de eficiencia propuesta (no impuesta a agentes independientes)
1. Un solo resumen breve al dueño; detalles y enlaces en GitHub.
2. No convocar agentes para repetir conteos, estado de corridas, hashes o fórmulas programables.
3. Agrupar solicitudes para un mismo jefe; no repetir el mismo contexto en varias sesiones.
4. Conservar resultados en archivos e issues, con identificador de commit, para evitar pedir análisis desde cero.
5. Escalar al auditor independiente solo ante diseños nuevos, problemas de integridad, resultados terminados o revisión periódica ya autorizada.
6. No pedir a Claude investigación de mercado que no tenga fuente con URL y fecha; cuando falte evidencia, etiquetar **no verificado** y evitar reintentos excesivos.
7. El gerente aplica su propia política `docs/gerencia/INFORME_DIARIO.md`. **No se modifican instrucciones ni frecuencia del analista independiente ni del auditor por este documento.**

## Implementación inmediata
- [x] Publicar auditoría externa y seguimiento: Issue #1.
- [x] Preparar inspector read-only y pruebas sintéticas en PR #3.
- [x] Preparar comprobación CI de solo lectura en PR #3, pendiente de ejecución en GitHub.
- [ ] Ver resultados del CI, corregir pruebas que fallen y solicitar veredicto externo.
- [ ] Tras revisión, estudiar activación de comprobaciones periódicas de integridad sin agentes.
- [ ] Evaluar consumo real del plan de Claude durante varios días y ajustar únicamente las convocatorias que el gerente puede cambiar.

## Advertencias
- GitHub Actions también tiene cuotas de cómputo; usar comprobaciones ligeras y disparadas por evento antes que más jobs permanentes.
- ChatGPT no comparte sesión, cuota ni autonomía con Claude y no puede ejecutar automáticamente sus subagentes privados.
- Nada de capital real, órdenes, modificaciones de modelos ni holdouts; no declarar edge por acierto direccional.
- La propuesta no elimina la necesidad de auditoría independiente ni modifica la jerarquía de autorizaciones.

## Objetivo de aceptación
Menos convocatorias repetitivas a Claude, más evidencia automática y ningún descenso de calidad o controles. Medir número de convocatorias y razones antes/después; no inventar ahorro porcentual.
