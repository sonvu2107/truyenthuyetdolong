[CmdletBinding()]
param(
    [string]$GatePath = 'C:\GPHANTL\server\AHServer\GateServer\Win32\GateServer32_R.exe',
    [string]$GateWorkingDirectory = 'C:\GPHANTL\server\AHServer\GateServer\Win32',
    [string]$InstallRoot = 'C:\GPHANTL\tools',
    [string]$TaskName = 'AHTLGateServer'
)

$ErrorActionPreference = 'Stop'
$expectedSha256 = '4B9B9535AC39479EC35BDC3DA862FB59EE546E89099DDEA943ADF39DD3503148'

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal $identity
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw 'Hay chay PowerShell bang Run as administrator.'
}

$sourceWrapper = Join-Path $PSScriptRoot 'Start-GateWithDynamicHandshake.ps1'
if (-not (Test-Path -LiteralPath $sourceWrapper -PathType Leaf)) {
    throw "Khong tim thay wrapper: $sourceWrapper"
}
if (-not (Test-Path -LiteralPath $GatePath -PathType Leaf)) {
    throw "Khong tim thay GateServer: $GatePath"
}
if (-not (Test-Path -LiteralPath $GateWorkingDirectory -PathType Container)) {
    throw "Khong tim thay working directory: $GateWorkingDirectory"
}

$gateHash = (Get-FileHash -LiteralPath $GatePath -Algorithm SHA256).Hash
if ($gateHash -ne $expectedSha256) {
    throw "GateServer khong dung binary goc duoc ho tro: $gateHash"
}

New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
$installedWrapper = Join-Path $InstallRoot 'Start-GateWithDynamicHandshake.ps1'
Copy-Item -LiteralPath $sourceWrapper -Destination $installedWrapper -Force

$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask -and $existingTask.State -eq 'Running') {
    Stop-ScheduledTask -TaskName $TaskName
    Start-Sleep -Seconds 1
}
Get-Process -Name 'GateServer32_R' -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

$powerShell = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
$arguments = '-NoProfile -ExecutionPolicy Bypass -File "{0}"' -f $installedWrapper
$action = New-ScheduledTaskAction `
    -Execute $powerShell `
    -Argument $arguments `
    -WorkingDirectory $GateWorkingDirectory
$bootTrigger = New-ScheduledTaskTrigger -AtStartup
$taskPrincipal = New-ScheduledTaskPrincipal `
    -UserId 'SYSTEM' `
    -LogonType ServiceAccount `
    -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Days 3650) `
    -RestartCount 999 `
    -RestartInterval (New-TimeSpan -Minutes 1)
$task = New-ScheduledTask `
    -Action $action `
    -Trigger $bootTrigger `
    -Principal $taskPrincipal `
    -Settings $settings
Register-ScheduledTask -TaskName $TaskName -InputObject $task -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName

$deadline = (Get-Date).AddSeconds(40)
do {
    Start-Sleep -Milliseconds 500
    $gate = Get-Process -Name 'GateServer32_R' -ErrorAction SilentlyContinue
    $listen = netstat -ano | Select-String ':13000\s+.*LISTENING'
    $backChannel = if ($gate) {
        netstat -ano | Select-String ('127\.0\.0\.1:23000\s+ESTABLISHED\s+' + $gate.Id + '$')
    }
    $taskState = (Get-ScheduledTask -TaskName $TaskName).State
} while ((-not $gate -or -not $listen -or -not $backChannel -or $taskState -ne 'Running') -and
    (Get-Date) -lt $deadline)

if (-not $gate) { throw 'GateServer khong khoi dong.' }
if (-not $listen) { throw 'GateServer khong listen port 13000.' }
if (-not $backChannel) { throw 'GateServer chua ket noi LogicServer port 23000.' }
if ($taskState -ne 'Running') { throw "Task $TaskName co state=$taskState" }

Get-ScheduledTask -TaskName $TaskName |
    Select-Object TaskName, State,
        @{N = 'Trigger'; E = { $_.Triggers.CimClass.CimClassName }},
        @{N = 'Execute'; E = { $_.Actions.Execute }},
        @{N = 'WorkingDirectory'; E = { $_.Actions.WorkingDirectory }} |
    Format-List
Get-Process -Name 'GateServer32_R' | Select-Object Id, StartTime, Path | Format-List
Get-Content (Join-Path $InstallRoot 'gate-wrapper.log') -Tail 5 -ErrorAction SilentlyContinue
netstat -ano | Select-String ':13000|:23000'
