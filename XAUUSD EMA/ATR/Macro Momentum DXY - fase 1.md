# Macro Momentum DXY — fase 1 (retorno 1d, sin trigger técnico)

## Descartada (2026-08-03) — no pasa el checkpoint, sin reservas ambiguas

Índice: [[Bienvenido]] · Ver también [[Candidatos futuros]] · [[Objetivo del proyecto - biblioteca de factores]] · [[hypothesis-gate]] · [[Macro DXY - fase 1]]

## Contexto

Salió de un triage sistemático de los 8 candidatos listados en [[Candidatos futuros]] (ronda 2026-07-27). Es la única que pasó el triage de frecuencia (Fase 0 de `hypothesis-gate`) y el test de driver económico, de los 8. Distinta de [[Macro DXY - fase 1]] (nivel/caída sostenida N=20/60/120, ya descartada): esta mide el **retorno** de 1 día del DXY sintético, thresholdeado por desvíos estándar — mecanismo de microestructura FX de corto plazo, no de nivel/tendencia.

## Hipótesis (frase falsable)

Cuando el retorno diario del DXY sintético supera k desvíos estándar (calculados sobre TRAIN de cada fold, congelados, sin look-ahead) en valor absoluto, el oro tiene sesgo direccional **inverso** al signo del movimiento del dólar (DXY sube → oro sesgo bajista/venta; DXY baja → oro sesgo alcista/compra) en las M sesiones siguientes.

## Triage previo (Fase 0)

De los 8 candidatos, solo este pasó: 46.51 episodios/año (ventana 1d, k=1σ) → horizonte proyectado 4.1 años (< límite de 5), usando el efecto de referencia de DFII10 (media R=0.230, std R=1.135 — único con ambos momentos completos en la biblioteca de efectos típicos, documentado como supuesto optimista). Los otros 6 candidatos con datos reales (T10YIE, GVZ, VIX, spread crédito GHYG/LQD, pendiente curva TIPS) proyectaron 12.9-33.2 años — descartados sin pipeline. Detalle completo de los 8 en [[Candidatos futuros]].

**Test de driver económico**: pasa (describible sin Fed/tasas — microestructura y mecánica de conversión de precio en USD), con la reserva explícita de que el mecanismo roza una identidad de conversión de moneda más que una tesis de comportamiento — el valor real a testear era si la reacción del oro difiere de la conversión aritmética esperada.

## Metodología

1. **Grilla declarada (2×3, sin resweepeo)**: k∈{0.75, 1.0} × M∈{1, 3, 5} sesiones. N=1 día fijo desde el triage, no parte de la grilla.
2. **Walk-forward de 16 folds anclados** — derivado del chequeo de distribución temporal real de episodios (`distribucion_folds_momentum_dxy.py`, no corrido a ciegas con un default de otra hipótesis): con ~1029 episodios sobre 22.1 años, el máximo mecánico que respeta el piso de 30 trades/fold era K=18 pero con margen cero; se fijó K=16 (mínimo real 43 trades/fold, +43% de margen) para no depender de que ningún episodio se caiga en el filtrado de spread/ejecución.
3. **Selección de (k,M) en TRAIN** por t-stat sobre R neto (`metrica_robusta`, piso 30 trades), confirmación única en TEST.
4. **Std del umbral congelado en TRAIN**: decisión de diseño no cerrada explícitamente en la ficha original — usar el std del histórico completo (con datos futuros) para definir el umbral operativo en folds tempranos habría sido look-ahead sutil sobre el parámetro, no sobre la señal en sí. Se resolvió con el mismo criterio que el resto del proyecto usa para hiperparámetros: todo lo que se "conoce" para operar en TEST viene de TRAIN.
5. **Spread real**: `descontar_spread`, `SPREAD_PUNTOS=30` (misma constante de toda la familia EMA9/21 y de DFII10).

Scripts: `diagnostico_frecuencia_momentum_dxy.py`, `distribucion_folds_momentum_dxy.py`, `hipotesis_macro_momentum_dxy.py` (mismo patrón que los de DFII10, en la raíz del proyecto).

## Resultado (2026-08-03)

**❌ NO PASA EL CHECKPOINT** — descartada limpiamente, sin ambigüedad de fold marginal como DFII10.

| Métrica | Valor |
|---|---|
| Folds evaluables | 16/16 |
| Folds rentables (neto de spread) | 6/16 (37.5%) |
| Trades TEST acumulados | 678 |
| R neto acumulado | -17.20R |
| t-stat pooled (todos los folds) | -0.986 (p=0.324) |
| t-stat sin el fold más fuerte (Fold 11) | -1.195 (p=0.232) |

Regla de corte pre-registrada: \|t\| > 1.96. Ninguno de los dos t-stats se acerca, y ambos son **negativos** (pierde neto de spread), no un caso marginal-positivo como DFII10 (p=0.059) o límite como ratio oro/plata (p=0.11) — acá no hay lectura ambigua que discutir. No llegó a evaluarse DSR (Fase 2): el t-stat simple ya descarta antes de esa capa.

Por la regla de corte fijada de antemano, **no se prueba la dirección contraria ni se resweepea la grilla** ahora que se vio el resultado — eso sería exactamente la racionalización post-hoc que `hypothesis-gate` existe para evitar. Si en el futuro hay una razón *nueva*, no derivada de este resultado, para sospechar que el mecanismo es distinto, sería una hipótesis separada que entra de nuevo por Fase 0.

## Ver también
[[Candidatos futuros]] · [[Macro DXY - fase 1]] · [[Objetivo del proyecto - biblioteca de factores]] · [[hypothesis-gate]] · [[Estado actual y próximos pasos]]
