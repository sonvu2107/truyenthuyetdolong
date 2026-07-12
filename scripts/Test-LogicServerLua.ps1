[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$LanguageRoot,

    [string]$LuaCompiler = 'luac.exe',

    [string[]]$File = @('NormalTalk.txt', 'EntityName.txt', 'Quest.txt', 'Item.txt')
)

$ErrorActionPreference = 'Stop'

function Resolve-LuaCompiler {
    param([Parameter(Mandatory = $true)][string]$Command)

    if (Test-Path -LiteralPath $Command -PathType Leaf) {
        return (Resolve-Path -LiteralPath $Command).Path
    }
    $resolved = Get-Command -Name $Command -CommandType Application -ErrorAction SilentlyContinue
    if (-not $resolved) {
        throw "Không tìm thấy Lua compiler: $Command"
    }
    return $resolved.Source
}

function Copy-Utf8WithoutBom {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $bytes = [System.IO.File]::ReadAllBytes($Source)
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        $bytes = $bytes[3..($bytes.Length - 1)]
    }
    [System.IO.File]::WriteAllBytes($Destination, $bytes)
}

$root = (Resolve-Path -LiteralPath $LanguageRoot -ErrorAction Stop).Path
$compiler = Resolve-LuaCompiler -Command $LuaCompiler
$compilerVersion = ((& $compiler -v 2>&1) -join [Environment]::NewLine)
if ($compilerVersion -notmatch 'Lua 5\.1') {
    throw "Lua compiler phải tương thích Lua 5.1. Nhận được: $compilerVersion"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('ahtl-lua51-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

try {
    $results = @()
    foreach ($name in $File) {
        if ($name -notmatch '^(NormalTalk|EntityName|Quest|Item)\.txt$') {
            throw "File ngoài phạm vi ngôn ngữ LogicServer: $name"
        }

        $source = Join-Path $root $name
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
            throw "Thiếu file Lua: $source"
        }

        $staged = Join-Path $tempRoot $name
        Copy-Utf8WithoutBom -Source $source -Destination $staged

        $previousErrorAction = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        $output = & $compiler -p $staged 2>&1
        $exitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousErrorAction

        $results += [pscustomobject]@{
            File = $name
            ExitCode = $exitCode
            Output = ($output -join [Environment]::NewLine)
        }
    }

    $failed = @($results | Where-Object { $_.ExitCode -ne 0 })
    if ($failed.Count -gt 0) {
        $detail = $failed | ForEach-Object { "$($_.File): $($_.Output)" }
        throw ("Lua 5.1 syntax check failed:" + [Environment]::NewLine + ($detail -join [Environment]::NewLine))
    }

    Write-Output "Lua 5.1 syntax OK: $($results.Count) file(s)."
}
finally {
    Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
}
