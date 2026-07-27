# Diagnóstico entrada-vs-salida — el hallazgo más informativo del proyecto

Índice: [[Bienvenido]] · Ver también [[Metodología]] · [[EMA baseline (M15)]] · [[Ruptura y retest]]

## La pregunta

Tras 4 hipótesis de entrada/filtro fallidas (M15 baseline, MTF, estructura HH/HL, ruptura+retest — todas con el mismo síntoma: a veces mayoría de folds rentables pero agregado negativo, a veces folds ganadores/perdedores sin relación entre variantes, a veces resultado dominado por 1 fold), surgió una pregunta de fondo nunca explorada: **¿el problema es específico de cada trigger probado, o es la estructura de salida (SL 1.5×ATR fijo, TP en múltiplo R:R fijo) la que no logra capturar edge en este mercado/timeframe, sin importar qué tan buena sea la entrada?** Ninguna de las 4 variantes había tocado la salida — todas reusaban el mismo SL/TP ATR-based.

## Metodología (2026-07-24)

Reutilizando `diagnostico_entrada_vs_salida`/`elegir_mejor_rr` dentro de la disciplina honesta ya establecida (TRAIN barre R:R por t-stat, TEST solo confirma — ver [[Metodología]]), corrido para Baseline y para Retest sobre los mismos 9 folds. La pregunta que responde: en cada fold, ¿cuántos de los 5 R:R barridos en TRAIN muestran edge positivo? Si son varios (edge amplio, con margen), es señal de entrada genuina. Si es solo 1 de 5, el "edge" depende de acertar exactamente ese R:R — más parecido a ruido que a señal.

## Resultado: Ruptura y retest — el problema es la entrada

Edge de entrada débil y no persistente: en folds 6-9 solo 1 de los 5 R:R barridos mostraba edge>0 en TRAIN (vs 4-5/5 en baseline). El R:R elegido en TRAIN solo se sostuvo en TEST en 4/9 folds (44%, básicamente azar). El fold que explota (Fold 5: TRAIN edge +4.2pp, mismo R:R en TEST da -10.1pp, R total -19.00R) confirma que ahí la señal falla de lado con cualquier R:R — no es una salida mal calibrada sobre una entrada buena. **Conclusión: para Retest, un exit distinto (partial/trailing) no lo hubiera salvado.** Ver [[Ruptura y retest]].

## Resultado: Baseline M15 — primer hallazgo genuinamente alentador del proyecto

4-5 de 5 R:R con edge>0 en TRAIN en casi todos los folds (edge amplio, no depende de acertar el R:R exacto) y sostiene en TEST en **8 de 9 folds (89%)**. Es la primera variante que muestra edge de entrada real y consistente, no solo "gana en un fold suertudo". Esto cambió el marco de la decisión: no era un quinto intento de entrada a ciegas, sino actuar sobre evidencia positiva concreta de la única variante que se había ganado seguir siendo investigada.

El problema de Baseline era otro, ya conocido: un solo fold (Fold 1) concentra la mayoría del R neto agregado — posible sobre-dependencia de un período/racha excepcional, en principio gestionable por el lado de la salida (partial-close/trailing), no un problema de que la señal no prediga dirección.

## El chequeo de partial-close/trailing

**Regla de corte pre-registrada (2026-07-24), antes de correr nada**: si partial+trailing en Baseline NO reduce la concentración en Fold 1 de forma clara, O el resultado no sostiene en TEST, ese es el punto donde se para POR COMPLETO el enfoque de entrada técnica pura en M15/XAUUSD — no se diseña un sexto intento de entrada dentro de la misma familia de ideas.

**Criterio de éxito explícito**: reportar el % de concentración del R neto total en el fold más fuerte, antes (TP fijo) y después (partial+trailing) de aplicar la gestión combinada. Subir el R total sin bajar la concentración NO cuenta como mejora.

**Resultado, misma disciplina honesta** (`optimizar_trailing` elige por t-stat solo en TRAIN, `backtest_trailing_con_mult` confirma en TEST, mismos 9 folds):

| | TP fijo | Partial+trailing |
|---|---|---|
| R neto total | **+14.08R** | **-8.05R** |
| Folds rentables | 7/9 | 3/9 |
| Concentración Fold 1 | 93% | no bajó |

Los folds 3, 5, 6 y 7 — rentables con TP fijo — pasaron a perder con trailing. La concentración en Fold 1 no bajó; lo que empeoró fue todo lo demás, y el agregado se dio vuelta a negativo. Los t-stat con que `optimizar_trailing` eligió la combinación en cada TRAIN fueron todos débiles (~1.0-1.8, ninguno robusto) — mismo patrón de "edge delgado que no generaliza" ya visto con Retest.

**Esto cumple la condición de corte pre-registrada, sin ambigüedad**: no es un caso límite, es una reversión clara en la dirección contraria a la esperada.

## Lectura de por qué pasó esto

La hipótesis más plausible: el baseline M15 probablemente estaba montando una tendencia macro puntual del activo (XAUUSD tuvo una década 2016-2026 casi ininterrumpidamente alcista, +210%, 8 de 11 años positivos — ver contexto en [[Cronología]]), concentrada en el fold que coincidió con ese movimiento, más que una señal que el cruce EMA9/21 realmente predijera de forma repetible. Cuando la gestión de salida intentó "estirar" las ganancias de ese movimiento puntual con trailing, en vez de mejorar el resultado lo empeoró — consistente con que no había una tendencia recurrente y capturable ahí, sino un tramo de suerte direccional que el TP fijo capturaba de casualidad y el trailing, al intentar exprimir más, exponía a más ruido.

## Conclusión formal

Se para el enfoque de entrada técnica pura (cruce EMA + variantes de filtro/trigger) en M15/XAUUSD tal como fue explorado. **Encuadre correcto**: esto NO es "el proyecto fracasó" — es la regla de corte pre-registrada funcionando exactamente como fue diseñada, evitando 6-7 iteraciones más de diseño de entrada sobre una premisa ya descartada con datos. El resultado correcto para registrar es "M15 técnico puro no tiene edge confirmable", un hallazgo válido y útil.

## Ver también
[[EMA baseline (M15)]] · [[Ruptura y retest]] · [[Metodología]] · [[Cronología]]
