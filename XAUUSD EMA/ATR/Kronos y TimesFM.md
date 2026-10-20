---
tipo: referencia
estado: vigente
actualizado: 2026-10-20
tags: [kronos, timesfm, modelos, kt001]
---

# Kronos y TimesFM

Índice: [[00 Inicio]] · Usados en: [[KT-002 — Acierto prospectivo BTC]] · [[KT-003 — Diagnóstico histórico BTC]]

Modelos fundacionales de series de tiempo, usados sin reentrenar ("zero-shot"). Todas las versiones están **fijadas** para que cada resultado sea reproducible.

## Kronos-small
- Modelo de velas (OHLCV) preentrenado en mercados financieros; el artículo declara preentrenamiento hasta junio de 2024.
- Pesos `NeoQuasar/Kronos-small` @ `901c26c1`, tokenizer `NeoQuasar/Kronos-Tokenizer-base` @ `0e011738`, código `shiyu-coder/Kronos` @ `67b630e6`.
- Publicado en Hugging Face el 2025-06-30 (modificado 2025-09-09).
- Configuración: 400 velas de contexto, 4 pasos, 20 trayectorias promediadas, T=1, top_p=0,9, semilla 42.

## TimesFM 2.5 (200M)
- Modelo general de series de tiempo de Google; recibe solo los cierres.
- Pesos `google/timesfm-2.5-200m-pytorch` @ `1d952420`, código `google-research/timesfm` @ `e51928e2` (paquete 3.0.2).
- Publicado el 2025-09-02 (modificado 2025-10-02): es probable que el período 2024–2025 esté en su entrenamiento.
- Configuración: contexto 400, mediana, normalización activada, `force_flip_invariance`.

## KT-001 — combinación 50/50
- Promedio fijo de los retornos previstos a 4 h de los dos modelos, contra el mismo último cierre.
- Prueba técnica superada con datos sintéticos el 2026-10-19 (no mide acierto).

## Lo que se sabe hasta ahora
- En el histórico, Kronos es el que mejor acierta (56,8 % post corte) pero no supera la prueba estricta; TimesFM queda por debajo de «siempre sube». Ver [[KT-003 — Diagnóstico histórico BTC]].
- Kronos y TimesFM coinciden en la dirección solo ~57 % de las veces; por eso el promedio rinde menos que Kronos solo.
- **Regla del proyecto:** ningún modelo se descarta sin decisión del usuario; si uno rinde peor, se estudia cómo ajustarlo ([[Agentes del proyecto#Mejorador]]).

## Entorno
Python 3.13, PyTorch 2.14.1 (CPU), versiones exactas en `docs/evidencia/KT-001/requirements-resolved.txt` y `data/kt003/pip_freeze.txt`.
