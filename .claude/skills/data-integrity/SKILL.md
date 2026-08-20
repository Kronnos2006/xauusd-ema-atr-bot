---
name: data-integrity
description: Playbook de verificación de integridad para cualquier archivo de datos crudos nuevo (macro, precios, o cualquier fuente externa) — checksum, continuidad temporal, y detección de revisiones retroactivas de la fuente. Correr al descargar un dato nuevo por primera vez, y mensualmente sobre los datos macro ya en uso.
---

# Data Integrity

Este proyecto ya encontró, más de una vez, que un dato "obviamente confiable" no lo era del todo sin verificarlo (el `MergeError` de resolución datetime64 en la hipótesis MTF, el resguardo contra backfillear un episodio viejo como señal fresca en el logger DFII10, la verificación cruzada FRED vs. Treasury.gov). Este skill junta esa disciplina dispersa en un solo lugar, aplicable a cualquier archivo de datos nuevo, no solo a los que ya la tuvieron.

Complementa a `hypothesis-gate` (que verifica el dato al momento de evaluar UNA hipótesis) con un chequeo que no depende de estar evaluando nada — corre por su cuenta, sobre los datos que ya están en uso, para detectar si algo cambió por debajo sin que nadie lo pidiera.

## Los tres chequeos

Script de referencia: `verificar_integridad_datos.py` (funciones reusables, sin dependencias más allá de `pandas`/`hashlib`/lo que ya usa el proyecto).

### 1. Checksum SHA256 al descargar

Cada vez que se descarga un archivo de datos crudo por primera vez (o se re-descarga), calcular su SHA256 y registrarlo en `registro_checksums.json` (en la raíz del proyecto, **versionado en git a propósito** — a diferencia de los datos crudos en sí, que `historial/` ignora — para que el historial de checksums sobreviva en el log de commits aunque el dato no esté ahí). Si al volver a calcular el checksum de un archivo ya registrado da distinto sin que nadie lo haya vuelto a descargar intencionalmente, es una señal de alerta: el archivo cambió por una vía no controlada (edición manual, corrupción, sincronización de OneDrive, etc.).

### 2. Verificación de continuidad temporal

Sobre cualquier serie de tiempo nueva, antes de usarla en un backtest:

- **Sin huecos mayores a N días** en la frecuencia esperada de la serie (diaria, semanal) — un hueco de más de N días hábiles puede ser un feriado real (esperable) o un error de descarga (no esperable); el chequeo no distingue automáticamente entre ambos, pero señala el hueco para que se revise a mano, mismo criterio ya usado para distinguir sleep de caída real en `infra-ops-playbook`.
- **Sin fechas duplicadas.**
- **Valores dentro de un rango plausible** (a definir por serie — ej. una tasa de interés real difícilmente esté fuera de -5% a +15%, un índice de dólar difícilmente fuera de 50-150). El rango es un chequeo de sanidad grueso, no una validación estadística — su único trabajo es atrapar errores obvios (un `NaN` mal parseado como 0, un punto decimal corrido).

### 3. Chequeo mensual contra la fuente pública (revisiones retroactivas)

Para series que SÍ pueden ser revisadas después de publicadas (a diferencia de series de mercado como DFII10, que no lo son — ver la verificación real hecha para DFII10 en [[Macro DFII10 - fase 1]]#Auditoría de robustez, que sirve de plantilla): comparar periódicamente (mensual alcanza, no hace falta más seguido) una muestra de fechas históricas ya usadas en algún backtest contra el valor actual de la fuente pública (FRED/ALFRED u otra). Si el valor cambió, dos casos:

- **Cambió una fecha reciente** (dentro de la ventana normal de revisión de esa serie, ej. PBI se revisa varias veces en los meses siguientes a su publicación inicial): esperable, no es una alarma, pero sí hay que verificar que el HOLDOUT EN VIVO no esté usando el valor todavía no revisado como si fuera final.
- **Cambió una fecha vieja, ya usada hace años en un walk-forward**: esto es más serio — significa que el backtest se corrió con datos que en su momento no existían así, un caso de look-ahead bias retroactivo. Documentar como hallazgo, no ignorar, y re-evaluar si la hipótesis en cuestión sigue siendo válida con el valor histórico real (vía ALFRED) en vez del valor actual.

No hace falta desplegar esto como una tarea automática de Task Scheduler en esta etapa (no hay presión de tiempo — una revisión retroactiva no aparece de un día para el otro) — correrlo a mano una vez al mes alcanza. Si en algún momento se automatiza (mismo patrón que el monitor de holdout de DFII10, ver `Infraestructura` en el vault), documentarlo ahí.

## Cuándo correr esto

- **Al descargar cualquier archivo de datos crudo por primera vez**: checksum + continuidad, antes de que ese dato entre a un `hypothesis-gate`.
- **Una vez al mes, a mano**, sobre todas las series macro/externas ya en uso (hoy: DFII10, T10Y2Y aunque esté descartada, los 6 pares FX del DXY sintético) — chequeo de revisión retroactiva.
- **Cuando algo se ve raro** en un resultado (un backtest que de repente da distinto sin que el código haya cambiado) — el primer sospechoso es un dato que cambió por debajo, no un bug de lógica.

## Por qué importa

La disciplina de walk-forward de este proyecto asume que el dato usado en TRAIN y TEST es el dato real, tal como existía en cada momento. Si el dato en sí puede cambiar silenciosamente (por una revisión de la fuente, o por una corrupción local no detectada), toda esa disciplina metodológica se apoya sobre un piso que nadie verificó. Es barato verificarlo una vez al mes; es caro descubrir después de meses de holdout que el dato de entrada nunca fue el correcto.
