[CmdletBinding()]
param(
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot',
    [string]$GameHost = 'http://180.93.244.31:81',
    [string]$Branch = 'main'
)

$ErrorActionPreference = 'Stop'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Branch"
$workRoot = Join-Path $env:TEMP ('ahtl-github-sync-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $WebRoot ('_deploy_backups\github_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

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
    Get-GitHubFile -RelativePath 'assets/manifest.json' -Destination (Join-Path $workRoot 'manifest.json')
    $manifest = Get-Content -LiteralPath (Join-Path $workRoot 'manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json

    foreach ($file in $manifest.files) {
        $download = Join-Path $workRoot ($file.source.Replace('/', '\'))
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
    foreach ($file in $manifest.files) {
        $source = Join-Path $workRoot ($file.source.Replace('/', '\'))
        $target = Join-Path $WebRoot ($file.target.Replace('/', '\'))
        $backup = Join-Path $backupRoot ($file.target.Replace('/', '\'))
        New-Item -ItemType Directory -Path (Split-Path -Parent $backup) -Force | Out-Null
        if (Test-Path -LiteralPath $target) {
            Copy-Item -LiteralPath $target -Destination $backup -Force
        }
        Copy-Item -LiteralPath $source -Destination $target -Force
    }

    $spDefBackup = Join-Path $backupRoot 'game\SPDef.php'
    New-Item -ItemType Directory -Path (Split-Path -Parent $spDefBackup) -Force | Out-Null
    Copy-Item -LiteralPath $spDefPath -Destination $spDefBackup -Force
    $spDef = Get-Content -LiteralPath $spDefPath -Raw -Encoding UTF8
    $pattern = "define\('GAMEAPPURL','[^']*'\);"
    $replacement = "define('GAMEAPPURL','$($GameHost.TrimEnd('/'))/GameFrame.swf?v=$($manifest.version)');"
    if ($spDef -notmatch $pattern) {
        throw 'Khong tim thay dong GAMEAPPURL trong game\SPDef.php.'
    }
    Set-Content -LiteralPath $spDefPath -Value ($spDef -replace $pattern, $replacement) -Encoding UTF8
    Write-Output "Da dong bo GitHub version $($manifest.version)."
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
