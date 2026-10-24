# Reversión de la reparación ORION (PR #32)

Fecha: 2026-10-23. Autor: Claude (Anthropic). Revisor: ChatGPT (pendiente). Ninguna reversión toca `data/`, predicciones ni el preregistro de KT-002.

## 1. Código (después de fusionar el PR #32)
- Reversión normal, sin force: `git revert -m 1 <sha del merge del PR #32>` en una rama `revert/orion-AAAAMMDD`, PR y aprobación del propietario. Restaura la guardia anterior y quita del `kt002.yml` el disparo de la guardia y `actions: write`.
- Efecto en KT-002: ninguno sobre la medición. Cambiar `kt002.yml` en master encola una corrida de KT-002 (disparador `push` por ruta). Esa corrida espera en el grupo `kt002` detrás de la que esté en curso, sin tocarla.
- **Reemplazo automático de GitHub:** con `concurrency` y `cancel-in-progress: false`, GitHub deja **una sola corrida pendiente** por grupo. Si llega otra (cron, push, guardia o manual), marca como `cancelled` la pendiente anterior, que nunca arrancó. No es una cancelación de un agente, no pierde datos y no toca la corrida en curso. Se reconoce porque la cancelada nunca tuvo pasos y otra corrida del mismo grupo se creó en el mismo segundo. Ejemplo real: KT-002 #23 (creada 22:02:41Z) pasó a `cancelled` a las 00:30:38Z, al crearse #24 (00:30:37Z). Con la guardia nueva habrá más reemplazos de corridas pendientes de la propia guardia (disparo horario de KT-002, más cron, más manual), todos inocuos.
- Corridas KT-002 pendientes al revertir: no hace falta tocarlas. Esperan en el grupo y corren con el `kt002.yml` vigente cuando arrancan (sin el disparo de la guardia si ya se revirtió).
- Apagado rápido de la guardia, sin código (decisión del propietario): `gh workflow disable guardia.yml`. KT-002 sigue igual: su disparo a la guardia falla con un aviso (`::warning::`) y la medición continúa.

## 2. Tareas programadas de Claude
Las dos se cambian con `update_trigger` (mismo id, se conserva el historial).

### Vigía `trig_01R2brVLcYG6yfbMzA5uimhm`
- Versión vigente desde 2026-10-24T01:22:44Z: protección provisional (solo lee y escala al gerente; no cancela, reinicia ni relanza). Texto en `docs/ops/VIGIA_PROMPT_v2.md` (sección de la protección provisional).
- La v1 **no debe restaurarse**: convocaba al reparador y permitía relanzar, y con ella se canceló la corrida #19 el 2026-10-23.
- Texto v1, solo como registro:

> Sos el vigía de datos del repo Kronnos2006/xauusd-ema-atr-bot (proyecto de Kensy). Español, corto, MODO AHORRO MÁXIMO. La guardia de GitHub (.github/workflows/guardia.yml, cada hora) ya hace el trabajo mecánico: revisa KT-002, lo despierta, relanza lo fallido y abre un aviso (issue con etiqueta "guardia") si hay algo que reparar. Vos sos el respaldo. 1. Solo dos comandos: `gh run list ... -w guardia.yml -L 1 --json createdAt,conclusion` y `gh issue list ... -l guardia -s open --json number,title,body,comments`. 2. Si la guardia corrió en las últimas 3 h con éxito y no hay avisos abiertos: terminá con una línea. 3. Si hay un aviso abierto, o la guardia no corrió en 3 h o falló: add_repo y clonar; convocar al REPARADOR (repara lo operativo; commit y push sin force; si la guardia no corre, como mínimo relanzar KT-002 con `gh workflow run kt002.yml --ref master`); cerrar el aviso si quedó arreglado; dejar constancia en la Oficina (`informes`, doc_id "vigia-AAAA-MM-DD-HHMM"); solo si no se pudo arreglar, avisar con SendUserMessage en 2 líneas. No modifiques la lógica de las mediciones ni datos publicados; sin órdenes, dinero ni MT5.

### Gerente `trig_013FrUSspavgYpLTVTRWu46M`
- Cambios hechos por orden del propietario:
  - 2026-10-24T02:56:28Z: "Kensy" → "el propietario"; vigía "cada 2 h" → "cada 4 h".
  - 2026-10-24T03:14:41Z: el vigía "llama al reparador" → "solo lee y te avisa; el reparador lo convocás vos, por rama + PR, sin tocar corridas", y se agregó la prohibición de cancelar, reiniciar o relanzar corridas.
- No cambiaron el horario (6:30 Costa Rica), el modelo ni las demás funciones.
- Para revertir: volver a poner esas frases; el resto del texto no cambió.

## 3. Ramas de prueba
`prueba-guardia/<run_id>` las crean las corridas de prueba de la guardia lanzadas desde una rama: datos de mercado de prueba, fuera de master. Borrarlas no afecta nada, y queda a criterio del propietario porque es una operación destructiva. Hoy existen `prueba-guardia/40057266306` y `prueba-guardia/40057434838`. Responsable de borrarlas: el propietario, con `git push origin --delete <rama>` o desde GitHub.
