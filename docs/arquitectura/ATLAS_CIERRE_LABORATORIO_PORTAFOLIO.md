# ATLAS — Entrega integrada de laboratorio y portafolio

Estado: piloto de software, **no** investigación confirmatoria ni trading.

## Entregas concretas

- `atlas/laboratorio.py`: ejecución simulada intrabar con posiciones -1/0/+1, costos y benchmark.
- `atlas/validacion_temporal.py`: ventanas de entrenamiento, embargo y prueba con señales prefijadas; **no** entrena estrategias.
- `atlas/puente_mercado.py`: lectura local y solo lectura de BTC 4h/1d archivado con SHA-256 y filtro de cierre; no asegura hora histórica de recepción.
- `atlas/cartera_integrada.py`: traduce historiales del simulador en rendimientos sincronizados y los envía al portafolio. Rechaza ausencias, duplicados y capitales inválidos.
- `atlas/portafolio.py`: capital compuesto, drawdown, alertas de peso y correlación.
- Escenarios de estrés aditivos por estrategia; límites aplicados al caso base y a cada estrés.
- Pruebas de extremo a extremo y checks automáticos que preservan KT-002.

## Puertas científicas todavía abiertas

1. La marca booleana `sello_externo_verificado` **no es una firma criptográfica**. Falta verificador independiente de publicación remota anterior al resultado.
2. Datos archivados no establecen por sí mismos cuándo estaban disponibles. Los experimentos retrospectivos no se etiquetan como prospectivos.
3. No existe entrenamiento de modelos por fold, selección automática de estrategias ni comparación confirmatoria contra holdout sellado.
4. Costos intrabar y shocks constantes no modelan financiación, slippage variable, correlaciones cambiantes ni ejecuciones reales.
5. Estos módulos no autorizan ni producen órdenes. Ninguna señal ni estrategia está aprobada para operar con capital.

## Criterio de cierre de este bloque

El bloque de *infraestructura de laboratorio/portafolio* se considerará completo cuando la prueba de extremo a extremo, las pruebas adversas y el CI estén verdes, sin alterar KT-002. El criterio **no** equivale a cerrar las fases de investigación científica ni a demostrar rentabilidad.

Autoría: ChatGPT (OpenAI). Revisión externa pendiente.
