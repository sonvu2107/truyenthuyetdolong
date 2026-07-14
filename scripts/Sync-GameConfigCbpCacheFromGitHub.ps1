[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot'
)

$ErrorActionPreference = 'Stop'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$manifestPath = 'assets/manifest-gameconfig-cbp-cache-20260714.json'
$workRoot = Join-Path $env:TEMP ('ahtl-gameconfig-cache-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $WebRoot ('_deploy_backups\gameconfig_cbp_cache_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Get-GitHubFile {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    $log = "$Destination.download.log"
    $url = "$repoBase/$RelativePath"
    & certutil.exe -urlcache $url delete *> $null
    cmd.exe /c "certutil.exe -urlcache -split -f $url $Destination > $log 2>&1"
    if ($LASTEXITCODE -ne 0) {
        $details = Get-Content -LiteralPath $log -Raw -ErrorAction SilentlyContinue
        throw "Khong tai duoc $RelativePath. $details"
    }
    Remove-Item -LiteralPath $log -Force -ErrorAction SilentlyContinue
}

try {
    $manifestFile = Join-Path $workRoot 'manifest.json'
    Get-GitHubFile -RelativePath $manifestPath -Destination $manifestFile
    $manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne '20260714itemcache1' -or $manifest.files.Count -ne 1 -or
        $manifest.files[0].source -ne 'assets/game/GameConfig.php' -or
        $manifest.files[0].target -ne 'game/GameConfig.php') {
        throw 'Manifest GameConfig khong dung pham vi cache CBP.'
    }

    $file = $manifest.files[0]
    $download = Join-Path $workRoot $file.source.Replace('/', '\')
    Get-GitHubFile -RelativePath $file.source -Destination $download
    $actual = (Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash
    if ($actual -ne $file.sha256) {
        throw "Sai SHA-256 cho $($file.source)."
    }

    $target = Join-Path $WebRoot $file.target.Replace('/', '\')
    if (-not (Test-Path -LiteralPath $target)) {
        throw "Khong tim thay file deploy dich: $target"
    }
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot 'GameConfig.php') -Force
    Copy-Item -LiteralPath $download -Destination $target -Force

    $deployedHash = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
    if ($deployedHash -ne $file.sha256) {
        throw 'Hash GameConfig sau deploy khong khop manifest.'
    }
    Write-Output "Da deploy cache CBP $($manifest.version); backup: $backupRoot"
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
