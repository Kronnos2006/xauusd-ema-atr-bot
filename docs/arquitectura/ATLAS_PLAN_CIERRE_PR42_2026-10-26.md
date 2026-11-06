# Plan ejecutable de cierre PR #42 — 2026-10-26

Estado: **PARCIAL / NO CERTIFICADO**. Autor de cambios ChatGPT; revisión externa nueva obligatoria.
No alterar KT-002, holdout, estrategias ni permisos de trading.

## Orden y puertas
1. H1 (hecho en rama): la API descriptiva no marca jamás `pasa_barreras_estadisticas` como true; el DSR queda como dato diagnóstico sin procedencia certificada. Tests: retornos inventados, umbral alto, sin promoción.
2. H2 (endurecimiento inicial en rama): el sello comprueba ID, ID de señal, posición, publicación exacta y workflow `completed/success` antes de la publicación. Tests: ejecución fallida y sustitución de señal. Pendiente: demostrar origen remoto autenticado de proveedor/commit y hash de barra temporal; la inyección en tests no es prueba de custodia.
3. H4 (PENDIENTE): registrar definición **antes** del intento, resultado como nuevo evento inmutable; anclaje por lote a commit firmado y clave confiable fuera del alcance del invocador. El evaluador debe resolver ancla desde política, no aceptarla como argumento. No certificar exhaustividad retrospectiva sin reconciliación completa de todos los intentos.
4. H3 (PENDIENTE): protocolizar elección de estimador DSR antes de observar resultados, fórmula actual y supuesto de independencia, número nominal íntegro, estimación de varianza observada entre ensayos cuando haya matriz de retornos admisible. Correlación media no implica automáticamente N efectivo del DSR. Bootstrap por bloques con parámetros pre-registrados; si falta matriz o incertidumbre confiable => INCONCLUSA.
5. Integración (PENDIENTE): actualizar rama con master, ejecutar CI, probar ataques adversariales 1/2/3 y obtener auditoría nueva sin contexto del autor.
6. Cierre (PENDIENTE): si y solo si la custodia y procedencia quedan verificadas, emitir dictamen de software; jamás prometer rentabilidad ni habilitar trading real.

## Política de decisiones
- RECHAZADA: evidencia autenticada y prueba previamente fijada incumple.
- INCONCLUSA: falta custodia, procedencia, muestra o incertidumbre válida.
- CANDIDATA_PARA_VALIDACION: controles técnicos, estadísticos y de procedencia reproducibles superados; solo pasa a nueva fase prospectiva.
- La antigua `evaluar_confirmatorio` permanece bloqueada sin excepción hasta auditoría de todos esos componentes.
