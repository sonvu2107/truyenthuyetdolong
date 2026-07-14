[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot'
)

$ErrorActionPreference = 'Stop'
$Version = '20260714bagui3'
$RepoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$ManifestRelativePath = 'assets/manifest-backpack-polish-20260714.json'
$WorkRoot = Join-Path $env:TEMP ('ahtl-backpack-ui-' + [Guid]::NewGuid().ToString('N'))
$BackupRoot = Join-Path $WebRoot ('_deploy_backups\backpack_ui_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

function Get-GitHubFile {
    param([string]$RelativePath, [string]$Destination)
    New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
    Invoke-WebRequest -UseBasicParsing -Uri "$RepoBase/$RelativePath" -OutFile $Destination
}

function Copy-ToBackup {
    param([string]$Source, [string]$Name)
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination (Join-Path $BackupRoot $Name) -Force
    }
}

try {
    New-Item -ItemType Directory -Path $WorkRoot -Force | Out-Null
    $ManifestPath = Join-Path $WorkRoot 'manifest.json'
    Get-GitHubFile -RelativePath $ManifestRelativePath -Destination $ManifestPath
    $Manifest = Get-Content -LiteralPath $ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($Manifest.version -ne $Version -or $Manifest.files.Count -ne 4 -or $Manifest.entries.Count -ne 1) {
        throw 'Manifest Hanh Trang khong dung pham vi.'
    }

    foreach ($File in $Manifest.files) {
        $Download = Join-Path $WorkRoot $File.source.Replace('/', '\')
        Get-GitHubFile -RelativePath $File.source -Destination $Download
        if ((Get-FileHash -LiteralPath $Download -Algorithm SHA256).Hash -ne $File.sha256) {
            throw "Sai SHA-256 cua $($File.source)."
        }
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $Archive = Join-Path $WorkRoot 'assets\lang\zh-cn\cbp.zip'
    $Zip = [IO.Compression.ZipFile]::OpenRead($Archive)
    try {
        $Entry = $Zip.Entries | Where-Object { $_.FullName -ieq 'bagQuickConfig.cbp' } | Select-Object -First 1
        if ($null -eq $Entry) { throw 'cbp.zip thieu bagQuickConfig.cbp.' }
        $DirectEntry = Join-Path $WorkRoot 'bagQuickConfig.cbp'
        $Input = $Entry.Open()
        try {
            $Output = [IO.File]::Create($DirectEntry)
            try { $Input.CopyTo($Output) } finally { $Output.Dispose() }
        }
        finally { $Input.Dispose() }
    }
    finally { $Zip.Dispose() }
    if ((Get-FileHash -LiteralPath $DirectEntry -Algorithm SHA256).Hash -ne $Manifest.entries[0].sha256) {
        throw 'Sai SHA-256 cua bagQuickConfig.cbp.'
    }

    New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
    foreach ($File in $Manifest.files) {
        $Target = Join-Path $WebRoot $File.target.Replace('/', '\')
        Copy-ToBackup -Source $Target -Name $File.target.Replace('/', '_')
    }
    $DirectTarget = Join-Path $WebRoot 'data\lang\zh-cn\bagQuickConfig.cbp'
    Copy-ToBackup -Source $DirectTarget -Name 'data_lang_zh-cn_bagQuickConfig.cbp'

    try {
        foreach ($File in $Manifest.files) {
            $Source = Join-Path $WorkRoot $File.source.Replace('/', '\')
            $Target = Join-Path $WebRoot $File.target.Replace('/', '\')
            New-Item -ItemType Directory -Path (Split-Path -Parent $Target) -Force | Out-Null
            Copy-Item -LiteralPath $Source -Destination $Target -Force
            if ((Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash -ne $File.sha256) {
                throw "Hash sau deploy khong khop: $($File.target)."
            }
        }
        New-Item -ItemType Directory -Path (Split-Path -Parent $DirectTarget) -Force | Out-Null
        Copy-Item -LiteralPath $DirectEntry -Destination $DirectTarget -Force
        if ((Get-FileHash -LiteralPath $DirectTarget -Algorithm SHA256).Hash -ne $Manifest.entries[0].sha256) {
            throw 'Hash direct bagQuickConfig.cbp sau deploy khong khop.'
        }
    }
    catch {
        foreach ($File in $Manifest.files) {
            $Backup = Join-Path $BackupRoot $File.target.Replace('/', '_')
            if (Test-Path -LiteralPath $Backup) {
                Copy-Item -LiteralPath $Backup -Destination (Join-Path $WebRoot $File.target.Replace('/', '\')) -Force
            }
        }
        $DirectBackup = Join-Path $BackupRoot 'data_lang_zh-cn_bagQuickConfig.cbp'
        if (Test-Path -LiteralPath $DirectBackup) {
            Copy-Item -LiteralPath $DirectBackup -Destination $DirectTarget -Force
        }
        throw
    }

    Write-Output "VERSION=$Version"
    Write-Output "BACKUP=$BackupRoot"
    foreach ($File in $Manifest.files) {
        $Target = Join-Path $WebRoot $File.target.Replace('/', '\')
        Write-Output ($File.target + '=' + (Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash)
    }
    Write-Output ('data/lang/zh-cn/bagQuickConfig.cbp=' + (Get-FileHash -LiteralPath $DirectTarget -Algorithm SHA256).Hash)
}
finally {
    Remove-Item -LiteralPath $WorkRoot -Recurse -Force -ErrorAction SilentlyContinue
}
