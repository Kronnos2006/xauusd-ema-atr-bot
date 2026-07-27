# Macro DXY — fase 1 (bloqueado antes de empezar: sin instrumento real)

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

## Cómo aplicar

No retomar DXY salvo que: (a) el usuario confirme explícitamente construir el proxy sintético descrito arriba, o (b) aparezca otra fuente de datos real para el índice dólar (ej. una fuente externa tipo FRED, a verificar). Hasta entonces, este candidato queda cerrado sin haber llegado siquiera al chequeo de frecuencia.

## Ver también
[[Macro DFII10 - fase 1]] · [[Macro 2s10s - fase 1]] · [[Estado actual y próximos pasos]]
