# Informe de estado — Investigación de edge sistemático en XAUUSD

**Fecha:** 2026-07-30
**Alcance:** Estado general de la investigación (qué se probó, qué se descartó, qué sigue en curso). No incluye detalle de infraestructura técnica ni del motor de backtest.

---

## Resumen ejecutivo

Este es un proyecto de **investigación y validación estadística**, no un sistema operando con dinero real. El objetivo es determinar, con rigor metodológico, si existe una ventaja (edge) operable y estadísticamente sostenible en XAUUSD (oro) — antes de considerar cualquier paso hacia capital real.

En diez meses de trabajo se probaron **10 hipótesis** distintas (5 variantes técnicas sobre cruce de EMA, una en timeframe diario, y 4 hipótesis macro/fundamentales). **8 fueron descartadas** tras un proceso de validación diseñado específicamente para evitar autoengaño estadístico. **1 sigue en curso** con reservas documentadas, y **1 quedó pospuesta** (no descartada) por límite estructural de datos disponibles.

Una tasa de descarte alta no es un mal resultado — es la señal de que el proceso de validación está funcionando como debe: filtrando resultados que parecen prometedores en un análisis superficial pero no resisten un examen estadístico más exigente.

---

## Qué es este proyecto (y qué no es)

- **Es** un proceso sistemático de generación y prueba de hipótesis de trading sobre datos históricos, con el estándar de rigor estadístico que se aplicaría a cualquier investigación cuantitativa seria.
- **No** ejecuta órdenes. **No** hay capital real involucrado en ningún punto, en ninguna etapa del proyecto.
- Los "loggers en vivo" mencionados más abajo son de **solo lectura**: registran qué habría hecho una hipótesis si hubiera estado operando, sin colocar ninguna orden real. Sirven como fuente de datos de validación (holdout), no como operativa.

## Disciplina de validación aplicada

Todo resultado en este proyecto pasa por el mismo estándar, sin excepciones, adoptado tras detectar (y corregir) errores metodológicos propios en etapas tempranas:

1. **Separación honesta TRAIN/TEST.** Los parámetros de una estrategia se eligen mirando solo una porción de los datos (TRAIN); el resto (TEST) se evalúa una única vez, con los parámetros ya fijados, sin volver a ajustarlos.
2. **Walk-forward multi-fold**, no un único split. El histórico se corta en varios períodos sucesivos — cada uno es una prueba independiente de si el resultado se sostiene, en vez de depender de que un solo recorte haya caído en un tramo favorable por azar.
3. **Chequeo de "fold dominante".** Antes de confiar en un resultado agregado positivo, se recalcula excluyendo el período más favorable. Si el resultado deja de sostenerse, no se lo cuenta como edge real — es la diferencia entre una ventaja consistente y un solo evento afortunado disfrazado de tendencia.
4. **Criterio de selección estadístico** (t-stat sobre el resultado neto de costos de operar, con un mínimo de observaciones por período) — no "cuál dio más ganancia total", que es fácil de inflar con una muestra chica o un solo trade grande.
5. **Reglas de corte definidas por escrito antes de correr cada prueba.** Qué resultado exacto confirmaría la hipótesis y cuál la descartaría, decidido *antes* de ver los datos — para no mover la meta después de ver el resultado.

## Resultados — hipótesis probadas

| # | Hipótesis | Resultado | Motivo del descarte / estado |
|---|---|---|---|
| 1 | Cruce EMA9/21 (M15, baseline) | Descartada | Único caso con señal de entrada genuina (se sostuvo en 89% de los períodos de prueba), pero el resultado agregado dependía de un solo período — no pasó el chequeo de concentración |
| 2 | Cruce EMA9/21 + filtro de tendencia multi-timeframe (H1) | Descartada | Menos señales, sin mejora de selectividad, resultado neto negativo |
| 3 | Cruce EMA9/21 + filtro de estructura de mercado (máximos/mínimos crecientes) | Descartada | Peor que las variantes anteriores; resultado concentrado en un solo período muy por encima del 100% |
| 4 | Ruptura de estructura + reingreso (retest) | Descartada | Resultado neto agregado negativo, sin ningún período que lo sostenga |
| 5 | Variante H1 con parámetros propios reajustados | Descartada | Minoría de períodos rentables; la significancia estadística se degradaba a medida que se agregaban más datos (señal típica de un patrón ilusorio, no real) |
| 6 | Timeframe diario (D1) | **Pospuesta**, no descartada | Muestra estructuralmente insuficiente (77 operaciones en 11 años). Extender el histórico mezclaría regímenes de mercado no comparables — no es cuestión de esperar más tiempo |
| 7 | Tasas reales de EE.UU. (DFII10) → sesgo direccional en oro | **En curso** | Pasó el filtro exploratorio (3 de 4 períodos rentables) pero con significancia estadística marginal y frágil. No se avanza a la siguiente fase hasta tener una lectura más sólida (ver más abajo) |
| 8 | Pendiente de la curva de tasas 2s10s | Descartada | No pasó el filtro exploratorio inicial |
| 9 | Índice del dólar (DXY, vía proxy sintético validado con 6 pares de divisas) | Descartada | 3 de 4 períodos rentables, pero el resultado no era estadísticamente significativo y dependía en un 59% de un solo período |
| 10 | Ratio oro/plata | Descartada | 4 de 4 períodos rentables, pero tampoco alcanzó significancia estadística; 63% del resultado concentrado en un solo período |

**Lectura de conjunto:** las hipótesis descartadas comparten un patrón — resultados que a primera vista (conteo de períodos ganadores, ganancia total) parecen prometedores, pero que no sobreviven un examen estadístico más riguroso (significancia, dependencia de un único período). Es exactamente el tipo de espejismo que la disciplina de validación de este proyecto está diseñada para detectar antes de invertir más tiempo o, eventualmente, capital real.

## Estado actual

La única hipótesis con trabajo activo es la **#7 (DFII10)**. Su situación:

- Pasó el filtro exploratorio inicial, pero con una lectura estadística débil (no concluyente).
- Antes de diseñar la siguiente etapa de validación, el proyecto está acumulando datos de un **holdout en vivo** — un registro de solo lectura que no vuelve a mirar datos históricos ya usados, sino que espera observaciones genuinamente nuevas hacia adelante. Es la única forma honesta de confirmar un resultado sin caer en el sesgo de "recortar los mismos datos de otra forma hasta que dé bien".
- Este holdout arrancó a fines de julio de 2026. Por la baja frecuencia de la señal que se está probando, todavía no acumuló observaciones suficientes para una lectura — es lo esperable dado el diseño, no una señal de que algo falló.

Ninguna otra hipótesis tiene trabajo activo. La #6 (D1) queda como candidata solo si se agotan otras vías, dado su límite estructural de datos.

## Próximos pasos

1. **Corto plazo (pasivo):** seguir acumulando datos del holdout en vivo de DFII10. No es una tarea con fecha fija — depende de la frecuencia natural con la que ocurre la señal que se está probando.
2. **Cualquier hipótesis nueva** deberá cumplir la misma regla ya vigente desde julio de 2026: una hipótesis puntual y falsable, con su propia regla de corte, definida *antes* de tocar cualquier dato — no una categoría amplia como "probar algo macro".
3. En paralelo, se está reforzando la infraestructura interna de validación (reproducibilidad y trazabilidad de cada prueba) para que cualquier resultado futuro —incluida una eventual confirmación de DFII10— quede documentado de forma auditable desde el primer momento.

## Nota importante

En ningún momento de este proyecto se ejecutaron órdenes reales ni se comprometió capital. Todo lo descrito arriba es investigación sobre datos históricos y un registro de solo lectura hacia adelante. Cualquier paso hacia una implementación con capital real requeriría, como mínimo, que una hipótesis supere tanto el checkpoint exploratorio como una confirmación en el holdout en vivo — algo que, a la fecha de este informe, todavía no ocurrió con ninguna hipótesis.
