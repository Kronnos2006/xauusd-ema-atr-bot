# Candidatos futuros

Índice: [[Bienvenido]] · Ver también [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]] · [[hypothesis-gate]]

## Triage completo de la ronda (2026-08-03) — resultado

Los 8 candidatos de abajo pasaron por el triage de frecuencia real (Fase 0, con datos descargados/verificados, no estimados) y, el único que pasó, por el walk-forward completo. Resultado: **los 8 quedan cerrados, ninguno queda pendiente de trabajo en esta ronda.**

| Candidato | Frecuencia/año (mejor diseño) | Horizonte proyectado | Estado |
|---|---|---|---|
| **Momentum DXY sintético 1d** | 46.51 | 4.1 años → pasó triage | **Pasó triage y driver económico, pero descartada tras walk-forward completo** (16 folds, 6/16 rentables, R neto -17.20R, t=-0.986/p=0.32 pooled, t=-1.195/p=0.23 sin fold dominante — no llega ni cerca de \|t\|>1.96). Ver [[Macro Momentum DXY - fase 1]]. |
| Spread crédito GHYG/LQD | 14.94 (N=20) | 12.9 años | Descartado en triage (Fase 0), sin pipeline. |
| Pendiente curva TIPS (30Y-5Y) | 13.83 (N=20) | 13.9 años | Descartado en triage (Fase 0), sin pipeline. |
| Inflation breakevens 10Y (T10YIE) | 12.20 (N=20) | 15.7 años | Descartado en triage (Fase 0), sin pipeline. |
| GVZ (VIX del oro) | 6.11 (spike p85/252d) | 31.4 años | Descartado en triage (Fase 0), sin pipeline. |
| VIX (fuente FRED real) | 5.78 (spike p85/252d) | 33.2 años | Descartado en triage (Fase 0), sin pipeline. |
| GLD (flujos ETF) | — | — | Sin fuente de datos verificada — no evaluable, no se fabricó un número. Sigue pendiente de investigación de fuente si se retoma. |
| COT (posicionamiento CFTC) | — | ≥3.7 años en el mejor caso teórico irreal (52 episodios/año, cada semana cuenta) | Descarte estructural sin pipeline — un diseño realista de "posicionamiento extremo" es por naturaleza tan poco frecuente como GVZ/VIX (~6/año), que ya fallaron por amplio margen. |
| Oro en otras monedas (XAUEUR/XAUGBP/XAUJPY) | N/A | N/A | **Reclasificado**: no es una hipótesis con mecanismo propio, es una técnica de verificación cruzada para aislar si el driver de OTRA hipótesis es el oro o el dólar. Se anotó como auditoría posterior natural para Momentum DXY (ya sin efecto, no aplica). XAUJPY no existe en el broker (XAUEUR/XAUGBP sí, verificado vía MT5). |

Nota metodológica: la biblioteca de efectos típicos (`triage_frecuencia.py`) solo tenía UNA entrada completa (media_R + std_R) al momento de este triage — DFII10 (0.230/1.135) — así que se usó esa para los 8, documentado como supuesto optimista (DFII10 terminó fallando su propio power analysis). Esto no cambia el resultado: incluso con el efecto más generoso disponible, 6 de 8 candidatos fallaron el triage por márgenes amplios, y el único que pasó (Momentum DXY) falló limpio en el walk-forward.

Con esto, el pipeline de candidatos de esta ronda queda vacío — hace falta una ronda nueva de generación de candidatos antes de seguir (ver [[Estado actual y próximos pasos]]).

## Registro anterior (2026-07-27, revisión externa, punto 6)

**Ninguno de estos entra directo al pipeline completo** — todos pasan primero por el triage de frecuencia (Fase 0 de `hypothesis-gate`: chequeo de frecuencia + power analysis con efecto típico, descarte si el horizonte proyectado supera ~5 años) y por el screen rápido de IC (más abajo). El orden de la lista es de prioridad estimada, no de llegada — GLD y COT seguían en la lista de una ronda anterior y ya no son automáticamente los primeros.

## Screen rápido de IC — el segundo filtro barato, antes del pipeline completo

**Umbral: IC (correlación de Spearman entre la señal en t y el retorno de oro en t+1) > 0.03-0.05, con t-stat > 1.5, calculado sobre VALIDATION — no sobre TRAIN.**

Esto es un chequeo direccional simple (¿la señal predice algo del retorno siguiente, aunque sea débil?) más barato que un walk-forward completo, y complementa al triage de frecuencia (Fase 0): la frecuencia dice si HAY suficientes datos para confirmar algo; el IC dice si hay ALGO que confirmar en primer lugar. Un candidato tiene que pasar los dos antes de justificar el trabajo de un pipeline completo (grilla de parámetros, walk-forward de folds, DSR).

## Candidatos, priorizados por frecuencia + racional (no por orden de llegada)

| Candidato | Fuente probable | Frecuencia | Racional | Disponibilidad verificada (2026-07-27) |
|---|---|---|---|---|
| **Inflation breakevens 10Y** | FRED, serie `T10YIE` (o `T5YIE` a 5 años) | Diaria | Expectativas de inflación de mercado — mecanismo relacionado pero no idéntico a DFII10 (breakeven = nominal - real; DFII10 es el componente real solo) — chequear con `factor-independence` si de verdad no solapa con DFII10 antes de invertir tiempo | No verificada todavía (no está en MT5, requiere FRED como DFII10) |
| **GVZ (VIX del oro)** | CBOE, posiblemente FRED (`GVZCLS`) | Diaria | Volatilidad implícita específica de oro, no genérica — régimen de miedo/calma propio del activo, no importado de otro mercado | **No está en MT5** (verificado, búsqueda directa sin resultados) — necesita fuente externa, mismo tipo de investigación previa que ya se le hizo a DXY antes de construir el proxy |
| **Momentum DXY 1-5 días** (no el nivel) | DXY sintético ya construido (`construir_dxy_sintetico.py`) | Diaria | Distinto de la hipótesis DXY ya descartada (esa era nivel/caída sostenida a N=20/60/120 días) — momentum de muy corto plazo es un mecanismo distinto, aunque comparte la fuente de datos | **Datos ya disponibles** — reusa directamente `dxy_sintetico.csv`, sin trabajo de construcción nuevo |
| **VIX** | Sin símbolo índice directo en este broker | Diaria | Miedo/risk-off genérico → posible flujo hacia oro como refugio | **Parcial**: no hay índice VIX directo, pero sí ETFs relacionados (`SVIX`, `UVIX`, `VIXM` — todos productos de futuros VIX apalancados/inversos, no el índice spot). Evaluar si un ETF de estas características es un proxy aceptable o si hace falta una fuente externa (ej. FRED `VIXCLS`) antes de comprometerse |
| **Spread de crédito IG/HY (LQD/HYG)** | MT5 directo | Diaria | Apetito de riesgo crediticio — otro ángulo de risk-on/risk-off, mecanismo distinto al de tasas reales o volatilidad | **Datos ya disponibles**: `LQD` confirmado en MT5 (iShares Investment Grade). `HYG` específico no está, pero `GHYG` (iShares US & Intl High Yield) es un sustituto directo del mismo tipo de exposición — confirmar si sirve o si hace falta el HYG exacto |
| **Pendiente de curva TIPS** | home.treasury.gov (Daily Par Real Yield Curve, ya usado para verificación cruzada de DFII10) | Diaria | Forma de la curva real, no solo el nivel a 10 años — posible información adicional sobre expectativas de política monetaria a distintos horizontes | Fuente ya usada en el proyecto (`historial/treasury_real_yield_202{5,6}.csv`), solo falta extender el histórico y definir la métrica de pendiente |
| **Oro en otras monedas (XAUEUR/XAUJPY)** | MT5 directo | Diaria | Aísla si el driver es el oro en sí o el dólar específicamente — si una señal solo funciona en XAUUSD y no en XAUEUR/XAUGBP, es evidencia de que el mecanismo real es cambiario, no de oro | **Parcial**: `XAUEUR` y `XAUGBP` confirmados en MT5. `XAUJPY` específico NO está — mismo tipo de sorpresa que ya pasó con DXY, verificar antes de asumir |
| GLD (flujos de ETF) | State Street, fuente no verificada | Diaria | Proxy de demanda institucional — ya identificado en la ronda anterior, sigue en pausa | Sin cambios — sigue sin investigación de fuente, no es automáticamente el primero |
| COT (posicionamiento CFTC) | CFTC.gov, semanal | **Semanal** — techo de frecuencia estructural ya identificado | Sentimiento/posicionamiento extremo de futuros de oro | Sin cambios — fuente pública confiable pero cadencia semanal probablemente no sobrevive el triage de frecuencia (mismo problema que ya limitó 2s10s a K=2 folds) |

## Cómo aplicar

Antes de invertir tiempo en cualquiera de estos: (1) triage de frecuencia, (2) screen de IC sobre VALIDATION, (3) si pasa ambos, recién ahí `hypothesis-gate` Fase 1 completa. Para los candidatos macro relacionados entre sí (breakevens, DXY, GVZ — todos tocan expectativas/volatilidad ligadas a política monetaria o risk-off genérico), correr `factor-independence` contra DFII10 (ya archivado) y entre ellos mismos antes de asumir que aportan algo nuevo — varios de estos podrían resultar ser la misma exposición con otro nombre.

## Ver también
[[hypothesis-gate]] · [[factor-independence]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]] · [[Macro Momentum DXY - fase 1]] · [[Estado actual y próximos pasos]]
