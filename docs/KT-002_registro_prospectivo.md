# KT-002: muestra prospectiva de acierto direccional (BTCUSDT 1h)

2026-10-20, Costa Rica. Autor Claude; revisor Codex pendiente.
Registro escrito antes de recolectar cualquier dato de mercado para esta prueba.

## Decisión del usuario

El usuario pide, el 2026-10-20, que los modelos tomen datos reales y se mida su acierto sin depender de que su PC esté encendida. Elige explícitamente:

- prueba **prospectiva** (no histórica);
- evaluar **Kronos solo, TimesFM solo y KT-001 (50/50) por separado**.

## Qué es y qué no es

Es una medición **descriptiva** del acierto de dirección de pronósticos hechos antes de conocer el resultado. No es un backtest, ni una estrategia, ni una prueba de rentabilidad. No hay órdenes, MT5, capital ni costos. No completa la Fase 0 de BTC ni modifica el N canónico de resultados financieros. No abre reservas ni holdouts de otros proyectos.

Al ser prospectiva, el resultado queda fuera del período de preentrenamiento declarado por Kronos (hasta junio de 2024) y del de TimesFM, sin necesidad de auditar su procedencia.

## Configuración fija (no se cambia tras ver resultados)

- Datos: BTCUSDT Spot, velas de 1 h, endpoint público `data-api.binance.vision/api/v3/klines`. Solo velas cerradas.
- Ejecución: GitHub Actions, cada hora (minuto 7 UTC aprox.; GitHub puede retrasar u omitir corridas). Cada corrida pronostica una vez desde la última vela cerrada.
- Contexto: 400 velas cerradas. Horizonte: 4 velas.
- Kronos-small `901c26c1…`, tokenizer base `0e011738…`, 20 trayectorias, T=1, top_p=0.9, semilla 42. Código Kronos `67b630e6…`.
- TimesFM 2.5 200M `1d952420…`, mediana, solo cierres, código `e51928e2…`. Misma configuración de `ForecastConfig` que KT-001.
- KT-001: 0.5·(K/último−1) + 0.5·(T/último−1).

## Métrica

Base B = vela de apertura B, cerrada en B+1h, con cierre C₀. Objetivo = cierre de la vela que abre en B+4h (4 horas después de C₀).

- Retorno previsto r̂ = cierre previsto de la 4.ª vela / C₀ − 1. Retorno real r = cierre real objetivo / C₀ − 1.
- Acierto si sign(r̂) = sign(r). Si r = 0 o r̂ = 0, no se cuenta.
- Se informa por modelo: n, aciertos, tasa e intervalo Wilson 95 %.
- Referencia: tasa de un pronóstico "siempre sube" sobre las mismas observaciones.
- Las ventanas horarias se solapan (cada una comparte 3 de 4 horas con la siguiente), así que no son independientes. Se informa también el subconjunto sin solape (bases con hora UTC múltiplo de 4), que es el que se interpreta.

## Interpretación pre-declarada

- Sin regla de aprobación económica: esto no puede promover ninguna estrategia.
- Para decir algo sobre el acierto se usa solo el subconjunto sin solape. Con n pequeño el intervalo Wilson será ancho. A modo orientativo, con n≈100 no solapadas el intervalo es aprox. ±10 puntos, y distinguir 55 % de 50 % con potencia 80 % requiere del orden de 780 observaciones independientes (≈130 días).
- No se cambian modelos, umbrales, horizonte ni semilla según lo observado. Cualquier variante nueva se registra aparte.
- Superar a "siempre sube" en dirección no implica ganancia neta tras costos (0,20 %+ ida y vuelta según el borrador de Fase 0).

## Exposición de datos

Las velas posteriores al 2026-10-20 quedan vistas por esta prueba. Si más adelante se define un holdout BTC para una estrategia con estos modelos, debe declararse esta exposición.

## Archivos

- Código: `tools/kt002_prospectivo.py`. Workflow: `.github/workflows/kt002.yml`.
- Datos: `data/kt002/predicciones.csv` (una fila por pronóstico, se completa al vencer). Resumen: `data/kt002/resumen.md` y `resumen.json`.
- Para detenerla: desactivar el workflow en GitHub (Actions → KT-002 → Disable).

## Enmienda A (2026-10-20 14:30 UTC, antes del primer dato)

Pedida por el auditor `desconfiado`. Se agrega cuando todavía hay 0 pronósticos, así que no está influida por resultados.

- **Prueba pareada**: cada modelo se compara con «siempre sube» sobre las mismas filas con McNemar exacto (binomial bilateral sobre los casos donde solo uno de los dos acierta). Se informa p; con α = 0,05 bilateral, sin corrección para los tres modelos, que se leen como descriptivos.
- **Dependencia**: la lectura principal sigue siendo el subconjunto sin solape (una base cada 4 h). Aun ahí puede haber autocorrelación de régimen; por eso ninguna p se interpreta como prueba de edge, solo como señal para registrar un estudio confirmatorio aparte.
- **Horas omitidas**: el resumen cuenta las horas sin pronóstico entre el primero y el último (corridas que GitHub no hizo o que fallaron). No se rellenan después.
- **Reproducibilidad**: en la primera corrida se pronostica dos veces la misma base y se guarda `data/kt002/reproducibilidad.json`.
- **Conteo de intentos**: KT-001 (técnica, sintética), KT-002 (prospectiva) y KT-003 (diagnóstico histórico) usan la misma configuración; no son variantes de modelo distintas. Ninguna es un intento financiero ni cambia el N canónico.
- **Arranque**: el cron horario no se ejecutó (0 corridas al 14:30 UTC). Se agrega un disparo por push sobre el propio script/workflow para la primera corrida.
