# BTCUSDT Spot — borrador de Fase 0

Fecha: 2026-10-16, Costa Rica. Autor: Codex. Revisión pendiente.
Estado: NO LISTO; diseño preliminar, sin resultados, sin backtest y sin holdout sellado.

## Alcance y orden

Investigación exclusivamente en simulación, BTCUSDT Spot, sin margen ni órdenes. Se retira la propuesta de fijar 5 minutos de antemano.

1. Verificar y cerrar documentalmente Fase 0 de `tsm-volscaling`, incluido su commit y push.
2. Fijar por escrito el período reservado de BTC antes de analizar precios o rentabilidad. Descargar archivos oficiales y sellar manifiesto antes de explorar el desarrollo.
3. Auditar datos y costos en desarrollo; comparar factibilidad de 5 min, 1 h y 4 h sin buscar la variante con mayor beneficio.
4. Elegir una única señal por un mecanismo explícito y registrar el intento.
5. Completar triage de frecuencia y potencia con datos reales; luego pre-registrar hipótesis, reglas y corte, con decisión explícita del usuario.
6. Construir backtest solo si se cumplen los pasos anteriores. El holdout permanece reservado hasta una decisión posterior.

Proyectos localizados en C:\proyectos\tsm-volscaling y C:\proyectos\estrategias-clasicas. TSM tiene CLAUDE.md y docs/preregistro_fase0.md v1.0, pero no repositorio Git inicializado; su cierre sigue pendiente. Sus instrucciones requieren proponer el paso y esperar OK antes de ejecutarlo. Este documento no abre un segundo experimento ejecutable.

## Hipótesis pendiente

BTC y una duración de minutos describen un mercado y una preferencia, no una señal falsable. No se inventa una regla de entrada para completar el protocolo. Pendientes: condición medible, dirección esperada, horizonte de salida, regla de riesgo y número máximo de variantes. Si los costos descartan minutos, presentar 1 h/4 h al usuario antes de cambiar el horizonte.

## Costos: evidencia y supuestos

La [tabla oficial de Binance](https://www.binance.com/en/fee/trading), consultada el 2026-10-16, muestra para usuario regular Maker/Taker de 0,100 %/0,100 %, y 0,075 %/0,075 % con descuento BNB. Base propuesta: sin descuentos ni promociones; no es una verificación de la tarifa privada de la cuenta ni de las comisiones históricas.

Con f=0,001 por lado, la aproximación de comisión de ida y vuelta es 20 puntos básicos (0,20 %). Bajo un modelo de comisiones proporcionales que reducen el patrimonio en cada ejecución, el alza de equilibrio es 1/(1-f)^2 - 1 = 0,2003004 %, antes de fricción adicional. La implementación debe explicitar en qué activo se cobra cada comisión y su efecto sobre cantidades, saldo y redondeos.

Costo total: comisión de compra y venta + spread efectivo + deslizamiento por ambos lados. Sin funding de futuros. No tratar una orden límite como ejecución garantizada ni asignarle automáticamente costo cero.

Los klines OHLCV no contienen cotizaciones bid/ask, profundidad ni posición en cola: no permiten recuperar spread y deslizamiento históricos exactos. Hace falta evidencia de ejecución pública adicional o escenarios adversos declarados; el tamaño nocional de la orden está pendiente. Un snapshot actual no representa ocho años de costos.

En desarrollo, comparar costos con distribuciones de movimientos a horizontes definidos, por año y régimen. El rango high-low de una vela no es beneficio capturable ni una señal. Que una vela supere el costo no prueba edge; que muchas no lo superen tampoco descarta automáticamente señales selectivas o tenencias de varias velas.

## Datos y control de integridad

Fuente: [archivos públicos oficiales de Binance](https://data.binance.vision/?prefix=data/spot/monthly/klines/BTCUSDT/1m/), no yfinance. La [documentación oficial](https://github.com/binance/binance-public-data) describe archivos mensuales/diarios, checksums SHA-256 y cambios de archivos publicados. Desde 2025 los timestamps Spot usan microsegundos. Se deben conservar los ZIP originales, verificar sus CHECKSUM y registrar versión, URL y fecha de descarga. La cobertura de BTC desde 2017 y cualquier hueco deben comprobarse en los archivos; no se dan por auditados.

Auditar continuidad temporal, duplicados, orden, límites UTC y consistencia OHLCV antes de agregar intervalos. No rellenar velas faltantes fabricando precios. Validar agregación de 5 min/1 h/4 h y contrastar una muestra de desarrollo con el endpoint oficial, aclarando que es coherencia interna, no proveedor independiente.

## Holdout: diseño pendiente, no sellado

Antes de descargar: fijar cortes cronológicos de desarrollo y holdout, con período inicial de calentamiento y separación suficiente para evitar posiciones/etiquetas solapadas. Los cortes y la duración máxima de posición no están definidos aún. Verificar si el histórico ya se consultó en otro proyecto: reservarlo ahora no elimina exposición previa.

Al descargar: generar manifiesto por archivo con SHA-256, bytes, URL, fecha de captura y partición; hashear el manifiesto y versionarlo junto al protocolo. Guardar la reserva separada y excluir su carga del código de desarrollo. Verificar únicamente integridad de la reserva, sin gráficos, estadísticas de precios ni rendimientos. Registrar accesos y cualquier contaminación. Un hash no demuestra ausencia de lectura. No afirmar equivalencia con `estrategias-clasicas` hasta leer su implementación.

## Registro de intentos y potencia

Reservar identificador documental BTC-SPOT-001, sin resultados evaluados. Localizar el registro canónico de N_total y su cifra previa antes de modificarlo: no se conoce en este workspace. Sumar la hipótesis al registro al formalizar el intento; contar además todas las variantes realmente evaluadas y ensayos relacionados según la disciplina DSR. Separar número de hipótesis de número de variantes: una sola hipótesis no equivale siempre a N=1. No inventar un N_total global ni asumir que toda prueba pasada tiene igual dependencia estadística.

Tras definir señal, contar episodios no solapados sobre desarrollo y estimar dependencia. No igualar número de velas con observaciones independientes. Para potencia, no transferir automáticamente las medias R de factores macro al scalping BTC: justificar una referencia comparable o calcular el efecto mínimo detectable y declarar límites. Si se usa una formulación de portfolio/Sharpe, aplicar el caso específico de hypothesis-gate.

## Descarte y condiciones de avance

- Pausar si TSM sigue pendiente de cierre verificable.
- No avanzar con cobertura, unidades, integridad o estado de reserva sin resolver.
- Descartar en triage si la proyección de potencia justificada requiere más de cinco años, conforme al protocolo vigente.
- Si el movimiento capturable bajo la regla específica no cubre costos fundamentados, descartar esa regla/horizonte. No fijar un umbral de viabilidad después de observar los resultados.
- Si no hay señal concreta, referencia de potencia defendible o regla numérica explícita del usuario, estado NO LISTO, sin backtest.

Se mantienen walk-forward anclado, mínimo 30 trades TEST por fold, evaluación con/sin el fold dominante y DSR >= 0,95 contando variantes. El número de folds se deriva de la distribución real. Estos requisitos no sustituyen la regla de corte completa específica de BTC, aún pendiente de decisión del usuario. Nada de lo anterior constituye aprobación para capital real.

## Evidencia actual

Solo revisión documental y consulta de fuentes oficiales. Ningún histórico BTC descargado; costos de ejecución no medidos; ningún hash de reserva generado; ningún backtest, commit o push ejecutado. Pendientes: rutas TSM/clásicas, revisión del borrador, cierres cronológicos, tamaño nocional y definiciones de hipótesis y corte.

## Verificacion posterior de rutas y protocolo

El usuario confirmo la migracion a C:\proyectos. Revisiones realizadas desde las carpetas correspondientes:
- TSM: docs/preregistro_fase0.md aceptado el 2026-09-21, pendiente de commit/push. No se encontro .git. No hay evidencia de cierre de Fase 0 ni se iniciaron sus fases de datos/resultados.
- Clasicas: datos/registro_holdout.json declara closed=true, sellado 2026-08-20 21:51:46, con hashes por 15 instrumentos, fechas, filas y columnas. docs/fase0_protocolo.md y src/fase0_congelar.py describen separacion WF/reserva. No se abrio, leyo ni copio datos/final_test; no se recalcularon sus hashes, por lo que la integridad actual no esta certificada por esta revision.
- datos/registro_n.json conserva n_acumulado=8. TSM pre-registra N_previo=12 (8+4 clasicas) y N_total=13 (+1 TSM). BTC con una configuracion llevaria el total previsto a 14, una vez conciliado el registro canonico y formalizado el intento. No se modifico el registro ni el SR0 fijo pre-registrado de TSM. La regla del programa dice que los folds no incrementan N; contar variantes unicas y documentar ensayos adaptativos adicionales.
- Remotos leidos: estrategias-clasicas corresponde a Kronnos2006/estrategias-clasicas.git; el enlace xauusd-ema-atr-bot.git corresponde al proyecto XAUUSD, distinto. La inspeccion de estado Git de los repos migrados fallo con errores de worktree/permisos; no se repararon ni se supone que esten sincronizados.
- El borrador BTC permanece en la carpeta original de OneDrive. No se migro ni se copio al proyecto migrado.

Siguiente paso propuesto, pendiente de OK especifico conforme a CLAUDE.md de TSM: preparar Git, atributos/ignore y dependencias verificadas; commit y push del pre-registro y registro de hashes; conciliacion del registro del programa. Sin fases 1/2 ni apertura de reservas. La escritura en C:\proyectos requiere ademas acceso del entorno actual.

## Prioridad TSM completada

Fase 0 TSM cerrada con autorizacion explicita del usuario el 2026-10-16. Pre-registro publicado en 3762def90f4f7df7f71bd14e819e50e37567c093; cierre documentado y publicado en 17e6ac8bc7eac49663292827d795a667834138a1. Clasicas tiene N=13 publicado en c32769dcecc958fa46c4bbf06666bbe2f3c4d671. Consultar C:\proyectos\tsm-volscaling\docs\registro_commits.md y cierre_fase0.md. Esto reemplaza los bloqueos de cierre anteriores, conservados como historial. No se ejecutan fases siguientes ni se abre el holdout. BTC sigue sin datos ni experimento: quedan pendientes cortes de reserva, señal, costos de ejecucion y regla de corte; no se ha sumado al registro canonico.
