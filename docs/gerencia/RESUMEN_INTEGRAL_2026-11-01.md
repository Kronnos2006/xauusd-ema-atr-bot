# KRONNOS — informe integral y punto de pausa

Fecha de corte: 2026-11-01, Costa Rica. Autor: Codex. Consolidación solicitada por el propietario después de ordenar detener el trabajo. La meta general permanece **PAUSADA**. Esta actualización solo documenta; no integra PR, ejecuta experimentos ni reactiva automatizaciones del chat.

## Porcentaje oficial verificado

**31,25 %: 10 de 32 hitos acreditados. Restan 22 hitos (68,75 %).**

Fuente consultada en esta actualización: [Issue #88](https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/88), updated_at `2026-11-02T02:56:21Z`. Cuenta directa de casillas, ocho fases de cuatro hitos cada una. El porcentaje mide el plan de cierre; no el desarrollo histórico completo, calidad del sistema, probabilidad de éxito ni rentabilidad. El reporte automático anterior muestra31,2% por redondeo a un decimal; la fracción exacta10/32 es31,25%.

| Fase | Acreditados | Avance |
|---|---:|---:|
| Fase 1 — P0 Seguridad y estabilidad | 1/4 | 25 % |
| Fase 2 — P0 ATLAS, H3/H4 y custodia | 0/4 | 0 % |
| Fase 3 — P1 FreqAI y Binance | 3/4 | 75 % |
| Fase 4 — P1 Motor financiero | 3/4 | 75 % |
| Fase 5 — P1 Combinador y predicciones | 0/4 | 0 % |
| Fase 6 — P2 Panel ORION y reportes | 3/4 | 75 % |
| Fase 7 — P1 Auditoría profesional | 0/4 | 0 % |
| Fase 8 — P2 Entrega final en simulación | 0/4 | 0 % |

Los PR preparados o con CI verde no se suman hasta su aceptación, integración y acreditación con evidencia. En esta documentación no se marcan casillas.

## Qué se completó y autorizó en este chat

1. Se identificó el repositorio local de trading en `C:/Users/josem/OneDrive/Documents/rxt21/Nueva carpeta` (remoto Kronnos2006/xauusd-ema-atr-bot). La carpeta inicial del chat estaba vacía.
2. Se descargaron referencias y actualizó master por fast-forward (878 commits en esa actualización). Los commits propios quedaron conservados en codex/oracle-always-free; panel/ y los archivos locales no versionados se conservaron.
3. Se preparó [PR #96](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/96): panel unificado ORION/ATLAS/FreqAI/KT002 y alertas verificables. Se corrigió un hallazgo de empaquetado health.js ausente en /orion/; pruebas, CI y revisión independiente aprobadas.
4. El propietario escribió «APRUEBO» para #96. Se integró mediante merge9a9b05b3cb79ea1ffdc873a7c292c31d56c962e8, se acreditaron F6.2/F6.3 y se pasó de8/32 (25%) a10/32 (31,25%). El registro local y GitHub se sincronizaron (documentación b3e7abd).
5. La meta posterior abarcó los ocho frentes pendientes. Se desarrollaron los seis PR de implementación/evidencia #97, #99–#103, y el borrador de diseño #98. Todos siguen abiertos al corte; la aprobación de #96 no se extendió a ellos.
6. El propietario ordenó detener. La meta quedó pausada. No se integró nada más; las publicaciones periódicas preexistentes de GitHub no se cancelaron ni modificaron administrativamente.

## Trabajo preparado y evidencia por PR

### PR #97 — Seguridad de guardia

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/97); estado consultado: open, integrado: no.
- Rama: `codex/seguridad-guardia-auditoria`; SHA: `d3ab277c94c50ca3d45bb000a961868ad3c8f96c`.
- Cambio: Fechas inválidas/futuras, pasos obligatorios omitidos y entradas de corridas no verificables ya no producen falso sano ni dispatch no justificado.
- Evidencia: 28 pruebas de salud + 6 adversariales + 3 de publicación; revisión técnica independiente PASS.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/d3ab277c94c50ca3d45bb000a961868ad3c8f96c/docs/auditorias/SEGURIDAD_GUARDIA_2026-11-01.md).
- CI del SHA: [Kronnos - auditoria determinista de scripts: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41380870785); [Guardia - pruebas de publicacion segura: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41380870774).

### PR #98 — Propuesta FreqAI BTC

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/98); estado consultado: open, integrado: no.
- Rama: `docs/propuesta-freqai-btc`; SHA: `5c5911e590144090c55ddb4536ea40eb86057319`.
- Cambio: Borrador descriptivo BTCUSDT Spot a 4h, un modelo, baseline siempre sube y Fase 0 antes de entrenamiento/evaluación. Parámetros propuestos, no protocolo aprobado.
- Evidencia: Revisión metodológica identificó dependencia serial, faltantes y disponibilidad temporal; el borrador fue precisado. No se ejecutó experimento.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/5c5911e590144090c55ddb4536ea40eb86057319/docs/FREQAI_BTC_PROPUESTA_2026-11-01.md).
- No se recuperaron corridas de CI de PR para ese SHA; no se presenta como CI aprobada. La evidencia documental se revisó por separado.

### PR #99 — Panel móvil

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/99); estado consultado: open, integrado: no.
- Rama: `codex/panel-validacion-movil`; SHA: `9f3346b5068122ec9024c7fb7280ddde83c88ec2`.
- Cambio: Corrige documento de 767 px en viewport de 360 px; conserva navegación interna y fuentes verificables.
- Evidencia: 15 vistas Playwright (360/390/1280 x 5 pestañas), error API503 simulado, captura360 inspeccionada; 11+2 pruebas Python; revisión independiente PASS.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/9f3346b5068122ec9024c7fb7280ddde83c88ec2/docs/auditorias/PANEL_MOVIL_2026-11-01.md).
- CI del SHA: [Kronnos - auditoria determinista de scripts: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41381487672); [ORION Centro de Control - pruebas (sin Claude): success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41381487788).

### PR #100 — Riskfolio-Lib

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/100); estado consultado: open, integrado: no.
- Rama: `codex/riskfolio-limites`; SHA: `8e690cb666974d99aa9596b634a31fd190fa97f4`.
- Cambio: Reutiliza borrador de ChatGPT; limita posición a25%, bruto100%, vol10%, ventana60d, correlación y N efectivo. No optimiza ni autoriza posiciones.
- Evidencia: Riskfolio7.4.0 real aislado; 12 pruebas, pip check limpio y93 dependencias fijadas para QA. Revisión independiente PASS.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/8e690cb666974d99aa9596b634a31fd190fa97f4/docs/auditorias/RISKFOLIO_EVALUACION_2026-11-01.md).
- CI del SHA: [Kronnos - auditoria determinista de scripts: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41382513037); [Riskfolio - evaluacion offline con limites de riesgo: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41382513168).

### PR #101 — Evidencia original ATLAS

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/101); estado consultado: open, integrado: no.
- Rama: `docs/atlas-evidencia-recuperada`; SHA: `590a4d53e451028862c7155523dc239970344054`.
- Cambio: Recupera artifact12734829078 del run40507359902 y censo74 de Claude; preserva ZIP original, origen y hashes.
- Evidencia: Tres hashes coinciden con commit9b39ff9; FreeTSA y DigiCert ts-verify OK, repetidos por segundo agente. No acredita censo exhaustivo ni WORM.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/590a4d53e451028862c7155523dc239970344054/docs/auditorias/ATLAS_EVIDENCIA_RECUPERADA_2026-11-01.md).
- No se recuperaron corridas de CI de PR para ese SHA; no se presenta como CI aprobada. La evidencia documental se revisó por separado.

### PR #102 — Instalación y recuperación técnica

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/102); estado consultado: open, integrado: no.
- Rama: `codex/instalacion-recuperacion-smoke`; SHA: `1c2fb305656824320895b619a5ddddfeb7f5e09b`.
- Cambio: Fixture sintético16 períodos -> métricas/costos -> manifiesto -> restauración -> rechazo de corrupción. FuenteHEAD/hashes/dirty explícitos.
- Evidencia: Smoke y4 pruebas negativas PASS; CI Windows/Linux; revisión independiente PASS. No equivale a recuperación operacional completa.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/1c2fb305656824320895b619a5ddddfeb7f5e09b/docs/INSTALACION_RECUPERACION.md).
- CI del SHA: [Kronnos - auditoria determinista de scripts: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41383420023); [Instalacion y recuperacion sintetica sin red financiera: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41383419981).

### PR #103 — Permisos de PR

- [PR y discusión](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/103); estado consultado: open, integrado: no.
- Rama: `codex/permisos-pr-solo-lectura`; SHA: `56d601e6dce2fcf7d1d65710052c1cde2217508b`.
- Cambio: Jobs de validación Estado/Progreso con lectura; publicación solo noPR/master. KT004 solo jobpruebas endurecido, sin cambiar experimento.
- Evidencia: Chequeo estático3jobs/2guards,4 pruebas de mutación +4 de progreso; cinco CI SUCCESS; revisión independiente PASS.
- [Documento específico en ese SHA](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/56d601e6dce2fcf7d1d65710052c1cde2217508b/docs/auditorias/PERMISOS_PR_2026-11-01.md).
- CI del SHA: [Estado - actualizar ESTADO.md (sin IA): success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41384012754); [KT-004 multiactivo (ETH, SOL, BNB, XRP): success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41384012897); [Kronnos - auditoria determinista de scripts: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41384012698); [Permisos PR - regresiones estaticas de tokens: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41384012644); [KRONNOS - progreso de 32 hitos sin IA: success](https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41384012679).

## ATLAS: evidencia encontrada y límites

El propietario indicó que el trabajo compartido estaba en GitHub. Se encontró el trabajo de Claude en research/atlas-bloqueo-a-custodia-20261027, commit9b39ff94437655773efdaf39c4dcc714340cf100. Los archivos no estaban integrados en master.

- Censo localizado:74 líneas, explícitamente cota inferior del repositorio, no N exhaustivo.
- Artifact original:12734829078, run40507359902, sellos con genTime2026-10-27T12:53:34Z.
- ZIP original SHA256:0a098481008bf9c2595abfa1b54bdeabebac5a1bed2d8e84611184145ade19a8; preservado en PR101 junto con provenance.json, sin URLs temporales ni secretos.
- Firma FreeTSA verificada con manifiesto, cadena del artifact y CAHTTPS oficial; firma DigiCert verificada con cadenaTSR y bundleCA de Git. Ambos controles repetidos por segundo agente Codex.
- No se certificaron revocación, política de confianza previa, censo completo, disponibilidad temporal de todas las barras, custodia WORM ni validación confirmatoria.
- Artifact con retención90d no es almacenamiento inmutable independiente.
- [PR #42](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/42) sigue abierto y draft, SHA `3c943e96647b7bdc03abb06a913bb826bfdb9fe0`. No autorizar promoción o integración por la sola existencia de sellos.

## Seguridad y auditorías: resultados y límites

- Lectura estructural local de KT002:289 filas,285 puntuadas,289 bases únicas,0 duplicadas,12 horas omitidas acumuladas y0 en las últimas24 bases. Sin desfases de objetivo o puntuaciones anticipadas según el verificador básico; no prueba inferencia real, tiempo de publicación, acierto recalculado ni rentabilidad. Es una instantánea de esa copia, no estado vivo.
- Inventario inicial:47 workflows en master b70de39; el escaneo con el CI de instalación propuesto contenía48. El control automatizado de PR103 cubre tres jobs y dos guards, no todos los permisos posibles.
- Consulta remota de branches/master: protected=false, protection.enabled=false y enforcement_level=off; rulesets devolvió[]. Reconsulta independiente coincidió. No se modificaron esos ajustes; hacen falta diseño y autorización que preserven la publicación de KT002/guardia.
- Las revisiones técnicas se hicieron por un segundo agente Codex. No se atribuye a Claude una aprobación nueva ni se presenta como auditoría institucional externa.

## Pendientes por área y siguiente condición

| Área | Situación al pausar | Condición para seguir |
|---|---|---|
| Seguridad | PR97 y103 probados; auditoría global/estabilidad sin cerrar | Aceptación e integración, revisión del pipeline completo y permisos efectivos/protecciones sin interrumpir bots |
| ATLAS | Sellos originales recuperados; censo solo cota inferior | Conciliar todas las fuentes, custodia independiente inmutable y procedencia previa verificable; H3/H4 y revisión confirmatoria |
| FreqAI | PR98 es propuesta, no registro aprobado ni productor prospectivo completo | Fase0 real, parámetros estadísticos finales y aprobación del protocolo antes de evaluar |
| Motor financiero | PR100 evalúa librería real con límites parciales | Aceptar evaluación e integrar; no confundirla con stops/costos/kill switch completos |
| Combinador | Código existente exploratorio; protocolo nuevo no aprobado | Modelos/horizontes/unidades/pesos/baselines/costos fijos; predicciones futuras auténticas, muestra suficiente y revisión |
| Panel | PR99 validó viewports y erroresAPI | Aceptación del manual e integración; no es certificación de teléfono físico o accesibilidad total |
| Auditoría | Revisiones acotadas y pruebas específicas disponibles | Conciliar evidencia por experimento, sesgos/costos, N total y validación independiente del alcance completo |
| Entrega | PR102 guía y smoke técnico Windows/Linux | Producto integrado, recuperación operacional, prueba completa, acta y aceptación final |

No se puede convertir un histórico en muestra prospectiva ni crear hoy evidencia temporal previa de experimentos pasados. Los resultados futuros requieren tiempo de acumulación. El borrador de 4h no se presenta como horizonte óptimo demostrado ni como estrategia rentable.

## Las 22 casillas aún abiertas del tablero

- [ ] Incidencias críticas reproducibles diagnosticadas, con pruebas negativas
- [ ] Guardia y KT-002 auditados sin modificar datos ni relanzar corridas
- [ ] Auditoría de estabilidad y control de permisos aprobados
- [ ] Censo real N_total completo, histórico y con custodia externa previa e inmutable
- [ ] Procedencia temporal de barras/prerregistros probada por evidencia independiente
- [ ] Validación confirmatoria DSR ≥0.95, walk-forward y ≥30 operaciones/fold cuando aplique
- [ ] Revisión independiente del PR #42 y autorización expresa para fusionar; si falta, permanece bloqueado
- [ ] Protocolo prospectivo registrado y pipeline de inferencia reproducible en simulación
- [ ] Riskfolio-Lib evaluado/adaptado con límites de riesgo y tests de simulación
- [ ] Protocolo de modelos, horizontes, pesos, costos y baseline preregistrado
- [ ] Predicciones prospectivas de FreqAI/combinador verificadas sin fuga
- [ ] Comparación neta vs «siempre sube» y otras referencias sin selección posterior
- [ ] Informe de robustez, incertidumbre y veredicto sin declarar ventaja indebida
- [ ] Panel e informes validados con pruebas y manual de uso móvil
- [ ] Pruebas negativas de lookahead, fuga, sesgo y costos auditadas
- [ ] Walk-forward temporal, N_total y métricas reproducibles por experimento
- [ ] Auditoría independiente con resultado PASS/FAIL documentado
- [ ] Evidencias (PR, SHA, CI, custodia) consolidadas por cada decisión
- [ ] Repositorio, dependencias, scripts y permisos mínimos documentados
- [ ] Procedimiento reproducible de instalación y recuperación aprobado
- [ ] Prueba de extremo a extremo en simulación sin órdenes ni dinero real
- [ ] Acta de entrega final y lista de investigación prospectiva pendiente

## Ubicación y conservación del trabajo

Repositorio local: `C:/Users/josem/OneDrive/Documents/rxt21/Nueva carpeta`. Todos los commits descritos están publicados en sus ramas de GitHub; los documentos específicos se consultan en los enlaces porSHA anteriores aunque todavía no estén en master. Ramas no fusionadas conservan sus cambios de código y su propia bitácoraESTADO.md.

Entornos locales de QA: .local/ui-qa (Playwright), .local/riskfolio-env (venv aislado), .local/mobile-qa (capturas/reportes), .local/atlas-evidencia (extracción original), .local/centro-control (snapshot generado). No forman parte de una instalación productiva ni se versionan completos. panel/ preexistente permanece sin sobrescribir. El servidor local temporal de QA se detuvo.

No se modificaron órdenes, capital, holdouts ni registros de KT002. No se lanzaron, cancelaron o reiniciaron manualmente corridas de Actions; los PR dispararon sus comprobaciones preexistentes/declaradas. No se modificaron credenciales, protecciones administrativas o parámetros de experimentos. Documentar no equivale a aprobar o integrar ninguno de los seis PR pendientes.

## Punto exacto para retomar

Mantener la pausa hasta nueva instrucción. Si el propietario autoriza retomar e integrar, verificar otra vez los SHA y CI de #97, #99, #100, #101, #102 y #103, resolver conflictos de documentación conservando todas las entradas y acreditar solo hitos cuyo alcance se acepte. #98 requiere decisión metodológica; #42 mantiene sus bloqueos. Actualizar Issue88 y regenerar el reporte solo después de esa verificación. No atribuir un porcentaje anticipado a trabajo preparado.

