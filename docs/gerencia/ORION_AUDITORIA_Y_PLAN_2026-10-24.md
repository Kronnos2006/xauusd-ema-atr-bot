# ORION — Auditoría de arquitectura y plan de evolución

Corte: 2026-10-24 ~05:00 UTC. Autor: Claude (Anthropic). Revisor pendiente: ChatGPT. Autoridad: el propietario.
Construye sobre `REPOS_SIMILARES_ORION_LAB_2026-10-22.md`, `PLAN_MAESTRO_EJECUCION_2026-10-22.md`, `ORION_MANUAL_CONTINUIDAD.md` y `docs/riesgo/MARCO_DE_RIESGO.md`, que no se duplican.

Clasificación usada:
- **OV**: operativo y verificado;
- **OL**: operativo con limitaciones;
- **ED**: en desarrollo;
- **SD**: solo documentado;
- **DU**: duplicado o innecesario;
- **PV**: pendiente de validación.

Un agente definido en un archivo **no** cuenta como agente en ejecución: la columna "Evidencia" dice qué se observó.

## 1. Inventario

### 1.1 Workflows (GitHub Actions; repositorio público, runners estándar sin costo)
| Workflow | Clase | Evidencia (desde 2026-10-20) |
|---|---|---|
| `kt002.yml`: medición prospectiva | **OV** | 23 corridas, 6 537 min; 77 predicciones y 0 violaciones de integridad (`tools/kt002_integridad.py`, PR #32) |
| `guardia.yml` (versión en master) | **OL** | 18 corridas, 6 min. Puede dar falso verde y no actualizó la tendencia desde el 22-oct. Lo corrige el PR #32, **sin fusionar** |
| `guardia.yml` (versión del PR #32) | **PV** | Probada en GitHub real desde la rama: 40057266306 y 40057998529 en verde; 40057434838 en rojo con simulacro. Falta probarla en master |
| `kt003.yml`: histórico, manual | OV | 4 corridas, 183 min; diagnóstico cerrado (`docs/KT-003_registro_historico.md`) |
| `orion-pages.yml`: publicación móvil | OV | 15 corridas (14 bien). Publicación por Actions; la compilación desde la rama (`pages build`, 92 veces hasta el 22-oct 16:07) ya no corre |
| `orion-ci.yml`, `resumen-gerente-ci.yml`, `observatorio-kt002-ci.yml`, `orion-google-ci.yml` | OV (pruebas) | 12 / 5 / 1 / 1 corridas, todas en verde |
| `orion-arbitro.yml`, `orion-comandos.yml` | SD/PV | Sin corridas registradas en el período; con pruebas unitarias |
| `orion-pilot-b1.yml`, `orion-framework-smoke.yml`, `orion-upstream-pilot.yml` | ED (pilotos aislados) | 1 / 4 / 2 corridas en verde. Compilan o importan OpenHands y TradingAgents, sin agentes ni datos reales |
| `kt002-integridad-ci.yml` (PR #3 de ChatGPT, abierto) | **DU** con el PR #32 | Inspector de CSV con SHA-256. El de PR #32 agrega aciertos recalculados, resumen reproducido e historial de git. **Propuesta:** fusionar #32 y que el CI de #3 llame al verificador más completo (decide el propietario) |

### 1.2 Código y dependencias
- `tools/`: 10 scripts en master, más `guardia_salud.py` y `kt002_integridad.py` en el PR #32.
- Dependencias fijadas en `docs/evidencia/KT-001/requirements-resolved.txt`. Modelos fijados por revisión: Kronos-small `901c26c…`, Tokenizer `0e01173…`, TimesFM 2.5 `1d95242…`; código de Kronos `67b630e…` (`tools/kt002_prospectivo.py`).
- Pruebas:
  - 72 en `tests/`, más 32 del PR #32;
  - 1 error previo: `test_orion_google` necesita `fastapi`, que no está instalado (P8).
- Los datos de mercado (`data/mercado/`) son copias de Binance spot públicas. `tendencia.json` en master tiene fecha del **22-oct**: vieja, y la corrige el PR #32.

### 1.3 Agentes de Claude (27 archivos)
| Grupo | Clase | Evidencia de ejecución |
|---|---|---|
| gerente (tarea diaria 6:30), vigía (tarea cada 4 h) | **OV** | Historial de las tareas programadas: última corrida del gerente 23-oct 12:31Z SUCCEEDED; vigía 24-oct 00:37Z SUCCEEDED |
| analista con sus 3 ayudantes | OV | `docs/analisis/2026-10-21..23.md` |
| desconfiado | OV en hitos | `docs/auditorias/*`, 19 menciones en decisiones; auditoría del PR #32 el 23-oct. Su tarea diaria está **desactivada** desde el 20-oct |
| portafolio (jefe, investigador, réplica, estratega), riesgo (jefe y costos), mejorador | OL | Fase 0 HP-001 a HP-007, ES-001/002, marco de riesgo; solo se convocan bajo demanda |
| innovación con noticias, operaciones, recursos de IA | SD/OL | 1 mención cada uno |
| desarrollo (diseñador, programador, integrador, reparador), disciplina, documentación | **SD** | 0 menciones de ejecución |
| `infra-guardian`, `strategy-reviewer` (era MT5/XAUUSD, Windows) | **DU** | No aplican a la nube actual. Propuesta: archivar, no borrar (decide el propietario) |

### 1.4 Tareas programadas de Claude (3)
- **Gerente** (`trig_013F…`): **OV**.
- **Vigía** (`trig_01R2…`): **OV**, con la protección provisional activa.
- **Desconfiado diario** (`trig_01Ej…`): desactivada, **SD**.

### 1.5 Conectores de esta cuenta
| Conector | Uso en ORION | Clase |
|---|---|---|
| CoinMarketCap, Crypto.com | Asignados a analista-macro, ballenas, tendencia y riesgo-costos (solo lectura de mercado) | OL. Las tareas programadas los tienen disponibles, pero no hay prueba de que los subagentes los hayan usado |
| TinyFish, Claude_Code_Remote | Oficina del dueño (lectura web, disparar tareas) | OL |
| Google Drive, Figma, Vercel, Replit, Supabase, Canva, TradingNote, Claude Docs | Sin uso en ORION | No usar: suman permisos sin beneficio |

### 1.6 Skills del repositorio (12)
- `hypothesis-gate`, `data-integrity`, `factor-independence`, `debugging-and-error-recovery`, `code-review-and-quality`, `ponytail`: **OV** (usadas en la reparación y en las Fase 0).
- `infra-ops-playbook`, `strategy-research`, `run-backtest`, `sync-knowledge`: de la era MT5, **SD**.

### 1.7 Codex
- Sin commits ni PR atribuibles a Codex en el historial: los autores son Kronnos2006, Claude, kt002-bot, guardia-bot y kt003-bot.
- Clase **PV**: el protocolo lo prevé, pero no hay evidencia de uso.

### 1.8 Coordinación Claude–ChatGPT
- Es **manual, por GitHub**. ChatGPT publica desde la cuenta del propietario (commits "Kronnos2006", PR #3 a #30). Claude lee y escribe issues y PR por la API REST.
- No hay sincronización automática ni notificaciones entre chats.

## 2. Tecnología externa: matriz de reutilización
Fuente: metadatos de PyPI consultados el 2026-10-24. La API de GitHub para repositorios ajenos está bloqueada en esta sesión. Los proyectos ya estudiados el 22-oct no se repiten: OpenHands, TradingAgents, RD-Agent, Qlib, FinRobot, NautilusTrader, Agency, Cortex y ForgeFlow.

| Candidato | Versión / último lanzamiento | Licencia | Encaje | Decisión |
|---|---|---|---|---|
| VectorBT (`vectorbt`) | 1.2.0, 2026-10-19 | Apache-2.0 con Commons Clause (según el repo; **verificar**) | Simulación vectorizada rápida para la Etapa C | **Candidato principal** para el marco de simulación con costos, en un entorno separado de KT-002 y después de revisar la licencia |
| Backtrader | 1.9.78.123, 2023-04-19 | GPL-3.0+ | Motor por eventos maduro, sin mantenimiento desde 2023 | Descartar como base (sin mantenimiento; GPL) |
| backtesting.py | 0.6.6, 2026-07-22 | AGPL-3.0 | Simple | Descartar para integrar (AGPL) |
| QuantConnect LEAN (`lean` CLI) | 1.0.230, 2026-10-15 | Apache-2.0 | Motor completo en C# y nube; alto costo de adopción | Mantener como referencia, no adoptar |
| FinRL | 0.3.7, 2024-04-12 | MIT | Aprendizaje por refuerzo: alto riesgo de sobreajuste, choca con la disciplina de walk-forward | Descartar |
| MLflow | 3.17.2, 2026-10-21 | Apache-2.0 | Registro de experimentos y artefactos | No por ahora: los manifiestos, hashes y CSV versionados en git ya cubren la trazabilidad. Reconsiderar si hay más de 3 experimentos simultáneos |
| Prefect / Dagster | 3.9.0 / 1.13.26, oct-2026 | Apache-2.0 | Orquestación | Descartar: GitHub Actions ya orquesta sin costo; agregarlos sumaría un servicio y permisos |
| NautilusTrader | 1.231.0 | LGPL-3.0 | Ya evaluado el 22-oct | Solo referencia (incluye ejecución en vivo) |
| OpenHands / TradingAgents | Fijados por SHA (pilotos B1 a B4) | MIT / Apache-2.0 | Ya evaluados en pilotos aislados | Mantener aislados. No conectar a datos ni modelos reales sin una decisión nueva del propietario |

**Mantener propio:** medición prospectiva (KT-002), guardia, verificador de integridad, `hypothesis-gate`, marco de riesgo. Son pequeños, probados y específicos.

## 3. KT-002: lectura financiera (descriptiva)
`data/kt002/resumen.json` del 2026-10-24 a las 04:07Z: 77 predicciones, 73 evaluadas, 10 horas omitidas (3 huecos del 20 y 21-oct). La lectura principal usa solo observaciones **sin solape** (n=17):

| Modelo | Aciertos | IC95 (Wilson) | McNemar contra «siempre sube» |
|---|---|---|---|
| Kronos | 10/17 = 58,8 % | 36,0–78,4 % | p = 0,61 |
| TimesFM | 6/17 = 35,3 % | 17,3–58,7 % | p = 1,0 |
| KT-001 (50/50) | 6/17 = 35,3 % | 17,3–58,7 % | p = 1,0 |
| Siempre sube | 7/17 = 41,2 % | 21,6–64,0 % | — |

- **Sin ventaja demostrada.** Los intervalos se superponen por completo. Con n=17 no se distingue nada.
- Distinguir 55 % de 50 % requiere unas 780 observaciones independientes (preregistro). A 6 observaciones sin solape por día, n≈100 llega cerca del 6-nov y n≈780 cerca de fines de febrero de 2027.
- **Por régimen:** todo el período (20 al 24-oct) cayó en un único régimen diario (ALCISTA), así que no se puede evaluar la estabilidad por régimen.
- No se seleccionó ni se descartó ningún modelo: las 4 series se reportan siempre.
- Acertar la dirección **no implica rentabilidad**. A 4 h, los costos de ida y vuelta (unos 0,20–0,30 % según `MARCO_DE_RIESGO.md`) exigen un acierto bastante mayor que 50 %.
- **Marco financiero separado:** ya existe en `docs/riesgo/MARCO_DE_RIESGO.md` (costos, límites, apagado, requisitos para simular). La Etapa C lo usa tal cual: cualquier simulación nueva pasa por `hypothesis-gate`, el desconfiado y el jefe de riesgo, con registro previo y sin dinero real.

## 4. Observabilidad
No se crea un panel nuevo. Las preguntas se responden así:

| Pregunta | Dónde se responde hoy | Hueco |
|---|---|---|
| ¿KT-002 registra? ¿Cuál fue la última predicción? ¿Hay horas omitidas? | Panel ORION (Pages) y `data/kt002/resumen.md` | — |
| ¿Se actualizó el mercado? | Guardia del PR #32 (avisos y verificación) | En master, no (falso verde) |
| ¿Qué workflow falló? | Página de Actions y avisos `guardia` | — |
| ¿Qué agente actuó? ¿Qué cambió? | Commits con trailers, `decisiones.md`, Oficina | Los subagentes no dejan registro propio si no escriben un archivo |
| ¿Qué riesgos hay abiertos? ¿Qué decide el propietario? | Escalaciones de la Oficina; issues #1, #7, #9, #31 | Están repartidos |

**Tipos de falla:**
- infraestructura: workflow caído, cron, proxy;
- datos: huecos, duplicados, publicación;
- modelo: errores del script o resultados absurdos.

La guardia cubre infraestructura y publicación, `kt002_integridad.py` cubre datos y el desconfiado cubre modelo y método.

## 5. Costos (observados)
- **GitHub Actions** desde 2026-10-20: unas 6 905 min de runner. KT-002 suma 6 537 (95 %), KT-003 183 y el resto menos de 200. Costo $0 (repositorio público).
- **Guardia:** unos 20 s por corrida.
- **Claude:**
  - consumo de tokens: no se puede consultar desde esta sesión;
  - tareas: gerente 1 vez por día y vigía 6 veces por día, ambos con Sonnet. El vigía, si todo está sano, hace 4 lecturas;
  - esta reparación usó 1 subagente de auditoría (unos 88 mil tokens).
- **Optimización** (nada redundante comprobado para eliminar):
  - la compilación de Pages desde la rama ya está apagada;
  - el vigía v2 no clona el repositorio;
  - la tarea diaria del desconfiado sigue desactivada; se convoca solo en hitos.

## 6. Plan maestro por etapas
Los criterios son medibles. Una etapa no avanza porque su documentación esté escrita.

| Etapa | Criterio de aceptación | Estado al 2026-10-24 |
|---|---|---|
| **A. Confiabilidad** | PR #32 en master; guardia en verde en master con disparo desde KT-002; un aviso real abierto y cerrado; vigía v2 activo; 7 días sin fallas silenciosas | **Bloqueada:** falta fusionar el PR #32 (botón del propietario). Todo lo demás está preparado |
| **B. Calidad de investigación** | Verificador de integridad en CI de cada PR; manifiestos y hashes por experimento; n sin solape de KT-002 ≥ 100 | Verificador listo (PR #32); n = 17 |
| **C. Validación financiera** | Una hipótesis que pase la Fase 0 con potencia, registro previo y simulación con costos sin dinero real (VectorBT u otro, en un entorno aislado) | No iniciada. 7 hipótesis descartadas en Fase 0 (HP-001 a HP-007) |
| **D. Inteligencia operativa** | Avisos por excepción con cierre automático; informe del gerente con evidencia enlazada; ningún agente con autoaprobación | Parcial: avisos listos en el PR #32; informe diario operativo |
| **E. Plataforma** | Panel único consolidado; poder agregar estudios sin tocar los vigentes | Panel ORION v2 operativo; consolidación pendiente |

**Prioridades justificadas:**
1. Fusionar el PR #32 y verificar en master.
2. Resolver el duplicado PR #3 contra PR #32.
3. Archivar los agentes de la era MT5 y los que nunca se ejecutaron, por decisión del propietario.
4. Dejar acumular KT-002 sin tocarlo.
5. Revisar la licencia de VectorBT antes de cualquier marco de simulación.
