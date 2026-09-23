# Tài Liệu Thiết Kế Biểu Đồ & Bảng UML (UML Diagrams Specification)

Tài liệu này được tạo dựa trên `uml-design` skill, mô hình hóa toàn diện hệ thống quản lý tour du lịch tích hợp AI (Đề tài 17) bao gồm: Use Case Diagram, Class Diagram, Sequence Diagrams, Activity Diagrams và Entity-Relationship Diagram (ERD).

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
        UC1["Đăng ký & Đăng nhập"]
        UC2["Quản lý thông tin cá nhân"]
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
    Customer --> UC1
    Customer --> UC2
    Customer --> UC3
    Customer --> UC7
    Customer --> UC8
    Customer --> UC9
    Customer --> UC12
    Customer --> UC15

    Staff --> UC1
    Staff --> UC4
    Staff --> UC5
    Staff --> UC6
    Staff --> UC7
    Staff --> UC13

    Accountant --> UC1
    Accountant --> UC8
    Accountant --> UC9
    Accountant --> UC14

    Guide --> UC1
    Guide --> UC11

    Admin --> UC1
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
    Admin --> UC13
    Admin --> UC14

    UC6 -.-> AI
    UC13 -.-> AI
    UC15 -.-> AI
```

### 1.2 Bảng mô tả chi tiết các Use Case chính

| Mã Use Case | Tên Use Case | Tác nhân chính | Tiền điều kiện | Hậu điều kiện |
|---|---|---|---|---|
| `UC-01` | Đặt chỗ tour (Booking) | Khách hàng | Khách đã chọn đợt khởi hành còn chỗ (`available_seats > 0`) | Tạo bản ghi booking, giảm số chỗ trống tương ứng |
| `UC-02` | Hủy đặt chỗ (Cancel Booking) | Khách hàng / Kế toán | Đơn đặt chỗ ở trạng thái PENDING hoặc CONFIRMED | Đơn chuyển CANCELLED, hoàn trả số chỗ về lịch trình |
| `UC-03` | Chatbot tư vấn tour (RAG) | Khách hàng | Người dùng nhập câu hỏi tự nhiên | Chatbot trả lời thông tin chính xác từ CSDL, không bịa |
| `UC-04` | AI sinh mô tả tour | Nhân viên / Admin | Nhân viên nhập điểm đến, từ khóa | AI sinh đoạn văn mô tả chuẩn SEO và lịch trình chi tiết |
| `UC-05` | AI tóm tắt phản hồi | Admin / Quản lý | Đã có các phản hồi đánh giá trong CSDL | AI sinh báo cáo tổng hợp ưu/nhược điểm dịch vụ |

---

## 2. Biểu đồ Lớp (Class Diagram)

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
        +check_password(password) bool
    }

    class Destination {
        +int id
        +string name
        +string region
        +string description
        +string image_url
        +datetime created_at
    }

    class Tour {
        +int id
        +int destination_id
        +string title
        +string slug
        +string description
        +int duration_days
        +int duration_nights
        +float base_price
        +string transportation
        +string itinerary_text
        +string image_url
        +bool is_active
    }

    class TourSchedule {
        +int id
        +int tour_id
        +date departure_date
        +date return_date
        +float adult_price
        +float child_price
        +int total_seats
        +int available_seats
        +string status
        +has_enough_seats(seats) bool
        +reserve_seats(seats) void
        +release_seats(seats) void
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
        +float total_amount
        +string status
        +string notes
        +datetime created_at
    }

    class Payment {
        +int id
        +int booking_id
        +float amount
        +string payment_method
        +string transaction_id
        +string payment_status
        +datetime payment_date
    }

    class TourGuide {
        +int id
        +string full_name
        +string phone
        +string email
        +string languages
        +int experience_years
        +string bio
        +bool is_active
    }

    class GuideAssignment {
        +int id
        +int schedule_id
        +int guide_id
        +string role_in_tour
        +string notes
    }

    class Feedback {
        +int id
        +int user_id
        +int tour_id
        +int booking_id
        +int rating
        +string comment
        +datetime created_at
    }

    class ChatLog {
        +int id
        +string session_id
        +string user_message
        +string intent_json
        +string retrieved_tour_ids
        +string bot_response
        +datetime created_at
    }

    Destination "1" --> "*" Tour : contains
    Tour "1" --> "*" TourSchedule : schedules
    TourSchedule "1" --> "*" Booking : booked_in
    User "1" --> "*" Booking : places
    Booking "1" --> "*" Payment : payments
    TourSchedule "1" --> "*" GuideAssignment : assigns
    TourGuide "1" --> "*" GuideAssignment : assigned_to
    Tour "1" --> "*" Feedback : reviews
    User "1" --> "*" Feedback : writes
    Booking "1" --> "0..1" Feedback : relates_to
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
    participant SchedRepo as 💾 ScheduleRepository
    participant BookRepo as 💾 BookingRepository
    participant DB as 🗄️ MySQL Database

    Customer->>Route: POST /bookings (schedule_id, num_adults, num_children, contact_info)
    Route->>Service: create_booking(user_id, schedule_id, adults, children, contact)
    Service->>SchedRepo: get_schedule_for_update(schedule_id)
    SchedRepo->>DB: SELECT * FROM tour_schedules WHERE id = ? FOR UPDATE
    DB-->>SchedRepo: schedule record (available_seats)

    alt available_seats < (num_adults + num_children)
        Service-->>Route: Raise OverbookingError("Không đủ số chỗ khả dụng")
        Route-->>Customer: 400 Bad Request ("Chuyến đi chỉ còn X chỗ")
    else available_seats >= requested_seats
        Service->>SchedRepo: update available_seats = available_seats - requested_seats
        SchedRepo->>DB: UPDATE tour_schedules SET available_seats = ...
        Service->>BookRepo: insert_booking(booking_data)
        BookRepo->>DB: INSERT INTO bookings ...
        DB-->>BookRepo: Booking Created (BK-XXXXX)
        Service-->>Route: Return Booking Object
        Route-->>Customer: 201 Created (Chuyển hướng trang xác nhận & thanh toán)
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
    participant DB as 🗄️ MySQL Database
    participant CtxBuilder as 📝 ContextBuilder
    participant PromptBuilder as 📄 PromptBuilder
    participant Gemini as 🤖 GeminiService

    Customer->>UI: Nhập: "Có tour Đà Nẵng 3 ngày dưới 4 triệu không?"
    UI->>ChatAPI: POST /api/chat { "question": "..." }
    ChatAPI->>RAG: answer_question("Có tour Đà Nẵng...")
    
    RAG->>Analyzer: analyze_question(question)
    Analyzer-->>RAG: Structured Intent: { destination: "Đà Nẵng", max_price: 4000000, duration: 3 }

    RAG->>Retriever: retrieve_tours(intent)
    Retriever->>DB: SELECT * FROM tours JOIN tour_schedules WHERE ... AND available_seats > 0
    DB-->>Retriever: [Tour "Đà Nẵng - Hội An 3N2Đ", Giá: 3.500.000, Còn: 8 chỗ]
    Retriever-->>RAG: List[TourData]

    alt Không có tour nào phù hợp (Empty List)
        RAG-->>ChatAPI: "Hiện tại không tìm thấy tour phù hợp với yêu cầu của bạn..."
        ChatAPI-->>UI: Hiển thị thông báo không có tour và gợi ý xem các tour khác
    else Tìm thấy tour
        RAG->>CtxBuilder: build_context(tours)
        CtxBuilder-->>RAG: Context Text (Danh sách tour chuẩn hóa từ CSDL)
        RAG->>PromptBuilder: build_prompt(question, context)
        PromptBuilder-->>RAG: Grounded Prompt (Cấm bịa dữ liệu)
        RAG->>Gemini: generate_content(prompt)
        Gemini-->>RAG: Câu trả lời tư vấn chi tiết
        RAG-->>ChatAPI: { "answer": "...", "tours": [...] }
        ChatAPI-->>UI: 200 OK (Render văn bản + Thẻ Tour Cards)
        UI-->>Customer: Hiển thị câu trả lời và thẻ tour trực quan
    end
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
    
    ChoosePayment --> PayOnline[Thanh toán Online / Chuyển khoản]
    ChoosePayment --> PayLater[Giữ chỗ thanh toán sau]
    
    PayOnline --> CheckPaymentSuccess{Thanh toán thành công?}
    CheckPaymentSuccess -- Thành công --> ConfirmBooking[Cập nhật trạng thái CONFIRMED]
    CheckPaymentSuccess -- Thất bại / Quá hạn --> CancelPending[Hủy đơn quá hạn & Hoàn trả số chỗ]
    
    PayLater --> ConfirmBooking
    
    ConfirmBooking --> TravelProcess[Khách hàng tham gia Tour du lịch]
    TravelProcess --> FinishTour[Hoàn thành tour COMPLETED]
    FinishTour --> SendFeedback[Gửi đánh giá & phản hồi chất lượng]
    SendFeedback --> End([Kết thúc])

    ConfirmBooking --> CustomerCancel{Khách yêu cầu Hủy tour?}
    CustomerCancel -- Có --> ApplyPolicy[Áp dụng chính sách hoàn hủy]
    ApplyPolicy --> ReleaseSeats[Cộng hoàn trả số chỗ vào Lịch trình]
    ReleaseSeats --> UpdateCancelled[Cập nhật trạng thái CANCELLED]
    UpdateCancelled --> End
```

---

## 5. Biểu đồ Thực thể Liên kết (Entity-Relationship Diagram - ERD)

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : "places"
    USERS ||--o{ FEEDBACKS : "submits"
    DESTINATIONS ||--o{ TOURS : "contains"
    TOURS ||--o{ TOUR_SCHEDULES : "has"
    TOURS ||--o{ FEEDBACKS : "receives"
    TOUR_SCHEDULES ||--o{ BOOKINGS : "scheduled_in"
    TOUR_SCHEDULES ||--o{ GUIDE_ASSIGNMENTS : "assigned"
    TOUR_GUIDES ||--o{ GUIDE_ASSIGNMENTS : "guides"
    BOOKINGS ||--o{ PAYMENTS : "paid_by"
    BOOKINGS ||--o| FEEDBACKS : "verified_for"

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
        string region "Bắc, Trung, Nam, Quốc tế"
        string description
        string image_url
        datetime created_at
    }

    TOURS {
        int id PK
        int destination_id FK
        string title
        string slug UK
        string description
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
        string status "OPEN, FULL, CLOSED, CANCELLED"
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
        string transaction_id
        string payment_status "PENDING, SUCCESS, FAILED, REFUNDED"
        datetime payment_date
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
        int booking_id FK
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
```

