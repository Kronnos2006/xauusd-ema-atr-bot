---
name: sync-knowledge
description: Sincroniza memoria del proyecto, vault de Obsidian y commits de git después de cualquier incidente de infraestructura resuelto, fix desplegado a un logger en vivo, o resultado/checkpoint de una hipótesis. Se dispara solo, sin que el usuario tenga que pedirlo cada vez.
---

# Sync Knowledge

Este proyecto tiene tres lugares de verdad que tienen que quedar consistentes después de cualquier resultado o cambio importante: la memoria auto-persistente de Claude Code, el vault de Obsidian del proyecto, y el historial de git. En esta sesión ya pasó varias veces que quedaron desincronizados hasta que el usuario lo pidió explícitamente -- esta skill existe para que eso deje de depender de que lo pida.

## Cuándo disparar esto (no esperar a que lo pidan)

- Se resolvió o diagnosticó un incidente de infraestructura (caída de logger, corte de conexión, gap de latidos, migración de LogonType, etc.).
- Se aplicó y/o desplegó un fix a un script que corre en producción (loggers en vivo, Task Scheduler).
- Una hipótesis cruzó un checkpoint go/no-go (pasa, no pasa, queda con reservas) -- ver skill `hypothesis-gate`.
- Cualquier cambio de estado de la infraestructura productiva que vaya a importar la próxima vez que se retome el proyecto (ej. "ya no es Interactive, ahora es S4U").

No hace falta para cambios chicos de código sin impacto operativo (ej. un refactor sin cambio de comportamiento) -- el criterio es "si alguien retoma el proyecto en una sesión nueva, ¿necesita saber esto para no repetir trabajo o asumir algo desactualizado?".

## Vault de Obsidian: ubicación

El vault de este proyecto vive en `Nueva carpeta/XAUUSD EMA/ATR/` (tiene su propio `.obsidian/`) -- **no** es el vault conectado por defecto al servidor MCP de Librarian, que es de otro proyecto. Verificar la carpeta directamente si el MCP de Librarian no encuentra nada relacionado a este proyecto, en vez de asumir que no hay vault.

## Los tres pasos

### 1. Git

¿El código relevante al resultado/cambio está commiteado? Si hay cambios sin commit directamente relacionados, proponer el commit (mensaje enfocado en el *por qué*, no en el qué -- convención ya establecida en este repo). No commitear archivos operativos que el proyecto no versiona por convención (scripts `_remediar_*.ps1`/`_crear_*.ps1`, backups `*.xml`, logs, CSVs de datos en vivo -- revisar `.gitignore` y el patrón de commits previos antes de agregar algo nuevo al repo).

### 2. Memoria interna (auto-memory)

Crear o actualizar la nota `project` correspondiente en el sistema de memoria: qué pasó, **Por qué importa**, **Cómo aplicar** para la próxima sesión. Enlazar con `[[nombre-de-otra-nota]]` las notas relacionadas ya existentes. Actualizar la línea correspondiente en `MEMORY.md` (una línea, bajo ~150 caracteres). Si una nota existente quedó desactualizada por este cambio (ej. un pendiente que ya se resolvió), actualizarla ahí mismo en vez de dejar dos fuentes contradictorias.

### 3. Vault de Obsidian

Actualizar el/los archivo(s) que correspondan según el tipo de evento, siguiendo el estilo ya establecido (secciones con fecha, `[[wikilinks]]`, sección "Ver también" al final):

- **Incidente o cambio de infraestructura** → `Infraestructura.md` (estado operativo) y, si hubo un bug real con causa/fix, también una entrada nueva en `Errores y bugs corregidos.md`.
- **Resultado o checkpoint de una hipótesis** → la nota específica de esa hipótesis (ej. `Macro DFII10 - fase 1.md`) con el resultado y el veredicto.
- **Cualquiera de los dos casos anteriores que cambie qué es lo próximo a hacer** → `Estado actual y próximos pasos.md`, para que ese archivo siga siendo la fuente de verdad de "qué sigue corriendo" y "qué está pendiente" sin quedar desactualizado.

## Cómo reportarlo

No hacer esto en silencio ni como un paso oculto -- al cerrar la respuesta donde se resolvió el incidente/fix/checkpoint, mencionar en una línea qué se sincronizó ("actualicé memoria + vault + commit"; o si algo no aplicaba, decir cuál y por qué). Si el cambio tocó infraestructura productiva en vivo, este paso va DESPUÉS de que `infra-guardian` (o el chequeo manual equivalente) ya verificó el estado real -- no documentar un cambio como resuelto si todavía no se confirmó que quedó como se esperaba.
