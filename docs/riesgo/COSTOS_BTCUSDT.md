# Costos reales BTCUSDT spot (riesgo-costos)

- **Autor:** riesgo-costos · **Fecha:** 2026-10-21 · **Encargo:** `docs/riesgo/ENCARGO_COSTOS_BTC.md`
- **Estado:** PARCIAL. Binance (api, www, fapi, data-api.binance.vision) devolvió 403 desde el proxy del entorno: **no se pudo medir libro, spread ni funding**. Lo no medido queda como SUPUESTO de peor caso. Solo el umbral de equilibrio (sección 3) está calculado con datos.

## 1. Tabla de costos

| Componente | Valor | Estado | Fuente / fecha |
|---|---|---|---|
| Comisión taker VIP 0, sin BNB | 0,10 % por lado | Publicado, **no reverificado hoy** | Tabla Binance consultada 2026-10-16 (`docs/BTCUSDT_Fase_0_borrador.md`); la página oficial no abrió el 2026-10-21 |
| Comisión maker VIP 0, sin BNB | 0,10 % por lado | Publicado, no reverificado hoy | Misma fuente |
| Con BNB (descuento 25 % citado por terceros) | 0,075 % por lado | SUPUESTO no usado | Solo fuentes secundarias; no se usa en la base |
| Spread efectivo (mediana/p90/p99) | **No medido** | **SUPUESTO** 0,02 % por lado (peor caso del marco) | Sin acceso a `/api/v3/bookTicker`/`depth`. Un snapshot actual tampoco representaría años pasados |
| Deslizamiento 1 000 / 10 000 / 100 000 USDT | **No medido** | **SUPUESTO** 0,03 % por lado (todos los tamaños) | Sin libro. Para 100 000 USDT podría ser mayor; no verificable |
| Financiamiento spot 1x | 0 | Por construcción | — |
| Funding perpetuo (referencia, "no aprobable") | **No medido** | Sin dato | fapi bloqueado |
| **Ida y vuelta, base** | **0,30 %** (2 x (0,10 + 0,02 + 0,03)) | Solo la comisión es publicada; 0,10 % de 0,30 % | Igual al provisional del marco v1.0 |
| **Ida y vuelta, x2** | **0,60 %** | Estrés | — |

Conclusión: el 0,30 % del marco **no queda confirmado ni refutado** en spread/deslizamiento; sigue vigente como supuesto. Pendiente: repetir con acceso a Binance (>= 24 muestras en un día).

## 2. Qué falta para cerrar el encargo
Ejecutar desde un entorno con acceso: `curl "https://api.binance.com/api/v3/bookTicker?symbol=BTCUSDT"` (24+ muestras) y `.../depth?symbol=BTCUSDT&limit=1000` para recorrer el libro a 1 000/10 000/100 000 USDT; `https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=90`.

## 3. Umbral de equilibrio (medido, descriptivo, sin señales)

Datos: `data/kt003/btcusdt_1h.csv.gz`, 80 308 velas de 1 h, 2017-08-17 a 2026-10-20. Retorno |log| a h velas (por filas; hay velas de 2018-02 con marca horaria corrida, se redondeó a la hora y se quitaron duplicados; huecos menores no corregidos). Movimiento mínimo para empatar = costo ida y vuelta: **0,30 % (base) / 0,60 % (x2)**.

Mediana de |retorno| (todo el período) y acierto mínimo p = (m + c) / (2m), con ganancia y pérdida media = mediana. **p > 100 % = imposible: el costo supera el movimiento típico.**

| Horizonte | Mediana | p75 | p mín. c=0,30 % | p mín. c=0,60 % |
|---|---|---|---|---|
| 1 h | 0,250 % | 0,523 % | 110 % (imposible) | 170 % (imposible) |
| 4 h | 0,494 % | 1,084 % | 80,4 % | 110,8 % (imposible) |
| 24 h | 1,472 % | 3,106 % | 60,2 % | 70,4 % |

Por año (mediana % / p mínimo c=0,30 % / p mínimo c=0,60 %):

| Año | 1 h | 4 h | 24 h |
|---|---|---|---|
| 2017* | 0,593 / 75,3 / 100,6 | 1,222 / 62,3 / 74,6 | 3,428 / 54,4 / 58,8 |
| 2018 | 0,320 / 96,9 / 143,8 | 0,632 / 73,7 / 97,5 | 2,055 / 57,3 / 64,6 |
| 2019 | 0,235 / 113,8 / 177,6 | 0,442 / 83,9 / 117,9 | 1,371 / 60,9 / 71,9 |
| 2020 | 0,249 / 110,3 / 170,6 | 0,496 / 80,2 / 110,5 | 1,462 / 60,3 / 70,5 |
| 2021 | 0,418 / 85,9 / 121,7 | 0,859 / 67,5 / 84,9 | 2,356 / 56,4 / 62,7 |
| 2022 | 0,261 / 107,5 / 164,9 | 0,505 / 79,7 / 109,4 | 1,511 / 59,9 / 69,9 |
| 2023 | 0,162 / 142,5 / 235,0 | 0,316 / 97,5 / 145,1 | 0,951 / 65,8 / 81,6 |
| 2024 | 0,243 / 111,8 / 173,5 | 0,477 / 81,5 / 112,9 | 1,373 / 60,9 / 71,8 |
| 2025 | 0,200 / 124,9 / 199,9 | 0,399 / 87,6 / 125,2 | 1,127 / 63,3 / 76,6 |
| 2026** | 0,189 / 129,6 / 209,1 | 0,377 / 89,8 / 129,6 | 1,137 / 63,2 / 76,4 |

\* 2017 parcial (desde ago). \*\* 2026 parcial (hasta 20-oct).

Lectura (descriptiva): con el costo base, 1 h es inviable en casi todos los años (solo 2017 y 2021 dan p < 100 %); 4 h exige 74-98 % de acierto salvo 2017/2021; 24 h exige 54-66 % (60 % en el total). Con costo x2, 24 h exige ~70 %. La volatilidad cae con los años (mediana 24 h 3,4 % en 2017 a 1,1 % en 2025-26), así que el umbral reciente es más duro que el promedio. El modelo "ganancia = pérdida = mediana" es una simplificación del encargo, no una estimación de edge.

## 4. Supuestos marcados
1. Comisión 0,10 % por lado: publicada el 2026-10-16, no reverificada hoy.
2. Spread 0,02 % por lado: SUPUESTO.
3. Deslizamiento 0,03 % por lado, igual para los tres tamaños: SUPUESTO (100 000 USDT puede ser peor).
4. Funding perpetuo: sin dato, y no aprobable.
5. Sin impuestos, retiros ni costos de transferencia.

## 5. Reproducir
- Umbral: script en el entorno de la sesión (lee el csv.gz, `pd.to_datetime(..., utc=True, format='mixed')`, `.dt.floor('h')`, `np.log(c.shift(-h)/c).abs()`, mediana y cuantil 0,75 por año, `p=(m+c)/(2m)`), h = 1, 4, 24.
- Intento de acceso: `curl https://api.binance.com/api/v3/bookTicker?symbol=BTCUSDT` -> `CONNECT tunnel failed, response 403` (2026-10-21).
