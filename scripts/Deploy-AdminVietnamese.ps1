[CmdletBinding()]
param(
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot',
    [string]$SourceRoot = ''
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($SourceRoot)) {
    $SourceRoot = Join-Path $PSScriptRoot '..\assets\admin'
}
$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$web = (Resolve-Path -LiteralPath $WebRoot).Path
$backupRoot = Join-Path $web ('_deploy_backups\admin_vi_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

$files = @(
    'common\admin_vi.js',
    'common\admin_vi.css',
    'admincenter\templates\header.shtml',
    'admincenter\templates\login.shtml',
    'admincenter\templates\top.shtml',
    'admincenter\templates\menu.shtml',
    'admincenter\templates\body.shtml',
    'admintool\templates\header.shtml',
    'admintool\templates\new_header.shtml',
    'admintool\templates\login.shtml',
    'admintool\templates\admin_top.shtml',
    'admintool\templates\admin_left.shtml',
    'admintool\templates\index.shtml'
)

New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null

foreach ($relative in $files) {
    $sourceFile = Join-Path $source $relative
    $targetFile = Join-Path (Join-Path $web 'oss') $relative
    $backupFile = Join-Path $backupRoot (Join-Path 'oss' $relative)

    if (-not (Test-Path -LiteralPath $sourceFile)) {
        throw "Thieu file nguon: $sourceFile"
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $targetFile) -Force | Out-Null
    if (Test-Path -LiteralPath $targetFile) {
        New-Item -ItemType Directory -Path (Split-Path -Parent $backupFile) -Force | Out-Null
        Copy-Item -LiteralPath $targetFile -Destination $backupFile -Force
    }
    Copy-Item -LiteralPath $sourceFile -Destination $targetFile -Force

    $sourceHash = (Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash
    $targetHash = (Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash
    if ($sourceHash -ne $targetHash) {
        throw "Xac minh SHA-256 that bai: $relative"
    }
}

Write-Output "Da trien khai Viet hoa admin. Backup: $backupRoot"
