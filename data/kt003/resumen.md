# KT-003 — diagnóstico histórico de acierto (BTCUSDT 1h, 4h, una base diaria)

Diagnóstico, no backtest de estrategia: sin costos ni rentabilidad.
"Dentro del entrenamiento" no mide predicción: Kronos ya vio esos datos.

## Después del corte (desde 2024-07-01) — n=842

- Kronos: 478/842 = 56.8 % (IC95 53.4–60.1)
- TimesFM: 410/842 = 48.7 % (IC95 45.3–52.1)
- KT-001 50/50: 467/842 = 55.5 % (IC95 52.1–58.8)
- Referencia «siempre sube»: 429/842 = 50.9 % (IC95 47.6–54.3)
- Referencia «persistencia» (repite las 4 h previas): 408/842 = 48.5 % (IC95 45.1–51.8)
- McNemar vs «siempre sube» (p / p Holm): kronos 0.0285 / 0.0855, timesfm 0.3699 / 0.3699, kt001 0.0864 / 0.1728

## Dentro del entrenamiento (hasta 2024-06-30) — n=2086

- Kronos: 1099/2085 = 52.7 % (IC95 50.6–54.9)
- TimesFM: 1075/2085 = 51.6 % (IC95 49.4–53.7)
- KT-001 50/50: 1100/2085 = 52.8 % (IC95 50.6–54.9)
- Referencia «siempre sube»: 1015/2085 = 48.7 % (IC95 46.5–50.8)
- Referencia «persistencia» (repite las 4 h previas): 912/2085 = 43.7 % (IC95 41.6–45.9)
- McNemar vs «siempre sube» (p / p Holm): kronos 0.0189 / 0.0492, timesfm 0.0673 / 0.0673, kt001 0.0164 / 0.0492

## Descriptivo: desde 2025-10-03 (tras publicar TimesFM 2.5; potencia baja) — n=383

- Kronos: 211/383 = 55.1 % (IC95 50.1–60.0)
- TimesFM: 189/383 = 49.4 % (IC95 44.4–54.3)
- KT-001 50/50: 203/383 = 53.0 % (IC95 48.0–58.0)
- Referencia «siempre sube»: 197/383 = 51.4 % (IC95 46.4–56.4)
- Referencia «persistencia» (repite las 4 h previas): 191/383 = 49.9 % (IC95 44.9–54.9)
- McNemar vs «siempre sube» (p / p Holm): kronos 0.358 / 1.0, timesfm 0.602 / 1.0, kt001 0.7169 / 1.0

## Total — n=2928

- Kronos: 1577/2927 = 53.9 % (IC95 52.1–55.7)
- TimesFM: 1485/2927 = 50.7 % (IC95 48.9–52.5)
- KT-001 50/50: 1567/2927 = 53.5 % (IC95 51.7–55.3)
- Referencia «siempre sube»: 1444/2927 = 49.3 % (IC95 47.5–51.1)
- Referencia «persistencia» (repite las 4 h previas): 1320/2927 = 45.1 % (IC95 43.3–46.9)
- McNemar vs «siempre sube» (p / p Holm): kronos 0.0015 / 0.0045, timesfm 0.2923 / 0.2923, kt001 0.003 / 0.006

## Por año (KT-001 / siempre sube)

- 2017: 58/103 = 56.3 % (IC95 46.7–65.5) / 57/103 = 55.3 % (IC95 45.7–64.6)
- 2018: 143/270 = 53.0 % (IC95 47.0–58.8) / 123/270 = 45.6 % (IC95 39.7–51.5)
- 2019: 149/283 = 52.6 % (IC95 46.8–58.4) / 139/283 = 49.1 % (IC95 43.3–54.9)
- 2020: 137/266 = 51.5 % (IC95 45.5–57.5) / 122/266 = 45.9 % (IC95 40.0–51.9)
- 2021: 147/268 = 54.9 % (IC95 48.9–60.7) / 132/268 = 49.2 % (IC95 43.3–55.2)
- 2022: 185/365 = 50.7 % (IC95 45.6–55.8) / 180/365 = 49.3 % (IC95 44.2–54.4)
- 2023: 189/348 = 54.3 % (IC95 49.1–59.5) / 168/348 = 48.3 % (IC95 43.1–53.5)
- 2024: 190/366 = 51.9 % (IC95 46.8–57.0) / 188/366 = 51.4 % (IC95 46.3–56.5)
- 2025: 215/365 = 58.9 % (IC95 53.8–63.8) / 190/365 = 52.0 % (IC95 46.9–57.1)
- 2026: 154/293 = 52.6 % (IC95 46.9–58.2) / 145/293 = 49.5 % (IC95 43.8–55.2)
