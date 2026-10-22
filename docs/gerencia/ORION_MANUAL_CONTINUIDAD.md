# Manual de continuidad — ORION y Plan Maestro

**Versión:** 2026-10-22 · Documentación consolidada para el dueño y futuros operadores.  
**Alcance vigente:** ChatGPT/Claude trabajan desde sus chats; GitHub conserva la evidencia; ORION la visualiza. Nada aquí autoriza cambios a experimentos activos.

## Guía rápida
| Necesidad | Dónde ir | Qué es |
|---|---|---|
| Supervisar desde teléfono | https://kronnos2006.github.io/xauusd-ema-atr-bot/ | ORION público, solo lectura |
| Ver visor Claude | https://kronnos2006.github.io/xauusd-ema-atr-bot/visor/ | Visor publicado conjuntamente, no sesión privada |
| Estado general y fases | [Plan Maestro](PLAN_MAESTRO_EJECUCION_2026-10-22.md) | objetivos y requisitos F1–F6 |
| Qué ya se comprobó | [Verificación de pendientes](PLAN_MAESTRO_VERIFICACION_PENDIENTES_2026-10-22.md) | hechos, timestamps y bloqueos |
| Qué entregó ORION | [Acta de cierre estable](ORION_ACTA_CIERRE_ESTABLE_2026-10-22.md) | aceptación de panel v2 |
| Referencias de otros proyectos | [Investigación GitHub](REPOS_SIMILARES_ORION_LAB_2026-10-22.md) | nueve repos, compatibilidad y prioridades |
| Coordinación entre dos chats | [Protocolo](../coordination/ORION_PROTOCOLO_COOPERACION.md) y [Contrato de tareas](../coordination/ORION_CONTRATO_TAREAS.md) | propiedad de archivos, issue, PR, bloqueo |
| Reservar tarea con cuenta GitHub | [Árbitro](../coordination/ORION_ARBITRO.md) | evita dos reservas en un mismo issue; no ejecuta IA |
| Comandos de verificación | [Comandos seguros](../coordination/ORION_COMANDOS_SEGUROS.md) | workflow_dispatch autenticado, solo lectura |
| Problemas aún abiertos | [Issue #1](https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/1), [#7](https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/7), [#9](https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/9) | auditor, informes, observación KT-002 |

## Arquitectura vigente (sin infraestructura nueva)

```text
        Dueño
       /     \
  Claude     ChatGPT     <- instrucciones y ejecución desde chats separados
       \     /
        GitHub           <- PR/Issues/Actions/commits y evidencia
          |
      ORION + visor      <- GitHub Pages público; solo observación
```

No hay transmisión automática de instrucciones privadas entre chats, y el organigrama de agentes no verifica ejecución en vivo. Los modelos de KT-002 no se controlan desde la página. No usar el código de `gateway/` (Google): fue preparado, **NO desplegado**, y está fuera de alcance por decisión posterior del dueño.

## Procedimiento de trabajo seguro

1. Leer [Plan Maestro](PLAN_MAESTRO_EJECUCION_2026-10-22.md), `CLAUDE.md` y `AGENTS.md` **sin editarlos**.
2. Revisar los Issues y PR abiertos, comprobar qué ramas/archivos trabaja la otra IA. Registrar tarea y su aceptación explícita en GitHub.
3. Crear una rama propia. No sobrescribir el visor `docs/visor/index.html` de Claude ni publicar un segundo GitHub Pages.
4. No tocar `data/kt002/`, `data/kt003/`, preregistros, holdouts, scripts activos, `kt002.yml`, `guardia.yml`, reglas de Auditor/Riesgo/Analista, ni secretos, sin procedimiento independiente específico.
5. Documentar cambios, pruebas y evidencia UTC en el PR. Distinguir **HECHO, EN CURSO, BLOQUEADO, NO VERIFICADO**. No inventar ejecuciones ni firmas.
6. Ejecutar comprobaciones read-only disponibles:
   ```bash
   python -m unittest discover -s tests -p 'test_centro_control.py' -v
   python -m unittest discover -s tests -p 'test_orion_release.py' -v
   python tools/orion_release_check.py --json
   python tools/centro_control.py status
   python tools/centro_control.py build --public
   ```
7. Solo fusionar cambios permitidos tras CI/revisión. Verificar resultado de `.github/workflows/orion-pages.yml` en Actions si se toca el panel/publicación.
8. Solicitar **Desconfiado** y **Vigía** por sus canales reales para liberar PR #3. No se los puede representar o sustituir desde ChatGPT.
9. Actualizar el Plan Maestro con IDs de evidencia y fecha; marcar cierre de fase solo cuando sus requisitos se cumplan.

## Prioridades pendientes (sin delegación ficticia)
1. **F1/F2**: dictamen Desconfiado y recuperación operativa comprobada por Vigía; PR #3 permanece abierto.
2. **F3**: tres informes reales con checklist, anexos hechos por Analista, métricas accesibles de Claude.
3. **F4**: KT-002 prospectivo continuo sin cambios, incertidumbre y control de fuentes.
4. **F5**: hipótesis nuevas aisladas en Fase 0; Fase 1 exige aprobación explícita del dueño.
5. **F6**: ORION estable completado como supervisor; la antigua idea de control OAuth/backend **no forma parte** del alcance presente.

## Reutilización futura
Los repos del [estudio comparativo](REPOS_SIMILARES_ORION_LAB_2026-10-22.md) **no están instalados**. No copiar ni importar código sin licencia, seguridad, pruebas y un piloto aislado. Un proyecto parecido no demuestra que su metodología cuantitativa sea correcta.

## Recuperación
- Si ORION falla al publicarse: mirar Actions de ORION Pages, restaurar un commit publicado conocido o revertir el PR afectado. No alterar cron KT-002.
- Si GitHub API falla: mostrar NO VERIFICADO; no asumir que el agente está ocioso/activo.
- Si hay dos operadores en el mismo archivo: detener ambos cambios sobre ese archivo y conciliar mediante PRs, sin force-push.
- Si aparece una cuestión científica: escalar al dueño y auditor correspondiente, detener cualquier acción reservada.

## Criterio de documentación completa
Los enlaces de entrada, arquitectura, estado real, protección experimental, procedimiento, pruebas, responsables, recuperación y fuentes de reutilización están descritos aquí. Esto **no** convierte en terminadas las auditorías pendientes ni el experimento.
