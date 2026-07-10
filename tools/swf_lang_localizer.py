#!/usr/bin/env python3
"""Biên dịch ClientLang.txt vào lớp ngôn ngữ ActionScript của GameFrame.swf.

Tool chỉ thay vế phải của các phép gán chuỗi theo đúng khóa:

* Biến đơn: ``Common_OK = \"Xác nhận\"``
* Phần tử mảng: ``skill[0] = \"Kỹ năng\"``

Không thay chuỗi theo nội dung toàn cục, vì cùng một câu tiếng Trung có thể là
định danh kỹ thuật ở nơi khác. File báo cáo JSON giúp kiểm tra độ phủ và toàn bộ
phép gán còn Hán tự trước khi nhập mã nguồn trở lại SWF.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


HAN_RE = re.compile(r"[\u3400-\u9fff]")
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
ASSIGN_RE = re.compile(
    r"^(?P<indent>\s*)(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\[(?P<index>\d+)\])?\s*=\s*(?P<value>.*?);\s*"
    r"(?P<newline>\r?\n)?$"
)


class LangError(ValueError):
    pass


@dataclass(frozen=True)
class ClientLang:
    scalars: dict[str, str]
    arrays: dict[str, list[str]]

    @property
    def entry_count(self) -> int:
        return len(self.scalars) + sum(len(values) for values in self.arrays.values())


class Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0

    def error(self, message: str) -> LangError:
        line = self.text.count("\n", 0, self.pos) + 1
        return LangError(f"{message} tại dòng {line}, byte ký tự {self.pos}")

    def skip_space(self) -> None:
        while self.pos < len(self.text):
            if self.text[self.pos].isspace() or self.text[self.pos] in ",;":
                self.pos += 1
                continue
            if self.text.startswith("--", self.pos):
                newline = self.text.find("\n", self.pos + 2)
                self.pos = len(self.text) if newline < 0 else newline + 1
                continue
            break

    def take(self, expected: str) -> None:
        self.skip_space()
        if not self.text.startswith(expected, self.pos):
            raise self.error(f"Cần {expected!r}")
        self.pos += len(expected)

    def identifier(self) -> str:
        self.skip_space()
        match = IDENT_RE.match(self.text, self.pos)
        if not match:
            raise self.error("Cần tên biến")
        self.pos = match.end()
        return match.group(0)

    def quoted_raw(self) -> str:
        self.skip_space()
        if self.pos >= len(self.text) or self.text[self.pos] != '"':
            raise self.error("Cần chuỗi đặt trong dấu nháy kép")
        start = self.pos
        self.pos += 1
        escaped = False
        while self.pos < len(self.text):
            char = self.text[self.pos]
            self.pos += 1
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                raw = self.text[start : self.pos]
                if "\n" in raw or "\r" in raw:
                    raise self.error("Chuỗi ClientLang không được chứa xuống dòng thật")
                return raw
        raise self.error("Chuỗi chưa đóng dấu nháy kép")

    def array(self) -> list[str]:
        self.take("{")
        values: list[str] = []
        while True:
            self.skip_space()
            if self.pos < len(self.text) and self.text[self.pos] == "}":
                self.pos += 1
                return values
            values.append(self.quoted_raw())

    def parse(self) -> ClientLang:
        root = self.identifier()
        if root != "ClientLang":
            raise self.error("File phải bắt đầu bằng ClientLang")
        self.take("=")
        self.take("{")
        scalars: dict[str, str] = {}
        arrays: dict[str, list[str]] = {}
        while True:
            self.skip_space()
            if self.pos >= len(self.text):
                raise self.error("Thiếu dấu đóng của ClientLang")
            if self.text[self.pos] == "}":
                self.pos += 1
                break
            name = self.identifier()
            self.take("=")
            self.skip_space()
            if name in scalars or name in arrays:
                raise self.error(f"Khóa ClientLang bị lặp: {name}")
            if self.pos < len(self.text) and self.text[self.pos] == "{":
                arrays[name] = self.array()
            else:
                scalars[name] = self.quoted_raw()
        self.skip_space()
        if self.pos != len(self.text):
            raise self.error("Còn dữ liệu ngoài khối ClientLang")
        return ClientLang(scalars=scalars, arrays=arrays)


def load_client_lang(path: Path) -> ClientLang:
    text = path.read_text(encoding="utf-8-sig")
    return Parser(text).parse()


def validate_shape(translated: ClientLang, reference: ClientLang) -> None:
    translated_keys = set(translated.scalars) | set(translated.arrays)
    reference_keys = set(reference.scalars) | set(reference.arrays)
    if translated_keys != reference_keys:
        missing = sorted(reference_keys - translated_keys)
        extra = sorted(translated_keys - reference_keys)
        raise LangError(f"Khóa ClientLang lệch bản gốc: thiếu={missing}, thừa={extra}")
    mismatches = [
        (name, len(reference.arrays[name]), len(translated.arrays[name]))
        for name in sorted(reference.arrays)
        if len(translated.arrays[name]) != len(reference.arrays[name])
    ]
    if mismatches:
        raise LangError(f"Độ dài mảng ClientLang lệch bản gốc: {mismatches}")


def has_han(value: str) -> bool:
    return HAN_RE.search(value) is not None


def patch_source(source: str, lang: ClientLang) -> tuple[str, dict]:
    output: list[str] = []
    matched_keys: set[tuple[str, int | None]] = set()
    changed = 0
    matched = 0
    source_assignments = 0
    source_han_assignments = 0

    for line in source.splitlines(keepends=True):
        match = ASSIGN_RE.match(line)
        if not match:
            output.append(line)
            continue
        source_assignments += 1
        name = match.group("name")
        index_text = match.group("index")
        index = int(index_text) if index_text is not None else None
        target: str | None = None
        if index is None:
            target = lang.scalars.get(name)
        elif name in lang.arrays and index < len(lang.arrays[name]):
            target = lang.arrays[name][index]
        if has_han(match.group("value")):
            source_han_assignments += 1
        if target is None:
            output.append(line)
            continue

        matched += 1
        matched_keys.add((name, index))
        if match.group("value").strip() != target:
            changed += 1
        index_part = f"[{index}]" if index is not None else ""
        newline = match.group("newline") or ""
        output.append(f'{match.group("indent")}{name}{index_part} = {target};{newline}')

    patched = "".join(output)
    residual: list[dict[str, object]] = []
    for line_number, line in enumerate(patched.splitlines(), start=1):
        match = ASSIGN_RE.match(line)
        if match and has_han(match.group("value")):
            residual.append(
                {
                    "line": line_number,
                    "name": match.group("name"),
                    "index": (
                        int(match.group("index"))
                        if match.group("index") is not None
                        else None
                    ),
                    "value": match.group("value"),
                }
            )

    missing_client_entries: list[str] = []
    for name in sorted(lang.scalars):
        if (name, None) not in matched_keys:
            missing_client_entries.append(name)
    for name in sorted(lang.arrays):
        for index in range(len(lang.arrays[name])):
            if (name, index) not in matched_keys:
                missing_client_entries.append(f"{name}[{index}]")

    report = {
        "client_lang_entries": lang.entry_count,
        "client_lang_scalars": len(lang.scalars),
        "client_lang_arrays": len(lang.arrays),
        "source_assignments": source_assignments,
        "source_han_assignments": source_han_assignments,
        "matched_entries": matched,
        "changed_entries": changed,
        "missing_client_entries": missing_client_entries,
        "residual_han_assignments": residual,
    }
    return patched, report


def command_patch(args: argparse.Namespace) -> None:
    lang = load_client_lang(args.client_lang)
    if args.reference_client_lang:
        validate_shape(lang, load_client_lang(args.reference_client_lang))
    source = args.source.read_text(encoding="utf-8-sig")
    patched, report = patch_source(source, lang)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(patched, encoding="utf-8", newline="\n")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    print(f"ClientLang: {report['client_lang_entries']} mục")
    print(
        "ActionScript: "
        f"khớp {report['matched_entries']}, đổi {report['changed_entries']}, "
        f"còn Hán tự {len(report['residual_han_assignments'])} phép gán"
    )
    print(f"Mục ClientLang chưa có trong SWF: {len(report['missing_client_entries'])}")

    if report["matched_entries"] < args.min_matched:
        raise LangError(
            f"Độ phủ quá thấp: {report['matched_entries']} < {args.min_matched}"
        )
    residual_count = len(report["residual_han_assignments"])
    if args.max_residual_han is not None and residual_count > args.max_residual_han:
        raise LangError(
            f"Số phép gán còn Hán tự quá cao: {residual_count} > "
            f"{args.max_residual_han}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    patch = sub.add_parser("patch-source", help="Áp ClientLang vào lang/ZH_CN.as")
    patch.add_argument("--client-lang", type=Path, required=True)
    patch.add_argument("--reference-client-lang", type=Path)
    patch.add_argument("--source", type=Path, required=True)
    patch.add_argument("--output", type=Path, required=True)
    patch.add_argument("--report", type=Path)
    patch.add_argument("--min-matched", type=int, default=1)
    patch.add_argument("--max-residual-han", type=int)
    patch.set_defaults(func=command_patch)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (LangError, OSError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
