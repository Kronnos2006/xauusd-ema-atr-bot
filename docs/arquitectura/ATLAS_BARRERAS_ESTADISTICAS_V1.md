# ATLAS — barreras estadísticas v1 (infraestructura en revisión)

- Se agrega `evaluar_confirmatorio` en `atlas/validacion_temporal.py`. No sustituye ni declara confirmatoria la evaluación exploratoria `evaluar_fuera_muestra`.
- `evaluar_folds_operaciones`: un fold con <30 operaciones es `INVALIDO`, no interviene en DSR ni t-stat ni puede promoverse. DSR del módulo raíz `deflated_sharpe.py`, umbral fijo ≥0.95; t-stat con todos los folds válidos y excluyendo el dominante (mayor valor absoluto de la suma de retornos netos por operación).
- `N_total` se conserva sin reducción mediante igualdad exacta entre censo y número declarado. **Limitación crítica:** ese censo todavía lo proporciona el invocador; esta infraestructura no puede certificar que incluya absolutamente todas las variantes históricas. Auditoría independiente obligatoria.
- `verificar_sello` confirma que un documento con `id` de preregistro aparece en un commit git concreto y exige una observación de GitHub Actions, con `head_sha` coincidente y fecha de creación **estrictamente anterior** a la señal. El booleano de `Senal` se ignora para la nueva puerta. **Limitación crítica:** GitHub Actions run no demuestra que el contenido completo del diseño experimental estuviera congelado ni que la fuente de anclas inyectada sea confiable. En producción falta implementar y auditar un proveedor independiente autenticado de evidencias GitHub; **sin proveedor la puerta falla cerrada**.
- El simulador histórico `simular` sigue aceptando el booleano para investigación retrospectiva y pruebas de regresión. **No es seguro usarlo como validación confirmatoria**, ni como ejecutor de estrategias; la única ruta de evaluación estadística nueva es `evaluar_confirmatorio`. Exige endurecer futuras rutas públicas para impedir el bypass.
- Los tests incluyen 29 y 30 operaciones, N_total inflado/reducido, commit anclado antes/después/igual a publicación, contenido de preregistro no coincidente y ausencia de ancla.
- No incluye nuevas señales, estrategias, datos ni resultados financieros. No hubo acceso a holdout ni modificación de KT-002. **No se autoriza promoción ni fusionar sin auditoría independiente y permiso del propietario.**

Autor: ChatGPT (OpenAI), 2026-10-24.

## Corrección de auditoría — 2026-10-26 (fail-closed)

La auditoría independiente detectó dos vulnerabilidades: retornos arbitrarios desvinculados de señales selladas y `N_total` elegido por el invocador. **`evaluar_confirmatorio` ahora lanza `ValueError` incondicionalmente** hasta que se implemente y audite una cadena verificable de procedencia de retornos y un censo de variantes independiente, completo y anclado. Ninguna estadística recibida por argumento autoriza una promoción.

`evaluar_folds_operaciones` es **descriptiva**, conserva `promocion_permitida=False` por compatibilidad de API y expone `pasa_barreras_estadisticas` como diagnóstico calculado sobre datos NO certificados; tampoco demuestra ventaja. El comparador `validar_n_total` sigue existiendo solo como validación de consistencia entre dos argumentos, **no es un control de censo real**. No se debe tratar esa comparación como barrera de procedencia.

Pruebas de regresión agregadas: retornos fabricados con sello válido deben ser rechazados, evaluación descriptiva jamás promueve y ancla `created_at=None` falla cerrada sin excepción. Estas son barreras provisionales de seguridad, **no la implementación completa del censo inmutable ni la trazabilidad operación→señal→datos→SHA**. Esos desarrollos siguen pendientes. PR en borrador; no fusionar sin nueva auditoría independiente y aprobación expresa del propietario.

## Prototipo de procedencia reproducible (2026-10-26)

Se agrega `atlas/evidencia_confirmatoria.py` con `preparar_evidencia`, `censar_variantes` y `reconstruir_operaciones`. Lee barras JSON con hash de bytes SHA-256, reconstruye posiciones a partir de señales admitidas por el simulador ATLAS v2 y computa rendimientos intrabar netos por apertura/cierre de posición (costo por lado). El censo local enumera variantes identificadas y rechaza duplicados, esquemas incorrectos y totales declarados que difieran de la cantidad de entradas. No admite un parámetro `N_total` alternativo en esta API. Tiene pruebas para modificación de archivos, censos falsificados, sellos ausentes y retorno reproducible.

**Advertencia explícita de confianza:** los SHA de entrada y el fichero del censo todavía pueden ser sustituidos conjuntamente por el invocador. Un registro local encadenado no prueba por sí solo exhaustividad histórica. El booleano de `Senal` no constituye una verificación remota: aquí se emplea solamente como control de acceso al simulador heredado, y no sirve para promoción. Los retornos provienen del archivo de barras, pero todavía falta verificar que el SHA pertenece a un blob Git inmutable, que ese commit tiene fecha observada por servidor anterior al evento, y que cada señal fue verificada por un proveedor de confianza que no dependa del propio invocador. También queda pendiente validar no solapamiento de pliegues e independencia estadística para un estudio confirmatorio.

Por estas limitaciones, el estado producido es `DESCRIPTIVO_NO_CONFIRMATORIO`; `evaluar_confirmatorio` sigue **cerrada incondicionalmente** y `promocion_permitida` permanece `False`. El componente es una base técnica verificable, no una aprobación estadística ni un resultado de estrategia.

## Revalidación — sellos para cada señal

`preparar_evidencia` ahora exige `repo`, referencias de commit/ruta por ID de señal y proveedor de anclas; ejecuta `verificar_sello` para **cada señal** antes de reconstruir operaciones. El booleano suministrado por una instancia de `Senal` no basta para admitirla. Si falta sello o ancla, falla cerrado. Los proveedores inyectados solo sirven para pruebas; la autenticidad y la exhaustividad requieren auditoría operacional independiente.

Las pruebas de CI ahora incorporan `tests.test_atlas_evidencia`. La puerta original `evaluar_confirmatorio` sigue cerrada porque los SHA y el censo no tienen todavía custodia externa confiable ni pruebas de exhaustividad a lo largo de todas las búsquedas y variantes del historial. **No promueve, no opera, no interpreta datos como ventaja.**

## Censo encadenado de intentos (2026-10-26)

`atlas/censo_variantes.py` introduce `construir_evento` y `verificar_censo`: cada intento registrado lleva ID propio, variante, pre-registro, hora UTC y hash del evento anterior. El verificador compara **bytes exactos SHA256**, número de líneas y último hash con un ancla que debe obtenerse de una autoridad de custodia externa, rechaza duplicados, contenido modificado, truncado, reordenamiento y eventos posteriores al corte. **Cada evaluación distinta es un intento:** el censo no debe confundir número de identificadores únicos de variante con la cantidad histórica de intentos efectivamente ejecutados.

`preparar_evidencia_encadenada` une ese cálculo del N a la reconstrucción de operaciones desde barras comprobadas por SHA y señales verificadas contra pre-registros; no acepta ni retornos ni N por argumento. El esquema del registro de intentos requiere poblar el historial real exhaustivo antes de usarse; ninguna entrada histórica se ha inventado o reconstruido sin pruebas. **La autoridad de custodia externa no está implementada:** el parámetro ancla puede aún ser falsificado si el llamador lo inventa. Esto es un control de integridad reproducible local, no una prueba externa de integridad histórica. No se habilita ninguna aprobación.
