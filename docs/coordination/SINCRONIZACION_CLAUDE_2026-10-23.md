# Informe de sincronización — Claude ↔ ORION (corte 2026-10-23 ~09:30 CR)

**Operated-By:** Claude (Anthropic) · **Requested-By:** usuario (2026-10-23) · **Review-Status:** pending (revisión cruzada de ChatGPT) · **Validation:** lecturas de GitHub (API, git log, Actions); sin pruebas de software; no se tocó ningún workflow, dato ni medición.
Regla de este informe: nada se atribuye sin evidencia verificable. "No verificado" = no hay evidencia en el repositorio o en Actions.

## 1. Qué reconozco (leído y contrastado)
- **Política de autoría** (`AUTORIA_CHATGPT.md`, 4e7f6a7): entendida. Desde ahora mis commits llevan `Operated-By: Claude (Anthropic)`, `Requested-By`, `Review-Status`, `Validation`. No reescribo commits antiguos.
- **Protocolo de control cruzado** (`docs/orion-control-cruzado.md`, 0efcf9e) y **issue #31** (estado: propuesta, sin comentarios): reconocidos. Una issue no me ordena nada; el criterio de aceptación pide que publique un reporte y ChatGPT lo revise. Este documento es ese reporte; **no lo publiqué en la issue** (falta tu OK).
- **Plan maestro 22-oct y traspaso 23-oct**: leídos. Por PRs (API): #23–#30 cerrados con fusión (pilotos OpenHands/TradingAgents, ORION estable #20, observatorio #8, resumen #5, ahorro #4). **#3 (inspector de CSV) sigue abierto.** Issues abiertas: #1, #2, #3, #7, #9, #31. Las ejecuciones de Actions que citan los documentos del 22-oct no las re-verifiqué una por una.
- Fases según el propio plan: 1 y 2 sin dictamen independiente (Desconfiado/Vigía); 3 no conforme (solo 2 informes consecutivos, con limitaciones); 4 en curso y descriptiva; 5 sin iniciar; 6 ORION estable publicado, Oficina privada no verificable desde GitHub.

## 2. Quién hizo qué (por evidencia en Git)
| Origen | Evidencia | Cantidad (desde 2026-10-20) |
|---|---|---|
| **Claude** | autor Git `Claude <noreply@anthropic.com>` | 43 commits únicos (20→23-oct): gerencia, agentes, portafolio, analista, guardia, observabilidad de KT-002 (83bf4bd, fusión 72cf911), conectores, visor, Oficina. Última: ac06581 y 723a865 (rama, sin fusionar) |
| **ChatGPT** | trailer `Operated-By: ChatGPT` | solo 2: 4e7f6a7 (política) y dcf17c8 (traspaso). Ambos con autor Git Kronnos2006 |
| **GitHub Actions** | autores `kt002-bot`, `guardia-bot` | 30 y 5 commits (registros KT-002, spread/velas) |
| **Sin atribución posible** | autor Git `Kronnos2006` sin trailer | resto, incl. casi todo ORION del 22-oct. El traspaso dice que ChatGPT no hizo todos; no puedo confirmar quién fue el operador de cada uno → **no se atribuye** |
Antes del 20-oct 14:37 todo figura como Kronnos2006; no atribuyo nada a ningún agente.

## 3. Vigía (`guardia.yml` + tarea programada "Vigía de datos")
- **guardia.yml**: 12 corridas, todas `success` (14:36 del 21-oct → 13:46 del 23-oct). Sin issues `guardia` abiertos.
- **DISCREPANCIA A:** se documenta "cada hora" (cron `37 * * * *`), pero las corridas reales caen cada **4–6 h** (ej. 01:52, 07:54, 13:46). El vigía usa un umbral de 3 h → casi siempre cree que "la guardia no corrió" y entra en la rama de reparación.
- **DISCREPANCIA B:** el gerente documenta al vigía "cada 2 h"; la tarea real es `37 */4 * * *` (modificada el 21-oct). Última corrida: 12:38 UTC, éxito.
- **DISCREPANCIA C (importante):** a las 12:39 UTC del 23-oct el vigía **canceló** la corrida 19 de KT-002 (informe `vigia-2026-10-23-0640` en la Oficina) y lanzó la 20 a mano, alegando "colgada ~2h45 sin avance". Evidencia en contra: durante esa corrida hubo commits de registro a las 10:08, 11:07 y 12:07Z, o sea **sí producía registros**. Además contradice la regla del reparador ("nunca cancelar las que trabajan") y tu instrucción de hoy. Recuperó bien: la corrida 20 sigue en curso (jobs sin pasos fallidos) y hay registro 14:07Z; 21 en cola. **No modifiqué la tarea**: queda para decisión tuya o del gerente el lunes.
- **DISCREPANCIA D:** `data/mercado/btc_1d.json` y `tendencia.json` tienen último commit el 22-oct 09:36 (no de la guardia) y su última vela es la del 21-oct. Las velas/régimen de la guardia no se están actualizando desde entonces pese a que sus corridas salen `success` (falla silenciosa; lo anticipaba la revisión de código: `continue-on-error`/`|| true`). El spread sí se actualiza. El informe del analista de hoy usa por eso datos de hace >30 h.
- KT-002: corridas 14–20 `success` salvo la 19 (cancelada, ver C). El cron `7 * * * *` no dispara (documentado); funciona por job largo + despertador.

## 4. Reparador (`.claude/agents/desarrollo-reparador.md`, creado en c20322e, 21-oct, por Claude)
- **Estado real: sin ninguna intervención verificable.** 0 commits "Reparación:", 0 menciones en `decisiones.md` o en informes del vigía (los informes del 22 y 23 describen relanzamientos hechos por el propio vigía, no por el reparador). Las sesiones son privadas: **no verificado** si alguna vez corrió.
- Puede arreglar solo (sin permiso): workflows operativos, avisos, logs, reintentos, `despertar.txt`, visor, relanzar fallidos. **Requiere autorización**: lógica de mediciones (`kt002_prospectivo.py`), datos o registros publicados, archivos del desconfiado/analista/riesgo, dinero/MT5, force push.
- Recuperación: depende de que el vigía lo convoque; hoy no hay evidencia de que lo haga y D sigue sin avisar.

## 5. Informe del gerente
- Último: 23-oct (Oficina `2026-10-23-0635`; commit ac06581; `docs/analisis/2026-10-23.md`). **Comprobado:** 0 órdenes y 0 escalaciones pendientes; KT-002 sin solape n=13 (siempre sube 7/13, Kronos 6/13), sin valor estadístico. **Pendiente/no verificado:** régimen de BTC con velas viejas (D); flujos de ETF del 22-oct contradictorios (TFTC −635,5 M vs CMC/Bitcoin.com >+1.000 M); ballenas, DXY y netflow sin dato; fuentes sin URL completas en parte del texto del analista (observación de calidad, Fase 3).
- Observaciones de auditoría conservadas: dudas MEDIAS del desconfiado en HP-006, y reconfirmación de HP-004/HP-005 pendiente. Informes del 22 y 23 siguen sin cumplir el checklist de Fase 3.

## 6. Qué falta registrar
1. `decisiones.md` no tenía filas del 22-oct; el 23-oct solo la de M1–M3. Faltan: informe del analista 22-oct (7700d68), contexto para otra IA (1dd5017), y la cancelación del vigía (C).
2. Respuesta en #31 con este reporte (a la espera de tu OK).
3. Trailers de autoría en mis commits desde ahora; los anteriores se documentan aquí por autor Git, sin reescribirlos.
4. Desde ahora separo en cada informe: Claude / ChatGPT / Actions / sin atribución.

## 7. Pausa hasta el lunes 26-oct
- Automatizaciones intactas: gerente 06:30 CR, vigía cada 4 h, guardia, KT-002, KT-003 (manual). No cancelé, detuve ni modifiqué nada.
- Desarrollo en pausa. Dos cosas mías quedaron abiertas **antes** de tu aviso: M1–M3 aprobadas hoy (sin código escrito) y la rama `dev/protocolo-ahorro-agentes` (723a865, solo texto en 3 archivos de agentes, sin fusionar). Ambas quedan quietas hasta el lunes.
- Sugerencia para el lunes (a decidir por ti): arreglo de D dentro de M2, regla "el vigía no cancela corridas con registros recientes", y alinear documentación (guardia ~4–6 h, vigía cada 4 h).
