# Estructura de gerencia

Creada el 2026-10-20 por pedido del usuario, para automatizar la toma de decisiones y que el usuario no tenga que responder todo.

## Jerarquía

```
Usuario (dueño del proyecto)
└── Gerente general            .claude/agents/gerente.md
    ├── Jefe de Investigación   .claude/agents/mejorador.md
    ├── Jefe de Auditoría       .claude/agents/desconfiado.md
    ├── Jefe de Datos           .claude/agents/vigia-datos.md
    ├── Jefe de Operaciones     .claude/agents/jefe-operaciones.md
    └── Jefe de Documentación   .claude/agents/jefe-documentacion.md
        └── (subordinados de cada jefe: .claude/agents/<area>-<tarea>.md)
```

Todos los jefes le reportan al gerente, y el gerente le rinde cuentas al usuario. Cada nivel le rinde cuentas al de arriba con evidencia. El de arriba puede pedir explicaciones, corregir y registrar llamados de atención. Los subordinados siguen la misma regla con su jefe.

## Funciones únicas (no se pisan)

| Área | Jefe | Hace | No hace |
|---|---|---|---|
| Investigación | mejorador | Estudia resultados y propone variantes nuevas pre-registradas | Aprobarse a sí mismo; tocar lo que ya corre |
| Auditoría | desconfiado | Audita diseños y resultados; aprueba o rechaza con evidencia | Escribir código del proyecto |
| Datos | vigia-datos | Verifica los datos recogidos (huecos, duplicados, hashes, coherencia) | Editar datos |
| Operaciones | jefe-operaciones | Mantiene funcionando workflows, tareas programadas y panel | Interpretar resultados |
| Documentación | jefe-documentacion | Bóveda de Obsidian, README, bitácora y actas | Decidir |

## Quién decide qué

**El gerente decide solo:** lo operativo; la priorización y el reparto de tareas; la creación de subordinados; y la aprobación de mediciones nuevas sin dinero que el desconfiado haya aprobado sin problemas ALTOS ni MEDIOS. Esta última decisión el usuario se la delegó el 2026-10-20.

**Se escala al usuario solo si hay:**
1. dinero real (órdenes, brokers, cuentas, pagos);
2. un holdout sellado que habría que abrir o usar;
3. datos, resultados o registros publicados que habría que borrar o reescribir;
4. un experimento en curso o su registro previo que habría que cambiar;
5. un cambio de reglas del proyecto (`CLAUDE.md`, `AGENTS.md`) o de estos límites;
6. un veto del desconfiado con el que el gerente no está de acuerdo;
7. un colapso que no se arregló tras 2 intentos distintos.

**Independencia del auditor:** el gerente puede corregir al desconfiado por cómo trabaja (falta de evidencia, salirse de su función), pero no puede bajarle la vara ni hacerlo aprobar.

## Registros
- `docs/gerencia/decisiones.md`: cada decisión del gerente.
- `docs/gerencia/desempeno.md`: llamados de atención y correcciones.
- `docs/gerencia/INFORME_DIARIO.md`: cómo el gerente revisa y rinde cuentas cada día (modo ahorro, sin reunión).
