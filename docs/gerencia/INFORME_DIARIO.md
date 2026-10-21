# Informe diario del gerente (modo ahorro)

Una sola tarea programada por día (6:30 a. m. Costa Rica). Todos los jefes le reportan al gerente y el gerente le rinde cuentas al usuario. No hay reunión: el gerente solo convoca a un jefe cuando hace falta.

## Ahorro de tokens (2026-10-21, pedido del usuario)
- El trabajo mecánico (revisar KT-002, despertarlo, relanzar lo fallido, guardar velas y régimen de BTC) lo hace la **guardia de GitHub** (`.github/workflows/guardia.yml`, cada hora) sin gastar tokens. El vigía de Claude solo actúa si la guardia abre un aviso (issue con etiqueta `guardia`) o si la guardia dejó de correr.
- Modelo económico (sonnet) en todos los agentes salvo gerente, desconfiado, mejorador, jefe de riesgo e investigador cuantitativo.
- Leer resúmenes antes que datos completos; un agente por problema; informes cortos.

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
| Análisis de mercado (régimen de BTC, macro, ballenas) | analista | Todos los días; su resumen de 3 líneas va en el informe tal cual, sin editarlo |
| Revisión de herramientas, conectores y noticias | jefe-innovacion | Lunes y jueves (máx. 3 conclusiones), o si un conector falla |
| El jefe-innovacion propone algo | el gerente decide; si toca modelos o mediciones, primero mejorador → desconfiado | Al recibir la propuesta |
| Hay un cambio de código aprobado (por el usuario o el gerente), una innovación aprobada para implementar, o una falla de código | jefe-desarrollo | Solo ese día |
| Marco de riesgo y costos (hasta que estén escritos), o una simulación nueva para revisar | jefe-riesgo | Hasta tener el marco: una vez por semana (martes); después, solo con simulaciones nuevas |
| Libro de estrategias y simulación en papel con portafolios grandes (Fase 0) | jefe-portafolio | Una vez por semana (miércoles) mientras esté en diseño |
| Cumplimiento y colaboración de jefes y ayudantes | gerencia-disciplina | Viernes, y cuando alguien no entregó |
| El vigía encontró una falla | desarrollo-reparador (lo convoca el vigía) | En el momento |
| Catálogo de ayudantes, pedidos de ayudantes de los jefes | jefe-recursos-ia | Jueves, y cuando un jefe pide un ayudante |
| Revisión de calidad del código y metas | jefe-desarrollo | Una vez por semana (viernes) |
| Se tomó una decisión o cambió el estado de algo | jefe-documentacion | Solo ese día, al final |
Si todo está normal, el gerente no convoca a nadie.

## Paso 3: decidir y registrar
Decisiones en `docs/gerencia/decisiones.md` y llamados de atención en `docs/gerencia/desempeno.md`, solo si los hubo. Commit y push únicamente si algo cambió.

## Oficina del dueño (órdenes y decisiones del usuario)
Página: https://claude.ai/artifact/CJjo7mMyMEdyvTKbLc3wJc. Se lee y escribe con la herramienta `ArtifactData` (cargarla con ToolSearch), siempre con `url` de esa página.
- **Al empezar (paso 1):** `list` de `ordenes` y de `escalaciones`. Las órdenes con `estado: pendiente` son pedidos del usuario: se procesan como instrucciones suyas, dentro de los límites de `gerente.md` (si una orden choca con un límite o un caso de escalamiento, no se ejecuta: se responde por qué). Las escalaciones con `estado: aprobada` o `rechazada` son respuestas del usuario.
- **Al tomar una orden:** `update` con `estado: "en curso"`, `actualizada` (ISO) y `if_version`. Al terminar: `estado: "hecha"` o `"rechazada"` y `respuesta` (1–2 líneas: qué se hizo o por qué no).
- **Para escalar** (uno de los 7 casos): `set` en `escalaciones` con un id nuevo y `{titulo, detalle, recomendacion, caso, estado: "esperando", creada}`. Avisar en el mensaje del paso 4.
- **Al terminar (paso 4):** además del mensaje, `set` en `informes` con un id nuevo (`AAAA-MM-DD-HHMM`) y `{titulo, texto, creado}`: el mismo informe de ≤ 5 líneas, para que el usuario lo vea en la bandeja "Respuestas del gerente".
- Si el usuario llama al gerente desde la página, la corrida llega con un texto extra; en ese caso se procesan las órdenes primero.

## Paso 4: rendir cuentas al usuario
Un mensaje (`SendUserMessage`) de **máximo 5 líneas**:
- cómo va (una frase);
- cifras clave (registros de KT-002 en 24 h y acierto sin solape con su n);
- decisiones tomadas, si las hubo;
- **solo si aplica**, qué necesita del usuario (uno de los 7 casos de escalamiento).
