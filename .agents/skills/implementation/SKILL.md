---
name: implementation
description: Triển khai tính năng trung thành với yêu cầu đã phê duyệt, hướng dẫn kiến trúc và đặc tả CSDL; mã sạch, xử lý lỗi đầy đủ và kiểm thử vững chắc.
---
# Skill Triển Khai (Implementation)

## Mục tiêu
Viết mã Python Flask dễ bảo trì, an toàn, sẵn sàng production, thực thi đúng đặc tả đã phê duyệt — không tự thêm giả định ngoài tài liệu và không thay đổi kiến trúc.

## Đầu vào
Đọc:
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/database-design.md`
- `docs/acceptance-criteria.md`

## Quy trình
1. **Đọc đặc tả:** Xem lại các Yêu cầu chức năng và Tiêu chí chấp nhận liên quan trước khi triển khai.
2. **Hiểu kiến trúc:** Xác định thành phần đích trong kiến trúc phân lớp (Route → Service → Database).
3. **Hiểu CSDL:** Kiểm tra schema, kiểu dữ liệu, ràng buộc và quan hệ.
4. **Triển khai logic cốt lõi:**
   - Viết hàm/lớp Python sạch, mô-đun hóa, kèm type hints và docstrings.
   - Triển khai kiểm tra dữ liệu đầu vào và xử lý lỗi.
   - Chỉ dùng truy vấn SQL tham số hóa để phòng chống SQL injection.
   - Đảm bảo giao dịch CSDL nguyên tử cho các thao tác quan trọng (ví dụ: giữ chỗ).
5. **Chạy linter / kiểm tra cú pháp:** Xác minh cú pháp và chất lượng mã.
6. **Chạy kiểm thử:** Thực thi kiểm thử tự động unit và integration.
7. **Soát diff:** Kiểm tra các file đã thay đổi để đảm bảo không có hồi quy (regression) hoặc chỉnh sửa ngoài ý muốn.

## Quy tắc
- Không thay đổi yêu cầu hoặc kiến trúc khi chưa được phê duyệt.
- Không hard-code API key, secrets hoặc thông tin đăng nhập CSDL.
- Nếu đặc tả chưa đủ hoặc mơ hồ, dừng lại và xin hướng dẫn từ con người thay vì đoán.
- Tuyệt đối không cho dịch vụ AI LLM truy cập CSDL trực tiếp.

## Đầu ra
- Mã nguồn trong `models/`, `services/`, `routes/`, `templates/`, `static/` và `app.py`.
- Bộ kiểm thử tự động trong `tests/`.

## Kiểm tra
- Mã vượt qua kiểm tra lint/cú pháp.
- Toàn bộ kiểm thử unit và integration PASS sạch.
- Xử lý lỗi trả thông báo thân thiện với người dùng, không rò rỉ stack trace nhạy cảm.
