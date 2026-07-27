# Metodología — disciplina de validación del proyecto

Índice: [[Bienvenido]]

Estas prácticas se fueron incorporando entre el 2026-07-21 y el 2026-07-22 (ver [[Cronología]] y [[Errores y bugs corregidos]] para el detalle de qué problema motivó cada una) y después se mantuvieron sin excepción para toda hipótesis nueva. No son un checklist genérico: cada una responde a un error concreto que ya se cometió una vez en este proyecto.

## Separación honesta TRAIN/TEST

**Qué**: dentro de cada fold, los parámetros (R:R, trailing, filtro de sesión) se eligen mirando *solo* el tramo TRAIN. El tramo TEST se evalúa una única vez, con los parámetros ya fijados, y nunca se vuelve a mirar para ajustar nada.

**Por qué**: la primera versión del pipeline optimizaba los barridos de R:R/trailing/filtro de sesión sobre *todo* el dataset y recién después aplicaba un split 70/30 — para ese punto el "TEST" ya estaba contaminado, porque los parámetros elegidos ya habían visto esos datos indirectamente (a través del barrido conjunto). Ver [[Errores y bugs corregidos]]#Data-snooping-estructural.

## Walk-forward anclado multi-fold

**Qué**: en vez de un único corte 70/30, el dataset se corta en N folds anclados (expanding window): cada fold tiene su propio TRAIN (que crece) y su propio TEST (tramo cronológico disjunto, nunca visto antes por esa selección de parámetros).

**Por qué**: un único split 70/30 da un solo punto de dato sobre "¿esto generaliza?" — no alcanza para distinguir un edge real de que el TEST elegido haya caído, por azar, en un período favorable. Con N folds se obtienen N mediciones independientes del mismo procedimiento, lo que permite ver si el resultado es consistente o depende de un tramo particular del calendario.

**Parámetro elegido**: `N_FOLDS=9` por defecto (10 bloques de ~1500 velas c/u en M15, más poder estadístico que los 4 folds probados inicialmente). Para la hipótesis macro DFII10, con episodios mucho más escasos que cruces EMA, se usó `N_FOLDS=4` para no caer por debajo del piso de trades por fold — ver [[Macro DFII10 - fase 1]].

## Chequeo de fold dominante antes de confiar en un resultado agregado

**Qué**: cuando un walk-forward da folds rentables en mayoría, siempre se recalcula el resultado **sin el fold más fuerte**, y se reporta qué porcentaje del R neto total concentra ese único fold.

**Por qué**: un R total agregado positivo puede ser enteramente producto de un solo período excepcional (una racha, un movimiento macro puntual) sin que el resto de los folds aporte nada — ese no es un edge robusto, es un outlier temporal disfrazado de resultado agregado. Este chequeo fue el que evitó declarar "edge confirmado" en el baseline M15 pese a tener 5-7 de 9 folds rentables: el fold más fuerte llegó a concentrar 51-93% del R neto según la corrida, y sin él el resto no era significativo (t≈0.6). Ver [[EMA baseline (M15)]].

## Criterio de selección: t-stat sobre R neto de spread, con piso de trades

**Qué**: `metrica_robusta` — en vez de elegir la configuración con mayor R total crudo, se elige la que tiene mejor t-stat sobre el R **neto de spread**, exigiendo un piso de 30 trades (`MIN_TRADES_SELECCION`) para que el resultado cuente.

**Por qué**: el R total crudo premia a un ganador espurio de muestra chica (2-3 trades grandes por azar) y además ignora el costo real de operar (spread). El t-stat normaliza por la varianza de la muestra, y el piso de 30 trades evita que un fold con 5 trades "gane" el barrido por pura casualidad. Ver [[Errores y bugs corregidos]].

## Diagnóstico entrada-vs-salida

**Qué**: antes de aceptar o descartar una hipótesis solo por su R total agregado, se corre un barrido de R:R en TRAIN (`diagnostico_entrada_vs_salida`/`elegir_mejor_rr`) para ver si el edge está en la *entrada* (la dirección de la señal predice algo, con margen en varios R:R) o depende de acertar la *salida* exacta (solo 1 de 5 R:R muestra edge, sin margen).

**Por qué**: dos hipótesis pueden tener el mismo R total agregado por razones completamente distintas — una por señal genuinamente predictiva, otra por haber acertado casualmente un R:R en un barrido. Distinguir esto cambia qué se hace después: si el problema es la salida, vale la pena probar gestión de salida distinta (partial/trailing); si el problema es la entrada, ningún cambio de salida lo va a arreglar. Ver [[Diagnóstico entrada-vs-salida]] para el caso donde esto marcó la diferencia entre dos hipótesis.

## Reglas de corte definidas ANTES de correr cada experimento

**Qué**: para cada hipótesis nueva, se escribe de antemano (a) qué resultado exacto se necesita ver para considerarla viable y (b) qué resultado la descarta — antes de correr el experimento o mirar cualquier dato.

**Por qué**: decidir el criterio de éxito *después* de ver el resultado es la forma más fácil de auto-engañarse (mover la meta para que el resultado obtenido "cuente" como éxito). Pre-registrar la regla de corte convierte cada experimento en una prueba real, no en una excusa para justificar lo que ya se quería creer. Esto es lo que permitió cerrar la familia EMA9/21 completa en base a evidencia — sin la regla de corte pre-registrada del chequeo de partial/trailing, hubiera sido tentador "probar una variante más" indefinidamente. Ver [[Diagnóstico entrada-vs-salida]] y el cierre de capítulo en [[EMA baseline (M15)]].

**Regla general vigente desde el 2026-07-24** (aplica a cualquier hipótesis nueva, no solo a las de EMA): antes de arrancar, definir (1) una frase concreta y falsable de qué señal específica se va a probar y (2) su propia regla de corte. Una categoría amplia como "macro/fundamental" no alcanza — tiene que ser una hipótesis puntual. Ver [[Estado actual y próximos pasos]].

## Commit antes de que exista dato fresco (loggers en vivo)

**Qué**: la lógica de cada logger en vivo (`log_senales_demo.py`, `log_senal_macro_dfii10.py`) se commitea/congela **antes** de que exista un solo dato real en el CSV de salida.

**Por qué**: deja un timestamp verificable de que la lógica no se ajustó después de mirar cómo salían las primeras señales reales. Cualquier fix posterior a la lógica va en un commit aparte, así se puede filtrar por fecha de commit qué filas del historial son pre-fix y cuáles post-fix — sin esto, sería imposible distinguir "el logger predijo bien" de "se lo ajustó hasta que predijo bien".

## No recortar el mismo dataset de más formas para buscar confirmación

**Qué**: una vez que un tramo de datos histórico ya fue "mirado" (usado como TEST en algún walk-forward, con cualquier partición de folds), no se lo vuelve a cortar de otra manera buscando un resultado distinto. La única confirmación final honesta es con datos genuinamente nuevos hacia adelante (holdout en vivo).

**Por qué**: las mismas 15.000 velas M15 se cortaron de tres formas distintas (split 70/30, walk-forward de 4 folds, walk-forward de 9 folds) a lo largo del proyecto — para cuando se llegó a evaluar el trigger de ruptura+retest, **todas** las fechas del rango ya habían aparecido como TEST en alguna configuración anterior. Seguir "mirando" ese mismo tramo de infinitas formas hasta que una dé un resultado favorable es exactamente el problema de comparaciones múltiples (multiple-comparisons) que toda esta disciplina busca evitar. Por eso los loggers en vivo existen: son la única fuente de datos que ningún análisis retrospectivo tocó todavía.

## Ver también
[[Cronología]] · [[Errores y bugs corregidos]] · [[Diagnóstico entrada-vs-salida]]
