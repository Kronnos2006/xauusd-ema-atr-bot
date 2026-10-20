# Monitor de conveniencia (NO productivo) del holdout en vivo de la hipotesis
# Macro DFII10. Corre una vez al dia via Task Scheduler (LogonType=Interactive,
# necesario porque muestra una notificacion toast en el escritorio -- si no hay
# sesion iniciada ese dia, simplemente no se muestra hasta el proximo login).
#
# No toca el CSV del logger productivo, solo lo lee. Guarda su propio estado
# en estado_monitor_dfii10.json para no re-notificar filas ya vistas.
#
# Rutas resueltas desde la ubicacion del propio script ($PSScriptRoot) para que
# el proyecto funcione desde cualquier carpeta sin editar el codigo.

$csvPath = Join-Path $PSScriptRoot 'senal_macro_dfii10_live.csv'
$estadoPath = Join-Path $PSScriptRoot 'estado_monitor_dfii10.json'

if (-not (Test-Path $csvPath)) {
    exit 0
}

$filas = @(Import-Csv -Path $csvPath)
$conteoActual = $filas.Count

$conteoAnterior = 0
if (Test-Path $estadoPath) {
    try {
        $estado = Get-Content $estadoPath -Raw | ConvertFrom-Json
        $conteoAnterior = [int]$estado.conteo
    } catch {
        $conteoAnterior = 0
    }
}

if ($conteoActual -gt $conteoAnterior) {
    $nuevas = $filas | Select-Object -Skip $conteoAnterior
    $detalle = ($nuevas | ForEach-Object {
        "evento=$($_.evento) entrada=$($_.fecha_entrada) resultado_R=$($_.resultado_R)"
    }) -join "`n"
    $nuevosEpisodios = $conteoActual - $conteoAnterior
    $titulo = "Macro DFII10: $nuevosEpisodios episodio(s) nuevo(s) en el holdout"

    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(
            [Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        $textNodes.Item(0).AppendChild($template.CreateTextNode($titulo)) | Out-Null
        $textNodes.Item(1).AppendChild($template.CreateTextNode($detalle)) | Out-Null
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("PowerShell").Show($toast)
    } catch {
        # Si el toast falla (ej. sin sesion grafica), no perder el aviso --
        # dejar constancia en un log simple ademas del estado.
        $logPath = Join-Path $PSScriptRoot 'monitor_holdout_dfii10.log'
        "$(Get-Date -Format o) UTC-local | $titulo`n$detalle`n(toast fallo: $($_.Exception.Message))" |
            Out-File -FilePath $logPath -Append -Encoding utf8
    }
}

@{ conteo = $conteoActual; ultima_revision = (Get-Date -Format 'o') } |
    ConvertTo-Json | Set-Content -Path $estadoPath -Encoding utf8