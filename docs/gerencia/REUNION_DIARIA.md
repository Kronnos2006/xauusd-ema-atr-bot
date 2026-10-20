# Reunión diaria de la mesa directiva

La convoca el gerente todos los días (tarea programada, 6:57 a. m. Costa Rica). Reemplaza a la auditoría diaria separada del desconfiado: él participa como Jefe de Auditoría.

## Orden del día
1. **Operaciones** (`jefe-operaciones`): estado de KT-002, KT-003, tareas programadas y panel en las últimas 24 h.
2. **Datos** (`vigia-datos`): calidad de lo recogido (filas nuevas, horas omitidas, duplicados, coherencia del resumen, hashes).
3. **Auditoría** (`desconfiado`): auditoría de los resultados y cambios nuevos de las últimas 24 h, con veredicto.
4. **Investigación** (`mejorador`): avance de las propuestas y si hay algo nuevo que proponer.
5. **Decisiones del gerente**: qué se aprueba, qué se corrige y quién hace qué hoy. Cada decisión va a `docs/gerencia/decisiones.md`.
6. **Llamados de atención**, si los hubo, en `docs/gerencia/desempeno.md`.
7. **Documentación** (`jefe-documentacion`): escribe el acta y actualiza las notas afectadas.

Cada jefe responde con su formato de informe y con evidencia (archivo, comando, cifra). Si un jefe no trae evidencia, el gerente se lo marca.

## Acta
`XAUUSD EMA/ATR/Reuniones/AAAA-MM-DD.md`, con la plantilla `XAUUSD EMA/ATR/Reuniones/_Plantilla de acta.md`.

## Resumen al usuario
Máximo 8 líneas, en lenguaje sencillo:
- cómo va el proyecto en una frase;
- cifras clave del día (acierto de KT-002 sin solape, n y estado de las propuestas);
- decisiones que tomó el gerente;
- **solo si aplica**, lo que necesita del usuario (uno de los 7 casos de escalamiento).

## Al terminar
Commit y push de las actas, decisiones y notas de documentación (nunca datos ni resultados). Sin force push.
