#!/usr/bin/env python3
"""Kiểm toán catalog hard-code và cây nguồn sau khi ghép bản dịch."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from audit_gameframe_localization import signature, visible_text
from finish_gameframe_catalog import AS_LITERAL_RE
from translate_gameframe_catalog import HAN_RE, TranslationError, decode_as_string
from translate_gameframe_hardcoded import line_reason


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def audit_catalog(path: Path) -> tuple[int, int, list[str]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("format") != 1 or not isinstance(document.get("files"), list):
        raise TranslationError("Catalog hard-code sai format 1")
    errors: list[str] = []
    replacements = 0
    for file_entry in document["files"]:
        relative = file_entry.get("path", "")
        for row in file_entry.get("replacements", []):
            replacements += 1
            source = row.get("source")
            target = row.get("target")
            if not isinstance(source, str) or not AS_LITERAL_RE.fullmatch(source):
                errors.append(f"{relative}: source không phải một chuỗi ActionScript")
                continue
            if not isinstance(target, str) or not AS_LITERAL_RE.fullmatch(target):
                errors.append(f"{relative}: target không phải một chuỗi ActionScript")
                continue
            source_text = decode_as_string(source)
            target_text = decode_as_string(target)
            if signature([source_text]) != signature([target_text]):
                errors.append(f"{relative}: thay đổi HTML/placeholder/URL/route")
            if HAN_RE.search(visible_text(target_text)):
                errors.append(f"{relative}: target vẫn còn Hán tự hiển thị")
    return len(document["files"]), replacements, errors


def scan_overlay(source_root: Path, overlay_root: Path) -> tuple[list[dict], list[str]]:
    technical: list[dict] = []
    errors: list[str] = []
    for source_path in source_root.rglob("*.as"):
        relative = source_path.relative_to(source_root)
        if relative.as_posix() == "scripts/lang/ZH_CN.as":
            continue
        overlay_path = overlay_root / relative
        path = overlay_path if overlay_path.is_file() else source_path
        content = path.read_text(encoding="utf-8-sig")
        lines = content.splitlines()
        for match in AS_LITERAL_RE.finditer(content):
            literal = match.group(0)
            if not HAN_RE.search(literal):
                continue
            line_number = content.count("\n", 0, match.start()) + 1
            line = lines[line_number - 1]
            decoded = decode_as_string(literal)
            reason = line_reason(line, literal, decoded)
            row = {
                "path": relative.as_posix(),
                "line": line_number,
                "source_expression": literal,
                "reason": reason,
            }
            if reason is None:
                errors.append(
                    f"{relative.as_posix()}:{line_number} còn Hán tự hiển thị: {decoded}"
                )
            else:
                technical.append(row)
    return technical, errors


def decoded_literals(path: Path) -> list[str]:
    content = path.read_text(encoding="utf-8-sig")
    return [decode_as_string(match.group(0)) for match in AS_LITERAL_RE.finditer(content)]


def load_exclusions(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("format") != 1:
        raise TranslationError("Báo cáo ngoại lệ compile sai format 1")
    return {entry["path"]: entry["reason"] for entry in document.get("entries", [])}


def audit_compiled(
    catalog_path: Path,
    source_root: Path,
    overlay_root: Path,
    compiled_root: Path,
    exclusions: dict[str, str],
) -> tuple[dict, list[str]]:
    document = json.loads(catalog_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    checked_files = 0
    compiled_replacements = 0
    excluded_replacements = 0
    for file_entry in document["files"]:
        relative = file_entry["path"]
        source_path = source_root / relative
        overlay_path = overlay_root / relative
        compiled_path = compiled_root / relative
        if not compiled_path.is_file():
            errors.append(f"{relative}: thiếu lớp sau xuất ngược SWF")
            continue
        if relative in exclusions:
            expected_path = source_path
            excluded_replacements += len(file_entry.get("replacements", []))
        else:
            expected_path = overlay_path
            compiled_replacements += len(file_entry.get("replacements", []))
        if decoded_literals(expected_path) != decoded_literals(compiled_path):
            errors.append(f"{relative}: chuỗi sau compile lệch nguồn mong đợi")
        checked_files += 1

    not_decompiled = []
    technical = []
    visible_han = []
    for path in compiled_root.rglob("*.as"):
        relative = path.relative_to(compiled_root).as_posix()
        content = path.read_text(encoding="utf-8-sig")
        if "Not decompiled due to error" in content:
            not_decompiled.append(relative)
        if relative == "scripts/lang/ZH_CN.as":
            continue
        lines = content.splitlines()
        for match in AS_LITERAL_RE.finditer(content):
            literal = match.group(0)
            if not HAN_RE.search(literal):
                continue
            line_number = content.count("\n", 0, match.start()) + 1
            line = lines[line_number - 1]
            decoded = decode_as_string(literal)
            reason = (
                f"ngoại lệ compile: {exclusions[relative]}"
                if relative in exclusions
                else line_reason(line, literal, decoded)
            )
            row = {
                "path": relative,
                "line": line_number,
                "source_expression": literal,
                "reason": reason,
            }
            if reason is None:
                visible_han.append(row)
            else:
                technical.append(row)
    if not_decompiled:
        errors.append(f"Còn {len(not_decompiled)} lớp không decompile được: {not_decompiled}")
    if visible_han:
        errors.append(f"Còn {len(visible_han)} chuỗi Hán tự hiển thị sau compile")
    return (
        {
            "checked_files": checked_files,
            "compiled_replacements": compiled_replacements,
            "excluded_replacements": excluded_replacements,
            "compile_exclusions": sorted(exclusions),
            "not_decompiled": not_decompiled,
            "technical_han_occurrences": technical,
            "visible_han_occurrences": visible_han,
        },
        errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--overlay-root", type=Path, required=True)
    parser.add_argument("--technical-output", type=Path, required=True)
    parser.add_argument("--compiled-root", type=Path)
    parser.add_argument("--compile-exclusions", type=Path)
    parser.add_argument("--compiled-report", type=Path)
    args = parser.parse_args()

    files, replacements, errors = audit_catalog(args.catalog)
    technical, scan_errors = scan_overlay(args.source_root, args.overlay_root)
    errors.extend(scan_errors)
    compiled_report = None
    if args.compiled_root:
        compiled_report, compiled_errors = audit_compiled(
            args.catalog,
            args.source_root,
            args.overlay_root,
            args.compiled_root,
            load_exclusions(args.compile_exclusions),
        )
        errors.extend(compiled_errors)
        if args.compiled_report:
            args.compiled_report.write_text(
                json.dumps(compiled_report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    args.technical_output.write_text(
        json.dumps(
            {
                "format": 1,
                "description": "Hán tự hard-code chỉ còn trong định danh kỹ thuật được phép giữ.",
                "entries": technical,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"Catalog: {files} lớp, {replacements} chuỗi duy nhất; "
        f"residual kỹ thuật: {len(technical)} lần; lỗi: {len(errors)}"
    )
    if compiled_report:
        print(
            "Compiled: "
            f"{compiled_report['checked_files']} lớp, "
            f"{compiled_report['compiled_replacements']} chuỗi đã nhập, "
            f"{compiled_report['excluded_replacements']} chuỗi giữ bytecode gốc, "
            f"visible Han={len(compiled_report['visible_han_occurrences'])}, "
            f"not-decompiled={len(compiled_report['not_decompiled'])}"
        )
    for error in errors[:100]:
        print(f"- {error}")
    if errors:
        raise TranslationError(f"Kiểm toán hard-code thất bại với {len(errors)} lỗi")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, TranslationError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        raise SystemExit(1)
