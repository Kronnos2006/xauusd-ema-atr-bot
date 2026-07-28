# Macro DXY — fase 1 (proxy sintético validado, en curso)

Índice: [[Bienvenido]] · Ver también [[Macro DFII10 - fase 1]] · [[Metodología]]

## Contexto

Candidato explorado el 2026-07-27 como posible próxima hipótesis, en paralelo a [[Macro DFII10 - fase 1]] (activa, con reservas) y después de descartar [[Macro 2s10s - fase 1]]. Screening inicial (antes de comprometerse) señaló a DXY como el candidato más limpio: mismo patrón que DFII10 ("caída sostenida de N días → sesgo alcista en oro") y, en apariencia, mismos datos ya disponibles vía MT5.

## Frase falsable propuesta (nunca llegó a formalizarse del todo)

Cuando el índice dólar (DXY) viene cayendo de forma sostenida en los últimos N días hábiles, el oro tiene sesgo alcista sostenido en las M sesiones siguientes — misma estructura que DFII10, con la grilla N/M a definir según el chequeo de frecuencia.

## Bloqueo encontrado (2026-07-27) — antes del chequeo de frecuencia, no después

Al intentar el primer paso (chequeo de frecuencia sobre el histórico de DXY en MT5), se descubrió que **este broker no ofrece el índice dólar real (ICE DXY) bajo ningún símbolo**:

- `USDX` existe como símbolo, pero es *"SGI Enhanced Core ETF"* (Nasdaq, ISIN `US74933W2540`) — un ETF de renta fija sin relación con el dólar, con solo 593 velas D1 (2024-02-29 → hoy).
- `DXYN` = *"The Dixie Group Inc"* (fabricante de alfombras), `DXYZ` = *"Destiny Tech100 Inc."* (fondo cerrado), `GDXY` = *"YieldMax Gold Miners Option Income Strategy ETF"* — los cuatro son coincidencias de ticker, no el índice dólar.
- Búsqueda exhaustiva por descripción (`"DOLLAR INDEX"`, `"US DOLLAR"`) solo devuelve los pares forex individuales (`EURUSD`, `USDJPY`, etc.), nunca un índice compuesto.
- Categorías completas de símbolos del broker: `Forex`, `Indexes` (solo bursátiles: SPX, DAX, FTSE, Nikkei, etc.), `Metals`, `Nasdaq` — ninguna contiene un índice de moneda.

**Conclusión: DXY no es testeable con los datos de este broker tal como está planteado.** No es un problema de baja frecuencia (como podría haber pasado con COT) — es la ausencia total del instrumento.

## Decisión pendiente de confirmación (bloqueado, no decidido unilateralmente)

Existe un camino técnico para no abandonar la idea del todo: construir un DXY sintético a partir de los 6 pares que componen la fórmula real del índice ICE (`EURUSD`, `USDJPY`, `GBPUSD`, `USDCAD`, `USDSEK`, `USDCHF`, con los pesos fijos de la fórmula oficial `50.14348112 × EURUSD^-0.576 × USDJPY^0.136 × GBPUSD^-0.119 × USDCAD^0.091 × USDSEK^0.042 × USDCHF^0.036`) — los 6 pares están disponibles en este mismo broker. Se dejó **sin decidir** porque cambia el carácter de la hipótesis (una construcción propia con su propia metodología y limitada por el historial más corto de sus 6 componentes, no un dato de mercado directo) y no es una decisión que corresponda tomar sin el usuario — análoga a por qué DFII10 usó FRED como fuente en vez de improvisar un proxy.

## Confirmado: construcción del proxy sintético (2026-07-27)

El usuario confirmó explícitamente construir el proxy sintético desde los 6 pares FX con la fórmula real de ICE (no una aproximación propia):

```
USDX = 50.14348112 × EURUSD^(-0.576) × USDJPY^(+0.136) × GBPUSD^(-0.119)
                    × USDCAD^(+0.091) × USDSEK^(+0.042) × USDCHF^(+0.036)
```

Nota sobre signos: EURUSD/GBPUSD llevan exponente **negativo** (se cotizan "dólares por unidad de la otra moneda" — bajan cuando el dólar se fortalece), el resto **positivo** (se cotizan al revés). Los pesos que dio el usuario en porcentaje sin signo (57.6/13.6/11.9/9.1/4.2/3.6) coinciden en magnitud con los exponentes reales, pero el signo se completó con la fórmula estándar publicada, no inventado.

Código escrito en `construir_dxy_sintetico.py` (commiteado), listo para correr — **pero bloqueado antes de poder validarlo**.

## Bloqueo nuevo (2026-07-27) — conexión MT5, no de diseño

Al intentar bajar el historial D1 de los 6 pares FX, dos intentos sucesivos de conectar a MT5 quedaron colgados sin completar ni fallar (`mt5.initialize()`/`copy_rates_range` nunca retornan), dejando dos procesos Python huérfanos compitiendo por el canal IPC del terminal. Matar esos procesos (`Stop-Process`) fue **denegado por el clasificador de auto-mode** de la sesión — no se insistió, siguiendo la instrucción explícita del usuario de documentar y no forzar bloqueos que requieren su confirmación.

**Verificado que no es un problema de infraestructura productiva**: los dos loggers en vivo (EMA y Macro DFII10) no muestran errores nuevos en sus logs desde la remediación del mismo día (27/7 15:54 UTC) — el colgado es aislado a los scripts de diagnóstico ad-hoc de esta sesión, no afecta los procesos productivos.

**Pendiente para retomar**: el usuario necesita liberar la conexión (matar los procesos Python colgados, o confirmar que ya se resolvieron solos/reiniciar el terminal MT5 si hace falta) antes de que se pueda bajar el historial de los 6 pares FX y completar la validación (paso 2 del plan: comparar contra 5-10 valores reales publicados de DXY, ya obtenidos de investing.com para fechas de julio 2026 — falta el lado del cálculo sintético).

## Bloqueo de conexión resuelto (2026-07-27)

El usuario liberó la conexión MT5 (procesos colgados terminados/reiniciados). Diagnóstico posterior sobre los procesos que sí llegaron a completar: no era un deadlock real sino una sincronización de historial muy lenta la primera vez que el terminal accede a un símbolo nunca antes seleccionado (~4 minutos por par en el peor caso) — quedó resuelto simplemente esperando o reintentando, sin necesidad de intervención más allá de liberar el canal.

## Validación del proxy sintético (2026-07-27)

`construir_dxy_sintetico.py` bajó los 6 pares (2000-01-03 → 2026-07-27, 6902 días solapados) y calculó la serie con la fórmula ICE exacta. `validar_dxy_sintetico.py` comparó 21 de 23 fechas de referencia (investing.com, 2026-06-29 → 2026-07-27) contra el cálculo:

- **Correlación: 0.9945**. Diferencia absoluta media: 0.023 puntos (~0.02% del nivel del índice, ~101). Máxima: 0.069.
- **3/21 fechas superan el umbral estricto de 0.05** prestado de la verificación FRED-vs-Treasury de DFII10 (07-07: 0.067, 07-08: 0.069, 07-13: 0.062) — ese umbral se calibró para puntos porcentuales de tasa de interés, una escala distinta a puntos de un índice ~100, así que no es directamente comparable. Sin sesgo direccional visible en los residuos (no hay patrón de sobre/sub-estimación sistemática) — el patrón es consistente con diferencias de timing de cotización FX entre el broker de este proyecto y el settlement oficial de ICE, no con un error de fórmula.
- **Veredicto: validación aceptada** sobre el criterio sustantivo (correlación + error relativo pequeño, sin sesgo), con la reserva de las 3 fechas anotada explícitamente. Se procedió al chequeo de frecuencia y walk-forward.

## Chequeo de frecuencia (2026-07-27)

`diagnostico_frecuencia_dxy.py`, misma definición que DFII10 (`DXY[t] < DXY[t-N]`). Restringido al rango de datos de oro en MT5 (2004-06-11+): **260 episodios (N=20), 200 (N=60), 111 (N=120)** — comparable a DFII10 (291/177/132). Justifica N_FOLDS=4, igual que DFII10.

## Resultado del walk-forward (2026-07-27) — NO PASA el checkpoint

`hipotesis_macro_dxy.py`, mismo diseño exacto que DFII10 (frase, entrada D+1, ATR SL, horizonte M, walk-forward 4 folds anclados, grilla 3×3 de N×M), única variable cambiada: la fuente macro. Regla de corte fijada **antes de correr** (más estricta que la redacción original de DFII10, corrigiendo la falta de un número explícito señalada en la nota metodológica de [[Ratio oro-plata - fase 1]]): p<0.05 en el t-stat pooled, con y sin el fold más fuerte.

- **3/4 folds rentables netos** (149 trades TEST acumulados, +27.18R neto total).
- **t-stat pooled con todos los folds: p=0.0720** — no cruza 0.05.
- **Sin el fold más fuerte** (Fold 4, 2022-02-24→2026-07-27, 59% del R neto acumulado): **p=0.3057** — no significativo.
- **NO PASA**, aplicando la regla pre-registrada sin ambigüedad. Nota de consistencia: incluso con el estándar más laxo que se usó originalmente para DFII10 (solo mirar el p con todos los folds, sin exigir también <0.05 sin el fold dominante), DXY seguiría sin pasar — su p=0.072 es peor que el p=0.059 marginal de DFII10.

**Conclusión**: el proxy sintético valida bien como serie de datos, pero la hipótesis en sí (caída sostenida de DXY → sesgo alcista en oro) no muestra un edge estadísticamente distinguible de ruido con esta definición. No se itera N/M fuera de la grilla ya declarada.

## Cómo aplicar

No retomar DXY salvo una razón nueva y específica (otra definición de "caída sostenida", otro horizonte, o combinarlo como filtro de otra señal en vez de hipótesis propia). Código en `construir_dxy_sintetico.py`, `validar_dxy_sintetico.py`, `diagnostico_frecuencia_dxy.py`, `hipotesis_macro_dxy.py` (todos commiteados). Serie en `historial/dxy_sintetico.csv` (ignorada por git).

## Ver también
[[Macro DFII10 - fase 1]] · [[Macro 2s10s - fase 1]] · [[Estado actual y próximos pasos]]
