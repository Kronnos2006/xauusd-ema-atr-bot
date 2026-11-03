# Auditoría de la corrida histórica FreqAI del 2 de noviembre

Se consultaron los metadatos, pasos y logs de la corrida 41511415903 y el código de kronnos_freqai_native_fit.py. La corrida programada terminó correctamente y publicó el artefacto 13171919731 con el informe JSON y el manifiesto de Binance. El workflow publica esos dos archivos. La lista de salida no incluye los pesos del modelo ni la serie de predicciones individuales.

- Corrida: https://github.com/Kronnos2006/xauusd-ema-atr-bot/actions/runs/41511415903
- Archivo BTCUSDT Spot 1 h: octubre de 2026, 744 velas. SHA-256 del ZIP da174c1563c8436f1700be3587800376f6edadfa12e28a142ac8a5dc53f2d1a3.
- Digest de imagen Docker consignado en el log: sha256:fd6ec506e2ef5ca9a7e32e00c239b8d722d7e9c0343cb23c0bba8f7ef1175183. El workflow solicita stable_freqai. Para repetir esa versión de imagen se puede resolver el digest registrado.
- Entrenamiento e inferencia nativos de LightGBMRegressor confirmados por el informe y el paso exitoso. La etiqueta del código es retorno entre cierres consecutivos de una hora. La propuesta prospectiva del PR #98 usa aperturas separadas por cuatro horas.

## Discrepancia de recuento

Para 744 velas, range(5, len(rows)-1) construye 738 ejemplos. split=int(738*0.7) vale 516. El código entrena con X.iloc[:split-1] y omite el índice 515 por purga. El ajuste recibe 515 filas. Las 222 filas de prueba empiezan en el índice 516. El JSON usa n_train=split y por eso muestra 516. En una revisión de ese informe conviene reportar por separado filas ajustadas, purgadas y evaluadas.

El informe exploratorio registró 113 aciertos del modelo frente a 106 del baseline en 222 observaciones. Esos totales no identifican qué aciertos son compartidos. Los casos discordantes pueden ir de 7 a 219 con esos mismos totales, de modo que la inferencia pareada y su dependencia temporal requieren conservar los resultados individuales. La ejecución histórica aporta evidencia de funcionamiento del estimador. La emisión prospectiva a cuatro horas, el protocolo aprobado y la evaluación de costos siguen pendientes.

Para el productor prospectivo, registrar por corte las marcas de disponibilidad, emisión y objetivo, más el hash de entradas, la versión de la imagen y el identificador del modelo. Guardar también los fallos y abstenciones para conservar el denominador de cobertura.
