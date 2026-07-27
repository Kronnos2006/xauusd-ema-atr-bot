# Macro 2s10s — fase 1 (spread de tasas 2yr-10yr, sin trigger técnico)

Índice: [[Bienvenido]] · Ver también [[Metodología]] · [[Macro DFII10 - fase 1]]

## Contexto

Segunda hipótesis macro del proyecto, evaluada con la misma disciplina que [[Macro DFII10 - fase 1]] vía la skill `hypothesis-gate`. Frase falsable + regla de corte fijadas y mostradas al usuario antes de escribir una sola línea de `hipotesis_macro_2s10s.py`.

## Hipótesis (frase falsable)

Empinamiento (steepening) sostenido de N días en el spread 2s10s (10 años - 2 años, FRED `T10Y2Y`, nominal) → sesgo alcista en M sesiones de oro. Igual que DFII10, hipótesis puramente macro, sin trigger técnico de confirmación en esta fase 1.

Definición operacional de "empinamiento sostenido": `spread[t] > spread[t-N]` (nivel neto de ventana, sin exigir monotonía día a día — mismo criterio que usó DFII10, dirección invertida).

## Metodología

1. **Chequeo de frecuencia previo**: 288/135/77 episodios para N=20/60/120 días (2004-2026) — sensiblemente menos que los 291/177/132 de DFII10, sobre todo en N=60 y N=120.
2. **Folds derivados del piso de 30 episodios/fold**, no fijados de antemano: con la grilla completa {20,60,120}, N=120 es el cuello de botella y solo permite **2 folds** (con 3 folds cae a 16 en el peor caso). Decisión explícita del usuario: mantener la grilla completa y aceptar K=2 en vez de acotarla para ganar folds — **reserva metodológica documentada desde antes de correr nada**, no después de ver el resultado: con solo 2 folds el chequeo de "sin fold dominante" tiene poder de discriminación casi nulo.
3. **Regla de corte, más estricta que la de DFII10 (decisión explícita del usuario, sin zona de "pasa con reservas")**: pasa solo si (a) mayoría de folds rentables netos de spread, Y (b) t-stat pooled p<0.05, Y (c) ese p se sostiene sin el fold más fuerte.
4. **Verificación cruzada de la fuente de datos**: FRED `T10Y2Y` vs. spread nominal calculado a mano con la curva Par Yield de home.treasury.gov (columnas "2 Yr"/"10 Yr").

Grilla 3×3 (N∈{20,60,120} × M∈{5,10,20}) — mismos valores que usó DFII10, primera vez aplicados a este dato (no es reusar un barrido ya hecho sobre 2s10s).

## Resultado (2026-07-26)

**NO PASA el checkpoint exploratorio**, sin ambigüedad:

- 2/2 folds rentables netos de spread (110 trades TEST acumulados, +20.43R neto) — cumple (a), pero con K=2 esto es poco informativo por sí solo.
- **t-stat pooled (ambos folds): p=0.2033** — no cruza 0.05, incumple (b).
- **t-stat pooled sin el fold más fuerte: p=0.4205** — tampoco, incumple (c). No es un caso de "pasa con todos pero no sin el dominante" (que sería régimen-dependencia); acá ninguna de las dos versiones se acerca a significativo.
- Verificación cruzada de fuente: correlación 1.000000, diferencia máxima 0.0000 entre FRED y Treasury.gov en el solapamiento 2025-2026 — fuente confiable, la falla no es de datos.
- Dato lateral no accionable: en ambos folds la única ventana N que superó el piso de 30 con t-stat positivo en TRAIN fue N=20 (la más corta); N=60/120 casi siempre quedaron bajo piso o con t-stat negativo. No alcanza para revivir la hipótesis con una grilla acotada — el resultado pooled ya incluye ese sesgo hacia N=20 y sigue sin ser significativo.

**Conclusión: se descarta en esta fase.** Al fallar en el filtro exploratorio (mismo criterio que ya se aplicó al trigger ruptura+retest de la familia EMA), no se justifica instrumentar un logger en vivo para este candidato — no hay holdout en curso para 2s10s.

## Código

`hipotesis_macro_2s10s.py` (raíz del repo) — reutiliza toda la infraestructura ya validada (`metrica_robusta`, `descontar_spread`, `construir_bloques_walk_forward`, `bajar_datos_rango` de `Backtest ema v4.py`), mismo patrón que `hipotesis_macro_dfii10.py`.

## Ver también
[[Macro DFII10 - fase 1]] · [[Metodología]] · [[Bienvenido]]
