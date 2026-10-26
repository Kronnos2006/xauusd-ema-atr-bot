# ATLAS — Evaluación temporal incremental

El módulo `atlas/validacion_temporal.py` produce ventanas cronológicas de **entrenamiento → embargo → prueba**, con señales de entrada externas congeladas.

**Importante:** el código todavía **no entrena ni optimiza estrategias**. Por tanto, los resultados son evaluación temporal descriptiva sobre reglas prefijadas, **no** walk-forward confirmatorio. Cada ventana guarda indices de entrenamiento, embargo y prueba, retorno neto intrabar, referencia y drawdown. Los folds pueden solaparse entre sí si `paso < prueba`; la futura evaluación estadística deberá manejar dependencia.

Se admite únicamente señal con preregistro y verificación de sello suministrada por una etapa externa. No existe aún comprobación criptográfica de la firma del sello. No usa dinero, API bursátil ni `data/kt002`.

**Pendientes:** conectores de datos reales con auditoría de recepción, bloqueo de holdout por hash, entrenamiento restringido a datos previos a cada corte, validación remota del preregistro y criterios estadísticos preregistrados. Ningún resultado de este módulo autoriza negociación.
