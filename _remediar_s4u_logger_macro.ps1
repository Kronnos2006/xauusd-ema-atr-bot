# Aplicar LogonType S4U a la tarea productiva EMA_XAUUSD_MacroDFII10_LiveSignalLogger,
# registrando desde cero (no mutando la existente) -- patron validado en el logger EMA,
# donde Set-ScheduledTask -Principal dejo un proceso huerfano sin supervision.
# Requiere consola de PowerShell como Administrador.

# 0. Confirmar que el proceso sigue siendo el mismo PID antes de matarlo
Get-CimInstance Win32_Process -Filter "ProcessId=33612" | Select-Object ProcessId, SessionId, CreationDate

# 1. Matar el proceso actual del logger macro
Stop-Process -Id 33612 -Force

# 2. Desregistrar la tarea vieja
Unregister-ScheduledTask -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger" -Confirm:$false

# 3. Reconstruir Action (identico al original)
$action = New-ScheduledTaskAction -Execute 'cmd.exe' `
    -Argument '/c ""C:\Users\josem\AppData\Local\Programs\Python\Python313\python.exe" -u "C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\log_senal_macro_dfii10.py" >> "C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\log_senal_macro_dfii10_stdout.log" 2>&1"' `
    -WorkingDirectory 'C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta'

# 4. Reconstruir los dos Triggers originales (cada 15min por 10 anios + logon)
$triggerTime = New-ScheduledTaskTrigger -Once -At '2026-07-24T20:56:41-06:00' `
    -RepetitionInterval (New-TimeSpan -Minutes 15) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User 'DESKTOP-08C36UV\josem'

# 5. Reconstruir Settings (RestartCount=999/1min, sin limite de ejecucion, no para con bateria)
$settings = New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0)

# 6. Principal con S4U desde la creacion
$principal = New-ScheduledTaskPrincipal -UserId 'josem' -LogonType S4U -RunLevel Limited

# 7. Registrar desde cero
Register-ScheduledTask -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger" `
    -Action $action -Trigger @($triggerTime, $triggerLogon) -Settings $settings -Principal $principal -Force

Start-ScheduledTask -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger"
Start-Sleep -Seconds 5
Get-ScheduledTaskInfo -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger" | Format-List LastRunTime, LastTaskResult
Get-ScheduledTask -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger" | Select-Object -ExpandProperty Principal
