# Fase 3 — Control de calidad de informes sin gastar cuota de Claude

**Fecha:** 2026-10-22. **Estado:** propuesta en PR, no modifica las conclusiones del analista independiente.

## Propósito
Convertir los informes diarios en piezas comprobables sin pedir rondas adicionales de Claude. Una fuente debe permitir revisar por terceros qué se afirmó, cuándo se observó, de dónde viene y si sigue siendo vigente.

## Evidencia requerida por afirmación
| Campo | Obligación |
|---|---|
| Afirmación concreta | Dato, activo/unidad y período |
| Fuente | Organización o documento original |
| URL directa | Enlace exacto al dato, no portada |
| Fecha de observación (UTC) | Cuándo corresponde el dato |
| Fecha de consulta (UTC) | Cuándo fue consultada la fuente |
| Estado | CONFIRMADO, PROVISIONAL, INCONSISTENTE, NO VERIFICADO |
| Comparación | Si existe discrepancia entre fuentes, mostrar ambas sin resolverla arbitrariamente |
| Caducidad | Hasta cuándo conviene usar el dato para decisiones operativas |

**Regla:** un dato que no cumpla los campos mínimos se conserva como **NO VERIFICADO**, no se inventa la fuente ni se lo corrige mediante una estimación.

## Controles del informe del gerente
- [ ] Encabezado con fecha y zona horaria
- [ ] Estado de Actions con evidencia/URL o marcado no verificado
- [ ] Conteo de registros, puntuadas y muestra sin solape n
- [ ] Mención explícita de dependencia y de que acierto direccional no demuestra rentabilidad
- [ ] Señalar fallos/anomalías en vez de declarar "todo sano" basándose solo en un resumen
- [ ] Decisiones y escalaciones vinculadas a un issue, archivo o registro privado
- [ ] Número de convocatorias de Claude y razón (o no medido)
- [ ] No divulgar contenido privado de la Oficina en GitHub

## Controles del informe independiente del analista
- [ ] Cada afirmación sobre macroeconomía, ETF, ballenas, cotizaciones o mercado lleva fuente directa/UTC
- [ ] Distinguir observado de inferido; sin enlace verificable, declarar NO VERIFICADO
- [ ] Anexos versionados por el propio analista; el gerente no edita sus conclusiones
- [ ] Las discrepancias con el gerente se escalan, no se silencian

## Auditoría independiente
El control editorial/documental **NO** reemplaza `desconfiado`, no prueba edge ni modifica su protocolo. Toda conclusión científica que lo exija conserva su dictamen independiente y veto.

## Muestreo de aceptación de Fase 3
Tomar **tres informes diarios consecutivos reales** posteriores a activar este control, con enlace/commit de cada uno; registrar una ficha por informe (conforme/no conforme y fallos). Si cualquiera falla, mantener la fase en proceso y corregir el flujo sin alterar análisis independiente.

Medir convocatorias y consumo real del plan de Claude mediante registros accesibles o cifras proporcionadas por el dueño. GitHub por sí solo no conoce el consumo del plan de Claude. **No fabricar porcentaje de ahorro.**

## Límites
No se modifican `.claude/agents/analista*.md`, `.claude/agents/desconfiado.md`, jefe de riesgo, KT-002, datos, holdouts, cron privado ni Oficina del Dueño.
