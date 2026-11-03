# Propuesta para BTCUSDT: FreqAI descriptivo antes de posiciones

2026-11-01, Costa Rica. Autor Codex. Estado: PROPUESTA, no prerregistro
aprobado, no autorización de backtest ni de operación. El propietario pidió
la recomendación para el mercado del proyecto. No existe un horizonte
universalmente óptimo demostrado para BTC.

## Recomendación y razón

BTCUSDT Spot, datos base de una hora, horizonte de cuatro horas, evaluación
descriptiva de un único FreqAI LightGBMRegressor. Sin posiciones, costos
convertidos artificialmente en acierto, capital ni órdenes. Una medición
separada evita modificar KT-002 y permite contrastar horizontes iguales.
Kronos/TimesFM no se agregan al candidato: KT-004 no respaldó Kronos a 4h
en cripto y no se deben mezclar signos, probabilidades y retornos sin
calibración predefinida. El combinador permanece sin promoción.

Primero Fase 0: cobertura real, huecos, frecuencia no solapada, distribución
de clases y sensibilidad de potencia ante distintos niveles de dependencia y discordancia. No es posible medir discordancias reales del candidato sin generar predicciones; cualquier piloto exige autorización y muestra separadas, excluidas de confirmación. No entrenar ni evaluar
predicciones hasta revisar ese diagnóstico. El tamaño final no se elige
para obtener un resultado positivo. No abrir holdouts existentes.

## Candidato de diseño para decisión explícita

- Etiqueta continua del Regressor: retorno open/open BTCUSDT entre base UTC
  00/04/08/12/16/20 y base+4h. Convertir pronóstico a signo con umbral cero.
  Emisión propuesta base-5min: usar únicamente barras con cierre <=base-1h,
  disponibles al emitir. Registrar recepción y emisión antes de la base; una
  predicción tardía es fallo, nunca pronóstico a posteriori del mismo tramo.
- Un modelo, hiperparámetros congelados antes de evaluación; ventana
  propuesta de 365 días y reentrenamiento semanal. Es una elección de
  diseño conservadora, no una optimización demostrada.
- Características propuestas: retornos pasados 1/4/24h, volatilidad pasada
  24h y volumen relativo pasado 24h. Sin datos de la vela objetivo.
- Etiquetas de entrenamiento deben haber vencido estrictamente antes
  del corte; purga de al menos cuatro horas y control de disponibilidad.
- Baseline primario: siempre sube; persistencia como secundario. La
  muestra primaria usa todos los cortes programados con objetivo observable.
  Abstención, pronóstico cero, fallo o emisión tardía cuentan como no acierto
  del candidato, y reducen cobertura. Retorno objetivo exactamente cero: ambos
  predictores direccionales no aciertan. Si falta el precio objetivo, registrar
  dato faltante común, sin imputar y con análisis de sensibilidad explícito;
  no declarar éxito si la cobertura de objetivos cae por debajo de 95 %.
- Umbral propuesto para señal descriptiva: mejora >=2 puntos porcentuales
  frente al baseline y prueba pareada unilateral p<0,05 al cierre fijado;
  sin solape no equivale a independencia. Antes del prerregistro deben
  fijarse longitud de bloques, procedimiento de bootstrap temporal y
  potencia compatible con dependencia serial usando una muestra externa.
  No se eligen esos ajustes después de mirar la muestra confirmatoria;
  cobertura >=95 %. Sin búsquedas de umbral ni revisiones intermedias.
  Fase 0 debe determinar si es medible; si no, NO LISTO.
- La frase falsable propuesta: «FreqAI con estas entradas y parámetros
  fijados supera al baseline siempre sube al predecir el signo del retorno
  BTCUSDT Spot a cuatro horas en observaciones prospectivas sin solape».

Los umbrales son propuestas para elección del dueño. La solicitud de
recomendación no se registra como aceptación. No se decide número de folds
sin frecuencia real; la confirmación financiera posterior exige su propio
prerregistro, >=30 operaciones por fold, censo completo y DSR>=0,95.

## Costos y riesgo de una etapa financiera posterior

Tarifa pública regular Binance consultada: maker/taker 0,100 % por lado,
sin descuento BNB. Presupuesto base aproximado ida/vuelta 0,20 %, al que
se suman spread y slippage medidos; composición exacta y base de cobro se
implementarán en la simulación. No asumir descuento ni traslado de costos
de otro instrumento. Simular estrés de costos duplicados antes de promoción.

No se propone operar por alcanzar 52 % de acierto. Magnitud de ganancias,
pérdidas, costos y exposición determinan la utilidad financiera. Se conserva
íntegro docs/riesgo/MARCO_DE_RIESGO.md: posición <=25 %, bruto <=100 %,
riesgo por operación <=0,5 %, pérdidas diarias/semanales/mensuales y apagado
por drawdown 10 %. No se cambian estos límites mediante una librería.

## Dependencias que no resuelve esta propuesta

Custodia externa previa e independiente y censo histórico de ATLAS no
pueden reconstruirse como evidencia previa creando hashes hoy. Necesitan
fuentes originales y custodio con permisos independientes. La recopilación
prospectiva necesita tiempo real; históricos no se rotulan prospectivos.
Instalación, recuperación, entrega y auditoría global siguen pendientes.

## Fuentes primarias consultadas

- Binance: https://www.binance.com/en/fee/trading
- FreqAI entrenamiento y evaluación temporal:
  https://www.freqtrade.io/en/stable/freqai-running/
- Freqtrade detección de fuga temporal:
  https://docs.freqtrade.io/en/2026.5/lookahead-analysis/

La documentación respalda controles técnicos, no garantiza rentabilidad
ni recomienda estos hiperparámetros. Las decisiones de diseño anteriores
son propuestas de Codex y requieren revisión metodológica independiente.

## Revisión metodológica del borrador

Segundo agente Codex identificó necesidad de separar potencia por sensibilidad
de discordancias observadas, contemplar dependencia serial, y precisar etiqueta,
faltantes y tiempos. Este borrador incorpora esas distinciones; aún NO LISTO
para ejecución: falta estimar la discordancia pareada y la dependencia del candidato, fijar
bloques y potencia, y obtener la decisión explícita y la revisión del
prerregistro final. La cobertura y el diagnóstico de dependencia del
baseline de Fase 0 están en FREQAI_BTC_FASE0_COBERTURA_2026-11-02.md.

## Decisión para un piloto prospectivo separado

Propuesta para el dueño: piloto de 30 días de FreqAI BTCUSDT Spot, seis
cortes diarios de 4 h, usando el reloj de emisión y etiqueta de este
documento. El objetivo del piloto es comprobar disponibilidad y
reproducibilidad, y estimar discordancias para diseñar la confirmación.
El intervalo comienza en el primer corte posterior a la aprobación y
al registro de una versión ejecutable. Se conserva el calendario completo
de 180 cortes y se registra cada fallo, retraso y abstención.

Criterio operativo propuesto: al menos 171 de 180 cortes con emisión válida
y anterior al inicio del objetivo. Cada emisión válida debe poder
reproducirse a partir de sus entradas, imagen y modelo identificados.
Registrar la publicación mediante un recibo verificable independiente
del timestamp declarado por el productor. Antes de iniciar falta acordar
ese mecanismo y congelar los parámetros del modelo.

El piloto se excluye de la muestra confirmatoria. Sus etiquetas se unen
solo una vez vencido el objetivo para estimar discordancias y dependencia.
No fija el tamaño confirmatorio, declara ventaja ni inicia una comparación
con costos. El plazo de 30 días y el criterio de cobertura son propuestas
de Codex para la decisión del dueño.
