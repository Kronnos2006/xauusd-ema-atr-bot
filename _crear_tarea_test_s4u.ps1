$pythonExe = 'C:\Users\josem\AppData\Local\Programs\Python\Python313\python.exe'
$scriptPath = 'C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\test_s4u_conexion_mt5.py'
$workDir = 'C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta'

$action = New-ScheduledTaskAction -Execute $pythonExe -Argument "-u `"$scriptPath`"" -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(15)
$principal = New-ScheduledTaskPrincipal -UserId 'josem' -LogonType S4U -RunLevel Limited

Register-ScheduledTask -TaskName 'EMA_XAUUSD_LiveSignalLogger_TEST' -Action $action -Trigger $trigger -Principal $principal -Description 'PRUEBA no productiva: LogonType S4U' -Force | Out-Null
