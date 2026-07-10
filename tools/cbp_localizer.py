#!/usr/bin/env python3
"""Biên dịch bản dịch vào CBP mà không làm hỏng dữ liệu nhị phân.

Các lệnh chính:
  skill-catalog  Tạo catalog JSON từ Skill.txt và skillconfig.cbp sạch.
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


def apply_catalog(data: bytes, catalog: dict) -> tuple[bytes, int, int]:
    header, root, node_count = decode_cbp(data)
    strings = dict(walk_strings(root))
    changed = 0
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
        if target != node.text:
            node.text = target
            changed += 1
    output = encode_cbp(header, root)
    decode_cbp(output)
    return output, changed, node_count


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
