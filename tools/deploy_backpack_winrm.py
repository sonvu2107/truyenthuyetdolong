#!/usr/bin/env python3
"""Chạy script deploy Hành Trang trên VPS qua WinRM."""

from __future__ import annotations

import argparse
import os
import sys

import winrm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    password = os.environ.get("AHTL_VPS_PASSWORD")
    if not password:
        raise SystemExit("Thiếu biến môi trường AHTL_VPS_PASSWORD")

    script_url = (
        "https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/"
        f"{args.revision}/scripts/Sync-BackpackPolishFromGitHub.ps1"
    )
    if args.verify_only:
        powershell = """$ErrorActionPreference='Stop'
$root='C:\\GPHANTL\\server\\GPHweb\\wwwroot'
$targets=@('GameFrame.swf','data\\lang\\zh-cn\\cbp.zip','game\\GameConfig.php','game\\djrm.php','data\\lang\\zh-cn\\bagQuickConfig.cbp')
foreach ($relative in $targets) {
    $path=Join-Path $root $relative
    Write-Output ($relative + '=' + (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash)
}
$backup=Get-ChildItem -LiteralPath (Join-Path $root '_deploy_backups') -Directory | Where-Object Name -like 'backpack_ui_*' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Write-Output ('BACKUP=' + $backup.FullName)
Select-String -LiteralPath (Join-Path $root 'game\\djrm.php') -Pattern 'AHTL_GLOBAL_CBP_CACHE|ahtlcache=' | ForEach-Object { Write-Output $_.Line.Trim() }
"""
    else:
        powershell = f"""$ErrorActionPreference='Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$path=Join-Path $env:TEMP 'Sync-BackpackPolishFromGitHub.ps1'
Invoke-WebRequest -UseBasicParsing -Uri '{script_url}' -OutFile $path
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
& $path -Revision {args.revision}
"""
    session = winrm.Session(
        f"http://{args.host}:5985/wsman",
        auth=(args.user, password),
        transport="ntlm",
    )
    result = session.run_ps(powershell)
    sys.stdout.write(result.std_out.decode("utf-8", "replace"))
    sys.stderr.write(result.std_err.decode("utf-8", "replace"))
    return result.status_code


if __name__ == "__main__":
    raise SystemExit(main())
