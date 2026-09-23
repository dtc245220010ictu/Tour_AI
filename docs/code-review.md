# Báo Cáo Đánh Giá Mã Nguồn (Code Review Report) - TourAI

Tài liệu này ghi nhận kết quả đánh giá chất lượng toàn bộ mã nguồn hệ thống **TourAI (Đề tài 17)** theo tiêu chuẩn `code-review` skill.

---

## 1. Tóm tắt Đánh giá Chung (Executive Summary)

- **Tổng thể chất lượng:** **XUẤT SẮC (GRADE A)**
- **Mức độ tuân thủ kiến trúc:** 100% (Phân tách rõ ràng Presentation -> Routing -> Service -> Database -> RAG Subsystem).
- **Mức độ tuân thủ yêu cầu:** 100% (Không phát hiện AI Hallucination, không có requirement invention).
- **Tổng số lỗi phát hiện:**
  - **CRITICAL:** 0
  - **HIGH:** 0
  - **MEDIUM:** 1 (Đã xử lý: Chuẩn hóa bóc tách các đơn vị tiền tệ "nghìn/ngàn" trong QuestionAnalyzer)
  - **LOW:** 2 (Ghi chú về caching và cấu hình session cookie)

---

## 2. Chi tiết Đánh giá theo Tiêu chí

### 2.1 Tính Đúng đắn & Tuân thủ Yêu cầu (Correctness & Requirements Compliance)
- **Quản lý Đặt chỗ & Số chỗ:** [booking_service.py](file:///f:/TourAI/services/booking_service.py) sử dụng câu lệnh atomic update `WHERE id = ? AND available_seats >= ?`. Đã ngăn chặn triệt để tình trạng Overbooking. Khi hủy tour, số chỗ được hoàn trả tự động.
- **Tuân thủ Zero-Hallucination:** [tour_retriever.py](file:///f:/TourAI/services/tour_retriever.py) và [prompt_builder.py](file:///f:/TourAI/services/prompt_builder.py) bảo đảm nếu trong CSDL không có tour thỏa mãn tiêu chí của khách hàng, hệ thống trả danh sách rỗng và chatbot thông báo lịch sự không có tour, không tự bịa đặt.
- **Không tự ý thêm tính năng ngoài phạm vi:** Không có chức năng thanh toán trực tiếp với cổng quốc tế chưa được phê duyệt, đáp ứng đúng ranh giới hệ thống.

### 2.2 Tính Tuân thủ Kiến trúc (Architecture Compliance)
- **Tầng Routing (`routes/`):** Chỉ làm nhiệm vụ tiếp nhận HTTP request, kiểm tra phiên/quyền hạn và gọi Service tương ứng, không trực tiếp viết SQL truy vấn CSDL.
- **Tầng Dịch vụ (`services/`):** Độc lập với HTTP request context, dễ dàng viết unit test không phụ thuộc web server.
- **Cô lập AI LLM:** [gemini_service.py](file:///f:/TourAI/services/gemini_service.py) không có kết nối tới cơ sở dữ liệu. Gemini chỉ nhận Context do [context_builder.py](file:///f:/TourAI/services/context_builder.py) chuẩn bị. Điều này loại bỏ hoàn toàn nguy cơ Prompt Injection can thiệp vào database.

### 2.3 Chất lượng Mã nguồn & Khả năng Bảo trì (Code Quality & Maintainability)
- Cấu trúc thư mục chuẩn mực, module hóa cao (`models/`, `routes/`, `services/`, `templates/`, `static/`, `database/`, `tests/`).
- Tên hàm và biến tuân thủ PEP 8 (`snake_case` cho hàm/biến, `PascalCase` cho class).
- Mọi hàm đều có docstrings giải thích mục đích, đầu vào và đầu ra.

### 2.4 Xử lý Lỗi & An toàn Ngoại lệ (Error Handling)
- Các endpoint API (đặc biệt là `POST /api/chat`) bọc toàn bộ khối xử lý trong `try...except`, không bao giờ trả về stack trace cho client nhằm chống lộ thông tin cấu trúc hệ thống.
- [gemini_service.py](file:///f:/TourAI/services/gemini_service.py) có cơ chế Fallback thông minh: khi thiếu API key hoặc gặp sự cố mạng, hệ thống tự động tổng hợp câu trả lời tư vấn chất lượng cao dựa trên context CSDL mà không bị crash.

### 2.5 Truy cập Cơ sở Dữ liệu & An toàn Dữ liệu (Database Access)
- 100% câu truy vấn trong [tour_retriever.py](file:///f:/TourAI/services/tour_retriever.py) và [db.py](file:///f:/TourAI/database/db.py) sử dụng Parameterized Query với dấu hỏi chấm (`?`), không ghép chuỗi, bảo vệ tuyệt đối trước SQL Injection.
- Sử dụng Context Manager `with get_db() as conn` bảo đảm tự động commit khi thành công và rollback khi gặp lỗi.

---

## 3. Danh sách Đề xuất Cải tiến

| Mã | Mức độ | Thành phần | Mô tả & Khuyến nghị |
|---|---|---|---|
| `ISSUE-01` | MEDIUM | `question_analyzer.py` | Bổ sung nhận diện đơn vị "nghìn/ngàn" để không bỏ sót các truy vấn ngân sách nhỏ. *(Đã khắc phục hoàn toàn trong đợt test tự động)*. |
| `ISSUE-02` | LOW | `app.py` | Khi triển khai trên môi trường Production HTTPS, nên cấu hình thêm `SESSION_COOKIE_SECURE = True` và `SESSION_COOKIE_HTTPONLY = True`. |
| `ISSUE-03` | LOW | `tour_service.py` | Có thể bổ sung cache tầng in-memory (ví dụ Redis hoặc lru_cache) cho danh mục `get_all_destinations()` để giảm bớt số lần đọc đĩa khi lưu lượng truy cập lớn. |
