# ORION — Acta de cierre operativo v2 estable

**Fecha de revisión:** 2026-10-22  
**Alcance:** panel de supervisión del dueño (no orquestación autónoma de sesiones privadas).

## Decisión de arquitectura del dueño
- Se dan instrucciones **desde los chats de Claude y ChatGPT**. ORION no inicia sesiones de esos servicios ni guarda contraseñas.
- ORION centraliza estado visible, estadísticas publicadas, organigrama declarado, enlaces a proyectos y tareas verificables de GitHub.
- Ambos operadores usan ramas separadas, Issues y PR; no deben sobrescribir trabajo ajeno.
- Google OAuth y gateway `gateway/orion_google.py` quedaron **en código pero no desplegados**, por elección del dueño; no se requieren secretos ni alojamiento adicional.
- El sitio GitHub Pages **sigue siendo público**. No contiene datos privados de la Oficina ni instrucciones internas de agentes en `data.json`. No almacenar información sensible en Issues públicos.

## Matriz de aceptación
| Elemento | Criterio | Evidencia automatizada |
|---|---|---|
| Móvil | Página ORION y controles principales presentes | `tests/test_orion_release.py`, JS por `node --check` |
| Claude | Visor original copiado sin modificar, ruta `/visor/` | `cmp` en `orion-pages.yml`, release gate |
| Publicación | Un único workflow despliega Pages | `tools/orion_release_check.py` |
| Experimentación | Solo lectura, sin rentabilidad afirmada, datos históricos no solapados | `tests/test_centro_control.py`, release gate |
| Enlaces | Repositorio, Actions, Issues, comandos, árbitro, visor accesibles como URLs HTTPS | release gate |
| Alertas | GitHub Actions/Issues públicos con momento de consulta; si API falla indica no verificado | JS panel, control de interfaz |
| Comandos | Lista cerrada y uso de GitHub Actions autenticado | `tests/test_orion_comandos.py` |
| Reservas | Evita doble reserva; registra actor GitHub, no simula sesión IA | `tests/test_orion_arbitro.py` |
| Privacidad | El snapshot Pages omite enlace a Oficina privada y descripciones de agentes | release gate, Pages pipeline |
| Convivencia | No se editan `docs/visor/index.html`, KT-002/KT-003, holdout ni reglas de auditoría | Revisión de diff en PR |

## Funciones que no se deben presentar como instaladas
- No hay conexión en vivo con sesiones privadas de Claude o ChatGPT.
- No existen compras, brokers, MT5 con capital real ni garantías de rentabilidad.
- No hay bloqueo Git efectivo por la reserva de un issue; se requieren revisiones y permisos de repo.
- La última verificación CI no sustituye una inspección manual del celular.
- La API pública de GitHub tiene límites y puede fallar. Una página accesible no certifica actualización reciente del CSV.

## Criterios finales de entrega
1. Ejecutar `python tools/orion_release_check.py --json` y todas las pruebas del workflow ORION.
2. Revisar que el PR toque **solo** herramientas, pruebas, panel, workflow ORION y este documento.
3. Integrar únicamente tras pruebas aprobadas.
4. Verificar `orion-pages.yml` con estado `success` después del merge; comprobar `/` y `/visor/` desde Android si se desea validación visual definitiva.
5. Mantener el PR #3 abierto hasta revisión independiente: el cierre de ORION **no** autoriza merge de KT-002.

## Operación habitual
- **ChatGPT/Claude:** las instrucciones y el trabajo real ocurren en sus chats.
- **GitHub:** mostrar evidencia de los cambios por PR, gestionar Issues y ejecutar verificaciones permitidas.
- **ORION:** observar cambios de manera transparente, conservando las fechas y distinción entre lo declarado y lo realmente comprobado.
- **No activar OAuth Google** ni comandos autónomos salvo nueva decisión explícita del dueño.

Si todas las verificaciones anteriores están verdes, ORION puede declararse **estable en este alcance**, aunque la experiencia visual del teléfono siempre pueda mejorarse sin alterar la arquitectura.
