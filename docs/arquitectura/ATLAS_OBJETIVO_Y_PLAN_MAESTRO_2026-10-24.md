# ORION–ATLAS — Objetivo estratégico, plan maestro y definición de terminado

**Fecha:** 24 de octubre de 2026 (Costa Rica)  
**Propietario / autoridad final:** José Mario  
**Responsable de ingeniería:** Claude (Anthropic)  
**Revisión cruzada:** ChatGPT (OpenAI)  
**Estado:** especificación de producto y criterios de aceptación; **no** aprobación de trading real ni declaración de rentabilidad.

## 1. Misión

**Convertir información del mercado en tesis y estrategias financieras fundamentadas, reproducibles y auditables, capaces de ser refutadas antes de convertirse en bots de simulación.**

ATLAS será el cerebro de investigación de ORION: un sistema que observe precios, volumen, liquidez, noticias y eventos macroeconómicos, cuestione sus propios modelos, identifique oportunidades, documente incertidumbres, compare alternativas, evalúe riesgos y sea capaz de recomendar **abstenerse**.

No será únicamente un predictor de precios, ni una máquina de señales ni un grupo de agentes que debaten sin evidencia. **El objetivo no es producir más tesis: es reducir decisiones mal fundamentadas y validar rigurosamente las que sobrevivan.**

## 2. Preguntas que ATLAS debe responder

1. ¿Qué está ocurriendo en cada mercado y qué ha cambiado respecto al contexto anterior?
2. ¿Qué hechos y noticias publicados a tiempo son relevantes y qué hipótesis causales quedan sin demostrar?
3. ¿Qué patrones técnicos, estadísticos, de volumen, liquidez y régimen se observan?
4. ¿Qué predicen Kronos, TimesFM y las referencias sencillas, y cuál es el alcance real de sus resultados?
5. ¿Qué evidencia respalda, contradice o deja inconclusa cada tesis?
6. ¿Las reglas derivadas generan mejoras robustas fuera de muestra y después de costos?
7. ¿Cuál es el efecto de una estrategia en la exposición y riesgo conjuntos del portafolio?

## 3. Arquitectura y responsabilidades

**ORION** opera, monitorea y coordina. **ATLAS** investiga, genera y refuta tesis. **Modelos** proponen evidencia predictiva sin autoridad decisoria. **Laboratorio** evalúa estrategias en simulación. **Control de riesgo** puede vetar. **Gerente** informa con enlaces verificables. **Propietario** conserva autoridad final. Claude implementa y ChatGPT realiza revisión cruzada.

Flujo obligatorio:

`DATOS CON PROCEDENCIA → ANÁLISIS INDEPENDIENTES → TESIS → CONTRADICCIÓN → PREREGISTRO → PRUEBAS FUERA DE MUESTRA → SIMULACIÓN CON COSTOS → ANÁLISIS DE PORTAFOLIO → AUDITORÍA → INFORME`

Un resultado de `INSUFICIENTE`, `INCONCLUSA` o `CONTRADICTORIA` puede cerrar la investigación o enviarla a recopilar más información. **Nunca se transforma automáticamente en una orden de compra/venta.**

## 4. Plan por fases y criterios de aceptación

| Fase | Entregable requerido | Criterios medibles de aceptación |
|---|---|---|
| **1. Fundación de datos** | Fuentes/adaptadores, contratos, timestamps, integridad y registro de tesis | Reproducción idéntica de entradas/tesis; pruebas de dato posterior al corte, duplicados, ausencia y discrepancias |
| **2. Inteligencia del mercado** | Analítica técnica, noticias, macro, liquidez, modelos y contexto por activo | Cada evidencia identifica fuente/hora/calidad; no se inventa cobertura; analistas mantienen independencia |
| **3. Contradicciones y gobierno** | Motor de argumentos a favor/en contra, 4 conclusiones y estados de tesis | Pruebas adversas; abstención por datos insuficientes; aprobaciones humanas autenticadas fuera de cadenas de texto |
| **4. Evaluación prospectiva** | Registro externo fechado de tesis antes del resultado y evaluador | Verificar sello temporal remoto, puntuación posterior al vencimiento, tasas de acierto/error, errores evitados y aciertos descartados |
| **5. Laboratorio de estrategias** | Reglas objetivas, backtesting, pruebas fuera de muestra, simulación sin dinero real | Preregistro, comparación con baseline, costos/derrapaje, control de sobreajuste, resultados reproducibles y validación de riesgo |
| **6. Inteligencia de portafolio** | Agregación de estrategias simuladas, correlación, exposición y estrés | Riesgos compartidos identificados, límites y vetos probados, medición de drawdown/concentración/liquidez |
| **7. Plataforma integral** | Integración al panel ORION, reportes y observabilidad | Informes automáticos trazables, operaciones seguras, aislamiento de experimentos y recuperación documentada |

**Puertas de aprobación:** cada fase requiere evidencia y revisión independiente; completar código/documentación no equivale a demostrar capacidad financiera. Las fases 5–6 no deben fingirse concluidas si ninguna hipótesis supera la evaluación científica.

## 5. Productos finales esperados

### A. Observatorio de mercado
Cubre activos autorizados (inicialmente BTCUSDT; más adelante otros mercados según fuentes legales y verificables), noticias, macro, tendencias, volatilidad y cambios relevantes. Señala fuentes inaccesibles y retrasos.

### B. Fábrica de tesis
Toda tesis lleva ID, hipótesis, mecanismo, horizonte, fuentes, argumentos a favor/en contra, incertidumbre, criterios de invalidación, estado, responsable y trazabilidad. Puede cuestionar a Kronos y TimesFM sin atribuirles aciertos no confirmados.

### C. Motor de contradicciones
Examina temporalidad, calidad, cobertura, explicaciones alternativas, relación con el horizonte, evidencia opuesta, sesgo retrospectivo, costos y riesgos. **Se abstiene por defecto si faltan pruebas críticas**.

### D. Laboratorio de estrategias y bots simulados
Solo estrategias con reglas objetivas y revisión pasan a backtest, walk-forward y paper trading. Cada bot se vincula a la tesis/preregistro originales; sin fondos, credenciales ni órdenes reales.

### E. Gestor de portafolio
Evalúa correlación, concentraciones, riesgo agregado, exposición por activos y factores, liquidez, escenarios adversos y dependencia compartida de modelos/datos.

### F. Informe del gerente y memoria científica
Registra qué se decidió, cuándo, con qué datos, qué salió mal, qué se descartó y cómo evolucionó el desempeño. No reescribe tesis antiguas; los cambios se versionan.

## 6. Cómo demostrar que ATLAS agrega valor

**Métricas de integridad:** cobertura verificable, fugas temporales detectadas, reproducibilidad, porcentaje de registros válidos, trazabilidad y abstenciones fundamentadas.

**Métricas prospectivas:** predicciones erróneas evitadas, predicciones acertadas descartadas, errores/aciertos en casos investigados, tasas de abstención y cobertura de decisiones; comparar contra Kronos, TimesFM, KT-001, siempre-sube y alternativas sin ATLAS. No presentar una tasa alta de abstención como desempeño financiero.

**Métricas de estrategia:** retorno neto simulado después de comisiones/spread/deslizamiento, drawdown, rotación, sensibilidad a parámetros, robustez fuera de muestra, exposición al riesgo y comparación preregistrada con referencias.

**Métricas de portafolio:** riesgo total, correlación efectiva, concentración, escenarios de estrés y capacidad de cumplir límites.

**Rigor:** establecer tamaño de muestra, hipótesis y criterio de aceptación antes de la evaluación; corregir por múltiples pruebas cuando aplique, proteger holdouts y distinguir rendimiento técnico de rentabilidad demostrada. Ninguna cifra futura de beneficio es garantía.

## 7. Orden inmediata de ejecución — octubre de 2026

1. Mantener intactos KT-002 y el seguimiento operativo de siete días tras el PR #32.
2. Consolidar y revisar las correcciones del **PR #37** con el **PR #34** sin que sesiones simultáneas de Claude modifiquen la misma rama.
3. Corregir y probar autenticidad de revisores, asociación modelo–tesis, sellos de tiempo remotos y calidad de los datos. Las soluciones provisionales deben identificarse como tales.
4. Implementar y auditar el evaluador prospectivo de errores evitados **y** aciertos descartados; no atribuir retroactivamente sellos remotos a tesis.
5. Someter los cambios a CI y revisión independiente; no fusionar ATLAS a master sin aprobar las puertas pertinentes.
6. Una vez estable la fase 4, diseñar un piloto de estrategia 100 % simulada y, cuando haya hipótesis validada, el módulo de portafolio.

Referencias: [PR #32](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/32), [PR #33](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/33), [PR #34](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/34), [PR #37](https://github.com/Kronnos2006/xauusd-ema-atr-bot/pull/37), [issue #31](https://github.com/Kronnos2006/xauusd-ema-atr-bot/issues/31).

## 8. Definición de «terminado»

**ATLAS técnicamente terminado** exige las siete fases implementadas, probadas y auditadas, con fuentes confiables, registro prospectivo auténtico, controles de autorización, escenarios de fallo, panel utilizable y capacidad de abstenerse, generar tesis, simular estrategias y evaluar portafolios. Ninguna capacidad esencial debe ser solo un documento.

**ATLAS financieramente validado** es un estado adicional: debe demostrar con evidencia prospectiva suficiente y fuera de muestra que las estrategias simuladas aportan mejora estadística y económica neta frente a referencias y cumplen límites de riesgo. Puede quedar **NO DEMOSTRADO** aunque el sistema esté técnicamente terminado.

**No autorizado:** trading real, inversión de capital, cambio de parámetros de KT-002, modificación de predicciones existentes, ampliación no aprobada de permisos o servicios pagados.

## 9. Principio rector

> **ORION observa. ATLAS investiga. Los modelos proponen. La evidencia contradice o respalda. El laboratorio comprueba. Riesgo protege. El gerente informa. El propietario decide.**

**Resultado esperado:** una fábrica de estrategias financieras fundamentadas y refutables, no una fábrica de señales automáticas.

---
Operated-By: ChatGPT (OpenAI)  
Review-Required-By: Claude (Anthropic) + propietario  
Final-Authority: propietario
