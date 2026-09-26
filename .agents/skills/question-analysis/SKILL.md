---
name: question-analysis
description: Phân tích câu hỏi ngôn ngữ tự nhiên tiếng Việt của người dùng và bóc tách tham số tìm kiếm có cấu trúc gồm điểm đến, giới hạn ngân sách, thời lượng và sở thích.
---
# Skill Phân Tích Câu Hỏi

## Mục tiêu
Chuyển câu hỏi ngôn ngữ tự nhiên thô thành đối tượng intent JSON có cấu trúc, chứa tiêu chí tìm kiếm đã chuẩn hóa, phù hợp cho truy vấn CSDL.

## Đầu vào
- Chuỗi truy vấn ngôn ngữ tự nhiên (tiếng Việt).

## Đầu ra
Intent JSON có cấu trúc gồm các trường:
- `destinations`: danh sách điểm đến được nhắc đến (ví dụ `["Hạ Long", "Đà Nẵng"]`).
- `min_price`: giá tối thiểu (VND) hoặc null.
- `max_price`: giá tối đa (VND) hoặc null.
- `duration_days`: danh sách hoặc số ngày được yêu cầu (ví dụ `2`, `3`).
- `keywords`: các từ khóa du lịch chính được bóc tách (ví dụ `["biển", "du thuyền", "nghỉ dưỡng"]`).
- `sort_by`: tiêu chí sắp xếp (`"price_asc"`, `"price_desc"` hoặc `null`).

## Quy tắc
- Không tự thêm điểm đến không được nhắc đến hoặc không được hàm ý rõ ràng.
- Không đoán ràng buộc giá nếu người dùng không nêu ngân sách.
- Chuẩn hóa cách diễn đạt tiền Việt Nam về số VND:
  - "dưới 5 triệu" / "dưới 5tr" / "dưới 5 củ" → `max_price: 5000000`
  - "khoảng 3-4 triệu" → `min_price: 3000000, max_price: 4000000`
  - "khoảng 5 triệu" / "tour 5 triệu" / "tôi có 5 triệu" (ngân sách không có tiền tố rõ ràng) → `max_price: 5000000`
  - "ít nhất 3 ngày" → `duration_days: 3`
  - "3-4 ngày" / "từ 3 đến 4 ngày" → `duration_days: [3, 4]` (khoảng bao gồm hai đầu)
- Xử lý linh hoạt cả đầu vào có dấu và không dấu ("da lat" → "Đà Lạt").
- Chỉ so khớp điểm đến và từ khóa theo từ nguyên vẹn (whole word): "khoảng" khi bỏ dấu thành "khoang" tuyệt đối không được kích hoạt từ khóa "hoa", nếu không câu hỏi sẽ bị ánh xạ nhầm sang Đà Lạt và các câu hỏi ngân sách hợp lệ trả về 0 tour.
