[CmdletBinding()]
param(
    [string]$ServerRoot = 'C:\GPHANTL\server',
    [string]$RawBase = 'https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/main',
    [string]$ExpectedVersion = '20260712logicvi1'
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

$tempRoot = Join-Path $env:TEMP ('ahtl-logiclang-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
try {
    $manifestPath = Join-Path $tempRoot 'manifest.json'
    Get-RemoteFile -Url ($RawBase.TrimEnd('/') + '/assets/manifest-logicserver-language-20260712.json') -Destination $manifestPath
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne $ExpectedVersion) {
        throw "Unexpected manifest version: $($manifest.version)"
    }
    if ($manifest.blocked -eq $true) {
        $reason = [string]$manifest.block_reason
        if ([string]::IsNullOrWhiteSpace($reason)) {
            $reason = 'No reason was supplied.'
        }
        throw "LogicServer language deployment is blocked: $reason"
    }

    $downloads = @()
    foreach ($entry in $manifest.files) {
        $relativeSource = [string]$entry.source
        $relativeTarget = [string]$entry.target
        if ($relativeTarget -notmatch '^LogicServer/data/language/Zh-CN/(NormalTalk|EntityName|Quest|Item)\.txt$') {
            throw "Target is outside allowed language scope: $relativeTarget"
        }
        $target = Join-Path $ServerRoot ($relativeTarget -replace '/', '\\')
        $expectedSourceHash = ([string]$entry.source_sha256).ToUpperInvariant()
        if ($expectedSourceHash -notmatch '^[0-9A-F]{64}$') {
            throw "Missing or invalid source SHA-256: $relativeTarget"
        }
        if ((Get-Sha256 -Path $target) -ne $expectedSourceHash) {
            throw "Live source SHA-256 mismatch: $relativeTarget. Files were not changed."
        }
        $name = Split-Path -Path $relativeSource -Leaf
        $download = Join-Path $tempRoot $name
        Get-RemoteFile -Url ($RawBase.TrimEnd('/') + '/' + ($relativeSource -replace '\\', '/')) -Destination $download
        if ((Get-Sha256 -Path $download) -ne ([string]$entry.sha256).ToUpperInvariant()) {
            throw "SHA-256 mismatch: $name"
        }
        $downloads += [pscustomobject]@{ Entry = $entry; Path = $download; Name = $name }
    }

    $langRoot = Join-Path $ServerRoot 'LogicServer\data\language\Zh-CN'
    if (-not (Test-Path -LiteralPath $langRoot)) {
        throw "Language folder not found: $langRoot"
    }
    $backupRoot = Join-Path $ServerRoot ('_deploy_backups\logicserver_language_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

    foreach ($download in $downloads) {
        $target = Join-Path $ServerRoot (([string]$download.Entry.target) -replace '/', '\\')
        Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot $download.Name) -Force
        Copy-Item -LiteralPath $download.Path -Destination $target -Force
        if ((Get-Sha256 -Path $target) -ne ([string]$download.Entry.sha256).ToUpperInvariant()) {
            throw "Post-copy SHA-256 mismatch: $($download.Name)"
        }
    }

    Write-Output "LogicServer language deployed: $($manifest.version)"
    Write-Output "Backup: $backupRoot"
    Write-Output 'Start LogicServer with the normal maintenance procedure after this command completes.'
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
