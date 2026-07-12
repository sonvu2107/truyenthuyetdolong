#!/usr/bin/env python3
"""Sinh catalog hiển thị NPC/quái/item của Nhiệm Vụ từ mapping LogicServer.

Chỉ alias phần chữ người chơi nhìn thấy. ``Location.entityName`` và payload
``/M...`` vẫn là tiếng Trung để tự tìm đường/trả nhiệm vụ không bị ảnh hưởng.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

from cbp_localizer import decode_cbp, walk_strings


ROUTE_PATH_RE = re.compile(
    r"\.(?:prom|comp)\.npc$|\.target\.\d+\.location\.entityName$"
)
HAN_RE = re.compile(r"[\u3400-\u9fff]")

PREFERRED_ENTITY_ALIASES = {
    "毒蜘蛛": "Nhện Độc",
    "剧毒蜘蛛": "Nhện Kịch Độc",
    "花斑蜘蛛": "Nhện Hoa Ban",
}
MANUAL_ITEM_ALIASES = {
    "测试武魂": "Hồn Võ Kiểm Thử",
    "测试经验武魂": "Hồn Võ KN Kiểm Thử",
}


class AliasError(ValueError):
    pass


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_alias(
    mapping: dict[str, str],
    source: str,
    target: str,
    scope: str,
    conflicts: list[dict[str, str]] | None = None,
) -> None:
    if not source or source == target:
        return
    existing = mapping.get(source)
    if existing is not None and existing != target:
        if conflicts is None:
            raise AliasError(f"Alias xung đột tại {scope}: {source!r}")
        conflicts.append({"scope": scope, "source": source, "kept": existing, "ignored": target})
        return
    mapping[source] = target


def load_mappings(path: Path) -> tuple[dict[str, str], dict[str, str], list[dict[str, str]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("blocked") is True:
        raise AliasError(f"Catalog LogicServer bị khóa: {path}")
    if data.get("format") != 1 or not isinstance(data.get("files"), dict):
        raise AliasError(f"Catalog LogicServer không hợp lệ: {path}")
    entities: dict[str, str] = {}
    items: dict[str, str] = {}
    conflicts: list[dict[str, str]] = []
    for filename, mapping in (("EntityName.txt", entities), ("Item.txt", items)):
        entries = data["files"].get(filename, {}).get("entries")
        if not isinstance(entries, list):
            raise AliasError(f"Thiếu entries cho {filename}")
        for entry in entries:
            if not isinstance(entry, dict):
                raise AliasError(f"Entry không hợp lệ trong {filename}")
            key = entry.get("key")
            source = entry.get("source")
            target = entry.get("target")
            if not all(isinstance(value, str) for value in (key, source, target)):
                raise AliasError(f"Kiểu entry sai trong {filename}")
            if filename == "Item.txt" and not key.startswith("n"):
                continue
            add_alias(mapping, source, target, filename, conflicts)
    for source, target in list(entities.items()):
        entities[source] = target.replace("Tri Chu", "Nhện").strip()
    entities.update(PREFERRED_ENTITY_ALIASES)
    items.update(MANUAL_ITEM_ALIASES)
    return entities, items, conflicts


def read_cbp(zip_path: Path, filename: str):
    with zipfile.ZipFile(zip_path) as archive:
        try:
            data = archive.read(filename)
        except KeyError as exc:
            raise AliasError(f"Thiếu {filename} trong {zip_path}") from exc
    _, root, _ = decode_cbp(data)
    return root


def cbp_name_catalog(root, aliases: dict[str, str], filename: str, description: str) -> tuple[dict, list[str]]:
    translations: dict[str, dict[str, str]] = {}
    unmapped: list[str] = []
    for path, node in walk_strings(root):
        if not path.endswith(".name") or not HAN_RE.search(node.text):
            continue
        target = aliases.get(node.text)
        if target:
            translations[path] = {"source": node.text, "target": target}
        else:
            unmapped.append(f"{path}:{node.text}")
    return {
        "format": 1,
        "file": filename,
        "description": description,
        "translations": translations,
    }, unmapped


def build_quest_patch(aliases: dict[str, str]) -> dict:
    rows = [
        "         " + json.dumps(source, ensure_ascii=False) + ":" + json.dumps(target, ensure_ascii=False)
        for source, target in sorted(aliases.items())
    ]
    alias_object = ",\n".join(rows)
    insertion_source = "      private static var QuestTypeName:Array;\n"
    insertion_target = (
        insertion_source
        + "      \n"
        + "      private static var QuestNpcDisplayNames:Object = {\n"
        + alias_object
        + "\n      };\n"
        + "      \n"
        + "      private static function getQuestNpcDisplayName(param1:String) : String\n"
        + "      {\n"
        + "         var _loc2_:String = null;\n"
        + "         if(!param1)\n"
        + "         {\n"
        + "            return param1;\n"
        + "         }\n"
        + "         _loc2_ = QuestNpcDisplayNames[param1] as String;\n"
        + "         return !!_loc2_?_loc2_:param1;\n"
        + "      }\n"
    )
    replacements = [
        {
            "source": insertion_source,
            "target": insertion_target,
            "verify_target": "      private static var QuestNpcDisplayNames:Object = {",
        },
        {
            "source": "HyperlinkHandler.createPFTLink(_loc6_,_loc4_.npc)",
            "target": "HyperlinkHandler.createPFTLink(_loc6_,getQuestNpcDisplayName(_loc4_.npc))",
        },
        {
            "source": "HyperlinkHandler.createPathfindingLink(_loc6_,_loc4_.npc)",
            "target": "HyperlinkHandler.createPathfindingLink(_loc6_,getQuestNpcDisplayName(_loc4_.npc))",
        },
        {
            "source": "_loc4_ = _loc4_.replace(\"$TARGESOURCE$\",_loc6_ && _loc6_.entityName != \"\"?_loc6_.entityName:\"Chưa được định cấu hình\");",
            "target": "_loc4_ = _loc4_.replace(\"$TARGESOURCE$\",getQuestNpcDisplayName(_loc6_ && _loc6_.entityName != \"\"?_loc6_.entityName:\"Chưa được định cấu hình\"));",
        },
        {
            "source": "HyperlinkHandler.createPFTLink(_loc6_,_loc6_ && _loc6_.entityName != \"\"?_loc6_.entityName:\"Chưa được định cấu hình\")",
            "target": "HyperlinkHandler.createPFTLink(_loc6_,getQuestNpcDisplayName(_loc6_ && _loc6_.entityName != \"\"?_loc6_.entityName:\"Chưa được định cấu hình\"))",
            "expected": 2,
        },
        {
            "source": "HyperlinkHandler.createPFTLink(_loc6_.location,!!_loc6_.entityName?_loc6_.entityName:\"không tìm thấy\")",
            "target": "HyperlinkHandler.createPFTLink(_loc6_.location,getQuestNpcDisplayName(!!_loc6_.entityName?_loc6_.entityName:\"không tìm thấy\"))",
        },
        {
            "source": "_loc3_ = _loc3_ + (\":\" + _loc6_.location.entityName + \"<BR>\");",
            "target": "_loc3_ = _loc3_ + (\":\" + getQuestNpcDisplayName(_loc6_.location.entityName) + \"<BR>\");",
        },
        {
            "source": "_loc3_ = _loc3_ + (\":\" + _loc8_.npc + \"<BR>\");",
            "target": "_loc3_ = _loc3_ + (\":\" + getQuestNpcDisplayName(_loc8_.npc) + \"<BR>\");",
        },
    ]
    return {
        "format": 1,
        "description": "Alias tên NPC/quái của Nhiệm Vụ; Location.entityName vẫn giữ khóa route gốc.",
        "files": [{"path": "scripts/model/hlp/QuestHlp.as", "replacements": replacements}],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cbp-zip", type=Path, required=True)
    parser.add_argument("--logicserver-catalog", type=Path, required=True)
    parser.add_argument("--quest-patch-output", type=Path, required=True)
    parser.add_argument("--monster-output", type=Path, required=True)
    parser.add_argument("--item-output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    try:
        entity_aliases, item_aliases, mapping_conflicts = load_mappings(args.logicserver_catalog)
        quest_root = read_cbp(args.cbp_zip, "stdquest.cbp")
        quest_aliases: dict[str, str] = {}
        missing_quest_aliases: list[str] = []
        route_fields = 0
        for path, node in walk_strings(quest_root):
            if not ROUTE_PATH_RE.search(path) or not node.text:
                continue
            route_fields += 1
            target = entity_aliases.get(node.text)
            if target is None:
                missing_quest_aliases.append(f"{path}:{node.text}")
            else:
                add_alias(quest_aliases, node.text, target, "stdquest route")

        monster_catalog, missing_monsters = cbp_name_catalog(
            read_cbp(args.cbp_zip, "monster.cbp"),
            entity_aliases,
            "monster.cbp",
            "Dịch tên quái hiển thị theo alias LogicServer; không đổi entityName route.",
        )
        item_catalog, missing_items = cbp_name_catalog(
            read_cbp(args.cbp_zip, "stditems.cbp"),
            item_aliases,
            "stditems.cbp",
            "Dịch tên item hiển thị theo catalog LogicServer.",
        )
        write_json(args.quest_patch_output, build_quest_patch(quest_aliases))
        write_json(args.monster_output, monster_catalog)
        write_json(args.item_output, item_catalog)
        report = {
            "quest_route_fields": route_fields,
            "quest_aliases": len(quest_aliases),
            "missing_quest_aliases": missing_quest_aliases,
            "monster_translations": len(monster_catalog["translations"]),
            "missing_monster_names": missing_monsters,
            "item_translations": len(item_catalog["translations"]),
            "missing_item_names": missing_items,
            "mapping_conflicts": mapping_conflicts,
        }
        write_json(args.report, report)
        print(
            f"Alias Quest={len(quest_aliases)}, Monster={len(monster_catalog['translations'])}, "
            f"Item={len(item_catalog['translations'])}"
        )
        return 0
    except (AliasError, OSError, json.JSONDecodeError, zipfile.BadZipFile, ValueError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
