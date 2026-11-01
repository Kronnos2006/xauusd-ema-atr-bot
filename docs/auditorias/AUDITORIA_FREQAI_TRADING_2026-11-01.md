# KRONNOS — FreqAI integración y auditoría profesional (2026-11-01)
## Alcance probado
- El combinador `tools/kronnos_ensemble.py` admite FreqAI desde PR #68, pero **no ejecuta ni verifica modelos**.
- `tools/freqai_to_kronnos.py` importa resultados que se reciban de un productor FreqAI, exige manifiesto SHA-256, tiempos UTC, objetivo posterior a creación, IDs únicos y puntuaciones finitas en [-1,1]; prepara JSON compatible con combinador. SHA concordante **no prueba que FreqAI ejecutó** ni certifica su autoría.
- **No se ha creado una alimentación prospectiva real** ni un cron de predicción, por falta de un productor persistente verificado y un preregistro independiente. No usar históricos como prospectivos.
## Hallazgos de auditoría de trading (puertas de aceptación)
1. **Procedencia**: exigir evidencia de ejecución real (run, commit, imagen/digest, inputs, hashes y hora UTC), fuente punto-en-tiempo y hora de disponibilidad; el adaptador actual NO la certifica.
2. **Diseño causal**: preregistrar activo, horizonte, cutoff, reentrenamiento, universo, costos, separación temporal y holdout. Sin resultados usados para elegir parámetros.
3. **Baselines**: persistencia, siempre-sube, Kronos y TimesFM solo si mismo instrumento/horizonte/fecha; comparar en muestra sin solape y costos.
4. **Métricas**: acierto direccional, Brier si puntuación probabilística calibrada, MAE si objetivo es rendimiento; drawdown, turnover, slippage y costos solo si existe simulación predeclarada; controles de latencia y datos faltantes.
5. **Riesgo**: stress test, comportamiento de fallas, apagado preventivo, exposición nula por defecto. Nunca credenciales de exchange con permiso de órdenes.
6. **Validación**: walk-forward, ≥30 operaciones por fold si aplica, DSR ≥0.95 para hipótesis financieras con censo completo de intentos, evaluación independiente y reglas de promoción; **ATLAS H3/H4 siguen BLOQUEADOS**.
7. **Integridad**: NO alterar KT-002, data/kt002, datasets sellados, resultados de KT-004 ni el PR #42. Si no hay custodio externo previo, dictamen INCONCLUSO.
## Próximos hitos externos
- Productor FreqAI real en CI aislado que entregue predicciones nuevas posteriores al prerregistro, con procedencia autenticada; pruebas de integración en sandbox (sin operar).
- Auditoría independiente del censo/historial y sellado externo previo; sin eso no abrir ATLAS.
- Evaluación prospectiva completa y aprobación explícita del propietario para promoción futura, sin afirmar rentabilidad.
## Dictamen
**Software adaptador preparado, fase de producción de predicciones NO COMPLETA, estrategia de trading NO APROBADA**. Ninguna promesa de ventaja financiera.
