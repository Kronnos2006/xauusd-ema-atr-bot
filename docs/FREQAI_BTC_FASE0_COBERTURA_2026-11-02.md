# FreqAI: cobertura histórica y sensibilidad de potencia

Fecha local: 2026-11-02, Costa Rica. Se eligió septiembre de 2025 porque el repositorio ya lo usa como mes público de diagnóstico. Esta ventana se destina al diseño de Fase 0.

Fuente: https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2025-09.zip

El descargador existente validó el archivo contra el CHECKSUM de Binance. SHA-256 del ZIP: b0ad5b54097f6adb440d07204fd215dae9b224fb73569fd4309a55c9234d46b3. CSV normalizado: c8b3ca1bab35ec2e7fdd8054b1a03f9849317cdb3cc6474907765f646724043b.

| Control | Resultado |
|---|---:|
| Horas esperadas y presentes | 720/720 |
| Cortes programados a 4 h | 180 |
| Etiquetas open/open observables | 179 |
| Cortes con etiqueta y contexto horario completo | 172 |
| Etiquetas de subida/bajada/cero en los 179 cortes | 84/95/0 |
| Etiquetas de subida/bajada/cero en los 172 cortes con contexto | 79/93/0 |

Se tomó cada apertura UTC múltiplo de 4 h y se exigió la apertura en base +4 h para la etiqueta. Para el contexto se exigieron las 25 barras con aperturas de base −26 h a base −2 h, ambas inclusive, suficientes para un retorno de 24 h entre cierres. El último corte necesita la apertura del mes siguiente. Los primeros siete cortes carecen de contexto anterior al mes. Son efectos de borde del extracto. El ejercicio verifica cobertura de entradas y etiquetas, por separado de la ventana de entrenamiento de 365 días y de la disponibilidad efectiva al emitir.

## Sensibilidad para diseñar la muestra

Para una mejora propuesta de 2 puntos porcentuales, alfa unilateral 5% y potencia 80%, la aproximación normal con pares independientes usa n = techo((z0,95 + z0,80)^2 × q / 0,02^2). q es la fracción supuesta de pares donde difieren los aciertos del candidato y el baseline.

| Discordancia supuesta | Pares aproximados | Días mínimos a seis cortes diarios |
|---:|---:|---:|
| 10% | 1546 | 258 |
| 25% | 3865 | 645 |
| 50% | 7729 | 1289 |

Los supuestos de discordancia son escenarios. El horizonte sin solape todavía puede tener dependencia serial. La potencia definitiva requiere un método temporal preregistrado, calibración independiente de su muestra confirmatoria y ajuste por cobertura. El diagnóstico emplea etiquetas históricas del archivo público, sin generar pronósticos ni acceder a reservas. La decisión metodológica de Fase 1 permanece pendiente.

## Ventana histórica de 365 días

Se verificaron doce archivos mensuales públicos desde el 1 de septiembre de 2024, inclusive, hasta el 1 de septiembre de 2025, exclusivo. Los CHECKSUM de Binance coincidieron y se comprobó de nuevo el hash de cada CSV antes de contar las horas.

- 8760 de 8760 horas, sin huecos, duplicados ni fechas fuera de rango.
- 2190 cortes de 4 h, de los cuales 2182 tienen contexto y etiqueta dentro de la ventana. Siete cortes pierden contexto al comienzo y uno necesita la apertura posterior al final.
- La ventana acredita cobertura de una reconstrucción histórica. El registro de disponibilidad y latencia en el momento de emitir se verificará en una evaluación prospectiva.

El [manifiesto de la ventana](FREQAI_BTC_FASE0_VENTANA_365D_2026-11-02.json) contiene las doce URLs y los hashes SHA-256. Se utilizó tools/kronnos_binance_vision_archive.py para cada mes. El conteo compara time_open_ms con la rejilla horaria UTC y aplica las reglas de contexto y objetivo descritas arriba.
