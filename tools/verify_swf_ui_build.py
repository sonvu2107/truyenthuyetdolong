#!/usr/bin/env python3
"""Chặn regression UI: kiểm target catalog trong ActionScript đã export từ SWF."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from apply_swf_ui_overrides import load_overrides
from swf_lang_localizer import ASSIGN_RE
from translate_gameframe_catalog import TranslationError, decode_as_string


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


class VerifyError(ValueError):
    pass


def parse_lang_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        match = ASSIGN_RE.match(line)
        if not match:
            continue
        index = match.group("index")
        key = (
            f"{match.group('name')}[{int(index)}]"
            if index is not None
            else match.group("name")
        )
        try:
            values[key] = decode_as_string(match.group("value").strip())
        except TranslationError:
            continue
    return values


def merge_expected(catalog_paths: list[Path]) -> dict[str, str]:
    expected: dict[str, str] = {}
    for path in catalog_paths:
        for key, entry in load_overrides(path).items():
            target = entry["target"]
            expected[key] = target
    return expected


def find_source_file(roots: list[Path], relative: str) -> Path:
    candidates = [root / relative for root in roots]
    found = [path for path in candidates if path.is_file()]
    if len(found) != 1:
        raise VerifyError(
            f"Không xác định được source {relative!r}; candidates={candidates}"
        )
    return found[0]


def verify_source_catalogs(roots: list[Path], catalog_paths: list[Path]) -> list[dict]:
    checks: list[dict] = []
    for catalog_path in catalog_paths:
        document = json.loads(catalog_path.read_text(encoding="utf-8"))
        if document.get("format") != 1 or not isinstance(document.get("files"), list):
            raise VerifyError(f"Catalog source sai format: {catalog_path}")
        for file_entry in document["files"]:
            relative = file_entry.get("path")
            if not isinstance(relative, str):
                raise VerifyError(f"Thiếu path trong {catalog_path}")
            content = find_source_file(roots, relative).read_text(encoding="utf-8-sig")
            for replacement in file_entry.get("replacements", []):
                target = replacement.get("verify_target", replacement.get("target"))
                expected_count = replacement.get(
                    "verify_expected",
                    replacement.get("target_expected", replacement.get("expected", 1)),
                )
                if not isinstance(target, str) or not isinstance(expected_count, int):
                    raise VerifyError(f"Replacement không hợp lệ trong {catalog_path}:{relative}")
                actual_count = content.count(target)
                checks.append(
                    {
                        "catalog": str(catalog_path),
                        "path": relative,
                        "target": target,
                        "expected": expected_count,
                        "actual": actual_count,
                    }
                )
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lang-source", type=Path, required=True)
    parser.add_argument("--ui-catalog", type=Path, action="append", default=[])
    parser.add_argument("--source-root", type=Path, action="append", default=[])
    parser.add_argument("--source-catalog", type=Path, action="append", default=[])
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        expected = merge_expected(args.ui_catalog)
        actual = parse_lang_values(args.lang_source)
        missing = sorted(key for key in expected if key not in actual)
        mismatched = [
            {"key": key, "expected": target, "actual": actual[key]}
            for key, target in expected.items()
            if key in actual and actual[key] != target
        ]
        source_checks = verify_source_catalogs(args.source_root, args.source_catalog)
        source_failures = [
            check for check in source_checks if check["actual"] != check["expected"]
        ]
        report = {
            "format": 1,
            "ui_catalog_count": len(args.ui_catalog),
            "ui_key_count": len(expected),
            "ui_missing": missing,
            "ui_mismatched": mismatched,
            "source_checks": source_checks,
            "source_failures": source_failures,
        }
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        if missing or mismatched or source_failures:
            raise VerifyError(
                f"Regression UI: thiếu={len(missing)}, sai target={len(mismatched)}, "
                f"sai source patch={len(source_failures)}"
            )
        print(
            f"Đã xác nhận {len(expected)} key UI và {len(source_checks)} source patch "
            "trong SWF đã export"
        )
    except (OSError, json.JSONDecodeError, VerifyError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
