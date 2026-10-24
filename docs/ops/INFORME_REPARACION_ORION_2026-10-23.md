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

## 13. Adenda 2026-10-23 18:58 (hora CR) — protección inmediata del vigía (autorizada por el propietario)
- **Aplicado en producción (solo esto):** se reemplazó el texto de la tarea programada "Vigía de datos" (`trig_01R2brVLcYG6yfbMzA5uimhm`, actualizada 2026-10-24T01:22:44Z UTC). Prohíbe cancelar, reiniciar, relanzar o re-ejecutar corridas; solo lectura (`gh run list`, `gh api` REST); ya no convoca al reparador; ante una corrida sospechosa deja una escalación `esperando` para el gerente en la Oficina. No depende de código del PR #32. Vigía v2 completo: **no activado**.
- **Riesgo de relanzamientos duplicados (corregido en la rama):** (a) la deduplicación de la guardia comparaba contra la última corrida `success`, pero una corrida saltada también termina en `success` → podía encadenar saltos (cron + disparo de KT-002 a <40 min). Ahora compara contra el último commit de `data/mercado/spread_btcusdt.csv`. (b) Había 4 relanzadores posibles (guardia, vigía, reparador, vigia-datos/jefe-operaciones con `despertar.txt` o `rerun-failed-jobs`). Ahora el **único** que relanza KT-002 es la guardia; los agentes solo avisan.
- **Referencias al propietario:** se quitó el nombre personal en archivos operativos (`gerente.md`, `CONTEXTO_PARA_OTRA_IA.md`, `VIGIA_PROMPT_v2.md`, tarea del vigía) y se usa "el propietario". Registros históricos (decisiones.md, hipótesis, estrategias) **no se reescribieron**: cambiarlos es decisión del propietario. La tarea del gerente (`trig_013FrUSspavgYpLTVTRWu46M`) todavía nombra a "Kensy": pendiente de autorización.
- **KT-002 al 2026-10-24T01:25Z:** corrida #24 en curso, registros 23:07, 00:07 y 01:07 UTC; 74 filas. Sin cambios en predicciones, datos ni criterios.
- Pruebas: 15/15 OK; actionlint OK.
## 14. Adenda 2026-10-23 21:00 (hora CR) — observaciones de la revisión cruzada de ChatGPT
| # | Observación | Resultado |
|---|---|---|
| 1 | Rama 4 commits detrás de master | Reconciliada con **merge** (sin rebase ni force): 4 commits de datos (KT-002 01:07/01:08/02:07Z, spread 01:03Z), sin conflictos; `data/` de la rama idéntico a master. |
| 2 | `git pull --rebase \|\| true` en la verificación | **Eliminado.** La verificación ya no usa la copia local. Además se corrigió `frescura ... \|\| true`: si el verificador se caía, la lista quedaba vacía y la corrida salía verde. Ahora solo es verde con rc=0 y `[]`; cualquier otro resultado es falla. En publicar se agregó `git rebase --abort` entre reintentos. |
| 3 | Comprobar contra GitHub que los datos quedaron publicados | La verificación lee `spread_btcusdt.csv` y `tendencia.json` por la API de GitHub (`contents?ref=`) y exige que la fila de spread **de esta corrida** y el `generado_utc` de la tendencia **de esta corrida** estén publicados (3 intentos). |
| 4 | La deduplicación podía ocultar fallos | Ahora solo salta la **medición de spread** (<40 min desde el último publicado). KT-002, velas, publicación y verificación corren siempre. Límite de frescura del spread 45 min (> ventana de 40) para que un salto no dé falso rojo. |
| 5 | Pruebas | `tests/test_guardia_salud.py`: **28/28 OK** (15 originales + 13 de regresión: no publicado, remoto ilegible, tendencia no publicada, pasos fallidos, ventana de dedupe, salto sin ocultar KT-002 ni tendencia, CLI). Simulación del script real del paso con `gh` falso: sano rc=0; no publicado rc=1; KT-002 200 min rc=1; verificador roto rc=1. actionlint 1.7.7 OK. Suite completa: 72 pruebas, 1 error previo (`fastapi`, P8). |
| 6 | KT-002 intacto | Sin diferencias con master en `tools/kt002_prospectivo.py`, `data/` y `docs/KT-002_registro_prospectivo.md`. El único cambio en `kt002.yml` sigue siendo el disparo de la guardia (log en `$RUNNER_TEMP`, no publicado). |

Tareas programadas (autorizado por el propietario): gerente `trig_013FrUSspavgYpLTVTRWu46M` actualizada 2026-10-24T02:56:28Z ("Kensy" → "el propietario"; vigía "cada 4 h"); horario 6:30 sin cambios. Registros históricos intactos.

## 15. Orden ejecutiva final (2026-10-23 21:08 CR) — estado verificable

Leyenda: **[I]** implementado en la rama · **[L]** probado localmente · **[GH]** verificado en GitHub Actions real, desde la rama, sin tocar master · **[P]** verificado en producción (master).

| Tema | Estado | Evidencia |
|---|---|---|
| Rama sincronizada con master, sin force | I | Merges de master; `git rev-list HEAD..origin/master` = 0 al cerrar |
| Lógica de predicción de KT-002 sin cambios | I L | Sin diferencias con master en `tools/kt002_prospectivo.py`, `data/` ni el preregistro; cambios en `kt002.yml`: `actions: write`, disparo de la guardia y comentarios |
| Integridad de KT-002 | L | `tools/kt002_integridad.py` (solo lectura): 76 filas, 72 puntuadas, 0 duplicados, objetivo 4 h, aciertos recalculados sin diferencias, `resumen.json` reproducido idéntico con `summarize()` original, 76/76 versiones en git escritas solo por `kt002-bot` y solo anexadas, reproducibilidad de modelos `identico: true`. **10 horas omitidas** en 3 huecos conocidos (20-oct 14–16 y 22–00 h; 21-oct 06–09 h UTC), anteriores a esta reparación |
| Pruebas | L | `test_guardia_salud` 28/28, `test_kt002_integridad` 4/4 (negativas: detecta duplicado, objetivo alterado, acierto alterado, resumen alterado; los datos reales quedan con el mismo hash), simulación del paso de salud 4/4, actionlint 1.7.7 OK; suite completa: 1 error previo (`fastapi`) |
| Guardia en verde con datos reales | GH | Corridas 40057266306 y 40057998529 (esta última con las correcciones de la auditoría): spread y tendencia (estaba vieja desde el 22-oct) medidos, publicados (`prueba-guardia/40057266306`, commit `5afa9ec`) y verificados por la API |
| Guardia en rojo ante falla | GH | Corrida 40057434838 (simulacro): solo falló "Verificar salud"; sin avisos, por ser rama |
| Corrida fuera de master no actúa sobre KT-002 | GH | Ninguna corrida de KT-002 creada por las pruebas (la última sigue siendo #24) |
| Disparo desde KT-002, cierre de avisos, actualización diaria en master | **pendiente** | Requiere fusionar el PR #32 |
| Vigía | I | Protección provisional activa (sin cancelar, reiniciar ni relanzar; escala al gerente). v2 compatible lista en `VIGIA_PROMPT_v2.md`; pasos 1–2 probados en seco con datos reales (`ok`). Se activa después de verificar la guardia en master |
| Coordinación | I | `CLAUDE.md`, `INFORME_DIARIO.md`, `ESTRUCTURA.md`, `desarrollo-reparador.md` y la tarea del gerente: el vigía avisa, el gerente decide, solo la guardia relanza. Registros históricos intactos. La comunicación Claude–ChatGPT es manual por GitHub (issues y PR); no hay sincronización automática |
| Reversión | I | `docs/ops/REVERSION_ORION.md` (revert sin force, apagado rápido, textos anteriores de las tareas, reemplazo de pendientes, ramas de prueba) |
| Frecuencia real del cron | GH | Guardia: 13 corridas por cron del 21-oct 19:33 al 24-oct 01:02 UTC, intervalo mediana 4,3 h (2,5–6,1). KT-002: mediana 4,3 h (2,5–5,7). Mecanismo alternativo: KT-002 dispara la guardia en cada vuelta horaria |

### Auditoría independiente (desconfiado): DUDAS ABIERTAS, sin hallazgos ALTOS
| Hallazgo | Nivel | Resolución |
|---|---|---|
| GitHub reemplaza corridas pendientes (`cancelled`) y la documentación no lo decía | MEDIO | Documentado en `kt002.yml` (comentario), `REVERSION_ORION.md` y `VIGIA_PROMPT_v2.md`, con evidencia: #23 → #24 |
| Comentarios desactualizados (`despertar.txt`, "cada hora") | BAJO | Corregidos |
| La deduplicación podía saltar a ciegas si fallaba | BAJO | Ante cualquier error se mide |
| Relanzar tras una falla daba verde | BAJO | Relanzar por falla deja aviso (rojo); el solape normal no |
| `actions: write` y token en `kt002.yml` | BAJO | `actions: write` es necesario para el disparo. El token queda en línea a propósito: con `env:` quedaría expuesto como variable al código de terceros del mismo paso |
| Margen chico del spread (45 contra 40) | BAJO | Límite 50 min |
| El PR cambia `CLAUDE.md` | BAJO | Necesita aprobación explícita del propietario al fusionar |
| Reversión incompleta | BAJO | Agregados: pendientes de KT-002 y ramas de prueba, con responsable |
| Logs de las corridas | — | El proxy de esta sesión no deja bajarlos (403). Que ChatGPT o el propietario los revisen en la interfaz de GitHub: la corrida 40057434838 debe mostrar solo "SIMULACRO de falla" |

### Costos
- GitHub Actions: repositorio público, runners estándar sin costo. La guardia corre ~1 min por corrida, ~24–30 por día. KT-002 sin cambios.
- Claude: las dos tareas programadas (gerente 1 vez por día y vigía 6 veces por día) usan Sonnet. El vigía, cuando todo está sano, hace 4 lecturas y termina. No se agregaron servicios con costo nuevo.
- Esta reparación: 1 auditoría con subagente (desconfiado).
