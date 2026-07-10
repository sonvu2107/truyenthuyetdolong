# AHTL web deploy

Gói này chỉ chứa các tài nguyên công khai cần cập nhật cho game client:

- `assets/GameFrame.swf`
- `assets/ClientLang.txt`
- `assets/lang/zh-cn/clientlang.cbp`
- `assets/lang/zh-cn/cbp.zip`

Không đưa `wwwroot` nguyên trạng lên Git. Các file đó chứa thông tin kết nối database và khóa đăng nhập.

## Cập nhật từ máy có Git

```powershell
cd C:\GPHANTL
git clone https://github.com/sonvu2107/truyenthuyetdolong.git ahtl-web-deploy
```

## Đồng bộ trực tiếp trên Windows Server 2012

```powershell
certutil.exe -urlcache -split -f https://raw.githubusercontent.com/sonvu2107/truyenthuyetdolong/main/scripts/Sync-FromGitHub.ps1 C:\GPHANTL\Sync-FromGitHub.ps1
powershell.exe -ExecutionPolicy Bypass -File C:\GPHANTL\Sync-FromGitHub.ps1
```

Script kiểm SHA-256, sao lưu các file bị thay vào `wwwroot\_deploy_backups`, chép asset mới và chỉ thay dòng `GAMEAPPURL` trong `game\SPDef.php`; không chép đè khóa đăng nhập hoặc cấu hình database. Cách này không cần cài Git trên VPS cũ. Manifest hiện tại giữ `20260710stable1`, là GameFrame đã xác nhận chạy ổn.
