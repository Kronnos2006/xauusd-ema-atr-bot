# Auditoría externa de lectura — 2026-10-22

**Autor:** ChatGPT (revisor externo). **Estado:** DUDAS ABIERTAS; NO es aprobación de auditor independiente `desconfiado`.
**Alcance:** revisión estática de archivos publicados en `master` mediante conector GitHub. Sin ejecución de código, sin lectura de logs de Actions, sin acceso a Oficina privada ni pruebas en vivo. Sin cambios al experimento, modelos, datos, workflows o políticas.

## Evidencia leída
- `CLAUDE.md`, `AGENTS.md`, `docs/CONTEXTO_PARA_OTRA_IA.md`
- `docs/KT-002_registro_prospectivo.md`, `tools/kt002_prospectivo.py`
- `.github/workflows/kt002.yml`, `.github/workflows/guardia.yml`
- `.claude/agents/gerente.md`, `.claude/agents/analista.md`, `.claude/agents/desconfiado.md`
- `docs/gerencia/ESTRUCTURA.md`, `docs/gerencia/INFORME_DIARIO.md`
- `docs/analisis/2026-10-22.md`, `data/kt002/resumen.json` y `docs/coordination/CONTEXTO_COMPARTIDO.md`

## Resultado comprobado en archivos
- `data/kt002/resumen.json` actualizado `2026-10-22T12:07:00Z`: 37 pronósticos, 33 vencidos, 7 sin solape y **10 horas omitidas acumuladas desde el primer pronóstico**. La cifra no establece por sí misma cuántas omisiones ocurrieron en las últimas 24 h.
- En el subconjunto sin solape: siempre sube 4/7, Kronos 3/7, TimesFM 2/7 y KT-001 1/7. Sin inferencia de ventaja; no hay rentabilidad evaluada.
- `kt002_prospectivo.py` aplica filtros de velas cerradas y continuidad del contexto, revisiones fijadas, semilla fija, deduplicación por base, y guarda puntuaciones aun cuando falle una inferencia. Observación de código, **no prueba de correcta ejecución real**.
- `gerente.md` preserva exclusividad del usuario e independencia de auditor, riesgo y analista. `INFORME_DIARIO.md` exige convocatorias condicionadas, y los jueves innovación + recursos de IA: el relato del informe corresponde a ese calendario; las convocatorias reales no se verificaron.

## Hallazgos y solicitudes de evidencia
1. **MEDIA — Continuidad de KT-002 sin verificación completa.** `kt002.yml` usa procesos prolongados, grupo de concurrencia y publicación Git con rebase/reintentos; `guardia.yml` procura relanzar la corrida. Comprobar con la API de Actions: secuencia de ejecuciones, colas, fallos, horas con/sin commit y última hora sin predicción. Criterio: cada omisión debe estar contada; sin duplicados ni puntuaciones retrospectivas presentadas como predicciones prospectivas. No modificar workflow en esta auditoría.
2. **MEDIA — Desfase entre umbrales de supervisión y reporte.** `INFORME_DIARIO.md` exige llamar a `vigia-datos` cuando faltan >3 horas en 24 h; el resumen ya muestra 10 omisiones **acumuladas**, pero no contiene desglose de últimas 24 h. Solicitar cálculo exacto de omisiones por ventana móvil de 24 h, documentando si procede convocatoria. No afirmar incumplimiento sin ese cálculo.
3. **MEDIA — Fuentes del analista insuficientes.** `analista.md` pide cada dato con fecha, fuente y enlace, y no reportar datos sin fuente. El informe del 22-oct incluye macro/ETF con proveedor pero sin URL exacta; además reconoce tres días de antigüedad de datos macro y una discrepancia de precio BTC sin resolver. Solicitar URLs, timestamps UTC y fuente primaria/alternativa antes de tratar esos números como verificados; preservar el informe original y añadir rectificación o complemento separado a cargo del analista, no reescribir sus conclusiones.
4. **MEDIA — Verificar integridad de publicaciones automáticas.** El workflow registra fallos de `git pull`/push y reintenta 3 veces. Inspeccionar logs y commits para descartar resultados locales no publicados y duplicados; no atribuir salud total únicamente a ausencia de issue `guardia`.
5. **BAJA — Revisión cruzada pendiente.** `docs/coordination/CONTEXTO_COMPARTIDO.md` identifica tareas con revisor Codex o Claude pendiente. Conservarlas como pendientes hasta prueba concreta; el presente documento no sustituye la auditoría independiente del proyecto.

## Acciones recomendadas sin alterar KT-002
- **Gerente / Operaciones:** aportar IDs/estados de últimas corridas KT-002 y guardia, cronología UTC de commits y diagnóstico de lag.
- **Vigía de datos:** recalcular de CSV horas omitidas en últimas 24 h, bases únicas, marcas de tiempo de predicción y puntuación, resultados sin solape; conservar evidencia y hashes.
- **Analista independiente:** aportar anexos con enlaces exactos y timestamps para macro, ETF y precios discrepantes; distinguir «no verificado» de dato verificable.
- **Desconfiado independiente:** revisar este documento y emitir su propio veredicto, sin asumir aprobación por ChatGPT.
- **Gerente:** decidir correcciones documentales/operativas permitidas, escalar cambios al experimento en curso al usuario.

## Límites
No sugerir operar, abrir reservas/holdouts, optimizar modelos con estos resultados ni alterar un experimento vigente. No hay dictamen de edge ni decisión de Fase 1.