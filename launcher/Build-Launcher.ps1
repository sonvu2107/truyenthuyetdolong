param(
    [string]$OutputPath = (Join-Path $PSScriptRoot 'AHTL_Launcher_Fixed.exe')
)

$ErrorActionPreference = 'Stop'
$compiler = Join-Path $env:WINDIR 'Microsoft.NET\Framework\v4.0.30319\csc.exe'
if (-not (Test-Path -LiteralPath $compiler)) {
    throw "Không tìm thấy trình biên dịch .NET Framework x86: $compiler"
}

$arguments = @(
    '/nologo',
    '/target:winexe',
    '/platform:x86',
    '/optimize+',
    '/reference:System.dll',
    '/reference:System.Drawing.dll',
    '/reference:System.Windows.Forms.dll',
    ('/out:' + $OutputPath),
    (Join-Path $PSScriptRoot 'AHTLLauncher.cs')
)

& $compiler $arguments
if ($LASTEXITCODE -ne 0) {
    throw "Biên dịch launcher thất bại với mã $LASTEXITCODE"
}
Write-Host "Đã tạo launcher x86: $OutputPath"
