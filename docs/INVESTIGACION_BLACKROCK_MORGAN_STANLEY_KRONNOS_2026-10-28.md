# KRONNOS — Investigación institucional y catálogo de reutilización
Fecha: 2026-10-28
Estado: **documentación de investigación, no adopción ni certificación institucional**
Relacionados: `docs/POLITICA_SCRIPTS_PRIMERO_2026-10-28.md`; PR #45.

## Principios del proyecto
- Python / scripts deterministas / GitHub Actions primero; cero llamadas a LLM en operación ordinaria.
- Headless, sin UI compleja salvo necesidad demostrada; minimizar privilegios, secretos y dependencias.
- Registrar hora UTC, commit SHA, versiones, inputs, outputs, errores, anulaciones y métricas observables.
- Separar investigación, validación independiente y auditoría. No operar dinero real ni promover estrategias sin controles.
- No introducir nuevas conexiones con Claude. Preservar la evidencia histórica de atribución de autoría.

## Investigación: BlackRock y Morgan Stanley
**Precisión metodológica:** el GitHub público y los anuncios de empleo evidencian herramientas usadas por *algunos* equipos, no una descripción completa del stack interno de BlackRock/Aladdin ni de Morgan Stanley. La analogía con Kronnos no constituye validación de nuestras estrategias ni equivalencia institucional. Las cifras de repositorios y estrellas cambian; consultar organización al hacer un nuevo análisis.

BlackRock: https://github.com/blackrock
Morgan Stanley: https://github.com/morganstanley
FINOS Morphir: https://github.com/finos/morphir
Argo Events (hoy en argoproj): https://github.com/argoproj/argo-events
Aportes de Morgan Stanley a FINOS y otros proyectos deben contrastarse con documentación upstream.

### Catálogo de candidatos y decisión
| Proyecto | Rol potencial Kronnos | Decisión | Observación |
|---|---|---|---|
| morganstanley/testplan | Pruebas integración y simulación | INVESTIGAR PRIMERO | Comparar con pytest/stdlib y coste de mantenimiento |
| blackrock/ingen | Calidad/transformación de datos | INVESTIGAR PRIMERO | Verificar API, estado de mantenimiento y licencia |
| morganstanley/releaseherald | Notas deterministas desde Git | INVESTIGAR PRIMERO | Comparar con git log y script propio |
| blackrock/HOLA | Optimización de hiperparámetros | ESPERAR | Multiplicidad de pruebas aumenta N real del DSR; bloquear hasta controles estadísticos |
| blackrock/LCSO | Optimización con restricciones | FUTURO | Revisar utilidad cuando haya cartera simulada |
| blackrock/aladdinsdk | Patrones de auth, retry, logging | REFERENCIA | No asumir acceso a Aladdin ni instalar SDK sin uso concreto |
| finos/morphir | Reglas formales y lógica portable | REFERENCIA | No instalar framework completo sin justificar |
| argoproj/argo-events | Despacho event-driven | NO ADOPTAR AHORA | Requiere Kubernetes; Actions cubre los casos actuales |
| morganstanley/message-broker | Mensajería distribuida | NO ADOPTAR AHORA | Complejidad innecesaria para un pipeline headless pequeño |
| morganstanley/Xpedite | Perfilado de baja latencia | FUTURO | Solo tras evidencia de cuello de botella |
| morganstanley/optimus-cirrus | Computación/arquitectura distribuida | REFERENCIA | Scala y complejidad; no candidato inmediato |
| morganstanley/MSML | Investigación ML | EXPLORAR | No tratar como estrategia validada |
| morganstanley/binlog, pyfixmsg, treadmill | Registro, FIX, contenedores | NO ADOPTAR | Verificar estado/archivo y requisitos reales |
| blackrock/TopNotch, xml_to_parquet, micro-batcher, kafka-security, OCIBuilder | Calidad/formatos/lotes/infra | ESPECÍFICOS | Solo ante necesidad concreta |
| blackrock/EJML, protoc-jar-maven-plugin | Java/matriz/build | NO ADOPTAR | No aplican hoy al motor Python |
| BlackRock plugins Aladdin | Ecosistema APIs | REFERENCIA | Dependencias externas y credenciales no justificadas |
| morganstanley/treadmill-aws, Plug-in-AppDynamics-Data-Source | Orquestación/Java | NO ADOPTAR AHORA | Más infraestructura sin retorno claro |

No duplicar todo el catálogo en producción. Examinar commits, issues, tests, licencia y dependencias antes de reutilizar código. `api-evangelist/blackrock` es tercero, no oficial de BlackRock.

## Evidencia pública vs hipótesis
- Las páginas oficiales describen Aladdin como tecnología de análisis de carteras, riesgo y operaciones; no revelan por sí solas la implementación de cada workflow interno.
- Morgan Stanley publica herramientas y contribuciones a FINOS; no es correcto identificar cualquier repositorio suyo como parte del motor de trading interno.
- Empleos con Python, CI/CD GitHub Actions, Kubernetes, Terraform, Ansible, Argo CD, observabilidad o plataformas de artefactos sugieren herramientas en equipos específicos. **No afirmar** que BlackRock funciona exclusivamente con Python o GitHub Actions, que no usa Blazor en ningún entorno, o que copia exactamente el PR #45.
- Aladdin y Athena pertenecen a contextos institucionales diferentes: Aladdin a BlackRock; Athena a J.P. Morgan, no a Morgan Stanley.

## Mejoras low-cost scripts-first (propuestas; NO implementadas por este documento)
1. `GITHUB_STEP_SUMMARY`: incluir SHA, hora UTC, número de señales verificadas, errores, excepciones e informes inválidos. No inventar contadores: marcar `NO_VERIFICADO` cuando falte dato.
2. Concurrencia: el PR #45 usa `cancel-in-progress: false`; **no adoptar** propuestas con `true` sin verificar efectos sobre custodia y corridas de KT-002. Aislar grupos de workflow.
3. Registro de excepciones en JSON/CSV; alerta por recurrencia N en ejecuciones consecutivas. N configurable, y definir cómo se conservan y consultan ejecuciones previas; un artefacto aislado no sirve para medir continuidad.
4. SHA-256 canónico de entradas/salidas, con manifiesto, origen, versión y UTC; un hash solo NO prueba custodia externa ni autenticidad. No sustituir sello temporal RFC 3161 y almacenamiento inmutable cuando sea requisito.
5. Alertas en fallo, sin secretos en logs, `permissions: contents: read`, `persist-credentials: false` si no se necesita push.
6. Evitar pip/uv para informes basados en Python stdlib. Considerar uv/caché únicamente para trabajos con dependencias pesadas y mejoras medidas.
7. Mantener solo simulación/dry-run: no introducir opción de live execution en workflow_dispatch actual.
8. Artefactos Actions son temporales. Retención finita, no equivalen a auditoría inmutable. Anexar validación de integridad.
9. Distinguir observabilidad básica (métricas y alertas) de observabilidad completa (trazas, SLO, series de tiempo); no añadir Prometheus/Grafana sin necesidad.
10. Terraform/Ansible/ArgoCD y registries dedicados son referencias de escalamiento, NO tareas inmediatas.

## Prioridades de implementación
P0: cerrar correctamente barreras ATLAS #42 y Bloqueo A; proteger pre-registro, DSR, folds >=30, control de dominancia, evidencia sellada; no promover H3/H4 sin pruebas.
P1: probar reporte headless del PR #45 y agregar GITHUB_STEP_SUMMARY, manifiestos SHA y observación de fallos sin interrumpir KT-002.
P1: piloto comparativo testplan / ingen / releaseherald contra código actual; medir cobertura, memoria, tiempo, dependencias y licencias; adoptar solo ganancias observadas.
P2: explorar HOLA y LCSO después de controles de múltiples intentos.
P3: considerar plataformas distribuidas/UI/servicios extras solo al demostrar carga o escala.

## Fuentes para verificar al retomar este tema
- https://github.com/blackrock
- https://github.com/morganstanley
- https://github.com/blackrock/HOLA
- https://github.com/blackrock/ingen
- https://github.com/blackrock/LCSO
- https://github.com/blackrock/aladdinsdk
- https://github.com/morganstanley/testplan
- https://github.com/morganstanley/releaseherald
- https://github.com/morganstanley/message-broker
- https://github.com/finos/morphir
- https://github.com/argoproj/argo-events

## Regla de respuesta futura
Cuando el usuario pregunte por BlackRock, Morgan Stanley, software institucional, automatización o GitHub para **Kronnos**, revisar primero este archivo y `docs/POLITICA_SCRIPTS_PRIMERO_2026-10-28.md`, verificar el estado real del repositorio y distinguir «propuesto», «en PR», «fusionado», «corriendo» y «validado». Mencionar **Kronnos** siempre. No atribuir pruebas ni adopciones inexistentes.
