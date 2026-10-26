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
