# HP-008 (encargo a portafolio-investigador, Fase 0) — 2026-11-11

Autor del encargo: `jefe-portafolio`. Estado: **idea**. 0 resultados calculados, 0 variantes. Sin dinero ni órdenes.

## Idea (1 línea)
Rezago BTC -> altcoins en 1 h: el retorno de BTC en la hora t predice el signo del retorno de ETH/SOL/XRP/BNB en la hora t+1 (liderazgo de precio del activo más líquido).

## Por qué vale como Fase 0
- Potencia alta por N: BTC 80.308 velas 1 h (2017-08 a 2026-10); ETH/BNB/SOL/XRP 18.265 velas c/u (2024-07 a 2026-08), sin huecos (`data/kt004/manifiesto_datos.json`). Los descartes previos (HP-004 a HP-007) fallaron por pocos eventos; este tiene miles.
- No repite nada cerrado (no es momentum largo, ni calendario, ni 13F).
- Fundamento a citar y verificar por el investigador (marcar NO VERIFICADO si el proxy lo bloquea): literatura de lead-lag y liderazgo de precio cripto.

## Qué debe hacer la Fase 0 (solo conteos, potencia y costos; NO correlaciones ni retornos de la señal)
1. N de observaciones por par y N efectivo (autocorrelación de la volatilidad).
2. MDE de la correlación/acierto con ese N, contra el efecto plausible.
3. Costos de `riesgo-costos`: spread medido ~0,00001 % (`data/mercado/spread_btcusdt.csv`) frente a comisión/deslizamiento de 1 h de rotación; ¿el efecto esperado supera el costo por operación?
4. Piso de 30 operaciones por fold y folds derivados de la distribución real.
5. Borrador de Fase 1 con **PENDIENTE DEL USUARIO** en lo que él no dio.

## Cautelas (para el desconfiado)
- Los CSV de `data/kt004/` pertenecen a KT-004 (confirmación prospectiva): no usar su tramo sellado/holdout ni tocar esos archivos; confirmar con KT-004 qué tramo está libre.
- Un rezago de 1 h entre velas de cierre exige ejecutar en la apertura de t+1: modelar ese retraso y el deslizamiento.
- Riesgo de descarte: en cripto 1 h el rezago suele estar arbitrado y el costo real por rotación horaria (~0,1 %/lado en comisión) puede superar el efecto.
- Nada se calcula sobre la señal antes de registro previo, desconfiado y jefe de riesgo.
