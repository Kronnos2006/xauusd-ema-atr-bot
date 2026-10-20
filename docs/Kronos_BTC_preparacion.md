# Kronos / BTCUSDT Spot: preparacion

Fecha: 2026-10-19, Costa Rica. Autor: Codex. Revisor independiente: pendiente.

El usuario autoriza preparar una evaluacion de estrategia BTCUSDT Spot en simulacion. No hay hipotesis registrada ni backtest autorizado por el gate hasta completar las definiciones requeridas. Sin ordenes ni capital real.

## Evidencia tecnica

Repositorio: https://github.com/shiyu-coder/Kronos
Revision descargada: 67b630e67f6a18c9e9be918d9b4337c960db1e9a.
Codigo local en tools/kronos-upstream, entorno aislado en tools/kronos-env.
tools/kronos_smoke.py carga Kronos-small y su tokenizer base en CPU y pide cuatro velas a partir de 64 velas sinteticas. El intervalo sintetico de cinco minutos es un dato tecnico de la demostracion, no una temporalidad aprobada para BTC. No mide acierto, retorno ni potencia.
Dependencias de inferencia adaptadas a Python 3.13: el requirements original fija pandas 2.2.2 y matplotlib 3.9.3; no se instala el entorno completo original ni se presume equivalencia. Versiones efectivas y compatibilidad pendientes de ejecucion.

## Pendientes antes de datos de mercado y backtest

1. Auditar fechas, activos y cobertura de entrenamiento del checkpoint. Un corte posterior del dataset local no elimina exposicion del preentrenamiento. No certificar OOS historico sin evidencia; considerar evaluacion prospectiva si no puede establecerse.
2. Fijar periodos de desarrollo/reserva y comprobar exposicion previa antes de descargar o explorar precios; seguir docs/BTCUSDT_Fase_0_borrador.md. No abrir reservas de otros proyectos.
3. Recibir del usuario una condicion medible de entrada, direccion esperada y horizonte; salida y riesgo; regla numerica de aprobacion/rechazo; presupuesto de variantes y declaracion de grillas previas o ausencia de ellas. Son decisiones pendientes, no propuestas aceptadas.
4. Con la señal definida, Fase 0 con frecuencia real y potencia/MDE apropiados; no trasladar efectos macro R a BTC ni contar velas solapadas como episodios independientes. El numero de folds se deriva con piso de 30 trades TEST por fold.
5. Auditar comisiones de ambos lados, spread/slippage y ejecucion; no tratar OHLCV como cotizaciones bid/ask. Registrar configuracion del modelo, checkpoint, semilla y parametros de muestreo antes de evaluar; fijar revisiones de pesos y conservar hashes.
6. Conciliar registro canonico N y contar variantes realmente probadas. Una prueba sintetica sin criterio de seleccion financiero no constituye un intento de rentabilidad. No modificar N hasta formalizar el experimento.
7. Solo despues del gate: TRAIN selecciona y TEST confirma; t con/sin fold dominante y DSR >= 0.95. No usar la grafica de pronostico como prueba de ventaja economica.

Resultado tecnico: PASS_TECHNICAL_ONLY. Inferencia CPU completada, 64 filas sinteticas a 4 filas futuras con seis columnas finitas; 14.87 segundos incluyendo carga/descarga inicial. PyTorch 2.14.1+cpu, pandas 3.0.6, numpy 2.5.4. Reporte en tools/kronos-output/smoke_report.json, salida en synthetic_prediction.csv. Esto no mide rentabilidad ni acierto predictivo en mercado.

Estado: preparacion; NO LISTO para backtest. No datos financieros descargados por esta tarea.

## Propuesta solicitada por el usuario (pendiente de eleccion)

El usuario pide que Codex recomiende las definiciones. Esto permite formular una propuesta, no registrarla como aceptada.

- BTCUSDT Spot, solo compras, velas de 1 hora y salida temporal a las 4 horas. Cambio propuesto frente a la preferencia anterior de minutos: menos rotacion; no se afirma viabilidad de costos hasta auditarla.
- Kronos-small sin fine-tuning; 400 velas de contexto, cuatro futuras, 20 trayectorias promediadas; T=1, top_p=0.9, semilla 42. Configuracion unica, sin grilla ni busqueda por beneficio. Versiones inmutables antes de evaluar.
- Al cierre de cada hora, si no hay posicion, comprar cuando el cierre pronosticado a cuatro horas supere al cierre observado en al menos 0.60 %. Ejecutar en la siguiente apertura disponible con costos; nunca al precio conocido del cierre previo. Hipotesis propuesta: este filtro anticipa retornos positivos netos a cuatro horas.
- Una posicion a la vez. Vender al cumplir cuatro horas desde entrada o al tocar un stop de 1 % desde el precio de ejecucion. Sin take-profit. Nocional maximo 25 % del patrimonio simulado: perdida nominal al stop ~0.25 % del patrimonio antes de costos, gaps y slippage; no es un limite garantizado. Sin margen ni ventas en corto.
- Costo provisional de simulacion: 0.30 % de ida/vuelta, distribuido en ambos lados (supuesto, no medicion de tarifas ni ejecucion). Escenario adverso 0.50 % sin volver a ajustar la señal. Auditoria de costos previa obligatoria; si no se sostiene el supuesto, volver al usuario antes de registrar cambios. El umbral 0.60 % no deriva de precios observados.
- Corte propuesto: Sharpe anualizado neto > 0.5 sobre retornos diarios de patrimonio, drawdown maximo < 15 %, t positivo con p bilateral < 0.05 con y sin fold dominante, DSR >= 0.95, y retorno acumulado neto positivo bajo costo adverso. Todo en TEST concatenado y sin posiciones solapadas entre particiones; Sharpe incluye dias sin exposicion. Analisis de dependencia y potencia antes de decidir factibilidad. Descartar si falla Fase 0.
- Un unico intento; no probar mini/base, horizontes o umbrales alternativos si falla. Declaracion de intentos previos del usuario pendiente. Folds y cortes cronologicos pendientes de frecuencia real y auditoria de entrenamiento; no inventar un numero fijo.

Esta propuesta no completa Fase 0 ni autoriza ejecutar el backtest. Revision independiente pendiente.

## Aceptacion y diagnostico previo (2026-10-19)

El usuario acepta las reglas propuestas para analisis inicial de viabilidad mediante «si}}». Se conservan los parametros anteriores; no se cambian umbrales tras la aceptacion. Esto reemplaza el estado pendiente de eleccion de las secciones historicas. La declaracion sobre intentos anteriores sigue desconocida.

Checkpoint local small: 901c26c1332695a2a8f243eb2f37243a37bea320. Tokenizer: 0e0117387f39004a9016484a186a908917e22426. pip check correcto; dependencias efectivas en tools/kronos-output/requirements-resolved.txt.

Fuente primaria: https://arxiv.org/html/2508.02739v1, apendice D, Forecasting Task Setup: preentrenamiento hasta junio de 2024; evaluacion del articulo desde julio de 2024. Es una declaracion del articulo, no una auditoria de procedencia del checkpoint descargado. A 2026-10-19, el tiempo transcurrido posterior a ese corte es menor de 2.4 años, antes de reservar desarrollo, calentamiento y holdout. No se ha verificado cobertura de archivos de mercado ni certificado OOS de los pesos.

Diagnostico analitico reproducible con statistics.NormalDist, sin precios ni senales: para alfa bilateral 0.05, potencia 0.80 y Sharpe anual verdadero 0.5, T=((1.9599639845+0.8416212336)/0.5)^2=31.3955 años bajo aproximacion iid/normal. MDE a cinco años = (1.9599639845+0.8416212336)/sqrt(5)=1.25291. No se usa 0.5 como efecto empirico observado: es un chequeo de capacidad del diseño en su propio umbral. No es una estimacion de frecuencia real ni potencia del t de R por trade.

Limite: la estrategia propuesta tiene exposicion intermitente y stops; el caso portfolio siempre invertido del skill no se traslada literalmente a sus trades. Este calculo corresponde al criterio Sharpe sobre patrimonio diario, no sustituye el triage de episodios, dependencia y R. No implica imposibilidad de significancia con un efecto mucho mayor ni demuestra ausencia de edge en Kronos. Tampoco es prueba de que 31 años garanticen pasar DSR/drawdown/resto de condiciones.

Decision de Codex: NO LISTO para backtest confirmatorio; incompatibilidad entre confirmar efectos cercanos al umbral propuesto y el horizonte de cinco años del protocolo. Mi propuesta inicial debio incluir este diagnostico antes de pedir aceptacion. No se ejecuta ni se presenta como completa Fase 0; sin conteo de frecuencia real, sin folds derivados, sin seleccion de periodo/reserva y sin backtest. No se incrementa N de resultados evaluados ni se declara cerrado el modelo por falta de edge. Cualquier cambio de objetivo (p. ej. demostracion descriptiva sin pretension de confirmar rentabilidad) requiere decision explicita; no subir el Sharpe requerido para forzar viabilidad ni reoptimizar parametros.
