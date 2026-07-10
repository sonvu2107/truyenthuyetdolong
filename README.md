# AHTL web deploy

Gói này chỉ chứa các tài nguyên công khai cần cập nhật cho game client:

- `assets/GameFrame.swf`
- `assets/ClientLang.txt`
- `assets/lang/zh-cn/clientlang.cbp`
- `assets/lang/zh-cn/cbp.zip`
- `assets/client_login.php`, `assets/client_shell.html` và `assets/client_frame.png`
- `assets/game/GameConfig.php` để bật gói CBP tổng và đổi phiên bản cache tài nguyên

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

Phiên bản `20260710langcore1` giữ nền login, kích thước game, 733 chuỗi kỹ năng và bản vá chống tự chạy nhầm cổng cấp 25. Bản này sửa cấu trúc `ClientLang.txt`, đối chiếu đủ 3.069 mục với file Trung gốc, rồi biên dịch 2.868 phép gán giao diện tiếng Việt vào lớp `lang.ZH_CN` của `GameFrame.swf`. Chuỗi `Chưa kích hoạt` nằm ngoài lớp ngôn ngữ cũng được vá theo đúng lớp `model.hlp.SkillHlp`. Sau khi nhập, cả ba lớp `lang.ZH_CN`, `SkillHlp` và `LocalPlayer` đều được xuất ngược từ SWF để xác minh.

## Biên dịch CBP an toàn

`tools/cbp_localizer.py` chỉ thay node chuỗi, tính lại độ dài UTF-8 và header CBP, đồng thời kiểm câu gốc trước khi ghi. Catalog kỹ năng hiện tại nằm tại `translations/skillconfig.vi.json`; không dùng lại cách giải nén toàn bộ payload thành văn bản rồi thay chuỗi.

`tools/swf_lang_localizer.py` đọc `ClientLang.txt`, kiểm hình dạng mảng với file Trung gốc và chỉ ghép theo đúng tên biến/chỉ số. `tools/swf_source_patcher.py` dành cho số ít chuỗi hard-code ngoài `lang.ZH_CN`, luôn kiểm đúng file và số lần xuất hiện trước khi thay.

Lệnh `patch-bool-zip` sửa boolean có kiểm tra giá trị gốc. Bản hiện tại dùng lệnh này cho `stdquest.cbp:1.autoRun`, đồng thời xác nhận node `1.id` là nhiệm vụ 485 trước khi đóng gói.

Patch nguồn của phần nhận diện cùng map nằm tại `patches/GameFrame-LocalPlayer-same-scene-id.patch`. File `GameFrame.swf` được xuất lại lớp `Logic.Actors.ActorClass.LocalPlayer` để xác minh điều kiện `scenceid == GameMap.defaultMap.mapId` đã được biên dịch vào SWF.
