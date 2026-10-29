# Kronnos — Norma de ingeniería inversa y automatización
Fecha: 2026-10-29. Instrucción del propietario.

## Principio rector
Analizar sistemas externos, entender sus patrones, contrastarlos con el código propio, mejorar componentes existentes e incorporar únicamente cambios que demuestren una ventaja operativa verificable. No desviarse del plan maestro.

## Método obligatorio
1. Inventariar el problema actual y la prueba que falla.
2. Revisar primero si el repositorio ya tiene una solución.
3. Estudiar referencias externas (Lumina Capital AI, Qlib, FreqAI, Kronos, TimesFM) sin suponer que su README es evidencia de funcionamiento.
4. Revisar licencia y dependencias: Lumina CC BY-NC 4.0; no copiar ni reutilizar su código en usos comerciales sin autorización.
5. Diseñar un parche mínimo en rama aislada; preferir Python stdlib y GitHub Actions cuando sean suficientes.
6. Usar scripts deterministas para verificaciones, diagnósticos, comparadores, logs y reportes repetidos. Cero llamadas a LLM en ejecución normal.
7. Pruebas negativas, integridad, reproducibilidad y evidencia CI antes de fusionar.
8. Mantener autoría veraz, evidencia histórica, diffs pequeños, sin trading real y sin dependencia nueva de Claude.
9. Nunca confundir contrato válido con modelo ejecutado, inferencia real, predicción preregistrada o ventaja estadística.
10. Informar hechos verificables, problemas sin resolver y el siguiente bloqueo del plan.

## Orden de prioridad
P0 — ATLAS integridad externa, custodia, censo exhaustivo y validación confirmatoria.
P1 — KT-002: continuidad verificable de predicciones reales; Kronos, TimesFM, KT-001 y Siempre sube.
P2 — Ensayos reproducibles de motores independientes y comparadores.
P3 — Automatización, observabilidad y calidad; ORION coordina lo anterior.

No abrir nuevas hipótesis, añadir modelos ni sustituir motores sin justificación medible y preregistro. PR #42 permanece bloqueado hasta auditoría independiente y aprobación expresa.
