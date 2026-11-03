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
