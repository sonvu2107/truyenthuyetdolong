[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot'
)

$ErrorActionPreference = 'Stop'
$Version = '20260714itemcache5'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$manifestPath = 'assets/manifest-runtime-items-localization-20260714.json'
$workRoot = Join-Path $env:TEMP ('ahtl-runtime-items-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $WebRoot ('_deploy_backups\runtime_items_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Get-GitHubFile {
    param([string]$RelativePath, [string]$Destination)
    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    $log = "$Destination.download.log"
    $url = "$repoBase/$RelativePath"
    & certutil.exe -urlcache $url delete *> $null
    cmd.exe /c "certutil.exe -urlcache -split -f $url $Destination > $log 2>&1"
    if ($LASTEXITCODE -ne 0) {
        throw "Khong tai duoc $RelativePath. $(Get-Content -LiteralPath $log -Raw -ErrorAction SilentlyContinue)"
    }
    Remove-Item -LiteralPath $log -Force -ErrorAction SilentlyContinue
}

function Test-AsciiToken {
    param([string]$Path, [string]$Token)
    return [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($Path)).Contains($Token)
}

function Copy-ToBackup {
    param([string]$Source, [string]$Name)
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination (Join-Path $backupRoot $Name) -Force
    }
}

try {
    New-Item -ItemType Directory -Path $workRoot -Force | Out-Null
    $manifestFile = Join-Path $workRoot 'manifest.json'
    Get-GitHubFile -RelativePath $manifestPath -Destination $manifestFile
    $manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne $Version -or $manifest.files.Count -ne 3 -or $manifest.entries.Count -ne 2) {
        throw 'Manifest runtime items khong dung pham vi.'
    }

    foreach ($file in $manifest.files) {
        $download = Join-Path $workRoot $file.source.Replace('/', '\')
        Get-GitHubFile -RelativePath $file.source -Destination $download
        if ((Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash -ne $file.sha256) {
            throw "Sai SHA-256 cua $($file.source)."
        }
    }

    $archiveFile = $manifest.files | Where-Object { $_.source -eq 'assets/lang/zh-cn/cbp.zip' } | Select-Object -First 1
    $gameConfigFile = $manifest.files | Where-Object { $_.source -eq 'assets/game/GameConfig.php' } | Select-Object -First 1
    $djrmFile = $manifest.files | Where-Object { $_.source -eq 'assets/game/djrm.php' } | Select-Object -First 1
    if ($null -eq $archiveFile -or $null -eq $gameConfigFile -or $null -eq $djrmFile) {
        throw 'Manifest thieu file bat buoc.'
    }
    $archive = Join-Path $workRoot $archiveFile.source.Replace('/', '\')
    $downloadedGameConfig = Join-Path $workRoot $gameConfigFile.source.Replace('/', '\')
    $downloadedDjrm = Join-Path $workRoot $djrmFile.source.Replace('/', '\')
    if (-not (Test-AsciiToken -Path $downloadedGameConfig -Token "cbppack=1&ver=$Version&nocache=1") -or
        -not (Test-AsciiToken -Path $downloadedDjrm -Token "AHTL_GLOBAL_CBP_CACHE_$Version") -or
        -not (Test-AsciiToken -Path $downloadedDjrm -Token "ahtlcache=${Version}gf")) {
        throw 'Cache key trong loader khong khop manifest.'
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
        foreach ($entrySpec in $manifest.entries) {
            $entry = $zip.Entries | Where-Object { $_.FullName -ieq $entrySpec.name } | Select-Object -First 1
            if ($null -eq $entry) { throw "Khong tim thay $($entrySpec.name) trong cbp.zip." }
            $stagedEntry = Join-Path $workRoot ('entry-' + $entrySpec.name)
            $input = $entry.Open()
            try {
                $output = [IO.File]::Open($stagedEntry, [IO.FileMode]::Create, [IO.FileAccess]::Write)
                try { $input.CopyTo($output) } finally { $output.Dispose() }
            } finally { $input.Dispose() }
            if ((Get-FileHash -LiteralPath $stagedEntry -Algorithm SHA256).Hash -ne $entrySpec.sha256) {
                throw "Sai SHA-256 entry $($entrySpec.name)."
            }
        }
    } finally { $zip.Dispose() }

    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    foreach ($file in $manifest.files) {
        Copy-ToBackup -Source (Join-Path $WebRoot $file.target.Replace('/', '\')) -Name ($file.target.Replace('/', '_'))
    }
    foreach ($entrySpec in $manifest.entries) {
        Copy-ToBackup -Source (Join-Path $WebRoot $entrySpec.target.Replace('/', '\')) -Name ($entrySpec.target.Replace('/', '_'))
    }

    try {
        foreach ($file in $manifest.files) {
            $source = Join-Path $workRoot $file.source.Replace('/', '\')
            $target = Join-Path $WebRoot $file.target.Replace('/', '\')
            New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $target -Force
            if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $file.sha256) {
                throw "Hash sau deploy khong khop: $($file.target)."
            }
        }
        foreach ($entrySpec in $manifest.entries) {
            $source = Join-Path $workRoot ('entry-' + $entrySpec.name)
            $target = Join-Path $WebRoot $entrySpec.target.Replace('/', '\')
            New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
            Copy-Item -LiteralPath $source -Destination $target -Force
            if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $entrySpec.sha256) {
                throw "Hash entry sau deploy khong khop: $($entrySpec.target)."
            }
        }
    }
    catch {
        foreach ($file in $manifest.files) {
            $backup = Join-Path $backupRoot $file.target.Replace('/', '_')
            if (Test-Path -LiteralPath $backup) {
                Copy-Item -LiteralPath $backup -Destination (Join-Path $WebRoot $file.target.Replace('/', '\')) -Force
            }
        }
        foreach ($entrySpec in $manifest.entries) {
            $backup = Join-Path $backupRoot $entrySpec.target.Replace('/', '_')
            if (Test-Path -LiteralPath $backup) {
                Copy-Item -LiteralPath $backup -Destination (Join-Path $WebRoot $entrySpec.target.Replace('/', '\')) -Force
            }
        }
        throw
    }

    Write-Output "Da deploy catalog runtime $Version; backup: $backupRoot"
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
