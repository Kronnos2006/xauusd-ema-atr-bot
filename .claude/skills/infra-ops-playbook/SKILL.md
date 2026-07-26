---
name: infra-ops-playbook
description: Playbook de diagnóstico y cambios seguros sobre Task Scheduler y MT5 (LogonType, tareas programadas, procesos de loggers en vivo) armado a partir de los incidentes reales de este proyecto. Consultar antes de tocar LogonType, registrar/desregistrar tareas, matar procesos de loggers, o diagnosticar caídas/gaps de un logger en vivo.
---

# Infra Ops Playbook (Task Scheduler + MT5)

Cada paso de este playbook responde a un incidente real de este proyecto, no es teórico. No saltarse pasos "porque esta vez parece simple" — el orphan de procesos de esta sesión pasó precisamente por apurar el paso 3.

## 1. Verificar elevación ANTES de intentar nada que la necesite

`LogonType=S4U` o `Password`, matar un proceso que corre bajo token S4U, o mutar el `Principal` de una tarea ya S4U: todo esto requiere una PowerShell **elevada** (Administrador). Comprobar antes de intentar:

```powershell
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
```

Si devuelve `False` y la operación lo requiere: **no** insistir con variantes de `schtasks.exe`, `Register-ScheduledTask` con distintos parámetros, o `Stop-Process` reintentado. Ya está confirmado en este proyecto que `schtasks.exe /Create /RU ... ` sin elevación puede "tener éxito" (exit code 0) mientras degrada silenciosamente `S4U` a `Interactive` sin ningún error visible — no hay forma de evitar la elevación con otra sintaxis. Armar el comando completo y pedirle al usuario que lo corra en una PowerShell como Administrador.

## 2. Backup antes de cualquier cambio destructivo sobre una tarea existente

Antes de tocar una tarea productiva (cambiar Principal, LogonType, Action, Triggers):

```powershell
Export-ScheduledTask -TaskName "<nombre>" | Out-File "<ruta>\task_backup_<timestamp>.xml" -Encoding utf8
```

El XML de export contiene el SID de usuario de Windows — nunca commitearlo (el patrón `task_backup_*.xml` ya está en `.gitignore` de este proyecto; si el nombre del backup no matchea ese patrón, agregarlo antes de que quede trackeado por accidente).

## 3. Preferir desregistrar + re-registrar desde cero, no mutar

`Set-ScheduledTask -Principal` sobre una tarea que ya tiene un proceso corriendo puede dejar el proceso hijo huérfano (sin supervisión de Task Scheduler), porque el cambio de Principal no siempre se propaga limpiamente al proceso en ejecución. El patrón que funcionó en este proyecto:

1. Confirmar el PID del proceso actual antes de tocar nada (correlacionando `CreationDate` del proceso con la última línea "ARRANQUE" del log correspondiente — nunca asumir el PID a ciegas).
2. `Stop-Process -Id <pid> -Force` (o `Stop-ScheduledTask` si el wrapper `cmd.exe` sigue vivo y supervisado).
3. `Unregister-ScheduledTask -TaskName "<nombre>" -Confirm:$false`.
4. Reconstruir `Action`/`Trigger`/`Settings`/`Principal` desde cero y `Register-ScheduledTask` de nuevo (no editar la tarea existente).
5. `Start-ScheduledTask` y verificar (ver paso 5).

**Ojo con `Stop-ScheduledTask` en particular**: puede matar el `cmd.exe` que Task Scheduler supervisa pero dejar el `python.exe` hijo corriendo huérfano y sin proceso padre vivo — pasó exactamente esto en este proyecto al intentar desplegar un fix sobre tareas ya S4U. Después de cualquier `Stop-ScheduledTask`, verificar que no haya quedado un proceso huérfano (ver paso 5) antes de asumir que el reinicio limpió todo.

## 4. Diagnosticar un gap o caída: distinguir sleep de caída real ANTES de asumir un bug

No asumir que un hueco de latidos en el log es una falla del script. Revisar en este orden:

1. **Event Log `Microsoft-Windows-Power-Troubleshooter` (ID 1)**: si el sistema se suspendió (sleep) durante la ventana del gap, el timestamp del evento coincide casi exactamente con el inicio/fin del hueco de latidos — causa benigna, no hay nada que arreglar en el código.
2. **Event Log `System`, IDs 6005/6006/6008**: inicio/parada/apagado-inesperado del servicio de Registro de eventos — equivalente a un boot/shutdown real de Windows. Si coincide con el gap, es un reinicio real de la máquina, no solo sleep.
3. **Task Scheduler Operational log**: si Task Scheduler relanzó la tarea durante la ventana (nueva ejecución), contrastar con si el PID del proceso cambió o no.
4. **PID/CreationDate/SessionId del proceso**: si el mismo PID sigue vivo antes y después del gap (mismo `CreationDate`), el proceso nunca murió — el silencio es enteramente por el sleep, no un defecto del script (el heartbeat no corre si no hay CPU ejecutando instrucciones).

No mezclar estas dos causas en una sola conclusión — en este proyecto hubo reinicios de logger que eran boot real de Windows, y otros que eran logoff/reconexión de sesión (Parsec) sin ningún reinicio de máquina. Son causas distintas con implicancias distintas.

## 5. Verificar DESPUÉS de cualquier cambio, no solo antes

Nunca dar un cambio por exitoso solo porque el comando devolvió exit code 0. Confirmar explícitamente:

- `Get-ScheduledTask -TaskName "<nombre>" | Select State` y `Get-ScheduledTaskInfo -TaskName "<nombre>" | Select LastTaskResult` (0 = éxito real, no solo "no tiró excepción").
- `Get-ScheduledTask -TaskName "<nombre>" | Select -ExpandProperty Principal` — confirmar `LogonType` real, no asumido (recordar el caso de degradación silenciosa a `Interactive`).
- El proceso real: `Get-CimInstance Win32_Process -Filter "Name='python.exe'"` con `CommandLine` (para identificar cuál script es cuál) y `ParentProcessId` — si el padre no existe más, es un huérfano, no un proceso supervisado.
- Una línea "ARRANQUE" (o el evento de arranque equivalente) nueva en el log del script, con timestamp posterior al cambio.

Si algo no verifica como se esperaba, no es "probablemente está bien" — es un hallazgo a reportar, aunque el comando haya devuelto éxito.

## Patrón de conexión resiliente en scripts de loggers en vivo

Los loggers de este proyecto (`log_senales_demo.py`, `log_senal_macro_dfii10.py`) usan una versión propia de conexión a MT5 que **nunca** llama `mt5.shutdown()`/`sys.exit()` en un fallo transitorio — la función equivalente del backtest (`conectar_mt5`) sí lo hace, y usarla directamente mataría el proceso de fondo. Si se agrega un logger nuevo, reusar el patrón `intentar_conectar()` ya existente (devuelve `False` y loguea, no corta el proceso), y agregar conteo de fallos consecutivos que fuerce `mt5.shutdown()+initialize()` tras varios fallos seguidos de IPC (no confiar en que un error de IPC lance una excepción — puede devolver `None` silenciosamente).
