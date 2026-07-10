[CmdletBinding()]
param(
    [string]$HostName = '180.93.244.31',
    [int]$Port = 13000,
    [ValidateRange(1, 100)]
    [int]$Count = 12,
    [int]$TimeoutMilliseconds = 700
)

$ErrorActionPreference = 'Stop'

function Get-BitReflection {
    param([uint32]$Value, [int]$Bits)

    [uint32]$result = 0
    for ($index = 0; $index -lt $Bits; $index++) {
        if (($Value -band 1) -ne 0) {
            $result = $result -bor ([uint32]1 -shl ($Bits - 1 - $index))
        }
        $Value = $Value -shr 1
    }
    return $result
}

function Get-AhtlCrc16 {
    param([byte[]]$Bytes)

    [uint32[]]$table = New-Object 'uint32[]' 256
    for ($entry = 0; $entry -lt 256; $entry++) {
        [uint32]$crcEntry = [uint32]($entry -shl 8)
        for ($bit = 0; $bit -lt 8; $bit++) {
            if (($crcEntry -band 0x8000) -ne 0) {
                $crcEntry = [uint32]((([uint64]$crcEntry -shl 1) % 4294967296) -bxor 0x1021)
            } else {
                $crcEntry = [uint32](([uint64]$crcEntry -shl 1) % 4294967296)
            }
        }
        $table[$entry] = $crcEntry
    }

    [uint32]$crc = 0
    foreach ($value in $Bytes) {
        $reflected = Get-BitReflection -Value $value -Bits 8
        $tableIndex = [int](($reflected -bxor ($crc -shr 8)) -band 0xFF)
        $crc = [uint32]($table[$tableIndex] -bxor (([uint64]$crc -shl 8) % 4294967296))
    }
    return [uint16]((Get-BitReflection -Value $crc -Bits 16) -band 0xFFFF)
}

$results = @()
for ($attempt = 1; $attempt -le $Count; $attempt++) {
    $client = $null
    try {
        $client = New-Object Net.Sockets.TcpClient
        $connect = $client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $connect.AsyncWaitHandle.WaitOne($TimeoutMilliseconds)) {
            throw 'connect timeout'
        }
        $client.EndConnect($connect)
        $client.ReceiveTimeout = $TimeoutMilliseconds
        $client.SendTimeout = $TimeoutMilliseconds
        $stream = $client.GetStream()

        [uint32]$clientSalt = Get-Random -Minimum 1 -Maximum ([int64][uint32]::MaxValue)
        $clientSaltBytes = [BitConverter]::GetBytes($clientSalt)
        $stream.Write($clientSaltBytes, 0, 4)
        $stream.Flush()

        $serverSaltBytes = New-Object byte[] 4
        $read = 0
        while ($read -lt 4) {
            $part = $stream.Read($serverSaltBytes, $read, 4 - $read)
            if ($part -eq 0) { throw 'server closed before salt' }
            $read += $part
        }
        [uint32]$serverSalt = [BitConverter]::ToUInt32($serverSaltBytes, 0)
        [uint32]$key = [uint32]((([uint64]($clientSalt -bxor $serverSalt)) + 45786217832) % 4294967296)
        [uint16]$checkKey = Get-AhtlCrc16 -Bytes ([BitConverter]::GetBytes($key))
        $checkBytes = [BitConverter]::GetBytes($checkKey)
        $stream.Write($checkBytes, 0, 2)
        $stream.Flush()

        $status = 'PASS'
        $detail = 'connection remained open after dynamic CRC'
        $probeBuffer = New-Object byte[] 1
        $probeRead = $stream.BeginRead($probeBuffer, 0, 1, $null, $null)
        if ($probeRead.AsyncWaitHandle.WaitOne($TimeoutMilliseconds)) {
            $probeCount = $stream.EndRead($probeRead)
            if ($probeCount -eq 0) {
                $status = 'FAIL'
                $detail = 'Gate closed after CRC'
            } else {
                $detail = "Gate returned byte=$($probeBuffer[0])"
            }
        }

        $results += [pscustomobject]@{
            Attempt = $attempt
            Status = $status
            ClientSalt = $clientSalt
            ServerSalt = $serverSalt
            CheckKey = $checkKey
            Detail = $detail
        }
    } catch {
        $results += [pscustomobject]@{
            Attempt = $attempt
            Status = 'FAIL'
            ClientSalt = $null
            ServerSalt = $null
            CheckKey = $null
            Detail = "$($_.Exception.Message) line=$($_.InvocationInfo.ScriptLineNumber)"
        }
    } finally {
        if ($client) { $client.Close() }
    }
    Start-Sleep -Milliseconds 100
}

$results | Format-Table -AutoSize -Wrap
$passed = @($results | Where-Object Status -eq 'PASS').Count
Write-Output "SUMMARY passed=$passed total=$Count"
if ($passed -ne $Count) { exit 1 }
