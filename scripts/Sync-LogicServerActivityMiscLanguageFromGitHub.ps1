[CmdletBinding()]
param(
    [string]$ServerRoot = 'C:\GPHANTL\server',
    [string]$RawBase = 'https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/main',
    [string]$ExpectedVersion = '20260714activitymiscvi1'
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

$tempRoot = Join-Path $env:TEMP ('ahtl-activitymisclang-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
try {
    $manifestPath = Join-Path $tempRoot 'manifest.json'
    Get-RemoteFile -Url ($RawBase.TrimEnd('/') + '/assets/manifest-logicserver-activity-misc-language-20260714.json') -Destination $manifestPath
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $files = @($manifest.files)
    if ($manifest.version -ne $ExpectedVersion -or $files.Count -ne 2) {
        throw "Unexpected activity/misc language manifest: $($manifest.version)"
    }

    $allowed = @{
        'assets/logicserver-language/Zh-CN/Activity.txt' = 'LogicServer/data/language/Zh-CN/Activity.txt'
        'assets/logicserver-language/Zh-CN/Misc.txt' = 'LogicServer/data/language/Zh-CN/Misc.txt'
    }
    $downloads = @()
    foreach ($entry in $files) {
        $source = [string]$entry.source
        $targetRelative = [string]$entry.target
        if (-not $allowed.ContainsKey($source) -or $allowed[$source] -ne $targetRelative) {
            throw "Manifest target is outside the allowed language scope: $targetRelative"
        }
        $target = Join-Path $ServerRoot $targetRelative.Replace('/', [IO.Path]::DirectorySeparatorChar)
        if ((Get-Sha256 -Path $target) -ne ([string]$entry.source_sha256).ToUpperInvariant()) {
            throw "Live source SHA-256 mismatch: $targetRelative. Files were not changed."
        }
        $download = Join-Path $tempRoot (Split-Path -Path $source -Leaf)
        Get-RemoteFile -Url ($RawBase.TrimEnd('/') + '/' + $source) -Destination $download
        if ((Get-Sha256 -Path $download) -ne ([string]$entry.sha256).ToUpperInvariant()) {
            throw "Downloaded SHA-256 mismatch: $source"
        }
        $downloads += [pscustomobject]@{ Entry = $entry; Target = $target; Download = $download }
    }

    $backupRoot = Join-Path $ServerRoot ('_deploy_backups\logicserver_activity_misc_language_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    foreach ($download in $downloads) {
        Copy-Item -LiteralPath $download.Target -Destination (Join-Path $backupRoot (Split-Path -Path $download.Target -Leaf)) -Force
        Copy-Item -LiteralPath $download.Download -Destination $download.Target -Force
        if ((Get-Sha256 -Path $download.Target) -ne ([string]$download.Entry.sha256).ToUpperInvariant()) {
            throw "Post-copy SHA-256 mismatch: $($download.Entry.target)"
        }
    }

    Write-Output "LogicServer activity/misc language deployed: $($manifest.version)"
    Write-Output "Backup: $backupRoot"
    Write-Output 'Start LogicServer with the normal maintenance procedure after this command completes.'
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
