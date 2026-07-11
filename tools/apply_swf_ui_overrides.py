#!/usr/bin/env python3
"""Áp các bản rút gọn UI theo đúng khóa vào lang/ZH_CN.as đã Việt hóa."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from swf_lang_localizer import ASSIGN_RE
from translate_gameframe_catalog import TranslationError, decode_as_string


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class OverrideError(ValueError):
    pass


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    overrides = payload.get("overrides")
    if payload.get("format") != 1 or not isinstance(overrides, dict):
        raise OverrideError("Catalog override phải có format=1 và overrides")
    for key, entry in overrides.items():
        if not isinstance(entry, dict):
            raise OverrideError(f"Override không hợp lệ: {key}")
        if not isinstance(entry.get("source"), str) or not isinstance(
            entry.get("target"), str
        ):
            raise OverrideError(f"Override thiếu source/target: {key}")
        if entry["source"] == entry["target"]:
            raise OverrideError(f"Override không thay đổi nội dung: {key}")
    return overrides


def patch_source(source: str, overrides: dict[str, dict[str, str]]) -> tuple[str, dict]:
    output: list[str] = []
    matched: set[str] = set()
    changes: list[dict[str, str | int]] = []

    for line_number, line in enumerate(source.splitlines(keepends=True), start=1):
        match = ASSIGN_RE.match(line)
        if not match:
            output.append(line)
            continue
        index = match.group("index")
        key = (
            f"{match.group('name')}[{int(index)}]"
            if index is not None
            else match.group("name")
        )
        entry = overrides.get(key)
        if entry is None:
            output.append(line)
            continue
        expression = match.group("value").strip()
        try:
            current = decode_as_string(expression)
        except TranslationError as exc:
            raise OverrideError(f"{key} không phải chuỗi AS đơn tại dòng {line_number}") from exc
        if current != entry["source"]:
            raise OverrideError(
                f"Nguồn không khớp tại {key}: AS={current!r}, "
                f"catalog={entry['source']!r}"
            )
        target_expression = json.dumps(entry["target"], ensure_ascii=False)
        index_part = f"[{int(index)}]" if index is not None else ""
        newline = match.group("newline") or ""
        output.append(
            f"{match.group('indent')}{match.group('name')}{index_part} = "
            f"{target_expression};{newline}"
        )
        matched.add(key)
        changes.append(
            {
                "key": key,
                "line": line_number,
                "source": current,
                "target": entry["target"],
                "category": entry.get("category", ""),
            }
        )

    missing = sorted(set(overrides) - matched)
    if missing:
        raise OverrideError(f"Không tìm thấy {len(missing)} khóa override: {missing}")
    return "".join(output), {"changed": len(changes), "changes": changes}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        patched, report = patch_source(
            args.source.read_text(encoding="utf-8-sig"),
            load_overrides(args.catalog),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(patched, encoding="utf-8", newline="\n")
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        print(f"Đã áp {report['changed']} override UI vào {args.output}")
        return 0
    except (OSError, json.JSONDecodeError, OverrideError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
