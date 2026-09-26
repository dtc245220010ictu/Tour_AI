---
name: database-design
description: Thiết kế lược đồ CSDL quan hệ chuẩn hóa từ yêu cầu đã phê duyệt và mô hình kiến trúc, bao gồm bảng, quan hệ, ràng buộc, chỉ mục (index) và script SQL.
---
# Skill Thiết Kế CSDL

## Mục tiêu
Chuyển yêu cầu phần mềm đã phê duyệt và đặc tả kiến trúc thành thiết kế CSDL quan hệ chuẩn hóa, tối ưu (MySQL/SQLite), đầy đủ ràng buộc, chỉ mục và script SQL schema hoàn chỉnh.

## Đầu vào
Đọc:
- `docs/requirements.md`
- `docs/architecture.md`
- `docs/uml-diagrams.md`

## Quy trình
1. **Xác định thực thể:** Trích xuất toàn bộ thực thể miền cốt lõi từ yêu cầu và ERD.
2. **Định nghĩa thuộc tính & kiểu dữ liệu:** Chọn kiểu dữ liệu phù hợp (VARCHAR, INT, DECIMAL, DATETIME, TEXT, BOOLEAN), đảm bảo hiệu quả lưu trữ và độ chính xác.
3. **Thiết lập quan hệ & bản số:** Định nghĩa quan hệ 1-1, 1-N, N-M với khóa ngoại (Foreign Key) tường minh.
4. **Chuẩn hóa:** Áp dụng nguyên tắc chuẩn hóa 1NF, 2NF, 3NF để loại bỏ dư thừa dữ liệu và bất thường cập nhật.
5. **Khóa & ràng buộc:**
   - Định nghĩa khóa chính (AUTO_INCREMENT/INTEGER PRIMARY KEY).
   - Định nghĩa khóa ngoại kèm toàn vẹn tham chiếu (`ON DELETE CASCADE` hoặc `RESTRICT`).
   - Định nghĩa ràng buộc NOT NULL, UNIQUE và CHECK.
6. **Chiến lược đánh chỉ mục (Index):**
   - Đánh chỉ mục cho các cột tìm kiếm (ví dụ: tên tour, điểm đến, giá, departure_date).
   - Đánh chỉ mục cho khóa ngoại và các cột thường xuyên được lọc.
7. **Tối ưu truy xuất cho RAG & Chatbot:** Đảm bảo chỉ mục hỗ trợ hiệu quả các truy vấn tìm kiếm đa tiêu chí của RAG retriever (điểm đến, khoảng giá, thời lượng, số chỗ còn trống).
8. **Sinh script SQL schema:** Tạo script DDL sạch, sẵn sàng production, tương thích cả MySQL và SQLite.

## Quy tắc
- Không viết mã nguồn ứng dụng.
- Không tự sáng tạo trường dữ liệu không có trong tài liệu.
- Tuân thủ nghiêm ngặt quy ước đặt tên (snake_case cho bảng và cột).
- Đảm bảo khóa ngoại và chỉ mục được định nghĩa tường minh.

## Đầu ra
Tạo:
- `docs/database-design.md`
- `database/schema.sql`

## Kiểm tra
- Xác minh mọi yêu cầu chức năng đều được bao phủ về lưu trữ dữ liệu.
- Xác minh chuẩn hóa đạt tới 3NF.
- Xác minh các ràng buộc sức chứa (`available_seats`, `total_seats`) được hỗ trợ bằng ràng buộc và thao tác nguyên tử.
