#!/usr/bin/env python3
"""Lập báo cáo các khóa ngôn ngữ có nguy cơ tràn nút/tab/label GameFrame."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from swf_lang_localizer import load_client_lang
from translate_gameframe_catalog import AS_STRING_RE, decode_as_string


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


HAN_RE = re.compile(r"[\u3400-\u9fff]")
TAG_RE = re.compile(r"<[^<>]*>")
TOKEN_RE = re.compile(r"\$[A-Za-z0-9_]+\$?|%[A-Za-z0-9_]+%|@@[^\s<>]+")
REF_RE = re.compile(
    r"LangManager\.Lang\.([A-Za-z_][A-Za-z0-9_]*)(?:\[(\d+)\])?"
)


def visible_text(value: str) -> str:
    value = TAG_RE.sub("", value)
    value = TOKEN_RE.sub("", value)
    value = value.replace("\\n", " ").replace("\\", " ")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def estimated_width(value: str) -> float:
    width = 0.0
    for char in visible_text(value):
        if HAN_RE.match(char):
            width += 1.0
        elif char.isspace():
            width += 0.28
        elif char.isupper():
            width += 0.62
        elif char.isalpha():
            width += 0.52
        elif char.isdigit():
            width += 0.55
        else:
            width += 0.4
    return round(width, 2)


def language_pairs(client_path: Path, reference_path: Path, machine_path: Path) -> tuple[dict, dict]:
    translated = load_client_lang(client_path)
    reference = load_client_lang(reference_path)
    pairs: dict[str, dict[str, str]] = {}

    for key, target in translated.scalars.items():
        if key in reference.scalars:
            pairs[key] = {
                "source": reference.scalars[key][1:-1],
                "target": target[1:-1],
                "layer": "ClientLang",
            }
    for key, values in translated.arrays.items():
        for index, target in enumerate(values):
            if key in reference.arrays and index < len(reference.arrays[key]):
                pairs[f"{key}[{index}]"] = {
                    "source": reference.arrays[key][index][1:-1],
                    "target": target[1:-1],
                    "layer": "ClientLang",
                }

    machine = json.loads(machine_path.read_text(encoding="utf-8"))
    for key, entry in machine.get("translations", {}).items():
        if key in pairs or not isinstance(entry, dict) or not isinstance(entry.get("target"), str):
            continue
        expression = entry.get("source_expression", "")
        if not isinstance(expression, str) or not AS_STRING_RE.fullmatch(expression):
            continue
        pairs[key] = {
            "source": decode_as_string(expression),
            "target": entry["target"],
            "layer": "ZH_CN-extra",
        }

    translated_keys = set(translated.scalars) | set(translated.arrays)
    reference_keys = set(reference.scalars) | set(reference.arrays)
    shape = {
        "missing_reference_keys": sorted(reference_keys - translated_keys),
        "extra_translated_keys": sorted(translated_keys - reference_keys),
    }
    return pairs, shape


def source_references(source_root: Path) -> dict[str, list[dict]]:
    references: dict[str, list[dict]] = {}
    for path in source_root.rglob("*.as"):
        relative = path.relative_to(source_root).as_posix()
        for line_number, line in enumerate(
            path.read_text(encoding="utf-8-sig", errors="replace").splitlines(),
            start=1,
        ):
            context = "other"
            if re.search(r"\.caption\s*=", line):
                context = "caption"
            elif re.search(r"\.text\s*=", line):
                context = "text"
            elif re.search(r"\btitle\s*=", line):
                context = "title"
            for match in REF_RE.finditer(line):
                index = match.group(2)
                key = (
                    f"{match.group(1)}[{int(index)}]"
                    if index is not None
                    else match.group(1)
                )
                references.setdefault(key, []).append(
                    {"file": relative, "line": line_number, "context": context}
                )
    return references


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-lang", type=Path, required=True)
    parser.add_argument("--reference-client-lang", type=Path, required=True)
    parser.add_argument("--machine-catalog", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    pairs, shape = language_pairs(
        args.client_lang, args.reference_client_lang, args.machine_catalog
    )
    references = source_references(args.source_root)
    candidates: list[dict] = []
    for key, pair in pairs.items():
        refs = references.get(key, [])
        contexts = sorted({entry["context"] for entry in refs})
        if not set(contexts).intersection({"caption", "text", "title"}):
            continue
        source_width = estimated_width(pair["source"])
        target_width = estimated_width(pair["target"])
        target_visible = visible_text(pair["target"])
        if source_width > 10 or target_width < 7.5:
            continue
        if target_width <= source_width * 1.25 and len(target_visible) < 14:
            continue
        candidates.append(
            {
                "key": key,
                "layer": pair["layer"],
                "source": visible_text(pair["source"]),
                "target": target_visible,
                "source_width": source_width,
                "target_width": target_width,
                "expansion_ratio": round(
                    target_width / source_width if source_width else 99.0, 2
                ),
                "contexts": contexts,
                "references": refs,
            }
        )
    candidates.sort(
        key=lambda item: (item["expansion_ratio"], item["target_width"]),
        reverse=True,
    )
    summary = {
        "language_pairs": len(pairs),
        "referenced_keys": len(references),
        "reference_count": sum(len(value) for value in references.values()),
        "risk_candidates": len(candidates),
        "caption_candidates": sum("caption" in item["contexts"] for item in candidates),
        "title_candidates": sum("title" in item["contexts"] for item in candidates),
        "text_candidates": sum("text" in item["contexts"] for item in candidates),
    }
    payload = {"format": 1, "summary": summary, "shape": shape, "candidates": candidates}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
