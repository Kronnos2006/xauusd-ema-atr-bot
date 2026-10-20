# KT-003: diagnóstico histórico de acierto direccional (BTCUSDT 1h, 2017–2026)

2026-10-20, Costa Rica. Autor Claude; auditor: agente `desconfiado`; revisor Codex pendiente.
Registro escrito antes de descargar datos o correr modelos.

## Decisión del usuario

El usuario pidió un backtest de al menos 20 años. Se le explicó que BTCUSDT en Binance solo existe desde agosto de 2017 (unos 9 años) y que Kronos declara preentrenamiento hasta junio de 2024. Eligió igualmente Kronos/TimesFM en BTC, entendido como diagnóstico.

## Qué es y qué no es

- Es un **diagnóstico** de acierto de dirección con datos históricos, no un backtest de estrategia ni una prueba de rentabilidad. No hay órdenes, costos ni capital.
- **No cumple los 20 años** pedidos: cubre 2017-08 → 2026-10.
- **La parte anterior a 2024-07-01 está contaminada**: Kronos pudo haber visto esos precios al entrenarse. Ahí el acierto no mide predicción. La procedencia del entrenamiento de TimesFM 2.5 no está auditada; se asume que también puede estar contaminado.
- Solo el período **post corte** (desde 2024-07-01) se acerca a una medición fuera de muestra, y aun así no está certificado.
- No completa la Fase 0 de BTC, no modifica el N canónico y no abre reservas de otros proyectos. Las velas desde 2024-07-01 quedan expuestas para cualquier holdout BTC futuro.

## Configuración fija

- Datos: ZIP mensuales oficiales de `data.binance.vision` (BTCUSDT 1h) con verificación SHA-256 contra su CHECKSUM; el mes en curso, y el último mes si aún no está publicado, por la API pública. Se registran huecos, duplicados y velas OHLC inválidas en `data/kt003/manifiesto_datos.json`. No se rellenan huecos.
- Bases: **una por día**, la vela que abre a las 00:00 UTC, para que las ventanas de 4 h no se solapen. Se salta la base si las 400 velas previas no son contiguas o si falta la vela objetivo; se informa cuántas.
- Modelos, revisiones y parámetros idénticos a KT-002 (Kronos-small 20 trayectorias, T=1, top_p=0.9; TimesFM 2.5 mediana; KT-001 50/50). Diferencia operativa declarada: Kronos se corre en lotes de 8 (`predict_batch`, semilla 42 por lote), así que el muestreo no coincide bit a bit con una llamada individual.
- Métrica: igual a KT-002 (dirección del retorno a 4 h, intervalo Wilson 95 %, referencia «siempre sube»).

## Interpretación pre-declarada

- El resultado principal es **post corte** (n esperado ≈ 840). Con n≈840 el intervalo es aprox. ±3,4 puntos.
- Si el acierto **dentro del entrenamiento** es claramente mayor que el post corte, se interpreta como memorización, no como capacidad predictiva.
- Acertar la dirección más que «siempre sube» no implica ganancia tras costos (0,20 %+ ida y vuelta).
- No se ajustan modelos, horizonte, hora base ni semilla según lo observado. Cualquier variante nueva se registra aparte y suma al conteo de intentos.

## Archivos

- Código: `tools/kt003_historico.py`. Workflow: `.github/workflows/kt003.yml` (GitHub Actions, 16 tareas en paralelo).
- Resultados: `data/kt003/predicciones.csv`, `resumen.md`, `resumen.json`, `manifiesto_datos.json`.

## Enmienda A (2026-10-20, antes de ejecutar)

Pedida por el auditor `desconfiado`.

- **Lanzamiento**: el workflow ya no corre al fusionar código; solo al crear `data/kt003/lanzar.txt` o a mano desde Actions.
- **Prueba pareada**: McNemar exacto de cada modelo contra «siempre sube» sobre las mismas bases, por período y en total.
- **Dependencia**: las bases son diarias y no se solapan, pero días seguidos comparten régimen de mercado; las p se leen como descriptivas, no como prueba de edge.
- **Reproducibilidad**: el shard 0 repite su primer lote con la misma semilla y guarda `data/kt003/reproducibilidad.json`.
- **Conteo de intentos**: misma configuración que KT-001/KT-002; no es una variante nueva ni un intento financiero.
