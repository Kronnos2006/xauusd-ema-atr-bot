# Kronnos — Arquitectura operativa institucional: BlackRock y J.P. Morgan
Investigación pública: 2026-10-28. Estado: análisis; NO supone adopción/validación técnica ni acceso a sistemas internos.
Complementa docs/INVESTIGACION_BLACKROCK_MORGAN_STANLEY_KRONNOS_2026-10-28.md y POLITICA_SCRIPTS_PRIMERO_2026-10-28.md.

## Separar entidades
BlackRock (Aladdin) != J.P. Morgan Chase (gobierno de modelos, Fusion, DataQuery, Athena) != Morgan Stanley (Testplan, Morphir). Evitar atribuciones cruzadas.

## BlackRock: lo públicamente documentado
- Aladdin integra datos, gestión de cartera, trading, operaciones, compliance, contabilidad y riesgo con lenguaje común, no se ha publicado arquitectura interna exhaustiva: https://www.blackrock.com/aladdin/about-us/about/faqs
- Aladdin Risk usa factores, escenarios, stress testing, límites, cumplimiento y procesos de escalamiento/auditoría (Risk Radar): https://www.blackrock.com/aladdin/platforms/products/aladdin-risk
- Aladdin Studio: APIs para lectura/escritura, automatización de informes, órdenes, exposición, conciliaciones, con gestión y controles: https://www.blackrock.com/aladdin/platforms/products/aladdin-studio ; https://www.blackrock.com/aladdin/platforms/products/apis
- Aladdin Data Cloud: datos institucionales compartidos, monitorización y control de calidad: https://www.blackrock.com/aladdin
- BlackRock sí estudia y usa IA; no afirmar que toda su ingeniería sea exclusivamente Python/Actions o libre de IA: https://www.blackrock.com/aladdin/discover/report/ai-in-investment-management
- Lección Kronnos: fuente de datos consistente, riesgo antes de decisiones, interoperabilidad vía contratos pequeños, guardar procedencia y reportes.

## J.P. Morgan Chase: gobierno público
- Informe anual FY2025: tres líneas de defensa: negocio/operación controla riesgos; gestión de riesgos independiente mide/desafía; auditoría interna evalúa controles.
- Model Risk Governance and Review (MRGR): los usuarios/desarrolladores diseñan/prueban modelos, la función independiente revisa, aprueba modelos nuevos y cambios materiales, pide pruebas y supervisión continua; clasificación según exposición/criticidad. Excepciones están controladas. Fuente primaria: https://www.jpmorganchase.com/ir/annual-report (FY2025, apartado 'Estimations and model risk management' y 'Three lines of defense').
- No se conoce el diseño interno exhaustivo de Athena desde fuentes públicas; no presentarlo como código abierto ni confundir con Morgan Stanley.
- Lección Kronnos: tres responsabilidades separadas, preregistro, validación estadística independiente, aprobación humana para cambios de alto riesgo, seguimiento prospectivo, sin trading real.

## Repos oficiales JPMC descubiertos
- https://github.com/jpmorganchase/dataquery-sdk — Python para API de datos, OAuth, token bucket, reintentos exponenciales, circuit breaker, sync/async, logging, descarga masiva y diagnóstico. UTILIDAD ALTA: estudiar patrones, no asumir acceso a servicio de pago ni instalar dependencia sin necesidad.
- https://github.com/jpmorganchase/fusion — SDK Python para plataforma de datos institucionales; UTILIDAD MEDIA-ALTA, estudiar contratos de datos, catálogo y procedencia.
- https://github.com/jpmorganchase/nbcelltests — tests por celdas en notebooks para reports; solo si el proyecto usa Jupyter.
- https://github.com/jpmorganchase — catálogo de proyectos abiertos, no es un mapa del software interno.

## Arquitectura objetivo pequeña para Kronnos (propuesta)
1. Ingesta Python/API -> snapshot con origen, ventana UTC, SHA-256, esquema y pruebas de calidad.
2. Datos normalizados inmutables por corrida -> motor de predicciones sin LLM (KT-002 y otros modelos evaluados).
3. Resultados y variantes -> registro exhaustivo de intentos + hash preregistro anterior a señal.
4. Validador independiente -> walk-forward, 30 operaciones mínimas por fold, DSR >= 0.95, dependencia temporal/HAC, prueba con/sin fold dominante y controles de costos.
5. Riesgo/cumplimiento -> política fail-closed: estado NO_VERIFICADO/INVÁLIDO no promociona.
6. Auditoría -> SHA, UTC, cambios Git, cadena de evidencia, sellos externos cuando son requisito, controles de excepciones y custodia independiente.
7. Reporte programado -> GITHUB_STEP_SUMMARY, JSON, métricas; monitoreo por reglas, cero LLM normal.
8. Gerente -> intervención humana solo en excepciones, presupuesto de recursos y decisiones explícitas.
**No** implementar Kubernetes/ArgoCD, APIs institucionales, dashboards complejos o ejecución monetaria sin necesidad validada.

## Priorización por beneficio/costo
P0: controles pendientes de ATLAS PR #42 y Bloqueo A, validez científica de H3/H4, no afectar KT-002.
P1: automatización mínima, observabilidad GITHUB_STEP_SUMMARY, manifiestos verificables, pruebas deterministicamente repetibles.
P1: piloto patrones DataQuery (reintentos, rate limiting, circuit breaker), evaluar sin conexión a plataforma propietaria.
P2: esquema de catálogo tipo Fusion; pruebas notebook solo si hay notebooks productivos.
P3: optimización avanzada (HOLA/LCSO) y orquestación distribuida tras demostrar necesidad.

## Reglas de precisión y respuesta
Distinguir factualmente *documentado por institución*, *repositorio público* e *inferencia de diseño para Kronnos*. No afirmar replicar Aladdin ni Athena, ni que acciones de GitHub equivalen a supervisión corporativa. Documentar siempre estado real propuesto/PR/merge/corriendo. Conservar fuentes y comprobar cambios antes de citar datos actuales.
