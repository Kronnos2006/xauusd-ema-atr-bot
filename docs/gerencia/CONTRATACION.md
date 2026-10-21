# Contratación de ayudantes (cada jefe con su propio criterio)

Decisión del usuario, 2026-10-21: para crecer rápido, **cada jefe crea ("contrata") los ayudantes que necesite**, sin esperar que se lo pidan. Ejemplos: Desarrollo ve una falla que se repite y crea un reparador; Portafolio tiene una hipótesis en curso, aparece otra y crea un investigador aparte para desarrollarla en paralelo.

## Cuándo contratar
- Hay **trabajo que espera** porque el equipo actual está ocupado (por ejemplo, una segunda hipótesis).
- Una **falla o tarea se repite** y conviene que alguien se especialice.
- Hace falta una **habilidad** que nadie del área tiene.
Si alcanza con pedirle algo a un ayudante que ya existe, no se contrata.

## Cómo
1. Copiar `docs/gerencia/PLANTILLA_AYUDANTE.md` a `.claude/agents/<area>-<tarea>.md` (por ejemplo `portafolio-investigador-hp002.md`) y completarlo: una sola función, a quién reporta, qué no le toca, cómo informa.
2. Agregarlo a `docs/gerencia/equipo.json` (eso lo hace aparecer en el organigrama de la Oficina y del visor) con `creado_por` = el jefe y `estado: "activo"`.
3. Una línea en `docs/gerencia/decisiones.md`: quién lo creó, para qué y hasta cuándo.
4. Commit y push. En el informe al gerente: "Contraté a X para Y".
5. Hasta que una sesión nueva lo cargue, se lo convoca como `general-purpose` con su archivo como rol. Como un subagente no puede convocar a otro, **el jefe le pide al gerente** que convoque a su ayudante y le pase el resultado.

## Límites (control de gasto y de calidad)
- **Modelo económico (sonnet) por defecto.** Usar el modelo de la cuenta solo si la tarea lo justifica, y decirlo.
- **Máximo 5 ayudantes activos por jefe.** Más que eso requiere OK del gerente.
- **Ayudantes temporales** (una hipótesis, una falla): al terminar se marcan `estado: "retirado"` en `equipo.json` y se mueve su archivo a `.claude/agents/retirados/`. No se borra la historia.
- Cada ayudante **hereda todos los límites** de su jefe y del proyecto: sin dinero ni órdenes, sin cambiar experimentos en curso, sin tocar datos o registros publicados, sin tocar a los independientes.
- Jefes de **solo lectura** (operaciones, vigía de datos): le piden al gerente o a Desarrollo que cree el archivo por ellos.
- **Independientes** (desconfiado, analista, jefe de riesgo): pueden contratar sus propios ayudantes con el mismo procedimiento. El gerente no puede crearles, cambiarles ni quitarles ayudantes.
- **Disciplina** revisa los viernes que cada ayudante contratado trabaje; uno que no aporta se retira.
