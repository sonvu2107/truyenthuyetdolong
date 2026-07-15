[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$ServerRoot = 'C:\GPHANTL',
    [string]$GameHost = 'http://180.93.244.31:81'
)

$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$webRoot = Join-Path $ServerRoot 'server\GPHweb\wwwroot'
$logicRoot = Join-Path $ServerRoot 'server\LogicServer\data\language\Zh-CN'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$manifestRelative = 'assets/manifest-localization-release-20260715.json'
$workRoot = Join-Path $env:TEMP ('ahtl-localization-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $ServerRoot ('server\_deploy_backups\localization_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Get-Sha256([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

function Get-RemoteFile([string]$RelativePath, [string]$Destination) {
    Invoke-WebRequest -UseBasicParsing -Uri "$repoBase/$RelativePath" -OutFile $Destination
}

$logicWasRunning = $false
$copied = @()
$spDef = Join-Path $webRoot 'game\SPDef.php'
$spDefBackup = $null
try {
    New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
    $manifestPath = Join-Path $workRoot 'manifest.json'
    Get-RemoteFile $manifestRelative $manifestPath
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne '20260715vinotices1' -or @($manifest.files).Count -ne 9) {
        throw 'Manifest release không đúng phạm vi 9 file Việt hóa.'
    }

    foreach ($file in $manifest.files) {
        $target = if ($file.target -like 'web/*') {
            Join-Path $webRoot $file.target.Substring(4).Replace('/', '\')
        } elseif ($file.target -like 'logic/*') {
            Join-Path $logicRoot $file.target.Substring(6).Replace('/', '\')
        } else {
            throw "Đích ngoài phạm vi: $($file.target)"
        }
        if (-not (Test-Path -LiteralPath $target)) { throw "Thiếu file live: $target" }
        if ((Get-Sha256 $target) -ne $file.source_sha256.ToUpperInvariant()) {
            throw "Hash live đã thay đổi, hủy deploy: $($file.target)"
        }
        $download = Join-Path $workRoot ([IO.Path]::GetFileName($file.source))
        Get-RemoteFile $file.source $download
        if ((Get-Sha256 $download) -ne $file.sha256.ToUpperInvariant()) {
            throw "Hash tải về sai: $($file.source)"
        }
        Add-Member -InputObject $file -NotePropertyName target_path -NotePropertyValue $target
        Add-Member -InputObject $file -NotePropertyName download_path -NotePropertyValue $download
    }

    $logicWasRunning = @(Get-Process -Name LogicServerCQ32_R,LogicServer -ErrorAction SilentlyContinue).Count -gt 0
    if ($logicWasRunning) {
        Stop-ScheduledTask -TaskName 'AHTLLogicServer' -ErrorAction Stop
        $deadline = (Get-Date).AddSeconds(60)
        while ((Get-Process -Name LogicServerCQ32_R,LogicServer -ErrorAction SilentlyContinue) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 2 }
        if (Get-Process -Name LogicServerCQ32_R,LogicServer -ErrorAction SilentlyContinue) { throw 'LogicServer chưa dừng sau 60 giây.' }
    }

    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    foreach ($file in $manifest.files) {
        $backup = Join-Path $backupRoot $file.target.Replace('/', '\')
        New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
        Copy-Item -LiteralPath $file.target_path -Destination $backup -Force
    }
    $spDefBackup = Join-Path $backupRoot 'web\game\SPDef.php'
    New-Item -ItemType Directory -Path (Split-Path -Parent $spDefBackup) -Force | Out-Null
    Copy-Item -LiteralPath $spDef -Destination $spDefBackup -Force

    foreach ($file in $manifest.files) {
        Copy-Item -LiteralPath $file.download_path -Destination $file.target_path -Force
        if ((Get-Sha256 $file.target_path) -ne $file.sha256.ToUpperInvariant()) { throw "Hash sau chép sai: $($file.target)" }
        $copied += $file
    }
    $spDefText = Get-Content -LiteralPath $spDef -Raw -Encoding UTF8
    $pattern = "define\('GAMEAPPURL','[^']*'\);"
    $replacement = "define('GAMEAPPURL','$($GameHost.TrimEnd('/'))/GameFrame.swf?v=$($manifest.version)');"
    if ($spDefText -notmatch $pattern) { throw 'Không tìm thấy GAMEAPPURL.' }
    Set-Content -LiteralPath $spDef -Value ($spDefText -replace $pattern, $replacement) -Encoding UTF8

    if ($logicWasRunning) {
        Start-ScheduledTask -TaskName 'AHTLLogicServer' -ErrorAction Stop
        $deadline = (Get-Date).AddSeconds(60)
        while (-not (Get-Process -Name LogicServerCQ32_R,LogicServer -ErrorAction SilentlyContinue)) {
            if ((Get-Date) -gt $deadline) { throw 'LogicServer không khởi động lại sau 60 giây.' }
            Start-Sleep -Seconds 2
        }
    }

    Write-Output "DEPLOY_OK=$($manifest.version)"
    Write-Output "BACKUP=$backupRoot"
    foreach ($file in $manifest.files) { Write-Output "HASH=$($file.target)|$(Get-Sha256 $file.target_path)" }
    Get-Process -Name LogicServerCQ32_R,LogicServer -ErrorAction SilentlyContinue | ForEach-Object { Write-Output "PROCESS=$($_.ProcessName)|$($_.Id)" }
}
catch {
    foreach ($file in $copied) {
        $backup = Join-Path $backupRoot $file.target.Replace('/', '\')
        if (Test-Path -LiteralPath $backup) { Copy-Item -LiteralPath $backup -Destination $file.target_path -Force }
    }
    if ($spDefBackup -and (Test-Path -LiteralPath $spDefBackup)) { Copy-Item -LiteralPath $spDefBackup -Destination $spDef -Force }
    throw
}
finally {
    if ($logicWasRunning -and -not (Get-Process -Name LogicServerCQ32_R,LogicServer -ErrorAction SilentlyContinue)) { Start-ScheduledTask -TaskName 'AHTLLogicServer' -ErrorAction SilentlyContinue }
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
