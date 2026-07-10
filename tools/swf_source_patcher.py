#!/usr/bin/env python3
"""Áp catalog thay chuỗi có kiểm tra vào các lớp ActionScript đã xuất."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class PatchError(ValueError):
    pass


def safe_relative(value: str) -> Path:
    path = Path(value.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts:
        raise PatchError(f"Đường dẫn catalog không an toàn: {value!r}")
    return path


def apply_catalog(source_root: Path, output_root: Path, catalog_path: Path) -> dict:
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    if catalog.get("format") != 1 or not isinstance(catalog.get("files"), list):
        raise PatchError("Catalog không đúng format 1")
    report = {"files": [], "replacement_count": 0}
    seen_paths: set[Path] = set()
    for file_entry in catalog["files"]:
        relative = safe_relative(file_entry.get("path", ""))
        if relative in seen_paths:
            raise PatchError(f"File bị lặp trong catalog: {relative}")
        seen_paths.add(relative)
        source_path = source_root / relative
        if not source_path.is_file():
            raise PatchError(f"Không tìm thấy mã nguồn: {source_path}")
        content = source_path.read_text(encoding="utf-8-sig")
        file_changes = 0
        for replacement in file_entry.get("replacements", []):
            source = replacement.get("source")
            target = replacement.get("target")
            expected = replacement.get("expected", 1)
            if not isinstance(source, str) or not isinstance(target, str):
                raise PatchError(f"Chuỗi thay thế không hợp lệ trong {relative}")
            if source == target:
                raise PatchError(f"Nguồn và đích giống nhau trong {relative}: {source!r}")
            actual = content.count(source)
            if actual != expected:
                raise PatchError(
                    f"Số lần khớp sai trong {relative}: {source!r}, "
                    f"cần {expected}, thực tế {actual}"
                )
            content = content.replace(source, target)
            file_changes += actual
        target_path = output_root / relative
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8", newline="\n")
        report["files"].append(
            {"path": relative.as_posix(), "replacement_count": file_changes}
        )
        report["replacement_count"] += file_changes
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = apply_catalog(args.source_root, args.output_root, args.catalog)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        print(
            f"Đã vá {report['replacement_count']} vị trí trong "
            f"{len(report['files'])} lớp ActionScript"
        )
    except (OSError, json.JSONDecodeError, PatchError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
