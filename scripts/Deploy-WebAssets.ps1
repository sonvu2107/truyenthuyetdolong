[CmdletBinding()]
param(
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot',
    [Parameter(Mandatory = $true)]
    [string]$GameHost,
    [Parameter(Mandatory = $true)]
    [string]$Version
)

$ErrorActionPreference = 'Stop'
$assetsRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\assets')).Path
$spDefPath = Join-Path $WebRoot 'game\SPDef.php'
$backupRoot = Join-Path $WebRoot ('_deploy_backups\' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

foreach ($path in @($WebRoot, $assetsRoot, $spDefPath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Khong tim thay: $path"
    }
}

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

$files = @(
	@{ Source = 'client_login.php'; Target = 'client_login.php' },
	@{ Source = 'client_shell.html'; Target = 'client_shell.html' },
	@{ Source = 'client_frame.png'; Target = 'client_frame.png' },
    @{ Source = 'GameFrame.swf'; Target = 'GameFrame.swf' },
    @{ Source = 'ClientLang.txt'; Target = 'data\commonasset\ClientLang.txt' },
    @{ Source = 'lang\zh-cn\clientlang.cbp'; Target = 'data\lang\zh-cn\clientlang.cbp' },
    @{ Source = 'lang\zh-cn\cbp.zip'; Target = 'data\lang\zh-cn\cbp.zip' }
)

foreach ($file in $files) {
    $source = Join-Path $assetsRoot $file.Source
    $target = Join-Path $WebRoot $file.Target
    $backup = Join-Path $backupRoot $file.Target
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
$replacement = "define('GAMEAPPURL','$($GameHost.TrimEnd('/'))/GameFrame.swf?v=$Version');"

if ($spDef -notmatch $pattern) {
    throw 'Khong tim thay dong GAMEAPPURL trong game\SPDef.php.'
}

Set-Content -LiteralPath $spDefPath -Value ($spDef -replace $pattern, $replacement) -Encoding UTF8
Write-Output "Da deploy asset va dat GAMEAPPURL phien ban $Version"
