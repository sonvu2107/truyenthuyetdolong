[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot'
)

$ErrorActionPreference = 'Stop'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$manifestPath = 'assets/manifest-direct-item-localization-20260714.json'
$workRoot = Join-Path $env:TEMP ('ahtl-direct-item-lang-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $WebRoot ('_deploy_backups\direct_item_localization_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

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

function Replace-AsciiOnce {
    param([string]$Path, [string]$Needle, [string]$Replacement)
    [byte[]]$data = [IO.File]::ReadAllBytes($Path)
    [byte[]]$old = [Text.Encoding]::ASCII.GetBytes($Needle)
    [byte[]]$new = [Text.Encoding]::ASCII.GetBytes($Replacement)
    $matchIndex = -1
    $matchCount = 0
    for ($index = 0; $index -le $data.Length - $old.Length; $index++) {
        $same = $true
        for ($offset = 0; $offset -lt $old.Length; $offset++) {
            if ($data[$index + $offset] -ne $old[$offset]) { $same = $false; break }
        }
        if ($same) { $matchIndex = $index; $matchCount++ }
    }
    if ($matchCount -ne 1) {
        throw "Mau thay the trong $Path phai xuat hien dung mot lan, thuc te: $matchCount."
    }
    [byte[]]$output = New-Object byte[] ($data.Length - $old.Length + $new.Length)
    [Array]::Copy($data, 0, $output, 0, $matchIndex)
    [Array]::Copy($new, 0, $output, $matchIndex, $new.Length)
    [Array]::Copy($data, $matchIndex + $old.Length, $output, $matchIndex + $new.Length, $data.Length - $matchIndex - $old.Length)
    [IO.File]::WriteAllBytes($Path, $output)
}

try {
    $manifestFile = Join-Path $workRoot 'manifest.json'
    Get-GitHubFile -RelativePath $manifestPath -Destination $manifestFile
    $manifest = Get-Content -LiteralPath $manifestFile -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.version -ne '20260714directitem1' -or
        $manifest.archive.source -ne 'assets/lang/zh-cn/cbp.zip' -or
        $manifest.entry.name -ne 'stditems.cbp' -or
        $manifest.entry.target -ne 'data/lang/zh-cn/stditems.cbp' -or
        $manifest.legacy_loaders.Count -ne 2) {
        throw 'Manifest localization item truc tiep khong dung pham vi.'
    }

    $archive = Join-Path $workRoot $manifest.archive.source.Replace('/', '\')
    Get-GitHubFile -RelativePath $manifest.archive.source -Destination $archive
    if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash -ne $manifest.archive.sha256) {
        throw 'Sai SHA-256 cua cbp.zip.'
    }

    $itemTarget = Join-Path $WebRoot $manifest.entry.target.Replace('/', '\')
    $gphPhp = Join-Path $WebRoot 'GPH.php'
    $gphHtml = Join-Path $WebRoot 'GPH.html'
    foreach ($path in @($itemTarget, $gphPhp, $gphHtml)) {
        if (-not (Test-Path -LiteralPath $path)) { throw "Khong tim thay file dich: $path" }
    }
    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    Copy-Item -LiteralPath $itemTarget -Destination (Join-Path $backupRoot 'stditems.cbp') -Force
    Copy-Item -LiteralPath $gphPhp -Destination (Join-Path $backupRoot 'GPH.php') -Force
    Copy-Item -LiteralPath $gphHtml -Destination (Join-Path $backupRoot 'GPH.html') -Force

    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $zip = [IO.Compression.ZipFile]::OpenRead($archive)
    try {
        $entry = $zip.Entries | Where-Object { $_.FullName -ieq $manifest.entry.name } | Select-Object -First 1
        if ($null -eq $entry) { throw 'Khong tim thay stditems.cbp trong cbp.zip.' }
        $input = $entry.Open()
        try {
            $output = [IO.File]::Open($itemTarget, [IO.FileMode]::Create, [IO.FileAccess]::Write)
            try { $input.CopyTo($output) } finally { $output.Dispose() }
        } finally { $input.Dispose() }
    } finally { $zip.Dispose() }
    if ((Get-FileHash -LiteralPath $itemTarget -Algorithm SHA256).Hash -ne $manifest.entry.sha256) {
        throw 'Hash stditems.cbp sau deploy khong khop.'
    }

    $phpReplacement = "cbppack:0,`r`n" + "`t`tver:`"20260714directitem1`",`r`n" + "`t`tnocache:1,"
    Replace-AsciiOnce -Path $gphPhp -Needle 'cbppack:0,' -Replacement $phpReplacement
    Replace-AsciiOnce -Path $gphHtml -Needle '&cbppack=0&srvportmax=13000&srvid=1&ip1=123456&spid=937&' -Replacement '&cbppack=0&ver=20260714directitem1&nocache=1&srvportmax=13000&srvid=1&ip1=123456&spid=937&'
    Write-Output "Da deploy item truc tiep $($manifest.version); backup: $backupRoot"
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
