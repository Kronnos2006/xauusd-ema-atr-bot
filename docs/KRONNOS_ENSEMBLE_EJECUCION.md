# Kronnos: combinación experimental de predicciones
Objetivo: combinar señales **ya generadas** de Kronos, TimesFM, KT-001 y Siempre sube en el mismo instrumento y hora objetivo, promediando puntuaciones con pesos iguales y fijados antes de evaluar resultados.

Interfaz: `python3 tools/kronnos_ensemble.py --input predicciones.json --out artifacts/ensemble-kronnos.json`.
Formato JSON `{"predictions":[{"model":"Kronos","prediction_id":"p1","instrument":"BTCUSDT","created_utc":"2026-10-28T00:00:00Z","target_utc":"2026-10-28T01:00:00Z","artifact_sha256":"<64 hex>","prediction":0.5}]}`.

**Advertencias**: valores [-1,+1] son contratos provisionales y NO la salida automática de los motores; cada modelo requiere normalización calibrada sin mirar el holdout. Validación de estructura y SHA declarativo no equivale a ejecución ni custodia externa. Solo emite ensemble para grupos con >=2 modelos; faltar predicciones puede introducir sesgo de selección. No optimiza pesos retrospectivamente, no evalúa aciertos, no promociona ATLAS, no opera. Para medir ventaja se requieren datos prospectivos comparables y baselines previamente definidos, incluidos costes y control por ensayos múltiples.
