#!/usr/bin/env python3
"""Kiểm tra catalog và chứng minh phần Hán tự còn lại chỉ là mã kỹ thuật."""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

from finish_gameframe_catalog import AS_LITERAL_RE
from translate_gameframe_catalog import HAN_RE, TranslationError, decode_as_string


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


STANDARD_TAG_RE = re.compile(
    r"</?(?:font|a|iobj|br|textformat|b|u|p|span)(?:\s[^<>]*)?/?>",
    re.IGNORECASE,
)
ANY_TAG_RE = re.compile(r"<([^<>]*)>")
PLACEHOLDER_RE = re.compile(
    r"\$[A-Za-z0-9_]+\$?|%[A-Za-z0-9_]+%|@@[A-Za-z0-9_,.+-]+"
)
URL_RE = re.compile(r"https?://[^\s<>\"']+")
ROUTE_ONLY_RE = re.compile(r"^[Mmfjx][^\s<>]*(?:[:;,].*)?$", re.IGNORECASE)


def literals(expression: str) -> list[str]:
    return [decode_as_string(match.group(0)) for match in AS_LITERAL_RE.finditer(expression)]


def skeleton(expression: str) -> str:
    return AS_LITERAL_RE.sub('""', expression)


def standard_tags(text: str) -> list[str]:
    return STANDARD_TAG_RE.findall(text)


def custom_routes(text: str) -> list[str]:
    routes: list[str] = []
    for match in ANY_TAG_RE.finditer(text):
        token = match.group(0)
        if STANDARD_TAG_RE.fullmatch(token):
            continue
        content = match.group(1)
        if content.lower().startswith("(c0x"):
            continue
        if "/" in content:
            routes.append(content.split("/", 1)[1])
        elif content.startswith("(x") and content.endswith(")"):
            routes.append(content)
    return routes


def signature(texts: list[str]) -> dict[str, collections.Counter[str]]:
    combined = "\n".join(texts)
    return {
        "html": collections.Counter(standard_tags(combined)),
        "placeholder": collections.Counter(PLACEHOLDER_RE.findall(combined)),
        "url": collections.Counter(URL_RE.findall(combined)),
        "route": collections.Counter(custom_routes(combined)),
    }


def visible_text(text: str) -> str:
    def tag_value(match: re.Match[str]) -> str:
        token = match.group(0)
        if STANDARD_TAG_RE.fullmatch(token):
            return ""
        content = match.group(1)
        if content.startswith("(") and ")" in content:
            close = content.find(")")
            prefix = content[: close + 1]
            if prefix.lower().startswith("(c0x"):
                return content[close + 1 :]
            if prefix.lower().startswith("(x"):
                return ""
            if content[close + 1 :].startswith("/"):
                return content[1:close]
        if "/" in content:
            return content.split("/", 1)[0]
        return content

    result = ANY_TAG_RE.sub(tag_value, text)
    result = PLACEHOLDER_RE.sub("", result)
    result = URL_RE.sub("", result)
    if ROUTE_ONLY_RE.fullmatch(result.strip()):
        return ""
    return result


def audit_catalog(path: Path) -> tuple[int, list[str]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if document.get("format") != 1 or not isinstance(document.get("translations"), dict):
        raise TranslationError(f"Catalog sai format 1: {path}")
    errors: list[str] = []
    for uid, entry in document["translations"].items():
        source_expression = entry.get("source_expression")
        if not isinstance(source_expression, str):
            errors.append(f"{uid}: thiếu source_expression")
            continue
        source_texts = literals(source_expression)
        target_expression = entry.get("target_expression")
        if isinstance(target_expression, str):
            target_texts = literals(target_expression)
            if skeleton(source_expression) != skeleton(target_expression):
                errors.append(f"{uid}: đổi cấu trúc biểu thức ActionScript")
            if len(source_texts) != len(target_texts):
                errors.append(f"{uid}: đổi số chuỗi con ActionScript")
        else:
            target = entry.get("target")
            if not isinstance(target, str):
                errors.append(f"{uid}: thiếu target/target_expression")
                continue
            if len(source_texts) != 1:
                errors.append(f"{uid}: target thường nhưng nguồn không phải một chuỗi")
            target_texts = [target]
        source_signature = signature(source_texts)
        target_signature = signature(target_texts)
        for kind in source_signature:
            if source_signature[kind] != target_signature[kind]:
                errors.append(f"{uid}: đổi token kỹ thuật loại {kind}")
    return len(document["translations"]), errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, action="append", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--technical-output", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    catalog_entries = 0
    for catalog in args.catalog:
        count, catalog_errors = audit_catalog(catalog)
        catalog_entries += count
        errors.extend(f"{catalog.name}: {error}" for error in catalog_errors)

    report = json.loads(args.report.read_text(encoding="utf-8"))
    technical: list[dict] = []
    for entry in report["residual_han_assignments"]:
        texts = literals(entry["value"])
        visible = "".join(visible_text(text) for text in texts)
        if HAN_RE.search(visible):
            errors.append(
                f"ZH_CN.as:{entry['line']} {entry['name']} còn Hán tự hiển thị: {visible}"
            )
        else:
            technical.append(entry)

    args.technical_output.write_text(
        json.dumps(
            {
                "format": 1,
                "description": "Hán tự chỉ còn trong font, route hoặc định danh kỹ thuật; không được dịch.",
                "entries": technical,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"Catalog: {catalog_entries} mục; residual kỹ thuật: {len(technical)}; "
        f"lỗi: {len(errors)}"
    )
    for error in errors[:100]:
        print(f"- {error}")
    if errors:
        raise TranslationError(f"Kiểm toán thất bại với {len(errors)} lỗi")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, TranslationError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        raise SystemExit(1)
