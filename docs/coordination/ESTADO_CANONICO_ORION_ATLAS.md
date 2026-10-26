# ORION–ATLAS — FUENTE DE VERDAD Y CONTINUIDAD
**Corte verificado:** 2026-10-26. **Propietario:** Kronnos.
**Propósito:** que cada respuesta y cada intervención identifique el último punto verificado, los pendientes y la evidencia. **Este archivo NO certifica por sí mismo que algo ocurrió.**

## Regla de trato y comunicación (obligatoria para quien siga este proyecto)
- Dirigirse al propietario como **Kronnos en cada respuesta**.
- Nunca afirmar que algo fue implementado, auditado, fusionado, probado o certificado sin evidencia concreta (commit SHA, URL PR, corrida CI, informe verificable).
- Distinguir siempre: **VERIFICADO**, **EN PROGRESO**, **PENDIENTE**, **BLOQUEADO**, **PROPUESTA**.
- Si no hay acceso actualizado a GitHub, decirlo; este documento puede quedar desactualizado. No asumir que un texto sustituye el estado remoto.
- No confundir CI verde, software verificado, validez estadística, ventaja financiera y autorización para trading; son criterios diferentes.
- Antes de trabajar: leer este archivo, el PR activo y su último commit. Al terminar: actualizar aquí fecha, acciones realmente completadas, pruebas/corridas, pendientes y siguiente paso. Mantener historial, no borrar fracasos.
- No trabajar ni declarar ejecución asíncrona sin una automatización real.
- No modificar KT-002, estrategias congeladas, holdouts ni habilitar trading real sin autorización explícita y controles correspondientes.

## Orden de prioridades — extrema a baja
| Prioridad | Entregable | Criterio de cierre |
|---|---|---|
| **P0 EXTREMA** | Preservar bloqueo confirmatorio y no tocar producción/KT-002 | No bypass; no promoción ni trading; control por pruebas adversariales |
| **P0 EXTREMA** | **H4** custodia + censo completo | Alta previa por intento; definición y resultados inmutables; comparación con registro independiente autorizado; ancla resuelta por política; si no hay fuente externa => INCONCLUSA |
| **P0 EXTREMA** | **H3** DSR y varianza entre ensayos | Método elegido antes de resultados; varianza entre variantes examinada con datos adecuados, N nominal completo, sensibilidad y abstención por incertidumbre |
| **P1 ALTA** | **H2** sello de señal y datos punto-en-tiempo | Proveedor remoto autenticado; señal completa pre-registrada; ejecución exitosa previa; controles anti-look-ahead |
| **P1 ALTA** | Demostración adversarial reproducible | Detectar omisión 100→5 o 95, cambio de ATR sin nueva alta, nuevo ATR sellado válido, alteración posterior, fuga temporal y muestra escasa; rechazar o abstenerse por la causa correcta |
| **P1 ALTA** | Auditoría nueva e independiente del PR #42 | Revisor no involucrado en autoría; comandos, commits, pruebas y hallazgos publicados; cero bloqueantes |
| **P2 MEDIA** | Actualizar #42 con master y fusionar solo cuando cumpla lo anterior | CI verde, auditoría reproducible y autorización de integración; mantener draft mientras incompleto |
| **P2 MEDIA** | Protocolo a priori KT-002 | Objetivo, n, horizonte, potencia/efecto mínimo, ventana y condición de rechazo registrados antes de evaluar |
| **P2 MEDIA** | Resolver `MomentumCandleProximity.mq5` | Prerregistro íntegro o exclusión formal sin mezclar sus resultados |
| **P3 BAJA** | Estrategias clásicas, Enmienda 01, tsm-volscaling Fase 0 | Ejecutar conforme a su propio protocolo, sin aplicar retroactivamente exigencias ATLAS |
| **P3 BAJA** | Infraestructura avanzada S3 Object Lock / RFC 3161 y certificación de laboratorio | Custodia externa real configurada y probada con separación de permisos; política de retención y costo; no fingir disponibilidad |
| **P3 BAJA** | Evaluación prospectiva extensa, informes gerenciales y eventual evaluación financiera | Evidencia nueva, métricas y riesgos claros; ninguna promesa de rentabilidad |

## Último estado remoto confirmado (2026-10-26)
- Repositorio: `Kronnos2006/xauusd-ema-atr-bot`.
- PR **#42**: **ABIERTO, DRAFT, NO FUSIONADO**. Rama `research/atlas-barreras-estadisticas-20261024`; último SHA verificado `66f5fc9b3f19c74836acf3e6fff2c7796618128f`.
- CI ATLAS: corrida **#56** (`40421645734`) **success** para `66f5fc9`; no equivale a certificación.
- H1: corregida en rama la falsa bandera `pasa_barreras_estadisticas` para datos descriptivos; diagnósticos no autorizan promoción.
- H2: parcialmente reforzada en rama (identidad de señal y ejecución remota completed/success); **sin custodia remota integral autenticada**.
- H3: **PARCIAL**; se implementó diagnóstico separado de varianza observada entre Sharpe de ensayos, pero sigue sin certificarse estimador robusto, dependencia y DSR confirmatorio.
- H4: **PARCIAL**; se añadió conciliación de IDs contra inventario externo con fallo cerrado y pruebas 100→5/95; no existe identidad de proveedor ni custodia externa completa, verificable y obligatoria.
- `evaluar_confirmatorio` sigue bloqueado. Sin prueba de ventaja financiera. KT-002 no alterado por los cambios anteriores.
- Fase documental 1 finalizada: PR #33 merge `17be07c5`, #36 merge `6ad4460b`, #38 merge `72ce284a`.
- Plan técnico de #42: `docs/arquitectura/ATLAS_PLAN_CIERRE_PR42_2026-10-26.md` en rama PR.
- Último informe al PR #42: https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/42#issuecomment-6428811116

## Reglas de prueba de la arquitectura
1. **No inferir completitud del censo a partir de un hash o un tag.** Una fuente externa solo demuestra lo que registró; registros ocultos antes de la custodia siguen siendo un riesgo.
2. Registro previo completo: hipótesis, parámetros, código, referencia de datos, autor y sello antes de empezar; eventos de resultado separados, sin reescritura.
3. Modificar ATR requiere **nuevo intento y nuevo sello antes de correr**. Sin nueva alta debe bloquearse; con nueva alta puede investigarse, sin aprobar su desempeño.
4. El evaluador no recibe `N_total` ni anclas arbitrarias como autoridad. Cuando no pueda reconstruir evidencia autenticada: **INCONCLUSA**.
5. HAC (dependencia temporal), varianza de Sharpe entre variantes (DSR), CPCV/PBO y potencia son problemas diferentes: no sustituir uno por otro sin justificación.
6. Un rechazo estadístico requiere evidencia válida; falta de evidencia implica abstención/inconclusión, no falsos rechazos.
7. No atribuir políticas específicas a BlackRock/AQR ni afirmar estándares regulatorios sin documentos verificables.

## Cómo actualizar este archivo
Añadir debajo de este encabezado una entrada por intervención con fecha, responsable, PR, SHA, CI y pendientes; si cambia el último estado, editar también la sección anterior. Conservar la trazabilidad de cambios en Git.

### Bitácora
- **2026-10-26 — ChatGPT:** creación inicial del registro y orden de prioridades según instrucciones de Kronnos. No se declara haber resuelto H3/H4 ni auditado el #42.

- **2026-10-26 — ChatGPT:** en PR #42 agregó conciliación contra inventario externo de intentos (sin afirmar que este proveedor esté autenticado), diagnóstico de varianza observada entre ensayos y pruebas adversariales. CI #56 success en `66f5fc9`. H3/H4 siguen parciales, PR sin fusionar, puerta confirmatoria cerrada.
