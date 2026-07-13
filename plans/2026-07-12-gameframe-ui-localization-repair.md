# Kế hoạch sửa UI Việt hóa GameFrame

## Mục tiêu

Sửa toàn bộ lỗi Việt hóa đã audit ở UI người chơi mà không làm thay đổi logic game, khóa route/NPC, cấu trúc CBP hoặc phần admin đang có thay đổi dở dang. Kết quả cần có chữ vừa khung, đúng nghĩa và giữ nguyên biến động/markup kỹ thuật.

Phạm vi gồm:

- Chuỗi thông tin, ô nhập liệu và trạng thái chung đã bị dịch máy dài hoặc sai nghĩa.
- Toàn bộ cụm event: `active`, `combineActive`, `MonsterTreasure`, `onlineRewards`, `superGift` và các chuỗi `welfare` dùng lại trong màn event.
- Phúc Lợi Chiến Thần, chỉ xử lý các key còn ngoài lô `welfare[1..105]` đã có override.
- Màn **Thưởng Online theo thời lượng** (`onlineTimeAward`), gồm ClientLang và chữ hardcode trong `OnlineAwardCell.as`.
- Các CBP Phúc Lợi đã nằm trong bản build hiện tại: `welFare.cbp`, `uiawarditems.cbp`, `stditems.cbp`.

Không thuộc phạm vi:

- Thay đổi mechanic, mốc thưởng, giá nạp, dữ liệu runtime hay route scene/NPC.
- Việt hóa hoặc deploy phần quản trị trong `assets/admin/`.
- Dịch toàn bộ các chuỗi còn Hán tự chưa được audit trực quan.

## Quy ước Việt hóa đã chốt

Việt hóa không phải là thay chữ trực tiếp trong file game. Mọi sửa đổi phải đi qua catalog, được biên dịch lại đúng định dạng và chỉ thay layout ActionScript ở control thực sự bị tràn.

### Lớp 1 — CBP

Áp dụng cho vật phẩm, nhiệm vụ, kỹ năng, Phúc Lợi và cấu hình game.

1. Đọc/áp catalog bằng `tools/cbp_localizer.py`.
2. Xuất chuỗi cần dịch thành `*.vi.json`.
3. Chỉ sửa `target`; giữ nguyên key, node, số liệu và thứ tự dữ liệu.
4. Biên dịch lại CBP đúng cấu trúc nhị phân, đóng lại `cbp.zip`.
5. Validate header, zlib, UTF-8, cây dữ liệu và CRC ZIP trước khi dùng output.

Tuyệt đối không mở `.cbp` bằng text editor để thay trực tiếp.

### Lớp 2 — Ngôn ngữ GameFrame

Chuỗi giao diện chính nằm trong `lang/ZH_CN.as` và được quản lý qua catalog:

- `gameframe-zhcn-machine.vi.json`: bản dịch nền.
- `gameframe-zhcn-final.vi.json`: bản dịch thủ công có ưu tiên cao hơn.
- Catalog override theo màn hình, ví dụ `gameframe-welfare-overrides.json`, `gameframe-event-overrides.json`, `gameframe-online-award-overrides.json`.

Tool phải đối chiếu đúng `source` trước khi ghi `target`; source mismatch là lỗi chặn build vì có thể là SWF sai phiên bản hoặc nhầm khóa.

### Lớp 3 — Chữ hardcode trong ActionScript

Các chuỗi không nằm trong ClientLang hoặc CBP phải được sửa theo đúng file/class bằng `tools/swf_source_patcher.py`, ví dụ:

```text
"领取" → "Nhận"
"小时" → " giờ"
"分钟" → " phút"
```

Không thay toàn cục vì cùng chữ có thể có ngữ nghĩa hoặc vùng hiển thị khác nhau ở từng class. Source sau đó được import vào bản sao của `GameFrame.swf` bằng FFDec.

### Quy chuẩn câu chữ và xử lý tràn

- Nút: 1–2 từ (`Nhận`, `Dùng`, `Mua`).
- Tab: 1–3 từ (`Quà Cấp`, `Mã Quà`, `Chia Sẻ`).
- Label hẹp: `Cấp`, `HP`, `MP`, `CS`.
- Không dịch sát từng chữ Trung; giữ nguyên `$num$`, `$value$`, `$time$`, `$libao$`, tag HTML, mã màu, link và payload định tuyến bản đồ/NPC.
- Thứ tự xử lý tràn: rút câu → giảm font riêng 13–14 → xuống dòng khi control hỗ trợ `multiline` → chỉnh vị trí/kích thước của đúng class. Không giảm font hoặc bật `wordWrap` toàn cục.

Mỗi build chỉ được deploy khi không lỗi placeholder/markup/route, CBP+ZIP đọc được hoàn toàn, SWF biên dịch thành công, catalog áp đủ key không source mismatch, QA trực quan đạt và manifest/version/SHA-256 đã cập nhật.

## Nguyên tắc bắt buộc

1. Chỉ sửa `target` trong catalog; không thay `source`, key, thứ tự mảng hoặc payload route.
2. Giữ nguyên `$num$`, `$time$`, `$time0$`, `$time1$`, `$level$`, `$value$`, `$libao$`, HTML và link kỹ thuật. Mọi key thiếu/thừa placeholder là lỗi chặn build.
3. Nút tối đa 1–2 từ, tab tối đa 1–3 từ, label chỉ số dùng dạng ngắn; mô tả dài mới được dùng `<br>` và cỡ 13–14.
4. Không giảm font toàn cục, không bật `wordWrap` hàng loạt. Chỉ chỉnh ActionScript từng control sau khi câu ngắn vẫn không vừa.
5. Làm toàn bộ trong staging copy; chỉ thay `assets/GameFrame.swf`, `assets/ClientLang.txt`, CBP/ZIP và manifest khi audit + kiểm tra trực quan đều đạt.
6. Giữ nguyên toàn bộ thay đổi admin chưa commit trong worktree. Không gộp chúng vào commit UI game.

Quy chuẩn câu chữ gốc nằm tại `translations/VI_STYLE_GUIDE.md`.

## Nhật ký thực thi — 2026-07-12

### Đã hoàn tất ở staging

- Dựng `build/gameframe-ui-20260712/GameFrame.ui.swf` từ bản sao `GameFrame.swf`; SHA-256 staging: `C18885B8AC073EFF39E3C8F612402C38393C4379FBF5AF668387DDE7697D5D45`.
- Áp đúng source hiện hành: 5 key thông tin, 11 key event, 6 key `onlineTimeAward` và 3 chuỗi hardcode chỉ trong `OnlineAwardCell.as`.
- Khôi phục `welfare[118]` từ bản dịch cũ đã mất `$num$` sang target có đủ placeholder, tag và màu. Catalog chuẩn vẫn giữ source của build sạch; `gameframe-ui-legacy-repair-overrides.json` chỉ là cầu nối cho SWF hiện hành.
- Export ngược SWF đã build xác nhận `lang/ZH_CN.as` và `OnlineAwardCell.as` chứa đúng target. Audit hardcode đã qua: 3/3 replacement nhập bytecode, không còn Hán tự hiển thị trong class đã vá.
- Kiểm tra placeholder/markup cho 24 key UI đã tác động: 0 lỗi. `cbp.zip` đọc CRC thành công đủ 225 entry; `welFare.cbp`, `uiawarditems.cbp`, `stditems.cbp` và `clientlang.cbp` đều qua validator CBP.
- Audit độ dài cuối có 752 cảnh báo tổng quát còn ngoài phạm vi (từ 900 ở báo cáo cũ); 24 key của đợt này và toàn bộ `onlineTimeAward` có 0 cảnh báo còn lại. Sáu nhãn còn cảnh báo ban đầu đã được rút tiếp ở catalog, rồi build và export ngược lại.

### Ngoại lệ đã xác định, chưa sửa dữ liệu

- `items.cbp` trong `cbp.zip` là payload zlib ngoài (không có header CBP), còn `EquipExchange.cbp` dùng text không phải UTF-8. Hai file không thuộc nhóm Phúc Lợi đã sửa và không được phép tái mã hóa bằng parser UTF-8 hiện tại; ZIP vẫn đọc CRC hoàn toàn.
- SWF hiện hành đã áp một phần catalog UI cũ. `tools/apply_swf_ui_overrides.py` nay ghi nhận trạng thái `already_compatible` có kiểm soát, chỉ chấp nhận source/target từ catalog được truyền rõ ràng; giá trị lạ vẫn chặn build.

### Deploy UI riêng — hoàn tất 2026-07-12

- Đã commit/push `5ef1f88` và deploy gói riêng `20260712uifit2` bằng `Sync-GameFrameUiFromGitHub.ps1`; gói chỉ chứa `GameFrame.swf`, không đưa file admin vào VPS.
- VPS đã sao lưu `GameFrame.swf` cùng `game/SPDef.php` tại `C:\GPHANTL\server\GPHweb\wwwroot\_deploy_backups\gameframe_ui_20260712_221214`.
- Hash file trên VPS và HTTP công khai đều là `C18885B8AC073EFF39E3C8F612402C38393C4379FBF5AF668387DDE7697D5D45`; `GAMEAPPURL` dùng cache-bust `v=20260712uifit2`.
- `assets/manifest.json` tổng vẫn giữ nguyên vì đang lệch hash ở 7 file admin có sẵn trong worktree; gói UI dùng manifest riêng nên không trộn thay đổi admin vào deploy.
- Còn QA trực quan trong client VPS theo ma trận Bước 5; phát hiện mới phải quay về catalog/build, không vá binary trực tiếp.

## Bước 0 — Chuẩn bị baseline có thể lặp lại

1. Trong `ahtl-web-deploy`, ghi lại `git status --short`, SHA-256 của `assets/GameFrame.swf`, `assets/ClientLang.txt`, `assets/lang/zh-cn/clientlang.cbp`, `assets/lang/zh-cn/cbp.zip` và nội dung `assets/manifest.json`.
2. Tạo thư mục staging ngoài `assets/`, ví dụ `build/gameframe-ui-20260712/`, gồm:
   - bản export ActionScript của `GameFrame.swf`;
   - `lang/ZH_CN.as` đã Việt hóa;
   - catalog hiện hành;
   - log build, report audit và ảnh QA.
3. Chốt Python 3 dùng để chạy tool. Hiện `python` chưa có trong `PATH`; phải xác định launcher Python trước khi thao tác build và lưu thành biến `<PYTHON>` trong log build.
4. Dùng FFDec đóng gói sẵn ở `服务端/GPHANTL/环境/工具/ffdec/ffdec.exe`; chỉ export/import vào bản staging, không sửa SWF production trực tiếp.

**Điểm dừng:** Có manifest/hash baseline và staging có thể export/import lại một SWF không đổi hash logic.

## Bước 1 — Chốt catalog rút gọn theo vùng UI

Tạo các catalog mới, tách theo phạm vi để dễ review và rollback:

- `translations/gameframe-info-overrides.json`: 9 câu input/text đã audit.
- `translations/gameframe-event-overrides.json`: key event từ `active`, `combineActive`, `MonsterTreasure`, `onlineRewards`, `superGift` và các key `welfare` được event tái sử dụng.
- `translations/gameframe-online-award-overrides.json`: 7 key `onlineTimeAward`.
- `translations/gameframe-online-award-hardcoded.json`: ba replacement giới hạn đúng file `scripts/view/game/onlineAward/OnlineAwardCell.as`.

Không sửa trực tiếp `gameframe-zhcn-machine.vi.json`; đặt các quyết định thủ công ở `gameframe-zhcn-final.vi.json` hoặc các catalog override nói trên.

### 1.1. Câu thông tin/ô nhập liệu đã xác nhận

| Key | Target cần dùng |
| --- | --- |
| `bag[82]` | `Dùng nhiều` |
| `bag[83]` | `Nhập số lượng` |
| `storage[28]` | `Nhập số Kim Tệ` |
| `friend[24]` | `Nhập tâm trạng` |
| `guild[136]` | `Nhập 1–6 ký tự` |

Giữ `customerService[11]`, `customerService[29]`, `systemConfig[21]`, `systemConfig[22]` nếu kiểm tra ảnh cho thấy vừa khung; chỉ rút tiếp khi có bằng chứng tràn.

### 1.2. Lô event ưu tiên cao

Đưa ít nhất các key sau vào catalog event, giữ biến số có trong source:

| Key | Mục tiêu câu chữ |
| --- | --- |
| `active[174]` | `Khôi phục nhanh` |
| `active[91]` | `Bù nhanh` |
| `active[92]` | `Nhận quà` |
| `active[146]` | `LC đề xuất:` |
| `active[90]` | `Quà cá nhân` |
| `active[103]` | `Năng động hôm nay` |
| `active[170]` | `Có thể lấy lại` |
| `active[171]` | `Bù Xu khóa` |
| `active[172]` | `Bù Nguyên Bảo` |
| `active[176]` | `Thiếu, dùng Nguyên Bảo` |
| `active[178]` | `Dùng để khôi phục?` |
| `active[183]` | `Lấy lại tài nguyên` |
| `active[128]` | `Sự kiện Mở Server` |
| `happlyWorke[4]` | `Phó Bản Quét Nhanh` |
| `baifu[209]` | `Danh Sách Trúng Lớn` |
| `MonsterTreasure[19]` | `Đạt $num$ cấp nhận` |
| `combineActive[3]` | `Gộp Server:` |
| `welfare[109]` | `Quà Nạp Đầu Gộp` |
| `welfare[118]` | `Thời gian gộp:` |
| `welfare[120]` | `Đổi không giới hạn` |

Tên event riêng như `yuanZuiZhiZhan[0]`, `combineActive[1]`, `welfare[124]`, `welfare[125]` phải được đối chiếu ảnh UI và tài liệu game trước khi chốt thuật ngữ. Không dùng bản dịch máy hoặc dịch theo từng chữ.

### 1.3. Thưởng Online theo thời lượng

Các chuỗi của màn trong ảnh phải thay bằng:

| Key | Target cần dùng |
| --- | --- |
| `onlineTimeAward[0]` | `Thưởng Online` |
| `onlineTimeAward[1]` | `Còn $time0$ nhận quà $time1$` |
| `onlineTimeAward[2]` | `Đã online: $time$` |
| `onlineTimeAward[3]` | `24:00 quà chưa nhận tự gửi thư` |
| `onlineTimeAward[4]` | `Online $time$` |
| `onlineTimeAward[5]` | `Đã nhận hết quà online` |
| `onlineTimeAward[6]` | `Có quà online` |

Trong `OnlineAwardCell.as`, giới hạn replacement theo đúng file/source:

| Source | Target |
| --- | --- |
| `"领取"` | `"Nhận"` |
| `"小时"` | `" giờ"` |
| `"分钟"` | `" phút"` |

`OnlineAwardCell` có card rộng 300 px, nút nằm từ x=250; tiêu đề chỉ có khoảng 170 px trước nút. Vì vậy không dùng lại mẫu `Tích lũy trực tuyến … có sẵn`.

## Bước 2 — Áp catalog vào source staging

1. Dùng `tools/swf_lang_localizer.py patch-source` để tạo `lang/ZH_CN.as` staging từ `assets/ClientLang.txt`, bản tham chiếu và các catalog ClientLang cần thiết.
2. Chạy `tools/apply_swf_ui_overrides.py` lần lượt cho lô info, event, online award và welfare; mỗi lô phải xác minh source hiện tại trước khi thay và sinh report riêng.
3. Chạy `tools/swf_source_patcher.py` với catalog hardcode của Online Award trên copy `scripts/` staging. Không dùng replacement global cho `领取`, `小时`, `分钟` vì chúng xuất hiện ở nhiều màn khác.
4. Nếu câu ngắn vẫn tràn, thêm một layout patch có điều kiện cho class cụ thể. Thứ tự ưu tiên:
   1. rút câu;
   2. giảm cỡ riêng xuống 13–14;
   3. thêm `<br>` cho mô tả có `multiline`;
   4. mới điều chỉnh vị trí/kích thước label.
5. Với Phúc Lợi, giữ catalog `gameframe-welfare-overrides.json` và `gameframe-welfare-layout-patch.json` hiện có; chỉ bổ sung key ngoài phạm vi đã áp.

**Điểm dừng:** Mỗi report ghi đúng số key thay đổi, không có key thiếu và không có source mismatch.

## Bước 3 — Build CBP cho các text Phúc Lợi liên quan

1. Chỉ sửa target trong `welfare.cbp.vi.json` và `stditems-welfare.cbp.vi.json` khi cần đồng bộ nhãn/event với GameFrame.
2. Dùng `tools/cbp_localizer.py apply-zip` trên bản sao `cbp.zip`; không giải nén rồi thay text toàn payload.
3. Validate từng CBP đầu ra bằng `tools/cbp_localizer.py validate`, kiểm tra ZIP có đủ entry, sau đó chép các file đã build về staging asset.
4. Đối chiếu các nhóm: `welFare.cbp`, `uiawarditems.cbp`, `stditems.cbp`, `clientlang.cbp` và `cbp.zip` để tránh tình trạng ClientLang mới nhưng archive cũ.

**Điểm dừng:** Không có lỗi CBP/header/ZIP; source, clientlang.cbp và cbp.zip cùng phiên bản build.

## Bước 4 — Tái biên dịch GameFrame và kiểm tra tĩnh

1. Import source ActionScript staging vào một copy `GameFrame.swf` bằng FFDec.
2. Export ngược các class đã thay đổi và xác nhận các target đã biên dịch vào SWF:
   - `lang/ZH_CN.as`;
   - `view/game/onlineAward/OnlineAwardCell.as`;
   - các class event có layout patch (nếu có).
3. Chạy `tools/audit_gameframe_localization.py` cho tất cả catalog đã dùng.
4. Chạy `tools/audit_gameframe_hardcoded.py` với source gốc, overlay staging, compiled root và compile-exclusions.
5. Chạy lại `tools/audit_gameframe_ui_length.py` sau build. Báo cáo cũ tạo trước Welfare không được dùng làm bằng chứng hoàn tất.
6. Đặt ngưỡng chấp nhận:
   - không lỗi placeholder, markup, route/NPC;
   - không còn `nhận được` ở nút 50 px của Online Award;
   - không còn các câu dài đã liệt kê ở lô info/event ưu tiên;
   - mọi cảnh báo còn lại phải có owner, ảnh QA và lý do giữ nguyên.

## Bước 5 — QA trực quan trong client

Kiểm tra bằng launcher/projector ở độ phân giải logic hiện hành, chụp ảnh trước/sau cho từng trạng thái.

### Ma trận bắt buộc

1. **Thưởng Online:** 10 phút, 30 phút, 1 giờ, 2 giờ, 6 giờ; trạng thái chưa nhận/đủ điều kiện/đã nhận; test lúc hết mốc để kiểm tra dòng `24:00`.
2. **Phúc Lợi:** Quà Online, Đăng Nhập, Quà Cấp, Quà Nạp, Mã Quà, Chia Sẻ, Cập Nhật; test có và không có `$num$`, `$value$`, `$libao$`.
3. **Hoạt động:** bù tài nguyên, bù bằng Xu khóa/Nguyên Bảo, năng động ngày, Mở Server, Gộp Server, Săn Kho Báu, Quà Online quay thưởng.
4. **Input/popup:** dùng nhiều vật phẩm, nạp/rút Kim Tệ, tâm trạng, tạo Bang, xác nhận event.
5. Xác nhận không chồng chữ, không cắt nút, không dính số + đơn vị, không mất màu/HTML và không che icon/nút nhận.

Mọi phát hiện phải quay lại Bước 1 hoặc 2; không sửa trực tiếp binary sau QA.

## Bước 6 — Đóng gói, commit và deploy có kiểm chứng

1. Chép đúng asset đã QA vào `assets/`, tăng `assets/manifest.json.version` theo phiên bản mới, tính lại SHA-256 cho mọi file thay đổi.
2. Chỉ stage các file GameFrame/CBP/catalog/report/plan thuộc đợt này; loại trừ toàn bộ thay đổi admin dở dang.
3. Chạy kiểm tra cuối: `git diff --cached --check`, audit, validate CBP và đối chiếu manifest hash.
4. Commit riêng với thông điệp nêu rõ UI localization/event/online award.
5. Deploy bằng workflow chuẩn `C:\GPHANTL\Sync-FromGitHub.ps1` với đúng commit SHA. Script phải tạo backup và cập nhật cache-bust `GAMEAPPURL`.
6. Sau deploy, xác minh cả file VPS và HTTP công khai cho:
   - `GameFrame.swf`;
   - `data/commonasset/ClientLang.txt`;
   - `data/lang/zh-cn/clientlang.cbp`;
   - `data/lang/zh-cn/cbp.zip`.
7. Mở client từ môi trường sạch cache, chụp lại ma trận QA tối thiểu của Thưởng Online, Phúc Lợi và một màn event.

## Tiêu chí hoàn tất

- 100% key trong catalog mới được áp đúng source và có report.
- Không lệch placeholder/tag/route; CBP và ZIP hợp lệ.
- Thưởng Online hiển thị đúng các mẫu `Còn X nhận quà Y`, `Online X`, `Nhận`, `1 giờ 30 phút`.
- Các text info/event ưu tiên không còn dịch máy, không tràn UI và có ảnh xác minh.
- Asset VPS/public hash khớp manifest phiên bản mới.
- Không có file admin hoặc cấu hình bí mật bị đưa vào commit/deploy UI game.

## Đợt bổ sung từ audit ảnh — đã deploy 2026-07-12

- Phạm vi ảnh: Mini Client, Hoạt Động/Năng động, Dọn nhanh và Cánh.
- Đã thêm quy tắc viết hoa chữ cái đầu câu, nút, tab, nhãn và trạng thái; đơn vị ghép số như `đ`, `giờ`, `phút` là ngoại lệ.
- SWF: 31 override cho các key `clientLogon`, `active`, `bag`, `property`; rút bộ lọc Hoạt Động còn `Lọc · Tất cả · Cấp · Mạnh · Đồ · Vàng · PK · Khác`, vẫn giữ đủ link `event:0..6`.
- CBP: 60 target tại `activity.cbp`, `achieves.cbp`, `fubennewClient.cbp` và `WingConfig.cbp`; không sửa `npc.name`, scene hoặc tọa độ tự tìm đường.
- Staging đã qua: source match 31/31, placeholder/markup/độ dài UI 31/31, ZIP CRC 225 entry, bốn CBP parse lại được, và export ngược SWF xác nhận toàn bộ target.
- Asset deploy riêng phiên bản `20260712uifit3` chỉ gồm `GameFrame.swf` và `data/lang/zh-cn/cbp.zip`; không dùng `assets/manifest.json` tổng vì worktree admin còn thay đổi độc lập.
- Đã deploy từ commit `83caaef` bằng script giới hạn hai asset; backup VPS: `C:\GPHANTL\server\GPHweb\wwwroot\_deploy_backups\gameframe_screenshot_20260712_224504`.
- Hash VPS và HTTP công khai đã khớp manifest: `GameFrame.swf` `52658E0842259B62F1E3CE251120105AC3C3F5E4D3B4BBF8A2F6905D17E2B359`, `cbp.zip` `C88DA837EE1DC2C5D01079787345CB0886C449224C0BBACB8B0CF7B87C4919AF`.
- `GAMEAPPURL` đã cache-bust tới `GameFrame.swf?v=20260712uifit3`; còn lại QA trực quan trong client với cache sạch.

## Chống regression khi cập nhật GameFrame

- Không được import `ZH_CN.as` từ `GameFrame.base.swf` hoặc một staging cũ vào asset mới. Mỗi build phải export `lang/ZH_CN.as` từ đúng `assets/GameFrame.swf` đang được deploy, rồi chỉ áp delta catalog của đợt đó.
- Trước deploy, bắt buộc export ngược SWF và chạy `tools/verify_swf_ui_build.py`. Gate kiểm toàn bộ catalog Info, Event, Thưởng Online, Welfare, audit ảnh và các source patch; key mất target hoặc patch biến mất là lỗi chặn deploy.
- Với CBP, luôn lấy `assets/lang/zh-cn/cbp.zip` hiện hành làm input rồi áp thêm catalog mới tuần tự. Không dùng archive staging/baseline cũ để thay toàn bộ ZIP.
- Hotfix `20260712uifit4` đã khôi phục 21 key UI bị baseline cũ ghi đè, gồm 6 key Thưởng Online; gate xác nhận 151 key UI và 4 source patch trước deploy.

## Nhiệm Vụ và phần thưởng — đợt 1

- `stdquest.cbp`: đã dịch toàn bộ 6 nội dung còn Hán ngoài payload route và tên `Sứ Giả Phó Bản`; mọi `/Mscene:x:y:npc` giữ nguyên từng ký tự.
- `monster.cbp`: tên quái `魔化鸡` hiển thị là `Gà Ma Hóa`; `entityName` tự tìm đường không thay đổi.
- Phần thưởng Nhiệm Vụ dùng `KN`, `Vàng`, `Xu khóa`. Số từ `10.000` dùng hậu tố K, một số lẻ thập phân: `10.000 → 10K`, `35.083 → 35.1K`; chỉ đổi presentation ở `QuestHlp`, không đổi số server.
- Đợt 1 còn phát hiện 240 tên item Hán chưa có target catalog và thoại NPC không nằm trong `cbp.zip`. Hai nhóm này phải đi theo catalog/owner riêng, không dịch trực tiếp các khóa route `prom.npc`, `comp.npc`, `location.entityName`.

## Triển khai Nhiệm Vụ — 2026-07-12

- Đã deploy commit `0ca9361` với phiên bản `20260712uifit5`. Gói này kế thừa toàn bộ UI đã khôi phục ở `uifit4`, sau đó chỉ thêm delta Nhiệm Vụ/CBP.
- Hash đã kiểm chứng trên VPS và HTTP công khai: `GameFrame.swf` `56952F889B86DC3EA58CECDE99FA9776870A187E618173A065207B1BA8F82BB9`; `cbp.zip` `BC7442A7DB79D548DF2156BD4C40B7F24027D41F0676B2D7ECC3D60EC16643C3`.
- Backup trước deploy: `C:\GPHANTL\server\GPHweb\wwwroot\_deploy_backups\gameframe_screenshot_20260712_232038`.
- Quy tắc bắt buộc cho các phiên bản sau: build từ đúng hai asset hiện hành, áp tuần tự delta mới, export ngược và chạy regression gate trước manifest/deploy. Không được dùng SWF, `ZH_CN.as` hoặc `cbp.zip` baseline cũ.

## LogicServer — thoại NPC, tên NPC, nhiệm vụ và item

- Owner đã xác minh: `LogicServer/data/language/Zh-CN/NormalTalk.txt` (thoại), `EntityName.txt` (tên NPC/quái), `Quest.txt` (mục tiêu/nội dung nhiệm vụ), `Item.txt` (tên/mô tả item). Script NPC chỉ tham chiếu các key `Lang.*`, không chứa câu thoại trực tiếp.
- Snapshot VPS là input bắt buộc. Catalog `translations/logicserver-core.vi.json` lưu `source`/`target` theo `file + key + occurrence`; công cụ `tools/server_lang_localizer.py` chặn source mismatch, placeholder, màu, xuống dòng và payload `/M`/`/@@`.
- Bản staging `20260712logicvi1` áp được 11.687 entry: 489 thoại NPC, 2.191 tên thực thể, 3.260 chuỗi nhiệm vụ và 5.747 chuỗi item. Trong 747 chuỗi nhiệm vụ có route, payload máy được phục hồi từ source trước khi dịch phần nhãn hiển thị.
- Asset đủ bốn file, manifest SHA-256 và script deploy bảo trì đã được đóng gói. Script từ chối chạy khi LogicServer còn hoạt động, tạo backup riêng và kiểm hash trước/sau copy; vì vậy cập nhật sau không thể vô tình ghi đè bằng baseline cũ.
- Chưa deploy phần LogicServer trong lúc server đang chạy: còn 373 entry bị loại vì translation cũ làm đổi màu hoặc xuống dòng, 215 key VPS mới chưa có target, 24 tên item và 223 mô tả item vẫn Hán. Các nhóm này phải dịch/QA từng entry trước đợt kế tiếp.
- Đã deploy `20260712logicvi1` trong bảo trì ngày 2026-07-13: task `AHTLLogicServer` được dừng/chạy lại theo Scheduled Task, process mới `LogicServerCQ32_R.exe` PID 2916 hoạt động. Backup deploy: `C:\GPHANTL\server\_deploy_backups\logicserver_language_20260713_000601`; backup an toàn độc lập: `C:\GPHANTL\server\_deploy_backups\logicserver_language_pre_20260712logicvi1_20260713_000554`. Bốn hash ngôn ngữ trên VPS khớp manifest.

## Nhiệm Vụ và item — đợt 2 (`20260712uifit6`)

- `QuestHlp` có alias 251 NPC/quái chỉ ở nhãn hiển thị. `Location.entityName` vẫn là tên Hán gốc nên tự tìm đường, click link và trả nhiệm vụ không đổi.
- `monster.cbp` dịch thêm 1.596 tên quái; `stditems.cbp` dịch 240 tên item còn Hán. Sau build, hai CBP không còn node `.name` chứa Hán tự.
- Source map được sinh lại từ catalog LogicServer bằng `tools/generate_quest_alias_catalogs.py`; 12 alias trùng được chốt một tên thống nhất và hai item test được dịch riêng.
- Build xuất ngược đã xác nhận 154 key UI cũ và 20 source patch; CBP ZIP có 225 entry, CRC hợp lệ. Mọi lần build sau phải lấy `assets/GameFrame.swf`/`cbp.zip` hiện hành làm input, chạy generator, apply hai catalog CBP mới và regression gate trước deploy.
- Đã deploy commit `d3e7ceb`; backup VPS: `C:\GPHANTL\server\GPHweb\wwwroot\_deploy_backups\gameframe_screenshot_20260713_000216`. Hash VPS và HTTP công khai: `GameFrame.swf` `8EC3B3957CA302F3DA9F78C90128CD255A414FE25E3624BDAC612F3FE600BB21`, `cbp.zip` `E1F3C3D019612601A435B8C3278963552EF1DCC80EF76B007E595C5F2A9CDD73`.

## Sự cố LogicServer — rollback bắt buộc 2026-07-13

- Gói `20260712logicvi1` không được dùng lại. Khi LogicServer khởi động, log báo lỗi Lua `'}' expected ... near '?'` trong Language Config; client vì vậy dừng ở màn hình loading 100%.
- Kiểm tra bằng `luac 5.1` xác nhận lỗi cú pháp đầu tiên là `Item.txt:i864`, dòng 866: parser cũ không nhận nháy escape `\"`, cắt chuỗi và để payload Hán ở ngoài string. `Item.txt:i2875` là lỗi thứ hai: target có một dấu `\` lẻ ở cuối (source không có), sẽ escape nháy đóng Lua sau khi `i864` được sửa. Không phải do logic route/NPC thiếu điều kiện.
- Audit Lua phát hiện thêm lỗi parser: nó không nhận nháy đã escape (`\"`) nên có thể cắt sai entry, ví dụ `Item.txt:i864`. Parser đã được sửa; mọi gói server về sau phải lấy snapshot trực tiếp từ VPS và xác nhận source của từng entry trước khi tạo catalog.
- Đã khôi phục toàn bộ `NormalTalk.txt`, `EntityName.txt`, `Quest.txt`, `Item.txt` từ `C:\GPHANTL\server\_deploy_backups\logicserver_language_pre_20260712logicvi1_20260713_000554`, sau khi tạm vô hiệu task `AHTLLogicServer` để không có tiến trình giữ hoặc ghi đè file. Bốn SHA-256 trên VPS đều khớp bản sao lưu; process LogicServer mới khởi động không còn lỗi nạp ngôn ngữ.
- Manifest của gói bị đánh dấu `blocked`; script deploy sẽ dừng trước khi tải/copy bất kỳ file nào. Không được bỏ cờ này chỉ để thử lại.
- `tools/server_lang_localizer.py` chặn từ lúc tạo/apply catalog nếu placeholder, route, màu, xuống dòng hoặc số dấu `\` cuối chuỗi khác source; đồng thời từ chối nháy chưa escape, control character và số dấu `\` lẻ ở cuối target.
- Bắt buộc chạy `scripts/Test-LogicServerLua.ps1` với `luac` Lua 5.1 trước manifest/deploy. Script copy file sang staging ASCII không BOM rồi chạy `luac -p` cho đủ bốn file, vì Lua 5.1 cũ không đọc trực tiếp đường dẫn Unicode/BOM trong workspace.
- Manifest deploy bắt buộc có `source_sha256` cho từng file và script kiểm hash file đang chạy trên VPS trước khi tải/copy. Nếu server đang ở phiên bản khác, toàn bộ deploy dừng trước khi tạo backup hoặc sửa file.
- Từ đây, tên NPC/quái, item và mục tiêu nhiệm vụ tiếp tục dịch ở GameFrame/CBP theo lớp hiển thị, giữ nguyên payload và tên gốc phục vụ route. Thoại NPC phía LogicServer chỉ được mở lại sau khi có trình xác thực Lua tương thích và danh sách entry dịch thủ công đã QA từng câu.

## Snapshot và catalog LogicServer sạch — 2026-07-13

- Đã tải trực tiếp bốn file live sau rollback vào `assets/logicserver-language-source/Zh-CN/`; `snapshot-manifest.json` lưu length và SHA-256 VPS. Snapshot qua `luac 5.1` 4/4 file.
- `tools/server_lang_localizer.py export` tạo `translations/logicserver-core-20260713.vi.json` gồm 13.190 entry, với `target` ban đầu bằng `source`. Catalog self-apply giữ nguyên tuyệt đối hash bốn file và tiếp tục qua Lua 5.1.
- Catalog `translations/logicserver-core.vi.json` cũ bị khóa vì parser cũ xử lý sai escaped quote; tool apply và generator alias đều từ chối catalog bị khóa. Không được khôi phục nó để lấy lại bản dịch cũ.

## Thoại NPC batch 1 — staging 2026-07-13

- Đã dịch 30 thoại NPC đầu game trong `NormalTalk.txt`: các key `h00006..h00015` chọn lọc, `h00017..h00021`, `h00023`, `h00027..h00033`, `h00038..h00041`, `h00043`, `h00049`, `h00051`.
- Phong cách dùng xưng hô `ta/ngươi`, tên riêng Diablo quen thuộc, câu mở đầu viết hoa và nhãn Nhiệm Vụ ngắn. Toàn bộ tag, escape và số mốc giữ nguyên.
- Apply staging chỉ đổi `NormalTalk.txt` (SHA-256 `235608511DDF7BE187A3307B3A3DAE34034C69BDF349E5D35DF6515CA3EB671E`); ba file EntityName, Quest, Item vẫn khớp snapshot.
- Gate source/placeholder/markup và Lua 5.1 đã qua. Chưa deploy: manifest LogicServer vẫn bị khóa đến khi batch được QA trực quan và có gói version mới.

## Thoại NPC batch 2 — staging 2026-07-13

- Đã dịch thêm 30 thoại NPC: `h00052..h00067` chọn lọc, `h00073..h00079` và `h00083..h00089`.
- Ưu tiên nhóm lính đánh thuê, Trại Rogue, Harrogath và NPC nhiệm vụ; tên riêng, số PK và thuật ngữ Diablo được giữ thống nhất với batch 1.
- Tổng 60 target NormalTalk đã Việt hóa không còn Hán tự. Gate source/placeholder/markup, viết hoa đầu câu và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (`168D755C8DF9B02B7636FA434438AACC8E61A5520FC2C238B9DF8E262E21E82F`); EntityName, Quest, Item vẫn giữ hash snapshot. Chưa deploy VPS.

## Thoại NPC batch 3 — staging 2026-07-13

- Đã dịch thêm 30 thoại NPC: `h00090`, `h00097..h00105`, `h00107`, `h00109..h00114`, hai occurrence `h00115`, và `h00118..h00128`.
- Ưu tiên Rogue, Tyrael, Amazon, Harrogath và Kurast; thống nhất thuật ngữ KN, Hào Quang, Thánh Kỵ Sĩ, Đá Thế Giới.
- Tổng 90 target NormalTalk đã Việt hóa, không có Hán tự. Gate source/placeholder/markup, viết hoa đầu câu và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (`965CFC5561B49863B3D18E7A9AD145438F8D09C3721BF84115E05EC6BAB06CEC`); EntityName, Quest, Item vẫn giữ hash snapshot. Chưa deploy VPS.

## Thoại NPC batch 4 — staging 2026-07-13

- Đã dịch 30 entry liên tiếp `h00129..h00158`, gồm thoại Pháp Sư, Druid, NPC Pháo Đài, Rừng Tiên Tích và nhóm thông báo Quà Nạp.
- Chuẩn hóa cách viết `Nguyên Bảo`, `Quà Nạp Theo Mốc`, `Kỵ Sĩ Trưởng`, cùng phong cách xưng hô `ta/ngươi`; mọi câu đã viết hoa ký tự đầu tiên.
- Tổng 120 target NormalTalk đã Việt hóa, không có Hán tự. Gate source/placeholder/markup và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (`25B3F9FA535383EDDCC1D2FA1182E5E6A53B3287D12E68B32B1469623C96E23E`); EntityName, Quest, Item vẫn giữ hash snapshot. Chưa deploy VPS.

## Thoại NPC batch 5 — staging 2026-07-13

- Đã dịch 30 thoại NPC `h00159..h00188`: Bạch Nhật Môn, các cửa hàng, Thôn Biên Giới và người tị nạn vùng Tuyết Sơn.
- Giữ giọng MMORPG ngắn gọn, xưng hô `ta/ngươi`; chuẩn hóa thuật ngữ Long Văn, Sách Kỹ Năng, Ma Tộc và Quỷ Dữ. Mọi câu viết hoa ký tự đầu tiên.
- Tổng 150 target NormalTalk đã Việt hóa, không có Hán tự. Gate source/placeholder/markup và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (`F65F6DC2CB1CD8E2381E04D7D2C04369D78B582482EB410E29797F8096DE77F1`); EntityName, Quest, Item vẫn giữ hash snapshot. Chưa deploy VPS.

## Thoại NPC batch 6 — staging 2026-07-13

- Đã dịch 22 thoại còn lại của cụm `h00189..h00210`: Băng Phong Cốc, La Lan, Thành Huyết Sắc, Tháp Thất Lạc và NPC Patty.
- Thống nhất tên hiển thị Maya, Ma Đạo Sư, Chiến Minh, Thành Huyết Sắc; giữ giọng thoại ngắn và viết hoa ký tự đầu tiên.
- Tổng 172 target NormalTalk đã Việt hóa, không có Hán tự. Gate source/placeholder/markup và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (`03D3E290A380B97D66F61A9A28EF84FE3A7A05B149EC251F889486917B24C32B`); EntityName, Quest, Item vẫn giữ hash snapshot. Chưa deploy VPS.

## Hotfix parity nhiệm vụ ID 2 — deploy 2026-07-13

- Audit so sánh `stdquest.cbp` đang deploy với 2.434 file task LogicServer: 207 ID nhiệm vụ chung được đối chiếu; chỉ task ID `2` (`Thực Lực Tiểu Thí`) lệch target. Client yêu cầu diệt `Gà Ma Hóa` ID `862` x2 tại Biên Giới Thôn `(107,120)`, trong khi `task2.txt` trên server có `target = {}`.
- Không bật hàng loạt `MonsterClass`: toàn bộ 1.715 dòng `#include` trong `MonsterConfig.txt` đều có tiền tố `--`, nên đây không phải chỉ dấu spawn runtime riêng cho ID 862. Không có thay đổi diện rộng ở file này.
- Đã thêm target ID `862` x2 vào `task2.txt`, và callback `OnPromCreateMonsterBatch` trong `NormalFuncForQuest.txt` để spawn riêng cho người nhận nhiệm vụ hai Gà Ma Hóa tại `(106,120)` và `(108,120)`, tồn tại 120 giây.
- Local gate: Lua 5.1 qua cho `task2` và callback mới; parity target sau sửa `207/207`. Deploy VPS có backup `C:\GPHANTL\server\_deploy_backups\quest2_monster_spawn_20260713_020509`; SHA-256 `task2.txt` `2922711C5306D9997BE7FB6E180803A55993C6C72F78B9488934A1B4606AF531`, `NormalFuncForQuest.txt` `4D9C34174A5A7BB818BDEEC79CC713D68FCFB45799F1AEF7C657DE85404BF7D7`.
- LogicServer restart thành công PID `7592`, log `LogicServer_2026-07-13 02-05-17.log.txt` không có lỗi. Cần QA trong client bằng cách nhận mới task ID 2; quest đã nhận trước hotfix cần hủy/nhận lại để callback spawn chạy.

## Thoại NPC batch 7 — staging 2026-07-13

- Đã dịch 30 thoại `NormalTalk`: NPC Thành Trì/Chiến Trường (`n00001..n00017` chọn lọc), Động Bảo Thạch, Ma Vực Xích Nguyệt và hướng dẫn triệu hồi Boss (`n02024..n02051` chọn lọc).
- Thống nhất cách dùng KN, Vàng, Boss, Bang Hội và Hào Quang; giữ giọng MMORPG ngắn, xưng hô `ta/ngươi`, mọi câu viết hoa ký tự đầu tiên.
- Tổng 202 target NormalTalk đã Việt hóa, không có Hán tự. Gate source/placeholder/markup và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (`4C0F76F6E4A3E9644F6D8747A29071035FCB4D28E661AE79CB9B834C6E46474B`); EntityName, Quest, Item vẫn giữ hash snapshot. Chưa deploy phần dịch thoại lên VPS.

## Hotfix nhiệm vụ ID 2 bị kẹt tự tìm đường — deploy 2026-07-13

- Ảnh QA xác nhận nhân vật nhận `Thực Lực Tiểu Thí` đứng yên ở trạng thái `自动寻路中`, tiến độ `Gà Ma Hóa 0/2`. `task2.txt` và callback trên VPS vẫn đúng hash của hotfix parity trước, nên không phải payload route bị Việt hóa sai.
- Nguyên nhân còn lại nằm ở vòng đời mục tiêu: callback chỉ tạo hai quái lúc nhận nhiệm vụ và đặt `liveTime = 120`; bốn bãi Gà Ma Hóa ID `862` trong `data/envir/scene/refresh1.txt` đều đang nằm trong block comment. Nhiệm vụ đã nhận trước hotfix, đăng nhập lại hoặc kéo dài quá 120 giây sẽ không còn thực thể để auto-path khóa mục tiêu.
- Đã khôi phục một bãi thường trú gồm 13 Gà Ma Hóa trong vùng gốc `(107..115, 120..128)`, hồi sau 1 giây; callback spawn tức thời vẫn được giữ. Cách này tự phục hồi cho cả nhiệm vụ đang nhận dở, không cần hủy/nhận lại.
- VPS đã sao lưu file cũ tại `C:\GPHANTL\server\_deploy_backups\quest2_scene_spawn_20260713_023931\refresh1.txt`. Hash `refresh1.txt` sau deploy là `3DEB06575C434A5E4CDDF081057CB728050BC0B3EE401B8B4C6C5F4E53B4E5ED`.
- Task `AHTLLogicServer` đã khởi động lại, process mới `LogicServerCQ32_R.exe` PID `6904`; log `LogicServer_2026-07-13 02-45-39.log.txt` nạp xong engine, không có lỗi scene/refresh/Lua. Còn QA trực quan: đăng nhập lại nhân vật đang giữ task ID 2, xác nhận tự chạy tới bãi quái, hạ 2 mục tiêu và trả nhiệm vụ.

### Lớp tự phục hồi và đo runtime nhiệm vụ ID 2

- Phiên client sau hotfix đầu đã ghi nhân vật ID `90` từ `(109,21)` tới `(109,121)`, scene `1`; `goingquest` vẫn là `idtask=2, id=862, value=0`. Auto-path vì vậy đã hoạt động, nhưng client không có mục tiêu hợp lệ để tăng tiến độ.
- Đã thêm handler đăng nhập `ensureFirstQuestMonsters` trong `ActorLoginHandler.txt`: khi vào scene `1`, server gọi `Fuben.getLiveMonsterCount(..., 862)`; nếu dưới 2 thì dùng API scene `Fuben.createMonsters` tạo 6 mục tiêu thường trú tại vùng nhiệm vụ. Handler ghi `[Quest2Monitor]` để xác nhận số thực thể mà runtime thật nhìn thấy.
- Deploy có backup `C:\GPHANTL\server\_deploy_backups\quest2_login_recovery_20260713_030627`; hash mới `ActorLoginHandler.txt` là `2C8A785E70279C877BF37F2718432736F97282A837E9698553762D26BD0B79E3`. LogicServer khởi động PID `6520`, log `LogicServer_2026-07-13 03-06-03.log.txt` chưa có lỗi script/load.
- Chưa có phiên đăng nhập mới sau deploy trong cửa sổ theo dõi 60 giây, nên còn chờ client QA để đọc `liveBefore` và xác nhận tiến độ `0/2` tăng đúng.

## Thoại NPC batch 8 — staging 2026-07-13

- Đã dịch 30 thoại nhóm Lửa Trại/Hỏa Chủng (`gh00001..gh00036` chọn lọc), gồm mua thời gian đốt lửa, nâng cấp, buff Hỏa Chủng, nướng thức ăn và giao dịch.
- Chuẩn hóa thuật ngữ `Lửa Trại`, `Hỏa Chủng`, `Vận Tiêu`, `Nguyên Bảo`, `Vàng Khóa`, `KN`; giữ nguyên toàn bộ placeholder `%d`, tag màu và escape gốc. Mọi câu bắt đầu bằng ký tự viết hoa.
- Tổng 232 target NormalTalk đã Việt hóa; 30 target mới không còn Hán tự, placeholder/markup qua gate.
- Apply staging chỉ đổi NormalTalk (`5933CD93F70E55EFA0D0A4CEAC482F25EBC928A5807D444D63C7289C2A51233B`); EntityName, Quest, Item vẫn giữ hash snapshot. Lua 5.1 đạt 4/4 file. Chưa deploy VPS.

## Thoại NPC batch 9 — staging 2026-07-13

- Đã dịch 30 thoại/nhãn sự kiện: Đá Thế Giới, Chiến Trường Hắc Ám, Công Thành, Cống Hiến, Mê Thành Đoạt Bảo, sự kiện đôi lứa và Nhà Thờ Hắc Ám.
- Thống nhất `Bang Hội`, `Đá Thế Giới`, `Nguyên Bảo`, `CS`, `Vàng`, `Mê Thành Đoạt Bảo`; màu/tag, placeholder và các payload hiển thị được giữ nguyên. Mọi câu bắt đầu bằng ký tự viết hoa.
- Tổng 262 target NormalTalk đã Việt hóa; 30 target mới không còn Hán tự, placeholder/markup qua gate.
- Apply staging chỉ đổi NormalTalk (`28EF53A07D056752190DE9039613C1EA39296371578E79740D5F331CFD417D86`); EntityName, Quest, Item vẫn giữ hash snapshot. Lua 5.1 đạt 4/4 file. Chưa deploy VPS.

## Thoại NPC batch 10 — staging 2026-07-13

- Đã dịch 30 thoại/nhãn Nhà Thờ Hắc Ám, Tháp Ánh Sáng và hệ thống kết hôn; thông báo có payload tự tìm đường vẫn giữ nguyên, không đưa vào batch.
- Thống nhất `Nhà Thờ Hắc Ám`, `Tháp Ánh Sáng`, `Nguyên Bảo`, `KN`, `Trang Bị`, `Đạo Cụ`; giữ nguyên `%s`, tag tên người chơi, màu, escape và toàn bộ cấu trúc dữ liệu.
- Tổng 292 target NormalTalk đã Việt hóa; 30 target mới không còn Hán tự, placeholder/markup qua gate.
- Apply staging chỉ đổi NormalTalk (`6FF776FEC49B3C42E696E6D4D32F94A4EFF55B9586BA96DBAC122D90DC5BF0CF`); EntityName, Quest, Item vẫn giữ hash snapshot. Lua 5.1 đạt 4/4 file. Chưa deploy VPS.

## Thoại NPC batch 11 — staging 2026-07-13

- Đã dịch 30 thoại/nhãn hôn lễ, phó bản Kho Báu Thánh Đường và thông báo đội/phó bản ngắn; các chuỗi có route hoặc nhiều dòng escape tiếp tục để QA riêng.
- Chuẩn hóa `Vàng Khóa`, `Bang Hội`, `Giám Mục`, `Linh Mục Thánh Đường`, `Phó Bản`; giữ nguyên `%s` và tag tên người chơi.
- Tổng 322 target NormalTalk đã Việt hóa; batch mới không còn Hán tự, placeholder/tag qua gate.
- Apply staging chỉ đổi NormalTalk (`3B8859E2E37A2797B1419C1911EA291B2FADF634D001EBE3390102722742BC16`); EntityName, Quest, Item giữ hash snapshot. Lua 5.1 đạt 4/4 file. Chưa deploy VPS.

## Thoại NPC batch 12 — staging 2026-07-13

- Đã dịch 27 chuỗi Thử Luyện Boss và Đại Sảnh Thăng Cấp: triệu hồi Boss, giới hạn, phần thưởng và nhận KN.
- Chuẩn hóa `Boss`, `KN`, `Nguyên Bảo`, `Vàng Khóa`, `Phó Bản`; giữ nguyên tag màu và placeholder `%d`.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi. Các nhãn trùng không được thay toàn cục, sẽ xử lý theo key ở batch sau.

## Thoại NPC batch 13 — staging 2026-07-13

- Đã dịch 20 nhãn vượt ải, phó bản cá nhân/đội và đại sứ sự kiện; giữ nguyên tag `<br>` và placeholder.
- Chuẩn hóa `KN`, `Trang Bị`, `Vàng Khóa`, `Nguyên Bảo`, `Boss`, `Phó Bản` và giọng MMORPG ngắn gọn.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `1CDF1F4357177BB0DEE60ED9E5858D3528F262B86048669ACA1AC870B6020E31`). Chưa deploy VPS.

## Thoại NPC batch 14 — staging 2026-07-13

- Đã dịch 10 thoại NPC Thánh Thành và bảng quảng cáo Bang Hội, giữ phong cách game và tên riêng Diablo.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `DEF184E18B929B1E5B8BDA389F2D9A64071776806913AFB994283E3B97B2A044`). Chưa deploy VPS.

## Thoại NPC batch 15 — staging 2026-07-13

- Đã dịch 15 thoại NPC và nhãn sự kiện ngắn, gồm Ảnh Vệ, Thánh Kỵ Sĩ, Tinh Linh Hoa Hồng và quản lý Bang Hội.
- Chuẩn hóa `10K Vàng` cho giá trị 10.000, cùng `Nguyên Bảo`, `Bang Hội`; tag rich image/màu và escape được giữ nguyên.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `9DFF90F4EBD4287AB2DF4A3C14DC1B0A6ED1E7921582881E92AF0CF142FB2152`). Chưa deploy VPS.

## Thoại NPC batch 16 — staging 2026-07-13

- Đã dịch 21 thông báo hôn lễ: pháo hoa, kẹo cưới, tiệc cưới, cầu hôn và danh hiệu.
- Chuẩn hóa `100K Vàng Khóa`, `Nguyên Bảo`, `Kẹo Cưới`; không thay đổi chuỗi route/tự tìm đường.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `D977660AA6A511F0557439FB64BC107072EF4B8491435DAA02EED176203A9A9D`). Chưa deploy VPS.

## Thoại NPC batch 17 — staging 2026-07-13

- Đã dịch 19 thoại NPC Luyện Ngục/Vực Sâu, tiện ích phó bản, Bái Sư và Khối Lập Phương Horadric.
- Thống nhất tên hiển thị Vực Sâu Liệt Diệm, Thủ Hộ Vực Sâu, Phó Bản và Bang Hội; không chạm route hay payload máy.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `39781D3F45E9FAE17DB98005DC32B3DDAB575AF47B794088A8A001E2B6051F88`). Chưa deploy VPS.

## Thoại NPC batch 18 — staging 2026-07-13

- Đã dịch 12 nhãn/nhắc nhở Đại Sảnh Thăng Cấp, hôn lễ, Lễ Hội Pháo Hoa và sự kiện server mới.
- Chuẩn hóa `KN`, `VIP`, `Nguyên Bảo`, `Phó Bản`; không thay route hay payload máy.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `B77D6F0BA1C21B05DA11821765F0E0895D33B67273D2A492772C92EAA0BE5DFF`). Chưa deploy VPS.

## Thoại NPC batch 19 — staging 2026-07-13

- Đã dịch 9 mô tả sự kiện: treo máy an toàn, hoàn nạp Server Mới, Niên Thú, chiếm ô và Lửa Trại Tranh Đoạt.
- Giữ nguyên tag màu, `%d`/`%s`, thời gian, tọa độ và từng ngắt dòng source. Gate đã phát hiện thiếu một ngắt dòng ở `ghzdz001`; đã khôi phục trước khi pass.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `B090D34714E0440A6992039E71F86E963F2C46C846A269D36F558A7A38DA6304`). Chưa deploy VPS.

## Thoại NPC batch 20 — staging 2026-07-13

- Đã dịch 9 mô tả tượng vinh danh cho Bang Hội, Chiến Binh, Pháp Sư, Đạo Sĩ và các hạng Liên Server.
- Chuẩn hóa `CS`, `Bang Chủ`, `Bang Hội`, `Liên Server`; giữ nguyên tag `<br>`, ngắt dòng source và phạm vi chỉ hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `2690D0F526B12358313AD496FF20803CE27ECDE93A0C0D3AE0DEE61CAA9EF43D`). Chưa deploy VPS.

## Thoại NPC batch 21 — staging 2026-07-13

- Đã dịch 5 thông báo Tranh Bá Liên Server và Bãi Biển, giữ nguyên mốc giờ/tag màu.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `69AE59BE609F896B10E05A753E377B08112271309DE09EFB938BB72040EB2590`). Chưa deploy VPS.

## Thoại NPC batch 22 — staging 2026-07-13

- Đã dịch 6 thoại Chuyển Sinh, Hoa Hồng và nguyên liệu cường hóa; chuẩn hóa HP, Vàng Khóa, Hồn Thạch và Đá Cường Hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `983DEB0A90F570BB8C2E3E3981C45D980E0FCFD7197B71809A31733C33624407`). Chưa deploy VPS.

## Thoại NPC batch 23 — staging 2026-07-13

- Đã dịch 5 thoại cơ chế phó bản: Quỷ Giới, giữ bóng, Hang Bí Ẩn, Thần Đăng và Boss Cuối.
- Giữ nguyên mọi điều kiện số lượng 3/4/5 và ngắt dòng source; chỉ thay nội dung hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `7E9168DA5A96979D44320E1BDCDC5437429539F266929540CB73B8A8006B59A3`). Chưa deploy VPS.

## Thoại NPC batch 24 — staging 2026-07-13

- Đã dịch 4 mô tả dài: Trí Giả, Linh Tuyền, Bãi Biển và Hẻm Núi Hoang Vu.
- Chuẩn hóa KN, CS, Trang Bị, thuốc PK và các tên nguyên liệu; giữ từng tag màu/ngắt dòng source.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `7AFDB04215E12EF894F0709957FFD6C926E8F46B1A54237C373F3B64E0A81DD5`). Chưa deploy VPS.

## Thoại NPC batch 25 — staging 2026-07-13

- Đã dịch 5 thông báo Bang Hội/Thành Chiến: Hào Quang, phe chiến đấu, Long Ảnh Đàn và Bái Sư.
- Chuẩn hóa Quỹ Bang Hội, Hào Quang, CS, 10K và cụm thuật ngữ PK; giữ nguyên tag/ngắt dòng source.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `95BB0D64694A4C180BD134DB750BE457BDC37D9162D40131B6C0C30A5A646A0A`). Chưa deploy VPS.

## Thoại NPC batch 26 — staging 2026-07-13

- Đã dịch 4 đoạn lore phó bản: Thủy Vực Long Đô, Xích Huyết Ma Cung, Địa Ngục Kết Giới và Cửu Thiên Băng Cung.
- Giữ nguyên tag màu/điều kiện 2-3 Thần Phù; thống nhất các tên Long Vương, Quỷ Giới, Ma Giới và KN.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `5FDA670C287FCA2DFB6F21F04A9EA6F1F11C8B4FA2320C7C2964F8F826948867`). Chưa deploy VPS.

## Thoại NPC batch 27 — staging 2026-07-13

- Đã dịch 4 quy tắc/sự kiện: đấu trường, Cầu Nguyện, Long Ảnh Đàn và thông điệp Huynh Đệ.
- Gate chặn `n02008` vì có route nội bộ không hiển thị rõ; entry được phục hồi source và loại khỏi batch, không sửa payload máy.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `71EEBC95291DA66A6670F89315FECE4F74F70115C4A301FC3E418F0BFEEAA203`). Chưa deploy VPS.

## Thoại NPC batch 28 — staging 2026-07-13

- Đã dịch 4 mô tả Vực Sâu Liệt Diệm và ba tầng Cửu Thiên Băng Cung.
- Giữ nguyên điều kiện 1 Thần Phù mỗi tầng, tag màu và các tên Thiên Thần/Xà Linh.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `69F1F81645AA6FE77E534DC542BAED30DEBD9D804320822E672A6A5AF65EC9D9`). Chưa deploy VPS.

## Thoại NPC batch 29 — staging 2026-07-13

- Đã dịch 4 thoại Săn Quỷ và điều kiện 10/15 Điểm vào các tầng.
- Giữ nguyên tag màu, ngưỡng điểm và cơ chế nhận điểm; chỉ thay nội dung hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `30DF9CC5FA1063D5B0D9DC66E87B50A4BFBF9C2FBAF2B73B661543DE40513AA3`). Chưa deploy VPS.

## Thoại NPC batch 30 — staging 2026-07-13

- Đã dịch 4 mô tả Tà Linh và Ải Bò; chuẩn hóa CS, KN, Điểm Thần Hồn/Chiến Hồn/Tinh Hồn, Nguyên Bảo và vật phẩm Ải Bò.
- Giữ nguyên tỷ lệ VIP 20%, các tag màu và điều kiện thu thập theo thứ tự.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `2402CE45E5FE695B5D41E2B1E2C8575D4C2ABF4CF2ADB904142EA94B8DB06F3E`). Chưa deploy VPS.

## Thoại NPC batch 31 — staging 2026-07-13

- Đã dịch 3 bước nhiệm vụ Ải Bò: vào ải, Chân Wirt và giải cứu Deckard Cain lấy Khối Lập Phương Horadric.
- `n02084` có escape bất thường nên được tách QA riêng; không thay khi chưa qua gate.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `2D6DBF3E74A7A17D824EA0E48156D2402F32F964B852A3126D5FA6AC691A472D`). Chưa deploy VPS.

## Thoại NPC batch 32 — staging 2026-07-13

- Đã dịch 3 thông báo Ma Long Dung Nham, Bái Sư và quy tắc triệu hồi Tà Linh.
- Giữ nguyên các mốc giờ, số lượng 1 Lệnh, tag màu và cơ chế ưu tiên Lệnh trước Nguyên Bảo.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `630C9653C3B5D8D588A5BE3995C56D76276F768EA3249A65EB9BAA548604BDBF`). Chưa deploy VPS.

## Thoại NPC batch 33 — staging 2026-07-13

- Đã dịch 6 chuỗi Lửa Trại/Hỏa Chủng/Nướng Thịt: cấp lửa, buff x1.5, thời gian và tỷ lệ món nướng.
- Giữ nguyên mọi placeholder `%d`, `%d%%`, tag màu và ngắt dòng source; chuẩn hóa KN, Hỏa Chủng, Nguyên Bảo.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `13A1BC78E68C1C91CDBBA2C0A53D4564E08B61F4D340F69C8FA81750F2DD23D1`). Chưa deploy VPS.

## Thoại NPC batch 34 — staging 2026-07-13

- Đã dịch 5 chuỗi Đá Thế Giới: điều kiện/chi tiết sự kiện, đăng ký, Bang đối chiến và triệu hồi Chiến Binh.
- Giữ nguyên `%d`, tab, ngắt dòng, thời gian và điều kiện chiếm giữ 15 phút; thống nhất Quỹ Bang Hội/Nguyên Bảo.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `1D24C3000B879E68AD3AAAE3F9F88799E449C579A4960D8A793073940098E958`). Chưa deploy VPS.

## Thoại NPC batch 35 — staging 2026-07-13

- Đã dịch 5 mô tả Công Thành, Mê Thành Đoạt Bảo, Siêu Hộ Vệ và Chiến Tranh Nguyên Tội.
- Giữ tag/ngắt dòng, bảng ba loại Hộ Vệ và cơ chế cướp trạng thái; thống nhất KN, CS, Nguyên Bảo, Trang Bị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `7C2F8BDB8CA04B7D3E25D12A443196709BD6E282DA4C67E58EA10BCCD4626456`). Chưa deploy VPS.

## Thoại NPC batch 36 — staging 2026-07-13

- Đã dịch 3 hướng dẫn NPC: Horadric, Đào Mỏ và Hộ Tống x2.
- Giữ nguyên rich image, tag màu, phím P, điều kiện tương tác và ngắt dòng source.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `408DF6E1D29AFDD46A7DE61A38466A1166EF4ADDA167935EFA28E1A8ACE8BA1E`). Chưa deploy VPS.

## Thoại NPC batch 37 — staging 2026-07-13

- Đã dịch lời nhắc Đấu Trường về PK và rơi đồ.
- Bảng Siêu Hộ Vệ `n02089` có escape legacy dày nên tách QA riêng; không sửa mạo hiểm.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `10497E523475D5C4934E844F2E1BD8157E76223B58DD64FB4776DDC3E44E6F0C`). Chưa deploy VPS.

## Thoại NPC batch 38 — staging 2026-07-13

- Đã dịch hướng dẫn Hộ Tống Người Đẹp, gồm phím P, cấp 35, giờ 16:30-17:00 và thưởng x2.
- Giữ nguyên toàn bộ tag màu/escape source; chuẩn hóa KN, Vàng và gợi ý mini map.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `579C8E9375FDFDAB2D1C08DC9DAA8943F8DC2EE2E278F90BC5A4760917547DD0`). Chưa deploy VPS.

## Thoại NPC batch 39 — staging 2026-07-13

- Đã dịch quy tắc Tranh Bá Thiên Hạ Đệ Nhất Liên Server: thời gian, tầng, hạ tầng, chia Nguyên Bảo và nhận thưởng.
- Giữ nguyên mọi tag màu, thời điểm 5/20 phút và mốc đóng 23:30.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `5C1B7D51D12B6EA2FC650871357CF482D30F801D59F68B50CB22F9D032860C59`). Chưa deploy VPS.

## Thoại NPC batch 40 — staging 2026-07-13

- Đã dịch 5 thông báo hôn lễ: lì xì/hoàn Nguyên Bảo, Kẹo Cưới và lời chúc toàn server.
- Giữ nguyên `%s`, `%d`, `%d%%` và cấu trúc thông báo; chuẩn hóa bạn đời, Bang Hội, Cha Xứ.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `7FAD646CFBD87EE7FCFF79DB3984A989803DD6E8AD2360946CD2B18D3F8B3607`). Chưa deploy VPS.

## Thoại NPC batch 41 — staging 2026-07-13

- Đã dịch 2 mô tả Ảo Cảnh Hồn Phách: cấp mở, lượt vào, Linh Phách Chuyển Sinh và triệu hồi Boss.
- Giữ nguyên các điều kiện CS 1/Cấp 70, CS 2 và số lần vào; chỉ thay nội dung hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `289E55A0BFEAA772E37C20793760C43EBB87CB28BA85A7A64A6E627D619026AF`). Chưa deploy VPS.

## Thoại NPC batch 42 — staging 2026-07-13

- Đã dịch 5 thông báo phó bản Thánh Đường/đội ngũ: cấp mở, Vàng Khóa, quái còn lại và tọa độ Ma Thần Boss.
- Giữ nguyên `%d`, tọa độ, tag màu, ngắt dòng và điều kiện đội 2-5 người.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `B38CD8C649838B5C96D55F66801B3C49EEEEB3258E2349BF80F05C83DACBB40C`). Chưa deploy VPS.

## Thoại NPC batch 43 — staging 2026-07-13

- Đã dịch mô tả sự kiện Ma Tộc Tiên Phong: mốc 13:00-13:30, các đợt quái và phần thưởng Trang Bị.
- Giữ nguyên tag tên quái/trang bị và cấu trúc ngắt dòng source.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `83732DA3EED755E6F74A26638E98BE6B12F2606C91E384E9B9547C5D7FE21B1B`). Chưa deploy VPS.

## Thoại NPC batch 44 — staging 2026-07-13

- Đã dịch thông báo Ma Tộc xâm lấn, đợt quái và vật liệu ghép giám định/huy chương.
- Payload tự tìm đường `<屠龙城(170,228)/M屠龙城:170:224>` được giữ nguyên và đã qua gate route.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `68E9E653F392C322BB8C91D1FE94647526912FB3386AADE50BEE6C54D47716B0`). Chưa deploy VPS.

## Thoại NPC batch 45 — staging 2026-07-13

- Đã dịch giới thiệu Kẻ Trộm Kỳ Diệu, Tiên Nữ Hầu, Chiến Sĩ Liệt Hỏa và Tứ Thần Nữ.
- Giữ nguyên tag màu/ngắt dòng, thời lượng pet 10 phút và các hiệu ứng hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `7030F292A974C05396706944DD0D679AB8C971594C36C3E9D64097A39C157EE2`). Chưa deploy VPS.

## Thoại NPC batch 46 — staging 2026-07-13

- Đã dịch 10 nhãn phó bản/Đại Sảnh Thăng Cấp: quái còn lại, tọa độ Boss, KN, Vàng Khóa, thời gian và triệu hồi.
- Giữ nguyên `%d`, `%s`, `%time%`, HTML font/tag màu và các điều kiện gameplay.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `A79C3517DDCAAD3A3D1EA9D9176CADE6B2E3A1AD5CCACA2EA72A4F4AA1D919AE`). Chưa deploy VPS.

## Thoại NPC batch 47 — staging 2026-07-13

- Đã dịch 6 lối vào Thú Hồn và Boss cá nhân: Andariel, Duriel, Azmodan, Mephisto, Baal.
- Chuẩn hóa Boss, World Boss, CS, Tọa Kỵ, Thú Hồn và dải cấp Trang Bị.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `9D860836F7764E09F54CDA6FA83C073C3F3EF7183C064630B84D8E64CA65F456`). Chưa deploy VPS.

## Thoại NPC batch 48 — staging 2026-07-13

- Đã dịch 9 nhãn Bói Vận, Mộ Thần và Đại Sảnh Thăng Cấp: Sao, KN, VIP và dải Trang Bị.
- Giữ nguyên `%d`, tag màu/tên người chơi và toàn bộ điều kiện gameplay.
- Apply staging qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `775ECDBD33A672BB81A99C31CE9396754B6D8F2DE7FA2A1036129B0D079E7D45`). Chưa deploy VPS.

## Thoại NPC batch 49 — staging 2026-07-13

- Đã dịch 3 thông báo hôn lễ/diễu hành và nhãn route `Đi tới`.
- Giữ nguyên tuyệt đối payload `/M圣城:0:0:爱神丘比特`; route gate và Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (SHA-256 `9DF0A0511DAE39D493840D1A66E3FFE7936B4A015FC8543E00D97A129770E393`). Chưa deploy VPS.

## Thoại NPC batch 50 — staging 2026-07-13

- Đã dịch 2 thông báo mở đội Mê Thành Đoạt Bảo và nhãn `Vào Đội Nhanh`.
- Giữ nguyên `%d`, `%s`, tag tên người chơi và payload `/j,%s`; route gate/Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (SHA-256 `E7E2BDAA131E2860671D61A19C144AC7C8DDB4FDFB6489E17ED25DA1835D9363`). Chưa deploy VPS.

## Thoại NPC batch 51 — staging 2026-07-13

- Đã dịch 3 chuỗi Điện Danh Dự/Đại Sảnh Thăng Cấp: Lửa Trại Danh Dự, thời gian còn lại, qua phó bản/nhận KN.
- Giữ nguyên payload mua thuốc `<#BLI004购买药品/@NPCTradeInfoToClient,5>`, `%time%`, HTML font/tag và ngắt dòng.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ NormalTalk thay đổi (SHA-256 `A6955E68489863EEED74F725D40740F61E6396B424B4B33A3ABFF2E4EC31FECD`). Chưa deploy VPS.

## Thoại NPC batch 52 — staging 2026-07-13

- Đã dịch quy tắc sự kiện 12 tầng: giờ, mốc tầng, KN, HP/MP, rơi đồ và thưởng định kỳ.
- Validator từng hiểu nhầm `HP/MP` là route `/M`; đã dùng `HP và MP` để giữ route invariant, sau đó route gate/Lua 5.1 đều qua.
- Apply staging chỉ đổi NormalTalk (SHA-256 `3F14E0D3FA10AF3B72BF132F091D7C533A24792B0D8000E9E37A2884F8F678A5`). Chưa deploy VPS.

## Thoại NPC batch 53 — staging 2026-07-13

- Hoàn tất toàn bộ 589 chuỗi có nội dung của `NormalTalk.txt`: Mảnh Sách Truyền Tống Cổ, Bí Mật Pháo Đài Thành Chiến và bảng Siêu Hộ Vệ.
- Giữ nguyên 8 cặp escape Thành Chiến, 9 cặp escape Siêu Hộ Vệ, toàn bộ tag màu và đơn vị Nguyên Bảo; chuẩn hóa KN, Vàng, Bang, Bang Chủ.
- Hai key `n02048` và `team0007` có `source` rỗng nên được giữ rỗng, không coi là chuỗi chưa dịch.
- Apply staging/validator catalog qua Lua 5.1 4/4 file (SHA-256 `87A61B928BEEBD8F3A21EB23C1DCDFD202B602E82D70BED804415C22D4490406`). Chưa deploy VPS.

## Tên NPC batch 01 — staging 2026-07-13

- Đã dịch 20 tên đầu của `EntityName.txt`: các Bang Hội Top, NPC làng/thành, tiệm Trang Bị/Trang Sức/Kho và Nhân Hoàng.
- Giữ tên riêng dễ nhận diện (Gray, Luna), chuẩn hóa chức danh như Đội Trưởng, Sứ Giả, Quản Lý và Lão Binh.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `5F65081A04B803D66845B29037358A83302D96B52BE279AAF093C5A19F08AE3C`). Chưa deploy VPS.

## Tên NPC batch 02 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC/công năng: thành viên thành trì, tiệm tạp hóa/thuốc, phó bản, doanh trại và chức danh quân đội.
- Chuẩn hóa tên riêng Osma/Jack cùng các thuật ngữ Thành Chiến, KN, Bang, Hộ Vệ, Pháp Sư.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `FD3A628F17EB24AF50C4AD6D3248D05A4A3363B0D21D51A90173234B767F22C6`). Chưa deploy VPS.

## Tên NPC batch 03 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC/hệ thống: Quan Chấp Chính, Tranh Bá, Sư Đồ, Chiến Trường, lửa trại và nhóm chức danh thành trì.
- Giữ tên riêng Mejev; chuẩn hóa các danh xưng Võ Thần, Chiến Thần, Đấu Sĩ, Ảnh Vệ và Nhân Tộc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `B1161B4B015FBB12FEF1F13962B4EEE8425F6D0547F774B46244DB3A43BDDCA5`). Chưa deploy VPS.

## Tên NPC batch 04 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC/thực thể: Thánh Đường, Pháo Đài, tầng 10-12, Bang Hội, Tinh Linh, Sứ Giả và thương nhân.
- Giữ các tên riêng Rogue, Ashe, Natalya; dùng thuật ngữ ngắn gọn theo UI game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `BF01E8AAEB0977CDD894344FE512D972E83269E8CAD35781BC48080892B8CC57`). Chưa deploy VPS.

## Tên NPC batch 05 — staging 2026-07-13

- Đã dịch thêm 20 tên thực thể: bảng xếp hạng/liên server, Ma Vực Zuma, Pháo Đài Thành Chiến, NPC hệ Ma và các bức tượng danh hiệu.
- Giữ tên riêng Elena/Luna, rút gọn cấp bậc thành Chiến Sĩ/Pháp Sư/Đạo Sĩ Số 1 để tránh tràn UI.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `F96A88757EEEFAAB3E6944C78E912FC5CA712F5A97836361CC0BBFAB42B21A21`). Chưa deploy VPS.

## Tên NPC batch 06 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC: kho Pháo Đài, Thánh Đường, Druid, Rogue, Cupid, thương nhân và các chức danh thành trì.
- Giữ tên riêng Druid/Rogue/Anya/Cupid; dùng chức danh Việt hóa ngắn để phù hợp bảng tên NPC.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `5C7266D2793F7791BD293E2EAFAA2668A81CB4155078A27C08DB72791AD190CB`). Chưa deploy VPS.

## Tên NPC batch 07 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC/sự kiện: Bang Hội, Thánh Đường, đua ngựa, Luyện Ngục, Xích Nguyệt, Ma Vực và Sa Mạc.
- Chuẩn hóa KN, Hộ Vệ, Sứ Giả, Trưởng Lão và các thuật ngữ bản đồ; giữ tên riêng Trịnh Thất Bảo/Trí Đa Tinh.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `3DAC51539ED6A08E88734952022936EB1F53EB7B683DAFCC21B06979AB2AAFD2`). Chưa deploy VPS.

## Tên NPC batch 08 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC/bản đồ: Long Đô, Ải Bò, chiến trường, hôn lễ, Trạm Dịch Chuyển và thợ mỏ.
- Giữ tên riêng Rykaf/Kashya, thống nhất các danh xưng Sứ Giả, Hộ Vệ, Thiên Sứ, Quản Lý và Chỉ Huy.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `2AD556A4CF22A97658E3C2BB58F06E93241DE369E0F05D3BCBAC258EEC087636`). Chưa deploy VPS.

## Tên NPC batch 09 — staging 2026-07-13

- Đã dịch thêm 30 tên NPC: Bang Hội, Phó Bản, Liệt Vực, Băng Cung, Thánh Đường, Sa Mạc và thương nhân.
- Chuẩn hóa tên Diablo nhận diện: Deckard Cain, Akara, Kashya, Hratli; các tầng Liệt Vực dùng dạng `Tầng N`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `85D128374FDDDB31E10C67F85F2E8FB3E105FA8F96D0271356914A2A51BE23BF`). Chưa deploy VPS.

## Tên NPC batch 10 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC: Liệt Vực, Trưởng Làng, Bái Nguyệt, Săn Ma, Cây Cầu Phúc và Sứ Giả Đổi Trang Bị.
- Chuẩn hóa tên Boss Andariel, Duriel, Azmodan, Baal, Mephisto theo cách gọi quen thuộc của game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `22F1A930F9E8506E3A65AEF98A45C586E73A3522F28C589F954A51C10F13D8F9`). Chưa deploy VPS.

## Tên NPC batch 11 — staging 2026-07-13

- Đã dịch thêm 20 tên thực thể: danh hiệu Liên Server, đá dịch chuyển, lớp nhân vật, Thánh Đường, Kurast và Pháo Đài.
- Rút gọn tên đá Pháo Đài Liên Server để giảm nguy cơ tràn UI; giữ Amazon, Mara và Kurast là tên riêng.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `6C2041807927CE92DF2047F59064A362EB22F9F3F3109CA6226518E4A744B49F`). Chưa deploy VPS.

## Tên NPC batch 12 — staging 2026-07-13

- Đã dịch thêm 20 tên NPC: Thí Luyện, Phó Bản Diệt Ma, chuồng ngựa, Đại Thiên Sứ và các NPC Diablo cổ điển.
- Chuẩn hóa Charsi, Akara, Mara, Gheed, Jamella, Drognan theo tên quốc tế quen thuộc; các tên còn lại theo phong cách Việt hóa game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `EntityName.txt` (SHA-256 `194AA5E6022B653E1BAD897329FFF84AA7F5F87B67FAAAB72E643092D592E62E`). Chưa deploy VPS.

## Nhiệm vụ batch 01 — staging 2026-07-13

- Đã dịch 22 chuỗi `Quest.txt`: mô tả Phó Bản Trang Bị Cấp 30 và lời nhắc NPC đầu tiên.
- Giữ nguyên payload tự chạy `/M王城:0:0接引灵使`, các cặp escape `\\` và chuẩn hóa `CS`, Nhẫn Tê Liệt, Lut Gholein.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `71C9329521244D752EF9C5932490BDB35AA21C539851A2E9BB12C13E01732CF1`). Chưa deploy VPS.

## Nhiệm vụ batch 02 — staging 2026-07-13

- Đã dịch 20 lời nhắc NPC về quái, nhiệm vụ, ma thần, quê hương, kỹ năng và chiến đấu.
- Giữ toàn bộ cặp escape `\\`; chuẩn hóa Quái, Hỏa Tường, Thiên Thạch Thuật và `CS` theo phong cách game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `32A012218A42DE03BD5C319E2B4FC26C3B4BBB0C11907BBDB501B37503FFEA2F`). Chưa deploy VPS.

## Nhiệm vụ batch 03 — staging 2026-07-13

- Đã dịch 20 lời nhắc NPC về chiến đấu, ác quỷ, lão binh, quê hương, ma pháp và kỹ năng.
- Giữ toàn bộ cặp escape `\\`; chuẩn hóa Đồ Long Đao, Long Văn Kiếm, Băng Cầu và tên gọi `Quái`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8FEC50FA4DEA6F853C40F2B0D8A3309FB9889F8CB39F40B482B93BEC7261A326`). Chưa deploy VPS.

## Nhiệm vụ batch 04 — staging 2026-07-13

- Đã dịch 20 lời nhắc NPC về chiến tranh, quân lực, Đá Linh Hồn, vận mệnh, nhiệm vụ và ác quỷ.
- Giữ toàn bộ cặp escape `\\`; chuẩn hóa `CS`, Quái, Chiến Sĩ, Nhẫn Tê Liệt và cách xưng hô `ta/ngươi`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7F1F7F38DBDB0E9F1E93E7550201E6401C42FBCCFA68B446B7B00DF7AFC5E279`). Chưa deploy VPS.

## Nhiệm vụ batch 05 — staging 2026-07-13

- Đã dịch 20 lời nhắc NPC về Nhiệm Vụ Săn Bắn, ác quỷ, Ẩn Trú Bí Ẩn, cảnh báo và tiến độ nhiệm vụ.
- Giữ toàn bộ cặp escape `\\`; nội dung hướng dẫn nhận nhiệm vụ vẫn chỉ vị trí bảng nhiệm vụ bên phải, không đổi cơ chế.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F82DFC3D3272B8BAE8566A1C38091CA484DEF50BF014C5707960A69F78A88A7E`). Chưa deploy VPS.

## Nhiệm vụ batch 06 — staging 2026-07-13

- Đã dịch 20 lời nhắc NPC về Huyết Điểu, Diablo, Cây Tử Vong, Thánh Đường và Nhiệm Vụ Săn Bắn.
- Giữ toàn bộ cặp escape `\\`; rút gọn hướng dẫn nhận Nhiệm Vụ Săn Bắn nhưng vẫn giữ cả hai điểm nhận: bảng bên phải và Sứ Giả Nhiệm Vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9CF8B175481564DF09DF147886DE8513B9BC629DFD58C3B4DFF8F706151EEF5E`). Chưa deploy VPS.

## Nhiệm vụ batch 07 — staging 2026-07-13

- Đã dịch 27 lời nhắc NPC về Pháo Đài Thế Giới, Thánh Thành, Nhiệm Vụ Săn Bắn, Diệt Ma và trạng thái nhiệm vụ.
- Kiểm tra lại trực tiếp các key lặp sau apply để bảo đảm đúng câu/đúng escape; toàn bộ cặp `\\` vẫn được giữ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `895D466BC5077FCD2CA96216052F1DCA518791D8D38745D8BBEA859E50E460F1`). Chưa deploy VPS.

## Nhiệm vụ batch 08 — tiêu đề đầu game, staging 2026-07-13

- Đã dịch 30 tiêu đề nhiệm vụ đầu `name0`–`name29`: Hành Trình Huyền Thoại, Long Vệ, Hang Zombie, Thánh Thành, Ma Trùng và các mục tiêu tân thủ.
- Dùng Title Case nhất quán cho tiêu đề; kiểm tra lại trực tiếp `name0`, `name10`, `name20`, `name29` sau apply.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9ECB122CB66914F728FA3874522B86B6850DC2D76F479512BB3C2B3F3E43124B`). Chưa deploy VPS.

## Nhiệm vụ batch 09 — mục tiêu đầu game, staging 2026-07-13

- Đã dịch 10 mục tiêu đầu `desc0`–`desc9`: gặp NPC, thăm dò Hang Xương Khô, diệt Ma Nhân Bù Nhìn/Chiến Sĩ Xương Khô và báo nhiệm vụ.
- Chỉ thay nhãn hiển thị trong các link NPC; toàn bộ payload `/M边界村...` và `/M骷髅洞...` được giữ nguyên.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `CC13B33E6EE1B3304F332AFBB56FD2F1F7F62B9E085680DE88A24BC9830B6842`). Chưa deploy VPS.

## Nhiệm vụ batch 10 — mục tiêu Hang Zombie/Thung Lũng, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc10`–`desc19`: Hang Zombie, Thung Lũng Rắn Độc, giao nhiệm vụ và diệt Zombie/Thú Tộc.
- Nhãn NPC được Việt hóa ngắn gọn; giữ nguyên mọi payload route `/M僵尸洞...`, `/M毒蛇山谷...` và `/M边界村...`.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `495DF5B0C43DCF58C316F7A3B43AEC452FFF7D6D2565DCCCFBD6DCA8F54257E8`). Chưa deploy VPS.

## Nhiệm vụ batch 11 — tiêu đề tuyến giữa, staging 2026-07-13

- Đã dịch 20 tiêu đề `name30`–`name49`: Thành Chiến, Rogue, Harrogath, kỹ năng, trang bị, ác quỷ và quái vật.
- Dùng Title Case nhất quán, giữ các tên riêng Charsi/Rogue/Harrogath để khớp bối cảnh game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AB1425B440CA7F63493154357773D4E4B104848B20534CC92C91C3D7CD726E38`). Chưa deploy VPS.

## Nhiệm vụ batch 12 — mục tiêu Thánh Thành/Rogue, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc20`–`desc29`: Thánh Thành, Hang Xương Khô, Hang Zombie, Thung Lũng Rắn Độc và báo NPC.
- Payload tự chạy `/M圣城...`, `/M王城...`, `/M边界村...`, `/M骷髅洞...`, `/M僵尸洞...`, `/M毒蛇山谷...` được giữ nguyên tuyệt đối.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7736866DA6FC17EB8E46BB0E95AE798BB361C81175F80C7CF7C36EB1D9A683A0`). Chưa deploy VPS.

## Nhiệm vụ batch 13 — mục tiêu Thung Lũng/Rogue, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc30`–`desc39`: thu thập Cỏ Hỏa Long, Thành Chiến, Rogue Camp và gặp Cain.
- Giữ nguyên mọi route `/M毒蛇山谷...`, `/M罗格营地...`, `/M圣城...`; chỉ đổi nhãn NPC và câu mô tả.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `40A202A8FE3C1AB9B803825F5ECB85EA22178489F4BA16D68577339FA81BE414`). Chưa deploy VPS.

## Nhiệm vụ batch 14 — mục tiêu Thánh Thành, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc40`–`desc49`: an ninh Thánh Thành, Ma Phủ Binh, Charsi, Akara, Mara và công thức thất lạc.
- Giữ nguyên mọi payload `/M圣城...`; dùng tên Diablo chuẩn Gray/Charsi/Akara/Mara trong nhãn hiển thị.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `22AAFF60BC4FF07CF083E008D39DEDD72771E64CABFF6C63BEA8938BD87192B9`). Chưa deploy VPS.

## Nhiệm vụ batch 15 — mục tiêu Thánh Thành, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc50`–`desc59`: Drognan, Gheed, kho, hôn lễ, Quân Thánh Thành, Tế Tư Osma và Chủ Mỏ.
- Giữ nguyên mọi payload `/M圣城...`; nhãn hiển thị dùng tên Diablo chuẩn và thuật ngữ ngắn gọn.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `A989CDF6916C6B7861D9DC8557DA1098C9BAC352C8D3F85A82C76468161C53E4`). Chưa deploy VPS.

## Nhiệm vụ batch 16 — mục tiêu Travincal, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc60`–`desc69`: Travincal, Ác Quỷ Khát Máu, Xác Trùng, Tế Tư Tà Ác và Giáo Chủ Zuma Ảo Ảnh.
- Route gốc `/M邪恶洞穴...` trong mục tiêu Travincal được giữ nguyên payload; các route Travincal khác cũng không thay đổi.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `41B45E215571B9C77B3BF4879D42EFA73483312486537F3BCC740675240BFF80`). Chưa deploy VPS.

## Nhiệm vụ batch 17 — mục tiêu Travincal tầng 2, staging 2026-07-13

- Đã dịch 9 mục tiêu `desc70`–`desc78`: Cỏ Cầm Máu, Rogue Anya, Xác Trùng Biến Dị, Đao Thủ Tà Ác và Thú Nhân Rìu Dài.
- Giữ nguyên mọi payload route Travincal/Ác Động tầng 2; chỉ đổi phần nhãn và mô tả hiển thị.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `330D405C9C9D6056D56CD31FCA962106F97E0B5CDC7993661DFAC7CB93835DF8`). Chưa deploy VPS.

## Nhiệm vụ batch 18 — mục tiêu Travincal tầng 2, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc79`–`desc88`: Lợn Nan Huyết, Bọ Cánh Cứng Thánh, Andariel, Giám Mục Thánh Đường, Cain và Người Dẫn.
- Giữ nguyên mọi route Travincal/Ác Động/Thánh Thành tầng 2; không sửa bản đồ, NPC ID hay tọa độ trong payload.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `FE9D89B8CFBA8678C50221CF0867D1399BD6E2529206E10275D1CB4D6B157569`). Chưa deploy VPS.

## Nhiệm vụ batch 19 — mục tiêu Đồ Long Thành/Thần Điện, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc89`–`desc98`: Thợ Săn Saya, Akara, Mara, Drognan, Chiến Binh Amazon và Thần Điện Hắc Ám.
- Payload thiếu `M` vốn có ở `desc90` được giữ nguyên nguyên văn; các route khác qua route gate/Lua bình thường.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B313B2E9840780C66A0701A0B36EEE01F6BFA28F3EAC09509338C13C42E0DDEB`). Chưa deploy VPS.

## Nhiệm vụ batch 20 — mục tiêu Thần Điện Hắc Ám, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc99`–`desc108`: Hộ Vệ Thần Điện, Long Vệ Bóng Tối, Trứng Côn Trùng, Andra và Thánh Kỵ Hắc Ám.
- Hai route có cùng nhãn Hộ Vệ Thần Điện nhưng tọa độ khác nhau được xử lý theo đúng từng key, giữ nguyên payload nguồn.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5399CFE7A624E5F6220A246A60F0607179CDD8FF54F2FA29B96E5F824DCAD383`). Chưa deploy VPS.

## Nhiệm vụ batch 21 — mục tiêu Thần Điện Hắc Ám tầng 2, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc109`–`desc118`: Xà Nhân Gorgon, Chiến Binh Man Tộc, Nghị Viên Travincal, Sát Thủ Hắc Ám và Pháp Sư Lửa.
- Giữ nguyên mọi route `/M黑暗神殿...`; mô tả chỉ thay nhãn NPC/quái theo phong cách game.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `CDDF59291761A215410F4EE0E9195D981FC3423360939A291C5B4707F6750D5B`). Chưa deploy VPS.

## Nhiệm vụ batch 22 — mục tiêu Pháo Đài Thế Giới, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc119`–`desc128`: Kỵ Sĩ Khát Máu, Pháp Sư Lửa, Drognan, Người Dẫn Pháo Đài, Tộc Trưởng Mara, Dethas.
- Giữ nguyên toàn bộ route Thần Điện Hắc Ám/Đồ Long Thành/Pháo Đài Thế Giới và các tọa độ NPC.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `824C15E8E38A0D43ED7B5B54C6B147C54C12DE11EE02976E313B3AD1F5722854`). Chưa deploy VPS.

## Nhiệm vụ batch 23 — mục tiêu Kurast, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc129`–`desc138`: Tổng Giám Mục, Dethas, Tế Tư Kurast, Hộ Vệ Kurast, Người Sói và Trầm Luân Ma.
- Giữ nguyên toàn bộ route `/M世界要塞...`; hai mục tiêu có cùng route được xác nhận cùng payload gốc.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F169CCDE9E47EA3A18F68D3CD1C65C810AA676E3F0CAF827E6C82529C82A391B`). Chưa deploy VPS.

## Vật phẩm batch 01 — trang bị khởi đầu, staging 2026-07-13

- Đã dịch 20 tên vật phẩm `n1`–`n20`: Kiếm/Giáp Sắt, set Linh Xảo, set Man Lực và Đá Mắt Mèo.
- Chuẩn hóa tên set ngắn, hậu tố `(Nam)`/`(Nữ)` và tên slot (Mũ, Đai, Ủng, Găng, Nhẫn, Dây Chuyền).
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `D68426780DA76C2EB12A2961C8CAFC6EE8E06E22F2B7A025512BCAA6E74E3E44`). Chưa deploy VPS.

## Vật phẩm batch 02 — set Toái Cốt, staging 2026-07-13

- Đã dịch 18 tên vật phẩm `n21`–`n38`: set Man Lực còn lại, Hồng Ngọc, huy chương và trọn set Toái Cốt.
- Chuẩn hóa tên slot Vòng Tay/Đai/Ủng/Mũ/Dây Chuyền, hậu tố `(Nam)`/`(Nữ)` và nhãn `(Đã Bỏ)`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `D2907ECC85CD617D69220CD2D4A2CB997FF3804BC22E3BB6F64E3E2AE1C572E2`). Chưa deploy VPS.

## Vật phẩm batch 03 — mô tả set Huy Hoàng, staging 2026-07-13

- Đã dịch Pháp Trượng Huy Hoàng và mô tả `i39`: nguồn rơi, thưởng Nhiệm Vụ Chính và nâng cấp bằng Đá Nâng Cấp Trang Bị.
- Giữ nguyên 2 cặp escape, tag màu `c0xFF00FF00`, cấp 40 và dữ liệu gameplay; đây là mẫu cho mô tả set cùng cấu trúc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `D34AC17081E25C5C8FA00D18AD7C5589ED141D7000EEB89F077EA8CC17E035A2`). Chưa deploy VPS.

## Vật phẩm batch 04 — Pháp Bào Huy Hoàng, staging 2026-07-13

- Đã dịch Pháp Bào Huy Hoàng Nam/Nữ cùng hai mô tả rơi/nâng cấp tương ứng.
- Giữ nguyên tag màu, 2 cặp escape, cấp 40 và nguồn rơi; áp dụng cùng thuật ngữ của mô tả Pháp Trượng Huy Hoàng.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `63E0892288F404D01A050E6C7380ADFD467B57DEAE2A777171702D8E1BC3ECBB`). Chưa deploy VPS.

## Vật phẩm batch 05 — phụ kiện Huy Hoàng, staging 2026-07-13

- Đã dịch Mũ, Dây Chuyền và Vòng Tay Huy Hoàng cùng ba mô tả rơi/nâng cấp tương ứng.
- Giữ nguyên tag màu, 2 cặp escape, cấp 40 và nguồn rơi để đồng nhất toàn bộ set Huy Hoàng.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `86A6D375A21C507BEDA9F687AF0047913A1CC9DDA98FE05BB36DC12482A8F10C`). Chưa deploy VPS.

## Vật phẩm batch 06 — set Huy Hoàng hoàn tất, staging 2026-07-13

- Đã dịch Đai, Ủng, Đá, Nhẫn, Huy Chương Huy Hoàng cùng năm mô tả rơi/nâng cấp.
- Hoàn tất toàn bộ phần set Huy Hoàng hiện có trong catalog, giữ nguyên tag màu, escape và điều kiện nâng cấp cấp 40.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `39E4EBA0E58C4B30AAEF683410A305B0409D3649508E485ADA11EE74ABD9C1A3`). Chưa deploy VPS.

## Vật phẩm batch 07 — set Băng Sương phần 1, staging 2026-07-13

- Đã dịch Kiếm, Giáp Nam/Nữ, Mũ, Dây Chuyền Băng Sương và năm mô tả tương ứng.
- Giữ nguyên tag màu, escape, cấp 40 và nguồn rơi; mô tả được rút gọn thành sát ý giá buốt đúng phong cách game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `E6BC255E82DDFB7304ACD783055BC6DF70B94AD7639BFF13D49DD3275B15F364`). Chưa deploy VPS.

## Vật phẩm batch 08 — set Băng Sương hoàn tất, staging 2026-07-13

- Đã dịch Vòng Tay, Đai, Ủng, Đá, Nhẫn, Huy Chương Băng Sương cùng sáu mô tả tương ứng.
- Hoàn tất set Băng Sương trong catalog, giữ nguyên tag màu, escape, nguồn rơi và điều kiện nâng cấp cấp 40.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `79F11475C094448719F48EA46DE4355ABB29430BC606AB1DA5E1798A51E4A861`). Chưa deploy VPS.

## Vật phẩm batch 09 — hợp thành Thương Lang, staging 2026-07-13

- Đã dịch Đao Thương Lang và mô tả hợp thành 3 Đao Thương Lang thành Đao Hoàng Kim.
- Giữ nguyên 5 tag cam, một cặp escape, số lượng `3` và phím tắt `x`; chỉ đổi nhãn hiển thị/hướng dẫn.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `6D5234A113803CF0C465460A698A332C886ED6A99359049CDED084A598CD0936`). Chưa deploy VPS.

## Vật phẩm batch 10 — hợp thành Thương Lang, staging 2026-07-13

- Đã dịch Giáp Nam/Nữ, Mũ, Dây Chuyền, Vòng Tay Thương Lang cùng năm mô tả hợp thành Hoàng Kim.
- Giữ nguyên 5 tag cam, số lượng `3`, một cặp escape và phím tắt `x`; chỉ thay nhãn UI/mô tả.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `9FD0948B478072CDE40355A7DCD169293EF4376CED8D15808342949C8AC03E51`). Chưa deploy VPS.

## Vật phẩm batch 11 — set Thương Lang hoàn tất, staging 2026-07-13

- Đã dịch Đai, Ủng, Đá, Nhẫn, Huy Chương Thương Lang cùng năm mô tả hợp thành Hoàng Kim.
- Hoàn tất set Thương Lang trong catalog, giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `EF1A9CF27CA6AA095AF35032AC4FB04B3FFF56DD35F8E7CB609FED2FAF9E8A1C`). Chưa deploy VPS.

## Vật phẩm batch 12 — set Tiên Phong phần 1, staging 2026-07-13

- Đã dịch Pháp Trượng, Pháp Bào Nam/Nữ, Mũ, Dây Chuyền Tiên Phong cùng năm mô tả hợp thành Đọa Lạc.
- Giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`; chỉ đổi nhãn/mô tả hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `764831FFB52EBC073B563646D4473B17A65F7B2B5FD8D9D089481F4692DC6A53`). Chưa deploy VPS.

## Vật phẩm batch 13 — set Tiên Phong phần 2, staging 2026-07-13

- Đã dịch Vòng Tay, Đai, Ủng, Đá, Nhẫn Tiên Phong cùng năm mô tả hợp thành Đọa Lạc.
- Giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`; set còn lại một Huy Chương ở lô sau.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `F20DA38B80F5D1543895284E8A0300492B12993F60C9B3F5BA70386F842AD8BC`). Chưa deploy VPS.

## Vật phẩm batch 14 — set Tiên Phong hoàn tất/Xé Rách phần 1, staging 2026-07-13

- Đã dịch Huy Chương Tiên Phong và Kiếm, Giáp Nam/Nữ, Mũ Xé Rách cùng mô tả hợp thành Đọa Lạc/Nguyền Rủa.
- Giữ nguyên các tag cam, số lượng `3`, escape và phím tắt `x`; hoàn tất set Tiên Phong trong catalog.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `19C245EF560C9D6D548A55BA2B56BE99E5DF2A859396C69C20422541AD776F6E`). Chưa deploy VPS.

## Vật phẩm batch 15 — set Xé Rách phần 2, staging 2026-07-13

- Đã dịch Dây Chuyền, Vòng Tay, Đai, Ủng, Đá Xé Rách cùng năm mô tả hợp thành Nguyền Rủa.
- Giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`; chỉ thay nhãn/mô tả hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `C21A23513E332688D81C248C8BAFF031B9DB14CB1FBD276AF748750676B6CB27`). Chưa deploy VPS.

## Vật phẩm batch 16 — set Xé Rách hoàn tất/Hoàng Kim phần 1, staging 2026-07-13

- Đã dịch Nhẫn/Huy Chương Xé Rách và Đao, Giáp Nam/Nữ Hoàng Kim cùng mô tả hợp thành Nguyền Rủa/Trác Việt.
- Chuẩn hóa tier `Trác Việt`; giữ nguyên các tag cam, số lượng `3`, escape và phím tắt `x`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `E232686F90725D176F862B81C2BFA070DCB61776CAD47626E5CF76E630840F88`). Chưa deploy VPS.

## Vật phẩm batch 17 — set Hoàng Kim phần 2, staging 2026-07-13

- Đã dịch Mũ, Dây Chuyền, Vòng Tay, Đai Hoàng Kim cùng bốn mô tả hợp thành Trác Việt.
- Dùng tier `Trác Việt` nhất quán; giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `0C02C14F2F0739869778AFE9AADA986880CE9B40DAFF00FBD9318310E396536B`). Chưa deploy VPS.

## Vật phẩm batch 18 — set Hoàng Kim hoàn tất, staging 2026-07-13

- Đã dịch Ủng, Đá, Nhẫn, Huy Chương Hoàng Kim cùng bốn mô tả hợp thành Trác Việt.
- Hoàn tất tier Hoàng Kim → Trác Việt trong catalog; giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `6AE9E7A99DDB2D9DF68CBEA2FA13976EA680F431E45D78469794159E750D9ACB`). Chưa deploy VPS.

## Vật phẩm batch 19 — set Đọa Lạc phần 1, staging 2026-07-13

- Đã dịch Pháp Trượng, Pháp Bào Nam/Nữ, Mũ Đọa Lạc cùng bốn mô tả hợp thành Khát Máu.
- Giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`; chỉ thay nhãn/mô tả hiển thị.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `E6F970980DBC4A7E9D3A8EB4A0C65D6CD448037C88EA7D1B3C43F8DDDEAFE899`). Chưa deploy VPS.

## Vật phẩm batch 20 — set Đọa Lạc hoàn tất, staging 2026-07-13

- Đã dịch Dây Chuyền, Vòng Tay, Đai, Ủng, Đá, Nhẫn, Huy Chương Đọa Lạc cùng bảy mô tả hợp thành Khát Máu.
- Hoàn tất tier Đọa Lạc → Khát Máu trong catalog; giữ nguyên 5 tag cam, số lượng `3`, escape và phím tắt `x`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Item.txt` (SHA-256 `8B95075D05D069B8B9BC8527343D7FBF923019AE69410EAC62431CEC3B58D2F9`). Chưa deploy VPS.

## Nhiệm vụ batch 24 — mục tiêu Pháo Đài Thế Giới tầng 2, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc139`–`desc148`: Huyết Ưng Baroque, Lính Gác/Quân Trưởng Pháo Đài, Ác Quỷ Bọ Cánh Cứng, Ma Xà Tử Thần và Nữ Phù Thủy Băng.
- Một câu nguồn thiếu động từ hoàn thành được làm rõ ở phần hiển thị; route, NPC ID và tọa độ `/M世界要塞...` vẫn giữ nguyên.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F9530966A9B291CAB461D7FCC03152DB5780A7CFFD6C0707750013F98CF22D60`). Chưa deploy VPS.

## Nhiệm vụ batch 25 — mục tiêu Pháo Đài Thế Giới tầng 2, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc149`–`desc158`: Linh Hồn Duriel, Tướng/Pháp Sư Nguyền Rủa, Thú Nhân Thiết Huyết và Druid Hắc Ám.
- Chuỗi nguồn `desc154` có hậu tố Nữ Phù Thủy Băng bị lặp/hỏng được rút về câu hiển thị hợp lệ; route `/M世界要塞二层...` giữ nguyên.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `43E7F7683A223E790E434D55AB067BB763AB672C7613797DDBFB1ADAA61188BC`). Chưa deploy VPS.

## Nhiệm vụ batch 26 — mục tiêu Pháo Đài/Rừng U Ám, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc159`–`desc168`: Huyết Ma Lothar, Đại Thiên Sứ, Kẻ Khải Huyền, Rừng U Ám, Hratli và Kẻ Diệt Ma.
- Hai chuỗi nguồn có route/nhãn dư ở phần sau được rút về câu hiển thị hợp lệ; route hợp lệ và tọa độ vẫn giữ nguyên.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `CFA2AA39B2F1F3669FA8A4FA075A3CC0B960BAF4E8303CAFEC8588FBBE9DA94F`). Chưa deploy VPS.

## Nhiệm vụ batch 27 — mục tiêu Rừng U Ám, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc169`–`desc178`: Linh Hồn Azmodan, Hratli, Rừng U Ám, Nữ Hoàng Rừng, Nhiệm Vụ Săn Bắn và các mốc cấp 59/70.
- Hai hậu tố dữ liệu dư trong nguồn được loại ở phần hiển thị; toàn bộ route `/M圣城...` và `/M幽暗丛林...` giữ nguyên.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `23BE80A9392C35B968B6DDDF4FFF8CB193E2DB6424197864BF3CE49946EF76FA`). Chưa deploy VPS.

## Nhiệm vụ batch 28 — mục tiêu Khu Tị Nạn/Vùng Chôn Cất, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc179`–`desc188`: Hồng Ma Đẫm Máu, Nguyên Soái Diệt Ma, Charsi, Akara, Kashya và Gargoyle Trầm Luân.
- Giữ nguyên toàn bộ route `/M幽暗丛林...`, `/M神秘避难所...`, `/M埋骨之地...` cùng NPC/tọa độ gốc.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `81FDD7E7206821F68D9561CF48960E4E096BE133A36AB424AAD5688E2FA77151`). Chưa deploy VPS.

## Nhiệm vụ batch 29 — mục tiêu Vùng Chôn Cất/Nhà Thờ Hắc Ám, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc189`–`desc198`: Gargoyle Trầm Luân, Kashya, Thủ Lĩnh Hộ Vệ và Kỵ Sĩ Thánh Đường.
- Giữ nguyên toàn bộ route `/M埋骨之地...` và `/M黑暗教堂...`; các câu lặp dùng cùng thuật ngữ hiển thị.
- Apply staging/route gate qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `58B2AADFA73CEEC1E5293D8D476ED7E2E043D976D8956A3B446E93A39B37AD13`). Chưa deploy VPS.

## Nhiệm vụ batch 30 — tiêu đề Travincal, staging 2026-07-13

- Đã dịch 20 tiêu đề `name50`–`name69`: kỹ năng, kho, tình yêu, Travincal, ác quỷ, Zuma, Dơi Khát Máu và Sức Mạnh Ánh Sáng.
- Tiêu đề dùng Title Case nhất quán, đồng bộ thuật ngữ với các `desc` đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AD1ADE7897EE1C8ADF4ED29F3BB6EE50F7C356D47F5F2CBEEE5C7CD091C2585F`). Chưa deploy VPS.

## Nhiệm vụ batch 31 — tiêu đề Travincal, staging 2026-07-13

- Đã dịch 10 tiêu đề `name70`–`name79`: thảo dược, Xác Trùng, Rogue Anya, Rìu Dài và tuyến Diệt Ma.
- Tiêu đề dùng Title Case thống nhất, đồng bộ với mục tiêu Rừng U Ám/Travincal đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `26088B95A630C5ACAD725874F576E2EE57874DA42496BE0540A332253BB48D15`). Chưa deploy VPS.

## Nhiệm vụ batch 32 — tiêu đề Thần Điện Hắc Ám, staging 2026-07-13

- Đã dịch 20 tiêu đề `name80`–`name99`: Andariel, Horadric, Thần Điện Hắc Ám, Amazon, Cổng Địa Ngục và các phong ấn.
- Tiêu đề dùng Title Case và tên Diablo quen thuộc, đồng bộ với mục tiêu/thoại đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4D18650BF394BA13E695289BDFB593BA4C1403E2A3804222251B6FE7A5B432DE`). Chưa deploy VPS.

## Nhiệm vụ batch 33 — tiêu đề Thần Điện/Man Tộc, staging 2026-07-13

- Đã dịch 20 tiêu đề `name100`–`name119`: Thần Điện Vuốt Lợi, Man Tộc, Nghị Viên Đọa Lạc, Sát Thủ Hắc Ám và Kỵ Sĩ Khát Máu.
- Tiêu đề dùng Title Case nhất quán, đồng bộ với tên NPC/quái trong các mục tiêu đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7889841EA4DEAAA6E65E4A18F578720A7563103B40A8ED9B1CEBFBBCA32D13DC`). Chưa deploy VPS.

## Nhiệm vụ batch 34 — tiêu đề Pháo Đài/Kurast, staging 2026-07-13

- Đã dịch 20 tiêu đề `name120`–`name139`: Pháo Đài Thế Giới, Linh Hồn Andariel, Phệ Hồn, Nguyền Rủa, Rừng Nhiệt Đới và Quái Thú.
- Tiêu đề dùng Title Case, đồng bộ thuật ngữ với mục tiêu Pháo Đài/Rừng U Ám đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `38D56E0816706A2C5CF7DDC3F1A074673F239063D8EC7E941B5669ADF333F426`). Chưa deploy VPS.

## Nhiệm vụ batch 35 — tiêu đề Pháo Đài tầng 2, staging 2026-07-13

- Đã dịch 20 tiêu đề `name140`–`name159`: Đọa Ma, Duriel, Diablo, Ma Thần, Phong Ấn và các sự kiện Pháo Đài tầng 2.
- Tiêu đề dùng Title Case, giữ tên Diablo/Duriel và thuật ngữ Nguyền Rủa thống nhất với các mục tiêu đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D93DE86CBAA0991BE6B0055CA220061AE5716F0997F0871A06501B8C503E5974`). Chưa deploy VPS.

## Nhiệm vụ batch 36 — tiêu đề Rừng U Ám/Khu Tị Nạn, staging 2026-07-13

- Đã dịch 20 tiêu đề `name160`–`name179`: Huyết Ma Lothar, Đại Thiên Sứ, Rừng U Ám, Linh Hồn Azmodan, Nhiệm Vụ Săn Bắn và Khu Tị Nạn.
- Tiêu đề dùng Title Case, đồng bộ các thuật ngữ route, NPC và mục tiêu đã Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E8D28236A005DB0A551F5D7181CCDB7C059EFA003DA2E1B8FF7FFA71C1AFF264`). Chưa deploy VPS.

## Nhiệm vụ batch 37 — tiêu đề Khu Tị Nạn/Nhà Thờ, staging 2026-07-13

- Đã dịch 20 tiêu đề `name180`–`name199`: Khu Tị Nạn Bí Ẩn, Vùng Chôn Cất, Huyết Điểu, Gargoyle, Nhà Thờ Hắc Ám và Ngục Thất Nhà Thờ.
- Tiêu đề dùng Title Case, khớp thuật ngữ với mục tiêu và tên quái/NPC đã Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `832347EA3DEFC390616EA02FDC0FD84DEF6710719EF8F5C848234A5F739ABE3F`). Chưa deploy VPS.

## Nhiệm vụ batch 38 — tiêu đề Thành Đồ Long/Băng Giá, staging 2026-07-13

- Đã dịch 20 tiêu đề `name200`–`name219`: Thành Đồ Long, Huyết Ma Lothar, Maya, Ngưu Quái, Pháp Sư Hắc Ám và Nữ Hoàng Băng Giá.
- Tiêu đề dùng Title Case, đồng bộ tên NPC/quái và khu vực với thoại, mục tiêu đã Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `012E38CBD9186920B809C0E3093ABBB52EC6247F542B946A32255730C01BA0C0`). Chưa deploy VPS.

## Nhiệm vụ batch 39 — tiêu đề Hải Yêu/Thành Thánh, staging 2026-07-13

- Đã dịch 20 tiêu đề `name220`–`name239`: Hải Quái, Tháp Thất Lạc, Ngưu Ma Vương, Bang Hội, Ma Vương Balok, Thành Thánh và Tiểu Giai.
- Tiêu đề dùng Title Case, đồng bộ tên NPC/quái và khu vực với các mục tiêu đã Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1518F971368C535C55C0F5611FC49F8BF0194DD1B9CC6624884A4D06B53E2AF5`). Chưa deploy VPS.

## Nhiệm vụ batch 40 — tiêu đề Sa Trùng/Pháo Đài, staging 2026-07-13

- Đã dịch 20 tiêu đề `name240`–`name259`: Vua Sa Trùng, Naga, Bát Kỳ Ma Xà, Nhà Thờ Hắc Ám, Huyết Điểu và Pháo Đài Thế Giới.
- Tiêu đề dùng Title Case, đồng bộ tên quái/khu vực với các mục tiêu đã Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E5DE140DAF6F6C7A802C7D2A2EE91DB8A76EF6CA253A5DFB1A7EDAF55A4B4637`). Chưa deploy VPS.

## Nhiệm vụ batch 41 — tiêu đề Treo Thưởng/Zuma, staging 2026-07-13

- Đã dịch 20 tiêu đề `name260`–`name279`: Treo Thưởng, Diệt Quái, Cuồng Đao, Khu Tị Nạn, Zuma và Thành Đồ Long.
- Tiêu đề dùng Title Case, giữ cách gọi khu vực, quái và mốc cấp nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AFD9E620705AF8D950F2C8950E156E72B9729C0A75DD7B55F7A4408A43DBBCCC`). Chưa deploy VPS.

## Nhiệm vụ batch 42 — tiêu đề Cao Nguyên/Liên Minh, staging 2026-07-13

- Đã dịch 20 tiêu đề `name280`–`name299`: Hồng Ma, Diệt Quái, Cao Nguyên, Ma Vương, Thiên Sứ và Liên Minh Chiến Tranh.
- Tiêu đề dùng Title Case và các mốc cấp ngắn gọn theo quy chuẩn UI.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B669C9AA3D2B903E5A90FAADB4E9384268A784859F923591AD81771306888D9B`). Chưa deploy VPS.

## Nhiệm vụ batch 43 — tiêu đề Nhà Thờ/Cao Nguyên, staging 2026-07-13

- Đã dịch 20 tiêu đề `name300`–`name319`: Khế Ước Hắc Ám, Huyết Điểu, Cao Nguyên, Vùng Chôn Cất và Rừng Hắc Ám.
- Tiêu đề dùng Title Case, đồng bộ các tên quái và khu vực đã có trong mục tiêu/thoại.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `3C621789D6F39B151609BA95B77AAE2241A98DD19CCDF6B13D2D122AF07480F9`). Chưa deploy VPS.

## Nhiệm vụ batch 44 — tiêu đề Cain/Diệt Ma, staging 2026-07-13

- Đã dịch 20 tiêu đề `name320`–`name339`: Cain, Ác Quỷ, Nhà Thờ, Vùng Chôn Cất, Rừng Hắc Ám và Diệt Ma.
- Tiêu đề dùng Title Case, giữ tên Cain khớp với các link nhiệm vụ đã Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `193D2DAEB7A888EF30A2B3931F04EAF2E9116A76EE095BF1A79E69BEC45D091B`). Chưa deploy VPS.

## Nhiệm vụ batch 45 — tiêu đề Cao Nguyên/Ác Quỷ, staging 2026-07-13

- Đã dịch 20 tiêu đề `name340`–`name359`: Cao Nguyên Khô Cằn, Thánh Dược, Ma Thần, Nhà Thờ và Cây Tử Thần.
- Tiêu đề dùng Title Case, giữ cách gọi quái/khu vực nhất quán với các batch trước.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `08E9AE51C28834F8EC9919535C46F9370DEA83E55B71FF6C281F4BB896E6CEF8`). Chưa deploy VPS.

## Nhiệm vụ batch 46 — tiêu đề Cain/Phong Ấn, staging 2026-07-13

- Đã dịch 20 tiêu đề `name360`–`name379`: Cain, Quần Ma, Rừng Hắc Ám, Nhà Thờ, Địa Ngục và Vùng Phong Ấn.
- Tiêu đề dùng Title Case, đồng bộ tên Cain và các khu vực với mục tiêu/thoại đã dịch.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `384F5CE02EAAE0F61D24E268437BD83D98935063CB22EAA279AE0B3C4112D092`). Chưa deploy VPS.

## Nhiệm vụ batch 47 — tiêu đề Hải Hoàng/Tử Linh, staging 2026-07-13

- Đã dịch 20 tiêu đề `name380`–`name399`: Cự Long, Hải Hoàng, Dạ Xoa, Long Ngạc, Vực Tử Linh và Tể Tướng.
- Tiêu đề dùng Title Case, giữ các tên riêng/quái có phong cách MMORPG Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `93896A0F03EF07DF83220FAB419762759DA4B9AA3F4DAE7895EDB5625B204C53`). Chưa deploy VPS.

## Nhiệm vụ batch 48 — tiêu đề Phó Bản KN/Đại Lục, staging 2026-07-13

- Đã dịch 20 tiêu đề `name400`–`name419`: Phó Bản KN, Cao Nguyên, Ma Động, Đại Lục, Long Thú và Đỉnh Cao Tu Luyện.
- Dùng viết tắt `KN` theo quy chuẩn hiển thị; tiêu đề giữ Title Case và thuật ngữ MMORPG thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `622E15DA2AA9A8BBC4A22105875F87B6B836F3C1A592ACB24BD494EC3777F930`). Chưa deploy VPS.

## Nhiệm vụ batch 49 — tiêu đề Hải Hoàng/Chuyển Sinh, staging 2026-07-13

- Đã dịch 20 tiêu đề `name420`–`name439`: Hải Hoàng Môn, Long Kỵ, Chuyển Sinh, Long Tử Cùng Kỳ và Hải Yêu.
- Tiêu đề dùng Title Case, giữ phong cách tên quái/NPC MMORPG Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8C6316FC82E115BD0E9A83BE3F474C69FD83EC09F7E74E0BC4F3B4A94CE26C9A`). Chưa deploy VPS.

## Nhiệm vụ batch 50 — tiêu đề Tiên Thôn/Huyền Trang, staging 2026-07-13

- Đã dịch 20 tiêu đề `name440`, `name441`, `name450`–`name467`: Thần Binh Thất Lạc, Tiên Thôn, Kiếm Tiên, Huyền Trang và Cao Lão Trang.
- Tiêu đề dùng Title Case, giữ các tên riêng/cụm danh xưng theo phong cách MMORPG Việt hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `76439FCFD172A2F014DF58C59209C46576B061E67065FDED6AEA6A608BC8CA66`). Chưa deploy VPS.

## Nhiệm vụ batch 51 — tiêu đề Tiệm/Nhiệm Vụ Chuyển Sinh, staging 2026-07-13

- Đã dịch 20 tiêu đề `name468`–`name487`: tiệm NPC, Linh Hồn Rừng, Phó Bản Sự Kiện, Chuyển Sinh, Doanh Trại và Hiền Giả Cain.
- Dùng `Lực Chiến` cho chuỗi liên quan sức mạnh và giữ tên Cain đồng bộ với link nhiệm vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E7DE4953A5D746BEB4689230A2297C5D0119B09DB6A0092585484B8AC8795C04`). Chưa deploy VPS.

## Nhiệm vụ batch 52 — tiêu đề Kashya/Akara/Pháo Đài, staging 2026-07-13

- Đã dịch 20 tiêu đề `name488`–`name507`: Thủ Lĩnh Kashya, Nữ Phù Thủy Akara, Pháo Đài Quần Ma, Sông Lửa và Hoang Dã Đá Tảng.
- Đồng bộ tên Kashya/Akara với EntityName và các link nhiệm vụ đã có; giữ Title Case nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `DEC6BAC7C63FCADDA466379DBE6181D9FE66933B6256BAD4CCF7EA1B1B4E82F2`). Chưa deploy VPS.

## Nhiệm vụ batch 53 — tiêu đề Wirt/Tháp Lãng Quên, staging 2026-07-13

- Đã dịch 20 tiêu đề `name508`–`name527`: Chân Giả Wirt, Khe Nứt Không Gian, Tháp Lãng Quên, Cửa Ải Bò và Chuột Phệ Hồn.
- Giữ tên Wirt theo thuật ngữ Diablo đã dùng trong thoại; tiêu đề theo Title Case.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E35F6EEF0A42BF0779C34F744BABD64093F68CF757CD7B9C501BB78F0E9AE65B`). Chưa deploy VPS.

## Nhiệm vụ batch 54 — tiêu đề Kurast/Doanh Trại, staging 2026-07-13

- Đã dịch 20 tiêu đề `name528`–`name547`: Kurast, Rogue Đọa Lạc, Doanh Trại, Pháo Đài Quần Ma và Lửa Địa Ngục.
- Giữ tên Kurast/Rogue theo thuật ngữ Diablo; các tiêu đề còn lại dùng Title Case.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `62E0C238BB84E6814AA1A33EEB9D854739602A0DB6AF6327A30648C0CA2F9804`). Chưa deploy VPS.

## Nhiệm vụ batch 55 — tiêu đề Hành Trình Mới/Thần Ma, staging 2026-07-13

- Đã dịch 21 tiêu đề `name548`, `name800`, `name8001`–`name8018`: Lửa Ngục, Hành Trình Mới, Thần Miếu, Cự Ma Kim Cang và Thần Ma Loạn Vũ.
- Giữ các tiêu đề ngắn, Title Case và đúng phong cách MMORPG; không có route/placeholder bị thay đổi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B1EBD1E33FD0A732C4D5D6403F381F806850047A90F9454827F85A0173C7C9DF`). Chưa deploy VPS.

## Nhiệm vụ batch 56 — tiêu đề Long Tộc/Thánh Phán, staging 2026-07-13

- Đã dịch 20 tiêu đề `name8019`, `name802`, `name8020`–`name8029`, `name803`, `name8030`, `name8031`, `name8033`, `name8034`, `name804`, `name805`, `name8050`: Long Tộc, Thánh Phán, Hải Tộc, thú cưỡi, đội và trang bị.
- Câu nhiệm vụ thao tác dùng số ngắn (`1 Lần`), còn các tiêu đề dùng Title Case thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5A761D4D9DECC1B76D1E012E14D6633B24E5A1B0F6BA8E7C6939E51B4E81D753`). Chưa deploy VPS.

## Nhiệm vụ batch 57 — tiêu đề Vạn Thú/Chiêu Hồn, staging 2026-07-13

- Đã dịch 20 tiêu đề `name8051`–`name8065`, `name807`–`name810`: Vạn Thú Phổ, Chiêu Hồn Phan, Thiên Thư, các phó bản và thao tác trang bị.
- Cấp I–V và các câu thao tác `1 Lần` được giữ gọn, dễ đọc trong UI.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `BB379E22B374534840BB820EAC304FE8913937A4F945D353B0AC17479547A3FC`). Chưa deploy VPS.

## Nhiệm vụ batch 58 — tiêu đề Du Hiệp/Hằng Ngày, staging 2026-07-13

- Đã dịch 20 tiêu đề `name8100`–`name8108`, `name811`–`name813`, `name840`, `name8416`–`name8422`: Du Hiệp, Cain, Treo Thưởng, Săn Bắn và Nhiệm Vụ Hằng Ngày.
- Danh xưng Cain và câu thao tác giữ cùng thuật ngữ với các batch nhiệm vụ trước.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F1AC43A6CBC8C990A892441EE1D60E378F316D8DFF9BFA6F9698E9DA01DC8D9C`). Chưa deploy VPS.

## Nhiệm vụ batch 59 — tiêu đề Hằng Ngày/Diệt Quái, staging 2026-07-13

- Đã dịch 20 tiêu đề `name8423`–`name8442`: Nhiệm Vụ Hằng Ngày và Diệt Quái.
- Chuỗi lặp được chuẩn hóa cùng một thuật ngữ để các danh sách nhiệm vụ hiển thị đồng nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4A456B17EEBAB48E97ED7709DA1BC1B3E9921ABCEB3FF5B09970BED3ABEF7341`). Chưa deploy VPS.

## Nhiệm vụ batch 60 — thoại ngắn Thành Thánh, staging 2026-07-13

- Đã dịch 19 câu `compTip231`, `compTip2311`–`compTip2471`: thoại hoàn thành nhiệm vụ, khích lệ, Trại Rogue, Thành Thánh và Patty.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi, không sửa route hay placeholder.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `2E44B8AA015ECB4F9B2626D4A359A6D4B754589AC25D56B22F5F1A699FE31AC4`). Chưa deploy VPS.

## Nhiệm vụ batch 61 — thoại ngắn diệt quái, staging 2026-07-13

- Đã dịch 20 câu `compTip2481`–`compTip2651`: nhắc diệt quái, khích lệ, giao nhiệm vụ và phản hồi NPC.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi; các câu thoại dùng lối xưng hô `ta/ngươi` thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `3FDF9D4BA010388729A012A0F1D929CA818B6C0B632C9CB37145326A8FF525FB`). Chưa deploy VPS.

## Nhiệm vụ batch 62 — thoại ngắn Nguyên Soái, staging 2026-07-13

- Đã dịch 20 câu `compTip2661`–`compTip2831`: nhắc tiến độ, mốc cấp 59, Đá Thế Giới, Nguyên Soái và các phản hồi NPC.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi; dùng cách gọi `Thiếu hiệp`, `ta/ngươi` nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `C035B26BB235732F51237F412A8484D7C07A3EF64B2979B1D66EF48B51AB4EE8`). Chưa deploy VPS.

## Nhiệm vụ batch 63 — thoại ngắn Du Hiệp, staging 2026-07-13

- Đã dịch 20 câu `compTip2841`–`compTip3011`: mốc cấp 61/63, phản hồi nhiệm vụ, Du Hiệp và Hoa Ăn Thịt Người.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi; dùng thuật ngữ `Diệt Quái` và `Nhiệm vụ` nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9774450E3F77A87FB7DC82195D781A2708976EF3E48413ADDE2B4FEE71FA6FF9`). Chưa deploy VPS.

## Nhiệm vụ batch 64 — thoại ngắn Thiếu Hiệp, staging 2026-07-13

- Đã dịch 20 câu `compTip3021`–`compTip3191`: phản hồi `Thiếu hiệp`, nhắc diệt quái và một câu thoại vui.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi, đảm bảo định dạng dữ liệu Lua không đổi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7462554F70FBA492E8CA8FDC86157CEBAB8C8D022DB391B05DDB210F7BD3D622`). Chưa deploy VPS.

## Nhiệm vụ batch 65 — thoại ngắn Thiếu Hiệp lặp, staging 2026-07-13

- Đã dịch 20 câu `compTip3201`–`compTip3371`: phản hồi NPC `Thiếu hiệp` và một câu thoại vui về ngoại hình.
- Chuỗi lặp được chuẩn hóa; giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `FA6FD509604F62197B47A795431C49C51830AF49D93CC7AD1B60BBE3BE08A1FE`). Chưa deploy VPS.

## Nhiệm vụ batch 66 — thoại ngắn Mỏ Khoáng, staging 2026-07-13

- Đã dịch 20 câu `compTip3381`–`compTip3551`: phản hồi `Thiếu hiệp`, kho báu Mỏ Khoáng và thoại NPC ngắn.
- Sau khi kiểm tra lại metadata `occurrence`, giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5AE3306B71A794854F4D6288A2A49A51E01F72DB09F1A60FC0CDDD549A38C93F`). Chưa deploy VPS.

## Nhiệm vụ batch 67 — thoại ngắn Tận Thế, staging 2026-07-13

- Đã dịch 20 câu `compTip3561`–`compTip3731`: phản hồi `Thiếu hiệp`, diệt quái, tên lửa và Ngày Tận Thế.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi, dùng lối xưng hô `ta/ngươi` thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `341DCAE5D02AB4E4119985E0A7EF723B4BB04BD18736DF006AB2F0030ED7754E`). Chưa deploy VPS.

## Nhiệm vụ batch 68 — thoại ngắn Hải Quốc, staging 2026-07-13

- Đã dịch 20 câu `compTip3741`–`compTip3911`: Khu Tị Nạn Bí Ẩn, Hải Quốc, phản hồi tiến độ và thoại NPC.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi; tên khu vực và cách xưng hô thống nhất với các batch trước.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B4933FC1BC21D2C579AB1F78070DAB845B5FFB472E3AE450FF85D776BA077329`). Chưa deploy VPS.

## Nhiệm vụ batch 69 — thoại ngắn Hải Quốc/Man Tộc, staging 2026-07-13

- Đã dịch 20 câu `compTip3921`–`compTip4091`, `compTip41`: Hải Quốc, Hiền Giả Hải Tộc, Man Tộc, Long Tộc, Kết Giới Địa Ngục và phó bản.
- Chuỗi KN dùng viết tắt `KN`; giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `251BF349125BFFE98C5B80976B53456F6CFA59DBD2187688037FB4D64E03BD66`). Chưa deploy VPS.

## Nhiệm vụ batch 70 — thoại ngắn Long Tộc/Hải Hoàng Môn, staging 2026-07-13

- Đã dịch 20 câu `compTip4101`–`compTip4271`, `compTip411`: Long Tộc, Tứ Thánh Linh, Hải Hoàng Môn và nhiệm vụ đặc biệt.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi, dùng lối xưng hô và tên phe phái thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4BF8050E314B615D1A0E8C0CB4B7619D38AA784C6D039F08AB68E06B476A7945`). Chưa deploy VPS.

## Nhiệm vụ batch 71 — thoại ngắn Tàn Hồn, staging 2026-07-13

- Đã dịch 20 câu `compTip4281`–`compTip4521`, `compTip431`, `compTip441`, `compTip451`: Tàn Hồn, lão tổ, mua vũ khí và phản hồi NPC.
- Rút gọn lời thoại dài nhưng vẫn giữ nghĩa; nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9C78B5085DC78C7ADB9104A240FD2DAE7382D7F7DC006E81983CEEB0ED646B56`). Chưa deploy VPS.

## Nhiệm vụ batch 72 — thoại ngắn Thương Nhân, staging 2026-07-13

- Đã dịch 20 câu `compTip4531`–`compTip471`, `compTip461`: phản hồi `Thiếu hiệp`, mua thuốc và thương nhân tạp hóa.
- Giữ nguyên cặp `\\` kết thúc từng chuỗi; câu mua/bán giữ ngắn cho UI.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9EC75656880698A7BC6F26D549B12441D60EE7210B1DCD7169BACF453ECFBE70`). Chưa deploy VPS.

## Nhiệm vụ batch 73 — thoại ngắn Linh Tuyền/Huyết Điểu, staging 2026-07-13

- Đã dịch 20 câu `compTip4711`–`compTip4891`, `compTip481`: phó bản, KN, Launcher, Linh Tuyền, Huyết Điểu và doanh trại.
- Dùng viết tắt `KN`; giữ nguyên cặp `\\` kết thúc từng chuỗi và tên NPC/quái thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F69666ED75D13EC0D662B01356B6A91FA4E0713E044CF576CC4924B119139CAE`). Chưa deploy VPS.

## Nhiệm vụ batch 74 — thoại ngắn Ác Quỷ/Đại Thiên Sứ, staging 2026-07-13

- Đã dịch 20 câu `compTip4901`–`compTip5071`, `compTip491`, `compTip501`: Ác Quỷ Trầm Luân, Đại Thiên Sứ, Kỵ Sĩ Lãng Quên và Lửa Địa Ngục.
- Lời thoại được rút gọn theo phong cách MMORPG; giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `6680D002E63E0CE0B4BAABF330B0F08B1608250EFE896D92AAE58C3E9A391560`). Chưa deploy VPS.

## Nhiệm vụ batch 75 — thoại ngắn Bò Địa Ngục/Horadric, staging 2026-07-13

- Đã dịch 20 câu `compTip5081`–`compTip5241`, `compTip51`, `compTip511`, `compTip521`: Bò Địa Ngục, Wirt, Cain, Horadric và Hội Đồng Angiris.
- Giữ thuật ngữ Diablo nhất quán và cặp `\\` kết thúc từng chuỗi không đổi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B72E2EE4AFA5A04ADA9D6D1F72290EEE0D8C08509D0D2FD77CFFC30CF3911063`). Chưa deploy VPS.

## Nhiệm vụ batch 76 — thoại ngắn Mephisto/Charsi, staging 2026-07-13

- Đã dịch 20 câu `compTip5251`–`compTip5431`, `compTip531`, `compTip541`: Mephisto, Huyết Điểu, Vùng Chôn Cất, doanh trại và Charsi.
- Một chuỗi không có hậu tố `\\` được giữ nguyên định dạng; các chuỗi khác giữ đúng cặp `\\`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8F51FB0C48CC839BA999237341CA35756251500F896DD9C86D5DC74E0C6DFFC6`). Chưa deploy VPS.

## Nhiệm vụ batch 77 — thoại ngắn Baal/Thú Công Thành, staging 2026-07-13

- Đã dịch 20 câu `compTip5441`–`compTip681`, `compTip551`, `compTip561`, `compTip61`: Lửa Luyện Ngục, Thú Công Thành, Andariel, Baal và Amazon.
- Một chuỗi không có hậu tố `\\` được giữ nguyên định dạng; các chuỗi khác giữ đúng cặp `\\`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5D1B1F7C299576F52D9BEA889F0AB8CFCE0536AC84A07B004D4B7332A1760193`). Chưa deploy VPS.

## Nhiệm vụ batch 78 — thoại ngắn Sát Thủ/Kurast, staging 2026-07-13

- Đã dịch 20 câu `compTip691`–`compTip80081`, `compTip71`, `compTip761`, `compTip771`, `compTip781`, `compTip791`: Sát Thủ, Golem Đất, Kurast, Amazon và phản hồi NPC.
- Giữ thuật ngữ Diablo/MMORPG nhất quán và cặp `\\` kết thúc từng chuỗi không đổi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `CB090A936F8BFB8498C62FEEFD7D6AF8741795EFCF262D4EE63B9793B8FB282D`). Chưa deploy VPS.

## Nhiệm vụ batch 79 — thoại ngắn Đại Tế Tư, staging 2026-07-13

- Đã dịch 20 câu `compTip80091`–`compTip80251`, `compTip801`, `compTip8011`, `compTip8021`: Đại Tế Tư Ác Quỷ Trầm Luân và phản hồi NPC.
- Chuỗi lặp được chuẩn hóa thành `Thiếu hiệp, có việc gì?`; giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `DC1750A4297F197CDEAD9753CA5AAE9C3CEC7D0596FA6847E8F09CF5093D72C8`). Chưa deploy VPS.

## Nhiệm vụ batch 80 — thoại ngắn Thiếu Hiệp lặp 2, staging 2026-07-13

- Đã dịch 20 câu `compTip80261`–`compTip80581`, `compTip8031`, `compTip8041`, `compTip8051`: phản hồi NPC `Thiếu hiệp`.
- Chuỗi lặp được chuẩn hóa, giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8A9C884D6311B906E394A92A8966EB2A815E4D30913C792F1C64C33A91331730`). Chưa deploy VPS.

## Nhiệm vụ batch 81 — thoại ngắn Thiếu Hiệp lặp 3, staging 2026-07-13

- Đã dịch 20 câu `compTip80591`–`compTip81061`, `compTip8061`, `compTip8071`, `compTip81`, `compTip8101`: phản hồi NPC `Thiếu hiệp`.
- Chuỗi lặp được chuẩn hóa, giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `80B85E66C4426F07A8B55FE3C83CC40C5BA2899CDC3D14D56118F05F62905802`). Chưa deploy VPS.

## Nhiệm vụ batch 82 — thoại ngắn Andariel/Săn Bắn, staging 2026-07-13

- Đã dịch 20 câu `compTip81071`–`compTip84251`, `compTip811`, `compTip831`, `compTip841`, `compTip84211`–`compTip84251`: Andariel, Pháp Sư Tử Linh và thoại Săn Bắn.
- Chuỗi lặp được chuẩn hóa, giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1563349252C0373C4550EE0E2DF79332449892B86D1A3DA08F1CB7FAB2926564`). Chưa deploy VPS.

## Nhiệm vụ batch 83 — thoại ngắn Săn Bắn/Ma Tộc, staging 2026-07-13

- Đã dịch 20 câu `compTip84261`–`compTip84421`, `compTip851`, `compTip861`, `compTip871`: thoại Săn Bắn, lâu la Ma Tộc và phản hồi nhiệm vụ.
- Chuỗi lặp được chuẩn hóa, giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `C4E718C73C0FD76960F9201EECA8A33D25343E199883665464A0EDC6D5E7CDF2`). Chưa deploy VPS.

## Nhiệm vụ batch 84 — thoại ngắn cuối, staging 2026-07-13

- Đã dịch 13 câu `compTip881`–`compTip991`, `compTip91`: Nhân loại, Lut Gholein, Amazon, tăng cấp và phản hồi nhiệm vụ.
- Hoàn tất toàn bộ nhóm `compTip*`; giữ nguyên cặp `\\` kết thúc từng chuỗi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `06EB3C6C37003579FD8C21BE69EFCF5F8828A7414103716535B039AE797EA41D`). Chưa deploy VPS.

## Nhiệm vụ batch 85 — mục tiêu Pháo Đài/Maya, staging 2026-07-13

- Đã dịch 12 mục tiêu `desc199`, `desc200`, `desc202`–`desc211`: quái Pháo Đài, Shaya, Lothar, Sứ Giả Maya và Herod.
- Giữ nguyên payload của toàn bộ route `/M...`; `desc201` bị loại vì nguồn đã hỏng cú pháp link, không tự sửa cấu trúc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `BC2002B17D22F6D07AD85F0A6D37F32C248B3F089E0F8DFB25F8BC8D711FB133`). Chưa deploy VPS.

## Nhiệm vụ batch 86 — mục tiêu Băng Phong/Atlantis, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc212`–`desc221`: Anna, Lucy, Sophie, Savina, Roland, Selvis và Osborne.
- Giữ nguyên payload của toàn bộ route `/M...`; chỉ Việt hóa label hiển thị và văn bản xung quanh.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1907FFDA584EA1655631CD98EAD06157706DA3AD8A7E2EBA5E471DC8541E87D4`). Chưa deploy VPS.

## Nhiệm vụ batch 87 — mục tiêu Atlantis/Tháp Thất Lạc, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc222`–`desc231`: Bahamut, Hải Quái Cung Bạc, Hải Yêu, Yoda, Roslan, Avis và Truna.
- Giữ nguyên payload của toàn bộ route `/M...`; chỉ Việt hóa label hiển thị và văn bản xung quanh.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E90A19EBA3347B5039B1C40C66A603DBC9669B0E415E1E648E2C04398FD7752B`). Chưa deploy VPS.

## Nhiệm vụ batch 88 — mục tiêu Patty/Thánh Thành, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc232`–`desc241`: Balok, Patty, Người Dẫn Đường, Osma, Shaya, Kỵ Sĩ Hoàng Gia và Lính Đánh Thuê Sa Mạc.
- Giữ nguyên payload của toàn bộ route `/M...`; chỉ Việt hóa label hiển thị và văn bản xung quanh.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `49BAC1A7ED3BAC297A4A99A7334AB6691C4EF7DCD0C266F8142D9B841FA5B580`). Chưa deploy VPS.

## Nhiệm vụ batch 89 — mục tiêu Naga/Nhà Thờ, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc242`–`desc251`: Naga, Bọ Cánh Cứng, Rogue, Bát Kỳ Ma Xà, Nhà Thờ Hắc Ám và Thú Vương Đọa Lạc.
- Không có route hay placeholder bị thay đổi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7878BAD7FA8F6CA0805C517225F2F4BB892E1EB73AE12B6034E19EA2EF0D001B`). Chưa deploy VPS.

## Nhiệm vụ batch 90 — mục tiêu Vùng Chôn Cất/Pháo Đài, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc252`–`desc261`: Huyết Điểu, Gargoyle, Quỷ Xà, Pháo Đài Thế Giới và Nguyên Soái Diệt Ma.
- Giữ nguyên payload của route `/M神秘避难所...`; không có placeholder bị thay đổi.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5CFE1BC3670C501A6BEBF2E46DCF640412FD1041F91078E686017BB1B78B1571`). Chưa deploy VPS.

## Nhiệm vụ batch 91 — mục tiêu Nguyên Soái/Cain, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc262`–`desc271`: Nguyên Soái Diệt Ma, Nguyên Soái Hàng Ma, Đốc Quân, Kashya và Cain.
- Giữ nguyên payload của toàn bộ route `/M...`; dọn dấu chấm dư ở label hiển thị nhưng không đụng route.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5CA70E69BE37A94BD403900C2DDE8183F392A13A375C7D0E23AD7B6FCB835124`). Chưa deploy VPS.

## Nhiệm vụ batch 92 — mục tiêu Baal/Sát Thủ Ác Quỷ, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc272`–`desc275`, `desc277`–`desc282`: Baal, Akara, Nguyên Soái Hàng Ma, Nguyên Soái Diệt Ma và Sát Thủ Ác Quỷ.
- Bỏ qua `desc276` do nguồn đã hỏng cú pháp hậu route; mọi payload `/M...` trong batch được giữ nguyên.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `04E98AA1B837678FAA2090AB8212A2523633122A5F73F8F2D2F9E0BCD4185851`). Chưa deploy VPS.

## Nhiệm vụ batch 93 — mục tiêu Cain/Nguyên Soái, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc283`–`desc292`: Cain và Nguyên Soái Diệt Ma.
- Giữ nguyên payload của toàn bộ route `/M...`; chuỗi lặp dùng cách gọi và động từ nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7EE23CBD32416065A546C5714D1077A51E940D7E18BA61B104089780E59B85BF`). Chưa deploy VPS.

## Nhiệm vụ batch 94 — mục tiêu Tyrael/Thiên Ma, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc293`–`desc302`: Cain, Đại Thiên Sứ Tyrael, Thân Đồ Ngạo Thiên và Ngoại Vực Thiên Ma.
- Giữ nguyên payload của toàn bộ route `/M...`; label hiển thị dùng tên Diablo đã chuẩn hóa.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `2330629E87415A66F4626067E5E2144CF9C7B4F2E9E27F9AF2C949428D08E57A`). Chưa deploy VPS.

## Nhiệm vụ batch 95 — mục tiêu Tyrael/Drognan, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc303`–`desc312`: Đại Thiên Sứ Tyrael, Nguyên Soái Diệt Ma và Drognan.
- Giữ nguyên payload của toàn bộ route `/M...`; chuỗi lặp dùng cách gọi và động từ nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D94CD05153B56D378AB039D173E42B28D02C43E71CAB61903ABF3EAE9EE5D540`). Chưa deploy VPS.

## Nhiệm vụ batch 96 — mục tiêu Drognan/Cain, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc313`–`desc322`: Drognan tại Đồ Long Thành và Cain tại Thánh Thành.
- Giữ nguyên payload của toàn bộ route `/M...`; chuỗi lặp dùng cách gọi và động từ nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9BD0B849BCD379A8A6EC431F0590B41F28151DC1757C1E58486899A0CEFEC8CB`). Chưa deploy VPS.

## Nhiệm vụ batch 97 — mục tiêu Cain/Nguyên Soái/Rogue, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc323`–`desc332`: Cain, Nguyên Soái Diệt Ma và Dũng Sĩ Rogue.
- Giữ nguyên payload của toàn bộ route `/M...`; chuỗi lặp dùng cách gọi và động từ nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D2FA8686FF19EF4D7E1D3C1B43A8034AC014331CC748E3376BB4718C984A3A39`). Chưa deploy VPS.

## Nhiệm vụ batch 98 — mục tiêu Nguyên Soái/Thuốc, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc333`–`desc342`: Nguyên Soái Diệt Ma, mốc cấp 67 và Chủ Tiệm Thuốc.
- Giữ nguyên payload của toàn bộ route `/M...`; chuỗi lặp dùng cách gọi và động từ nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `3A32311D255C946C9DC37D15BA4ADC4AFC22CE2E78876A7E22E1E532C6FE3316`). Chưa deploy VPS.

## Nhiệm vụ batch 99 — mục tiêu Tyrael/Đào Khoáng, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc343`–`desc352`: Nguyên Soái Diệt Ma, Đại Thiên Sứ Tyrael và học Đào Khoáng.
- Giữ nguyên payload của toàn bộ route `/M...`; động từ nhiệm vụ dùng thống nhất “Diệt quái rồi báo cáo”.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7FA68411E7339DDF7ADD2D06A46A44F6D8CDB3458D9C223F9E5970366ABD766C`). Chưa deploy VPS.

## Nhiệm vụ batch 100 — mục tiêu Tyrael/Cain, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc353`–`desc362`: Đại Thiên Sứ Tyrael, mốc cấp 69 và Hiền Giả Cain.
- Giữ nguyên payload của toàn bộ route `/M...`; động từ nhiệm vụ dùng thống nhất “Diệt quái rồi báo cáo”.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F75732B190747096C331BB4714F481450D4DA30EE0B4408B955137FF92E701AB`). Chưa deploy VPS.

## Nhiệm vụ batch 101 — mục tiêu Cain/Nguyên Soái, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc363`–`desc372`: Hiền Giả Cain, Nguyên Soái Diệt Ma và lời dẫn kể chuyện.
- Giữ nguyên payload của toàn bộ route `/M...`; động từ nhiệm vụ dùng thống nhất “Diệt quái rồi báo cáo”.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `FD9BAE5218AE193566EDE733B05CDD9671E208A78DDE9D5AEEFB0C7BAC7CCA62`). Chưa deploy VPS.

## Nhiệm vụ batch 102 — mục tiêu Nguyên Soái/Đại Hiền Giả, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc373`–`desc382`: Nguyên Soái Diệt Ma, Đại Hiền Giả và quái biển.
- Giữ nguyên payload của toàn bộ route `/M...`; câu hiển thị giữ ngắn để vừa khung nhiệm vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B4E2CEEAF79057A3529177FC0CDC745BD130DB175D5CC7181ADC8F63DCD1C61E`). Chưa deploy VPS.

## Nhiệm vụ batch 103 — mục tiêu Đại Hiền Giả/Hải Ngư Nhi, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc383`–`desc392`: Đại Hiền Giả, Hải Ngư Nhi, quái biển và mốc cấp 64.
- Giữ nguyên payload của toàn bộ route `/M...`; câu mô tả được rút gọn theo phong cách nhiệm vụ MMORPG.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `42120112FDF48C304537D4101243FAFA60E1C8597B9A6A15F0E8D34B108E1935`). Chưa deploy VPS.

## Nhiệm vụ batch 104 — mục tiêu Hải Ngư Nhi/Cao Địa Khô Cằn, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc393`–`desc402`: Hải Ngư Nhi, Đại Hiền Giả, Tể Tướng Rùa, mốc cấp 65 và CS 1 cấp 50.
- Giữ nguyên payload của toàn bộ route `/M...`; tên địa danh và cấp chuyển sinh dùng cách gọi thống nhất.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9D947C5FB9A0D90104072592126B4264004A782732E6EBEAECBD1056A89DBA0B`). Chưa deploy VPS.

## Nhiệm vụ batch 105 — mục tiêu Ma Động/Vương Thành, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc403`–`desc412`: Ma Động Minh Hà, Tiểu Giai, CS 1 cấp 60, Tướng Nghịch Long và Thương Nhân Tạp Hóa.
- Giữ nguyên payload của toàn bộ route `/M...`; mốc cấp và địa danh được chuẩn hoá theo phong cách game.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `0791D777CE891EB01E63E50AA8CC14A647388A040A87AADE1B71A6D379A138DA`). Chưa deploy VPS.

## Nhiệm vụ batch 106 — mục tiêu Long Quy/Hải Để, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc413`–`desc422`: Tể Tướng Rùa, Tướng Nghịch Long, Thủy Quỷ, Đệ Tử Hải Hoàng và mốc cấp 68.
- Giữ nguyên payload của toàn bộ route `/M...`; câu mô tả được rút gọn để phù hợp khung nhiệm vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E62677CAABEC7D7F0D6B7CB37A64A266D71F0147A1E627A6F30F5188F27905D1`). Chưa deploy VPS.

## Nhiệm vụ batch 107 — mục tiêu Hải Hoàng, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc423`–`desc432`: Đệ Tử Hải Hoàng, Tàn Hồn Hải Hoàng, Bạo Long và Hỏa Chủng Linh Hồn.
- Giữ nguyên payload của toàn bộ route `/M...`; tên quái và NPC được nhất quán giữa các mục tiêu.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F03D9BDCC2FA044A42FCF364C91673CF45B021344F3421DF5C382E37D6CADB49`). Chưa deploy VPS.

## Nhiệm vụ batch 108 — mục tiêu Hải Hoàng/Naga, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc433`–`desc441` và `desc450`: Cùng Kỳ, Hải Yêu Naga, Tiên Cơ và tuyến Hải Hoàng.
- Giữ nguyên payload của toàn bộ route `/M...`; các tên riêng mới được chuẩn hoá dùng lại ở batch sau.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1EFFFFB0FEBFE96C9A73BA9987E55F111935583F59EFA5D518CED3D5C65FC302`). Chưa deploy VPS.

## Nhiệm vụ batch 109 — mục tiêu Mỹ Nhân/Thủy Thôn, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc451`–`desc460`: Tiên Cơ, Triệu Phi Yến, Tây Thi, Tửu Kiếm Tiên và Vân Yên Thủy Thôn.
- Giữ nguyên payload của toàn bộ route `/M...`; tên nhân vật được phiên âm thống nhất theo phong cách tiên hiệp.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1B2CA75D42C35387F1A528F03D2B30E5DF327E17BDA5146E658B0433725E20D5`). Chưa deploy VPS.

## Nhiệm vụ batch 110 — mục tiêu Thủy Thôn/Cao Lão Trang, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc461`–`desc470`: Đường Huyền Trang, Sa Ngộ Tịnh, Cao Lão Trang và các chủ tiệm.
- Giữ nguyên payload của toàn bộ route `/M...`; tên NPC và địa danh dùng cách gọi nhất quán.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `FF9812494B0D5DAD34E02C35D920ED20B462B3E5D6FAADD6EDC0B6D78BD1A748`). Chưa deploy VPS.

## Nhiệm vụ batch 111 — mục tiêu Cao Lão Trang/Thánh Thành, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc471`–`desc480`: các chủ tiệm, Tiểu Giai, Dê Quỷ, Charsi và Hiền Giả Cain.
- Giữ nguyên payload của toàn bộ route `/M...`, kể cả route có dấu phẩy trong tên Chủ Tiệm Thuốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `24EB8CD3D33BFEB065BE466F9381FC7D09814BE1242FE316F4DA8FBD977F047E`). Chưa deploy VPS.

## Nhiệm vụ batch 112 — mục tiêu Hang Cốt Lâu/Trại Rogue, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc481`–`desc490`: Tiên Tử Linh Tuyền, Charsi, Cain, Kashya, Akara, Natalya và mốc CS cấp 70.
- Giữ nguyên payload của toàn bộ route `/M...`; các tên Diablo được dùng thống nhất với batch trước.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `DEAB4FE75E5077D7C514146445B8BD8EEED59EF9F6E3250365425FCD8235176E`). Chưa deploy VPS.

## Nhiệm vụ batch 113 — mục tiêu Pháo Đài/Sông Lửa, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc491`–`desc500`: tuyến Pháo Đài Quần Ma, Kỵ Sĩ Trưởng, Long Hành Giả và Kiếm Ma Darkin.
- Giữ nguyên payload của toàn bộ route `/M...`; tên quái/NPC được chuẩn hoá ngắn gọn cho UI nhiệm vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4BE3B3504F2B5185676510BDC2DDF948A73CF3F8C0A70BBADFA6D37831AA1E7B`). Chưa deploy VPS.

## Nhiệm vụ batch 114 — mục tiêu Sông Lửa/Hoang Dã Đá, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc501`–`desc510`: Man Vương, Mejev, Bò Hắc Ám, Akara Hoang Dã Đá và Trụ Đá Ma Pháp.
- Giữ nguyên payload của toàn bộ route `/M...`; câu mô tả ngắn gọn, nhất quán với tuyến Diablo.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AA259C8DF0184A0BE566E558D47DD30F658CC09E4208FE8FEEE38C80562EFE9B`). Chưa deploy VPS.

## Nhiệm vụ batch 115 — mục tiêu Hoang Dã Đá/Vương Tọa, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc511`–`desc520`: Vệ Binh Hoang Dã, Sát Thủ Lang Thang, Vương Tọa Hủy Diệt và các quái tinh anh.
- Giữ nguyên payload của toàn bộ route `/M...`; mô tả giữ ngắn để vừa UI nhiệm vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `92F28D8D874E1960651BBA6EB809EAC319C38A39103E1A6B7F9EA8030CDF27F6`). Chưa deploy VPS.

## Nhiệm vụ batch 116 — mục tiêu Ngũ Chỉ Sơn/Hang Tà Ác, staging 2026-07-13

- Đã dịch 10 mục tiêu `desc521`–`desc530`: Đường Huyền Trang, Druid, Rose Luna và tuyến Hang Tà Ác.
- Giữ nguyên payload của toàn bộ route `/M...`; tên NPC/quái được thống nhất với các batch trước.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F54A35019B085F2E104EBFFA14F58B4F6598DC8705F9AE923E424ACC8392AE0C`). Chưa deploy VPS.

## Nhiệm vụ batch 117 — mục tiêu Tây Hành/Đào Khoáng, staging 2026-07-13

- Đã dịch 9 mục tiêu hiển thị `desc531`–`desc534` và `desc540`–`desc544`: Bạch Tinh Tinh, Tôn Tiểu Không, Tây Hành và Đào Khoáng.
- Các key `desc535`–`desc539`, `desc545`–`desc548` chỉ là số định danh, giữ nguyên để tránh thay đổi dữ liệu nguồn.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F06249070FC223227936091B0184B20BB896DDB6930944088F26E65C71728CBA`). Chưa deploy VPS.

## Nhiệm vụ batch 118 — mục tiêu Bảng Nhiệm Vụ, staging 2026-07-13

- Đã dịch 10 chuỗi `desc800`, `desc8001`–`desc8009`: hướng dẫn cấp 55 và nội dung Bảng Nhiệm Vụ.
- Nội dung thông báo được rút gọn để tránh tràn khung, vẫn giữ nguyên toàn bộ route `/M...`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4E989C9AC55BE080A807574BDADC953398262517A46D96DEDE13605EF88CC292`). Chưa deploy VPS.

## Nhiệm vụ batch 119 — mục tiêu Bảng Nhiệm Vụ/Phục Ma Cốc, staging 2026-07-13

- Đã dịch 10 chuỗi `desc801`, `desc8010`–`desc8018`: Akara và các thông báo Bảng Nhiệm Vụ ở Phục Ma Cốc.
- Nội dung thông báo được rút gọn theo ngữ cảnh, giữ nguyên toàn bộ payload route `/M...`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D8899E324C662434058261782944B45640F2E413B3E874C86484BDADB0216ACC`). Chưa deploy VPS.

## Nhiệm vụ batch 120 — mục tiêu Bảng Nhiệm Vụ/Ma Giới, staging 2026-07-13

- Đã dịch 10 chuỗi `desc8019`, `desc802`, `desc8020`–`desc8027`: Jameela và các thông báo Bảng Nhiệm Vụ về Ma Giới.
- Nội dung được rút gọn theo khung UI; tất cả payload route `/M...` được giữ nguyên.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `879251DAACA44AB4D8630DBD713799DC9BF9D8D2BBEF8A00739A3B97D7B4044A`). Chưa deploy VPS.

## Nhiệm vụ batch 121 — mục tiêu Bảng Nhiệm Vụ/Hải Để, staging 2026-07-13

- Đã dịch 10 chuỗi `desc8028`–`desc8034`, `desc804`, `desc805`, `desc8050`: nhiệm vụ ngẫu nhiên, Hải Để U Ám, Mara và Gheed.
- Chuỗi nguồn hỏng hậu tố ở `desc8030`/`desc8034` được rút gọn phần hiển thị, không động vào route `/M...`.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `6DF0459B29E16FE369B0E1CB56B711D06D5A0E0DA62FDC60930FB0EF749F3CA9`). Chưa deploy VPS.

## Nhiệm vụ batch 122 — mục tiêu Bảng Nhiệm Vụ/Vạn Thú Phổ, staging 2026-07-13

- Đã dịch 10 chuỗi `desc8051`–`desc8059`, `desc806`: Vạn Thú Phổ, Chiêu Hồn Phan, hồi sinh quái và Jameela.
- Quy ước hiển thị được rút gọn theo UI: map cấp `40+`, mốc hồi sinh `5 phút`; route `/M...` giữ nguyên.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `01D4ADDED826A111FD5A71798DE6C4C3F4DE4110974BE43C3BC0E097AF7F9DE8`). Chưa deploy VPS.

## Nhiệm vụ batch 123 — mục tiêu Thiên Thư/Tinh Cung, staging 2026-07-13

- Đã dịch 10 chuỗi `desc8060`–`desc8065`, `desc807`–`desc810`: Thiên Thư, Tinh Cung Ma Huyễn, Thần Tài, phụ bản và Bãi Biển Nắng.
- Giữ nguyên payload của toàn bộ route `/M...`; tên tính năng, map và NPC được chuẩn hoá cho UI.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7C67A1C86E3BBCA41B443F33219821D2CCEC09FBE8EC2AEE66DA08AA8F4961A0`). Chưa deploy VPS.

## Nhiệm vụ batch 124 — mục tiêu Phục Ma Cốc/Tổ Đội, staging 2026-07-13

- Đã dịch 10 chuỗi `desc8100`–`desc8108`, `desc811`: nhiệm vụ tổ đội, Hành Chính Quan, Nhan Như Hoa và Mara.
- Giữ nguyên payload của toàn bộ route `/M...`; câu hiển thị giữ ngắn cho danh sách nhiệm vụ.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `199A418B98002D466EE4E5109F5BE94DEEC0CBB3BCCA9FABDEA6B6E4516447B4`). Chưa deploy VPS.

## Nhiệm vụ batch 125 — mục tiêu Ải Bò/Hướng Dẫn, staging 2026-07-13

- Đã dịch 10 chuỗi `desc812`, `desc813`, `desc840`, `desc8416`–`desc8422`: Ải Bò, Truy Nã, Săn Bắn, cường hóa và Hồn Thú.
- Chuẩn hoá thuật ngữ UI: `KN`, `CS`, Thú Cưỡi; câu giới thiệu được rút gọn để tránh tràn.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E4A87E6FE2636C638CA52BCA268F6815D76FD23A96C890CCC679EE0CE27F0714`). Chưa deploy VPS.

## Nhiệm vụ batch 126 — gợi ý hệ thống, staging 2026-07-13

- Đã dịch 20 chuỗi `desc8423`–`desc8442`: Phù Văn, đồng đội, gợi ý hằng ngày và kết bạn.
- Chuẩn hoá toàn bộ nhắc EXP thành `KN`; câu hiển thị ngắn để tránh tràn UI.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `BC853D220993E1672F9F22B5019294D25D9C676B0C5262C191C62970F076F937`). Chưa deploy VPS.

## Nhiệm vụ batch 127 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk01`, `compTlk1001`, `compTlk101`, `compTlk1011`–`compTlk1071`: Long Vệ, Pháo Đài Thế Giới và gợi ý tăng CS.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B17AAD54AC32D2B46FF474857F8FE3ED54EAA9178A1A2F9C7A93DCA68A72DD10`). Chưa deploy VPS.

## Nhiệm vụ batch 128 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1081`–`compTlk1151`: Nha Bì, Giáo Chủ Zuma, Nghị Viên Travincal và gợi ý CS.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `EC47CBCA702C70F33B289198B36F9A5944DD8F446382EC4BFB47D7A2C40D3299`). Chưa deploy VPS.

## Nhiệm vụ batch 129 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1161`–`compTlk1241`: Pháo Đài Thế Giới, Diablo, Andariel, ma thuật Pháp Sư và gợi ý CS.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AFD9C15D842FC1687CC2654F39AB4125C42C2A4A612CF4C2A39872E97CCC63A3`). Chưa deploy VPS.

## Nhiệm vụ batch 130 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1251`–`compTlk1331`: Linh Hồn Thạch, Ma Thần, Andariel và vật phẩm chiến đấu.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D17D93FCA13144BEFCE0578B35551E5F8BA71DD29E2E316146D5926F8AEFD4D7`). Chưa deploy VPS.

## Nhiệm vụ batch 131 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1341`–`compTlk1421`: Kurast, World Boss Diablo, Tam Long Vệ và gợi ý chiến đấu.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F6F1BD52F5A69B6B64B9AEB6ED1EFAFD0482EE138957B99C08278DCCAB04EF19`). Chưa deploy VPS.

## Nhiệm vụ batch 132 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1431`–`compTlk1511`: Linh Hồn Thạch, Ma Thần, Duriel, Azmodan và Long Vệ.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `A2585C189D81B9A27D28A8AC0CD92C31BD2CD6F7F47D03F5B08607CC741290AE`). Chưa deploy VPS.

## Nhiệm vụ batch 133 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1521`–`compTlk161`: Baal, Mephisto, Linh Hồn Thạch, đồng đội và gợi ý Boss.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `2925262C62AAC187623EE69934660D0130B18B3459E60E927E911E288F7B80A1`). Chưa deploy VPS.

## Nhiệm vụ batch 134 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1611`–`compTlk1701`: Diablo, Linh Hồn Thạch, Chuyển Sinh và gợi ý tăng cấp.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `0EE389EF85533B063E0F189474E1ECF5658B299F8D5D89655701140F53296871`). Chưa deploy VPS.

## Nhiệm vụ batch 135 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk171`, `compTlk1711`–`compTlk1791`: Chuyển Sinh, Săn Bắn, Lính Đánh Thuê và gợi ý tổ đội.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E564E5A1242B2321AA6CC602E5D9B09DE605907E6407BAE278143BED7A674F60`). Chưa deploy VPS.

## Nhiệm vụ batch 136 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1801`–`compTlk1881`: Long Vệ, Nơi Tị Nạn, Huyết Điểu và Trại Rogue.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `770607171894AE7CA91568C9AC8FAC04B4B61A9339B7E599B030A329241569A9`). Chưa deploy VPS.

## Nhiệm vụ batch 137 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1891`–`compTlk1971`: Huyết Điểu, Kashya, Nhà Thờ Hắc Ám và Săn Bắn.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `5F249598819D0039BE48E2F321DB7614DD2EFB982988E3B90F8E5F0C5CC64B97`). Chưa deploy VPS.

## Nhiệm vụ batch 138 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk1981`–`compTlk2061`: Nhà Thờ Hắc Ám, nhiệm vụ Săn Bắn, Thú Nhân và Thợ Săn Ác Ma.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `50B41C290F6D1C48935A81AAE5DD626AB7398084227558A754909E8AAD7675A3`). Chưa deploy VPS.

## Nhiệm vụ batch 139 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2071`–`compTlk2141`: Pháo Đài Thế Giới, Côn Ngô, Sứ Giả Maya và Hắc Vu Sư.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8A4A56C76DB1B04A3F64CA6B98A59E923DB3EFE51FBD2487EEC4A10245DD8060`). Chưa deploy VPS.

## Nhiệm vụ batch 140 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2151`–`compTlk2231`: Đá Maya, Ác Ngư, Tinh Linh và Quái Biển Cung Bạc.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1E06D14CACA2E83F5D27330D2231745D6B1C6D310BDD595B5414E8654C778747`). Chưa deploy VPS.

## Nhiệm vụ batch 141 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2241`–`compTlk2321`: Atlantis, Chiến Minh, Ma tộc và Kỵ Sĩ.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1F83148144F44F13CEF78D720A4C5B73C50A43C585DB23837FAF014CDF786AFB`). Chưa deploy VPS.

## Nhiệm vụ batch 142 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2331`–`compTlk2411`: Lục Địa Dũng Sĩ, Ma Bộc Luyện Ngục và Vua Sa Trùng.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `66C00CF3854EA569C63D0A9593747CA94046CE34E5737C605EC6B191BC6A5696`). Chưa deploy VPS.

## Nhiệm vụ batch 143 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2421`–`compTlk251`: Tế Tư, Nhà Thờ Hắc Ám, Xà Quái và Người Khổng Lồ Rogue.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `A5452667DCF88D1B5FDA969AEE5B9810F14F673D7E2D32300341443C0A4CB8F4`). Chưa deploy VPS.

## Nhiệm vụ batch 144 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2511`–`compTlk2601`: Huyết Điểu, Nha Bì, Pháo Đài Thế Giới và Đại Thiên Sứ.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AE7CC691050349C0A1DFD453A459A8550314D219067BBD2C31C6306D371B2576`). Chưa deploy VPS.

## Nhiệm vụ batch 145 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk261`–`compTlk2691`: đại chiến, Ma tộc và các câu phản hồi năng lực.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `6109DFDCF112F269CD5E4C4F2F194D8CEC7F6326FAF1AEE83F26BC078813B3F7`). Chưa deploy VPS.

## Nhiệm vụ batch 146 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2701`–`compTlk2781`: Linh Hồn Thạch, Baal, Nơi Tị Nạn và tín ngưỡng Ánh Sáng.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `DBB4201673F5BDA1A744EA517F97FBE720F1DDECEDB662F0B424DED455F198C7`). Chưa deploy VPS.

## Nhiệm vụ batch 147 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2791`–`compTlk2871`: phụ bản hằng ngày, Đế Quốc Long Thần, trang bị và cấp 66–68.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F7E4DFEE72721E512A50BD0D2C10CEC8B5AED48AFE4AF87FCBDFAB1ED6D1B26A`). Chưa deploy VPS.

## Nhiệm vụ batch 148 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2881`–`compTlk2961`: Hươu Ma Hóa, phản hồi chiến lực và tốc độ diệt quái.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D36557021D6BBACB20C6CE0C65C18B8ADC59A07512443986C6BCF927E2F86CD4`). Chưa deploy VPS.

## Nhiệm vụ batch 149 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk2971`–`compTlk3051`: tiền tuyến, Hoa Ăn Thịt Người, A Hoa và phản hồi chiến lực.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E893C0C8A20263872551B434D56167B6884102AD0BA566300F9C6A853C7FDC03`). Chưa deploy VPS.

## Nhiệm vụ batch 150 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3061`–`compTlk3131`: farm quái, Vàng Đại Gia, Châu Tránh Độc và gợi ý trang bị.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `338A0996C6C070CA0D0D4D6C4D1349E1768C8801834AAC91AEA9598194AF28F1`). Chưa deploy VPS.

## Nhiệm vụ batch 151 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3141`–`compTlk3221`: Châu Tránh Độc, Đạm Thủy và các phản hồi chiến lực.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `E9757A97B5FAEC67C6265466814FC62DFC6A37FE6EFF21C631120C0F0DD2351D`). Chưa deploy VPS.

## Nhiệm vụ batch 152 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3231`–`compTlk3311`: farm quái, Long Vệ, Đế Quốc Long Thần và phản hồi chiến lực.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4C8F50C8712DDD50AA85C46C83DFAEBD3E0F8A4672FAAEE8B4C50FF8A473950F`). Chưa deploy VPS.

## Nhiệm vụ batch 153 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3321`–`compTlk341`: phản hồi chiến lực, đồng đội và tình huynh đệ.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `6C75F39F6E6F4CD31830976ADCEE3D0096EE8BF87F3DDCC933F83F005D04F351`). Chưa deploy VPS.

## Nhiệm vụ batch 154 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3411`–`compTlk3501`: Quặng Đồng Đỏ, Pháp Sư Hắc Ám và các phản hồi chiến lực.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `CF064AECEC59360BA3D620DE1DA2075FBAB56634D1D10B4B5E21A8876A7E330A`). Chưa deploy VPS.

## Nhiệm vụ batch 155 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk351`–`compTlk3591`: Đại Thiên Sứ và các phản hồi đối thoại ngắn.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `85691137D4014B0D468BA51B5E730ECFED534D2104FE95D2EFE8C513BA701AEB`). Chưa deploy VPS.

## Nhiệm vụ batch 156 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3601`–`compTlk3681`: dao động linh hồn, Chuyển Sinh và các phản hồi ngắn.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `DCCED12411B3CFAB87BCE054ED93D2D377BB74B426D312C44C7E312F467F4E89`). Chưa deploy VPS.

## Nhiệm vụ batch 157 — thoại NPC Diablo, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3691`–`compTlk3771`: Trại, farm quái và phản hồi thành quả chiến đấu.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `00A6F08CF015273D348367D813FF543EE5D58BD2E13F6ED6511AA9BB8E0360EC`). Chưa deploy VPS.

## Nhiệm vụ batch 158 — thoại NPC Hải Tộc, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3781`–`compTlk3861`: Hải Tộc, Long Ngạc, Đại Thiên Sứ và Ngư Nhi.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `C24F0D7A58E35BE0BEDE40CE03E3533A8EFD5BF31A4CE84EFADFE8E75193CD16`). Chưa deploy VPS.

## Nhiệm vụ batch 159 — thoại NPC Hải Tộc, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3871`–`compTlk3951`: Hải Tộc, Dạ Xoa, Hồn Thạch và câu chuyện Ngư Nhi.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `7337B4D25DD5EEC8898CD5337BB141B1F50ECF2C2FEF4DDB3928221CF6FCA692`). Chưa deploy VPS.

## Nhiệm vụ batch 160 — thoại NPC Hải Tộc, staging 2026-07-13

- Đã dịch 10 thoại `compTlk3961`–`compTlk4041`: do thám Thần Điện, Hải Tộc phục quốc, Đại Hiền Giả và Thánh Thành.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `0AB785F96C8EA93A1BF3DE45F1C2F278DE49FA0DF97EB19E3899582790E8222A`). Chưa deploy VPS.

## Nhiệm vụ batch 161 — thoại NPC địa ngục và Long Tộc, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4051`–`compTlk4121`: Ác Ma, Ma Nhân Rơm, Địa Ngục, Long Tộc và Long Gai Lưng.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `C0E532D432DCF56C4AE89D5590083CCAAD17EBEAF613DB909634CDA8F484FB46`). Chưa deploy VPS.

## Nhiệm vụ batch 162 — thoại NPC Long Tộc, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4131`–`compTlk4211`: Long Quy, Thủy Quỷ, Long Kỵ Sĩ và việc phục quốc của Hải Tộc.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8CA0BBC48FA0D00A227D6F1A557F13D119489280601CDC77BB143EF88A4944AC`). Chưa deploy VPS.

## Nhiệm vụ batch 163 — thoại NPC Long Kỵ, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4221`–`compTlk431`: Long Xác Thối, Bạo Long, tàn hồn, Dạ Xoa và Chuyển Sinh.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B6D7BE65250411DBD25E691D3C685442F045FD1462684F190434C3EE278D61E0`). Chưa deploy VPS.

## Nhiệm vụ batch 164 — thoại NPC Hải Hoàng, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4311`–`compTlk4401`: Long Xác Thối, Lươn Điện, Cùng Kỳ, Hải Hoàng Môn và Tứ Thần Hải Tộc.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `6DDAED7C1F08ED2C6552C52F89898720FC8DC9E120E1D0A42F0F70696A68F91A`). Chưa deploy VPS.

## Nhiệm vụ batch 165 — thoại NPC Thánh Thành, staging 2026-07-13

- Đã dịch 10 thoại `compTlk441`–`compTlk4561`: Kiếm Pha Lê, cơ duyên cảnh giới mới, Trại Rogue và lời chào NPC.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `270399B44F812508EB14A8C598CC079C411262A1256A7B58C739E78ADDE17A76`). Chưa deploy VPS.

## Nhiệm vụ batch 166 — thoại NPC Thánh Thành, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4571`–`compTlk4651`: lời chào NPC lặp và công thức Bình Sinh Lực Lớn.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `ADFEBAE69861DBE2FA8F69239E12F8A9DFE09BA32DECA7302F281251723BA7D3`). Chưa deploy VPS.

## Nhiệm vụ batch 167 — thoại NPC Thánh Thành, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4661`–`compTlk4741`: lời chào NPC lặp và Hậu Duệ Anh Hùng.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `80D78581C5CEC8EC16116CCCC70058BC7D1F2907FDE9E7EE8E7193633ABA3046`). Chưa deploy VPS.

## Nhiệm vụ batch 168 — thoại NPC hướng dẫn, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4751`–`compTlk4831`: Thần Trang, Phù Văn, phó bản hoạt động, KN, Lực Chiến và CS.
- Giữ nguyên markup màu của tên hoạt động cùng hậu tố `\\` của thoại.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `74677D246FA18D6AAE00946594C279A6F7DAEF23D4565EB6E515CCDCD5A4FD17`). Chưa deploy VPS.

## Nhiệm vụ batch 169 — thoại NPC Hồn Thạch, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4841`–`compTlk4921`: Hồn Thạch, Ma Thần Hắc Ám, doanh trại và Ma Vương xâm lược.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `AFF55E5EC3B4B211E9AE79AE71D746FC1809757B13340A6488931166330C60D7`). Chưa deploy VPS.

## Nhiệm vụ batch 170 — thoại NPC Rừng Tiên Tung, staging 2026-07-13

- Đã dịch 10 thoại `compTlk4931`–`compTlk5011`: Rừng Tiên Tung, Lôi Sơn Đức, Lỗ Cao Nhân, Thú Cưỡi và Man Vương.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `877D4A7371C26FC915DC49A64213CD629D756458F0F97845916721B6C21A4CD3`). Chưa deploy VPS.

## Nhiệm vụ batch 171 — thoại NPC Ác Ma, staging 2026-07-13

- Đã dịch 10 thoại `compTlk5021`–`compTlk5101`: Đường Minh Hà, Phù Văn, Ác Ma và Chân Giả Wirt.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `77B5417CD8B9A96AA05A6DD25D0A2D1B2CCD606CF03FF8E34EA42810D97BDAE1`). Chưa deploy VPS.

## Nhiệm vụ batch 172 — thoại NPC Ải Bò Sữa, staging 2026-07-13

- Đã dịch 10 thoại `compTlk511`–`compTlk5191`: Dương Nhân Sa Ngã, Ải Bò Sữa Bí Mật, Tháp Lãng Quên và Hồn Thạch.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `73FC3C33403B190ADCA47D94B73F7CCA9A21E5F5CA59CB561E9767906C0BFD54`). Chưa deploy VPS.

## Nhiệm vụ batch 173 — thoại NPC Trại Rogue, staging 2026-07-13

- Đã dịch 10 thoại `compTlk5201`–`compTlk5281`: Trại Rogue, Huyết Điểu, Andariel và Nữ Phù Thủy Hắc Ám.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `154D1FCA4D16DDDE321C7CE3128B4BF9470EEBFDC9BEC3C25CA9DC04EC71D22A`). Chưa deploy VPS.

## Nhiệm vụ batch 174 — thoại NPC Travincal, staging 2026-07-13

- Đã dịch 10 thoại `compTlk5291`–`compTlk5371`: Mephisto, Travincal, Gheed, Hồn Thạch và lời chào NPC.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `C0F9C4F25E3C11C754992A17CBCF4819AC31EFF0B3AEEFC8D0143B76B70D11D0`). Chưa deploy VPS.

## Nhiệm vụ batch 175 — thoại NPC doanh trại, staging 2026-07-13

- Đã dịch 10 thoại `compTlk5381`–`compTlk5461`: Kashya, Charsi, Harrogath, Kiếm Pha Lê và Thú Công Thành.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `4A4A6FCBABB6FEC18AC9BC0B4DEE7DCAA16D360FFC5F2D352FC20E29CDBC3F12`). Chưa deploy VPS.

## Nhiệm vụ batch 176 — thoại NPC Hang Động Tà Ác, staging 2026-07-13

- Đã dịch 10 thoại `compTlk5471`–`compTlk611`: Andariel, Hang Động Tà Ác, Đại Tế Tư Sa Ngã và Ác Ma cấp cao.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F0B666452830206D3C2A1880B79B0D1943938BCB6707354A37E1DA595146B85F`). Chưa deploy VPS.

## Nhiệm vụ batch 177 — thoại NPC Andariel, staging 2026-07-13

- Đã dịch 10 thoại `compTlk621`–`compTlk71`: Andariel, Ác Ma cấp cao, Lực Chiến và thảo dược.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9D745311AC35344964D03C3838831DDD9FD2A09FE86D0794B85379802D9F76E0`). Chưa deploy VPS.

## Nhiệm vụ batch 178 — thoại NPC Kurast, staging 2026-07-13

- Đã dịch 10 thoại `compTlk711`–`compTlk8001`: Amazon, Boss Thế Giới, Trại Rogue, Cảng Kurast và Orc Rìu Dài.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1700702C5A5AAAEBD04E60792B98C3D10C14DBFC478E5C9F89B1E33004D9057B`). Chưa deploy VPS.

## Nhiệm vụ batch 179 — thoại NPC Ma Tộc, staging 2026-07-13

- Đã dịch 10 thoại `compTlk80011`–`compTlk801`: Nhân Tộc, Ma Tộc, Đại Tế Tư Sa Ngã và lời chào NPC.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `FE7346B4FB239CEDBF8339153BFADA127B1AA59844BC857D89031DE4839E8EEB`). Chưa deploy VPS.

## Nhiệm vụ batch 180 — thoại NPC giao lưu, staging 2026-07-13

- Đã dịch 10 thoại `compTlk80101`–`compTlk80181`: lời chào NPC và câu giao lưu bạn bè.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `A34EE80374B3644E39FD7BAD61905EE97D98CD6D2E40B152011C8B4B38CEFC3E`). Chưa deploy VPS.

## Nhiệm vụ batch 181 — thoại NPC giao lưu, staging 2026-07-13

- Đã dịch 10 thoại `compTlk80191`–`compTlk80271`: lời chào NPC và câu đánh giá sức mạnh.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `352E0063DFCF35DF2646845CD8704C5758396FD7967A44BD0BF6ACA8829EA1B0`). Chưa deploy VPS.

## Nhiệm vụ batch 182 — thoại NPC Thú Cưỡi, staging 2026-07-13

- Đã dịch 10 thoại `compTlk80281`–`compTlk8051`: Thú Cưỡi, đồng đội và lời chào NPC.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `27AC11062CD0B1C88103A659A9F5CC9E26A81C5A031B500B7DC1132783206835`). Chưa deploy VPS.

## Nhiệm vụ batch 183 — thoại NPC giao lưu, staging 2026-07-13

- Đã dịch 10 thoại `compTlk80511`–`compTlk80601`: lời chào NPC lặp.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `93AAEA35F454EB8F45FB88FBE6C1FB95358959F0F313A12290B2B71BFDB893DD`). Chưa deploy VPS.

## Nhiệm vụ batch 184 — thoại NPC chiến lợi phẩm, staging 2026-07-13

- Đã dịch 10 thoại `compTlk8061`–`compTlk81`: chiến lợi phẩm, Trang Bị, Tam Long Vệ và lời chào NPC.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `B18C8E078FAD4B6F8D93D9B8224A4962E7663FE371647C237155BA9A5D64815A`). Chưa deploy VPS.

## Nhiệm vụ batch 185 — thoại NPC phần thưởng, staging 2026-07-13

- Đã dịch 10 thoại `compTlk81001`–`compTlk81081`: phần thưởng Vàng và lời chào NPC.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `A13312BD71939664E14FA9162F8CAA245F16FC8DDA7B0978C1600E31EC257963`). Chưa deploy VPS.

## Nhiệm vụ batch 186 — thoại NPC Thánh Đường, staging 2026-07-13

- Đã dịch 10 thoại `compTlk811`–`compTlk84171`: Đại Giáo Đường, Giám Định, Đại Tế Tư Sa Ngã, KN và Ác Ma.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9E7FD94745BC339456DE4E5B35984641CD7678DF14D2240B977CE2095E78F0FA`). Chưa deploy VPS.

## Nhiệm vụ batch 187 — thoại NPC Công Kích, staging 2026-07-13

- Đã dịch 10 thoại `compTlk84181`–`compTlk84271`: Công Kích và lời khích lệ vượt quái.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D8F51E495DCE176BA1269ADF527815248E64DA575AC040A326691EDCDB059A10`). Chưa deploy VPS.

## Nhiệm vụ batch 188 — thoại NPC vượt quái, staging 2026-07-13

- Đã dịch 10 thoại `compTlk84281`–`compTlk84371`: lời khích lệ vượt quái.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `D2F16603C0471EAF25B6A3BE6FD768F8CAA04603460BD54FADD67E3BEDF65D37`). Chưa deploy VPS.

## Nhiệm vụ batch 189 — thoại NPC Thánh Thành, staging 2026-07-13

- Đã dịch 10 thoại `compTlk84381`–`compTlk891`: lời khích lệ vượt quái, Đức Giám Mục, Thánh Thành và Lực Chiến.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `1F98FEA743C1F671403D95492EE2A7973AD9F69712D3A2FA12097326949F91A6`). Chưa deploy VPS.

## Nhiệm vụ batch 190 — hoàn tất thoại `compTlk`, staging 2026-07-13

- Đã dịch 11 thoại `compTlk901`–`compTlk991`: Thần Điện Hắc Ám, Lỗ Cao Nhân, ba Đại Ma Thần và Diablo.
- Hoàn tất toàn bộ 641/641 thoại `compTlk`; tiếp theo dịch nhóm `promTlk` của nhiệm vụ.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `F8E44718099D6E10385F15BE5B97265746A84C3ADEBC37439189CC095F0FBF82`). Chưa deploy VPS.

## Nhiệm vụ batch 191 — nhắc nhiệm vụ Thần Điện, staging 2026-07-13

- Đã dịch 10 thoại `promTlk01`–`promTlk1071`: Thần Điện Hắc Ám, Horadric, Hang Cương Thi, Thần Nhẫn và Pháo Đài Thế Giới.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9B2B2D8B1D5B833D060C0BE419D2EF5B87E45E825EB619CA19D77A86F753A874`). Chưa deploy VPS.

## Nhiệm vụ batch 192 — nhắc nhiệm vụ Harrogath, staging 2026-07-13

- Đã dịch 10 thoại `promTlk1081`–`promTlk1151`: Harrogath, Travincal, Nhiệm Vụ Săn, Sát Thủ Hắc Ám và Ogre Khát Máu.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `9D109459B8B440A44462B2A100FD907396F9897E7C7F6D3E1E215961121AB1BF`). Chưa deploy VPS.

## Nhiệm vụ batch 193 — nhắc nhiệm vụ Pháo Đài Thế Giới, staging 2026-07-13

- Đã dịch 10 thoại `promTlk1161`–`promTlk1241`: Pháo Đài Thế Giới, Harrogath, Andariel, Malah và Cổng Địa Ngục.
- Giữ nguyên hậu tố `\\` của thoại để không làm thay đổi phân tách câu gốc.
- Apply staging qua Lua 5.1 4/4 file; chỉ đổi `Quest.txt` (SHA-256 `8984892B8B4F8B16257D31F6212E5F76CE41049D53F7F24BE053B075EFAA47D3`). Chưa deploy VPS.
