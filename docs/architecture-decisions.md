# Các Quyết Định Kiến Trúc (Architectural Decision Records - ADR)

Tài liệu này ghi nhận các quyết định kiến trúc quan trọng cho hệ thống TourAI (Đề tài 17) theo tiêu chuẩn kiến trúc phần mềm chuyên nghiệp.

---

## ADR-001: Lựa chọn Kiến trúc Phân lớp (Layered Modular Architecture)

### Trạng thái
**APPROVED**

### Bối cảnh
Hệ thống quản lý tour du lịch tích hợp AI cần quản lý các luồng nghiệp vụ phức tạp (đặt chỗ, trừ số chỗ, thanh toán, hủy tour) đồng thời tích hợp dịch vụ RAG AI. Cần một kiến trúc dễ triển khai, dễ kiểm thử, có tính module cao nhưng không quá cồng kềnh như microservices.

### Quyết định
Áp dụng mô hình **Layered Modular Architecture (Modular Monolith)** với các tầng riêng biệt:
- **Presentation Layer:** Jinja2 HTML5, CSS3, JavaScript.
- **Routing Layer:** Flask Blueprints (`auth`, `tour`, `booking`, `admin`, `chat`, `ai_tools`).
- **Service Layer:** Business logic độc lập với Web framework.
- **Data Access Layer:** Cung cấp interface truy cập CSDL thống nhất.
- **AI RAG Subsystem:** Hệ thống con độc lập gồm 6 module tuần tự.

### Hệ quả
- **Tích cực:** Code gọn gàng, kiểm thử đơn giản (có thể test service layer mà không cần chạy HTTP server), giảm độ phức tạp vận hành.
- **Tiêu cực:** Phải duy trì ranh giới giữa các tầng, không được gọi trực tiếp DB từ Controller/Route.

---

## ADR-002: Thiết kế Pipeline RAG Độc Lập - Loại bỏ Ảo Giác (Zero Hallucination)

### Trạng thái
**APPROVED**

### Bối cảnh
Người dùng thường hỏi tự nhiên (ví dụ: "Có tour nào dưới 5 triệu đi biển không?"). Nếu gửi trực tiếp câu hỏi cho LLM mà không cung cấp dữ liệu CSDL, LLM sẽ tự bịa ra tour, giá tiền và lịch trình ảo (hallucination). Nếu cho LLM quyền truy cập trực tiếp CSDL (text-to-SQL tự động), sẽ đối mặt nguy cơ SQL Injection và lỗi cú pháp.

### Quyết định
Thiết kế chuỗi RAG 6 bước có kiểm soát chặt chẽ:
`User Question` → `Question Analyzer (Structured JSON)` → `Tour Retriever (Parameterized SQL)` → `Context Builder (Compact Clean Text)` → `Prompt Builder (Grounding Rules)` → `Gemini API` → `Structured Output`.
- Nếu Retriever không tìm thấy tour phù hợp trong CSDL, hệ thống trả ngay phản hồi thông báo không tìm thấy mà không cho LLM suy diễn.
- LLM tuyệt đối không có quyền kết nối trực tiếp CSDL.

### Hệ quả
- **Tích cực:** 100% tour gợi ý là tour có thật và còn chỗ trong hệ thống; bảo mật CSDL tuyệt đối; tránh được prompt injection phá hoại CSDL.
- **Tiêu cực:** Cần triển khai Question Analyzer để bóc tách từ khóa tốt.

---

## ADR-003: Cơ chế Kiểm soát Số Chỗ Trống & Phòng chống Overbooking

### Trạng thái
**APPROVED**

### Bối cảnh
Nhiều khách hàng có thể cùng đặt chỗ cho một đợt khởi hành vào cùng một thời điểm. Nếu không xử lý concurrency, có thể dẫn đến việc bán vượt quá số chỗ (Overbooking).

### Quyết định
- Bảng `tour_schedules` lưu trữ hai trường: `total_seats` và `available_seats`.
- Khi thực hiện đặt tour, logic nghiệp vụ kiểm tra `available_seats >= (num_adults + num_children)`.
- Sử dụng Database Transaction với câu lệnh kiểm tra và cập nhật nguyên tử (Atomic Update):
  `UPDATE tour_schedules SET available_seats = available_seats - ? WHERE id = ? AND available_seats >= ?`.
- Khi hủy booking, thực hiện atomic update:
  `UPDATE tour_schedules SET available_seats = available_seats + ? WHERE id = ?`.
- Khi Staff/Admin cập nhật lịch khởi hành, không nhận `available_seats` từ client. Hệ thống tính lại giá trị này trong transaction bằng `total_seats - SUM(số khách của booking PENDING/CONFIRMED/COMPLETED)` và từ chối giảm `total_seats` thấp hơn số ghế đã giữ.

### Hệ quả
- **Tích cực:** Đảm bảo tính toàn vẹn dữ liệu, triệt tiêu nguy cơ overbooking.
- **Tiêu cực:** Cần xử lý rollback giao dịch khi có lỗi phát sinh.

---

## ADR-004: Lưu trữ MySQL 8 cho runtime

### Trạng thái
**APPROVED**

### Bối cảnh
Yêu cầu dự án bắt buộc sử dụng MySQL. Backend cũ dùng SQLite không đáp ứng yêu cầu triển khai, kiểm soát đồng thời và đối chiếu báo cáo.

### Quyết định
Phiên bản hiện tại chính thức dùng MySQL 8:
- Kết nối được cấu hình bằng `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD` và `MYSQL_DB`.
- `database/schema.sql` là DDL MySQL; `init_db()` tạo bảng và chỉ mục.
- `database/db.py` dùng `mysql-connector-python`, quản lý transaction và cung cấp adapter giữ hợp đồng truy vấn có tham số của các service.
- Dữ liệu SQLite cũ chỉ được chuyển bằng `scripts/migrate_sqlite_to_mysql.py` khi người vận hành chủ động chạy.

### Hệ quả
- **Tích cực:** Đáp ứng yêu cầu MySQL, hỗ trợ nhiều worker và có ràng buộc khóa ngoại/chỉ mục ở server CSDL.
- **Giới hạn:** Cần quản lý tài khoản, sao lưu, quyền truy cập và một database test riêng; không dùng `MYSQL_TEST_DB` cho dữ liệu vận hành.

---

## ADR-005: Cơ chế Bảo vệ Bí mật & Fallback khi thiếu Gemini API Key

### Trạng thái
**APPROVED**

### Bối cảnh
API key không được lưu trong mã nguồn hoặc client-side JS. Ngoài ra, trong môi trường đánh giá hoặc khi sinh viên/giảng viên chưa kịp điền API Key, ứng dụng vẫn phải hoạt động bình thường, không được văng lỗi 500.

### Quyết định
- Lưu `GEMINI_API_KEY` trong `.env` (được đưa vào `.gitignore`).
- `GeminiService` kiểm tra sự tồn tại của `GEMINI_API_KEY`.
- Nếu có Key hợp lệ: Gọi Google Gemini Generative AI API.
- Nếu không có Key (hoặc mất kết nối mạng): Tự động chuyển sang chế độ **Rule-Based Smart Fallback**, tổng hợp câu trả lời tư vấn chuẩn mực từ context đã truy xuất mà không làm gián đoạn trải nghiệm người dùng.

### Hệ quả
- **Tích cực:** Đảm bảo tính sẵn sàng cao (High Availability), kiểm thử và chấm điểm mượt mà trong mọi điều kiện mạng.

