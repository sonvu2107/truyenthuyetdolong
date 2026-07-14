[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot',
    [string]$ApacheRoot = 'C:\GPHANTL\server\GPHweb\Apache2'
)

$ErrorActionPreference = 'Stop'
$Version = '20260714itemcache2'
$repoBase = "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/$Revision"
$workRoot = Join-Path $env:TEMP ('ahtl-global-cbp-cache-' + [Guid]::NewGuid().ToString('N'))
$backupRoot = Join-Path $WebRoot ('_deploy_backups\global_cbp_cache_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))

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

$gameConfig = Join-Path $WebRoot 'game\GameConfig.php'
$djrm = Join-Path $WebRoot 'game\djrm.php'
$httpdConf = Join-Path $ApacheRoot 'conf\httpd.conf'
$httpd = Join-Path $ApacheRoot 'bin\httpd.exe'

function Restart-AhtlApache {
    param([string]$HttpdPath, [string]$ConfigPath)
    $processes = @(Get-CimInstance Win32_Process | Where-Object {
        $_.Name -eq 'httpd.exe' -and $_.ExecutablePath -eq $HttpdPath
    })
    if ($processes.Count -eq 0) {
        throw 'Khong tim thay process Apache cua GPHweb de khoi dong lai.'
    }
    foreach ($process in $processes | Sort-Object ProcessId -Descending) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    Start-Process -FilePath $HttpdPath -ArgumentList @('-f', $ConfigPath) -WorkingDirectory (Split-Path -Parent $HttpdPath) -WindowStyle Hidden
    $deadline = (Get-Date).AddSeconds(10)
    do {
        Start-Sleep -Milliseconds 500
        $running = @(Get-CimInstance Win32_Process | Where-Object {
            $_.Name -eq 'httpd.exe' -and $_.ExecutablePath -eq $HttpdPath
        })
    } while ($running.Count -eq 0 -and (Get-Date) -lt $deadline)
    if ($running.Count -eq 0) {
        throw 'Apache khong khoi dong lai sau khi dung process cu.'
    }
}

try {
    foreach ($path in @($gameConfig, $djrm, $httpdConf, $httpd, (Join-Path $ApacheRoot 'modules\mod_headers.so'))) {
        if (-not (Test-Path -LiteralPath $path)) { throw "Khong tim thay file bat buoc: $path" }
    }

    $downloadedGameConfig = Join-Path $workRoot 'GameConfig.php'
    Get-GitHubFile -RelativePath 'assets/game/GameConfig.php' -Destination $downloadedGameConfig
    if (-not (Test-AsciiToken -Path $downloadedGameConfig -Token "cbppack=1&ver=$Version&nocache=1")) {
        throw 'GameConfig tu GitHub khong co cache key du kien.'
    }

    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    Copy-Item -LiteralPath $gameConfig -Destination (Join-Path $backupRoot 'GameConfig.php') -Force
    Copy-Item -LiteralPath $djrm -Destination (Join-Path $backupRoot 'djrm.php') -Force
    Copy-Item -LiteralPath $httpdConf -Destination (Join-Path $backupRoot 'httpd.conf') -Force

    try {
        Copy-Item -LiteralPath $downloadedGameConfig -Destination $gameConfig -Force

        if (-not (Test-AsciiToken -Path $djrm -Token "AHTL_GLOBAL_CBP_CACHE_$Version")) {
            $lineEnding = if (Test-AsciiToken -Path $djrm -Token "`r`n") { "`r`n" } else { "`n" }
            Replace-AsciiOnce -Path $djrm -Needle 'session_start();' -Replacement ("session_start();" + $lineEnding + "header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');" + $lineEnding + "header('Pragma: no-cache');" + $lineEnding + "header('Expires: Thu, 01 Jan 1970 00:00:00 GMT');")
            $flashOverride = "// AHTL_GLOBAL_CBP_CACHE_$Version" + $lineEnding + "if (count(`$plainFlashVars) > 0)" + $lineEnding + "{" + $lineEnding + "    `$plainFlashVars['cbppack'] = '1';" + $lineEnding + "    `$plainFlashVars['ver'] = '$Version';" + $lineEnding + "    `$plainFlashVars['nocache'] = '1';" + $lineEnding + "}" + $lineEnding + $lineEnding + "if (!`$v || !`$sn)" + $lineEnding + "{"
            Replace-AsciiOnce -Path $djrm -Needle ("if (!`$v || !`$sn)" + $lineEnding + "{") -Replacement $flashOverride
        }

        if (-not (Test-AsciiToken -Path $httpdConf -Token "AHTL_GLOBAL_CBP_CACHE_$Version")) {
            if (Test-AsciiToken -Path $httpdConf -Token '#LoadModule headers_module modules/mod_headers.so') {
                Replace-AsciiOnce -Path $httpdConf -Needle '#LoadModule headers_module modules/mod_headers.so' -Replacement 'LoadModule headers_module modules/mod_headers.so'
            }
            elseif (-not (Test-AsciiToken -Path $httpdConf -Token 'LoadModule headers_module modules/mod_headers.so')) {
                throw 'Khong the bat mod_headers: khong tim thay dong LoadModule du kien.'
            }
            $apacheRules = (@'

# AHTL_GLOBAL_CBP_CACHE___VERSION__ begin
<IfModule headers_module>
    <LocationMatch "^/(?:client_shell\.html|GameFrame\.swf|GPH\.html|GPH\.php|data/lang/zh-cn/(?:[^/]+\.cbp|cbp\.zip))$">
        Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
        Header set Pragma "no-cache"
        Header set Expires "Thu, 01 Jan 1970 00:00:00 GMT"
    </LocationMatch>
</IfModule>
# AHTL_GLOBAL_CBP_CACHE___VERSION__ end
'@ -replace '__VERSION__', [string]$Version)
            [IO.File]::AppendAllText($httpdConf, $apacheRules, [Text.Encoding]::ASCII)
        }

        & $httpd -t -f $httpdConf
        if ($LASTEXITCODE -ne 0) { throw 'Apache config test that bai.' }
        Restart-AhtlApache -HttpdPath $httpd -ConfigPath $httpdConf
    }
    catch {
        Copy-Item -LiteralPath (Join-Path $backupRoot 'GameConfig.php') -Destination $gameConfig -Force
        Copy-Item -LiteralPath (Join-Path $backupRoot 'djrm.php') -Destination $djrm -Force
        Copy-Item -LiteralPath (Join-Path $backupRoot 'httpd.conf') -Destination $httpdConf -Force
        Restart-AhtlApache -HttpdPath $httpd -ConfigPath $httpdConf
        throw
    }

    Write-Output "Da ap cache bust toan cuc $Version; backup: $backupRoot"
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
