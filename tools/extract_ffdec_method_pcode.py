#!/usr/bin/env python3
"""Tách phần lệnh của một method từ file P-code/P-codeHex do FFDec xuất."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--marker", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8-sig")
    marker_at = source.find(args.marker)
    if marker_at < 0:
        raise SystemExit(f"Không tìm thấy method: {args.marker}")
    code_at = source.find("\n", source.find("code", marker_at)) + 1
    code_end = source.find("end ; code", code_at)
    if code_at <= 0 or code_end < 0:
        raise SystemExit(f"Không tách được khối code: {args.marker}")

    output: list[str] = []
    for raw_line in source[code_at:code_end].splitlines():
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue
        output.append(line)

    if not output or output[-1] not in {"returnvoid", "returnvalue"}:
        raise SystemExit(f"P-code tách ra không có lệnh return cuối: {args.marker}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(output) + "\n", encoding="utf-8", newline="\n")
    print(f"Đã tách {len(output)} dòng P-code: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
