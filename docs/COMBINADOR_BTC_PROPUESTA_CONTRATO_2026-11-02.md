# Combinador BTCUSDT: contrato de evaluación propuesto

2 de noviembre de 2026, Costa Rica. Borrador para discusión antes del prerregistro. La lista de modelos, los pesos, la regla de posición, los costos y el corte confirmatorio requieren decisión explícita.

## Reproducción del problema de emparejamiento

Se ejecutó combine() con entradas sintéticas para BTCUSDT. La primera fila tenía intervalo 12:00–16:00 UTC, emisión 11:55 y valor +0,02. La segunda tenía intervalo 15:00–16:00 UTC, emisión 15:30 y valor −0,01. Ambas se combinaron en un grupo con valor 0,005 porque la clave usa instrumento y hora final. El inicio del objetivo adicional se ignoró. Agregar una tercera fila con valor +0,03 cambió el grupo a tres miembros y su promedio a 0,013333. Así, EQUAL_FIXED describe la igualdad dentro de cada grupo, mientras el peso efectivo por modelo cambia cuando falta un miembro.

## Contrato mínimo propuesto

- Identidad común: mercado BTCUSDT Spot, inicio y fin de objetivo UTC, horizonte 4 h, unidad retorno simple open/open, versión del protocolo y corte planificado.
- Temporalidad: cada predicción debe quedar observada antes de la apertura objetivo. El recibo verificable enlaza modelo, ejecución, imagen, versión y hash de entradas. El hash del CSV por sí solo prueba coincidencia de bytes.
- Cobertura: conservar una fila por modelo y corte programado. Registrar no emitido, tarde, inválido o abstención. Con pesos fijos, el conjunto incompleto se registra como abstención del combinador, sin renormalizar entre miembros presentes. Es una propuesta para aprobar antes de evaluar.
- Comparadores: «siempre sube» y cada componente evaluados en los mismos cortes. Baseline separado del conjunto candidato. Informar cobertura y diferencias de acierto por pares con el tratamiento de faltantes aprobado de antemano.
- Resultados por corte: conservar pronóstico, referencia, dirección observada y retorno objetivo, más el indicador de acierto de cada serie. Mantener por separado los resultados de Fase 0 y la muestra prospectiva.

## Capa de costos, decisión pendiente

El acierto direccional y el retorno neto son evaluaciones separadas. Antes de simular posiciones debe fijarse la conversión de pronóstico a exposición, el reloj de ejecución, el estado de caja ante fallos y los límites de riesgo. Una forma de llevar costos consiste en registrar cada cambio de exposición y aplicar comisión, spread y deslizamiento sobre el nominal negociado, con la misma convención para los comparadores. Si se usa una orden de entrada y otra de salida para cada corte, se contabilizan ambas. La comparación neta exige fuentes y tasas versionadas, marcas de precio elegibles y escenarios de estrés fijados previamente.

El siguiente insumo necesario es una serie prospectiva de componentes en unidades compatibles. FreqAI histórico a una hora y KT-002 cierre a cierre con emisión posterior al inicio del retorno requieren productores alineados al nuevo contrato antes de entrar en la misma comparación. La prueba aquí solo inspeccionó el combinador con filas sintéticas.
