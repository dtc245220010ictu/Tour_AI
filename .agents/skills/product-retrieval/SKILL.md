---
name: product-retrieval
description: Truy xuất sản phẩm/tour phù hợp từ CSDL quan hệ bằng intent có cấu trúc và truy vấn SQL tham số hóa, đảm bảo không SQL injection và không bịa dữ liệu.
---
# Skill Truy Xuất Sản Phẩm (Tour)

## Mục tiêu
Thực thi truy vấn CSDL chính xác, an toàn, tham số hóa trên MySQL/SQLite để chỉ lấy ra các tour đang bán còn chỗ đúng với ý định (intent) của người dùng.

## Đầu vào
- Intent JSON có cấu trúc từ `question_analyzer`.

## Quy trình
1. Xây dựng câu truy vấn SQL tham số hóa nền.
2. Áp dụng bộ lọc trạng thái đang hoạt động.
3. Áp dụng ràng buộc sức chứa (`available_seats > 0`).
4. Áp dụng bộ lọc điểm đến/danh mục, ngân sách và thời lượng.
5. Giới hạn số lượng kết quả.

## Quy tắc
- TUYỆT ĐỐI KHÔNG nối chuỗi SQL.
- LUÔN dùng truy vấn tham số hóa (`?`).
- Không bao giờ bịa hoặc đoán sản phẩm.
