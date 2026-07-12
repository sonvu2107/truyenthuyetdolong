#!/usr/bin/env python3
"""Tạo và áp catalog cho bảng ngôn ngữ Lua của LogicServer.

Catalog luôn giữ cặp ``source``/``target`` theo từng file và từng key.  Công
cụ chỉ thay khi source của file đầu vào khớp tuyệt đối, đồng thời giữ nguyên
placeholder, định tuyến ``/M``/``/@@`` và số ký tự xuống dòng ``\\\\``.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PLACEHOLDER_RE = re.compile(r"\$[A-Za-z_][A-Za-z0-9_]*\$|(?<!%)%[ds]")
ROUTE_RE = re.compile(r"/(?:M|@@)[^>]*")
COLOR_RE = re.compile(r"c0x[0-9A-Fa-f]{8}")


@dataclass(frozen=True)
class Assignment:
    key: str
    occurrence: int
    quote: str
    value: str
    value_start: int
    value_end: int


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} không phải UTF-8: {exc}") from exc


def assignment_label(key: str, occurrence: int) -> str:
    return key if occurrence == 1 else f"{key}#{occurrence}"


def assignments(text: str, path: Path) -> dict[tuple[str, int], Assignment]:
    """Đọc field ``key = \"value\"`` của Lua mà không nhầm chuỗi/comment.

    Bảng Item đặt hai field trên cùng dòng (``n1=..., i1=...``), còn vài
    thoại dùng chuỗi nhiều dòng.  Vì vậy không thể chỉ dùng regex đầu dòng.
    """
    found: dict[tuple[str, int], Assignment] = {}
    occurrences: Counter[str] = Counter()
    index = 0
    size = len(text)
    while index < size:
        if text.startswith("--", index):
            newline = text.find("\n", index + 2)
            index = size if newline < 0 else newline + 1
            continue
        char = text[index]
        if char in "\"'":
            quote = char
            index += 1
            while index < size:
                if text[index] == "\\":
                    index += 2
                elif text[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
            continue
        if not (char.isascii() and (char.isalpha() or char == "_")):
            index += 1
            continue

        key_start = index
        index += 1
        while index < size and text[index].isascii() and (text[index].isalnum() or text[index] == "_"):
            index += 1
        key = text[key_start:index]
        cursor = index
        while cursor < size and text[cursor].isspace():
            cursor += 1
        if cursor >= size or text[cursor] != "=":
            continue
        cursor += 1
        while cursor < size and text[cursor].isspace():
            cursor += 1
        if cursor >= size or text[cursor] not in "\"'":
            continue

        quote = text[cursor]
        value_start = cursor + 1
        cursor = value_start
        while cursor < size:
            if text[cursor] == "\\":
                cursor += 2
            elif text[cursor] == quote:
                break
            else:
                cursor += 1
        if cursor >= size:
            raise ValueError(f"{path}: chuỗi chưa đóng tại key {key}")
        occurrences[key] += 1
        occurrence = occurrences[key]
        found[(key, occurrence)] = Assignment(
            key=key,
            occurrence=occurrence,
            quote=quote,
            value=text[value_start:cursor],
            value_start=value_start,
            value_end=cursor,
        )
        index = cursor + 1
    return found


def invariant_values(value: str) -> dict[str, Counter[str] | int]:
    return {
        "placeholders": Counter(PLACEHOLDER_RE.findall(value)),
        "routes": Counter(ROUTE_RE.findall(value)),
        "colors": Counter(COLOR_RE.findall(value)),
        "line_breaks": value.count("\\\\"),
        "trailing_backslashes": len(value) - len(value.rstrip("\\\\")),
    }


def is_escaped(value: str, position: int) -> bool:
    backslashes = 0
    position -= 1
    while position >= 0 and value[position] == "\\":
        backslashes += 1
        position -= 1
    return backslashes % 2 == 1


def validate_lua_string_fragment(value: str, quote: str, label: str) -> list[str]:
    """Chặn text có thể làm đổi điểm kết thúc của Lua string source.

    `target` được chèn vào giữa cặp nháy đã tồn tại của file snapshot. Chuỗi
    không được chứa newline/raw quote và không được kết thúc bằng một số dấu
    ``\\`` lẻ, vì dấu cuối cùng sẽ escape nháy đóng của source.
    """
    errors: list[str] = []
    if "\x00" in value or "\r" in value or "\n" in value:
        errors.append(f"{label}: target chứa ký tự điều khiển không hợp lệ cho Lua string")
    if any(char == quote and not is_escaped(value, index) for index, char in enumerate(value)):
        errors.append(f"{label}: target chứa nháy {quote} chưa escape")
    trailing_backslashes = len(value) - len(value.rstrip("\\\\"))
    if trailing_backslashes % 2:
        errors.append(f"{label}: target kết thúc bằng dấu \\ lẻ, sẽ escape nháy đóng Lua")
    return errors


def validate_translation(source: str, target: str, label: str, quote: str) -> list[str]:
    old = invariant_values(source)
    new = invariant_values(target)
    errors: list[str] = []
    for key in ("placeholders", "routes", "colors", "line_breaks", "trailing_backslashes"):
        if old[key] != new[key]:
            errors.append(f"{label}: {key} khác source")
    errors.extend(validate_lua_string_fragment(target, quote, label))
    return errors


def restore_route_payloads(source: str, target: str) -> tuple[str, bool]:
    """Giữ phần chữ hiển thị của target, nhưng phục hồi payload route từ source.

    Ví dụ ``<Gặp Akara/M...:阿卡拉>`` có thể dịch nhãn bên trái, còn phần sau
    ``/M`` bắt buộc dùng đúng map/NPC tiếng Trung mà LogicServer nhận diện.
    Chỉ sửa khi hai bên có cùng số route và cùng loại route.
    """
    source_routes = list(ROUTE_RE.finditer(source))
    target_routes = list(ROUTE_RE.finditer(target))
    if not source_routes or len(source_routes) != len(target_routes):
        return target, False
    def kind(match: re.Match[str]) -> str:
        return "@@" if match.group(0).startswith("/@@") else "M"

    if any(kind(a) != kind(b) for a, b in zip(source_routes, target_routes)):
        return target, False
    patched = target
    for old, new in reversed(list(zip(target_routes, source_routes))):
        patched = patched[:old.start()] + new.group(0) + patched[old.end():]
    return patched, patched != target


def load_catalog(path: Path) -> dict[str, list[dict[str, str | int]]]:
    data = json.loads(read_utf8(path))
    if data.get("format") != 1 or not isinstance(data.get("files"), dict):
        raise ValueError(f"{path} không đúng catalog server language format 1")
    files: dict[str, list[dict[str, str | int]]] = {}
    for filename, definition in data["files"].items():
        entries = definition.get("entries") if isinstance(definition, dict) else None
        if not isinstance(filename, str) or not isinstance(entries, list):
            raise ValueError(f"{path}: file/entries không hợp lệ: {filename!r}")
        checked: list[dict[str, str | int]] = []
        identities: set[tuple[str, int]] = set()
        for entry in entries:
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("key"), str)
                or not isinstance(entry.get("occurrence"), int)
                or entry["occurrence"] < 1
                or not isinstance(entry.get("source"), str)
                or not isinstance(entry.get("target"), str)
            ):
                raise ValueError(f"{path}: entry không hợp lệ: {filename}:{entry!r}")
            identity = (entry["key"], entry["occurrence"])
            if identity in identities:
                raise ValueError(f"{path}: entry trùng: {filename}:{assignment_label(*identity)}")
            identities.add(identity)
            checked.append({
                "key": entry["key"],
                "occurrence": entry["occurrence"],
                "source": entry["source"],
                "target": entry["target"],
            })
        files[filename] = checked
    return files


def command_generate(args: argparse.Namespace) -> int:
    source_root = Path(args.source_root)
    target_root = Path(args.target_root)
    result: dict[str, object] = {
        "format": 1,
        "description": args.description,
        "files": {},
    }
    report: dict[str, object] = {
        "files": {},
        "changed": 0,
        "missing_target_keys": [],
        "rejected": [],
        "route_payloads_restored": [],
    }

    for filename in args.file:
        source_path = source_root / filename
        target_path = target_root / filename
        source_values = assignments(read_utf8(source_path), source_path)
        target_values = assignments(read_utf8(target_path), target_path)
        entries: list[dict[str, str | int]] = []
        missing_target = sorted(set(source_values) - set(target_values))
        for identity, source in source_values.items():
            target = target_values.get(identity)
            if target is None or source.value == target.value:
                continue
            target_value, route_restored = restore_route_payloads(source.value, target.value)
            errors = validate_translation(
                source.value,
                target_value,
                f"{filename}:{assignment_label(*identity)}",
                source.quote,
            )
            if errors:
                report["rejected"].append({
                    "file": filename,
                    "key": source.key,
                    "occurrence": source.occurrence,
                    "errors": errors,
                })
                continue
            if route_restored:
                report["route_payloads_restored"].append(
                    f"{filename}:{assignment_label(*identity)}"
                )
            entries.append({
                "key": source.key,
                "occurrence": source.occurrence,
                "source": source.value,
                "target": target_value,
            })
        result["files"][filename] = {"entries": entries}
        report["files"][filename] = {
            "source_keys": len(source_values),
            "target_keys": len(target_values),
            "changed": len(entries),
            "missing_target_keys": missing_target,
        }
        report["changed"] += len(entries)
        report["missing_target_keys"].extend(
            f"{filename}:{assignment_label(*identity)}" for identity in missing_target
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã tạo {output}: {report['changed']} entry an toàn")
    if report["missing_target_keys"]:
        print(f"Cảnh báo: {len(report['missing_target_keys'])} key VPS chưa có target", file=sys.stderr)
    if report["rejected"]:
        print(f"Cảnh báo: loại {len(report['rejected'])} entry làm đổi cấu trúc", file=sys.stderr)
    if report["route_payloads_restored"]:
        print(f"Đã phục hồi payload route cho {len(report['route_payloads_restored'])} entry", file=sys.stderr)
    return 0


def replace_entries(
    text: str,
    found: dict[tuple[str, int], Assignment],
    entries: list[dict[str, str | int]],
    filename: str,
) -> tuple[str, list[str]]:
    errors: list[str] = []
    replacements: list[tuple[int, int, str]] = []
    for entry in entries:
        key = entry["key"]
        occurrence = entry["occurrence"]
        assert isinstance(key, str) and isinstance(occurrence, int)
        source = entry["source"]
        target = entry["target"]
        assert isinstance(source, str) and isinstance(target, str)
        assignment = found.get((key, occurrence))
        label = f"{filename}:{assignment_label(key, occurrence)}"
        if assignment is None:
            errors.append(f"{label}: thiếu key trong file đầu vào")
            continue
        if assignment.value != source:
            errors.append(f"{label}: source mismatch")
            continue
        errors.extend(validate_translation(source, target, label, assignment.quote))
        replacements.append((assignment.value_start, assignment.value_end, target))
    if errors:
        return text, errors
    for start, end, target in reversed(replacements):
        text = text[:start] + target + text[end:]
    return text, []


def command_apply(args: argparse.Namespace) -> int:
    source_root = Path(args.source_root)
    catalog = load_catalog(Path(args.catalog))
    output_root = Path(args.output_root) if args.output_root else source_root
    if args.output_root:
        output_root.mkdir(parents=True, exist_ok=True)

    pending: list[tuple[Path, Path, str]] = []
    report: dict[str, object] = {"files": {}, "changed": 0, "errors": []}
    for filename, entries in catalog.items():
        source_path = source_root / filename
        if not source_path.is_file():
            report["errors"].append(f"{filename}: không tìm thấy file đầu vào")
            continue
        text = read_utf8(source_path)
        try:
            found = assignments(text, source_path)
        except ValueError as exc:
            report["errors"].append(str(exc))
            continue
        patched, errors = replace_entries(text, found, entries, filename)
        if errors:
            report["errors"].extend(errors)
            continue
        output_path = output_root / filename
        pending.append((source_path, output_path, patched))
        report["files"][filename] = {"changed": len(entries)}
        report["changed"] += len(entries)

    if report["errors"]:
        if args.report:
            Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for error in report["errors"]:
            print(error, file=sys.stderr)
        return 2

    for source_path, output_path, patched in pending:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.output_root and source_path.resolve() != output_path.resolve():
            shutil.copy2(source_path, output_path)
        output_path.write_text(patched, encoding="utf-8", newline="")
    if args.report:
        Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Đã áp {report['changed']} entry")
    return 0


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    generate = sub.add_parser("generate", help="Tạo catalog source/target từ snapshot VPS và bản dịch.")
    generate.add_argument("--source-root", required=True)
    generate.add_argument("--target-root", required=True)
    generate.add_argument("--file", action="append", required=True)
    generate.add_argument("--output", required=True)
    generate.add_argument("--report")
    generate.add_argument("--description", default="Catalog LogicServer Vietnamese.")
    generate.set_defaults(func=command_generate)

    apply = sub.add_parser("apply", help="Áp catalog có kiểm source vào bản staging hoặc inplace.")
    apply.add_argument("--source-root", required=True)
    apply.add_argument("--catalog", required=True)
    apply.add_argument("--output-root")
    apply.add_argument("--report")
    apply.set_defaults(func=command_apply)
    return parser.parse_args(list(argv))


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
