# Censo de intentos — Bloqueo A

Generado por `tools/atlas_censo_desde_git.py` (determinista; reconstruible desde el historial Git).

- `censo_intentos.jsonl`: cadena SHA-256 solo-anexar (`atlas-intentos-v1`), verificable con `atlas.censo_variantes.verificar_censo`.
- `ANCLA_CENSO.json`: SHA-256 del archivo, líneas, último hash y corte UTC.
- `fuentes_git.json`: commit de alta de cada intento (la fecha la fija GitHub, no quien arma el censo).
- Sello externo: workflow `atlas-custodia.yml` reconstruye el censo, exige coincidencia byte a byte y pide sellos RFC 3161 a FreeTSA y DigiCert.

## Qué cierra y qué no

| Control | Estado con esta entrega |
|---|---|
| A.1 Censo localizado, N real | Censo versionado; N = cota inferior de este repo |
| A.3 Sello externo | Dos TSA RFC 3161 de terceros (una vez corra el workflow) |
| A.4 Pruebas en CI | Reconstrucción + verificación en GitHub Actions |
| A.2 Custodio independiente | **Pendiente**: requiere cuenta del propietario (p. ej. S3 Object Lock Compliance) |
| A.5 Certificación | **Pendiente**: auditor que no sea el autor (ChatGPT/desconfiado) + OK del propietario |

Fuera del alcance: corridas del Strategy Tester no versionadas, pruebas hechas en chats y otros
repositorios (`estrategias-clasicas`, `tsm-volscaling`, `auditoria-bots`). Si existieron, el N real es mayor.
El sello prueba existencia en la fecha del sello, no retroactiva.
