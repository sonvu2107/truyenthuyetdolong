#!/usr/bin/env python3
"""Chuẩn hóa tên tiền tệ và căn lại phần chân Hành Trang bằng bản vá AVM2 tối thiểu."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


STRING_REPLACEMENTS = {
    "Sắp Xếp,Tách,Bày Bán,Túi Sự Kiện,Kho Tầm Bảo":
        "Sắp Xếp,Tách,Bày Bán,Túi Sự Kiện,Tầm Bảo",
    "<font letterspacing='0'>Kim Tệ</font>":
        "<font letterspacing='0'>Xu</font>",
    "<font letterspacing='0'>Kim Tệ Khóa</font>":
        "<font letterspacing='0'>Xu Khóa</font>",
}

# _moneyPanel.move(45, 10 - 6) -> _moneyPanel.move(75, 10 - 6).
# Cùng độ dài bytecode, không thay metadata, scope hoặc nhánh điều khiển.
MONEY_PANEL_PATCH = (
    "66c444242d240a2406a14fb30a02",
    "66c444244b240a2406a14fb30a02",
)


def pcode_hex(path: Path, marker: str) -> str:
    source = path.read_text(encoding="utf-8-sig")
    marker_at = source.find(marker)
    if marker_at < 0:
        raise ValueError(f"Không tìm thấy method {marker!r} trong {path}")
    code_marker = source.find("code", marker_at)
    code_at = source.find("\n", code_marker) + 1
    code_end = source.find("end ; code", code_at)
    if code_marker < 0 or code_at <= 0 or code_end < 0:
        raise ValueError(f"Không đọc được code của {marker!r}")
    chunks = []
    for raw_line in source[code_at:code_end].splitlines():
        line = raw_line.strip()
        if line.startswith("; "):
            chunks.append(line[2:].replace(" ", ""))
    result = "".join(chunks).lower()
    if not result:
        raise ValueError(f"File không phải P-codeHex: {path}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-xml", type=Path, required=True)
    parser.add_argument("--backpack-pcodehex", type=Path, required=True)
    parser.add_argument("--output-xml", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    tree = ET.parse(args.input_xml)
    root = tree.getroot()
    items = list(root.iter("item"))
    report: dict[str, object] = {"strings": []}

    for source, target in STRING_REPLACEMENTS.items():
        hits = [item for item in items if item.text == source]
        if len(hits) != 1:
            raise SystemExit(f"Chuỗi nguồn không duy nhất ({len(hits)}): {source!r}")
        hits[0].text = target
        report["strings"].append({"source": source, "target": target})

    expected = pcode_hex(args.backpack_pcodehex, "public function BackPackWin()")
    bodies = [item for item in items if item.attrib.get("type") == "MethodBody"]
    hits = [
        (index, body)
        for index, body in enumerate(bodies)
        if body.attrib.get("codeBytes", "").lower() == expected
    ]
    if len(hits) != 1:
        raise SystemExit(f"Không xác định duy nhất constructor BackPackWin: {[i for i, _ in hits]}")
    body_index, body = hits[0]
    code = body.attrib["codeBytes"].lower()
    source_bytes, target_bytes = MONEY_PANEL_PATCH
    if code.count(source_bytes) != 1:
        raise SystemExit(f"Mẫu moneyPanel xuất hiện {code.count(source_bytes)} lần")
    if len(source_bytes) != len(target_bytes):
        raise SystemExit("Bản vá moneyPanel làm đổi độ dài bytecode")
    code = code.replace(source_bytes, target_bytes, 1)
    body.attrib["codeBytes"] = code

    report["bytecode"] = {
        "method_body": body_index,
        "method_info": int(body.attrib["method_info"]),
        "change": "_moneyPanel.x: 45 -> 75",
        "code_length_unchanged": True,
        "metadata_unchanged": True,
    }

    args.output_xml.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output_xml, encoding="utf-8", xml_declaration=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
