# Remediacion: matar los procesos python huerfanos de EMA y macro (quedaron sin
# supervision de Task Scheduler tras un Stop-ScheduledTask que solo mato el cmd.exe
# padre) y relanzar ambas tareas para que tomen el codigo nuevo con auto-recuperacion
# de IPC (mt5.shutdown()+initialize() tras varios fallos seguidos).
# Requiere consola de PowerShell como Administrador (Stop-Process sobre procesos S4U
# falla con "Acceso denegado" desde una shell no elevada).

# 1. Identificar los huerfanos por linea de comando (mas confiable que el PID, que
#    puede haber cambiado) y confirmar antes de matar.
$huerfanoEma = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*log_senales_demo.py*' }
$huerfanoMacro = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*log_senal_macro_dfii10.py*' }

$huerfanoEma | Select-Object ProcessId, ParentProcessId, CreationDate, CommandLine
$huerfanoMacro | Select-Object ProcessId, ParentProcessId, CreationDate, CommandLine

# 2. Matarlos (si aparece mas de uno para el mismo script, matar todos -- no deberia
#    pasar salvo que ya haya una duplicacion en curso).
$huerfanoEma | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
$huerfanoMacro | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

Start-Sleep -Seconds 2

# 3. Relanzar ambas tareas productivas (ya migradas a S4U) para que corran el
#    codigo nuevo con auto-recuperacion de IPC.
Start-ScheduledTask -TaskName "EMA_XAUUSD_LiveSignalLogger"
Start-ScheduledTask -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger"

Start-Sleep -Seconds 8

# 4. Verificar: LastTaskResult debe quedar en 0, y debe aparecer una nueva linea
#    ARRANQUE en ambos logs con timestamp de ahora.
Get-ScheduledTaskInfo -TaskName "EMA_XAUUSD_LiveSignalLogger" | Format-List LastRunTime, LastTaskResult
Get-ScheduledTaskInfo -TaskName "EMA_XAUUSD_MacroDFII10_LiveSignalLogger" | Format-List LastRunTime, LastTaskResult
Get-Content "C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\senales_demo_live.log" -Tail 3
Get-Content "C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\senal_macro_dfii10_live.log" -Tail 3
