# Yêu Cầu Cho Trợ Lý AI Chatbot Tư Vấn Tour (Chatbot Requirements)

## 1. Bối cảnh & Mục tiêu
Khách hàng truy cập website công ty du lịch thường có nhu cầu tư vấn tour bằng ngôn ngữ tự nhiên (tiếng Việt), ví dụ:
- *"Có tour Hạ Long nào 2 ngày dưới 4 triệu không?"*
- *"Tôi có khoảng 5 triệu, muốn đi biển 3-4 ngày thì có tour nào?"*
- *"Gợi ý cho tôi tour đi Sa Pa hoặc Hà Giang cuối tuần này còn chỗ."*
- *"Tour nào có giá thấp nhất hiện tại?"*

Hệ thống cần cung cấp trợ lý ảo AI thông minh, hỗ trợ khách hàng tìm kiếm và lựa chọn tour nhanh chóng mà không cần lật từng trang danh mục.

## 2. Các nguyên tắc và ràng buộc cốt lõi
1. **Chính sách Không bịa đặt dữ liệu (Zero Hallucination Policy):**
   - Chatbot bắt buộc phải dựa vào dữ liệu tour thực tế được truy xuất từ cơ sở dữ liệu (MySQL / SQLite).
   - Tuyệt đối không được tự ý bịa đặt tên tour, giá tiền, địa điểm, lịch trình hoặc ngày khởi hành không có thật trong hệ thống.
   - Nếu trong CSDL không có tour nào thỏa mãn yêu cầu của khách hàng, Chatbot phải thông báo lịch sự rằng hiện chưa có tour phù hợp và đề xuất các tour tương tự hoặc mời khách liên hệ nhân viên tư vấn.
2. **Ngôn ngữ:**
   - Chatbot phải hiểu và trả lời bằng tiếng Việt tự nhiên, thân thiện, lịch sự và chuyên nghiệp.
3. **Bảo mật tuyệt đối (Security & Secrets Isolation):**
   - API Key của Gemini không được xuất hiện trong source code, không lưu trong file tĩnh và tuyệt đối không truyền ra client/JavaScript.
   - Giao diện người dùng (frontend) chỉ gọi API thông qua endpoint an toàn của backend: `POST /api/chat`.
   - Chatbot và LLM không được quyền truy cập trực tiếp vào CSDL để tránh rò rỉ hoặc bị tấn công Prompt Injection / SQL Injection.
4. **Hiển thị trực quan (Rich UI):**
   - Khi gợi ý tour, phản hồi của Chatbot cần hỗ trợ hiển thị kèm thẻ tour trực quan (Tour Cards) gồm: ảnh đại diện, tên tour, điểm đến, thời lượng, giá tiền và nút "Xem chi tiết / Đặt tour".

