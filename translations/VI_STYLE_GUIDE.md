# Quy chuẩn Việt hóa AHTL

Mục tiêu của bản Việt hóa là dễ hiểu, ngắn gọn và không phá layout Flash cũ. Ưu tiên cao nhất là chữ phải vừa khung, nút bấm đọc được, panel không bị chồng chữ.

## Nguyên tắc chung

- Dịch theo phong cách game online Việt Nam, không dịch sát từng chữ Trung.
- UI hẹp dùng từ ngắn. Mô tả dài mới dùng câu đầy đủ.
- Giữ nguyên biến như `$num$`, `$time$`, `$level$`, `$value$`, `$name$`, `$type$`.
- Giữ nguyên tag định dạng nếu source có dùng: `<font>`, `<br>`, `<BR>`, `<A href=...>`.
- Không dịch khóa định tuyến scene/NPC. Các trường `comp.scene`, `comp.npc`,
  `prom.scene`, `prom.npc` và `target.*.location.entityName` phải giữ đúng câu gốc.
- Với liên kết nhiệm vụ dạng `<Tên hiển thị/Mscene:x:y:npc>`, chỉ dịch phần
  `Tên hiển thị`; toàn bộ payload sau `/M` phải giữ nguyên từng ký tự.
- Không xóa node JSON hoặc đổi `source`; chỉ sửa `target`.
- Nếu cần ẩn chữ phụ trong UI, ưu tiên `target: " "` thay vì xóa entry.
- Không dùng bản dịch máy dài kiểu “có thể nhận được phần thưởng” cho nút/tab.
- Viết hoa chữ cái đầu của mọi câu, nút, tab, nhãn và trạng thái. Ngoại lệ duy nhất là đơn vị/hậu tố ghép với số như `đ`, `giờ`, `phút`.

## Độ dài theo loại UI

| Loại text | Độ dài nên dùng | Ví dụ |
| --- | --- | --- |
| Nút bấm | 1-2 từ | `Nhận`, `Dùng`, `Mua`, `Đóng` |
| Tab nhỏ | 1-3 từ | `Kỹ năng`, `Túi`, `Thuộc tính` |
| Tiêu đề panel | 2-4 từ | `Quà Online`, `Chuyển Sinh` |
| Label chỉ số | Rất ngắn | `HP`, `MP`, `Công`, `Thủ`, `CS` |
| Mô tả dài | Tự nhiên, có thể chia dòng | Dùng `<br>` nếu source hỗ trợ |

## Thuật ngữ chuẩn

| Tiếng Trung | Dịch chuẩn | Ghi chú |
| --- | --- | --- |
| 领取 | Nhận | Dùng cho nút |
| 已领取 | Đã nhận | |
| 可领取 | Có thể nhận | Nếu chật thì dùng `Nhận` |
| 奖励 | Thưởng | Với sự kiện có thể dùng `Quà` |
| 礼包 | Gói quà | |
| 任务 | Nhiệm vụ | Nếu chật dùng `NV` |
| 当前任务 | NV hiện tại | |
| 可接任务 | NV có thể nhận | Nếu chật dùng `NV nhận` |
| 技能 | Kỹ năng | |
| 背包 | Túi | Không dùng `Ba lô` trong UI hẹp |
| 商城 | Shop | Ngắn hơn `Thương thành` |
| 元宝 | Nguyên Bảo | |
| 金币 | Vàng | |
| 绑定金币 | Xu khóa | |
| 等级 | Cấp | |
| 级 | cấp | Luôn thêm khoảng trắng khi ghép số: `70 cấp` |
| 战力 | Lực chiến | |
| 生命 | HP | Mô tả dài có thể dùng `Sinh lực` |
| 魔法 | MP | Mô tả dài có thể dùng `Pháp lực` |
| 攻击 | Công | |
| 防御 | Thủ | |
| 最大 | tối đa | Với label hẹp: `max` hoặc bỏ nếu đã rõ |
| 转生 | Chuyển Sinh | UI hẹp dùng `CS` |
| 转生灵魄 | Linh phách CS | |
| 宝石 | Gem | UI rộng có thể dùng `Bảo Thạch` |
| 宝石碎片 | Mảnh Gem | |
| 坐骑 | Thú cưỡi | |
| 翅膀 | Cánh | |
| 佣兵 | Dung binh | |
| 行会 | Bang | |
| 装备 | Trang bị | |
| 强化 | Cường hóa | |
| 合成 | Ghép | UI rộng có thể dùng `Hợp thành` |
| 升级 | Nâng cấp | UI hẹp dùng `Nâng` |
| 使用 | Dùng | |
| 购买 | Mua | |
| 关闭 | Đóng | |
| 确定 | Xác nhận | Nút hẹp dùng `OK` hoặc `Đồng ý` |
| 取消 | Hủy | |

## Quy tắc rút gọn UI chật

| Bản dài | Bản dùng trong UI |
| --- | --- |
| Nhận phần thưởng | Nhận |
| Đã nhận được | Đã nhận |
| Có thể nhận được | Có thể nhận |
| Cấp độ nhân vật | Cấp |
| Chuyển Sinh | CS |
| Bảo Thạch | Gem |
| Sinh Lực Tối Đa | HP tối đa |
| Pháp Lực Tối Đa | MP tối đa |
| Công Kích Tối Đa | Công tối đa |
| Phòng Ngự Tối Đa | Thủ tối đa |
| Kim Tệ Khóa | Xu khóa |
| Tinh thần Chuyển Sinh | Linh phách CS |

## Ví dụ sửa câu bị tràn

```text
Nhân vật 70cấp độ có thể Chuyển Sinh
=> Cấp 70 mở CS

Cấp độ nhân vật hiện tại là 11. Nếu bạn nâng cấp lên 59, bạn có thể thay đổi Chuyển Sinh thành 1.
=> Cấp 11, cần +59 cấp để CS 1

Yêu cầu chuyển kỳ tự 1
=> Yêu cầu CS 1

Hiệu ứng thưởng 1 Chuyển Sinh
=> Thưởng CS 1

nhận được
=> Nhận
```

### Quy ước riêng cho Chuyển Sinh

- `Chuyển Sinh` có thể viết tắt thành `CS` trong nhãn hẹp, nhưng giữ nguyên trong tiêu đề chính.
- Dùng `Linh phách` thay cho các bản dịch máy `linh hồn Chuyển Sinh` hoặc `tinh thần Chuyển Sinh`.
- Bốn nhãn cố định là `Cấp thế giới`, `Giới hạn CS`, `Linh phách CS`, `Số lần CS`.
- Hộp yêu cầu phải tách ba dòng: `Xu khóa`, `Cấp`, `Linh phách`.
- Thông báo thiếu cấp dùng mẫu `Cấp X · Cần thêm Y cấp để CS Z`.

### Quy ước riêng cho Phúc Lợi Chiến Thần

- Tab cố định dùng: `Quà Online`, `Đăng Nhập`, `Quà Cấp`, `Quà Nạp`, `Mã Quà`, `Chia Sẻ`, `Cập Nhật`.
- Gói theo Chuyển Sinh dùng mẫu `Quà CS X`; gói theo cấp dùng `Quà Cấp X`.
- Nút nhận quà chỉ dùng `Nhận`; nút nạp dùng `Nạp Ngay`; nhập mã dùng `Nhập mã để nhận`.
- Trạng thái phải viết hoa đầu câu và ưu tiên mẫu ngắn: `Đã nhận`, `Chưa mở`, `Còn X lượt`.
- Không hiển thị số ngày tính từ mốc sự kiện hoặc mốc mở server cũ; dùng `Máy chủ đang hoạt động`.
- Nội dung mô tả phải giữ số, điều kiện và biến động như `$value$`, `$num$`, `$libao$`, nhưng bỏ câu quảng cáo hoặc lời chúc không cung cấp thông tin.

## Quy tắc cho CBP

- Chỉ sửa `target` trong các file `*.vi.json`.
- Không sửa trực tiếp file `.cbp` hoặc `cbp.zip` bằng text editor.
- Sau khi sửa phải build lại CBP, đóng lại `cbp.zip`, validate ZIP, cập nhật manifest/hash/version rồi mới deploy.
- Nếu một chuỗi nằm trong ảnh hoặc hardcoded trong `GameFrame.swf`, sửa CBP sẽ không có tác dụng.
- Catalog `stdquest.cbp` phải vượt qua guard khóa định tuyến trước khi build.
  Không được đồng bộ bản dịch tên bản đồ/NPC vào các trường máy chỉ vì câu nguồn
  giống với tên đang hiển thị ở chỗ khác.

Ví dụ hợp lệ:

```text
<龙行者/M群魔堡垒:68:82:龙行者>
=> <Long Hành Giả/M群魔堡垒:68:82:龙行者>
```

Ví dụ sai vì làm hỏng tự tìm đường/trả nhiệm vụ:

```text
<Long Hành Giả/M Quần Ma Bảo Lũy:68:82:Long Hành Giả>
```

## Quy tắc cho GameFrame SWF

- Bản dịch máy nằm ở `gameframe-zhcn-machine.vi.json` chỉ dùng làm nền.
- Các sửa thủ công nên đặt ở `gameframe-zhcn-final.vi.json` để override.
- Với nút/tab/title trong SWF, ưu tiên bản ngắn hơn bản đầy đủ.
- Nếu rút gọn vẫn tràn, phải sửa layout ActionScript hoặc thay asset ảnh.
- Các chuỗi được `SplitString` theo dấu phẩy là dữ liệu có cấu trúc: phải giữ nguyên số phần tử, vị trí phần tử rỗng và thứ tự so với bản gốc.
- Tên ô trang bị 40 px dùng bộ nhãn rút gọn riêng trong layout; không rút tên `Prop_EquipPosNames` toàn cục.
