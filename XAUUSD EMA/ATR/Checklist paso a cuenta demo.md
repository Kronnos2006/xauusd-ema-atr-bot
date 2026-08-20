# Checklist objetivo — paso a cuenta demo

Índice: [[Bienvenido]] · Ver también [[Metodología]] · [[Macro DFII10 - fase 1]]

Redactado el 2026-07-27, **antes de que ninguna hipótesis esté cerca de necesitarlo** — a propósito, para que los umbrales no se negocien bajo presión el día que un resultado esté "casi" pasando. Aplica a cualquier hipótesis futura, no solo a DFII10. Si algún número acá se cambia más adelante, el cambio y su motivo quedan documentados en esta misma nota, con fecha — no se edita en silencio.

## Los nueve criterios

Los nueve tienen que cumplirse a la vez (los criterios 8 y 9 agregados el 2026-07-27, revisión externa). No hay promedio ni "pasa 7 de 9" — es la misma disciplina binaria (PASA / NO LISTO) que ya usa `hypothesis-gate` para el checkpoint exploratorio, aplicada un escalón más arriba.

### 1. Significancia estadística fuera de muestra
**t-stat pooled sobre R neto de spread, con Y sin el fold/período más fuerte, ambos con p < 0.05 (dos colas).**
No alcanza con que el p-value pooled cruce 0.05 si al sacar el resultado más fuerte deja de sostenerse — eso es depender de un solo período, no un edge estable. Mismo estándar ya aplicado (después de corregirlo) a DXY y al ratio oro/plata.

### 2. Tamaño de muestra mínimo fuera de muestra
**N ≥ el n necesario para 80% de poder estadístico al efecto YA OBSERVADO, calculado explícitamente (power analysis), no asumido.**
Advertencia de circularidad, para no repetir el error de tratarlo como una garantía: el n necesario se calcula con el efecto observado en la muestra actual, que puede reducirse con más datos (regresión a la media) o degradarse con el tiempo (cambio de régimen). Tratar el n del power analysis como **piso, no como objetivo fijo** — si al llegar a ese n el efecto se debilitó, recalcular antes de decidir, no usar el número viejo.

### 3. Máximo drawdown aceptable
**≤ 20%, sobre una curva de equity con un supuesto de riesgo por trade fijado de antemano** (1% es el default de reporte usado en este proyecto — ver [[Macro DFII10 - fase 1]] — pero el número real depende del riesgo por trade que se decida usar en demo, no de este porcentaje en abstracto).
20% es un default razonable, no una ley física — el usuario puede ajustarlo según su propia tolerancia, pero el número tiene que estar escrito ANTES de mirar el resultado de la hipótesis candidata, no elegido para que la hipótesis en cuestión pase.

### 4. Costos incluidos, y verificados contra la realidad
**Todo resultado se evalúa neto de spread, usando el mismo `SPREAD_PUNTOS` u costo equivalente ya validado para el resto del proyecto — y antes de ir a demo, ese supuesto de costo se contrasta contra el spread real registrado por el logger en vivo** (ya se registra spread/precio real en cada señal, ver [[Infraestructura]]), no solo contra el valor fijo asumido en el backtest.
Si el spread real observado en el holdout es sistemáticamente peor que el asumido, no se pasa a demo con el resultado del backtest sin re-verificar que el edge sobreviva al costo real.

### 5. Datos macro/externos verificados, sin contaminación de look-ahead
**Cualquier fuente de dato externa a MT5 (macro, intermarket) tiene que pasar verificación cruzada de fuente (ej. FRED vs. Treasury.gov) Y verificación de que la serie usada en el backtest coincide con la serie "tal como se conocía en tiempo real" en las fechas relevantes (ALFRED u equivalente para la fuente en cuestión).**
No alcanza con que la fuente sea "confiable" en general — series sujetas a revisión (a diferencia de DFII10, que no lo está) pueden dar un backtest optimista si se usa el valor revisado en vez del valor que realmente estaba disponible el día de la señal.

### 6. Consistencia cualitativa con el holdout en vivo
**El holdout genuinamente fuera de muestra (logger en vivo, no el walk-forward retrospectivo) tiene que acumular suficientes episodios como para no contradecir el signo y el orden de magnitud del resultado del walk-forward** — no se exige que el holdout por sí solo ya cumpla los criterios 1 y 2 en soledad (sería redundante con ellos), pero si el holdout en vivo apunta en la dirección contraria al walk-forward, eso pesa más que el walk-forward retrospectivo, no menos.

### 7. Regla de corte de la hipótesis, pre-registrada y respetada
**La hipótesis en cuestión tiene que tener su propia frase falsable y regla de corte fijadas ANTES de correr el walk-forward** (ya exigido por `hypothesis-gate` en la fase exploratoria) **Y el veredicto de este checklist tiene que aplicarse tal como está escrito acá, sin relajar ningún número porque el resultado "casi" pasa.**
Este último punto es el que más vale la pena escribir en frío: la tentación real no es ignorar un criterio entero, es mover un umbral 2-3 puntos porcentuales para que algo "casi listo" pase. Si eso pasa, es una señal de que el checklist se está usando mal, no de que el número original estaba mal.

### 8. Regla de degradación backtest → vivo

**Asumir que el Sharpe en cuenta viva va a ser el 40-60% del Sharpe de backtest (degradación conocida en la industria: costos no modelados, slippage, cambio de régimen, sesgo de selección del propio proceso de research). Para una hipótesis de baja frecuencia como las de este proyecto (pocos trades/año), esto exige un Sharpe de backtest ≥ 1.0-1.5 para tener una expectativa razonable de Sharpe en vivo positivo y útil.**

No es una corrección cosmética — con un Sharpe de backtest de 0.45 (el caso real de DFII10, ver [[Macro DFII10 - fase 1]]), el 40-60% esperado en vivo cae a 0.18-0.27, un nivel donde el ruido de ejecución real fácilmente se come cualquier edge. Este criterio es el motivo cuantitativo, no solo intuitivo, de por qué un Sharpe marginal en backtest no es "casi suficiente" — es estructuralmente insuficiente para sobrevivir el paso a vivo.

### 9. Autoridad para excepciones

**Solo el dueño del proyecto (el usuario) puede autorizar una excepción a cualquiera de estos nueve criterios, y tiene que hacerlo por escrito, con fecha y motivo, ANTES de la decisión de pasar a demo — nunca implícita, nunca decidida unilateralmente por el asistente.**

El asistente (Claude Code, cualquier skill o agente de este proyecto) puede señalar que un criterio no se cumple y puede opinar sobre si una excepción parece razonable, pero **no tiene autoridad para decidir que un criterio no aplica esta vez** ni para avanzar a demo asumiendo que una excepción está implícita. Cualquier excepción ejercida queda registrada en esta misma nota (nueva entrada abajo, con fecha) — no se relaja un umbral en silencio ni se edita el criterio original para que encaje con un resultado ya visto.

## Aplicación ilustrativa a DFII10 (2026-07-27, no es un veredicto de este checklist — la hipótesis nunca se propuso para demo)

Para que quede concreto, no solo abstracto — cómo se ve DFII10 hoy contra cada criterio, sin que esto implique que DFII10 esté siendo evaluada para pasar a demo (no lo está, ver [[Macro DFII10 - fase 1]]):

| Criterio | Estado de DFII10 hoy |
|---|---|
| 1. p<0.05 con y sin fold más fuerte | ❌ p=0.059 pooled (ni siquiera con todos los folds), p=0.30 sin el dominante |
| 2. N ≥ n para 80% poder | ❌ n=87 vs. n=192 necesario — faltan 105 trades (~13 años a la frecuencia actual) |
| 3. Drawdown ≤ 20% | ✅ -6.09% |
| 4. Costos incluidos y verificados | ✅ incluido (SPREAD_PUNTOS=30); verificación contra spread real pendiente (0 episodios en el holdout todavía) |
| 5. Datos sin look-ahead | ✅ verificado vía ALFRED, sin contaminación |
| 6. Consistencia con holdout en vivo | ⏳ sin datos todavía (0 episodios acumulados) |
| 7. Regla de corte pre-registrada | ✅ definida desde el inicio de la hipótesis |
| 8. Sharpe backtest ≥ 1.0-1.5 (para Sharpe vivo positivo) | ❌ Sharpe backtest = 0.453 — muy por debajo del piso, ni siquiera con el mejor escenario de degradación (60%) llegaría a algo útil |
| 9. Excepción autorizada por escrito | N/D — no se está evaluando pasar a demo, no aplica todavía |

Cumple 4 de 9 con certeza, 1 pendiente de datos, 1 no aplicable en este momento, y falla los tres criterios más duros (significancia estadística, tamaño de muestra, y ahora también Sharpe de backtest) por márgenes que no se cierran esperando poco tiempo. Consistente con la reclasificación a factor archivado (ver [[Objetivo del proyecto - biblioteca de factores]]).

## Registro de excepciones ejercidas

(Vacío al 2026-07-27 — ninguna excepción se ejerció todavía. Cualquier excepción futura se agrega acá, con fecha, criterio afectado, motivo, y quién la autorizó.)

## Ver también
[[Macro DFII10 - fase 1]] · [[Metodología]] · [[Infraestructura]] · [[Objetivo del proyecto - biblioteca de factores]]
