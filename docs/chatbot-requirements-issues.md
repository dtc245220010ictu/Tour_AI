# Phân Tích Điểm Chưa Rõ & Giả Định Của Chatbot (Chatbot Requirements Issues)

## 1. Điểm chưa rõ & Cách giải quyết
1. **Chuẩn hóa giá tiền trong câu hỏi tiếng Việt:**
   - *Vấn đề:* Khách hàng có thể viết "4 triệu", "4tr", "4 củ", "4.000.000", "4000k".
   - *Cách giải quyết:* `question_analyzer.py` cài đặt bộ regex thông minh nhận diện đầy đủ các biến thể từ ngữ tiếng Việt và quy đổi chính xác về con số VNĐ (ví dụ: "4 triệu" / "4tr" / "4 củ" -> `4000000`).
2. **Tìm kiếm mờ (Fuzzy / Keyword matching):**
   - *Vấn đề:* Khách hàng có thể gõ không dấu ("da nang", "ha long", "phu quoc") hoặc chỉ gõ sở thích ("nghỉ dưỡng biển", "leo núi săn mây").
   - *Cách giải quyết:* Xây dựng từ điển ánh xạ từ khóa sở thích sang các điểm đến và tour tương ứng (ví dụ: "biển" -> Phú Quốc, Hạ Long, Đà Nẵng; "núi" / "săn mây" -> Sa Pa, Hà Giang, Đà Lạt).

## 2. Các giả định chính
- Chatbot là kênh tư vấn hỗ trợ trước khi đặt chỗ (Pre-booking consultation). Chatbot không tự ý thanh toán hoặc trừ tiền của khách hàng; khi khách ưng ý một tour, chatbot sẽ cung cấp đường link và thông tin để khách tự xác nhận đặt tour qua quy trình chuẩn.
- Thời gian phản hồi trung bình của Chatbot được kỳ vọng dưới 3-5 giây.

