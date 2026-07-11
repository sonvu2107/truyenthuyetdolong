# AHTL web deploy

Gói này chỉ chứa các tài nguyên công khai cần cập nhật cho game client:

- `assets/GameFrame.swf`
- `assets/ClientLang.txt`
- `assets/lang/zh-cn/clientlang.cbp`
- `assets/lang/zh-cn/cbp.zip`
- `assets/client_login.php`, `assets/client_shell.html` và `assets/client_frame.png`
- `assets/game/GameConfig.php` để bật gói CBP tổng và đổi phiên bản cache tài nguyên
- `assets/game/djrm.php` để nhúng Flash ở chế độ windowless, không che nút HTML

Không đưa `wwwroot` nguyên trạng lên Git. Các file đó chứa thông tin kết nối database và khóa đăng nhập.

## Cập nhật từ máy có Git

```powershell
cd C:\GPHANTL
git clone https://github.com/sonvu2107/truyenthuyetdolong.git ahtl-web-deploy
```

## Đồng bộ trực tiếp trên Windows Server 2012

```powershell
certutil.exe -urlcache -split -f https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/main/scripts/Sync-FromGitHub-20260710c.ps1 C:\GPHANTL\Sync-FromGitHub.ps1
powershell.exe -ExecutionPolicy Bypass -File C:\GPHANTL\Sync-FromGitHub.ps1
```

Script kiểm SHA-256, sao lưu các file bị thay vào `wwwroot\_deploy_backups`, chép asset mới và chỉ thay dòng `GAMEAPPURL` trong `game\SPDef.php`; không chép đè khóa đăng nhập hoặc cấu hình database. Cách này không cần cài Git trên VPS cũ.

Phiên bản `20260711routefix2` giữ nền login, chế độ phóng to gameplay, 733 chuỗi kỹ năng, 5.285 chuỗi vật phẩm và 405 chuỗi nhiệm vụ hiển thị. Bản này khôi phục 288 khóa scene/NPC cùng payload của 106 nội dung có liên kết `/M`, đồng thời đồng bộ riêng nhiệm vụ 494 và 35 với chuỗi hiện tại của LogicServer: Lính Gác Rogue → Đại Thiên Sứ Tyrael → Lính Đánh Thuê Rogue. Guard vẫn chặn việc dịch nhầm khóa định tuyến ở các lần build sau; sửa lệch phiên bản máy chủ phải đi qua catalog `server-parity-datafix` riêng. `game/djrm.php` cũng được đồng bộ để Flash chạy `wmode=opaque` đúng dạng param, không phủ nút toàn màn hình của shell.

Nút toàn màn hình trong shell gọi `window.external.ToggleFullscreen()` khi chạy bằng `launcher/AHTL_Launcher_Fixed.exe`. Launcher .NET Framework x86 này giữ tương thích Flash ActiveX 32-bit, chuyển cửa sổ native sang `FormBorderStyle.None + Maximized`, hỗ trợ F11/Esc và khôi phục đúng kích thước cũ. Build lại bằng `powershell -ExecutionPolicy Bypass -File launcher/Build-Launcher.ps1`.

Phiên bản `20260711uifit1` chỉnh riêng bảng thưởng đăng nhập: dùng Arial 14 cho phần tiếng Việt, chèn `<br>` ở mô tả thưởng tuần và rút gọn các tab/tên hàng. Hệ thống label của game render chữ thành bitmap từ một `TextField` đã bật `multiline`; vì vậy xuống dòng có chủ đích bằng `<br>` an toàn hơn việc ép `wordWrap` hoặc đổi font toàn cục. Các thay đổi tái lập nằm trong `translations/gameframe-ui-fit-overrides.json`.

Phiên bản `20260711short1` áp lô rút gọn UI đầu tiên gồm 68 khóa nút/action/caption có độ tin cậy cao. Catalog nguồn nằm tại `translations/gameframe-ui-short-overrides.json`; công cụ `tools/apply_swf_ui_overrides.py` kiểm đúng giá trị hiện tại theo khóa trước khi ghi. Báo cáo độ dài toàn bộ UI nằm tại `translations/gameframe-ui-length-audit.json`. Bản này cũng chặn nhãn số ngày còn thiếu hiển thị `0` hoặc số âm trong hai lớp LandingReward.

Shell hiện tại giữ Flash ở chiều cao logic 750 px, tự tính chiều rộng theo tỷ lệ cửa sổ rồi phóng đồng đều và căn giữa. Nhờ vậy gameplay lấp đầy cửa sổ ở các tỷ lệ phổ biến, toàn bộ UI được phóng cùng nhau, trong khi Flash không phải render trực tiếp vùng 1920×1080 gây giảm khung hình.

## Biên dịch CBP an toàn

`tools/cbp_localizer.py` chỉ thay node chuỗi, tính lại độ dài UTF-8 và header CBP, đồng thời kiểm câu gốc trước khi ghi. Catalog kỹ năng hiện tại nằm tại `translations/skillconfig.vi.json`; không dùng lại cách giải nén toàn bộ payload thành văn bản rồi thay chuỗi.

`tools/swf_lang_localizer.py` đọc `ClientLang.txt` cùng các catalog bổ sung, kiểm hình dạng mảng và chỉ ghép theo đúng tên biến/chỉ số. `tools/translate_gameframe_hardcoded.py` lập catalog cho chuỗi nằm ngoài `lang.ZH_CN`; hai script audit kiểm placeholder, HTML/route kỹ thuật, chuỗi còn Hán tự và đối chiếu lại bytecode đã biên dịch. Ba lớp không thể tái biên dịch ổn định được ghi rõ trong `translations/gameframe-hardcoded-compile-exclusions.json` và giữ nguyên bytecode gốc.

Lệnh `patch-bool-zip` sửa boolean có kiểm tra giá trị gốc. Bản hiện tại dùng lệnh này cho `stdquest.cbp:1.autoRun`, đồng thời xác nhận node `1.id` là nhiệm vụ 485 trước khi đóng gói.

Lệnh `apply-datafix-zip` chỉ nhận catalog có `purpose=server-parity-datafix`; nó kiểm tra giá trị gốc của từng node string/number/boolean trước khi sửa. Bản vá nhiệm vụ hiện tại nằm tại `translations/stdquest.server-parity.datafix.json`, tách biệt khỏi catalog dịch để không vô hiệu hóa guard khóa scene/NPC.

Patch nguồn của phần nhận diện cùng map nằm tại `patches/GameFrame-LocalPlayer-same-scene-id.patch`. File `GameFrame.swf` được xuất lại lớp `Logic.Actors.ActorClass.LocalPlayer` để xác minh điều kiện `scenceid == GameMap.defaultMap.mapId` đã được biên dịch vào SWF.
