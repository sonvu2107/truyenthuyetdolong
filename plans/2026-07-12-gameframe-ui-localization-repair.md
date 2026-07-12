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
