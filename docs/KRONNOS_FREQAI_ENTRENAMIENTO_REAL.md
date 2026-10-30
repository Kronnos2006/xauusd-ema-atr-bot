# Kronnos - entrenamiento aislado en entorno real FreqAI
Se importa realmente `freqtrade.freqai.prediction_models.LightGBMRegressor` desde imagen oficial FreqAI y se entrena `lightgbm.LGBMRegressor` con datos **sintéticos deterministas**; 120 filas iniciales entrenamiento, 40 de validación temporal. Produce pronósticos y compara MAE con media histórica.
Es entrenamiento real de LightGBM **dentro del entorno FreqAI**, NO ejecución de la tubería completa FreqAI, NO datos de mercado, NO evaluación de estrategias ni de KT-002 y NO evidencia de ventaja predictiva. Imagen aún sin digest fijado; bloquear promoción.
Siguiente dependencia: datos OHLCV con procedencia verificable, entrenamiento real de pipeline FreqAI, exportar predicciones auténticas con horas UTC y trazabilidad para ensemble.
