# Estructura de gerencia

Creada el 2026-10-20 por pedido del usuario, para automatizar la toma de decisiones y que el usuario no tenga que responder todo.

## Jerarquía

```
Usuario (dueño del proyecto)
└── Gerente general            .claude/agents/gerente.md
    ├── Disciplina (ayudante)   .claude/agents/gerencia-disciplina.md
    ├── Recursos de IA          .claude/agents/jefe-recursos-ia.md     (catálogo y creación de ayudantes)
    ├── Jefe de Investigación   .claude/agents/mejorador.md
    ├── Jefe de Auditoría       .claude/agents/desconfiado.md      (independiente)
    ├── Analista de mercado     .claude/agents/analista.md         (independiente)
    │   ├── Tendencia           .claude/agents/analista-tendencia.md
    │   ├── Macro               .claude/agents/analista-macro.md
    │   └── Ballenas            .claude/agents/analista-ballenas.md
    ├── Jefe de Datos           .claude/agents/vigia-datos.md
    ├── Jefe de Operaciones     .claude/agents/jefe-operaciones.md
    ├── Jefe de Riesgo          .claude/agents/jefe-riesgo.md          (independiente)
    │   └── Costos              .claude/agents/riesgo-costos.md
    ├── Jefe de Portafolio      .claude/agents/jefe-portafolio.md
    │   ├── Réplica             .claude/agents/portafolio-replica.md
    │   ├── Investigador        .claude/agents/portafolio-investigador.md
    │   └── Estratega           .claude/agents/portafolio-estratega.md
    ├── Jefe de Desarrollo      .claude/agents/jefe-desarrollo.md
    │   ├── Diseñador           .claude/agents/desarrollo-disenador.md
    │   ├── Programador         .claude/agents/desarrollo-programador.md
    │   ├── Integrador          .claude/agents/desarrollo-integrador.md   (con Innovación)
    │   └── Reparador           .claude/agents/desarrollo-reparador.md    (lo convoca el gerente ante avisos de la guardia o del vigía)
    ├── Jefe de Documentación   .claude/agents/jefe-documentacion.md
    └── Jefe de Innovación      .claude/agents/jefe-innovacion.md
        └── Noticias            .claude/agents/innovacion-noticias.md
        └── (subordinados de cada jefe: .claude/agents/<area>-<tarea>.md)
```

Todos los jefes le reportan al gerente, y el gerente le rinde cuentas al usuario. Cada nivel le rinde cuentas al de arriba con evidencia. El de arriba puede pedir explicaciones, corregir y registrar llamados de atención. Los subordinados siguen la misma regla con su jefe.

## Funciones únicas (no se pisan)

| Área | Jefe | Hace | No hace |
|---|---|---|---|
| Investigación | mejorador | Estudia resultados y propone variantes nuevas pre-registradas | Aprobarse a sí mismo; tocar lo que ya corre |
| Auditoría | desconfiado | Audita diseños y resultados; aprueba o rechaza con evidencia | Escribir código del proyecto |
| Mercado | analista | Analiza BTC, oro, dólar, petróleo, ballenas y noticias; dice si el mercado está alcista, bajista o lateral con reglas fijas | Dar señales de trading; cambiar modelos o mediciones |
| Datos | vigia-datos | Verifica los datos recogidos (huecos, duplicados, hashes, coherencia) | Editar datos |
| Operaciones | jefe-operaciones | Mantiene funcionando workflows, tareas programadas y panel | Interpretar resultados |
| Riesgo | jefe-riesgo | Límites escritos antes de cualquier estrategia, costos reales, veto y apagado de simulaciones | Operar; cambiar modelos o datos |
| Portafolio | jefe-portafolio | Libro de estrategias; portafolios en papel con datos públicos de portafolios grandes, con registro previo | Dinero real; simular sin registro ni auditorías |
| Recursos de IA | jefe-recursos-ia | Catálogo de ayudantes, propone y crea los que eligen los jefes o el gerente, retira los que no sirven | Elegir por otros; dirigir trabajo; tocar a los independientes |
| Desarrollo | jefe-desarrollo | Calidad del código, metas para el código, implementa los cambios que deciden el usuario o el gerente (en ramas, con pruebas) y pasa el reporte a Documentación. Puede crear sus propios ayudantes | Cambiar experimentos en curso sin OK del usuario; tocar al desconfiado o al analista |
| Documentación | jefe-documentacion | Bóveda de Obsidian, README, bitácora y actas | Decidir |
| Innovación | jefe-innovacion | Busca skills, repos, agentes, plugins, conectores e ideas; detecta conectores caídos; noticias que afectan predicciones (subordinado `innovacion-noticias`) | Instalar, pagar o cambiar modelos; lo que afecte predicciones va al mejorador y al desconfiado |

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

**Independencia del jefe de riesgo (2026-10-21):** igual que el desconfiado y el analista; sus límites y vetos solo los cambia el usuario.

**Independencia del analista (decisión del usuario, 2026-10-21):** misma autoridad que el desconfiado. El gerente lo convoca y lee sus informes, pero no puede cambiar sus reglas, sus ayudantes, sus conclusiones ni sus archivos sin permiso explícito del usuario. Un desacuerdo con el analista se le plantea al usuario.

## Contrataciones
Cada jefe crea sus propios ayudantes con su criterio (decisión del usuario, 2026-10-21): ver `CONTRATACION.md`. La lista viva del equipo está en `equipo.json`, que alimenta el organigrama de la Oficina y del visor.

## Registros
- `docs/gerencia/decisiones.md`: cada decisión del gerente.
- `docs/gerencia/desempeno.md`: llamados de atención y correcciones.
- `docs/gerencia/INFORME_DIARIO.md`: cómo el gerente revisa y rinde cuentas cada día (modo ahorro, sin reunión).
