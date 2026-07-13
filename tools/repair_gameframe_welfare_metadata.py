#!/usr/bin/env python3
"""Repair AVM2 method metadata damaged by the welfare method-body transplant.

The replacement bodies were compiled with additional local registers, but the
release SWF accidentally retained the original method-body limits.  This tool
updates only the seven audited bodies and removes the obsolete activation
metadata from LandingRewardCell1.data/set.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


BODY_FIXES = {
    9776: {"max_regs": "4", "max_stack": "4", "init_scope_depth": "14", "max_scope_depth": "15"},
    9777: {"max_regs": "7", "max_stack": "4", "init_scope_depth": "14", "max_scope_depth": "15"},
    9783: {"max_regs": "13", "max_stack": "7", "init_scope_depth": "14", "max_scope_depth": "15"},
    9796: {"max_regs": "4", "max_stack": "6", "init_scope_depth": "14", "max_scope_depth": "15"},
    9801: {"max_regs": "5", "max_stack": "3", "init_scope_depth": "14", "max_scope_depth": "15"},
    27718: {"max_regs": "7", "max_stack": "7", "init_scope_depth": "12", "max_scope_depth": "13"},
    27720: {"max_regs": "2", "max_stack": "3", "init_scope_depth": "12", "max_scope_depth": "13"},
}

LANDING_SETTER_BODY = 27718
LANDING_SETTER_METHOD_INFO = 27939


def indexed_items(root: ET.Element, item_type: str) -> list[ET.Element]:
    return [item for item in root.iter("item") if item.attrib.get("type") == item_type]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_xml", type=Path)
    parser.add_argument("output_xml", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    tree = ET.parse(args.input_xml)
    root = tree.getroot()
    bodies = indexed_items(root, "MethodBody")
    methods = indexed_items(root, "MethodInfo")

    if len(bodies) != 28143:
        raise SystemExit(f"Số MethodBody không đúng: {len(bodies)} (cần 28143)")
    if len(methods) <= LANDING_SETTER_METHOD_INFO:
        raise SystemExit(f"Thiếu MethodInfo {LANDING_SETTER_METHOD_INFO}")

    report: dict[str, object] = {"method_body_count": len(bodies), "changes": []}
    changes = report["changes"]
    assert isinstance(changes, list)

    for index, expected in BODY_FIXES.items():
        body = bodies[index]
        before = {key: body.attrib.get(key) for key in expected}
        body.attrib.update(expected)
        changes.append({"body_index": index, "before": before, "after": expected})

    setter = bodies[LANDING_SETTER_BODY]
    traits = setter.find("traits")
    removed_activation_nodes = 0
    if traits is not None:
        removed_activation_nodes = len(list(traits))
        for child in list(traits):
            traits.remove(child)

    method = methods[LANDING_SETTER_METHOD_INFO]
    old_flags = method.attrib.get("flags")
    method.attrib["flags"] = "0"
    report["landing_setter"] = {
        "method_info": LANDING_SETTER_METHOD_INFO,
        "flags_before": old_flags,
        "flags_after": "0",
        "removed_activation_nodes": removed_activation_nodes,
    }

    args.output_xml.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output_xml, encoding="utf-8", xml_declaration=True)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
