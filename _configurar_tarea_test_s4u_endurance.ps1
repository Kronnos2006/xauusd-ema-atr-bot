$py = 'C:\Users\josem\AppData\Local\Programs\Python\Python313\python.exe'
$script = 'C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\log_senales_demo_test_s4u.py'
$stdout = 'C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta\test_s4u_endurance_stdout.log'
$workDir = 'C:\Users\josem\OneDrive\Documents\rxt21\Nueva carpeta'

$cmdArgs = '/c ""' + $py + '" -u "' + $script + '" >> "' + $stdout + '" 2>&1"'
$action = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument $cmdArgs -WorkingDirectory $workDir

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(10) `
    -RepetitionInterval (New-TimeSpan -Minutes 15) `
    -RepetitionDuration (New-TimeSpan -Days 4)

$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Seconds 0)

Set-ScheduledTask -TaskName "EMA_XAUUSD_LiveSignalLogger_TEST" -Action $action -Trigger $trigger -Settings $settings
Start-ScheduledTask -TaskName "EMA_XAUUSD_LiveSignalLogger_TEST"
Start-Sleep -Seconds 5
Get-ScheduledTaskInfo -TaskName "EMA_XAUUSD_LiveSignalLogger_TEST" | Format-List LastRunTime, LastTaskResult, NextRunTime
