#!/usr/bin/env python3
"""Biên dịch bản dịch vào CBP mà không làm hỏng dữ liệu nhị phân.

Các lệnh chính:
  skill-catalog  Tạo catalog JSON từ Skill.txt và skillconfig.cbp sạch.
  item-catalog   Tạo catalog JSON từ Item gốc và Item tiếng Việt.
  value-catalog  Tạo catalog từ các file Lua đối chiếu theo cùng khóa.
  merge-catalogs Gộp các catalog cùng CBP, kiểm tra xung đột từng node.
  apply          Áp catalog vào một file CBP.
  apply-zip      Áp catalog vào đúng file bên trong cbp.zip.
  validate       Đọc và kiểm tra toàn bộ cây của một file CBP.
"""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
import zlib
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


CBP_MAGIC = 5_259_843
CBP_VERSION = 17_435_658
HEADER_SIZE = 64

QUEST_ROUTE_PATH_PATTERN = re.compile(
    r"(?:^|\.)(?:comp|prom)\.(?:scene|npc)$"
    r"|\.target\.\d+\.location\.(?:entityName|sceneName)$"
)
QUEST_MOVE_LINK_PATTERN = re.compile(r"<[^<>]*/M([^<>]*)>")


class CbpError(ValueError):
    pass


@dataclass
class Node:
    name: str
    kind: int
    padding: bytes = b"\0\0\0\0"
    raw_value: bytes = b""
    text: str = ""
    children: list["Node"] = field(default_factory=list)


class Reader:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.position = 0
        self.node_count = 0

    def take(self, size: int) -> bytes:
        if size < 0 or self.position + size > len(self.payload):
            raise CbpError(
                f"Đọc tràn tại byte {self.position}: cần {size}, "
                f"payload chỉ có {len(self.payload)} byte"
            )
        start = self.position
        self.position += size
        return self.payload[start : self.position]

    def read_node(self, depth: int = 0) -> Node:
        if depth > 2_000:
            raise CbpError("Cây CBP lồng quá sâu")
        name_size = self.take(1)[0]
        kind = self.take(1)[0]
        self.node_count += 1

        if kind in (0, 1, 2):
            raw_value = self.take(8)
            name = self.take(name_size).decode("utf-8")
            return Node(name=name, kind=kind, raw_value=raw_value)

        if kind not in (3, 4):
            raise CbpError(f"Kiểu node {kind} không hợp lệ tại node {self.node_count}")

        value = struct.unpack("<I", self.take(4))[0]
        padding = self.take(4)
        name = self.take(name_size).decode("utf-8")
        node = Node(name=name, kind=kind, padding=padding)
        if kind == 3:
            node.text = self.take(value).decode("utf-8")
        else:
            node.children = [self.read_node(depth + 1) for _ in range(value)]
        return node


def decode_cbp(data: bytes) -> tuple[bytearray, Node, int]:
    if len(data) < HEADER_SIZE:
        raise CbpError("File ngắn hơn header CBP 64 byte")
    magic, version, unpacked_size, packed_size = struct.unpack_from("<4I", data)
    if magic != CBP_MAGIC:
        raise CbpError(f"Sai magic CBP: {magic}")
    if version != CBP_VERSION:
        raise CbpError(f"Sai phiên bản CBP: {version}")
    if len(data) < HEADER_SIZE + packed_size:
        raise CbpError(
            f"Luồng zlib bị thiếu: cần {packed_size}, chỉ còn {len(data) - HEADER_SIZE}"
        )
    try:
        payload = zlib.decompress(data[HEADER_SIZE : HEADER_SIZE + packed_size])
    except zlib.error as exc:
        raise CbpError(f"Không giải nén được zlib: {exc}") from exc
    if len(payload) != unpacked_size:
        raise CbpError(
            f"Kích thước payload sai: header={unpacked_size}, thực tế={len(payload)}"
        )

    reader = Reader(payload)
    root = reader.read_node()
    if reader.position != len(payload):
        raise CbpError(f"Payload còn dư {len(payload) - reader.position} byte")
    return bytearray(data[:HEADER_SIZE]), root, reader.node_count


def encode_node(node: Node) -> bytes:
    name = node.name.encode("utf-8")
    if len(name) > 255:
        raise CbpError(f"Tên node dài hơn 255 byte: {node.name!r}")
    output = bytearray((len(name), node.kind))
    if node.kind in (0, 1, 2):
        if len(node.raw_value) != 8:
            raise CbpError(f"Node {node.name!r} thiếu giá trị nhị phân 8 byte")
        output.extend(node.raw_value)
        output.extend(name)
        return bytes(output)

    if node.kind == 3:
        value = node.text.encode("utf-8")
        output.extend(struct.pack("<I", len(value)))
        output.extend(node.padding)
        output.extend(name)
        output.extend(value)
        return bytes(output)

    if node.kind == 4:
        output.extend(struct.pack("<I", len(node.children)))
        output.extend(node.padding)
        output.extend(name)
        for child in node.children:
            output.extend(encode_node(child))
        return bytes(output)

    raise CbpError(f"Không thể ghi kiểu node {node.kind}")


def encode_cbp(header: bytearray, root: Node) -> bytes:
    payload = encode_node(root)
    compressed = zlib.compress(payload, level=9)
    struct.pack_into("<I", header, 0, CBP_MAGIC)
    struct.pack_into("<I", header, 4, CBP_VERSION)
    struct.pack_into("<I", header, 8, len(payload))
    struct.pack_into("<I", header, 12, len(compressed))
    return bytes(header) + compressed


def walk_strings(node: Node, parent: str = "") -> Iterator[tuple[str, Node]]:
    path = f"{parent}.{node.name}" if parent and node.name else (node.name or parent)
    if node.kind == 3:
        yield path, node
    elif node.kind == 4:
        for child in node.children:
            yield from walk_strings(child, path)


def walk_nodes(node: Node, parent: str = "") -> Iterator[tuple[str, Node]]:
    path = f"{parent}.{node.name}" if parent and node.name else (node.name or parent)
    yield path, node
    if node.kind == 4:
        for child in node.children:
            yield from walk_nodes(child, path)


def load_catalog(path: Path) -> dict:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if catalog.get("format") != 1 or not isinstance(catalog.get("translations"), dict):
        raise CbpError("Catalog không đúng format 1")
    return catalog


def is_quest_route_path(path: str) -> bool:
    return bool(QUEST_ROUTE_PATH_PATTERN.search(path))


def quest_move_payloads(text: str) -> list[str]:
    return QUEST_MOVE_LINK_PATTERN.findall(text)


def validate_catalog_translation(
    file_name: str, path: str, source: str, target: str
) -> None:
    if file_name.lower() != "stdquest.cbp":
        return
    if is_quest_route_path(path) and target != source:
        raise CbpError(
            f"Không được dịch khóa định tuyến nhiệm vụ tại {path}: "
            f"{source!r} -> {target!r}"
        )
    source_payloads = quest_move_payloads(source)
    target_payloads = quest_move_payloads(target)
    if source_payloads != target_payloads:
        raise CbpError(
            f"Payload /M bị thay đổi tại {path}: "
            f"source={source_payloads!r}, target={target_payloads!r}"
        )


def apply_catalog(data: bytes, catalog: dict) -> tuple[bytes, int, int]:
    header, root, node_count = decode_cbp(data)
    strings = dict(walk_strings(root))
    changed = 0
    file_name = str(catalog.get("file", ""))
    for path, entry in catalog["translations"].items():
        if path not in strings:
            raise CbpError(f"Catalog tham chiếu node không tồn tại: {path}")
        if not isinstance(entry, dict) or "source" not in entry or "target" not in entry:
            raise CbpError(f"Mục catalog không hợp lệ: {path}")
        node = strings[path]
        if node.text != entry["source"]:
            raise CbpError(
                f"Câu gốc không khớp tại {path}: "
                f"CBP={node.text!r}, catalog={entry['source']!r}"
            )
        target = entry["target"]
        if not isinstance(target, str):
            raise CbpError(f"Câu đích không phải chuỗi tại {path}")
        validate_catalog_translation(file_name, path, entry["source"], target)
        if target != node.text:
            node.text = target
            changed += 1
    output = encode_cbp(header, root)
    decode_cbp(output)
    return output, changed, node_count


def load_datafix(path: Path) -> dict:
    datafix = json.loads(path.read_text(encoding="utf-8"))
    if (
        datafix.get("format") != 1
        or datafix.get("purpose") != "server-parity-datafix"
        or not isinstance(datafix.get("changes"), dict)
    ):
        raise CbpError(
            "Datafix phải có format=1, purpose=server-parity-datafix và changes"
        )
    return datafix


def apply_datafix(data: bytes, datafix: dict) -> tuple[bytes, int, int]:
    """Áp sửa dữ liệu có chủ đích, tách biệt hoàn toàn khỏi catalog dịch thuật."""
    header, root, node_count = decode_cbp(data)
    nodes = dict(walk_nodes(root))
    changed = 0

    for path, entry in datafix["changes"].items():
        node = nodes.get(path)
        if node is None:
            raise CbpError(f"Datafix tham chiếu node không tồn tại: {path}")
        if not isinstance(entry, dict):
            raise CbpError(f"Mục datafix không hợp lệ: {path}")

        kind = entry.get("kind")
        source = entry.get("source")
        target = entry.get("target")
        if kind == "string":
            if node.kind != 3 or not isinstance(source, str) or not isinstance(target, str):
                raise CbpError(f"Datafix string không hợp lệ tại {path}")
            current = node.text
            if current != source:
                raise CbpError(
                    f"Giá trị gốc không khớp tại {path}: "
                    f"CBP={current!r}, datafix={source!r}"
                )
            if current != target:
                node.text = target
                changed += 1
            continue

        if kind == "number":
            if node.kind != 2 or not isinstance(source, (int, float)) or not isinstance(target, (int, float)):
                raise CbpError(f"Datafix number không hợp lệ tại {path}")
            current = struct.unpack("<d", node.raw_value)[0]
            if current != float(source):
                raise CbpError(
                    f"Giá trị gốc không khớp tại {path}: "
                    f"CBP={current!r}, datafix={source!r}"
                )
            if current != float(target):
                node.raw_value = struct.pack("<d", float(target))
                changed += 1
            continue

        if kind == "boolean":
            if node.kind != 1 or not isinstance(source, bool) or not isinstance(target, bool):
                raise CbpError(f"Datafix boolean không hợp lệ tại {path}")
            current = bool(node.raw_value[0])
            if current != source:
                raise CbpError(
                    f"Giá trị gốc không khớp tại {path}: "
                    f"CBP={current!r}, datafix={source!r}"
                )
            if current != target:
                node.raw_value = bytes((1 if target else 0,)) + node.raw_value[1:]
                changed += 1
            continue

        raise CbpError(f"Kiểu datafix không được hỗ trợ tại {path}: {kind!r}")

    output = encode_cbp(header, root)
    _, _, checked_nodes = decode_cbp(output)
    if checked_nodes != node_count:
        raise CbpError("Số node thay đổi sau khi áp datafix")
    return output, changed, checked_nodes


def find_zip_name(names: list[str], wanted: str) -> str:
    matches = [name for name in names if name.lower() == wanted.lower()]
    if len(matches) != 1:
        raise CbpError(f"Không tìm thấy duy nhất {wanted!r} trong ZIP")
    return matches[0]


def read_zip_entry(path: Path, wanted: str) -> bytes:
    with zipfile.ZipFile(path) as archive:
        name = find_zip_name(archive.namelist(), wanted)
        return archive.read(name)


def write_zip_with_replacement(
    input_zip: Path, output_zip: Path, wanted: str, replacement: bytes
) -> None:
    with zipfile.ZipFile(input_zip) as source:
        names = source.namelist()
        actual_name = find_zip_name(names, wanted)
        entries = {name: source.read(name) for name in names}
    entries[actual_name] = replacement
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        output_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as target:
        for name in sorted(entries, key=str.lower):
            target.writestr(name, entries[name])
    with zipfile.ZipFile(output_zip) as check:
        bad = check.testzip()
        if bad:
            raise CbpError(f"ZIP tạo ra bị lỗi CRC tại {bad}")


SKILL_PATTERN = re.compile(
    r's(?P<skill>\d+)(?:L(?P<level>\d+))?'
    r'(?P<field>Name|Desc)="(?P<value>(?:\\.|[^"\\])*)"',
    re.IGNORECASE | re.DOTALL,
)

ITEM_PATTERN = re.compile(
    r'(?P<field>[ni])(?P<item>\d+)\s*=\s*"(?P<value>(?:\\.|[^"\\])*)"',
    re.IGNORECASE | re.DOTALL,
)

LUA_VALUE_PATTERN = re.compile(
    r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*"(?P<value>(?:\\.|[^"\\])*)"',
    re.DOTALL,
)


def unescape_config_string(value: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\" or index + 1 >= len(value):
            output.append(char)
            index += 1
            continue
        nxt = value[index + 1]
        if nxt == "n":
            output.append("\n")
        elif nxt == "r":
            output.append("\r")
        elif nxt == "t":
            output.append("\t")
        else:
            output.append(nxt)
        index += 2
    return "".join(output)


def make_skill_catalog(cbp_data: bytes, skill_text: str, file_name: str) -> dict:
    _, root, _ = decode_cbp(cbp_data)
    strings = dict(walk_strings(root))
    translations: dict[str, dict[str, str]] = {}
    unmatched: list[str] = []

    for match in SKILL_PATTERN.finditer(skill_text):
        skill = match.group("skill")
        level = match.group("level")
        field = match.group("field").lower()
        if level:
            if field != "desc":
                continue
            path = f"{skill}.skillSubLevel.{int(level) - 1}.desc"
        else:
            path = f"{skill}.{field}"
        node = strings.get(path)
        if node is None:
            unmatched.append(path)
            continue
        target = unescape_config_string(match.group("value"))
        if target == node.text:
            continue
        translations[path] = {"source": node.text, "target": target}

    return {
        "format": 1,
        "file": file_name,
        "description": "Việt hóa kỹ năng từ LogicServer/data/language/Zh-CN/Skill.txt",
        "translations": dict(sorted(translations.items())),
        "metadata": {
            "matched_and_changed": len(translations),
            "unmatched_paths": sorted(set(unmatched)),
        },
    }


def parse_item_strings(text: str) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    duplicates: set[str] = set()
    field_names = {"n": "name", "i": "desc"}
    for match in ITEM_PATTERN.finditer(text):
        path = f"{int(match.group('item'))}.{field_names[match.group('field').lower()]}"
        value = unescape_config_string(match.group("value"))
        if path in values:
            duplicates.add(path)
        # File Lua dùng giá trị khai báo sau cùng khi một ID bị lặp.
        values[path] = value
    if not values:
        raise CbpError("Không tìm thấy mục n<ID> hoặc i<ID> trong Item.txt")
    return values, sorted(duplicates)


def parse_item_files(paths: list[Path]) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    duplicates: set[str] = set()
    for path in paths:
        parsed, _ = parse_item_strings(path.read_text(encoding="utf-8-sig"))
        for item_path, value in parsed.items():
            if item_path in values:
                duplicates.add(item_path)
                if values[item_path] != value:
                    raise CbpError(
                        f"Mục vật phẩm mâu thuẫn giữa các file: {item_path}"
                    )
            values[item_path] = value
    return values, sorted(duplicates)


def parse_lua_values(paths: list[Path]) -> tuple[dict[str, str], list[str]]:
    values: dict[str, str] = {}
    duplicates: set[str] = set()
    for path in paths:
        local_values: dict[str, str] = {}
        for match in LUA_VALUE_PATTERN.finditer(path.read_text(encoding="utf-8-sig")):
            key = match.group("key")
            value = unescape_config_string(match.group("value"))
            if key in local_values:
                duplicates.add(key)
            # Lua dùng giá trị sau cùng khi một khóa bị lặp trong cùng file.
            local_values[key] = value
        if not local_values:
            raise CbpError(f"Không tìm thấy chuỗi Lua trong {path}")
        for key, value in local_values.items():
            if key in values and values[key] != value:
                raise CbpError(f"Khóa Lua mâu thuẫn giữa các file: {key}")
            if key in values:
                duplicates.add(key)
            values[key] = value
    return values, sorted(duplicates)


def make_value_catalog(
    cbp_data: bytes,
    source_paths: list[Path],
    target_paths: list[Path],
    file_name: str,
    allow_partial: bool = False,
) -> dict:
    _, root, _ = decode_cbp(cbp_data)
    source_values, source_duplicates = parse_lua_values(source_paths)
    target_values, target_duplicates = parse_lua_values(target_paths)
    missing_targets = sorted(set(source_values) - set(target_values))
    if missing_targets and not allow_partial:
        raise CbpError(
            "Value catalog không an toàn: "
            f"thiếu {len(missing_targets)} bản dịch "
            f"(mẫu: {', '.join(missing_targets[:5])})"
        )

    source_to_targets: dict[str, set[str]] = {}
    for key, source in source_values.items():
        target = target_values.get(key)
        if target is None or target == source:
            continue
        source_to_targets.setdefault(source, set()).add(target)

    unique_targets = {
        source: next(iter(targets))
        for source, targets in source_to_targets.items()
        if len(targets) == 1
    }
    ambiguous_sources = sorted(
        source for source, targets in source_to_targets.items() if len(targets) > 1
    )
    translations: dict[str, dict[str, str]] = {}
    for path, node in walk_strings(root):
        target = unique_targets.get(node.text)
        if target is not None:
            translations[path] = {"source": node.text, "target": target}

    return {
        "format": 1,
        "file": file_name,
        "description": "Việt hóa từ các file Lua gốc và tiếng Việt theo cùng khóa",
        "translations": dict(sorted(translations.items())),
        "metadata": {
            "source_keys": len(source_values),
            "matched_and_changed": len(translations),
            "missing_target_keys": missing_targets,
            "ambiguous_source_values": ambiguous_sources,
            "duplicate_source_keys": source_duplicates,
            "duplicate_target_keys": target_duplicates,
        },
    }


def make_item_catalog(
    cbp_data: bytes,
    source_paths: list[Path],
    target_paths: list[Path],
    file_name: str,
    allow_partial: bool = False,
) -> dict:
    _, root, _ = decode_cbp(cbp_data)
    strings = dict(walk_strings(root))
    source_values, source_duplicates = parse_item_files(source_paths)
    target_values, target_duplicates = parse_item_files(target_paths)
    translations: dict[str, dict[str, str]] = {}
    missing_targets: list[str] = []
    unmatched_paths: list[str] = []
    source_mismatches: list[str] = []

    for path, source in sorted(source_values.items()):
        target = target_values.get(path)
        if target is None:
            missing_targets.append(path)
            continue
        node = strings.get(path)
        if node is None:
            unmatched_paths.append(path)
            continue
        if node.text != source:
            source_mismatches.append(path)
            continue
        if target != source:
            translations[path] = {"source": source, "target": target}

    if (missing_targets or source_mismatches) and not allow_partial:
        messages: list[str] = []
        if missing_targets:
            messages.append(
                f"thiếu {len(missing_targets)} bản dịch "
                f"(mẫu: {', '.join(missing_targets[:5])})"
            )
        if source_mismatches:
            messages.append(
                f"lệch {len(source_mismatches)} câu gốc CBP "
                f"(mẫu: {', '.join(source_mismatches[:5])})"
            )
        raise CbpError("Item catalog không an toàn: " + ", ".join(messages))

    return {
        "format": 1,
        "file": file_name,
        "description": "Việt hóa vật phẩm từ các phần Item gốc và tiếng Việt đã đối chiếu",
        "translations": translations,
        "metadata": {
            "source_entries": len(source_values),
            "matched_and_changed": len(translations),
            "unmatched_paths": unmatched_paths,
            "missing_target_paths": missing_targets,
            "source_mismatch_paths": source_mismatches,
            "duplicate_source_paths": source_duplicates,
            "duplicate_target_paths": target_duplicates,
        },
    }


def command_skill_catalog(args: argparse.Namespace) -> None:
    cbp_data = read_zip_entry(args.input_zip, args.file)
    catalog = make_skill_catalog(
        cbp_data,
        args.skill_text.read_text(encoding="utf-8-sig"),
        args.file,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Đã tạo {args.output}: {len(catalog['translations'])} câu thay đổi, "
        f"{len(catalog['metadata']['unmatched_paths'])} đường dẫn không khớp"
    )


def command_item_catalog(args: argparse.Namespace) -> None:
    cbp_data = read_zip_entry(args.input_zip, args.file)
    catalog = make_item_catalog(
        cbp_data,
        args.source,
        args.target,
        args.file,
        args.allow_partial,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Đã tạo {args.output}: {len(catalog['translations'])} câu thay đổi, "
        f"{len(catalog['metadata']['unmatched_paths'])} đường dẫn không khớp, "
        f"bỏ qua {len(catalog['metadata']['missing_target_paths']) + len(catalog['metadata']['source_mismatch_paths'])} "
        "mục không an toàn"
    )


def command_value_catalog(args: argparse.Namespace) -> None:
    cbp_data = read_zip_entry(args.input_zip, args.file)
    catalog = make_value_catalog(
        cbp_data,
        args.source,
        args.target,
        args.file,
        args.allow_partial,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Đã tạo {args.output}: {len(catalog['translations'])} câu thay đổi, "
        f"bỏ qua {len(catalog['metadata']['missing_target_keys'])} khóa thiếu dịch, "
        f"{len(catalog['metadata']['ambiguous_source_values'])} câu gốc mơ hồ"
    )


def command_merge_catalogs(args: argparse.Namespace) -> None:
    catalogs = [load_catalog(path) for path in args.catalog]
    file_names = {catalog.get("file") for catalog in catalogs}
    if len(file_names) != 1 or not isinstance(next(iter(file_names)), str):
        raise CbpError("Các catalog cần gộp phải cùng một file CBP")
    translations: dict[str, dict[str, str]] = {}
    conflicts: list[str] = []
    for path, catalog in zip(args.catalog, catalogs):
        for node_path, entry in catalog["translations"].items():
            existing = translations.get(node_path)
            if existing is not None and existing != entry:
                conflicts.append(
                    f"{node_path}: {existing.get('target')!r} <> {entry.get('target')!r} ({path})"
                )
                continue
            translations[node_path] = entry
    if conflicts and not args.prefer_first:
        raise CbpError(
            f"Có {len(conflicts)} xung đột catalog: " + "; ".join(conflicts[:10])
        )
    output = {
        "format": 1,
        "file": next(iter(file_names)),
        "description": "Catalog CBP đã gộp từ các lô Việt hóa an toàn",
        "translations": dict(sorted(translations.items())),
        "metadata": {
            "matched_and_changed": len(translations),
            "merged_from": [str(path) for path in args.catalog],
            "skipped_conflict_paths": (
                [conflict.split(":", 1)[0] for conflict in conflicts]
                if args.prefer_first
                else []
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Đã gộp {args.output}: {len(translations)} câu thay đổi")


def command_apply(args: argparse.Namespace) -> None:
    catalog = load_catalog(args.catalog)
    output, changed, nodes = apply_catalog(args.input.read_bytes(), catalog)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(output)
    print(f"Đã biên dịch {args.output}: đổi {changed} chuỗi trong {nodes} node")


def command_apply_zip(args: argparse.Namespace) -> None:
    catalog = load_catalog(args.catalog)
    file_name = catalog.get("file")
    if not isinstance(file_name, str) or not file_name.lower().endswith(".cbp"):
        raise CbpError("Catalog thiếu tên file CBP")
    source = read_zip_entry(args.input_zip, file_name)
    replacement, changed, nodes = apply_catalog(source, catalog)
    write_zip_with_replacement(args.input_zip, args.output_zip, file_name, replacement)
    check = read_zip_entry(args.output_zip, file_name)
    _, _, checked_nodes = decode_cbp(check)
    if checked_nodes != nodes:
        raise CbpError("Số node thay đổi sau khi ghi ZIP")
    print(
        f"Đã tạo {args.output_zip}: {file_name}, đổi {changed} chuỗi, "
        f"kiểm lại {checked_nodes} node"
    )


def command_apply_datafix_zip(args: argparse.Namespace) -> None:
    datafix = load_datafix(args.datafix)
    file_name = datafix.get("file")
    if not isinstance(file_name, str) or not file_name.lower().endswith(".cbp"):
        raise CbpError("Datafix thiếu tên file CBP")
    source = read_zip_entry(args.input_zip, file_name)
    replacement, changed, nodes = apply_datafix(source, datafix)
    write_zip_with_replacement(args.input_zip, args.output_zip, file_name, replacement)
    check = read_zip_entry(args.output_zip, file_name)
    _, _, checked_nodes = decode_cbp(check)
    if checked_nodes != nodes:
        raise CbpError("Số node thay đổi sau khi ghi ZIP datafix")
    print(
        f"Đã tạo {args.output_zip}: áp {changed} datafix vào {file_name}, "
        f"kiểm lại {checked_nodes} node"
    )


def command_validate(args: argparse.Namespace) -> None:
    _, _, nodes = decode_cbp(args.input.read_bytes())
    print(f"CBP hợp lệ: {args.input} ({nodes} node)")


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("Giá trị boolean phải là true hoặc false")


def command_patch_bool_zip(args: argparse.Namespace) -> None:
    source = read_zip_entry(args.input_zip, args.file)
    header, root, node_count = decode_cbp(source)
    nodes = dict(walk_nodes(root))
    node = nodes.get(args.path)
    if node is None:
        raise CbpError(f"Không tìm thấy node {args.path!r} trong {args.file}")
    if node.kind != 1 or len(node.raw_value) != 8:
        raise CbpError(f"Node {args.path!r} không phải boolean CBP")
    current = bool(node.raw_value[0])
    if current != args.expect:
        raise CbpError(
            f"Giá trị gốc tại {args.path} không khớp: "
            f"CBP={str(current).lower()}, mong đợi={str(args.expect).lower()}"
        )
    node.raw_value = bytes((1 if args.value else 0,)) + node.raw_value[1:]
    replacement = encode_cbp(header, root)
    _, _, checked_nodes = decode_cbp(replacement)
    if checked_nodes != node_count:
        raise CbpError("Số node thay đổi sau khi sửa boolean")
    write_zip_with_replacement(args.input_zip, args.output_zip, args.file, replacement)
    print(
        f"Đã sửa {args.file}:{args.path} "
        f"{str(current).lower()} -> {str(args.value).lower()}, "
        f"kiểm lại {checked_nodes} node"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    skill = sub.add_parser("skill-catalog", help="Tạo catalog từ Skill.txt")
    skill.add_argument("--input-zip", type=Path, required=True)
    skill.add_argument("--skill-text", type=Path, required=True)
    skill.add_argument("--file", default="skillconfig.cbp")
    skill.add_argument("--output", type=Path, required=True)
    skill.set_defaults(func=command_skill_catalog)

    item = sub.add_parser("item-catalog", help="Tạo catalog stditems từ Item gốc và tiếng Việt")
    item.add_argument("--input-zip", type=Path, required=True)
    item.add_argument(
        "--source",
        type=Path,
        action="append",
        required=True,
        help="File Item tiếng Trung; lặp lại tùy theo số phần dữ liệu",
    )
    item.add_argument(
        "--target",
        type=Path,
        action="append",
        required=True,
        help="File Item tiếng Việt tương ứng; có thể chia nhỏ hơn file nguồn",
    )
    item.add_argument("--file", default="stditems.cbp")
    item.add_argument(
        "--allow-partial",
        action="store_true",
        help="Chỉ tạo các cặp khớp CBP; ghi riêng mục thiếu/lệch để xử lý thủ công",
    )
    item.add_argument("--output", type=Path, required=True)
    item.set_defaults(func=command_item_catalog)

    value = sub.add_parser(
        "value-catalog", help="Tạo catalog CBP từ file Lua theo cùng khóa"
    )
    value.add_argument("--input-zip", type=Path, required=True)
    value.add_argument("--source", type=Path, action="append", required=True)
    value.add_argument("--target", type=Path, action="append", required=True)
    value.add_argument("--file", required=True)
    value.add_argument("--allow-partial", action="store_true")
    value.add_argument("--output", type=Path, required=True)
    value.set_defaults(func=command_value_catalog)

    merge = sub.add_parser(
        "merge-catalogs", help="Gộp catalog cùng file CBP với kiểm tra xung đột"
    )
    merge.add_argument("--catalog", type=Path, action="append", required=True)
    merge.add_argument(
        "--prefer-first",
        action="store_true",
        help="Khi có xung đột đã rà soát, giữ bản dịch ở catalog đứng trước",
    )
    merge.add_argument("--output", type=Path, required=True)
    merge.set_defaults(func=command_merge_catalogs)

    apply = sub.add_parser("apply", help="Áp catalog vào một file CBP")
    apply.add_argument("--input", type=Path, required=True)
    apply.add_argument("--catalog", type=Path, required=True)
    apply.add_argument("--output", type=Path, required=True)
    apply.set_defaults(func=command_apply)

    apply_zip = sub.add_parser("apply-zip", help="Áp catalog vào CBP bên trong ZIP")
    apply_zip.add_argument("--input-zip", type=Path, required=True)
    apply_zip.add_argument("--catalog", type=Path, required=True)
    apply_zip.add_argument("--output-zip", type=Path, required=True)
    apply_zip.set_defaults(func=command_apply_zip)

    apply_datafix_zip = sub.add_parser(
        "apply-datafix-zip",
        help="Áp bản sửa dữ liệu server-parity có kiểm tra vào CBP trong ZIP",
    )
    apply_datafix_zip.add_argument("--input-zip", type=Path, required=True)
    apply_datafix_zip.add_argument("--datafix", type=Path, required=True)
    apply_datafix_zip.add_argument("--output-zip", type=Path, required=True)
    apply_datafix_zip.set_defaults(func=command_apply_datafix_zip)

    validate = sub.add_parser("validate", help="Kiểm tra một file CBP")
    validate.add_argument("--input", type=Path, required=True)
    validate.set_defaults(func=command_validate)

    patch_bool = sub.add_parser(
        "patch-bool-zip", help="Sửa một node boolean có kiểm tra trong CBP của ZIP"
    )
    patch_bool.add_argument("--input-zip", type=Path, required=True)
    patch_bool.add_argument("--file", required=True)
    patch_bool.add_argument("--path", required=True)
    patch_bool.add_argument("--expect", type=parse_bool, required=True)
    patch_bool.add_argument("--value", type=parse_bool, required=True)
    patch_bool.add_argument("--output-zip", type=Path, required=True)
    patch_bool.set_defaults(func=command_patch_bool_zip)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
        return 0
    except (CbpError, OSError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
