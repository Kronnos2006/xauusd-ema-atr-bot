# Informe del gerente — Reparación de ORION (guardia y KT-002)

Fecha: 2026-10-23 (noche, Costa Rica). Orden: "Orden maestra — reparación y sincronización de ORION" del propietario.
**Operated-By:** Claude (Anthropic) · **Requested-By:** propietario · **Review-Status:** pending (revisión cruzada de ChatGPT) · **Validation:** ver §4.
Rama: `fix/orion-guardia-kt002-20261023` (sin fusionar). Nada se fusionó a `master` ni se alteró ninguna automatización activa.

Clasificación: ✅ corregido y verificado · 🟡 corregido, pendiente de integración · 🔎 diagnosticado, pendiente · ⛔ bloqueado · ❔ no verificado.

## 1. Estado general
KT-002 sigue midiendo sin pérdida de datos desde el 21-oct. Los problemas encontrados son **operativos** (vigilancia y datos de mercado), no de la medición. Las reparaciones están escritas y probadas en rama; **no hay evidencia real de funcionamiento hasta integrarlas**, así que ningún problema se declara cerrado.

## 2. Problemas y causas raíz
| # | Problema | Causa raíz (evidencia) | Estado |
|---|---|---|---|
| P1 | La guardia no corre cada hora | GitHub retrasa el cron `37 * * * *` en este repo: 14 corridas entre el 21-oct 14:36 y el 23-oct 22:35, separadas **4–6 h** (Actions, workflow `guardia.yml`). | 🟡 |
| P2 | `tendencia.json`, `btc_1d.json`, `btc_4h.json` sin actualizar desde el 22-oct | El paso de velas solo corría si la guardia caía **exactamente a las 00 UTC** (`[ "$(date -u +%H)" = "00" ]`); con el cron retrasado nunca pasó (corridas a las 01:47 y 01:52). Solo se actualizó con corridas manuales. Falla silenciosa: la corrida igual salía verde. | 🟡 |
| P3 | Éxitos que ocultaban fallas | Paso de spread con `continue-on-error` y `|| true`; el push podía fallar sin aviso. | 🟡 |
| P4 | Cancelación indebida de KT-002 (23-oct) | El **vigía** canceló la corrida **#19** (`39935415378`) a las 12:39:14 UTC por "colgada ~2 h 45 sin avance", pero esa corrida había registrado a las 10:07, 10:08, 11:07 y 12:07 UTC. Usó solo el tiempo transcurrido. No se perdieron datos (la #20 registró 12:40). | 🟡 |
| P5 | Otras corridas "cancelled" de KT-002 (#3, #10, #23) | Nunca arrancaron (sin jobs): **GitHub las canceló por la regla de concurrencia** (un solo pendiente por grupo `kt002`). No es error ni pérdida. | ✅ (diagnóstico) |
| P6 | Incidente del 20-oct | No fue KT-002: fue la cancelación del intento 1 de **KT-003** (run `39450116803`), ya documentada en la Nota E de `docs/KT-003_registro_historico.md`. | ✅ (ya documentado) |
| P7 | Reparador sin ejecución | **0 evidencias**: ningún commit "Reparación:", ninguna mención en `decisiones.md`, ningún issue `guardia` creado. Existe solo como definición (`.claude/agents/desarrollo-reparador.md`). | 🔎 |
| P8 | Prueba `test_orion_google` falla | Falta `fastapi` en el entorno de Claude (ImportError); ajeno a esta reparación. | ❔ |

## 3. Reparaciones (rama, sin integrar)
1. **`tools/guardia_salud.py`** (nuevo): lógica pura de decisión para KT-002 y de frescura de datos. No existe la acción "cancelar". Una corrida `in_progress` con registro en las últimas 130 min está sana aunque dure horas; sin registro → **alerta** (escalar, no cancelar); en cola >120 min → alerta; nada vivo y fallida o sin registro >75 min → relanzar; solape cada 4 h sin duplicar. 🟡
2. **`guardia.yml` rediseñada:** deduplicación (<40 min desde la última sana), decisión con el módulo, spread sin ocultar errores, velas **cuando `tendencia.json` tiene >20 h** (ya no depende de la hora), publicación única con reintentos que falla en rojo, y paso final de **salud**: verde solo si tendencia (<26 h), spread (<30 min) y registro de KT-002 (<130 min) están verificados; si no, abre/actualiza el aviso `guardia` y termina en rojo; cuando todo vuelve a estar sano, **cierra el aviso con el enlace de la corrida**. 🟡
3. **`kt002.yml`:** solo agrega permiso `actions: write` y, al final de cada vuelta horaria, dispara la guardia (`origen=kt002`); si eso falla deja un aviso y sigue. **No toca `tools/kt002_prospectivo.py`, el minuto 7, el modelo ni los registros.** 🟡
4. **Vigía v2** (`docs/ops/VIGIA_PROMPT_v2.md`) y agentes `vigia-datos` / `desarrollo-reparador`: prohibición absoluta de cancelar, mismas reglas que la guardia, reparador en rama + PR con revisión cruzada y confirmación de recuperación. La **tarea programada del vigía no se modificó** (requiere tu aprobación). 🟡
5. **CLAUDE.md:** modelo de colaboración ORION (propietario, ChatGPT, Claude, Codex, gerente) agregado sin borrar el texto original; regla de no cancelar. 🟡

## 4. Pruebas
- `tests/test_guardia_salud.py`: **15/15 OK** (nunca cancela; incidente del 23-oct reproducido como "ok"; viva sin registros → alerta; solape sin duplicar; cola corta/larga; fallida → relanzar; parado → relanzar; frescura con archivo viejo/faltante; tendencia vieja sin depender de la hora; CLI).
- Suite completa: 58 OK, 1 error previo (P8).
- `actionlint` 1.7.7 sobre `guardia.yml` y `kt002.yml`: sin errores. `bash -n` y compilación de los bloques Python: OK.
- Simulación local del paso de salud con datos reales del repo: detectó tendencia de 2 705 min y spread de 124 min y un paso fallido (esperado).
- **No probado en GitHub real** (requiere integrar). Ninguna prueba canceló ni tocó corridas productivas.

## 5. KT-002 (integridad verificada con `data/kt002/predicciones.csv`, 2026-10-24 00:07 UTC)
73 filas, 73 bases únicas, **0 duplicadas**, objetivo siempre a 4 h, 69 vencidas con aciertos **recalculados sin discrepancias**; `resumen.json` coincide (73/69). Huecos: los 3 conocidos (20-oct 13→17, 20-oct 21→21-oct 01, 21-oct 05→10 UTC) = 10 horas omitidas, todas antes del arreglo de observabilidad. Sin solape n=16: Kronos 9, siempre sube 7, TimesFM 6, KT-001 5. **No hay ventaja estadística demostrada** (hacen falta ~100 para una lectura y ~780 para distinguir 55 % de 50 %).

## 6. Guardia y mercado
Hoy: guardia verde pero con P1–P3. `tendencia.json` generado 2026-10-22 03:34 UTC (velas al 21-oct). Spread: 11 filas, última 22:35 UTC; diferencia compra/venta ≈ 0,00001 %.

## 7. Vigía
Tarea programada cada 4 h (`37 */4 * * *`), modelo Sonnet. Incidente P4 documentado. v2 lista para aplicar.

## 8. Reparador
Estado real: **definición documental, sin ejecuciones verificadas** (P7). Mecanismo propuesto: guardia detecta → issue `guardia` con evidencia → vigía convoca al reparador → rama + PR + pruebas → revisión cruzada → integración aprobada → la guardia siguiente verifica y cierra el aviso. No se crean agentes ni procesos nuevos.

## 9. Costos
La guardia pasa de ~5 corridas/día a ~24 (minutos gratis de Actions en repo público). El vigía de Claude puede bajar a cada 6–8 h cuando la guardia esté verificada (ahorro de tokens). La prueba de fastapi requiere instalar dependencias solo si se quiere esa suite.

## 10. Riesgos y pendientes
- Integrar la rama tras la revisión de ChatGPT (tu aprobación).
- Aplicar el vigía v2 a la tarea programada (tu aprobación). **Hasta entonces el riesgo de otra cancelación sigue vivo.**
- Primera semana tras integrar: confirmar corridas horarias reales, cierre automático de avisos y `tendencia.json` diario.
- Si el disparo desde KT-002 se ve bloqueado por permisos, alternativa: el vigía dispara la guardia.

## 11. Evidencias
Commits de esta rama y PR enlazados en la issue #31. Corridas citadas: guardia `40034590053`, `40005297361`, `39964033317`; KT-002 #19 `39935415378`, #20 `39954911090`, #23 `40031000348`.

## 12. Opinión del gerente
La medición está sana; lo frágil era la vigilancia: dependía de un reloj que GitHub no respeta y declaraba éxito sin comprobar nada, y el vigía tomó una decisión destructiva con un solo dato. Con la lógica única probada, la salud verificada y la prohibición de cancelar, el sistema queda más simple y auditable. Recomiendo integrar rápido el punto 4 (vigía v2), porque es el único riesgo activo sobre datos reales.
