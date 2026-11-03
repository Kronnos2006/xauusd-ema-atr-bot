# ATLAS: conciliación del alcance del censo original

Fecha local: 2026-11-02, Costa Rica. Fuente fijada: commit 9b39ff94437655773efdaf39c4dcc714340cf100. Se compararon las reglas REGLAS del generador original con las rutas de ese mismo árbol, leídas en UTF-8 con separador nulo. Se consultaron el código y el censo versionados con git show, sin ejecutar el generador ni abrir reservas.

| Categoría | Registros |
|---|---:|
| Scripts | 44 |
| Notas | 13 |
| Tesis | 7 |
| Corridas 0031 | 7 |
| Asesores expertos | 3 |
| Total | 74 |

Hay 74 identificadores de intento distintos y 70 identificadores de variante distintos. Dos variantes de tesis aparecen tres veces cada una. Una variante repetida puede representar varias evaluaciones. Los scripts, notas y ejecuciones son categorías distintas, por lo que el recuento tampoco prueba que cada artefacto sea un ensayo estadístico separado.

## Omisiones verificadas

Tres rutas que satisfacen las reglas de inclusión están en el árbol original pero no en el censo:

- XAUUSD EMA/ATR/KT-002 — Acierto prospectivo BTC.md
- XAUUSD EMA/ATR/KT-003 — Diagnóstico histórico BTC.md
- XAUUSD EMA/ATR/TF_Basket_H1 — Fase 0.md

El generador usa git ls-files en formato de líneas. Con la configuración predeterminada, Git entrecomilla las rutas con caracteres no ASCII, por lo que las expresiones ancladas al inicio de la ruta pueden perder esas entradas. La comparación se hizo con git ls-tree -rz --name-only 9b39ff9, que entrega los nombres sin ese entrecomillado. La corrección para un inventario posterior es leer git ls-files -z y separar por NUL.

La fecha que el generador llama ejecutado_utc viene de la fecha de committer del alta del artefacto. Sirve para trazar el historial, pero no establece cuándo se ejecutó un ensayo. Las asociaciones de prerregistro por nombre requieren verificación independiente.

Conservar los 74 registros originales y sus sellos. La conciliación siguiente debe relacionar cada artefacto con evidencia de ejecución, ID de corrida, variante y versión, además de separar repeticiones de duplicados documentales. Los tres archivos omitidos son candidatos a conciliación. El resultado no autoriza aumentar el N de DSR de 74 a 77 ni cerrar F2.

## Corrección preparada

El PR #105 agrega el modo --rutas-completas sobre la rama que contiene el generador original. Requiere --salida con un directorio nuevo fuera de research/atlas/censo. El modo anterior sigue disponible para reproducir el sello.

Sobre el mismo árbol, el modo histórico reprodujo los 74 registros byte por byte. El diagnóstico de rutas completas produjo 77 artefactos y recuperó las tres notas identificadas. Pasaron las 15 pruebas del censo y se verificó que el modo nuevo rechaza tanto la carpeta sellada como una salida ya existente.

El PR permanece en borrador. Antes de integrarlo, revisar el disparador push de atlas-custodia.yml en la rama base, porque una integración allí puede iniciar solicitudes a las autoridades de sellado. El diagnóstico queda separado de la evidencia sellada y de cualquier N confirmatorio.

## Verificación de barreras en el PR #42

El head del PR consultado es 3c943e96647b7bdc03abb06a913bb826bfdb9fe0. En un worktree separado de ese commit se ejecutó python -B -m unittest tests.test_atlas_barreras tests.test_atlas_evidencia tests.test_atlas_censo -q. Pasaron 41 pruebas sintéticas en 0,131 segundos. Las pruebas construyen su evidencia en directorios temporales.

Cobertura comprobada: rechazo de censos manipulados, duplicados y recortados; rechazo de inventario declarado sin autenticación; verificación de orden temporal del sello y vínculo con la señal; rechazo de barras alteradas y retornos inventados; mínimo de 30 operaciones por fold; reporte del fold dominante y varianza entre ensayos como diagnósticos. La prueba test_confirmatorio_sigue_cerrado confirma que la ruta confirmatoria permanece bloqueada.

La entrada autenticado=True en fixtures prueba la conciliación después de un supuesto de confianza. La autenticación real del inventario requiere una fuente externa, su vínculo verificable con los intentos y una política de custodia. Los sellos del censo recuperado prueban contenido y fecha del manifiesto, mientras que el total estadístico exige la conciliación de los artefactos con ejecuciones. F2 sigue abierto hasta tener ambas piezas y validar los folds con el protocolo aprobado. PR #42 permanece en borrador.

## Conciliación de las tres notas recuperadas

| Nota | Evidencia localizada | Clasificación para conciliación |
|---|---|---|
| KT-002, acierto prospectivo BTC | El job pronosticar de la corrida 39440365971 registró la base 13:00 UTC a las 14:35:37 UTC del 20-oct. El primer commit del CSV es 6a7cf49, de ese mismo segundo. | La nota describe un protocolo y su monitor prospectivo. La corrida identifica una emisión. Falta definir la familia estadística aplicable y su relación con las repeticiones horarias antes de contar ensayos. |
| KT-003, diagnóstico histórico BTC | El registro de ejecución de df45730 identifica modo completo, run 39450116803 y SHA 6971d03fd1e4d582b66de0b7de3934e4fa7f4c62. La API confirma que esa corrida del workflow kt003.yml terminó correctamente. | La nota apunta a una ejecución histórica identificada. El número de variantes evaluadas y su pertenencia a la familia confirmatoria requieren conciliación. |
| TF_Basket_H1, Fase 0 | La nota describe tres rondas de diagnóstico. El censo original ya enumera diagnostico_frecuencia_tf_basket_h1.py, mde_trend_following_tf_basket_h1.py y calibracion_efecto_tf_basket_h1.py. El commit 30df13a documenta el cierre en triage. | La nota agrupa evidencia de artefactos ya registrados. No hay una ejecución adicional identificada por la nota ni logs autenticados para cada variante. |

Fuentes remotas:
- KT-002: https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39440365971
- KT-003: https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/39450116803
- Registro KT-003: https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/df45730/data/kt003/ejecucion.txt
- Cierre TF_Basket_H1: https://github.com/Kronnos2006/xauusd-ema-atr-bot/commit/30df13a

La conciliación usa metadatos, el log de la primera emisión de KT-002 y las notas versionadas. La custodia independiente y el inventario exhaustivo siguen pendientes. Los 77 artefactos del diagnóstico Unicode conservan su carácter documental.
