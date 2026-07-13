# Kinh nghiệm vá bytecode GameFrame

## Sự cố ngày 14/07/2026

Bản vá Phúc Lợi thay đúng 7 method body nhưng sau đó khôi phục metadata từ bản gốc. Body mới do FFDec biên dịch cần nhiều local register và stack hơn, còn `max_regs`, `max_stack`, scope depth và cờ activation lại thuộc body cũ. Kết quả là SWF vẫn đóng gói được nhưng không hợp lệ với Flash ActiveX 11.4.

Biểu hiện thực tế:

- Client đăng nhập được nhưng đơ hoặc crash khi vào map.
- Windows Event Viewer báo `0xc0000005` tại `Flash32_11_4_402_265.ocx`.
- Server vẫn tải và lưu nhân vật bình thường, sau đó chỉ thấy client tự đóng kết nối.
- Lỗi rõ nhất: `LandingRewardCell1.data/set` khai báo `localcount = 4` nhưng truy cập `setlocal 6`.

## Nguyên nhân gốc

Không được ghép `codeBytes` mới với header MethodBody cũ. Các trường sau là một phần của cùng hợp đồng bytecode và phải đi cùng body đã biên dịch:

- `max_regs` / `localcount`
- `max_stack`
- `init_scope_depth`
- `max_scope_depth`
- `NEED_ACTIVATION`
- activation traits
- exception table

Việc kiểm tra “số method body không đổi” và “chỉ đúng các body mục tiêu thay đổi” là cần thiết nhưng chưa đủ để chứng minh SWF chạy được.

## Quy tắc bắt buộc cho các bản vá sau

1. Không khôi phục metadata MethodBody từ bản gốc sau khi FFDec đã biên dịch body mới.
2. Nếu chỉ ghép `codeBytes`, phải ghép đồng thời toàn bộ giới hạn register, stack, scope, exception và activation tương ứng.
3. Với mỗi method đã sửa, bắt buộc kiểm tra `max_local_index < localcount`.
4. Method có cờ `NEED_ACTIVATION` phải thực sự dùng `newactivation`; nếu body chuyển sang local register thì phải bỏ cờ và activation traits cũ.
5. So sánh P-code giữa bản gốc, bản compiler sinh ra và bản release cuối cùng; không chỉ so sánh source ActionScript đã decompile.
6. Chạy kiểm tra trên đúng Flash ActiveX 11.4 trước khi deploy, vì FFDec có thể xuất SWF thành công dù AVM2 metadata không hợp lệ.
7. Luôn giữ bản backup web và dùng cache version mới khi deploy.

## Checklist trước deploy

- [ ] Số MethodBody trước và sau bằng nhau.
- [ ] Danh sách body thay đổi đúng phạm vi yêu cầu.
- [ ] Mọi local register nằm trong `0 .. localcount - 1`.
- [ ] `max_stack` lấy từ body compiler sinh ra, không lấy từ bản cũ.
- [ ] Scope depth khớp body compiler sinh ra.
- [ ] Cờ và traits activation nhất quán với lệnh `newactivation`.
- [ ] CBP/ZIP vượt qua kiểm tra CRC.
- [ ] SWF mở, đăng nhập, vào map và mở đúng màn hình vừa sửa trên Flash 11.4.
- [ ] Sau deploy, kiểm tra Event Viewer không có lỗi `Flash32_11_4_402_265.ocx`.
- [ ] Xác nhận server vẫn tải/lưu nhân vật và kết nối không bị đóng bất thường.

## Phương án rollback

Nếu client crash sau deploy, rollback riêng `GameFrame.swf` về backup gần nhất trước. Không rollback CBP hoặc dữ liệu server khi chúng đã được xác minh độc lập và không liên quan đến lỗi. Sau rollback phải đổi cache version để client không tiếp tục dùng SWF lỗi.
