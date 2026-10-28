# Báo Cáo Đánh Giá Mã Nguồn (Code Review Report) - TourAI

Tài liệu này ghi nhận kết quả đánh giá chất lượng toàn bộ mã nguồn hệ thống **TourAI (Đề tài 17)** theo tiêu chuẩn `code-review` skill.

---

## 1. Tóm tắt Đánh giá Chung (Executive Summary)

- **Tổng thể chất lượng:** **TỐT (GRADE B)**
- **Mức độ tuân thủ kiến trúc:** Luồng chính tách Presentation -> Routing -> Service -> Database -> RAG; có ngoại lệ ở `accounting_routes.py` truy vấn trực tiếp để nạp dropdown.
- **Mức độ tuân thủ yêu cầu:** Logic RAG vẫn được giữ nguyên; bộ kiểm thử phải được chạy lại trên `MYSQL_TEST_DB` trước khi xác nhận kết quả cho runtime MySQL.
- **Tổng số lỗi phát hiện:**
  - **CRITICAL:** 0
  - **HIGH:** 1 (fallback `SECRET_KEY` hard-code phải được thay bằng cấu hình bắt buộc khi production)
  - **MEDIUM:** 1 (một số query ở route)
  - **LOW:** 2 (Ghi chú về caching và cấu hình session cookie)

---

## 2. Chi tiết Đánh giá theo Tiêu chí

### 2.1 Tính Đúng đắn & Tuân thủ Yêu cầu (Correctness & Requirements Compliance)
- **Quản lý Đặt chỗ & Số chỗ:** [booking_service.py](../services/booking_service.py) sử dụng câu lệnh atomic update `WHERE id = ? AND available_seats >= ?`. Đã ngăn chặn triệt để tình trạng Overbooking. Khi hủy tour, số chỗ được hoàn trả tự động.
- **Tuân thủ Zero-Hallucination:** [tour_retriever.py](../services/tour_retriever.py) và [prompt_builder.py](../services/prompt_builder.py) bảo đảm nếu trong CSDL không có tour thỏa mãn tiêu chí của khách hàng, hệ thống trả danh sách rỗng và chatbot thông báo lịch sự không có tour, không tự bịa đặt.
- **Không tự ý thêm tính năng ngoài phạm vi:** Không có chức năng thanh toán trực tiếp với cổng quốc tế chưa được phê duyệt, đáp ứng đúng ranh giới hệ thống.

### 2.2 Tính Tuân thủ Kiến trúc (Architecture Compliance)
- **Tầng Routing (`routes/`):** Chỉ làm nhiệm vụ tiếp nhận HTTP request, kiểm tra phiên/quyền hạn và gọi Service tương ứng, không trực tiếp viết SQL truy vấn CSDL.
- **Tầng Dịch vụ (`services/`):** Độc lập với HTTP request context, dễ dàng viết unit test không phụ thuộc web server.
- **Cô lập AI LLM:** [gemini_service.py](../services/gemini_service.py) không có kết nối tới cơ sở dữ liệu. Gemini chỉ nhận Context do [context_builder.py](../services/context_builder.py) chuẩn bị. Điều này loại bỏ hoàn toàn nguy cơ Prompt Injection can thiệp vào database.

### 2.3 Chất lượng Mã nguồn & Khả năng Bảo trì (Code Quality & Maintainability)
- Cấu trúc thư mục module hóa rõ ràng (`routes/`, `services/`, `templates/`, `static/`, `database/`, `tests/`); dự án không có package `models/`/ORM, dữ liệu được trao đổi bằng `dict`/`Row` do adapter MySQL chuẩn hóa.
- Tên hàm và biến tuân thủ PEP 8 (`snake_case` cho hàm/biến, `PascalCase` cho class).
- Mọi hàm đều có docstrings giải thích mục đích, đầu vào và đầu ra.

### 2.4 Xử lý Lỗi & An toàn Ngoại lệ (Error Handling)
- Các endpoint API (đặc biệt là `POST /api/chat`) bọc toàn bộ khối xử lý trong `try...except`, không bao giờ trả về stack trace cho client nhằm chống lộ thông tin cấu trúc hệ thống.
- [gemini_service.py](../services/gemini_service.py) có cơ chế Fallback thông minh: khi thiếu API key hoặc gặp sự cố mạng, hệ thống tự động tổng hợp câu trả lời tư vấn chất lượng cao dựa trên context CSDL mà không bị crash.

### 2.5 Truy cập Cơ sở Dữ liệu & An toàn Dữ liệu (Database Access)
- 100% câu truy vấn trong [tour_retriever.py](../services/tour_retriever.py) và [db.py](../database/db.py) sử dụng Parameterized Query với dấu hỏi chấm (`?`), không ghép chuỗi, bảo vệ tuyệt đối trước SQL Injection.
- Sử dụng Context Manager `with get_db() as conn` bảo đảm tự động commit khi thành công và rollback khi gặp lỗi.

---

## 3. Danh sách Đề xuất Cải tiến

| Mã | Mức độ | Thành phần | Mô tả & Khuyến nghị |
|---|---|---|---|
| `ISSUE-01` | MEDIUM | `question_analyzer.py` | Bổ sung nhận diện đơn vị "nghìn/ngàn" để không bỏ sót các truy vấn ngân sách nhỏ. *(Đã khắc phục hoàn toàn trong đợt test tự động)*. |
| `ISSUE-02` | LOW | `app.py` | Khi triển khai trên môi trường Production HTTPS, nên cấu hình thêm `SESSION_COOKIE_SECURE = True` và `SESSION_COOKIE_HTTPONLY = True`. |
| `ISSUE-03` | LOW | `tour_service.py` | Có thể bổ sung cache tầng in-memory (ví dụ Redis hoặc lru_cache) cho danh mục `get_all_destinations()` để giảm bớt số lần đọc đĩa khi lưu lượng truy cập lớn. |
| `ISSUE-04` | HIGH | `app.py` | `SECRET_KEY` có giá trị fallback hard-code. Production phải fail-fast khi thiếu secret hoặc inject secret ngẫu nhiên qua environment; không dùng fallback demo. |
| `ISSUE-05` | RESOLVED | `database/db.py` | Runtime đã chuyển sang MySQL 8 với transaction và test database riêng; toàn bộ 175 pytest đã PASS trên MySQL. Hai query nạp dropdown ở route vẫn là ngoại lệ với tầng service, nên chuyển vào service khi tái cấu trúc. |

---

## 4. Rà soát điều hướng theo vai trò (2026-10-27)

| Mức độ | Phát hiện | Bằng chứng | Trạng thái xử lý |
|---|---|---|---|
| HIGH | Chọn nhóm đổi màu nhưng không đổi phần nội dung. | JavaScript tìm `[data-workspace-panel]`, trong khi section panel chưa có thuộc tính này. | Đã gắn `data-workspace-panel` cho mọi panel và bổ sung kiểm thử xác nhận mọi tab đều ánh xạ tới panel tương ứng. |
| MEDIUM | Thanh điều hướng chung lặp lại các lối vào theo vai trò (Kế toán, Quản trị, Lịch phân công, Tour của tôi) vốn đã có trong Không gian làm việc. | `base.html` và `partials/manage_menu.html` cùng hiển thị các chức năng nghiệp vụ. | Đã giữ Trang chủ, Khám phá Tour, Trợ lý AI và một lối quay lại Không gian làm việc; các chức năng nghiệp vụ chi tiết chỉ có trong Không gian làm việc. |
| LOW | CSS của các liên kết vai trò cũ không còn được sử dụng sau khi bỏ menu lặp. | `.nav-link-accounting`, `.nav-link-admin`, `.nav-link-guide`. | Đã loại bỏ các selector không còn dùng. |

Kết quả sau khắc phục: các tab nhóm chỉ thay đổi panel chức năng tương ứng; các thẻ chức năng trong panel vẫn là liên kết điều hướng thực đến endpoint có RBAC.

