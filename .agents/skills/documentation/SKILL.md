---
name: documentation
description: Duy trì tài liệu dự án đầy đủ và luôn đồng bộ, gồm README, đặc tả API, hướng dẫn triển khai, hướng dẫn sử dụng và các tài liệu tham chiếu kiến trúc — bám sát đúng thực tế triển khai.
---
# Skill Viết Tài Liệu

## Mục tiêu
Tạo ra tài liệu rõ ràng, chính xác và có thể hành động, phản ánh đúng phần mềm đã triển khai, giúp lập trình viên, kỹ sư vận hành và người dùng cuối hiểu, triển khai và vận hành hệ thống dễ dàng.

## Đầu vào
Đọc:
- Toàn bộ mã nguồn (`app.py`, `routes/`, `services/`, `database/`, `tests/`)
- Toàn bộ đặc tả thiết kế đã phê duyệt trong `docs/`

## Quy trình
1. **Tạo/cập nhật README.md:**
   - Tổng quan dự án, tính năng cốt lõi, tóm tắt kiến trúc.
   - Yêu cầu hệ thống, cài đặt, cấu hình biến môi trường, thiết lập CSDL.
   - Lệnh quickstart để chạy ứng dụng và chạy kiểm thử tự động.
   - Tài khoản demo và các câu truy vấn thử nghiệm.
2. **Đặc tả API (`docs/api.md`):**
   - Danh sách endpoint (`GET`, `POST`), tham số URL, schema request body, payload phản hồi, mã lỗi HTTP.
3. **Hướng dẫn triển khai (`docs/deployment.md`):**
   - Hướng dẫn triển khai production với Gunicorn, Nginx, Docker, systemd và cấu hình MySQL.
4. **Hướng dẫn sử dụng (`docs/user-guide.md`):**
   - Hướng dẫn từng bước cho Khách hàng (xem tour, tìm kiếm, tư vấn chatbot, đặt chỗ, thanh toán, đánh giá) và Nhân viên/Quản trị (dashboard, CRUD tour, công cụ AI sinh nội dung, tóm tắt phản hồi).

## Quy tắc
- Tài liệu hóa đúng thực tế đã triển khai; tuyệt đối không mô tả tính năng không tồn tại trong mã nguồn.
- Mọi dòng lệnh và đoạn mã đều phải sẵn sàng copy-paste và đã được kiểm chứng.
- Duy trì tính nhất quán song ngữ hoặc dùng tiếng Việt chuẩn cho hướng dẫn sử dụng và tài liệu kỹ thuật.

## Đầu ra
- `README.md`
- `docs/api.md`
- `docs/deployment.md`
- `docs/user-guide.md`
