#!/usr/bin/env python3
"""Việt hóa catalog vật phẩm AMF3 ``items.cbp`` trong gói CBP.

Client production đặt ``ResourceLoader.isVal = true`` nên nguồn vật phẩm cuối
cùng là ``items.cbp`` (ByteArray nén zlib chứa một mảng AMF3), không phải
``stditems.cbp``. Công cụ này giữ nguyên bốn class alias/trait mà Flash cần,
kiểm câu nguồn trước khi sửa và giải mã lại đầu ra để tránh tạo gói lỗi.
"""

from __future__ import annotations

import argparse
import json
import sys
import zlib
import zipfile
from pathlib import Path

try:
    import pyamf
    from pyamf import amf3
    from pyamf.util import BufferedByteStream
except ImportError as exc:  # pragma: no cover - thông báo dành cho máy build
    raise SystemExit(
        "Thiếu Py3AMF. Cài bằng: pip install -r tools/requirements-amf3.txt"
    ) from exc


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


ITEM_ATTRS = [
    "effectOffsetX", "effectOffsetY", "name", "runeLevel",
    "btRuneMailProperty", "breakId", "openUi", "dura", "icon",
    "dropEffect", "weight", "dropBroadcast", "smithId", "desc", "conds",
    "runeSubProperty", "shape", "nameColor", "grownupAttrs", "shape2",
    "param_type", "type", "runeMailProperty", "dealType", "shakeFrame",
    "extendsDesc", "suitId", "smithCount", "useDurDrop", "staitcAttrs",
    "cdTime", "validFbId", "candidateIconCount", "id", "validSceneId",
    "colorEffect", "btRuneLevel", "colGroup", "dealPrice", "time",
    "existScenes", "btRuneSubProperty", "param_value", "flags",
    "maxSmithAttrs", "btRuneIdentifyNumber", "maxstrong", "showQuality",
    "dup", "qualityAttrs", "strongAttrs", "initSmithId",
]

FLAG_ATTRS = [
    "denyDestroy", "fullDel", "denyStorage", "canDig", "denyBuffOverlay",
    "offlineDropdown", "denyDropDua", "denyDopDua", "denyTipsAutoLine",
    "denyDeal", "autoStartTime", "denyHeroUse", "skillRemoveItem",
    "showLootTips", "hideDura", "canChange", "prompt", "useOnPractice",
    "monAlwaysDropdown", "notShowAppear", "diamondAlwaysActive", "cankiss",
    "notConsumeForCircleForge", "destroyOnOffline", "bagSell", "dieDropdown",
    "denySell", "autoBindOnTake", "recordLog", "denySplite", "denyRepair",
    "denyDropdown", "destroyOnDie", "inlayable", "asQuestItem",
    "matchAllSuit", "hideQualityName",
]

ALIASES = {
    "common.Data.Items.std": ITEM_ATTRS,
    "StdItemCondition": ["value", "cond"],
    "common.Data.Attribute": ["value", "type"],
    "common.Data.Items.type": FLAG_ATTRS,
}


def register_aliases() -> dict[str, type]:
    classes: dict[str, type] = {}
    for alias, attrs in ALIASES.items():
        cls = type(
            alias.replace(".", "_"),
            (),
            {"__amf__": {"static": attrs, "dynamic": False}},
        )
        pyamf.register_class(cls, alias)
        classes[alias] = cls
    return classes


CLASSES = register_aliases()


def decode_items(data: bytes) -> list:
    try:
        payload = zlib.decompress(data)
        items = amf3.Decoder(payload).readElement()
    except Exception as exc:
        raise ValueError(f"Không giải mã được items.cbp: {exc}") from exc
    if not isinstance(items, list):
        raise ValueError("Gốc items.cbp không phải mảng AMF3")
    for index, item in enumerate(items):
        if not isinstance(item, CLASSES["common.Data.Items.std"]):
            raise ValueError(f"Vật phẩm {index} sai class alias")
        if item.id != index:
            raise ValueError(f"Vật phẩm tại chỉ số {index} có id={item.id!r}")
    return items


def encode_items(items: list) -> bytes:
    stream = BufferedByteStream()
    amf3.Encoder(stream).writeElement(items)
    output = zlib.compress(stream.getvalue(), level=9)
    checked = decode_items(output)
    if len(checked) != len(items):
        raise ValueError("Số vật phẩm sau mã hóa không khớp")
    return output


def load_catalog(path: Path) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("format") != 1 or not isinstance(catalog.get("translations"), dict):
        raise ValueError("Catalog dịch không đúng format 1")
    return catalog


def parse_item_files(paths: list[Path]) -> dict[str, str]:
    # Dùng lại parser Lua đã được kiểm chứng của bộ CBP thường.
    from cbp_localizer import parse_item_files as parse_files

    values, _ = parse_files(paths)
    return values


def make_catalog(items: list, source_paths: list[Path], target_paths: list[Path]) -> dict:
    source_values = parse_item_files(source_paths)
    target_values = parse_item_files(target_paths)
    translations: dict[str, dict[str, str]] = {}
    missing_targets: list[str] = []
    source_mismatches: list[str] = []
    for node_path, source in sorted(source_values.items()):
        target = target_values.get(node_path)
        if target is None:
            missing_targets.append(node_path)
            continue
        item_id_text, field = node_path.rsplit(".", 1)
        item_id = int(item_id_text)
        if item_id >= len(items) or getattr(items[item_id], field, None) != source:
            source_mismatches.append(node_path)
            continue
        if target != source:
            translations[node_path] = {"source": source, "target": target}
    return {
        "format": 1,
        "file": "items.cbp",
        "description": "Việt hóa catalog AMF3 thực tế mà client production sử dụng",
        "translations": translations,
        "metadata": {
            "source_entries": len(source_values),
            "matched_and_changed": len(translations),
            "missing_target_paths": missing_targets,
            "source_mismatch_paths": source_mismatches,
        },
    }


def apply_catalog(items: list, catalog: dict) -> int:
    changed = 0
    for node_path, entry in catalog["translations"].items():
        try:
            item_id_text, field = node_path.rsplit(".", 1)
            item_id = int(item_id_text)
        except (ValueError, AttributeError) as exc:
            raise ValueError(f"Khóa catalog không hợp lệ: {node_path!r}") from exc
        if field not in ("name", "desc"):
            raise ValueError(f"Không cho phép sửa trường {field!r}")
        if item_id < 0 or item_id >= len(items):
            raise ValueError(f"Không có vật phẩm {item_id}")
        source = entry.get("source")
        target = entry.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            raise ValueError(f"Bản dịch {node_path} thiếu source/target chuỗi")
        current = getattr(items[item_id], field)
        if current != source:
            raise ValueError(
                f"Lệch nguồn tại {node_path}: hiện tại={current!r}, catalog={source!r}"
            )
        setattr(items[item_id], field, target)
        changed += 1
    return changed


def rewrite_zip(input_zip: Path, output_zip: Path, replacement: bytes) -> None:
    found = 0
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(input_zip, "r") as source, zipfile.ZipFile(output_zip, "w") as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename.lower() == "items.cbp":
                data = replacement
                found += 1
            target.writestr(info, data, compress_type=info.compress_type, compresslevel=9)
    if found != 1:
        output_zip.unlink(missing_ok=True)
        raise ValueError(f"Gói ZIP phải có đúng một items.cbp, thực tế: {found}")
    with zipfile.ZipFile(output_zip, "r") as checked:
        bad = checked.testzip()
        if bad:
            raise ValueError(f"CRC lỗi sau khi ghi ZIP: {bad}")
        decode_items(checked.read("items.cbp"))


def command_apply_zip(args: argparse.Namespace) -> None:
    with zipfile.ZipFile(args.input_zip, "r") as archive:
        source = archive.read("items.cbp")
    items = decode_items(source)
    changed = 0
    for catalog_path in args.catalog:
        changed += apply_catalog(items, load_catalog(catalog_path))
    replacement = encode_items(items)
    rewrite_zip(args.input_zip, args.output_zip, replacement)
    print(
        f"Đã Việt hóa {changed} chuỗi trong {len(items)} vật phẩm; "
        f"items.cbp {len(source)} -> {len(replacement)} byte"
    )


def command_catalog(args: argparse.Namespace) -> None:
    with zipfile.ZipFile(args.input_zip, "r") as archive:
        items = decode_items(archive.read("items.cbp"))
    catalog = make_catalog(items, args.source, args.target)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    metadata = catalog["metadata"]
    print(
        f"Đã tạo {args.output}: {metadata['matched_and_changed']} câu; "
        f"lệch nguồn={len(metadata['source_mismatch_paths'])}, "
        f"thiếu đích={len(metadata['missing_target_paths'])}"
    )


def command_validate_zip(args: argparse.Namespace) -> None:
    with zipfile.ZipFile(args.input_zip, "r") as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError(f"CRC lỗi: {bad}")
        items = decode_items(archive.read("items.cbp"))
    print(f"Hợp lệ: {len(items)} vật phẩm; ID 907={items[907].name!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    catalog = sub.add_parser("catalog")
    catalog.add_argument("--input-zip", type=Path, required=True)
    catalog.add_argument("--source", type=Path, action="append", required=True)
    catalog.add_argument("--target", type=Path, action="append", required=True)
    catalog.add_argument("--output", type=Path, required=True)
    catalog.set_defaults(func=command_catalog)
    apply_zip = sub.add_parser("apply-zip")
    apply_zip.add_argument("--input-zip", type=Path, required=True)
    apply_zip.add_argument("--catalog", type=Path, action="append", required=True)
    apply_zip.add_argument("--output-zip", type=Path, required=True)
    apply_zip.set_defaults(func=command_apply_zip)
    validate_zip = sub.add_parser("validate-zip")
    validate_zip.add_argument("--input-zip", type=Path, required=True)
    validate_zip.set_defaults(func=command_validate_zip)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
