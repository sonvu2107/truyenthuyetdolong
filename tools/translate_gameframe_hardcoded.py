#!/usr/bin/env python3
"""Dịch chuỗi hard-code ngoài lang.ZH_CN với allowlist kỹ thuật bảo thủ."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from audit_gameframe_localization import visible_text
from finish_gameframe_catalog import AS_LITERAL_RE, SegmentTranslator
from translate_gameframe_catalog import HAN_RE, TranslationError, decode_as_string


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


FONT_NAMES = {
    "黑体",
    "宋体",
    "幼圆",
    "微软雅黑",
    "楷体",
    "隶书",
}
LOOKUP_RE = re.compile(
    r"(?:getChildByName|getDefinitionByName|hasOwnProperty|getAttribute|"
    r"getQualifiedClassName)\s*\([^)]*$",
    re.IGNORECASE,
)
PATH_RE = re.compile(r"^[^\s<>]+\.(?:swf|cbp|xml|png|jpe?g|gif|mp3|wav)$", re.I)
SAFE_COMPARISON_OVERRIDES = {
    ("scripts/view/game/city/page/CityOfficialPage.as", "待定"),
    ("scripts/view/game/city/win/CytiOfficalResultWin.as", "待定"),
}
MANUAL_TARGETS = {
    "待定": "Chưa bổ nhiệm",
}


def line_reason(line: str, literal: str, decoded: str) -> str | None:
    shown = visible_text(decoded)
    if not HAN_RE.search(shown):
        return "font/route/markup kỹ thuật"
    if decoded.strip() in FONT_NAMES:
        return "tên font hệ thống"
    without_font_names = decoded
    for font_name in FONT_NAMES:
        without_font_names = without_font_names.replace(font_name, "")
    if not HAN_RE.search(without_font_names):
        return "mảnh chuỗi tên font hệ thống"
    if decoded.lstrip().startswith("@"):
        return "lệnh nội bộ bắt đầu bằng @"
    if PATH_RE.fullmatch(decoded.strip()):
        return "đường dẫn tài nguyên"
    position = line.find(literal)
    before = line[:position] if position >= 0 else line
    after = line[position + len(literal) :] if position >= 0 else ""
    if re.search(r"\bcase\s*$", before):
        return "giá trị case nội bộ"
    if re.search(r"(?:===?|!==?)\s*$", before) or re.match(
        r"\s*(?:===?|!==?)", after
    ):
        return "khóa so sánh nội bộ"
    if LOOKUP_RE.search(before):
        return "khóa tra cứu đối tượng"
    return None


def scan(root: Path) -> tuple[dict[str, dict[str, dict]], list[dict]]:
    candidates: dict[str, dict[str, dict]] = defaultdict(dict)
    occurrences: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for path in root.rglob("*.as"):
        relative = path.relative_to(root).as_posix()
        if relative == "scripts/lang/ZH_CN.as":
            continue
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
            if (relative, decoded) in SAFE_COMPARISON_OVERRIDES:
                reason = None
            occurrences[(relative, literal)].append(
                {
                    "line": line_number,
                    "context": line.strip(),
                    "reason": reason,
                }
            )

    allowlist: list[dict] = []
    for (relative, literal), uses in sorted(occurrences.items()):
        reasons = sorted({use["reason"] for use in uses if use["reason"]})
        if reasons:
            allowlist.append(
                {
                    "path": relative,
                    "source_expression": literal,
                    "expected": len(uses),
                    "reasons": reasons,
                    "lines": [use["line"] for use in uses],
                }
            )
            continue
        candidates[relative][literal] = {
            "expected": len(uses),
            "lines": [use["line"] for use in uses],
        }
    return candidates, allowlist


def load_existing(path: Path) -> dict[str, dict[str, dict]]:
    result: dict[str, dict[str, dict]] = defaultdict(dict)
    if not path.exists():
        return result
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("format") != 1:
        raise TranslationError("Catalog hard-code hiện có sai format")
    for file_entry in document.get("files", []):
        relative = file_entry["path"]
        for replacement in file_entry.get("replacements", []):
            result[relative][replacement["source"]] = replacement
    return result


def write_catalog(path: Path, replacements: dict[str, dict[str, dict]]) -> None:
    files = []
    for relative in sorted(replacements):
        rows = list(replacements[relative].values())
        if rows:
            files.append({"path": relative, "replacements": rows})
    path.write_text(
        json.dumps(
            {
                "format": 1,
                "description": (
                    "Chuỗi hiển thị hard-code ngoài lang.ZH_CN; thay cả biểu thức "
                    "chuỗi và giữ nguyên HTML, placeholder, route."
                ),
                "files": files,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allowlist-output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=25)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--pause", type=float, default=0.05)
    args = parser.parse_args()

    candidates, allowlist = scan(args.source_root)
    replacements = load_existing(args.output)
    translator = SegmentTranslator(args.timeout, args.retries, args.pause)
    total = sum(len(values) for values in candidates.values())
    done = sum(
        1
        for relative, values in candidates.items()
        for literal in values
        if literal in replacements.get(relative, {})
    )
    print(
        f"Cần dịch {total} chuỗi duy nhất; đã có checkpoint {done}; "
        f"giữ kỹ thuật {len(allowlist)} chuỗi"
    )

    for relative in sorted(candidates):
        for literal, metadata in candidates[relative].items():
            if literal in replacements.get(relative, {}):
                continue
            source = decode_as_string(literal)
            target = MANUAL_TARGETS.get(source, translator.text(source))
            if target == source or HAN_RE.search(visible_text(target)):
                raise TranslationError(
                    f"Chưa dịch hết Hán tự hiển thị tại {relative}:{metadata['lines']}"
                )
            target_expression = json.dumps(target, ensure_ascii=False)
            replacements[relative][literal] = {
                "source": literal,
                "target": target_expression,
                "expected": metadata["expected"],
                "review": "segmented-machine",
                "source_lines": metadata["lines"],
            }
            done += 1
            write_catalog(args.output, replacements)
            if done % 25 == 0:
                print(f"Đã dịch {done}/{total}")

    args.allowlist_output.write_text(
        json.dumps(
            {
                "format": 1,
                "description": (
                    "Chuỗi Hán tự hard-code phải giữ nguyên vì là font, route, "
                    "lệnh, khóa so sánh hoặc khóa tra cứu nội bộ."
                ),
                "entries": allowlist,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Hoàn tất {done}/{total}; allowlist kỹ thuật {len(allowlist)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, TranslationError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        raise SystemExit(1)
