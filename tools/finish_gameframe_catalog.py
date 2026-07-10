#!/usr/bin/env python3
"""Hoàn thiện catalog ZH_CN mà không làm đổi mã HTML, route và placeholder.

Khác trình dịch lô ban đầu, công cụ này dịch từng đoạn chữ hiển thị nằm giữa
thẻ/placeholder. Nó cũng hỗ trợ biểu thức ActionScript ghép chuỗi và mảng bằng
``target_expression`` để giữ nguyên cấu trúc mã nguồn.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from translate_gameframe_catalog import (
    AS_STRING_RE,
    GLOSSARY,
    HAN_RE,
    TranslationError,
    decode_as_string,
    google_translate,
)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


AS_LITERAL_RE = re.compile(r'"(?:\\.|[^"\\])*"')
STRUCTURE_RE = re.compile(
    r"<[^<>]*>"
    r"|\$[A-Za-z0-9_]+\$?"
    r"|%[A-Za-z0-9_]+%"
    r"|@@[A-Za-z0-9_,.+-]+"
    r"|\\[\\nrt]"
    r"|https?://[^\s<>\"']+",
    re.IGNORECASE,
)
STANDARD_TAG_RE = re.compile(
    r"^</?(?:font|a|iobj|br|textformat|b|u|p|span)(?:\s|>|/)",
    re.IGNORECASE,
)
ROUTE_ONLY_RE = re.compile(r"^[Mmfjx][^\s<>]*(?:[:;,].*)?$", re.IGNORECASE)


def key_for(entry: dict) -> str:
    index = entry.get("index")
    return f"{entry['name']}[{index}]" if index is not None else entry["name"]


def join_parts(parts: list[str]) -> str:
    result = ""
    for part in parts:
        if not part:
            continue
        if result and result[-1].isalnum() and part[0].isalnum():
            result += " "
        result += part
    return result


class SegmentTranslator:
    def __init__(self, timeout: int, retries: int, pause: float) -> None:
        self.timeout = timeout
        self.retries = retries
        self.pause = pause
        self.cache: dict[str, str] = {}
        glossary_pairs = [
            (source, target)
            for target, sources in GLOSSARY.items()
            for source in sources
        ]
        glossary_pairs.sort(key=lambda item: len(item[0]), reverse=True)
        self.glossary = dict(glossary_pairs)
        self.glossary_re = re.compile(
            "|".join(re.escape(source) for source, _target in glossary_pairs)
        )

    def network(self, source: str) -> str:
        if not HAN_RE.search(source):
            return source
        if source in self.cache:
            return self.cache[source]
        target = google_translate(source, self.timeout, self.retries).strip()
        if not target:
            raise TranslationError(f"Bản dịch rỗng cho {source!r}")
        self.cache[source] = target
        time.sleep(self.pause)
        return target

    def prose(self, source: str) -> str:
        if not HAN_RE.search(source):
            return source
        if ROUTE_ONLY_RE.fullmatch(source.strip()):
            return source
        parts: list[str] = []
        position = 0
        for match in self.glossary_re.finditer(source):
            parts.append(self.network(source[position : match.start()]))
            parts.append(self.glossary[match.group(0)])
            position = match.end()
        parts.append(self.network(source[position:]))
        return join_parts(parts)

    def custom_tag(self, token: str) -> str:
        content = token[1:-1]
        if STANDARD_TAG_RE.match(token + ">"):
            return token
        if content.startswith("(") and ")" in content:
            close = content.find(")")
            prefix = content[: close + 1]
            if prefix.lower().startswith("(c0x") or prefix.lower().startswith("(x"):
                return "<" + prefix + self.prose(content[close + 1 :]) + ">"
            if content[close + 1 :].startswith("/"):
                label = self.prose(content[1:close])
                return "<(" + label + ")" + content[close + 1 :] + ">"
        if "/" in content:
            label, route = content.split("/", 1)
            return "<" + self.prose(label) + "/" + route + ">"
        return "<" + self.prose(content) + ">"

    def text(self, source: str) -> str:
        parts: list[str] = []
        position = 0
        for match in STRUCTURE_RE.finditer(source):
            parts.append(self.prose(source[position : match.start()]))
            token = match.group(0)
            parts.append(self.custom_tag(token) if token.startswith("<") else token)
            position = match.end()
        parts.append(self.prose(source[position:]))
        return "".join(parts)


def translate_expression(expression: str, translator: SegmentTranslator) -> str:
    output: list[str] = []
    position = 0
    found = False
    for match in AS_LITERAL_RE.finditer(expression):
        found = True
        output.append(expression[position : match.start()])
        literal = match.group(0)
        source = decode_as_string(literal)
        target = translator.text(source)
        output.append(json.dumps(target, ensure_ascii=False))
        position = match.end()
    if not found:
        raise TranslationError(f"Biểu thức không có chuỗi ActionScript: {expression}")
    output.append(expression[position:])
    return "".join(output)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allowlist-output", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=25)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--pause", type=float, default=0.05)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    translations: dict[str, dict] = {}
    if args.output.exists():
        current = json.loads(args.output.read_text(encoding="utf-8"))
        if current.get("format") != 1:
            raise TranslationError("Catalog hoàn thiện không đúng format 1")
        translations = current.get("translations", {})

    translator = SegmentTranslator(args.timeout, args.retries, args.pause)
    allowlist: list[dict] = []
    residual = report["residual_han_assignments"]
    for number, entry in enumerate(residual, start=1):
        source_key = key_for(entry)
        uid = f"{source_key}@{entry['line']}"
        if uid in translations:
            continue
        source_expression = entry["value"]
        target_expression = translate_expression(source_expression, translator)
        if target_expression == source_expression:
            allowlist.append(
                {
                    "source_key": source_key,
                    "source_line": entry["line"],
                    "source_expression": source_expression,
                    "reason": "Chỉ còn Hán tự trong font, route hoặc định danh kỹ thuật",
                }
            )
        else:
            translations[uid] = {
                "source_key": source_key,
                "source_line": entry["line"],
                "source_expression": source_expression,
                "target_expression": target_expression,
                "review": "segmented-machine",
            }
            write_json(
                args.output,
                {
                    "format": 1,
                    "description": "Bản dịch phần dư theo đoạn, bảo toàn mã ActionScript/HTML/route/placeholder.",
                    "translations": translations,
                },
            )
        if number % 20 == 0:
            print(
                f"Đã xử lý {number}/{len(residual)}; "
                f"dịch={len(translations)}, kỹ thuật={len(allowlist)}"
            )

    write_json(
        args.output,
        {
            "format": 1,
            "description": "Bản dịch phần dư theo đoạn, bảo toàn mã ActionScript/HTML/route/placeholder.",
            "translations": translations,
        },
    )
    write_json(
        args.allowlist_output,
        {
            "format": 1,
            "description": "Các Hán tự kỹ thuật phải giữ nguyên để route/font còn hoạt động.",
            "entries": allowlist,
        },
    )
    print(
        f"Hoàn tất: dịch {len(translations)} mục, "
        f"giữ kỹ thuật {len(allowlist)} mục"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, TranslationError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        raise SystemExit(1)
