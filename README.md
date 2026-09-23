# TourAI - Hệ Thống Quản Lý Tour Du Lịch Tích Hợp AI (Đề Tài 17)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.sqlite.org/)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Google%20Gemini%20%7C%20RAG-purple.svg)](https://aistudio.google.com/)
[![Tests](https://img.shields.io/badge/Tests-20%2F20%20PASSED%20(100%25)-brightgreen.svg)](#-chạy-kiểm-thử-tự-động)

---

## 1. Giới thiệu Dự án
**TourAI** là giải pháp phần mềm quản trị du lịch lữ hành toàn diện kết hợp Trí tuệ Nhân tạo thế hệ mới (Đề tài 17). Hệ thống giải quyết trọn vẹn bài toán vận hành tour, đặt chỗ, kiểm soát số chỗ theo thời gian thực và tích hợp AI hỗ trợ khách hàng và nhân viên theo quy trình **AI-Augmented SDLC**.

### Các Tính Năng Nổi Bật:
1. **Quản Lý Tour & Điểm Đến:** Quản lý điểm đến, tour du lịch, lịch trình chi tiết và phương tiện di chuyển.
2. **Lịch Khởi Hành & Chống Overbooking Tuyệt Đối:** Kiểm soát số chỗ khả dụng bằng giao dịch nguyên tử (Atomic Database Transaction), ngăn chặn hoàn toàn việc bán vượt quá số chỗ trống khi có nhiều khách cùng đặt. Tự động hoàn lại chỗ khi đơn tour bị hủy.
3. **Trợ Lý AI Tư Vấn Tour (RAG Chatbot):**
   - Phân tích câu hỏi tự nhiên bằng tiếng Việt (ngân sách, số ngày, điểm đến, sở thích đi biển, leo núi, nghỉ dưỡng).
   - Truy vấn CSDL thực tế bằng Parameterized SQL an toàn.
   - **Chính sách Không Bịa Đặt Dữ Liệu (Zero Hallucination):** Chỉ gợi ý tour có thật và còn chỗ trong hệ thống. Nếu không có tour thỏa mãn, thông báo lịch sự không có tour thay vì tự bịa ra thông tin giả.
   - Hiển thị trực quan dưới dạng thẻ tour (Product Cards) kèm nút xem chi tiết và đặt chỗ ngay.
4. **Công Cụ AI Sinh Nội Dung Cho Nhân Viên:**
   - Tự động sinh mô tả tour chuẩn SEO và gợi ý lịch trình chi tiết theo ngày.
   - Tự động phân tích và tóm tắt toàn bộ phản hồi, đánh giá của khách hàng thành báo cáo chất lượng dịch vụ.
5. **Báo Cáo & Thống Kê:** Thống kê doanh thu, tỷ lệ lấp đầy chỗ (Occupancy Rate) của các đợt khởi hành và top tour bán chạy nhất.
6. **Bảo Mật Cao Cấp:** Băm mật khẩu bằng PBKDF2:SHA256, phân quyền 5 vai trò (Admin, Staff, Accountant, Guide, Customer), cô lập tuyệt đối API key và không cho LLM truy cập trực tiếp CSDL.

---

## 2. Cấu Trúc Thư Mục Dự Án

```text
TourAI/
├── .agents/
│   └── skills/                         # Hệ thống 13 Skills quy trình chuyên môn chuẩn hóa
│       ├── requirements-analysis/      # Skill 1: Phân tích yêu cầu phần mềm
│       ├── uml-design/                 # Skill 2: Thiết kế biểu đồ UML & bảng
│       ├── architecture-design/        # Skill 3: Thiết kế kiến trúc phân lớp & RAG
│       ├── database-design/            # Skill 4: Thiết kế CSDL 3NF, schema & index
│       ├── implementation/             # Skill 5: Quy chuẩn triển khai mã nguồn
│       ├── testing/                    # Skill 6: Quy trình lập kế hoạch & chạy test
│       ├── code-review/                # Skill 7: Kiểm thử chất lượng & tuân thủ kiến trúc
│       ├── security-review/            # Skill 8: Đánh giá an toàn thông tin & OWASP
│       ├── question-analysis/          # Skill 9: Bóc tách intent câu hỏi tiếng Việt
│       ├── tour-retrieval/             # Skill 10: Truy xuất tour an toàn (parameterized SQL)
│       ├── product-retrieval/          # Skill 10 (alias): Truy xuất sản phẩm tour
│       ├── context-builder/            # Skill 11: Nén & chuẩn hóa context CSDL
│       ├── rag-prompt/                 # Skill 12: Prompt engineering cấm ảo giác
│       └── documentation/              # Skill 13: Đồng bộ tài liệu kỹ thuật
│
├── docs/                               # Toàn bộ tài liệu quy trình AI-Augmented SDLC
│   ├── customer-requirement.md         # Yêu cầu khách hàng ban đầu (Đề tài 17)
│   ├── requirements.md                 # Đặc tả yêu cầu FR-001..FR-025 & NFR-001..NFR-008
│   ├── user-stories.md                 # Danh sách User Stories & Ma trận truy xuất
│   ├── acceptance-criteria.md          # Tiêu chí chấp nhận Gherkin (Given-When-Then)
│   ├── requirements-issues.md          # Phân tích điểm mơ hồ & Biên bản Human Gate 1
│   ├── uml-diagrams.md                 # Biểu đồ Use Case, Class, Sequence, Activity, ERD
│   ├── architecture.md                 # Thiết kế kiến trúc phân lớp & RAG Pipeline
│   ├── architecture-decisions.md       # Các quyết định kiến trúc quan trọng (ADR-001..005)
│   ├── database-design.md              # Thiết kế CSDL chi tiết chuẩn 3NF
│   ├── test-plan.md                    # Kế hoạch kiểm thử toàn diện
│   ├── test-report.md                  # Báo cáo kết quả kiểm thử tự động (20/20 PASS)
│   ├── code-review.md                  # Báo cáo đánh giá mã nguồn & phân loại lỗi
│   ├── security-review.md              # Báo cáo đánh giá an toàn thông tin & lỗ hổng
│   ├── chatbot-requirements.md         # Yêu cầu chuyên biệt cho Chatbot AI
│   ├── chatbot-functional-requirements.md # Yêu cầu chức năng Chatbot
│   ├── chatbot-user-stories.md         # User stories của Chatbot
│   ├── chatbot-acceptance-criteria.md  # Tiêu chí chấp nhận Chatbot
│   ├── chatbot-requirements-issues.md  # Vấn đề & giả định của Chatbot
│   ├── chatbot-architecture.md         # Kiến trúc chi tiết của Chatbot RAG
│   ├── chatbot-data-flow.md            # Sơ đồ và ví dụ luồng dữ liệu 7 bước
│   ├── question-analysis.md            # Đặc tả bóc tách Structured Intent
│   ├── api.md                          # Tài liệu RESTful API endpoints
│   ├── deployment.md                   # Hướng dẫn triển khai Production
│   └── user-guide.md                   # Hướng dẫn sử dụng cho Khách hàng & Nhân viên
│
├── database/
│   ├── schema.sql                      # Schema DDL (MySQL 8 & SQLite)
│   ├── db.py                           # Database Manager & Connection Pool
│   └── seeder.py                       # Seeder dữ liệu mẫu phong phú
│
├── models/                             # Data Access & Entity Definitions
├── routes/                             # Flask Blueprints (Controllers)
│   ├── auth_routes.py                  # Đăng ký, đăng nhập, phân quyền RBAC
│   ├── tour_routes.py                  # Trang chủ, danh mục, lọc & chi tiết tour
│   ├── booking_routes.py               # Đặt chỗ, thanh toán, hủy đơn
│   ├── feedback_routes.py              # Đánh giá sau chuyến đi
│   ├── admin_routes.py                 # Dashboard thống kê, CRUD tour & lịch trình
│   ├── chat_routes.py                  # API Chatbot (POST /api/chat)
│   └── ai_tools_routes.py              # Công cụ AI sinh nội dung & tóm tắt phản hồi
│
├── services/                           # Business Logic & AI Services
│   ├── auth_service.py                 # Xác thực & mã hóa mật khẩu
│   ├── tour_service.py                 # Nghiệp vụ tour, điểm đến & lịch khởi hành
│   ├── booking_service.py              # Xử lý đặt chỗ & khóa nguyên tử chống overbooking
│   ├── payment_service.py              # Ghi nhận thanh toán & đặt cọc
│   ├── feedback_service.py             # Quản lý đánh giá sao & nhận xét
│   ├── analytics_service.py            # Doanh thu, tỷ lệ lấp đầy, top tour
│   ├── question_analyzer.py            # Bóc tách intent tiếng Việt
│   ├── tour_retriever.py               # Truy vấn CSDL tour còn chỗ an toàn
│   ├── context_builder.py              # Chuẩn hóa context ngắn gọn cho LLM
│   ├── prompt_builder.py               # Xây dựng prompt kèm quy tắc Zero-Hallucination
│   ├── gemini_service.py               # Gọi Gemini API an toàn kèm fallback
│   ├── rag_service.py                  # Điều phối toàn trình RAG
│   └── ai_content_service.py           # Sinh mô tả tour & tóm tắt phản hồi
│
├── templates/                          # Giao diện HTML5 Jinja2 hiện đại
│   ├── base.html                       # Layout khung chuẩn, navbar & footer
│   ├── index.html                      # Trang chủ hấp dẫn, danh mục điểm đến
│   ├── tours.html                      # Danh sách tour kèm bộ lọc đa tiêu chí
│   ├── tour_detail.html                # Chi tiết tour, lịch trình, bảng đợt khởi hành
│   ├── booking.html                    # Form đặt tour & tính tiền tự động
│   ├── booking_success.html            # Hóa đơn xác nhận & thanh toán mô phỏng
│   ├── my_bookings.html                # Quản lý đơn cá nhân & chức năng hủy tour
│   ├── login.html                      # Đăng nhập hệ thống
│   ├── register.html                   # Đăng ký tài khoản
│   ├── chatbot.html                    # Giao diện Chatbot AI hiện đại, Tour Cards
│   ├── 404.html & 500.html             # Trang thông báo lỗi thân thiện
│   └── admin/                          # Giao diện Quản trị
│       ├── dashboard.html              # Báo cáo thống kê, biểu đồ lấp đầy
│       ├── tours_manage.html           # Quản lý tour kèm nút AI sinh mô tả
│       ├── schedules_manage.html       # Quản lý lịch khởi hành & chỗ trống
│       ├── bookings_manage.html        # Quản lý trạng thái đơn đặt chỗ
│       └── feedbacks_manage.html       # Quản lý đánh giá kèm nút AI tóm tắt
│
├── static/
│   ├── css/
│   │   ├── style.css                   # Định kiểu giao diện toàn trang
│   │   └── chat.css                    # Định kiểu Chatbot, gradient header, cards
│   └── js/
│       ├── main.js                     # Tiện ích chung
│       └── chat.js                     # Xử lý fetch API chat, render cards, loading
│
├── tests/                              # Bộ kiểm thử tự động (Pytest)
│   ├── conftest.py                     # Cấu hình test database cô lập
│   ├── test_auth.py                    # Kiểm thử xác thực & băm mật khẩu
│   ├── test_booking_capacity.py        # Kiểm thử chống Overbooking & hoàn trả chỗ
│   ├── test_question_analyzer.py       # Kiểm thử bóc tách ngân sách & điểm đến
│   ├── test_tour_retrieval.py          # Kiểm thử truy xuất tour & không bịa dữ liệu
│   ├── test_context_builder.py         # Kiểm thử tạo ngữ cảnh CSDL
│   └── test_rag_pipeline.py            # Kiểm thử toàn trình RAG & API POST /api/chat
│
├── app.py                              # Entry Point & Application Factory
├── requirements.txt                    # Danh sách thư viện Python
├── .env.example                        # Mẫu cấu hình biến môi trường
└── .gitignore                          # Cấu hình bỏ qua file nhạy cảm và CSDL
```

---

## 3. Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 3.1 Yêu cầu hệ thống
- Python 3.10 trở lên
- Git

### 3.2 Các bước cài đặt
1. **Clone repository và mở thư mục dự án:**
   ```bash
   cd f:\TourAI
   ```

2. **Cài đặt các thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình biến môi trường:**
   Tạo file `.env` từ file mẫu `.env.example`:
   ```bash
   copy .env.example .env
   ```
   *(Tùy chọn: Nhập `GEMINI_API_KEY` từ Google AI Studio nếu muốn gọi trực tiếp Google Gemini API. Nếu chưa có API key, hệ thống tự động kích hoạt chế độ Thông Minh Fallback để phục vụ đầy đủ mọi chức năng).*

4. **Khởi tạo và Seed cơ sở dữ liệu mẫu:**
   ```bash
   python database/seeder.py
   ```

---

## 4. 🧪 Chạy Kiểm Thử Tự Động (Automated Tests)
Chạy toàn bộ bộ test kiểm tra tính đúng đắn, phòng chống Overbooking và Zero-Hallucination:
```bash
python -m pytest -v
```
**Kết quả mong đợi:** 20/20 tests `PASSED` 100%.

---

## 5. 🚀 Khởi Chạy Ứng Dụng Web
Khởi động máy chủ phát triển Flask:
```bash
python app.py
```
Mở trình duyệt và truy cập:
👉 **http://127.0.0.1:5000**

---

## 6. Danh Sách Tài Khoản Dùng Thử Có Sẵn

| Vai trò | Email đăng nhập | Mật khẩu | Quyền hạn |
|---|---|---|---|
| **Quản trị viên (Admin)** | `admin@tourai.vn` | `admin123` | Toàn quyền quản trị, xem doanh thu, xóa tour, quản lý lịch khởi hành |
| **Nhân viên tư vấn (Staff)** | `staff@tourai.vn` | `staff123` | Quản lý tour, mở lịch khởi hành, dùng AI sinh mô tả & tóm tắt phản hồi |
| **Kế toán (Accountant)** | `accountant@tourai.vn` | `accountant123` | Xác nhận thanh toán, theo dõi công nợ, xem báo cáo doanh thu |
| **Hướng dẫn viên (Guide)** | `guide@tourai.vn` | `guide123` | Xem lịch trình dẫn tour được phân công |
| **Khách hàng (Customer)** | `customer@tourai.vn` | `customer123` | Tìm kiếm tour, đặt tour, trò chuyện với Chatbot, hủy đơn, gửi đánh giá |

---

## 7. Các Câu Hỏi Mẫu Thử Nghiệm Chatbot RAG AI
Truy cập trang Chatbot tại **http://127.0.0.1:5000/chat** và thử nghiệm:
- *"Có tour Hạ Long nào dưới 4 triệu không?"* &rarr; Gợi ý Tour Hạ Long 3.200.000 VNĐ kèm thẻ tour.
- *"Tôi có khoảng 5 triệu, muốn đi biển 3-4 ngày thì có tour nào?"* &rarr; Gợi ý Tour Phú Quốc và Đà Nẵng còn chỗ.
- *"Tour Sa Pa leo núi Fansipan còn chỗ không?"* &rarr; Báo số chỗ còn của tour Sa Pa.
- *"Có tour Đà Lạt nào dưới 100 nghìn không?"* &rarr; **Kiểm tra Zero Hallucination**: Chatbot thông báo lịch sự không có tour nào giá dưới 100k, tuyệt đối không bịa tour giả!

#   H e _ t h o n g _ Q L _ t o u r _ c o _ t i c h _ h o p _ A I  
 #   T o u r _ A I  
 