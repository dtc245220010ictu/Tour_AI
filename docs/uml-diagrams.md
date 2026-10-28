# Tài Liệu Thiết Kế Biểu Đồ & Bảng UML (UML Diagrams Specification)

Tài liệu này mô hình hóa **trạng thái triển khai hiện tại (as-built)** của hệ thống quản lý tour du lịch tích hợp AI (Đề tài 17), gồm: Use Case Diagram, Class Diagram, Sequence Diagrams, Activity Diagrams và Entity-Relationship Diagram (ERD). Các quyền và luồng được đối chiếu với Flask routes, service và MySQL schema đang có.

---

## 1. Biểu đồ Use Case (Use Case Diagram)

### 1.1 Sơ đồ tổng quan phân hệ và tác nhân
```mermaid
flowchart LR
    subgraph Actors["Tác Nhân (Actors)"]
        Customer["👤 Khách Hàng (Customer)"]
        Staff["👤 Nhân Viên Tư Vấn (Staff)"]
        Admin["👤 Quản Trị Viên (Admin)"]
        Accountant["👤 Kế Toán (Accountant)"]
        Guide["👤 Hướng Dẫn Viên (Guide)"]
        AI["🤖 Trí Tuệ Nhân Tạo (Gemini AI)"]
    end

    subgraph AuthSubsystem["Phân Hệ Xác Thực"]
        Register["Đăng ký tài khoản Customer"]
        Login["Đăng nhập / Đăng xuất"]
        ManageCustomers["Quản lý tài khoản Customer"]
    end

    subgraph TourSubsystem["Phân Hệ Quản Lý Tour"]
        UC3["Xem & Tìm kiếm tour"]
        UC4["Quản lý Tour & Điểm đến"]
        UC5["Quản lý Lịch khởi hành & Số chỗ"]
        UC6["AI Sinh mô tả & Lịch trình"]
    end

    subgraph BookingSubsystem["Phân Hệ Đặt Tour & Thanh Toán"]
        UC7["Đặt chỗ tour"]
        UC8["Xác nhận thanh toán / Đặt cọc"]
        UC9["Hủy tour & Hoàn chỗ"]
    end

    subgraph FinanceSubsystem["Phân Hệ Kế Toán & Tài Chính"]
        FinancePayment["Đối soát thanh toán & Công nợ"]
        FinanceRefund["Duyệt / Từ chối hoàn tiền"]
        FinanceReport["Chi phí, P&L & Sổ quỹ"]
    end

    subgraph OperationsSubsystem["Phân Hệ Điều Hành & Đánh Giá"]
        UC10["Phân công Hướng dẫn viên"]
        UC11["Xem lịch dẫn đoàn"]
        UC12["Gửi đánh giá & phản hồi"]
        UC13["AI Tóm tắt phản hồi"]
        UC14["Thống kê doanh thu & Tỷ lệ lấp đầy"]
    end

    subgraph AISubsystem["Phân Hệ AI Chatbot"]
        UC15["Chatbot tư vấn tour (RAG)"]
    end

    %% Connections
    Customer --> Register
    Customer --> Login
    Customer --> UC3
    Customer --> UC7
    Customer --> UC8
    Customer --> UC9
    Customer --> UC12
    Customer --> UC15

    Staff --> Login
    Staff --> UC4
    Staff --> UC5
    Staff --> UC6
    Staff --> UC7
    Staff --> UC9

    Accountant --> Login
    Accountant --> UC8
    Accountant --> FinancePayment
    Accountant --> FinanceRefund
    Accountant --> FinanceReport
    Accountant --> UC14

    Guide --> Login
    Guide --> UC11

    Admin --> Login
    Admin --> ManageCustomers
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
    Admin --> UC13
    Admin --> UC14
    Admin --> FinancePayment
    Admin --> FinanceRefund
    Admin --> FinanceReport

    UC6 -.-> AI
    UC13 -.-> AI
    UC15 -.-> AI
```

> **Phạm vi as-built:** hệ thống hiện có đăng ký công khai cho `CUSTOMER`, đăng nhập/đăng xuất cho mọi vai trò và màn hình Admin quản lý tài khoản khách hàng. Chưa có route/trang để người dùng tự cập nhật hồ sơ cá nhân, nên use case này không được thể hiện như một chức năng đã triển khai.

### 1.2 Bảng mô tả chi tiết các Use Case chính

| Mã Use Case | Tên Use Case | Tác nhân chính | Tiền điều kiện | Hậu điều kiện |
|---|---|---|---|---|
| `UC-01` | Đặt chỗ tour (Booking) | Khách hàng; Staff/Admin theo quyền hỗ trợ booking | Đã chọn đợt khởi hành `OPEN` và còn chỗ (`available_seats > 0`) | Tạo bản ghi booking, giảm số chỗ trống tương ứng |
| `UC-02` | Hủy đặt chỗ (Cancel Booking) | Khách hàng sở hữu đơn; Staff/Admin qua quản lý booking | Đơn ở trạng thái PENDING hoặc CONFIRMED | Đơn chuyển CANCELLED, hoàn trả số chỗ; tạo phiếu báo hoàn nếu đã thanh toán |
| `UC-03` | Chatbot tư vấn tour (RAG) | Khách hàng | Người dùng nhập câu hỏi tự nhiên | Chatbot trả lời thông tin chính xác từ CSDL, không bịa |
| `UC-04` | AI sinh mô tả tour | Nhân viên / Admin | Nhân viên nhập điểm đến, từ khóa | AI sinh đoạn văn mô tả chuẩn SEO và lịch trình chi tiết |
| `UC-05` | AI tóm tắt phản hồi | Admin | Đã có các phản hồi đánh giá trong CSDL | AI sinh báo cáo tổng hợp ưu/nhược điểm dịch vụ |
| `UC-06` | Ghi nhận thanh toán / đặt cọc | Khách hàng (đơn của mình), Kế toán, Admin | Booking tồn tại; khách chỉ thao tác trên đơn của mình | Có bản ghi payment; booking được xác nhận khi thanh toán thành công hoặc kế toán duyệt giao dịch |
| `UC-07` | Xử lý hoàn tiền hủy tour | Kế toán / Admin | Booking đã `CANCELLED`, có `refund_request` PENDING và giao dịch thanh toán thành công | Phiếu hoàn được APPROVED/REJECTED; khi duyệt sinh payment loại `REFUND` không vượt quá số tiền thực đã thanh toán |
| `UC-08` | Quản lý tài chính theo đoàn | Kế toán / Admin | Người dùng có quyền vào phân hệ kế toán | Đối soát giao dịch, ghi nhận công nợ/chi phí, xem P&L và sổ quỹ |

### 1.3 Đặc tả luồng Use Case trọng yếu

#### UC-06 — Ghi nhận thanh toán / đặt cọc
- **Tác nhân:** Khách hàng (đơn của chính mình), Kế toán, Admin.
- **Tiền điều kiện:** Booking tồn tại; người thao tác được phân quyền phù hợp.
- **Luồng chính:**
  1. Người dùng chọn phương thức thanh toán và số tiền thanh toán/đặt cọc.
  2. Hệ thống tạo bản ghi `payments` với `payment_type` (`DEPOSIT`, `FULL` hoặc `REMAINING`) và trạng thái giao dịch.
  3. Nếu giao dịch `SUCCESS`, booking chuyển từ `PENDING` sang `CONFIRMED`.
  4. Với chuyển khoản ở trạng thái `PENDING`, Kế toán đối soát, cập nhật `verified_by`, `verified_at`, `payment_status = SUCCESS`; booking được xác nhận khi có tiền thanh toán thành công.
- **Ngoại lệ:** số tiền không lớn hơn 0; không tìm thấy booking; thao tác trên booking không thuộc khách hàng; giao dịch đã được duyệt trước đó.
- **Hậu điều kiện:** lịch sử thanh toán được lưu, trạng thái booking phản ánh kết quả duyệt.

#### UC-07 — Hủy tour và xử lý hoàn tiền
- **Tác nhân:** Khách hàng (hủy đơn của mình), Staff/Admin (đổi trạng thái booking sang hủy), Kế toán/Admin (hoàn tiền).
- **Tiền điều kiện:** booking ở `PENDING` hoặc `CONFIRMED`; booking `COMPLETED` không được hủy.
- **Luồng chính:**
  1. Hệ thống chuyển booking sang `CANCELLED` và hoàn số hành khách về lịch khởi hành.
  2. Kế toán xem booking đã hủy cùng tổng tiền đã thanh toán thành công.
  3. Hệ thống đề xuất tỷ lệ hoàn: từ 7 ngày trước khởi hành là 90%, từ 3 đến 6 ngày là 50%, dưới 3 ngày là 0%.
  4. Kế toán xác nhận số tiền hoàn không vượt quá số tiền đã trả còn lại.
  5. Hệ thống lưu payment loại `REFUND`, trạng thái `SUCCESS`, người duyệt và thời điểm duyệt.
- **Ngoại lệ:** khách hủy booking của người khác; hủy booking đã hoàn thành; hoàn vượt quá số tiền đã thanh toán hoặc số tiền còn có thể hoàn.
- **Hậu điều kiện:** chỗ được hoàn trả chính xác; dòng tiền hoàn được lưu để phục vụ công nợ, sổ quỹ và P&L.

---

## 2. Biểu đồ Lớp (Class Diagram)

> **Phạm vi và cách đọc:** mã nguồn Flask hiện tại không khai báo các lớp entity/ORM riêng; dữ liệu được đọc từ MySQL qua adapter và được chuẩn hóa thành `dict`/`Row` trước khi xử lý bởi các lớp service tĩnh. Vì vậy, sơ đồ 2.1 là **mô hình lớp miền** ánh xạ 1-1 với `database/schema.sql`; sơ đồ 2.2 thể hiện các **lớp thực thi** trong thư mục `services/` và các phụ thuộc chính của chúng.

### 2.1 Mô hình lớp miền

```mermaid
classDiagram
    class User {
        +int id
        +string email
        +string password_hash
        +string full_name
        +string phone
        +string role
        +datetime created_at
    }

    class Destination {
        +int id
        +string name
        +string region
        +text description
        +string image_url
        +datetime created_at
    }

    class Tour {
        +int id
        +int destination_id
        +string title
        +string slug
        +text description
        +int duration_days
        +int duration_nights
        +decimal base_price
        +string transportation
        +text itinerary_text
        +string image_url
        +bool is_active
        +datetime created_at
    }

    class TourSchedule {
        +int id
        +int tour_id
        +date departure_date
        +date return_date
        +decimal adult_price
        +decimal child_price
        +int total_seats
        +int available_seats
        +string status
        +text postpone_reason
        +datetime postponed_at
        +datetime created_at
    }

    class Booking {
        +int id
        +string booking_code
        +int user_id
        +int schedule_id
        +string customer_name
        +string customer_email
        +string customer_phone
        +int num_adults
        +int num_children
        +decimal total_amount
        +string status
        +text notes
        +datetime created_at
    }

    class Payment {
        +int id
        +int booking_id
        +decimal amount
        +string payment_method
        +string payment_type
        +string transaction_id
        +string payment_status
        +datetime payment_date
        +int verified_by
        +datetime verified_at
        +text notes
    }

    class RefundRequest {
        +int id
        +int booking_id
        +decimal paid_amount
        +decimal request_amount
        +text reason
        +string status
        +datetime requested_at
        +int processed_by
        +datetime processed_at
        +decimal decision_amount
        +text decision_notes
    }

    class TourGuide {
        +int id
        +string full_name
        +string phone
        +string email
        +string languages
        +int experience_years
        +text bio
        +bool is_active
        +datetime created_at
    }

    class GuideAssignment {
        +int id
        +int schedule_id
        +int guide_id
        +string role_in_tour
        +text notes
        +datetime created_at
    }

    class Feedback {
        +int id
        +int user_id
        +int tour_id
        +int booking_id
        +int rating
        +text comment
        +datetime created_at
    }

    class TourExpense {
        +int id
        +int schedule_id
        +string category
        +string title
        +decimal amount
        +string supplier_name
        +string invoice_code
        +date expense_date
        +int created_by
        +text notes
        +datetime created_at
    }

    class ChatLog {
        +int id
        +string session_id
        +text user_message
        +text intent_json
        +string retrieved_tour_ids
        +text bot_response
        +datetime created_at
    }

    Destination "1" --> "0..*" Tour : contains
    Tour "1" --> "0..*" TourSchedule : has
    TourSchedule "1" --> "0..*" Booking : booked_for
    User "1" --> "0..*" Booking : places
    Booking "1" --> "0..*" Payment : payment_history
    Payment "0..*" --> "0..1" User : verified_by
    Booking "1" --> "0..1" RefundRequest : refund_request
    RefundRequest "0..*" --> "0..1" User : processed_by
    TourSchedule "1" --> "0..*" GuideAssignment : guide_assignments
    TourGuide "1" --> "0..*" GuideAssignment : assignments
    User "1" --> "0..*" Feedback : writes
    Tour "1" --> "0..*" Feedback : receives
    Booking "0..1" --> "0..1" Feedback : verified_review
    TourSchedule "1" --> "0..*" TourExpense : operating_expenses
    User "0..1" --> "0..*" TourExpense : created_by
```

**Ràng buộc miền quan trọng:**

- `TourSchedule.available_seats` luôn nằm trong `[0, total_seats]`; chỉ lịch `OPEN` mới nhận đặt chỗ.
- `Booking` có các trạng thái `PENDING`, `CONFIRMED`, `COMPLETED`, `CANCELLED`; việc hủy hoàn chỗ về lịch khởi hành.
- `Payment.payment_type` gồm `DEPOSIT`, `FULL`, `REMAINING`, `REFUND`. Thanh toán thành công không phải `REFUND` xác nhận booking.
- Mỗi `Booking` có tối đa một `RefundRequest`; yêu cầu được duyệt sinh một `Payment` kiểu `REFUND`.
- `Feedback.booking_id` có thể rỗng theo schema, nhưng nghiệp vụ chỉ cho đánh giá một lần trên booking đã `COMPLETED`.
- `users.role = GUIDE` và hồ sơ `tour_guides` hiện chưa có khóa ngoại liên kết trực tiếp; các trang Guide chỉ đọc danh sách phân công/khách theo dữ liệu phân công hiện có.

### 2.2 Các lớp service và phụ thuộc thực thi

```mermaid
classDiagram
    class AuthService {
        +register_user(email, password, full_name, phone, role) dict
        +login_user(email, password) dict
        +get_user_by_id(user_id) dict
        +update_customer(user_id, full_name, phone, email, password) dict
    }
    class TourService {
        +get_tours(filters) list
        +create_tour(...) int
        +update_tour(...) void
        +sync_schedule_prices(tour_id, base_price) int
        +create_schedule(...) int
        +update_schedule(...) void
        +postpone_schedule(schedule_id, reason) void
        +resume_schedule(schedule_id) void
    }
    class BookingService {
        +create_booking(...) dict
        +cancel_booking(booking_id, user_id, reason) bool
        +update_booking_status(booking_id, status) bool
        +get_user_bookings(user_id) list
    }
    class PaymentService {
        +record_payment(...) int
        +get_payments_by_booking(booking_id) list
    }
    class RefundService {
        +create_request(booking_id, reason, amount) dict
        +approve_request(request_id, approver_id, amount, notes) bool
        +reject_request(request_id, approver_id, notes) bool
        +get_policy_percent(departure_date) int
    }
    class GuideService {
        +create_guide(...) int
        +assign_guide(schedule_id, guide_id, role, notes) int
        +get_assignments(guide_id) list
        +get_assigned_group_customers() list
    }
    class FeedbackService {
        +create_feedback(...) int
        +has_reviewed_booking(booking_id) bool
        +update_feedback(...) bool
        +delete_feedback(...) bool
    }
    class AccountingService {
        +get_payment_reconciliation_list(status) list
        +confirm_payment(payment_id, accountant_id) bool
        +get_booking_debt_list() list
        +record_debt_payment(...) bool
        +record_tour_expense(...) int
        +get_tour_expenses(schedule_id) list
        +get_schedule_pnl(schedule_id) dict
        +get_cashflow_summary(...) dict
        +process_refund(booking_id, refund_amount, accountant_id, notes) bool
    }
    class AnalyticsService {
        +get_dashboard_stats() dict
        +get_top_selling_tours(limit) list
        +get_occupancy_rates(filter) list
    }
    class RAGService {
        +answer_question(question, session_id, role) dict
    }
    class QuestionAnalyzer {
        +analyze_question(question) dict
        +is_feedback_summary_question(question) bool
    }
    class TourRetriever {
        +retrieve_tours(intent, limit) list
        +retrieve_alternative_tours(intent, limit) list
    }
    class ContextBuilder {
        +build_context(tours, alternatives) string
    }
    class PromptBuilder {
        +build_prompt(question, context) string
    }
    class GroundedAnswerBuilder {
        +build(question, intent, tours, alternatives) string
    }
    class GeminiService {
        +is_configured() bool
        +generate_content(prompt, temperature, fallback_answer, timeout) string
    }
    class AIContentService {
        +generate_tour_description(...) dict
        +summarize_feedbacks(feedbacks) string
    }
    class ImageUploadService {
        +save(file) string
    }

    BookingService ..> RefundService : creates request
    RefundService ..> AccountingService : records refund
    RAGService ..> QuestionAnalyzer : analyzes
    RAGService ..> TourRetriever : retrieves
    RAGService ..> ContextBuilder : builds context
    RAGService ..> PromptBuilder : builds prompt
    RAGService ..> GroundedAnswerBuilder : fallback
    RAGService ..> GeminiService : generates answer
    RAGService ..> FeedbackService : reads feedback
    RAGService ..> AIContentService : summarizes feedback
    AIContentService ..> GeminiService : generates content
```

---

## 3. Biểu đồ Trình tự (Sequence Diagrams)

### 3.1 Quy trình Đặt tour & Kiểm soát số chỗ (Booking & Capacity Control)
```mermaid
sequenceDiagram
    autonumber
    actor Customer as 👤 Khách hàng
    participant Route as 🌐 BookingRoute
    participant Service as ⚙️ BookingService
    participant DB as 🗄️ MySQL 8 Database

    Customer->>Route: POST /booking/new/{schedule_id} (form data)
    Route->>Service: create_booking(user_id, schedule_id, adults, children, contact)
    Service->>DB: Mở transaction và đọc lịch theo ID
    DB-->>Service: schedule (status, available_seats, prices)

    alt status != OPEN hoặc available_seats < requested_seats
        Service-->>Route: Raise OverbookingError("Không đủ số chỗ khả dụng")
        Route-->>Customer: Hiển thị lỗi và render lại form
    else lịch đang mở và còn đủ chỗ
        Service->>DB: Atomic update giảm available seats
        DB-->>Service: Cập nhật thành công
        Service->>DB: Tạo booking trạng thái PENDING
        Service->>DB: Đổi lịch thành FULL nếu hết chỗ
        DB-->>Service: Commit, tạo booking BK-XXXXX
        Service-->>Route: Return Booking Object
        Route-->>Customer: 302 Redirect /booking/success/{booking_code}
    end
```

### 3.2 Quy trình Chatbot RAG Tư vấn Tour (Zero Hallucination)
```mermaid
sequenceDiagram
    autonumber
    actor Customer as 👤 Khách hàng
    participant UI as 💻 Chat UI
    participant ChatAPI as 🌐 POST /api/chat
    participant RAG as 🧠 RAGService
    participant Analyzer as 🔍 QuestionAnalyzer
    participant Retriever as 🎯 TourRetriever
    participant DB as 🗄️ MySQL 8 Database
    participant CtxBuilder as 📝 ContextBuilder
    participant PromptBuilder as 📄 PromptBuilder
    participant GroundedAnswerBuilder as 🧾 GroundedAnswerBuilder
    participant Gemini as 🤖 GeminiService

    Customer->>UI: Nhập: "Có tour Đà Nẵng 3 ngày dưới 4 triệu không?"
    UI->>ChatAPI: POST /api/chat { "question": "..." }
    ChatAPI->>RAG: answer_question("Có tour Đà Nẵng...")
    
    RAG->>Analyzer: analyze_question(question)
    Analyzer-->>RAG: Structured Intent: { destinations: ["Đà Nẵng"], max_price: 4000000, duration_days: 3 }

    RAG->>Retriever: retrieve_tours(intent)
    Retriever->>DB: SELECT active tours with OPEN schedules and seats > 0
    DB-->>Retriever: strict matches
    Retriever-->>RAG: List[TourData]

    alt Không có strict match
        RAG->>Retriever: retrieve_alternative_tours(intent)
        Retriever->>DB: SELECT closest available tours
        DB-->>Retriever: alternatives or []
        Retriever-->>RAG: alternatives
    end

    RAG->>CtxBuilder: build_context(matches, alternatives)
    CtxBuilder-->>RAG: Context grounded in database rows
    RAG->>PromptBuilder: build_prompt(question, context)
    PromptBuilder-->>RAG: Grounded prompt
    RAG->>GroundedAnswerBuilder: build(question, intent, matches, alternatives)
    GroundedAnswerBuilder-->>RAG: fallback answer
    RAG->>Gemini: generate_content(prompt, fallback_answer)
    Gemini-->>RAG: grounded answer or fallback
    RAG->>DB: INSERT chat_logs (non-blocking audit log)
    RAG-->>ChatAPI: { "answer": "...", "tours": matches or alternatives }
    ChatAPI-->>UI: 200 OK (text + tour cards)
    UI-->>Customer: Hiển thị câu trả lời
```

---

## 4. Biểu đồ Hoạt động (Activity Diagram)

### Vòng đời Đặt tour - Thanh toán - Hủy tour
```mermaid
flowchart TD
    Start([Khách hàng duyệt danh sách Tour]) --> SelectSchedule[Chọn Lịch Khởi Hành]
    SelectSchedule --> InputInfo[Nhập thông tin khách & số lượng chỗ]
    InputInfo --> CheckSeats{Số chỗ còn đủ không?}
    
    CheckSeats -- Không --> NotifyFull[Thông báo hết chỗ / Đề xuất ngày khác]
    NotifyFull --> SelectSchedule
    
    CheckSeats -- Đủ chỗ --> LockSeats[Trừ số chỗ khả dụng trong CSDL]
    LockSeats --> CreateBooking[Tạo mã đơn Booking PENDING]
    CreateBooking --> ChoosePayment{Lựa chọn thanh toán}
    
    ChoosePayment --> PayOnline[Thanh toán mô phỏng / Chuyển khoản]
    ChoosePayment --> PayLater[Chờ thanh toán]
    
    PayOnline --> CheckPaymentSuccess{Thanh toán thành công?}
    CheckPaymentSuccess -- Thành công --> ConfirmBooking[Cập nhật trạng thái CONFIRMED]
    CheckPaymentSuccess -- Thất bại --> RemainPending[Giữ trạng thái PENDING]
    
    PayLater --> RemainPending
    RemainPending --> PayOnline
    
    ConfirmBooking --> TravelProcess[Khách hàng tham gia Tour du lịch]
    TravelProcess --> FinishTour[Hoàn thành tour COMPLETED]
    FinishTour --> SendFeedback[Gửi đánh giá & phản hồi chất lượng]
    SendFeedback --> End([Kết thúc])

    CreateBooking --> CustomerCancel{Khách yêu cầu Hủy tour?}
    ConfirmBooking --> CustomerCancel
    CustomerCancel -- Có --> UpdateCancelled[Cập nhật booking CANCELLED]
    UpdateCancelled --> ReleaseSeats[Cộng hoàn trả số chỗ và cập nhật lịch OPEN]
    ReleaseSeats --> CheckPaid{Đã có payment SUCCESS?}
    CheckPaid -- Không --> End
    CheckPaid -- Có --> CreateRefundRequest[Tạo refund_request PENDING bằng số tiền đã trả]
    CreateRefundRequest --> AccountantDecision{Kế toán/Admin duyệt?}
    AccountantDecision -- Từ chối --> RejectRefund[Lưu REJECTED và lý do]
    AccountantDecision -- Duyệt --> RecordRefund[Ghi payment REFUND với số tiền quyết định]
    RecordRefund --> ApproveRefund[Lưu APPROVED và thông tin xử lý]
    RejectRefund --> End
    ApproveRefund --> End
```

---

## 5. Biểu đồ Thực thể Liên kết (Entity-Relationship Diagram - ERD)

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : "places"
    USERS ||--o{ FEEDBACKS : "submits"
    USERS o|--o{ PAYMENTS : "verifies"
    USERS o|--o{ REFUND_REQUESTS : "processes"
    USERS o|--o{ TOUR_EXPENSES : "creates"
    DESTINATIONS ||--o{ TOURS : "contains"
    TOURS ||--o{ TOUR_SCHEDULES : "has"
    TOURS ||--o{ FEEDBACKS : "receives"
    TOUR_SCHEDULES ||--o{ BOOKINGS : "scheduled_in"
    TOUR_SCHEDULES ||--o{ GUIDE_ASSIGNMENTS : "assigned"
    TOUR_SCHEDULES ||--o{ TOUR_EXPENSES : "incurs"
    TOUR_GUIDES ||--o{ GUIDE_ASSIGNMENTS : "guides"
    BOOKINGS ||--o{ PAYMENTS : "paid_by"
    BOOKINGS ||--o| REFUND_REQUESTS : "has"
    BOOKINGS o|--o{ FEEDBACKS : "may_verify"

    USERS {
        int id PK
        string email UK
        string password_hash
        string full_name
        string phone
        string role "ADMIN, STAFF, ACCOUNTANT, GUIDE, CUSTOMER"
        datetime created_at
    }

    DESTINATIONS {
        int id PK
        string name UK
        string region
        text description
        string image_url
        datetime created_at
    }

    TOURS {
        int id PK
        int destination_id FK
        string title
        string slug UK
        text description
        int duration_days
        int duration_nights
        decimal base_price
        string transportation
        text itinerary_text
        string image_url
        boolean is_active
        datetime created_at
    }

    TOUR_SCHEDULES {
        int id PK
        int tour_id FK
        date departure_date
        date return_date
        decimal adult_price
        decimal child_price
        int total_seats
        int available_seats
        string status "OPEN, FULL, CLOSED, CANCELLED, POSTPONED"
        text postpone_reason
        datetime postponed_at
        datetime created_at
    }

    BOOKINGS {
        int id PK
        string booking_code UK
        int user_id FK
        int schedule_id FK
        string customer_name
        string customer_email
        string customer_phone
        int num_adults
        int num_children
        decimal total_amount
        string status "PENDING, CONFIRMED, COMPLETED, CANCELLED"
        text notes
        datetime created_at
    }

    PAYMENTS {
        int id PK
        int booking_id FK
        decimal amount
        string payment_method "CASH, BANK_TRANSFER, ONLINE"
        string payment_type "DEPOSIT, FULL, REMAINING, REFUND"
        string transaction_id
        string payment_status "PENDING, SUCCESS, FAILED, REFUNDED"
        datetime payment_date
        int verified_by FK
        datetime verified_at
        text notes
    }

    REFUND_REQUESTS {
        int id PK
        int booking_id FK, UK
        decimal paid_amount
        decimal request_amount
        text reason
        string status "PENDING, APPROVED, REJECTED"
        datetime requested_at
        int processed_by FK
        datetime processed_at
        decimal decision_amount
        text decision_notes
    }

    TOUR_GUIDES {
        int id PK
        string full_name
        string phone UK
        string email UK
        string languages
        int experience_years
        text bio
        boolean is_active
        datetime created_at
    }

    GUIDE_ASSIGNMENTS {
        int id PK
        int schedule_id FK
        int guide_id FK
        string role_in_tour "LEAD_GUIDE, ASSISTANT"
        string notes
        datetime created_at
    }

    FEEDBACKS {
        int id PK
        int user_id FK
        int tour_id FK
        int booking_id FK "nullable"
        int rating "1 to 5"
        text comment
        datetime created_at
    }

    CHAT_LOGS {
        int id PK
        string session_id
        text user_message
        text intent_json
        text retrieved_tour_ids
        text bot_response
        datetime created_at
    }

    TOUR_EXPENSES {
        int id PK
        int schedule_id FK
        string category "HOTEL, TRANSPORT, MEAL, TICKETS, GUIDE_FEE, OTHER"
        string title
        decimal amount
        string supplier_name
        string invoice_code
        date expense_date
        int created_by FK
        text notes
        datetime created_at
    }
```

