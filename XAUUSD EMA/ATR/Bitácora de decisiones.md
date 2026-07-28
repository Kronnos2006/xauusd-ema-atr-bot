# Bitácora de decisiones

Índice: [[Bienvenido]] · Ver también [[Cronología]] (narrativa completa, con hashes de commit) · [[Metodología]]

Un solo lugar con cada decisión importante del proyecto: fecha, hipótesis/tema, racional, resultado, decisión tomada. Existía dispersa entre [[Cronología]] y cada nota de hipótesis — consolidado acá el 2026-07-27 (revisión externa, punto 4). Para el detalle narrativo completo de cada fila, seguir el enlace a la nota correspondiente; esta tabla es el resumen de una línea, no el reemplazo de esas notas.

| Fecha | Hipótesis / tema | Racional | Resultado | Decisión |
|---|---|---|---|---|
| 2026-07-21 | Git init + rigor inicial | Formalizar control de versiones, empezar a corregir sesgos metodológicos conocidos | Fix `UnicodeEncodeError`, validación train/test de `optimizar_trailing` | Adoptar disciplina de validación más estricta en adelante |
| 2026-07-22 | Walk-forward anclado (reemplaza split 70/30) | Corregir data snooping estructural (optimización antes del split) | M15: 5/9 folds rentables, fold dominante 51% del R, sin él t≈0.6 (no significativo) | No operar todavía; nuevo criterio de selección = t-stat sobre R neto + piso 30 trades |
| 2026-07-22 | H1/D1, config M15 sin retunear | Ver si la config M15 transfiere a otros timeframes | H1 negativo (-3.22R/fold); D1 solo 77 trades (no-medición) | No concluir nada — H1 necesita retuneo propio, D1 necesita más folds/trades |
| 2026-07-22 | Logger EMA M15 en vivo | Empezar a acumular holdout genuinamente out-of-sample | Incidente: ~4hs caído sin reinicio (`LogonType=Interactive`) | Mitigar con log de ARRANQUE + trigger cada 15 min |
| 2026-07-23 | Filtro de tendencia MTF (H1) | Probar tendencia de timeframe mayor en vez de M15 | Descartado — R neto agregado -3.79R | Probar otra definición de tendencia (estructura) |
| 2026-07-23 | Filtro de tendencia por estructura (HH/HL) | Tercera definición de tendencia | Descartado — 3/9 folds, 123% concentrado en 1 fold | Sospechar que el problema es el trigger, no el filtro |
| 2026-07-23 | Diagnóstico de inestabilidad (N_FOLDS=4) | Descartar "muestra chica" como causa de folds dominantes distintos entre variantes | Patrón se sostiene/empeora con folds más grandes | Confirma: el trigger EMA9/21 en sí es el problema |
| 2026-07-24 | Trigger ruptura de estructura + retest | Reemplazar el trigger de entrada, no solo el filtro | Descartado — 443 trades, R neto -6.72R | Diagnosticar entrada vs. salida antes de seguir |
| 2026-07-24 | Diagnóstico entrada-vs-salida | Aislar si el problema es la señal o la gestión de salida | Baseline muestra edge de entrada real (89% persistencia TEST), concentrado en 1 fold | Probar partial-close/trailing en Baseline, con regla de corte pre-registrada |
| 2026-07-24 | Partial-close/trailing en Baseline | Reducir la concentración en el fold dominante | R neto se invierte de +14.08R a -8.05R | **Regla de corte disparada** — parar el enfoque de entrada técnica pura en M15 |
| 2026-07-24 | H1 retuneado (SL/R:R propios) | Evidencia externa sugería H1 con parámetros propios, no trasplantados | Descartado — 4/9 folds, t-stat decayendo con más datos (edge ilusorio) | Confirma: no es cuestión de retunear, el trigger no sirve |
| 2026-07-24 | **Cierre de la familia EMA9/21 completa** | 5 variantes fallan de forma convergente, no dispersa | — | Retirar la familia entera; no ir a D1 (techo de información bajo); fijar regla general (frase falsable + regla de corte antes de código) |
| 2026-07-24 | Macro DFII10 fase 1 (primera hipótesis post-EMA9/21) | Tasas reales → sesgo alcista en oro, sin trigger técnico | Pasa checkpoint exploratorio con reservas — t-stat p=0.059 | Desplegar logger en vivo; no pasar a fase 2 todavía |
| 2026-07-24/25 | Migración `LogonType S4U` | Resolver downtime por logoff/bloqueo de sesión sin guardar contraseña | Validado — prueba de resistencia 38hs+ sin reinicio, sobrevive sleeps | Migrar ambas tareas productivas |
| 2026-07-26 | Auto-recuperación de IPC | Incidente: corte de 11hs sin reconexión en logger macro | Fix escrito (`mt5.shutdown()+initialize()` tras fallos consecutivos) | Desplegar (bloqueado por huérfanos hasta 2026-07-27) |
| 2026-07-26 | 4 skills/agentes nuevos | Formalizar disciplina aprendida a los golpes | — | Crear `hypothesis-gate`, `infra-ops-playbook`, `infra-guardian`, `sync-knowledge` |
| 2026-07-26 | Macro 2s10s fase 1 | Empinamiento del spread de tasas → sesgo alcista en oro | No pasa — p=0.20 (p=0.42 sin el fold más fuerte); solo 2 folds (aceptado conscientemente) | Descartado, sin logger en vivo (falló el filtro barato) |
| 2026-07-27 | Remediación de huérfanos + despliegue de IPC | Procesos huérfanos con código viejo tras un `Stop-ScheduledTask` | Verificado: procesos nuevos, S4U intacto, ARRANQUE fresco | Primera invocación real de `infra-guardian` |
| 2026-07-27 | Sincronización de git/GitHub | Repo divergido, vault nunca commiteado | Rebase limpio, vault agregado por primera vez | Repo 0/0 con origin desde entonces |
| 2026-07-27 | Macro DXY fase 1 | Índice dólar → sesgo bajista/alcista en oro | Bloqueado (sin símbolo real) → proxy sintético construido y validado (correlación 0.9945) → walk-forward: no pasa, p=0.072 | Descartado; proxy sintético queda documentado y reusable |
| 2026-07-27 | Ratio oro/plata fase 1 | Z-score del ratio XAUUSD/XAGUSD → sesgo direccional en oro | 4/4 folds rentables pero t-stat no significativo (p=0.11, p=0.47 sin el fold dominante) | Descartado — ejemplo de "folds ganadores" engañosos |
| 2026-07-27 | Auditoría de robustez de DFII10 (spread, ALFRED, métricas, power analysis) | Verificar antes de seguir acumulando holdout pasivamente | Sobrevive spread y look-ahead; power analysis: necesita ~13 años más para 80% de poder | Ningún punto mata la hipótesis sola, pero cambia el marco de la decisión |
| 2026-07-27 | Checklist de 7 criterios para paso a demo | Escribir umbrales antes de que haga falta, no bajo presión | — | Documentado en [[Checklist paso a cuenta demo]] |
| 2026-07-27 | **Cambio de objetivo del proyecto** | 4 hipótesis macro con resultados individualmente marginales/débiles de forma consistente | — | De "encontrar una señal fuerte" a "biblioteca de factores independientes"; DFII10 reclasificado a factor archivado |
| 2026-07-27 | Incorporación de 3 rondas de revisión externa | Formalizar triage de frecuencia, DSR, independencia de factores, integridad de datos | — | `hypothesis-gate` actualizado (Fase 0 + DSR); skills nuevos `factor-independence` y `data-integrity`; [[Data Dictionary]], esta bitácora, [[Criterios de cierre del enfoque]] y [[Candidatos futuros]] creados |

## Ver también
[[Cronología]] · [[Metodología]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]]
