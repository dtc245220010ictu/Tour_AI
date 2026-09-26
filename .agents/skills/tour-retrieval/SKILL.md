---
name: tour-retrieval
description: Truy xuất tour và lịch khởi hành phù hợp từ CSDL quan hệ bằng intent có cấu trúc và truy vấn SQL tham số hóa, đảm bảo không SQL injection và không bịa dữ liệu.
---
# Skill Truy Xuất Tour / Sản Phẩm

## Mục tiêu
Thực thi truy vấn CSDL chính xác, an toàn, tham số hóa trên MySQL/SQLite để chỉ lấy ra các tour đang bán còn chỗ đúng với ý định (intent) của người dùng.

## Đầu vào
- Intent JSON có cấu trúc từ `question_analyzer`.

## Quy trình
1. Xây dựng câu truy vấn SQL tham số hóa nền (`tours` join với `destinations` và `tour_schedules`).
2. Áp dụng bộ lọc tour đang hoạt động (`tours.is_active = 1`).
3. Áp dụng bộ lọc lịch mở bán còn chỗ (`schedules.available_seats > 0`).
4. Áp dụng bộ lọc điểm đến và vùng miền.
5. Áp dụng ràng buộc ngân sách (`base_price <= max_price`, `base_price >= min_price`).
6. Áp dụng bộ lọc thời lượng (`duration_days = ?` khi intent nêu một số ngày; `duration_days BETWEEN ? AND ?` khi intent cho khoảng bao gồm hai đầu như `[3, 4]`).
7. Áp dụng sắp xếp (theo giá, đánh giá hoặc ngày khởi hành gần nhất).
8. Giới hạn số lượng kết quả (thường 3 đến 5 kết quả).

## Quy tắc
- TUYỆT ĐỐI KHÔNG dùng format/nối chuỗi để dựng câu truy vấn SQL.
- LUÔN dùng truy vấn tham số hóa với placeholder (`?` hoặc `%s`).
- Không trả về tour đã ngừng bán hoặc đã xóa.
- Không trả về tour hết chỗ (`available_seats = 0`).
- Nếu không tìm thấy tour phù hợp, trả về danh sách rỗng (`[]`). Không bao giờ bịa dữ liệu.
- Truy xuất thay thế (`retrieve_alternative_tours`) chạy sau khi tìm kiếm nghiêm ngặt trả về rỗng, để chatbot có thể trung thực báo "không có tour đúng tiêu chí" ĐỒNG THỜI giới thiệu các tour thật khác: ưu tiên tour thuộc điểm đến được yêu cầu (giá thấp nhất trước); nếu các điểm đến đó hoàn toàn không có tour, chuyển sang bất kỳ tour còn chỗ nào. Chỉ được trả về `[]` khi CSDL thực sự không còn tour nào khả dụng.
