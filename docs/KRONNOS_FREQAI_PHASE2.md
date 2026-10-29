# Kronnos — piloto FreqAI aislado
Origen oficial: https://github.com/freqtrade/freqtrade y https://docs.freqtrade.io/en/stable/freqai/
El puente tools/kronnos_freqai_bridge.py convierte CSV OHLCV generado por el recolector Binance del PR #61 a una tabla de entrada para investigaciones con FreqAI, sin copiar Freqtrade ni abrir trading.
Verifica monotonía temporal, velas cerradas y valores finitos. No genera etiquetas futuras, inferencias, entradas ni rentabilidad.
El workflow prueba el contrato con unittest y por separado intenta importar el runtime real de FreqAI desde su imagen oficial, sin red dentro del contenedor. El smoke test no es entrenamiento; una imagen sin digest fijado tampoco garantiza reproducibilidad de versiones.
Pendiente para aceptar integración funcional: fijar imagen/digest, descargar barras autorizadas de forma reproducible, definir e implementar estrategia experimental FreqAI, ejecutar entrenamiento + backtest walk-forward con costos y datos segregados, comparar KT-002 sin tocar su custodia.
ATLAS continúa como barrera de promoción, no como bloqueo de investigación. Sin trading real.
