#!/usr/bin/env python3
"""Dịch hàng loạt các chuỗi đơn còn lại trong báo cáo lang.ZH_CN.

Các placeholder, URL, thẻ HTML và liên kết kỹ thuật được thay bằng token trước
khi gửi. Catalog đầu ra vẫn lưu nguyên ``source_expression`` để bước biên dịch
kiểm đúng câu gốc. Chuỗi ghép ActionScript không được tự động xử lý.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


HAN_RE = re.compile(r"[\u3400-\u9fff]")
AS_STRING_RE = re.compile(r'^"(?:\\.|[^"\\])*"$')
STRUCTURAL_RE = re.compile(
    r"https?://[^\s<>\"']+"
    r"|<[^>]+>"
    r"|\$[A-Za-z0-9_]+\$"
    r"|@@[A-Za-z0-9_,.+-]+"
    r"|\\[\\nrt]"
    r"|%[-+0-9.]*[a-zA-Z]"
)


GLOSSARY = {
    "Thập Nhị Tinh Cung": ("十二星宫",),
    "Điểm Tinh Hồn": ("星魂值",),
    "Kim Tệ Khóa": ("绑定金币",),
    "Nguyên Bảo Khóa": ("绑定元宝",),
    "Nhiệm Vụ Chính Tuyến": ("主线任务",),
    "Thời Gian Chờ": ("冷却时间",),
    "Sách Kỹ Năng": ("技能书",),
    "Vật Công": ("物理攻击",),
    "Pháp Công": ("魔法攻击",),
    "Đạo Công": ("道术攻击",),
    "Vật Phòng": ("物理防御",),
    "Pháp Phòng": ("魔法防御",),
    "Sinh Lực": ("生命值",),
    "Pháp Lực": ("魔法值",),
    "Nguyên Bảo": ("元宝",),
    "Kim Tệ": ("金币",),
    "Lễ Kim": ("礼金",),
    "Bang Hội": ("行会", "公会"),
    "Dung Binh": ("佣兵",),
    "Tọa Kỵ": ("坐骑",),
    "Kỹ Năng": ("技能",),
    "Trang Bị": ("装备",),
    "Kinh Nghiệm": ("经验",),
    "người chơi": ("玩家",),
    "Anh Hùng": ("英雄",),
    "Chuyển Sinh": ("转生",),
    "Đồ Long": ("屠龙",),
    "Vương Thành": ("王城",),
    "Tinh Hồn": ("星魂",),
    "Phù Văn": ("符文",),
    "Bảo Thạch": ("宝石",),
    "Nạp Thẻ": ("充值",),
    "Gói Quà": ("礼包",),
    "Phó Bản": ("副本",),
    "Nộ Khí": ("怒气",),
    "Chiến Lực": ("战斗力",),
    "Tấn Công": ("攻击",),
    "Phòng Ngự": ("防御",),
    "Cường Hóa": ("强化",),
    "Hợp Thành": ("合成",),
    "Thương Thành": ("商城",),
    "Hành Trang": ("背包",),
    "Vật Phẩm": ("道具",),
    "Phần Thưởng": ("奖励",),
    "Nhiệm Vụ": ("任务",),
    "Chiến Sĩ": ("战士",),
    "Pháp Sư": ("法师",),
    "Đạo Sĩ": ("道士",),
    "Quái Vật": ("怪物",),
    "Bạo Kích": ("暴击",),
    "Chính Xác": ("命中",),
    "Né Tránh": ("闪避",),
    "Hồi Sinh": ("复活",),
    "Cửa Hàng": ("商店",),
    "Điểm Năng Động": ("活跃度",),
}


class TranslationError(ValueError):
    pass


def decode_as_string(expression: str) -> str:
    if not AS_STRING_RE.fullmatch(expression):
        raise TranslationError("Không phải chuỗi ActionScript đơn")
    source = expression[1:-1]
    output: list[str] = []
    index = 0
    escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\", '"': '"', "'": "'"}
    while index < len(source):
        char = source[index]
        if char != "\\":
            output.append(char)
            index += 1
            continue
        index += 1
        if index >= len(source):
            output.append("\\")
            break
        code = source[index]
        index += 1
        if code in escapes:
            output.append(escapes[code])
        elif code == "u" and index + 4 <= len(source):
            output.append(chr(int(source[index : index + 4], 16)))
            index += 4
        elif code == "x" and index + 2 <= len(source):
            output.append(chr(int(source[index : index + 2], 16)))
            index += 2
        else:
            output.extend(("\\", code))
    return "".join(output)


def make_key(entry: dict) -> str:
    index = entry.get("index")
    return f"{entry['name']}[{index}]" if index is not None else entry["name"]


def protect_text(text: str, serial_start: int) -> tuple[str, dict[str, str], int]:
    replacements: dict[str, str] = {}
    serial = serial_start

    def token(value: str) -> str:
        nonlocal serial
        marker = f"ZXQ{serial:08d}QXZ"
        serial += 1
        replacements[marker] = value
        return marker

    protected = STRUCTURAL_RE.sub(lambda match: token(match.group(0)), text)
    glossary_items = sorted(
        ((source, target) for target, sources in GLOSSARY.items() for source in sources),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for source, target in glossary_items:
        if source in protected:
            protected = re.sub(
                re.escape(source), lambda _match: token(target), protected
            )
    return protected, replacements, serial


def restore_text(text: str, replacements: dict[str, str]) -> str:
    restored = re.sub(
        r"ZXQ\s*(\d{8})\s*QXZ",
        lambda match: f"ZXQ{match.group(1)}QXZ",
        text,
        flags=re.IGNORECASE,
    )
    for marker, value in replacements.items():
        count = restored.count(marker)
        if count != 1:
            raise TranslationError(f"Token {marker} xuất hiện {count} lần sau khi dịch")
        restored = restored.replace(marker, value)
    restored = re.sub(r"[ \t]+([,.;:!?])", r"\1", restored)
    return restored


def google_translate(text: str, timeout: int, retries: int) -> str:
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "zh-CN", "tl": "vi", "dt": "t", "q": text}
    )
    request = urllib.request.Request(
        "https://translate.googleapis.com/translate_a/single?" + query,
        headers={"User-Agent": "Mozilla/5.0 AHTL-localizer/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            return "".join(segment[0] or "" for segment in payload[0])
        except Exception as exc:  # pragma: no cover - phụ thuộc mạng
            last_error = exc
            time.sleep(min(8.0, 0.75 * (2**attempt)))
    raise TranslationError(f"Dịch mạng thất bại: {last_error}")


def write_catalog(path: Path, translations: dict[str, dict]) -> None:
    document = {
        "format": 1,
        "description": (
            "Bản dịch máy có bảo vệ placeholder/HTML; cần kiểm duyệt dần theo nhóm UI."
        ),
        "provider": "Google Translate public endpoint, zh-CN to vi",
        "translations": translations,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-chars", type=int, default=2400)
    parser.add_argument("--batch-items", type=int, default=18)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--pause", type=float, default=0.2)
    parser.add_argument("--failed-output", type=Path)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    existing: dict[str, dict] = {}
    if args.output.exists():
        current = json.loads(args.output.read_text(encoding="utf-8"))
        if current.get("format") != 1:
            raise TranslationError("Catalog đầu ra hiện có sai format")
        existing = current.get("translations", {})

    candidates: list[dict] = []
    skipped_complex = 0
    skipped_technical = 0
    token_serial = 1
    for entry in report["residual_han_assignments"]:
        key = make_key(entry)
        if key in existing:
            continue
        expression = entry["value"]
        if not AS_STRING_RE.fullmatch(expression):
            skipped_complex += 1
            continue
        original = decode_as_string(expression)
        protected, replacements, token_serial = protect_text(original, token_serial)
        if not HAN_RE.search(protected):
            skipped_technical += 1
            continue
        candidates.append(
            {
                "key": key,
                "source_expression": expression,
                "original": original,
                "protected": protected,
                "replacements": replacements,
                "line": entry["line"],
            }
        )
    if args.limit is not None:
        candidates = candidates[: args.limit]

    print(
        f"Cần dịch {len(candidates)} chuỗi; bỏ qua {skipped_complex} biểu thức ghép, "
        f"{skipped_technical} chuỗi chỉ còn định danh kỹ thuật"
    )

    position = 0
    batch_number = 0
    failed: list[dict] = []
    while position < len(candidates):
        batch: list[dict] = []
        char_count = 0
        while position < len(candidates) and len(batch) < args.batch_items:
            candidate = candidates[position]
            size = len(candidate["protected"])
            if batch and char_count + size > args.batch_chars:
                break
            batch.append(candidate)
            char_count += size
            position += 1

        batch_number += 1
        delimiter = f"ZXQSPLIT{batch_number:06d}QXZ"
        request_text = ("\n" + delimiter + "\n").join(
            candidate["protected"] for candidate in batch
        )
        translated_text = google_translate(request_text, args.timeout, args.retries)
        parts = translated_text.split(delimiter)
        if len(parts) != len(batch):
            print(
                f"Batch {batch_number} mất delimiter; chuyển {len(batch)} câu sang chế độ riêng"
            )
            parts = [
                google_translate(candidate["protected"], args.timeout, args.retries)
                for candidate in batch
            ]
        for candidate, translated in zip(batch, parts):
            try:
                target = restore_text(translated.strip(), candidate["replacements"])
            except TranslationError as batch_error:
                try:
                    single = google_translate(
                        candidate["protected"], args.timeout, args.retries
                    )
                    target = restore_text(single.strip(), candidate["replacements"])
                    print(f"Fallback riêng: {candidate['key']}")
                except TranslationError as single_error:
                    failed.append(
                        {
                            "key": candidate["key"],
                            "line": candidate["line"],
                            "reason": str(single_error),
                            "batch_reason": str(batch_error),
                            "source_expression": candidate["source_expression"],
                        }
                    )
                    print(f"Bỏ qua để dịch tay: {candidate['key']}")
                    continue
            if not target:
                raise TranslationError(f"Bản dịch rỗng tại {candidate['key']}")
            existing[candidate["key"]] = {
                "source_expression": candidate["source_expression"],
                "target": target,
                "review": "machine",
                "source_line": candidate["line"],
                "source_sha256": hashlib.sha256(
                    candidate["original"].encode("utf-8")
                ).hexdigest(),
            }
        write_catalog(args.output, existing)
        if args.failed_output:
            args.failed_output.parent.mkdir(parents=True, exist_ok=True)
            args.failed_output.write_text(
                json.dumps(failed, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        print(
            f"Batch {batch_number}: {position}/{len(candidates)}; "
            f"catalog={len(existing)}"
        )
        time.sleep(args.pause)

    print(f"Đã tạo {args.output}: {len(existing)} mục; cần dịch tay {len(failed)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, TranslationError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        raise SystemExit(1)
