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

## Enmienda B (2026-10-20, antes de ejecutar)

Pedida por el auditor `desconfiado` en su segunda revisión del diseño.

- **Exposición total aceptada por el usuario** (2026-10-20, por respuesta explícita): KT-003 expone toda la historia BTCUSDT 2017–2026, no solo desde 2024-07-01. Ninguna estrategia BTC futura podrá usar ese período como holdout sellado; solo datos posteriores a hoy. Esto corrige el apartado "Exposición" del borrador de Fase 0 BTC.
- **Resultado primario**: período post corte. Las tres pruebas McNemar (Kronos, TimesFM, KT-001 contra «siempre sube») se corrigen con **Holm** dentro de ese período; los cortes por año y el período dentro del entrenamiento son descriptivos, sin inferencia.
- **Potencia**: con n≈840, MDE ≈ 4,8 puntos (80 %, bilateral, α 0,05), ≈ 5,6 con corrección para 3 modelos. Efectos menores no se pueden distinguir del azar.
- **Integridad de datos**: el manifiesto guarda SHA-256 del CSV final (comprimido y contenido) y del tramo bajado por API; el CSV se versiona en `data/kt003/`. Las bases cuyo contexto tenga una vela OHLC inválida se saltan y se cuentan; las velas de volumen 0 se cuentan pero no se excluyen.
- **Referencia adicional**: «persistencia» (repetir el signo de las 4 h previas a la base), además de «siempre sube».
- **Workflow**: solo corre desde `master`; `unir` exige que el conjunto de bases pronosticadas sea igual al esperado y falla si falta `reproducibilidad.json`.
- **Corrida de prueba previa**: con `lanzar.txt = prueba` se descargan y sellan los datos, se cuentan bases y saltos, se compara `predict` contra `predict_batch` con la misma semilla, se miden tiempos por lote y se registran las fechas de los checkpoints en Hugging Face. No se pronostica el diagnóstico. El modo `completo` solo se lanza después de que el auditor revise esa salida.
- Precisión de redacción: el contexto son 400 velas que terminan en la vela base (399 previas + la base).

## Enmienda C (2026-10-20, tras la corrida de prueba y antes de cualquier pronóstico)

- **Datos**: 80 308 velas, 0 duplicados, 0 velas OHLC inválidas. Hay 43 velas de febrero de 2018 desalineadas de la hora (apertura en :28:14, caída de Binance); se excluyen y se cuentan. Con eso quedan 28 huecos y 2928 bases válidas (404 saltadas por huecos en su contexto); post corte: 842, sin saltos.
- **Fechas de los checkpoints en Hugging Face** (registradas por la prueba): Kronos-small creado 2025-06-30 y modificado 2025-09-09; TimesFM 2.5 creado 2025-09-02. Que los pesos se publiquen después de junio de 2024 no prueba que se hayan entrenado con datos posteriores, pero **no se puede certificar que el período post corte esté fuera del entrenamiento**, sobre todo para TimesFM. El resultado post corte se lee como "probablemente menos contaminado", no como fuera de muestra.

## Enmienda D (2026-10-20, antes de cualquier pronóstico del diagnóstico)

Pedida por el auditor `desconfiado` tras revisar la corrida de prueba.

- **Datos sellados**: el modo completo usa `data/kt003/btcusdt_1h.csv.gz` del repo (SHA-256 `c3ccfb0a077574b9aa9611e0589c01ed1f679adb9caa38889ffd7f1b36f2cc61`, el de la prueba) y aborta si el hash no coincide. No vuelve a descargar. Resultado esperado: 2928 bases, 842 post corte.
- **Corte descriptivo adicional, declarado ahora**: desde 2025-10-03 (día siguiente a la última modificación de TimesFM 2.5 en Hugging Face). n ≈ 383, MDE ≈ 7,2 puntos (≈ 8,3 con Holm). Solo descriptivo, sin inferencia: su potencia es baja. No se agregará ningún otro corte después de ver resultados.
- **Fechas de checkpoints**: Kronos-Tokenizer-base creado 2025-06-30, modificado 2025-09-09 (además de las de la Enmienda C).
- **Velas recortadas**: hay 11 velas que cierran antes de completar la hora (caídas de Binance). Ninguna es base, objetivo ni referencia de persistencia de una base válida; el resumen igual las cuenta (`velas_recortadas_en_bases`). Se corrige la observación del auditor sobre 2021-04-25: ese día no es base porque su contexto incluye el hueco del 2021-04-20.
- **Versiones**: el shard 0 guarda `pip freeze` en `data/kt003/pip_freeze.txt`.
- **Exposición declarada**: al probar la unión de resultados sobre los datos reales con pronósticos aleatorios (sin modelos), el autor vio las tasas de las referencias triviales («siempre sube» y «persistencia») por período y año. No son hipótesis ni cambian ninguna regla de esta prueba; se deja constancia.
