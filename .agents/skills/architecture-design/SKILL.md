---
name: architecture-design
description: Thiết kế kiến trúc phần mềm từ yêu cầu đã được phê duyệt, bảo toàn truy xuất nguồn gốc và ghi nhận đầy đủ các quyết định kiến trúc.
---
# Skill Thiết Kế Kiến Trúc

## Mục tiêu
Chuyển yêu cầu phần mềm đã được phê duyệt thành kiến trúc phần mềm mạch lạc, mô-đun hóa và dễ mở rộng, sẵn sàng cho triển khai.

## Đầu vào
Đọc:
- `docs/requirements.md`
- `docs/user-stories.md`
- `docs/acceptance-criteria.md`
- `docs/uml-diagrams.md`
Chỉ sử dụng các yêu cầu đã được phê duyệt.

## Quy trình
1. Xác định phong cách kiến trúc (Layered Architecture, MVC, Modular Monolith kèm phân hệ AI RAG).
2. Xác định các thành phần và tầng chính (Presentation, Routing, tầng Application/Service, tầng truy cập dữ liệu/ORM, CSDL, dịch vụ AI bên ngoài).
3. Định nghĩa trách nhiệm của từng thành phần.
4. Định nghĩa quan hệ phụ thuộc giữa các thành phần (Dependency Inversion, Loose Coupling).
5. Định nghĩa giao thức giao tiếp và giao diện giữa các thành phần.
6. Định nghĩa luồng dữ liệu xuyên tầng cho các quy trình nghiệp vụ quan trọng.
7. Xác định các hệ thống bên ngoài (Google Gemini AI API, bộ mô phỏng cổng thanh toán).
8. Xác định ranh giới bảo mật, các điểm kiểm soát xác thực/phân quyền và cô lập bí mật (secrets).
9. Ghi nhận các quyết định kiến trúc theo định dạng ADR (Architectural Decision Records).
10. Kiểm tra truy xuất nguồn gốc yêu cầu → kiến trúc.

## Quy tắc
- Không viết mã nguồn.
- Không sửa đổi yêu cầu đã được phê duyệt.
- Không đưa vào công nghệ không cần thiết hoặc thiết kế quá mức (over-engineering).
- Mọi quyết định kiến trúc quan trọng phải có lý do rõ ràng.

## Đầu ra
Tạo:
- `docs/architecture.md`
- `docs/architecture-decisions.md`

## Kiểm tra
Xác minh mọi yêu cầu chức năng quan trọng đều được ít nhất một thành phần kiến trúc đáp ứng.
