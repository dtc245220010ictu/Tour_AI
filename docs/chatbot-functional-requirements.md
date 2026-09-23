# Yêu Cầu Chức Năng Cho Chatbot AI (Chatbot Functional Requirements)

Tài liệu này đặc tả các yêu cầu chức năng cụ thể của hệ thống con RAG Chatbot theo `requirements-analysis` skill.

---

## Danh sách Yêu cầu Chức năng Chatbot

- **FR-CHAT-001:** Hệ thống cung cấp giao diện chat trực tuyến cho phép khách hàng gửi câu hỏi bằng ngôn ngữ tự nhiên tiếng Việt.
- **FR-CHAT-002:** Hệ thống phân tích câu hỏi của khách hàng thành cấu trúc ý định (Structured Intent) gồm: điểm đến/vùng miền, ngân sách tối đa/tối thiểu, số ngày (thời lượng), từ khóa sở thích (biển, núi, du thuyền, nghỉ dưỡng), sắp xếp theo giá.
- **FR-CHAT-003:** Hệ thống xây dựng truy vấn SQL có tham số (parameterized query) để tìm kiếm các tour còn chỗ (`available_seats > 0`) trong cơ sở dữ liệu thỏa mãn điều kiện lọc.
- **FR-CHAT-004:** Hệ thống xây dựng ngữ cảnh dữ liệu (Context Text) tinh gọn, chính xác từ danh sách các tour tìm được trong CSDL.
- **FR-CHAT-005:** Hệ thống gắn ngữ cảnh và câu hỏi vào mẫu Prompt chuẩn với các quy tắc ràng buộc không bịa dữ liệu và gửi tới Google Gemini AI API.
- **FR-CHAT-006:** Hệ thống nhận phản hồi từ Gemini và trả về câu trả lời hoàn chỉnh kèm danh sách thẻ tour (tour cards) cho giao diện người dùng.
- **FR-CHAT-007:** Nếu không tìm thấy tour nào thỏa mãn điều kiện trong CSDL, hệ thống phải thông báo rõ ràng rằng hiện không có tour phù hợp và hướng dẫn khách hàng thay đổi tiêu chí, không được bịa ra thông tin giả.
- **FR-CHAT-008:** Hệ thống phải có cơ chế lưu nhật ký đối thoại (chat logs) để phân tích nhu cầu khách hàng và cải thiện chất lượng phục vụ.
- **FR-CHAT-009:** Hệ thống phải có cơ chế Fallback thông minh: Nếu chưa có Gemini API Key hoặc mất kết nối mạng bên ngoài, hệ thống tự động tổng hợp câu trả lời tư vấn chuẩn xác từ dữ liệu CSDL tìm được mà không làm gián đoạn trải nghiệm người dùng.

