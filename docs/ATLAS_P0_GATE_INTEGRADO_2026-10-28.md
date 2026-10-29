# Kronnos — ATLAS P0: gate único integrado y sin IA

Comando: `python3 tools/atlas_p0_gate.py` genera JSON y SHA-256 reproducibles, sin conectores de IA ni servicios pagos.

Opcional: `python3 tools/atlas_p0_gate.py --manifest expediente.json --stamp-spec sello.json`. Sello.json usa rutas locales `data`, `tsr`, `ca_file`, `event_utc` y opcional `untrusted`. La CA debe ser validada fuera del propio expediente. Se reutilizan módulos existentes: atlas_p0_guard y atlas_verificador_evidencias. GitHub Actions comprueba los casos de rechazo.

ATENCIÓN: se distingue correctamente: sello válido con CA aportada NO prueba custodia externa, censo exhaustivo, autenticidad del origen de precios, DSR ni auditoría independiente. El gate SIEMPRE devuelve `promocion_permitida=false` y `cierre_p0_autorizado=false`. Para levantar bloqueos se requieren datos externos completos y una auditoría separada; esta herramienta solo identifica y presenta el estado. El PR #42 y H3/H4 siguen bloqueados. No se envían órdenes ni se ejecutan estrategias.
