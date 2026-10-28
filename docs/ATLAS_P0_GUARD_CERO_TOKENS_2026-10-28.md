# Kronnos — auditor P0 reutilizable sin tokens de IA
Uso: `python3 tools/atlas_p0_guard.py` o `python3 tools/atlas_p0_guard.py --manifest evidencia.json --out artifacts/atlas-p0-report.json`.
Python stdlib. No SDK OpenAI/Anthropic, no llamadas a LLM, sin red ni credenciales. Github Actions permite repetir diagnóstico a demanda, con artifact y SHA-256.

## Los cinco controles
1. Censo exhaustivo: censo con SHA, N entero positivo y revisión de exhaustividad ajena.
2. Custodia: URI de recibo, SHA de custodia y custodio independiente.
3. Datos: huellas de precios, recibo temporal externo y pre-registro.
4. Walk-forward: artefactos de folds, DSR y costos.
5. Auditoria: informe, revisor independiente y aprobación externa del propietario.

## Advertencia esencial
El script **NO verifica criptográficamente sellos RFC3161, Object Lock, exhaustividad de variantes, fuente de precios ni matemática DSR**: solo valida manifest declarativo. Todos los campos completos producen `EVIDENCIA_DECLARADA_NO_VERIFICADA`, JAMAS aprobado ni promoción. Eso requiere verificadores independientes por control. Ninguna ausencia de evidencia habilita H3/H4.
No alterar PR42 ni KT-002; es vigilancia defensiva.
