#!/usr/bin/env python3
"""Vá chuỗi Hành Trang và bố cục ô Cửa Hàng bằng thay đổi AVM2 tối thiểu."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET


STRING_REPLACEMENTS = {
    "<font face='Tahoma' size='14'>": "<font face='Tahoma' size='12'>",
    "<textformat leading='5'>Giá gốc<BR><font color='#3ECB3E'>Giá hiện tại</font></textformat>":
        "<textformat leading='5'>Giá cũ<BR><font color='#3ECB3E'>Giá bán</font></textformat>",
    "<font size = '15' color = '#ffff00'>Thời gian gộp server cứ $time$ giờ làm mới 1 lần</font>":
        "<font size = '15' color = '#ffff00'>Sau khi gộp máy chủ, cửa hàng làm mới mỗi $time$ giờ.</font>",
    "Ẩn menu tiện ích mở rộng": "Ẩn menu tiện ích",
    "Mở menu tiện ích mở rộng": "Mở menu tiện ích",
    "Kho nhanh": "Cất nhanh",
    "Từ xa Cửa Hàng": "Tiệm từ xa",
    "Kho từ xa": "Kho đồ",
    "Vẻ đẹp Cửa Hàng": "Thương thành",
    "Tái chế Trang Bị": "Tái chế",
    "Dọn nhanh": "Sắp xếp",
    "Gợi ý bán để lấy Vàng": "Gợi ý vật phẩm nên bán",
    "Bán đồ dư lấy Vàng": "Bán vật phẩm dư để nhận Kim Tệ",
    "Diện tích còn trống trong kho:": "Ô trống trong kho:",
    "Hệ thống khuyến nghị nên lưu trữ Vật Phẩm sau đây trong kho":
        "Nên cất các vật phẩm sau vào kho",
    "Nên lưu trữ Vật Phẩm quan trọng trong kho": "Nên cất vật phẩm quan trọng vào kho",
    "Vật Phẩm đã được gửi vào kho thành công. Hãy đến kho để lấy nó ra nếu cần thiết.":
        "Đã cất vật phẩm vào kho. Bạn có thể đến kho để lấy khi cần.",
    "Có một người phụ nữ xinh đẹp đang đợi bạn ở Thương Thành, tại sao bạn không đi xem?":
        "Mở Thương Thành để xem và mua vật phẩm.",
    "Nếu bạn không phải là người dùng VIP, sử dụng Cửa Hàng từ xa sẽ tốn <font color='#ff0000'>$value$</font>Kim Tệ. Bạn có muốn sử dụng <BR> không?":
        "Người chơi chưa đạt VIP sẽ tốn <font color='#ff0000'>$value$</font> Kim Tệ khi dùng Cửa Hàng từ xa.<BR>Bạn có muốn tiếp tục không?",
    "Kim Tệ không đủ và việc mở không thành công. Vui lòng lưu tất cả <font color='#ff0000'>$value$</font>Kim Tệ và thử lại.":
        "Không đủ Kim Tệ. Hãy chuẩn bị <font color='#ff0000'>$value$</font> Kim Tệ rồi thử lại.",
    "Cuộc mua bán thành công và thu được Kim Tệ Khóa$value$":
        "Bán thành công, nhận $value$ Kim Tệ Khóa.",
    "Mỗi người: ": "Tối đa: ",
    " lần": " lượt",
    "Tiêu thụ 200Nguyên Bảo để mở 8 ô Hành Trang":
        "Dùng 200 Nguyên Bảo để mở 8 ô Hành Trang.",
    "Shop Ưu Đãi": "Cửa Hàng Ưu Đãi",
}


BYTE_PATCHES = (
    ("Khoảng trống giá cũ", "66c27d24124fc84301", "66c27d24104fc84301"),
    ("Dịch giá sang phải", "66c87d66d20a2416a0", "66c87d66d20a2430a0"),
    ("Khoảng trống giá bán", "66c17d24124fc84301", "66c17d24104fc84301"),
    ("Dịch nút Mua sang phải", "66bf7d258d0124314fb30a02", "66bf7d25910124314fb30a02"),
    ("Dịch nút Tặng sang phải", "66c07d258d0124194fb30a02", "66c07d25910124194fb30a02"),
)


def pcode_hex(path: Path, marker: str) -> str:
    source = path.read_text(encoding="utf-8-sig")
    marker_at = source.find(marker)
    if marker_at < 0:
        raise ValueError(f"Không tìm thấy method {marker!r} trong {path}")
    code_marker = source.find("code", marker_at)
    code_at = source.find("\n", code_marker) + 1
    code_end = source.find("end ; code", code_at)
    if code_marker < 0 or code_at <= 0 or code_end < 0:
        raise ValueError(f"Không đọc được code của {marker!r}")
    chunks = []
    for raw_line in source[code_at:code_end].splitlines():
        line = raw_line.strip()
        if line.startswith("; "):
            chunks.append(line[2:].replace(" ", ""))
    result = "".join(chunks).lower()
    if not result:
        raise ValueError(f"File không phải P-codeHex: {path}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-xml", type=Path, required=True)
    parser.add_argument("--shop-pcodehex", type=Path, required=True)
    parser.add_argument("--output-xml", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    tree = ET.parse(args.input_xml)
    root = tree.getroot()
    items = list(root.iter("item"))
    report: dict[str, object] = {"strings": [], "bytecode": []}

    for source, target in STRING_REPLACEMENTS.items():
        hits = [item for item in items if item.text == source]
        if len(hits) != 1:
            raise SystemExit(f"Chuỗi nguồn không duy nhất ({len(hits)}): {source!r}")
        hits[0].text = target
        report["strings"].append({"source": source, "target": target})

    expected = pcode_hex(args.shop_pcodehex, "public function ShopItemCell()")
    bodies = [item for item in items if item.attrib.get("type") == "MethodBody"]
    body_hits = [
        (index, body)
        for index, body in enumerate(bodies)
        if body.attrib.get("codeBytes", "").lower() == expected
    ]
    if len(body_hits) != 1:
        raise SystemExit(f"Không xác định duy nhất constructor ShopItemCell: {[i for i, _ in body_hits]}")
    body_index, body = body_hits[0]
    code = body.attrib["codeBytes"].lower()
    original_length = len(code)
    for name, source, target in BYTE_PATCHES:
        count = code.count(source)
        if count != 1:
            raise SystemExit(f"Mẫu bytecode {name!r} xuất hiện {count} lần")
        if len(source) != len(target):
            raise SystemExit(f"Bản vá {name!r} làm đổi độ dài bytecode")
        code = code.replace(source, target, 1)
        report["bytecode"].append({"name": name, "source": source, "target": target})
    if len(code) != original_length:
        raise SystemExit("Độ dài constructor ShopItemCell đã thay đổi")
    body.attrib["codeBytes"] = code
    report["method_body"] = body_index
    report["method_info"] = int(body.attrib["method_info"])
    report["code_bytes"] = original_length // 2

    args.output_xml.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output_xml, encoding="utf-8", xml_declaration=True)
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
