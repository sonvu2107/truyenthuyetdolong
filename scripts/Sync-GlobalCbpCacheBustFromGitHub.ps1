[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Revision,
    [string]$WebRoot = 'C:\GPHANTL\server\GPHweb\wwwroot',
    [string]$ApacheRoot = 'C:\GPHANTL\server\GPHweb\Apache2',
    [switch]$DynamicOnly
)

$ErrorActionPreference = 'Stop'
$Version = '20260714itemcache5'
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
    $processes = @(Get-WmiObject Win32_Process | Where-Object {
        $_.Name -eq 'httpd.exe' -and (
            $_.ExecutablePath -like '*\GPHweb\Apache2\bin\httpd.exe' -or
            $_.CommandLine -like '*GPHweb\Apache2\conf\httpd.conf*'
        )
    })
    if ($processes.Count -eq 0) {
        throw 'Khong tim thay process Apache cua GPHweb de khoi dong lai.'
    }
    foreach ($process in $processes | Sort-Object ProcessId -Descending) {
        Stop-Process -Id $process.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
    $apacheRoot = Split-Path -Parent (Split-Path -Parent $HttpdPath)
    $commandLine = '"' + $HttpdPath + '" -d "' + $apacheRoot + '" -f "' + $ConfigPath + '"'
    $created = ([wmiclass]'Win32_Process').Create($commandLine)
    if ($created.ReturnValue -ne 0) {
        throw "Khong tao duoc process Apache, ma WMI: $($created.ReturnValue)."
    }
    $deadline = (Get-Date).AddSeconds(10)
    do {
        Start-Sleep -Milliseconds 500
        $running = @(Get-WmiObject Win32_Process | Where-Object {
            $_.Name -eq 'httpd.exe' -and (
                $_.ExecutablePath -like '*\GPHweb\Apache2\bin\httpd.exe' -or
                $_.CommandLine -like '*GPHweb\Apache2\conf\httpd.conf*'
            )
        })
        $listening = (netstat -ano | Select-String ':81\s+.*LISTENING').Count -gt 0
    } while (($running.Count -lt 2 -or -not $listening) -and (Get-Date) -lt $deadline)
    if ($running.Count -lt 2 -or -not $listening) {
        throw 'Apache khong khoi dong lai sau khi dung process cu.'
    }
}

function Test-AhtlApacheConfig {
    param([string]$HttpdPath, [string]$ConfigPath)
    $apacheRoot = Split-Path -Parent (Split-Path -Parent $HttpdPath)
    $startInfo = New-Object Diagnostics.ProcessStartInfo
    $startInfo.FileName = $HttpdPath
    $startInfo.Arguments = '-t -d "' + $apacheRoot + '" -f "' + $ConfigPath + '"'
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.CreateNoWindow = $true
    $process = [Diagnostics.Process]::Start($startInfo)
    $process.WaitForExit()
    $output = $process.StandardOutput.ReadToEnd() + $process.StandardError.ReadToEnd()
    if ($process.ExitCode -ne 0) {
        throw "Apache config test that bai: $output"
    }
}

try {
    $requiredPaths = @($gameConfig, $djrm)
    if (-not $DynamicOnly) {
        $requiredPaths += @($httpdConf, $httpd, (Join-Path $ApacheRoot 'modules\mod_headers.so'))
    }
    foreach ($path in $requiredPaths) {
        if (-not (Test-Path -LiteralPath $path)) { throw "Khong tim thay file bat buoc: $path" }
    }

    $downloadedGameConfig = Join-Path $workRoot 'GameConfig.php'
    $downloadedDjrm = Join-Path $workRoot 'djrm.php'
    Get-GitHubFile -RelativePath 'assets/game/GameConfig.php' -Destination $downloadedGameConfig
    Get-GitHubFile -RelativePath 'assets/game/djrm.php' -Destination $downloadedDjrm
    if (-not (Test-AsciiToken -Path $downloadedGameConfig -Token "cbppack=1&ver=$Version&nocache=1")) {
        throw 'GameConfig tu GitHub khong co cache key du kien.'
    }
    if (-not (Test-AsciiToken -Path $downloadedDjrm -Token "AHTL_GLOBAL_CBP_CACHE_$Version") -or
        -not (Test-AsciiToken -Path $downloadedDjrm -Token "ahtlcache=${Version}gf")) {
        throw 'djrm.php tu GitHub khong co cache key du kien.'
    }

    New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
    Copy-Item -LiteralPath $gameConfig -Destination (Join-Path $backupRoot 'GameConfig.php') -Force
    Copy-Item -LiteralPath $djrm -Destination (Join-Path $backupRoot 'djrm.php') -Force
    if (-not $DynamicOnly) {
        Copy-Item -LiteralPath $httpdConf -Destination (Join-Path $backupRoot 'httpd.conf') -Force
    }

    try {
        Copy-Item -LiteralPath $downloadedGameConfig -Destination $gameConfig -Force
        Copy-Item -LiteralPath $downloadedDjrm -Destination $djrm -Force

        if (-not $DynamicOnly) {
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
    <LocationMatch "(?i)^/(?:client_shell\.html|GameFrame\.swf|GPH\.html|GPH\.php|data/lang/zh-cn/(?:[^/]+\.cbp|cbp\.zip))$">
        Header set Cache-Control "no-store, no-cache, must-revalidate, max-age=0"
        Header set Pragma "no-cache"
        Header set Expires "Thu, 01 Jan 1970 00:00:00 GMT"
    </LocationMatch>
</IfModule>
# AHTL_GLOBAL_CBP_CACHE___VERSION__ end
'@ -replace '__VERSION__', [string]$Version)
                [IO.File]::AppendAllText($httpdConf, $apacheRules, [Text.Encoding]::ASCII)
            }

            Test-AhtlApacheConfig -HttpdPath $httpd -ConfigPath $httpdConf
            Restart-AhtlApache -HttpdPath $httpd -ConfigPath $httpdConf
        }
    }
    catch {
        Copy-Item -LiteralPath (Join-Path $backupRoot 'GameConfig.php') -Destination $gameConfig -Force
        Copy-Item -LiteralPath (Join-Path $backupRoot 'djrm.php') -Destination $djrm -Force
        if (-not $DynamicOnly) {
            Copy-Item -LiteralPath (Join-Path $backupRoot 'httpd.conf') -Destination $httpdConf -Force
            Restart-AhtlApache -HttpdPath $httpd -ConfigPath $httpdConf
        }
        throw
    }

    $scope = if ($DynamicOnly) { 'dong (khong restart Apache)' } else { 'toan cuc' }
    Write-Output "Da ap cache bust $scope $Version; backup: $backupRoot"
}
finally {
    Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
}
