# KRONNOS — Expediente tecnológico Jane Street, Two Sigma y Citadel
Fecha: 2026-10-28; tipo: investigación pública, NO implementación ni reproducción de estrategias privadas.
Complementa BlackRock/Morgan Stanley/J.P. Morgan en docs/.

## Jane Street
- Org: https://github.com/janestreet
- https://github.com/janestreet/core y https://github.com/janestreet/base: librerías OCaml que ponen énfasis en tipado y contratos.
- https://github.com/janestreet/magic-trace: traza de alta resolución aprovechando Intel Processor Trace; normalmente Intel Linux y hardware compatible, no runners genéricos de GitHub.
- Mensaje útil: interfaces explícitas, reproducibilidad, pruebas y medición antes de optimizar. No migrar Kronnos a OCaml ni FPGA sin evidencia de cuellos de botella.
- El material atribuye OCaml y presencia de FPGA, pero no permite afirmar que *todo* su trading use un lenguaje o hardware específico.

## Two Sigma
- Org: https://github.com/twosigma
- https://github.com/twosigma/memento: transformaciones reproducibles, metadatos y procedencia; relevante **ALTO** para la cadena de datos de Kronnos.
- https://github.com/twosigma/flint: librería series temporales sobre Spark; analiza grandes series pero fija versiones Spark antiguas (2.3/2.4 en README), por ello **REFERENCIA**, no instalar sin revisión de compatibilidad.
- https://github.com/twosigma/Cook: planificación distribuida; validar estado actual y archiving antes de proponer. GitHub Actions basta a nuestra escala.
- Evitar afirmar que usan petabytes/notebooks o un stack interno preciso solo porque publicaron proyectos de ese ecosistema.

## Citadel vs Citadel Securities
- No confundir firma inversora Citadel con creador de mercado Citadel Securities.
- Los repositorios de competencias Terminal (terceros) NO prueban qué algoritmos ni herramientas internas emplea Citadel.
- Las ofertas y entrevistas públicas pueden indicar C++, Python, redes, baja latencia, pero no autorizan afirmar Redis, kdb+, colocación concreta o hardware particular como el diseño de todo su stack.
- Lección Kronnos: separar investigación de ejecución, medir latencias solo si afectan objetivo; no intentar HFT en Actions.

## Comparativa de valor práctico
| Referencia | Idea | Decisión Kronnos |
|---|---|---|
| Two Sigma Memento | lineage, transformaciones reproducibles y control de caché | PRIORIDAD ALTA: estudiar manifiestos por paso, evitar sobreescrituras |
| Jane Street Core/Base | contratos y tipos estrictos | APLICAR PRINCIPIOS con Python y tests, no portar |
| Jane Street magic-trace | perfilado de CPU | POSTERGAR: hardware/runners no adecuados y sin demanda comprobada |
| Two Sigma Flint | joins temporales correctos/as-of y series | ESTUDIAR algoritmos; sin Spark |
| Two Sigma Cook | trabajos distribuidos | NO INSTALAR ahora |
| Citadel Terminal repos terceros | patrones de juegos/problemas | NO tomar como infraestructura de Citadel ni señales de trading reales |

## Estado de ingeniería 28 octubre
- PR #45: políticas e informe headless de Kronnos, sigue borrador salvo verificación Git actual.
- PR #46: cuatro scripts experimentales, en rama de PR #45, **no corren automáticamente** y no son producción.
- Recolector: allowlist y rechazo de red privada/redirección. ADVERTENCIA: validación previa de DNS sola no elimina DNS rebinding ni proxies; pendiente de sandbox/egress proxy y pruebas de red para producción. No ejecutar contra URLs no aprobadas.
- Evaluador: usa git show SHA:path y fecha de committer anterior al tiempo publicado para pre-registro. La fecha Git es manipulable y no equivale a timestamp externo. Por eso promoción siempre BLOQUEADA, además faltan confirmación de madurez y DSR.
- Auditor: hash archivo y resumen; no es custodia sellada.
- Pruebas unitarias incluidas; solo reclamar ejecución después de comprobar GitHub Actions.
- No se han incorporado librerías de las firmas ni modificado automaciones de KT-002.

## Fuentes
- https://github.com/janestreet/magic-trace
- https://github.com/janestreet/core
- https://github.com/twosigma/memento
- https://github.com/twosigma/flint
- https://github.com/twosigma/Cook

## Regla documental
Ante consulta de sistemas de firmas cuantitativas siempre citar fuente verificable, marcar hecho vs inferencia y comprobar PRs y tests vivos, sin alucinar equivalencias con su infraestructura privada. Priorizar Kronnos scripts-first y evidencia sobre complejidad.
