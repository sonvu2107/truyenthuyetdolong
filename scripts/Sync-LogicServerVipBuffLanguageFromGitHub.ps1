[CmdletBinding()]
param(
    [string]$ServerRoot = 'C:\GPHANTL\server',
    [string]$RawBase = 'https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/main',
    [string]$ExpectedVersion = '20260714vipbuffvi1'
)

$ErrorActionPreference = 'Stop'

function Get-RemoteFile {
    param([Parameter(Mandatory = $true)][string]$Url, [Parameter(Mandatory = $true)][string]$Destination)
    & certutil.exe -urlcache -split -f $Url $Destination | Out-Null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Destination)) {
        throw "Download failed: $Url"
    }
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant()
}

$running = Get-Process -Name 'LogicServerCQ32_R', 'LogicServer' -ErrorAction SilentlyContinue
if ($running) {
    throw 'LogicServer is running. Stop LogicServer during maintenance, then run this script again. Files were not changed.'
}

$tempRoot = Join-Path $env:TEMP ('ahtl-vipbufflang-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
try {
    $manifestPath = Join-Path $tempRoot 'manifest.json'
    Get-RemoteFile -Url ($RawBase.TrimEnd('/') + '/assets/manifest-logicserver-vip-buff-language-20260714.json') -Destination $manifestPath
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne $ExpectedVersion -or @($manifest.files).Count -ne 1) {
        throw "Unexpected VIP buff language manifest: $($manifest.version)"
    }

    $entry = @($manifest.files)[0]
    if ($entry.target -ne 'LogicServer/data/language/Zh-CN/Misc.txt' -or $entry.source -ne 'assets/logicserver-language/Zh-CN/Misc.txt') {
        throw 'Manifest target is outside the allowed VIP buff language scope.'
    }

    $target = Join-Path $ServerRoot ($entry.target -replace '/', '\\')
    if ((Get-Sha256 -Path $target) -ne ([string]$entry.source_sha256).ToUpperInvariant()) {
        throw 'Live Misc.txt SHA-256 mismatch. Files were not changed.'
    }

    $download = Join-Path $tempRoot 'Misc.txt'
    Get-RemoteFile -Url ($RawBase.TrimEnd('/') + '/' + ($entry.source -replace '\\', '/')) -Destination $download
    if ((Get-Sha256 -Path $download) -ne ([string]$entry.sha256).ToUpperInvariant()) {
        throw 'Downloaded Misc.txt SHA-256 mismatch.'
    }

    $backupRoot = Join-Path $ServerRoot ('_deploy_backups\\logicserver_vip_buff_language_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot 'Misc.txt') -Force
    Copy-Item -LiteralPath $download -Destination $target -Force
    if ((Get-Sha256 -Path $target) -ne ([string]$entry.sha256).ToUpperInvariant()) {
        throw 'Post-copy SHA-256 mismatch: Misc.txt'
    }

    Write-Output "LogicServer VIP buff language deployed: $($manifest.version)"
    Write-Output "Backup: $backupRoot"
    Write-Output 'Start LogicServer with the normal maintenance procedure after this command completes.'
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
