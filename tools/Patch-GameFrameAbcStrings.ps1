param(
    [Parameter(Mandatory = $true)]
    [Alias('Input')]
    [string]$FwsInput,

    [Parameter(Mandatory = $true)]
    [string]$OriginalSource,

    [Parameter(Mandatory = $true)]
    [string]$PatchedSource,

    [Parameter(Mandatory = $true)]
    [string]$PatchReport,

    [Parameter(Mandatory = $true)]
    [Alias('Output')]
    [string]$FwsOutput,

    [string]$CompressedOutput,

    [string]$FfdecJar,

    [string]$Report,

    [string[]]$SkipKey = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Read-Utf8([string]$Path) {
    [IO.File]::ReadAllText((Resolve-Path -LiteralPath $Path), [Text.UTF8Encoding]::new($false))
}

function Write-Utf8([string]$Path, [string]$Content) {
    $parent = Split-Path -Parent $Path
    if ($parent) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
    [IO.File]::WriteAllText($Path, $Content, [Text.UTF8Encoding]::new($false))
}

function Get-Assignment([string]$Content, [string]$Key) {
    $pattern = '(?m)^\s*' + [regex]::Escape($Key) + '\s*=\s*(?<value>[^\r\n]*);\r?$'
    $matches = [regex]::Matches($Content, $pattern)
    if ($matches.Count -ne 1) { throw "Không tìm thấy đúng một dòng nguồn $Key (thực tế: $($matches.Count))." }
    $matches[0].Groups['value'].Value
}

function Decode-AsString([string]$Value) {
    $builder = [Text.StringBuilder]::new()
    for ($index = 0; $index -lt $Value.Length; $index++) {
        $char = $Value[$index]
        if ($char -ne '\') { [void]$builder.Append($char); continue }
        if ($index + 1 -ge $Value.Length) { throw 'Escape ActionScript bị thiếu ký tự.' }
        $index++
        $escape = $Value[$index]
        switch ($escape) {
            'n' { [void]$builder.Append("`n") }
            'r' { [void]$builder.Append("`r") }
            't' { [void]$builder.Append("`t") }
            'b' { [void]$builder.Append([char]8) }
            'f' { [void]$builder.Append([char]12) }
            'u' {
                if ($index + 4 -ge $Value.Length) { throw 'Escape Unicode ActionScript bị thiếu 4 chữ số.' }
                $hex = $Value.Substring($index + 1, 4)
                [void]$builder.Append([char][Convert]::ToInt32($hex, 16))
                $index += 4
            }
            default { [void]$builder.Append($escape) }
        }
    }
    $builder.ToString()
}

function Decode-AsExpression([string]$Expression) {
    $parts = [regex]::Matches($Expression, '"(?<value>(?:\\.|[^"\\])*)"')
    if ($parts.Count -eq 0) { throw "Không đọc được literal ActionScript: $Expression" }
    (($parts | ForEach-Object { Decode-AsString $_.Groups['value'].Value }) -join '')
}

function Get-U30([byte[]]$Bytes, [int]$Start, [ref]$End) {
    $value = 0
    $shift = 0
    $position = $Start
    while ($position -lt $Bytes.Length -and $position -lt ($Start + 5)) {
        $byte = $Bytes[$position]
        $value = $value -bor (($byte -band 0x7F) -shl $shift)
        $position++
        if (($byte -band 0x80) -eq 0) {
            $End.Value = $position
            return $value
        }
        $shift += 7
    }
    throw 'U30 không hợp lệ.'
}

function Encode-U30([int]$Value) {
    if ($Value -lt 0 -or $Value -gt 0x3FFFFFFF) { throw "U30 ngoài phạm vi: $Value" }
    $result = [Collections.Generic.List[byte]]::new()
    do {
        $byte = $Value -band 0x7F
        $Value = $Value -shr 7
        if ($Value -ne 0) { $byte = $byte -bor 0x80 }
        $result.Add([byte]$byte)
    } while ($Value -ne 0)
    return ,$result.ToArray()
}

function Find-Occurrences([byte[]]$Bytes, [byte[]]$Needle) {
    $found = [Collections.Generic.List[int]]::new()
    if ($Needle.Length -eq 0) { throw 'Không thể tìm chuỗi rỗng trong ABC.' }
    $latin1 = [Text.Encoding]::GetEncoding(28591)
    $haystack = $latin1.GetString($Bytes)
    $needleText = $latin1.GetString($Needle)
    $offset = 0
    while (($index = $haystack.IndexOf($needleText, $offset, [StringComparison]::Ordinal)) -ge 0) {
        $found.Add($index)
        $offset = $index + $needleText.Length
    }
    return ,$found.ToArray()
}

function Get-LengthPrefixStart([byte[]]$Bytes, [int]$TextStart, [int]$TextLength) {
    for ($start = [Math]::Max(0, $TextStart - 5); $start -lt $TextStart; $start++) {
        $end = 0
        try { $length = Get-U30 $Bytes $start ([ref]$end) } catch { continue }
        if ($end -eq $TextStart -and $length -eq $TextLength) { return $start }
    }
    throw "Không tìm thấy độ dài U30 cho chuỗi tại offset $TextStart."
}

function Get-SwfTags([byte[]]$Bytes) {
    if ($Bytes.Length -lt 13 -or [Text.Encoding]::ASCII.GetString($Bytes, 0, 3) -ne 'FWS') {
        throw 'Không đọc được header FWS.'
    }

    $rectBits = $Bytes[8] -shr 3
    $rectLength = [int][Math]::Ceiling((5 + (4 * $rectBits)) / 8.0)
    $position = 8 + $rectLength + 4 # RECT + frame rate + frame count
    $tags = [Collections.Generic.List[object]]::new()
    while ($position -lt $Bytes.Length) {
        if ($position + 2 -gt $Bytes.Length) { throw 'SWF bị thiếu tag header.' }
        $tagHeader = [BitConverter]::ToUInt16($Bytes, $position)
        $code = $tagHeader -shr 6
        $shortLength = $tagHeader -band 0x3F
        $isLong = $shortLength -eq 0x3F
        $lengthOffset = $null
        if ($isLong) {
            if ($position + 6 -gt $Bytes.Length) { throw 'SWF bị thiếu long tag length.' }
            $dataLength = [int][BitConverter]::ToUInt32($Bytes, $position + 2)
            $dataStart = $position + 6
            $lengthOffset = $position + 2
        } else {
            $dataLength = [int]$shortLength
            $dataStart = $position + 2
        }
        $dataEnd = $dataStart + $dataLength
        if ($dataEnd -gt $Bytes.Length) { throw "Tag SWF $code vượt quá cuối tệp." }
        $tags.Add([PSCustomObject]@{
            code = $code
            headerStart = $position
            dataStart = $dataStart
            dataEnd = $dataEnd
            dataLength = $dataLength
            isLong = $isLong
            lengthOffset = $lengthOffset
        })
        $position = $dataEnd
        if ($code -eq 0) { break }
    }
    return $tags.ToArray()
}

function Get-DoAbcTagForRange([byte[]]$Bytes, [int]$Start, [int]$End) {
    # DoABC has tag code 82. A string-pool replacement must remain inside its
    # payload; otherwise changing its byte length corrupts an unrelated tag.
    $tag = Get-SwfTags $Bytes | Where-Object {
        $_.code -eq 82 -and $Start -ge $_.dataStart -and $End -le $_.dataEnd
    } | Select-Object -First 1
    if (-not $tag) { throw "Hằng chuỗi tại offset $Start vượt ngoài DoABC." }
    if (-not $tag.isLong) { throw 'DoABC dùng short tag length, không hỗ trợ vá thay đổi kích thước.' }
    return $tag
}

function Replace-StringConstant([byte[]]$Bytes, [string]$Source, [string]$Target, [string]$Key) {
    $sourceBytes = [Text.Encoding]::UTF8.GetBytes($Source)
    $targetBytes = [Text.Encoding]::UTF8.GetBytes($Target)
    [int[]]$occurrences = Find-Occurrences $Bytes $sourceBytes
    if ($occurrences.Count -lt 1) { throw "Không tìm thấy hằng chuỗi ABC cho $Key." }

    $validPrefixes = [Collections.Generic.List[int]]::new()
    foreach ($occurrence in $occurrences) {
        try {
            $prefix = Get-LengthPrefixStart $Bytes $occurrence $sourceBytes.Length
            Get-DoAbcTagForRange $Bytes $prefix ($occurrence + $sourceBytes.Length) | Out-Null
            $validPrefixes.Add($prefix)
        } catch { }
    }
    $prefixes = @($validPrefixes | Sort-Object -Descending)
    if ($prefixes.Count -lt 1) { throw "Không tìm thấy hằng chuỗi ABC độc lập cho $Key." }
    foreach ($prefix in $prefixes) {
        $textStart = $prefix + (Encode-U30 $sourceBytes.Length).Length
        $textEnd = $textStart + $sourceBytes.Length
        $tag = Get-DoAbcTagForRange $Bytes $prefix $textEnd
        $delta = $targetBytes.Length - $sourceBytes.Length
        if ($delta -ne 0) {
            $newTagLength = $tag.dataLength + $delta
            if ($newTagLength -lt 0) { throw "Độ dài DoABC không hợp lệ cho $Key." }
            [Array]::Copy([BitConverter]::GetBytes([uint32]$newTagLength), 0, $Bytes, $tag.lengthOffset, 4)
        }
        $stream = [IO.MemoryStream]::new()
        $stream.Write($Bytes, 0, $prefix)
        $lengthBytes = Encode-U30 $targetBytes.Length
        $stream.Write($lengthBytes, 0, $lengthBytes.Length)
        $stream.Write($targetBytes, 0, $targetBytes.Length)
        $stream.Write($Bytes, $textEnd, $Bytes.Length - $textEnd)
        $Bytes = $stream.ToArray()
    }
    [PSCustomObject]@{ bytes = $Bytes; occurrences = $prefixes.Count }
}

$original = Read-Utf8 $OriginalSource
$patched = Read-Utf8 $PatchedSource
$keys = (Get-Content -LiteralPath $PatchReport -Raw -Encoding utf8 | ConvertFrom-Json).replacements
if (-not $keys -or $keys.Count -lt 1) { throw 'Patch report không có key cần áp.' }

$changes = [ordered]@{}
$skipped = @()
foreach ($key in $keys) {
    if ($key -eq 'diamondGame[33]' -or $SkipKey -contains $key) {
        $skipped += $key
        continue
    }
    $sourceExpression = Get-Assignment $original $key
    $targetExpression = Get-Assignment $patched $key
    $source = Decode-AsExpression $sourceExpression
    $target = Decode-AsExpression $targetExpression
    if ($source -eq $target) { continue }

    $sourceLiterals = @([regex]::Matches($sourceExpression, '"(?<value>(?:\\.|[^"\\])*)"') | ForEach-Object { Decode-AsString $_.Groups['value'].Value })
    $targetLiterals = @([regex]::Matches($targetExpression, '"(?<value>(?:\\.|[^"\\])*)"') | ForEach-Object { Decode-AsString $_.Groups['value'].Value })
    if ($sourceLiterals.Count -gt 1 -and $sourceLiterals.Count -eq $targetLiterals.Count) {
        for ($index = 0; $index -lt $sourceLiterals.Count; $index++) {
            if ($sourceLiterals[$index] -ceq $targetLiterals[$index]) { continue }
            if ($changes.Contains($sourceLiterals[$index]) -and $changes[$sourceLiterals[$index]].target -cne $targetLiterals[$index]) { throw "Một hằng chuỗi nguồn có hai target khác nhau: $key." }
            $changes[$sourceLiterals[$index]] = @{ key = "$key#$index"; target = $targetLiterals[$index] }
        }
        continue
    }
    if ($changes.Contains($source) -and $changes[$source].target -cne $target) {
        throw "Một hằng chuỗi nguồn có hai target khác nhau: $key."
    }
    $changes[$source] = @{ key = $key; target = $target }
}

$bytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $FwsInput))
if ($bytes.Length -lt 8 -or [Text.Encoding]::ASCII.GetString($bytes, 0, 3) -ne 'FWS') {
    throw 'Input phải là SWF đã giải nén dạng FWS.'
}

$applied = @()
foreach ($source in $changes.Keys) {
    $entry = $changes[$source]
    $result = Replace-StringConstant $bytes $source $entry.target $entry.key
    $bytes = $result.bytes
    $applied += [ordered]@{ key = $entry.key; occurrences = $result.occurrences; sourceLength = ([Text.Encoding]::UTF8.GetByteCount($source)); targetLength = ([Text.Encoding]::UTF8.GetByteCount($entry.target)) }
}

$sizeBytes = [BitConverter]::GetBytes([uint32]$bytes.Length)
[Array]::Copy($sizeBytes, 0, $bytes, 4, 4)
$parent = Split-Path -Parent $FwsOutput
if ($parent) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
[IO.File]::WriteAllBytes($FwsOutput, $bytes)
if (-not [IO.File]::Exists($FwsOutput)) { throw "Không ghi được FWS đầu ra: $FwsOutput" }

if ($CompressedOutput -or $FfdecJar) {
    if (-not $CompressedOutput -or -not $FfdecJar) { throw 'CompressedOutput và FfdecJar phải được truyền cùng nhau.' }
    $fwsAbsolute = (Resolve-Path -LiteralPath $FwsOutput).Path
    $compressedAbsolute = [IO.Path]::GetFullPath($CompressedOutput)
    $ffdecAbsolute = (Resolve-Path -LiteralPath $FfdecJar).Path
    & java '-Xmx1536m' '-Djna.nosys=true' '-Dsun.java2d.uiScale=1.0' -jar $ffdecAbsolute -compress zlib $fwsAbsolute $compressedAbsolute
    if ($LASTEXITCODE -ne 0 -or -not [IO.File]::Exists($compressedAbsolute)) {
        throw "Không nén được SWF đầu ra: $CompressedOutput"
    }
}

if ($Report) {
    $payload = [ordered]@{
        input = (Resolve-Path -LiteralPath $FwsInput).Path
        output = (Resolve-Path -LiteralPath $FwsOutput).Path
        compressedOutput = if ($CompressedOutput) { (Resolve-Path -LiteralPath $CompressedOutput).Path } else { $null }
        keyCount = $keys.Count
        skippedKeys = $skipped
        uniqueStringCount = $changes.Count
        applied = $applied
    }
    Write-Utf8 $Report (($payload | ConvertTo-Json -Depth 5) + "`n")
}

Write-Host "Đã vá $($keys.Count) key / $($changes.Count) hằng chuỗi ABC vào $FwsOutput"
