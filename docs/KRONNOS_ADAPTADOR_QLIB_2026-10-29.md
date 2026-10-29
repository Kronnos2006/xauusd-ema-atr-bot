# Kronnos: puente de contratos a Qlib, fase 1
Adaptador original read-only sin importar ni instalar Microsoft Qlib. Convierte predicciones de Kronos, TimesFM, KT-001 y Siempre sube a columnas `datetime,instrument,score` más lineage; formato CSV preparatorio para posteriores ingestas de Qlib, **no es ejecución de Qlib**.

Entrada JSON: `{"predictions":[{"model":"TimesFM","instrument":"BTCUSDT","prediction_id":"p1","created_utc":"2026-10-28T00:00:00Z","target_utc":"2026-10-28T01:00:00Z","artifact_sha256":"<64 hex>","prediction":0.4}]}`.
Comando: `python3 tools/adapter_qlib_kronnos.py --input predicciones.json --output artifacts/kronnos-qlib-contract.csv`.

Limita puntuaciones entre -1 y 1 (esquema provisional, no asumir salida nativa de motores); timestamp debe ser anterior al objetivo; protege duplicados. El SHA es declarativo y no autentica la predicción. NO realiza backtest, Qlib ni inferencia; no cambia ni promociona hipótesis ATLAS. Siguiente fase: instalar Qlib aisladamente, ejecutar pipeline con datos de prueba y evaluar requisitos de formato y licencia.
