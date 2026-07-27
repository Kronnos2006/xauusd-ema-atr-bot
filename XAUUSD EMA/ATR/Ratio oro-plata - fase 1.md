# Ratio oro/plata (XAUUSD/XAGUSD) — fase 1 (descartado)

Índice: [[Bienvenido]] · Ver también [[Macro DFII10 - fase 1]] · [[Macro 2s10s - fase 1]] · [[Metodología]]

## Contexto

Segundo candidato explorado el 2026-07-27, después de que [[Macro DXY - fase 1]] quedara bloqueado antes de siquiera empezar (sin instrumento real en el broker). A diferencia de DXY, este candidato pasó el screening inicial: ambos símbolos (`XAUUSD`, `XAGUSD`) están confirmados en MT5 real, sin investigación de fuente pendiente.

## Hipótesis (frase falsable)

Cuando el ratio XAUUSD/XAGUSD se aleja más de X desvíos estándar de su propia media móvil de Y días hábiles, el oro tiene sesgo direccional **opuesto** al signo del z-score en las Z sesiones siguientes: z > +X (oro caro relativo a la plata) → sesgo bajista; z < −X (oro barato relativo a la plata) → sesgo alcista. A diferencia de DFII10/2s10s (solo compra), esta hipótesis es bidireccional por construcción.

## Metodología

1. **Chequeo de frecuencia previo** (`diagnostico_frecuencia_ratio_oro_plata.py`): 106 a 425 episodios según la combinación (Y,X), sobre 17.7 años de historial solapado XAUUSD/XAGUSD (XAGUSD arranca en este broker en 2008-11-07, más tarde que XAUUSD) — 6 a 24 episodios/año, orden de magnitud comparable o mejor que DFII10 (132-291 episodios en >20 años).
2. **Walk-forward de 4 folds anclados** (mismo N_FOLDS que DFII10 — derivado por comparación de frecuencia, no copiado a ciegas) sobre grilla 3×2×3 (Y∈{20,60,120} × X∈{1.5,2.0} × Z∈{5,10,20} sesiones de horizonte). Grilla más ancha que la 3×3 de DFII10 porque suma el umbral X como grado de libertad nuevo — documentado explícitamente, no oculto.
3. Sin verificación cruzada de fuente aplicable: XAUUSD/XAGUSD ya son la fuente primaria validada de todo el proyecto (MT5 real), no una fuente macro externa nueva como FRED.

Código: `diagnostico_frecuencia_ratio_oro_plata.py` y `hipotesis_macro_ratio_oro_plata.py` (ambos commiteados).

## Resultado (2026-07-27)

**NO PASA el checkpoint exploratorio** — descartado, con un patrón que la propia disciplina del proyecto está diseñada para atrapar:

- **4/4 folds rentables netos de spread** (151 trades TEST acumulados, +31.73R neto total) — a primera vista suena como el resultado más fuerte de cualquier hipótesis macro probada hasta ahora.
- **Pero el t-stat pooled real no es significativo**: con los 4 folds, t=+1.581, **p=0.1138** — ni siquiera cerca del umbral convencional de 0.05.
- **Sin el fold más fuerte** (Fold 1, 2012-06-07→2015-12-17, que concentra **63% del R neto acumulado** — más que el 51% de concentración que en su momento sí se consideró señal real de dependencia en el caso M15 baseline): t=+0.727, **p=0.4671** — esencialmente ruido.
- **Conclusión: "4 de 4 folds ganadores" es el ejemplo exacto de conteo de folds que suena más fuerte de lo que es** — con una moneda sesgada por casualidad hacia un solo fold dominante, el patrón agregado no es distinguible de azar. Ningún parámetro (Y, X, Z) se itera fuera de la grilla ya declarada.

**Nota metodológica (autocrítica, para dejar constancia)**: la regla de corte pre-registrada en el docstring del código ("si no sostiene edge en la mayoría de folds sin depender de un fold dominante, se descarta") quedó redactada de forma más laxa que la de DFII10/2s10s (que fijaron un umbral numérico p<0.05 explícito antes de correr nada). El veredicto final aplicó el mismo estándar de todas formas (p<0.05 como vara de facto usada en el resto del proyecto), pero la próxima hipótesis debería fijar el número exacto en el docstring antes de correr, no solo la intención cualitativa.

## Cómo aplicar

No retomar esta definición del ratio oro/plata salvo una razón nueva y específica (otra ventana Y, otro umbral X, u otro mecanismo de traducir la reversión del ratio en una posición direccional en oro — la elección actual de "vender oro cuando el ratio está caro" fue una decisión de diseño razonable pero no la única posible, y no se descartaron alternativas como operar el ratio mismo como par). Datos y código quedan disponibles si se retoma.

## Ver también
[[Macro DXY - fase 1]] · [[Macro DFII10 - fase 1]] · [[Macro 2s10s - fase 1]] · [[Estado actual y próximos pasos]]
