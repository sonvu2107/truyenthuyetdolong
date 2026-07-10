[CmdletBinding()]
param(
    [string]$GatePath = 'C:\GPHANTL\server\AHServer\GateServer\Win32\GateServer32_R.exe',
    [string]$WorkingDirectory = 'C:\GPHANTL\server\AHServer\GateServer\Win32',
    [string]$LogPath = 'C:\GPHANTL\tools\gate-wrapper.log'
)

$ErrorActionPreference = 'Stop'
$expectedSha256 = '4B9B9535AC39479EC35BDC3DA862FB59EE546E89099DDEA943ADF39DD3503148'
$patchRva = 0x316B

function Write-WrapperLog {
    param([string]$Message)

    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Message
    Add-Content -LiteralPath $LogPath -Value $line -Encoding UTF8
}

$logDirectory = Split-Path -Parent $LogPath
New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null

if (-not (Test-Path -LiteralPath $GatePath -PathType Leaf)) {
    throw "Khong tim thay GateServer: $GatePath"
}
$hash = (Get-FileHash -LiteralPath $GatePath -Algorithm SHA256).Hash
if ($hash -ne $expectedSha256) {
    throw "GateServer tren dia khong dung ban goc: $hash"
}

if (-not ('Ahtl.NativeMethods' -as [type])) {
    Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

namespace Ahtl
{
    public static class NativeMethods
    {
        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern IntPtr OpenProcess(uint access, bool inheritHandle, int processId);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool ReadProcessMemory(
            IntPtr process, IntPtr address, byte[] buffer, UIntPtr size, out UIntPtr bytesRead);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool WriteProcessMemory(
            IntPtr process, IntPtr address, byte[] buffer, UIntPtr size, out UIntPtr bytesWritten);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool VirtualProtectEx(
            IntPtr process, IntPtr address, UIntPtr size, uint newProtect, out uint oldProtect);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool FlushInstructionCache(IntPtr process, IntPtr address, UIntPtr size);

        [DllImport("kernel32.dll", SetLastError = true)]
        [return: MarshalAs(UnmanagedType.Bool)]
        public static extern bool CloseHandle(IntPtr handle);
    }
}
'@
}

$gate = Get-Process -Name 'GateServer32_R' -ErrorAction SilentlyContinue |
    Sort-Object StartTime |
    Select-Object -First 1
if (-not $gate) {
    Write-WrapperLog 'Starting original GateServer binary.'
    $gate = Start-Process -FilePath $GatePath -WorkingDirectory $WorkingDirectory -PassThru
}

Start-Sleep -Milliseconds 250
$gate.Refresh()
if ($gate.HasExited) {
    throw "GateServer thoat som, exitCode=$($gate.ExitCode)"
}

$processVmOperation = 0x0008
$processVmRead = 0x0010
$processVmWrite = 0x0020
$processQueryInformation = 0x0400
$access = $processVmOperation -bor $processVmRead -bor $processVmWrite -bor $processQueryInformation
$oneByte = New-Object System.UIntPtr -ArgumentList ([uint64]1)
$handle = [Ahtl.NativeMethods]::OpenProcess($access, $false, $gate.Id)
if ($handle -eq [IntPtr]::Zero) {
    throw "OpenProcess that bai, win32=$([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
}

try {
    $address = [IntPtr]($gate.MainModule.BaseAddress.ToInt64() + $patchRva)
    $before = New-Object byte[] 1
    [UIntPtr]$read = [UIntPtr]::Zero
    if (-not [Ahtl.NativeMethods]::ReadProcessMemory($handle, $address, $before, $oneByte, [ref]$read)) {
        throw "ReadProcessMemory that bai, win32=$([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
    }
    if ($before[0] -ne 0x7E -and $before[0] -ne 0xEB) {
        throw ('Byte tai RVA 0x316B khong dung: 0x{0:X2}' -f $before[0])
    }

    if ($before[0] -eq 0x7E) {
        [uint32]$oldProtect = 0
        if (-not [Ahtl.NativeMethods]::VirtualProtectEx($handle, $address, $oneByte, 0x40, [ref]$oldProtect)) {
            throw "VirtualProtectEx that bai, win32=$([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
        }
        try {
            $replacement = [byte[]](0xEB)
            [UIntPtr]$written = [UIntPtr]::Zero
            if (-not [Ahtl.NativeMethods]::WriteProcessMemory($handle, $address, $replacement, $oneByte, [ref]$written)) {
                throw "WriteProcessMemory that bai, win32=$([Runtime.InteropServices.Marshal]::GetLastWin32Error())"
            }
            [void][Ahtl.NativeMethods]::FlushInstructionCache($handle, $address, $oneByte)
        } finally {
            [uint32]$ignoredProtect = 0
            [void][Ahtl.NativeMethods]::VirtualProtectEx(
                $handle, $address, $oneByte, $oldProtect, [ref]$ignoredProtect)
        }
    }

    $after = New-Object byte[] 1
    [UIntPtr]$verified = [UIntPtr]::Zero
    [void][Ahtl.NativeMethods]::ReadProcessMemory($handle, $address, $after, $oneByte, [ref]$verified)
    if ($after[0] -ne 0xEB) {
        throw ('Khong xac minh duoc byte va: 0x{0:X2}' -f $after[0])
    }
    Write-WrapperLog ("Patched Gate PID={0} address=0x{1:X} byte=EB" -f $gate.Id, $address.ToInt64())
} finally {
    [void][Ahtl.NativeMethods]::CloseHandle($handle)
}

$gate.WaitForExit()
Write-WrapperLog ("Gate exited PID={0} exitCode={1}" -f $gate.Id, $gate.ExitCode)
exit 1
