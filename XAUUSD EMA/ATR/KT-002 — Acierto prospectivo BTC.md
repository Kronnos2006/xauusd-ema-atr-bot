---
tipo: medicion
id: KT-002
estado: activa
inicio: 2026-10-20
activo: BTCUSDT Spot
temporalidad: 1h
horizonte: 4h
tags: [kt002, btc, kronos, timesfm, prospectivo]
---

# KT-002 — Acierto prospectivo BTC

Índice: [[00 Inicio]] · Modelos: [[Kronos y TimesFM]] · Uso: [[Guía de uso]] · Comparar con: [[KT-003 — Diagnóstico histórico BTC]]

## Qué es
Medición **descriptiva** y **prospectiva**: cada hora, los modelos predicen hacia dónde va BTC en las 4 h siguientes, y la predicción se puntúa cuando vence. Al ser hacia adelante, los modelos no pudieron ver esos datos al entrenarse. No es una estrategia ni mide rentabilidad.

## Cómo funciona
1. Al minuto 7 de cada hora (UTC), toma las últimas 400 velas **cerradas** de BTCUSDT 1h (API pública de Binance).
2. Kronos-small (20 trayectorias), TimesFM 2.5 (mediana) y KT-001 (promedio 50/50) predicen el cierre a 4 h.
3. Guarda una fila en `data/kt002/predicciones.csv` y, al vencer, anota el precio real y si acertó cada modelo.
4. Reescribe `data/kt002/resumen.md` y `resumen.json`.

## Métricas
- Acierto = el signo del retorno previsto coincide con el real. Intervalo Wilson 95 %.
- **Se interpreta solo el subconjunto sin solape** (bases a las 0, 4, 8, 12, 16 y 20 UTC, es decir 6, 10 y 2 a. m./p. m. en Costa Rica).
- Referencia «siempre sube», McNemar exacto contra ella y conteo de horas omitidas (Enmienda A).

## Estado
- Primera predicción: 2026-10-20, base de las 7:00 Costa Rica. Primer resultado: ✗ en los tres modelos (BTC subió 0,82 %). Un solo dato no dice nada.
- Datos útiles: unos 100 resultados sin solape (~17 días) para una idea general; unos 780 (~4 meses) para distinguir 55 % de 50 %.

## Incidentes y cambios operativos
- **El cron horario de GitHub no se disparó** durante casi 3 horas. Desde el 2026-10-20 17:05 UTC cada corrida queda activa ~4 h 45 min y repite el script cada hora; si se para, el [[Automatizaciones#Tareas programadas de Claude\|gerente]] la relanza en su informe diario. El cálculo no cambió.
- Mientras corría KT-003, KT-002 esperó en cola y se perdieron horas, que quedan contadas como omitidas.

## Documentos
- Registro previo y enmiendas: [docs/KT-002_registro_prospectivo.md](https://github.com/Kronnos2006/xauusd-ema-atr-bot/blob/master/docs/KT-002_registro_prospectivo.md)
- Script: `tools/kt002_prospectivo.py` · Workflow: `.github/workflows/kt002.yml`
- Las velas posteriores al 2026-10-20 quedan expuestas para cualquier holdout BTC futuro.
