---
name: security-review
description: Kiểm toán lỗ hổng an ninh mạng của ứng dụng gồm SQL Injection, Cross-Site Scripting (XSS), rò rỉ secrets, lỗi xác thực & phân quyền và các lỗ hổng đặc thù của LLM.
---
# Skill Đánh Giá Bảo Mật

## Mục tiêu
Thực hiện kiểm toán an ninh mạng toàn diện mã nguồn ứng dụng, hợp đồng API, thao tác CSDL và tích hợp AI bên ngoài để đảm bảo mức bảo mật chuẩn production.

## Danh mục kiểm tra
1. **SQL Injection (SQLi):** Đảm bảo 100% tương tác CSDL dùng truy vấn tham số hóa hoặc lời gọi ORM an toàn. Cấm nội suy chuỗi trong SQL.
2. **Cross-Site Scripting (XSS):** Xác minh mọi dữ liệu người dùng động khi render vào HTML template đều được escape mặc định (Jinja2 auto-escaping) và JS phía client không dùng `innerHTML` mất an toàn.
3. **Cross-Site Request Forgery (CSRF):** Xác minh bảo vệ session trên các request thay đổi trạng thái.
4. **Xác thực & lưu trữ mật khẩu:** Xác minh thuật toán băm mật khẩu (bcrypt / PBKDF2 với work factor cao). Kiểm tra thời hạn session và cơ chế chống brute-force.
5. **Phân quyền (RBAC):** Kiểm tra decorator kiểm soát truy cập theo vai trò (`@roles_required`) trên các endpoint quản trị và nhân viên.
6. **Quản lý secrets & thông tin đăng nhập:** Đảm bảo API key (Gemini API Key, Flask Secret Key, thông tin CSDL) chỉ nằm trong biến môi trường và bị `.gitignore` loại trừ. Kiểm tra JS phía client tuyệt đối không truy cập secrets.
7. **Kiểm tra & làm sạch đầu vào:** Kiểm tra giới hạn biên và kiểu dữ liệu cho mọi payload request (miền giá trị số, độ dài chuỗi, payload SQL injection).
8. **Rò rỉ thông tin:** Đảm bảo bộ xử lý lỗi production che giấu stack trace debug và đường dẫn schema nội bộ.
9. **Bảo mật LLM & RAG:** Xác minh khả năng chống prompt injection, quy tắc bám dữ liệu nghiêm ngặt và LLM không có quyền truy cập CSDL trực tiếp.

## Quy tắc
- KHÔNG chỉnh sửa mã ứng dụng trong quá trình đánh giá.
- Cung cấp bằng chứng cụ thể cho mỗi điểm kiểm tra.
- Phân loại lỗ hổng theo mức độ (CRITICAL, HIGH, MEDIUM, LOW, INFORMATIONAL).

## Đầu ra
Tạo:
- `docs/security-review.md`
