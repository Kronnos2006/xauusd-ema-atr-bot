# Candidatos futuros

Índice: [[Bienvenido]] · Ver también [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]] · [[hypothesis-gate]]

Registro actualizado el 2026-07-27 (revisión externa, punto 6). **Ninguno de estos entra directo al pipeline completo** — todos pasan primero por el triage de frecuencia (Fase 0 de `hypothesis-gate`: chequeo de frecuencia + power analysis con efecto típico, descarte si el horizonte proyectado supera ~5 años) y por el screen rápido de IC (más abajo). El orden de la lista es de prioridad estimada, no de llegada — GLD y COT seguían en la lista de una ronda anterior y ya no son automáticamente los primeros.

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
[[hypothesis-gate]] · [[factor-independence]] · [[Objetivo del proyecto - biblioteca de factores]] · [[Criterios de cierre del enfoque]]
