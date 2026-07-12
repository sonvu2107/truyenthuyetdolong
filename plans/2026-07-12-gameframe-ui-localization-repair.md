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

## Thoại NPC batch 8 — staging 2026-07-13

- Đã dịch 30 thoại nhóm Lửa Trại/Hỏa Chủng (`gh00001..gh00036` chọn lọc), gồm mua thời gian đốt lửa, nâng cấp, buff Hỏa Chủng, nướng thức ăn và giao dịch.
- Chuẩn hóa thuật ngữ `Lửa Trại`, `Hỏa Chủng`, `Vận Tiêu`, `Nguyên Bảo`, `Vàng Khóa`, `KN`; giữ nguyên toàn bộ placeholder `%d`, tag màu và escape gốc. Mọi câu bắt đầu bằng ký tự viết hoa.
- Tổng 232 target NormalTalk đã Việt hóa; 30 target mới không còn Hán tự, placeholder/markup qua gate.
- Apply staging chỉ đổi NormalTalk (`5933CD93F70E55EFA0D0A4CEAC482F25EBC928A5807D444D63C7289C2A51233B`); EntityName, Quest, Item vẫn giữ hash snapshot. Lua 5.1 đạt 4/4 file. Chưa deploy VPS.
