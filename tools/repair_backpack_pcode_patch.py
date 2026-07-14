#!/usr/bin/env python3
"""Ghép metadata AVM2 an toàn cho bản vá Hành Trang và đổi một hằng chuỗi."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET


BODY_SPECS = (
    {
        "name": "MoneyIcon.money/set",
        "target": 4051,
        "compiler_xml": "money",
        "pcode": "money",
        "marker": "public function set money(param1:uint)",
    },
    {
        "name": "BackPackPanicBuyPage.timeFormat",
        "target": 19665,
        "compiler_xml": "countdown",
        "pcode": "panic",
        "marker": "private function timeFormat",
    },
    {
        "name": "BackPackAuctionPage.timeFormat",
        "target": 19685,
        "compiler_xml": "countdown",
        "pcode": "auction",
        "marker": "private function timeFormat",
    },
)

BODY_META = ("max_regs", "max_stack", "init_scope_depth", "max_scope_depth")
SOURCE_CURRENCY = "<font letterspacing='0'>Đậu Hạnh Phúc</font>"
TARGET_CURRENCY = "<font letterspacing='0'>Đậu Vui Vẻ</font>"


def indexed_items(root: ET.Element, item_type: str) -> list[ET.Element]:
    return [item for item in root.iter("item") if item.attrib.get("type") == item_type]


def pcode_hex(path: Path, marker: str) -> str:
    source = path.read_text(encoding="utf-8-sig")
    marker_at = source.find(marker)
    if marker_at < 0:
        raise ValueError(f"Không tìm thấy method {marker!r} trong {path}")
    code_at = source.find("\n", source.find("code", marker_at)) + 1
    code_end = source.find("end ; code", code_at)
    if code_at <= 0 or code_end < 0:
        raise ValueError(f"Không đọc được code của {marker!r} trong {path}")
    chunks = []
    for raw_line in source[code_at:code_end].splitlines():
        line = raw_line.strip()
        if line.startswith("; "):
            chunks.append(line[2:].replace(" ", ""))
    result = "".join(chunks).lower()
    if not result:
        raise ValueError(f"File không phải P-codeHex: {path}")
    return result


def element_bytes(element: ET.Element) -> bytes:
    return ET.tostring(element, encoding="utf-8")


def restore_element(target: ET.Element, source: ET.Element) -> None:
    target.clear()
    target.attrib.update(source.attrib)
    target.text = source.text
    target.tail = source.tail
    for child in list(source):
        target.append(copy.deepcopy(child))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-xml", type=Path, required=True)
    parser.add_argument("--replaced-xml", type=Path, required=True)
    parser.add_argument("--money-compiler-xml", type=Path, required=True)
    parser.add_argument("--countdown-compiler-xml", type=Path, required=True)
    parser.add_argument("--money-pcodehex", type=Path, required=True)
    parser.add_argument("--panic-pcodehex", type=Path, required=True)
    parser.add_argument("--auction-pcodehex", type=Path, required=True)
    parser.add_argument("--output-xml", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    base_tree = ET.parse(args.base_xml)
    output_tree = ET.parse(args.replaced_xml)
    compiler_trees = {
        "money": ET.parse(args.money_compiler_xml),
        "countdown": ET.parse(args.countdown_compiler_xml),
    }
    pcode_paths = {
        "money": args.money_pcodehex,
        "panic": args.panic_pcodehex,
        "auction": args.auction_pcodehex,
    }

    base_root = base_tree.getroot()
    output_root = output_tree.getroot()
    base_bodies = indexed_items(base_root, "MethodBody")
    output_bodies = indexed_items(output_root, "MethodBody")
    base_methods = indexed_items(base_root, "MethodInfo")
    output_methods = indexed_items(output_root, "MethodInfo")
    if len(base_bodies) != 28143 or len(output_bodies) != len(base_bodies):
        raise SystemExit(
            f"Số MethodBody lệch: base={len(base_bodies)}, output={len(output_bodies)}"
        )
    if len(output_methods) != len(base_methods):
        raise SystemExit(
            f"Số MethodInfo lệch: base={len(base_methods)}, output={len(output_methods)}"
        )

    target_indexes = {int(spec["target"]) for spec in BODY_SPECS}
    restored_bodies = []
    for index, (base, output) in enumerate(zip(base_bodies, output_bodies)):
        if index not in target_indexes and element_bytes(base) != element_bytes(output):
            restore_element(output, base)
            restored_bodies.append(index)

    report: dict[str, object] = {
        "body_count": len(base_bodies),
        "restored_non_target_bodies": restored_bodies,
        "changes": [],
    }
    changes = report["changes"]
    assert isinstance(changes, list)
    for spec in BODY_SPECS:
        target_index = int(spec["target"])
        base_body = base_bodies[target_index]
        output_body = output_bodies[target_index]
        if base_body.attrib.get("codeBytes") == output_body.attrib.get("codeBytes"):
            raise SystemExit(f"Body mục tiêu chưa đổi: {spec['name']}")

        compiler_root = compiler_trees[str(spec["compiler_xml"])].getroot()
        compiler_bodies = indexed_items(compiler_root, "MethodBody")
        expected_hex = pcode_hex(
            pcode_paths[str(spec["pcode"])], str(spec["marker"])
        )
        compiler_hits = [
            (index, body)
            for index, body in enumerate(compiler_bodies)
            if body.attrib.get("codeBytes", "").lower() == expected_hex
        ]
        if len(compiler_hits) != 1:
            raise SystemExit(
                f"Không xác định duy nhất body compiler cho {spec['name']}: "
                f"{[index for index, _ in compiler_hits]}"
            )
        compiler_index, compiler_body = compiler_hits[0]
        before_meta = {key: output_body.attrib.get(key) for key in BODY_META}
        for key in BODY_META:
            output_body.attrib[key] = compiler_body.attrib[key]
        for child in list(output_body):
            output_body.remove(child)
        for child in list(compiler_body):
            output_body.append(copy.deepcopy(child))

        method_info = int(base_body.attrib["method_info"])
        output_body.attrib["method_info"] = base_body.attrib["method_info"]
        changes.append(
            {
                "name": spec["name"],
                "target_body": target_index,
                "compiler_body": compiler_index,
                "method_info": method_info,
                "metadata_before": before_meta,
                "metadata_after": {key: output_body.attrib[key] for key in BODY_META},
            }
        )

    currency_hits = [
        item for item in output_root.iter("item") if item.text == SOURCE_CURRENCY
    ]
    if len(currency_hits) != 1:
        raise SystemExit(f"Số hằng tiền tệ nguồn không đúng: {len(currency_hits)}")
    currency_hits[0].text = TARGET_CURRENCY
    report["currency"] = {"source": SOURCE_CURRENCY, "target": TARGET_CURRENCY}

    for base, output in zip(base_methods, output_methods):
        restore_element(output, base)
    for index, (base, output) in enumerate(zip(base_methods, output_methods)):
        if element_bytes(base) != element_bytes(output):
            raise SystemExit(f"MethodInfo chưa khôi phục đúng tại chỉ số {index}")

    args.output_xml.parent.mkdir(parents=True, exist_ok=True)
    output_tree.write(args.output_xml, encoding="utf-8", xml_declaration=True)
    if args.report:
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
