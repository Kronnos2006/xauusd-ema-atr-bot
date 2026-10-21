---
tipo: diagnostico
id: KT-003
estado: cerrado
fecha: 2026-10-20
activo: BTCUSDT Spot
periodo: 2017-09 a 2026-10
n_bases: 2928
veredicto: no significativo tras Holm
tags: [kt003, btc, kronos, timesfm, historico]
---

# KT-003 — Diagnóstico histórico BTC

Índice: [[00 Inicio]] · Modelos: [[Kronos y TimesFM]] · En vivo: [[KT-002 — Acierto prospectivo BTC]] · Auditor: [[Agentes del proyecto#Desconfiado]]

## Qué es
Diagnóstico del acierto de dirección a 4 h sobre **toda la historia de BTCUSDT en Binance** (2017-08 → 2026-10). Se usa una base por día (00:00 UTC) para que no haya solape. No es un backtest de estrategia: no hay costos ni rentabilidad.

> [!note] No llega a 20 años
> El usuario pidió 20 años; BTCUSDT en Binance solo existe desde agosto de 2017 (unos 9 años).

## Diseño (fijado antes de ver datos)
- Datos: ZIP oficiales de `data.binance.vision` verificados con su CHECKSUM, sellados con SHA-256 `c3ccfb0a…2cc61`. 80 308 velas; se excluyeron 43 velas desalineadas de febrero de 2018 (caída de Binance).
- 2928 bases válidas; 404 saltadas por huecos en las 400 velas previas.
- **Resultado primario: después del corte** (desde 2024-07-01, n=842), con McNemar contra «siempre sube» y corrección de Holm sobre 3 modelos.
- Corte descriptivo desde 2025-10-03 (tras la publicación de TimesFM 2.5).
- El usuario aceptó que esto expone toda la historia BTC: ninguna estrategia BTC futura puede usarla como holdout sellado.

## Resultado

| Período | Kronos | TimesFM | KT-001 | «Siempre sube» |
|---|---|---|---|---|
| Después del corte (n=842) | **56,8 %** | 48,7 % | 55,5 % | 50,9 % |
| Dentro del entrenamiento (n=2086) | 52,7 % | 51,6 % | 52,8 % | 48,7 % |
| Desde 2025-10-03 (n=383) | 55,1 % | 49,4 % | 53,0 % | 51,4 % |

- **Primario: no significativo.** Kronos p = 0,029 sin corregir, **0,086 con Holm** (el límite era 0,05).
- **Sin señal de memorización:** acierta más en lo no visto que en lo visto.
- **Sin señales de fuga** (auditoría independiente: error igual al de un paseo aleatorio, correlaciones normales).
- **Post hoc (no registrado):** el |retorno previsto| medio de KT-001 es 0,19 %, menor que el costo de 0,20 %. Con costos, el retorno neto es negativo.

**Conclusión:** ningún modelo le gana de forma confiable a «siempre sube»; Kronos se acerca. Aunque acertara, con estos movimientos no se gana dinero a 4 h.

## Incidentes
- El primer intento del run se **canceló por error** (la página decía "En cola" con 14 tareas a punto de terminar). Nadie miró resultados parciales; el muestreo es determinista. Documentado como Nota E en el registro.
- Las dos primeras pruebas fallaron por una lectura de fechas (formato ISO con microsegundos) y por logs ignorados por `.gitignore`. Corregido antes de cualquier pronóstico.

## Documentos
- Registro previo con enmiendas A–E: [docs/KT-003_registro_historico.md](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/master/docs/KT-003_registro_historico.md)
- Resultados: `data/kt003/resumen.md`, `predicciones.csv`, `manifiesto_datos.json`, `reproducibilidad.json`
- Script: `tools/kt003_historico.py` · Workflow: `.github/workflows/kt003.yml`

## Qué sigue
Las propuestas KT-004 (confirmar Kronos con datos nuevos) y KT-005 (ajuste de TimesFM) salen de acá; ver `docs/propuestas/`.
