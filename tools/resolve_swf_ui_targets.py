#!/usr/bin/env python3
"""Chốt source hiện tại cho catalog target UI trước khi áp vào ZH_CN.as."""

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--targets", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        payload = json.loads(args.targets.read_text(encoding="utf-8"))
        targets = payload.get("targets")
        if payload.get("format") != 1 or not isinstance(targets, dict):
            raise ValueError("Catalog target phải có format=1 và targets")

        current: dict[str, str] = {}
        for line in args.source.read_text(encoding="utf-8-sig").splitlines(True):
            match = ASSIGN_RE.match(line)
            if not match:
                continue
            index = match.group("index")
            key = (
                f"{match.group('name')}[{int(index)}]"
                if index is not None
                else match.group("name")
            )
            if key not in targets:
                continue
            current[key] = decode_as_string(match.group("value").strip())

        missing = sorted(set(targets) - set(current))
        if missing:
            raise ValueError(f"Không tìm thấy {len(missing)} khóa: {missing}")
        overrides = {}
        for key, entry in targets.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("target"), str):
                raise ValueError(f"Target không hợp lệ: {key}")
            if current[key] == entry["target"]:
                raise ValueError(f"Target không thay đổi: {key}")
            overrides[key] = {
                "source": current[key],
                "target": entry["target"],
                "category": entry.get("category", ""),
            }
        result = {
            "format": 1,
            "description": payload.get("description", "Catalog UI đã chốt source"),
            "overrides": overrides,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"Đã chốt source cho {len(overrides)} target UI")
        return 0
    except (OSError, json.JSONDecodeError, ValueError, TranslationError) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
