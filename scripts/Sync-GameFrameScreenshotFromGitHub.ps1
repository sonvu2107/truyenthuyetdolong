[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot',
    [string]$GameHost = 'http://180.93.244.31:81'
)

$ErrorActionPreference = 'Stop'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$manifestPath = 'assets/manifest-gameframe-screenshot-20260712.json'
$workRoot = Join-Path 'C:\Temp' ('ahtl-gameframe-screenshot-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $WebRoot ('_deploy_backups\gameframe_screenshot_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
$expectedFiles = @(
    [PSCustomObject]@{ source = 'assets/GameFrame.swf'; target = 'GameFrame.swf' },
    [PSCustomObject]@{ source = 'assets/lang/zh-cn/cbp.zip'; target = 'data/lang/zh-cn/cbp.zip' }
)

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
    $manifestFiles = @($manifest.files)

    if ($manifest.version -ne '20260712uifit6' -or $manifestFiles.Count -ne $expectedFiles.Count) {
        throw 'Manifest screenshot UI khong dung version hoac pham vi.'
    }
    for ($index = 0; $index -lt $expectedFiles.Count; $index++) {
        if ($manifestFiles[$index].source -ne $expectedFiles[$index].source -or
            $manifestFiles[$index].target -ne $expectedFiles[$index].target) {
            throw 'Manifest screenshot UI co file ngoai pham vi cho phep.'
        }
    }

    foreach ($file in $manifestFiles) {
        $download = Join-Path $workRoot $file.source.Replace('/', '\')
        Get-GitHubFile -RelativePath $file.source -Destination $download
        $actual = (Get-FileHash -LiteralPath $download -Algorithm SHA256).Hash
        if ($actual -ne $file.sha256) {
            throw "Sai SHA-256 cho $($file.source)."
        }
    }

    $spDefPath = Join-Path $WebRoot 'game\SPDef.php'
    if (-not (Test-Path -LiteralPath $spDefPath)) {
        throw "Khong tim thay $spDefPath"
    }
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $backupRoot 'game') -Force | Out-Null
    Copy-Item -LiteralPath $spDefPath -Destination (Join-Path $backupRoot 'game\SPDef.php') -Force

    foreach ($file in $manifestFiles) {
        $target = Join-Path $WebRoot $file.target
        if (-not (Test-Path -LiteralPath $target)) {
            throw "Khong tim thay file deploy dich: $target"
        }
        $backup = Join-Path $backupRoot $file.target
        New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
        Copy-Item -LiteralPath $target -Destination $backup -Force
    }

    foreach ($file in $manifestFiles) {
        $download = Join-Path $workRoot $file.source.Replace('/', '\')
        $target = Join-Path $WebRoot $file.target
        Copy-Item -LiteralPath $download -Destination $target -Force
    }

    $spDef = Get-Content -LiteralPath $spDefPath -Raw -Encoding UTF8
    $pattern = "define\('GAMEAPPURL','[^']*'\);"
    $replacement = "define('GAMEAPPURL','$($GameHost.TrimEnd('/'))/GameFrame.swf?v=$($manifest.version)');"
    if ($spDef -notmatch $pattern) {
        throw 'Khong tim thay dong GAMEAPPURL trong game\SPDef.php.'
    }
    Set-Content -LiteralPath $spDefPath -Value ($spDef -replace $pattern, $replacement) -Encoding UTF8
    Write-Output "Da deploy screenshot UI $($manifest.version); backup: $backupRoot"
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
