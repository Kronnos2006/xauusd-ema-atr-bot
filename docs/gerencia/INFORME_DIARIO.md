# Informe diario del gerente (modo ahorro)

Una sola tarea programada por día (6:52 a. m. Costa Rica). Todos los jefes le reportan al gerente y el gerente le rinde cuentas al usuario. No hay reunión: el gerente solo convoca a un jefe cuando hace falta.

## Paso 1: revisión barata (siempre, sin convocar agentes)
Con comandos directos, sin clonar el repo completo:
- `gh api "repos/Kronnos2006/xauusd-ema-atr-bot/actions/workflows/kt002.yml/runs?per_page=3"` y `kt003.yml`: estado de las corridas.
- `gh api "repos/Kronnos2006/xauusd-ema-atr-bot/commits?since=<hace 24 h>&per_page=50" --jq '.[].commit.message'`: cuántos registros horarios de KT-002 hubo.
- `gh api repos/Kronnos2006/xauusd-ema-atr-bot/contents/data/kt002/resumen.json --jq .content | base64 -d`: cifras de acierto.
- Archivos nuevos o modificados en `docs/propuestas/`.

## Paso 2: convocar jefes solo si hace falta
| Situación | A quién | Cuándo |
|---|---|---|
| Una corrida falló, KT-002 está parado (0 registros en 6 h) o hay algo en cola más de 2 h | jefe-operaciones | Solo ese día |
| Faltan más de 3 horas de KT-002 en 24 h, o el resumen no coincide con las filas | vigia-datos | Solo ese día |
| Hay una propuesta nueva o corregida, o terminó un experimento | desconfiado | Solo ese día |
| Revisión de rutina de los datos de KT-002 | desconfiado | Una vez por semana (lunes) |
| El desconfiado aprobó algo o pidió cambios a una propuesta | mejorador | Solo ese día |
| Se tomó una decisión o cambió el estado de algo | jefe-documentacion | Solo ese día, al final |
Si todo está normal, el gerente no convoca a nadie.

## Paso 3: decidir y registrar
Decisiones en `docs/gerencia/decisiones.md` y llamados de atención en `docs/gerencia/desempeno.md`, solo si los hubo. Commit y push únicamente si algo cambió.

## Paso 4: rendir cuentas al usuario
Un mensaje (`SendUserMessage`) de **máximo 5 líneas**:
- cómo va (una frase);
- cifras clave (registros de KT-002 en 24 h y acierto sin solape con su n);
- decisiones tomadas, si las hubo;
- **solo si aplica**, qué necesita del usuario (uno de los 7 casos de escalamiento).
