# TourAI - Hệ Thống Quản Lý Tour Du Lịch Tích Hợp AI (Đề Tài 17)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-MySQL%20%7C%20SQLite-orange.svg)](https://www.sqlite.org/)
[![AI Engine](https://img.shields.io/badge/AI%20Engine-Google%20Gemini%20%7C%20RAG-purple.svg)](https://aistudio.google.com/)
[![Tests](https://img.shields.io/badge/Tests-60%2F60%20PASSED%20(100%25)-brightgreen.svg)](#-chạy-kiểm-thử-tự-động)

---

## 1. Giới thiệu Dự án
**TourAI** là giải pháp phần mềm quản trị du lịch lữ hành toàn diện kết hợp Trí tuệ Nhân tạo thế hệ mới (Đề tài 17). Hệ thống giải quyết trọn vẹn bài toán vận hành tour, đặt chỗ, kiểm soát số chỗ theo thời gian thực và tích hợp AI hỗ trợ khách hàng và nhân viên theo quy trình **AI-Augmented SDLC**.

### Các Tính Năng Nổi Bật:
1. **Quản Lý Tour & Điểm Đến:** Quản lý điểm đến, tour du lịch, lịch trình chi tiết và phương tiện di chuyển. Hỗ trợ thêm ảnh đại diện bằng cách **chọn file, dán ảnh trực tiếp (Ctrl+V)** hoặc nhập URL.
2. **Lịch Khởi Hành & Chống Overbooking Tuyệt Đối:** Kiểm soát số chỗ khả dụng bằng giao dịch nguyên tử (Atomic Database Transaction), ngăn chặn hoàn toàn việc bán vượt quá số chỗ trống khi có nhiều khách cùng đặt. Tự động hoàn lại chỗ khi đơn tour bị hủy. **Giá vé đợt khởi hành được liên kết tự động với giá tour** (tự điền khi mở đợt, đồng bộ khi sửa giá tour) để tránh dữ liệu lệch.
3. **Trợ Lý AI Tư Vấn Tour (RAG Chatbot):**
   - Phân tích câu hỏi tự nhiên bằng tiếng Việt (ngân sách, số ngày, điểm đến, sở thích đi biển, leo núi, nghỉ dưỡng).
   - Truy vấn CSDL thực tế bằng Parameterized SQL an toàn.
   - **Chính sách Không Bịa Đặt Dữ Liệu (Zero Hallucination):** Chỉ gợi ý tour có thật và còn chỗ trong hệ thống. Nếu không có tour thỏa mãn, thông báo lịch sự không có tour thay vì tự bịa ra thông tin giả.
   - Hiển thị trực quan dưới dạng thẻ tour (Product Cards) kèm nút xem chi tiết và đặt chỗ ngay.
4. **Công Cụ AI Sinh Nội Dung Cho Nhân Viên:**
   - Tự động sinh mô tả tour chuẩn SEO và gợi ý lịch trình chi tiết theo ngày.
   - Tự động phân tích và tóm tắt toàn bộ phản hồi, đánh giá của khách hàng thành báo cáo chất lượng dịch vụ.
5. **Phân Hệ Kế Toán & Tài Chính Toàn Diện (4 Trụ Cột):**
   - **Thu & Công Nợ Khách Hàng:** Đặt cọc, thanh toán nhiều đợt, duyệt giao dịch chuyển khoản, theo dõi công nợ còn lại.
   - **Chi Phí Vận Hành Tour:** Ghi nhận chi phí xe, khách sạn, nhà hàng, vé tham quan, thù lao HDV theo từng lịch khởi hành.
   - **Hoàn Tiền Hủy Tour:** Tính tỷ lệ hoàn tiền theo chính sách (90% / 50% / 0%) và lập phiếu chi hoàn tiền.
   - **Báo Cáo Tài Chính:** P&L từng đoàn tour (Doanh thu − Chi phí = Lợi nhuận gộp, kèm Margin %) và Sổ quỹ Thu/Chi.
6. **Báo Cáo & Thống Kê:** Thống kê doanh thu, tỷ lệ lấp đầy chỗ (Occupancy Rate) của các đợt khởi hành và top tour bán chạy nhất.
7. **Phân Hệ Quản Trị & Phân Công Hướng Dẫn Viên:** CRUD Điểm đến, Tour, Lịch khởi hành, Khách hàng và Hướng dẫn viên; phân công HDV theo từng lịch khởi hành; phân quyền chi tiết từng thao tác (ví dụ: STAFF chỉ xem khách hàng, chỉ ADMIN được xóa tour/điểm đến). HDV xem bảng phân công dẫn tour tại `/guide/schedule`.
8. **Bảo Mật Cao Cấp:** Băm mật khẩu bằng PBKDF2:SHA256, phân quyền 5 vai trò (Admin, Staff, Accountant, Guide, Customer), cô lập tuyệt đối API key và không cho LLM truy cập trực tiếp CSDL.

---

## 2. Cấu Trúc Thư Mục Dự Án

```text
TourAI/
├── .agents/
│   └── skills/                         # Hệ thống 14 Skills quy trình chuyên môn chuẩn hóa
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
│   ├── functional-requirements.md      # Yêu cầu chức năng chi tiết theo từng phân hệ
│   ├── user-stories.md                 # Danh sách User Stories & Ma trận truy xuất
│   ├── acceptance-criteria.md          # Tiêu chí chấp nhận Gherkin (Given-When-Then)
│   ├── requirements-issues.md          # Phân tích điểm mơ hồ & Biên bản Human Gate 1
│   ├── uml-diagrams.md                 # Biểu đồ Use Case, Class, Sequence, Activity, ERD
│   ├── architecture.md                 # Thiết kế kiến trúc phân lớp & RAG Pipeline
│   ├── architecture-decisions.md       # Các quyết định kiến trúc quan trọng (ADR-001..005)
│   ├── database-design.md              # Thiết kế CSDL chi tiết chuẩn 3NF
│   ├── test-plan.md                    # Kế hoạch kiểm thử toàn diện
│   ├── test-report.md                  # Báo cáo kết quả kiểm thử tự động
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
│   ├── schema.sql                      # Schema DDL (MySQL 8 & SQLite), gồm bảng tour_expenses
│   ├── db.py                           # Database Manager, execute_query & migration tương thích
│   └── seeder.py                       # Seeder dữ liệu mẫu (chỉ chạy khi cần demo)
│
├── routes/                             # Flask Blueprints (Controllers)
│   ├── auth_routes.py                  # Đăng ký, đăng nhập, phân quyền RBAC
│   ├── tour_routes.py                  # Trang chủ, danh mục, lọc & chi tiết tour
│   ├── booking_routes.py               # Đặt chỗ, thanh toán, hủy đơn
│   ├── feedback_routes.py              # Đánh giá sau chuyến đi
│   ├── admin_routes.py                 # Dashboard, CRUD tour, điểm đến, khách hàng, HDV
│   ├── guide_routes.py                 # Phân hệ HDV: bảng phân công dẫn tour (/guide/schedule)
│   ├── accounting_routes.py            # Phân hệ kế toán: thu/chi, công nợ, P&L, hoàn tiền
│   ├── chat_routes.py                  # API Chatbot (POST /api/chat)
│   └── ai_tools_routes.py              # Công cụ AI sinh nội dung & tóm tắt phản hồi
│
├── services/                           # Business Logic & AI Services
│   ├── auth_service.py                 # Xác thực & mã hóa mật khẩu
│   ├── tour_service.py                 # Nghiệp vụ tour, điểm đến, lịch khởi hành & sync giá đợt theo giá tour
│   ├── booking_service.py              # Xử lý đặt chỗ & khóa nguyên tử chống overbooking
│   ├── payment_service.py              # Ghi nhận thanh toán & đặt cọc
│   ├── accounting_service.py           # Nghiệp vụ kế toán: đối soát, công nợ, chi phí, P&L, sổ quỹ
│   ├── feedback_service.py             # Quản lý đánh giá sao & nhận xét
│   ├── analytics_service.py            # Doanh thu, tỷ lệ lấp đầy, top tour
│   ├── guide_service.py                # Phân công HDV theo lịch khởi hành
│   ├── image_upload_service.py         # Upload ảnh admin: validate & lưu static/uploads
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
│   ├── admin/                          # Giao diện Quản trị
│   │   ├── dashboard.html              # Báo cáo thống kê, biểu đồ lấp đầy
│   │   ├── tours_manage.html           # Quản lý tour kèm nút AI sinh mô tả
│   │   ├── tour_edit.html              # Thêm/sửa chi tiết tour
│   │   ├── schedules_manage.html       # Quản lý lịch khởi hành & chỗ trống
│   │   ├── schedule_edit.html          # Thêm/sửa lịch khởi hành
│   │   ├── destinations_manage.html    # Quản lý điểm đến
│   │   ├── destination_edit.html       # Thêm/sửa điểm đến
│   │   ├── bookings_manage.html        # Quản lý trạng thái đơn đặt chỗ
│   │   ├── customers_manage.html       # Quản lý khách hàng (ADMIN thêm/sửa/xóa, STAFF chỉ xem)
│   │   ├── guides_manage.html          # Quản lý HDV & phân công theo lịch khởi hành
│   │   └── feedbacks_manage.html       # Quản lý đánh giá kèm nút AI tóm tắt
│   ├── guide/
│   │   └── schedule.html               # Bảng phân công dẫn tour của HDV
│   ├── partials/
│   │   ├── manage_menu.html            # Menu điều khiển chung cho các trang quản trị
│   │   └── image_field.html            # Ô upload/dán ảnh (Ctrl+V) dùng chung cho form admin
│   └── accounting/                     # Giao diện Phân hệ Kế toán
│       ├── dashboard.html              # Dashboard tài chính (thu, chi, tồn quỹ, công nợ)
│       ├── transactions.html           # Sổ quỹ thu & đối soát chuyển khoản
│       ├── expenses.html               # Kê chi phí vận hành & form thêm khoản chi
│       ├── debts.html                  # Quản lý công nợ & thu nợ nhiều đợt
│       ├── pnl_report.html             # Báo cáo lãi lỗ theo đoàn tour
│       └── refunds.html                # Lập phiếu chi hoàn tiền khi hủy tour
│
├── static/
│   ├── css/
│   │   ├── style.css                   # Định kiểu giao diện toàn trang
│   │   └── chat.css                    # Định kiểu Chatbot, gradient header, cards
│   └── js/
│       └── chat.js                     # Xử lý fetch API chat, render cards, loading
│
├── tests/                              # Bộ kiểm thử tự động (Pytest)
│   ├── conftest.py                     # Cấu hình test database cô lập
│   ├── test_auth.py                    # Kiểm thử xác thực, băm mật khẩu & đăng nhập nhanh (6)
│   ├── test_rbac.py                    # Kiểm thử phân quyền 5 vai trò trên mọi route (20)
│   ├── test_booking_capacity.py        # Kiểm thử chống Overbooking & hoàn trả chỗ (5)
│   ├── test_question_analyzer.py       # Kiểm thử bóc tách ngân sách & điểm đến (5)
│   ├── test_rag_pipeline.py            # Kiểm thử toàn trình RAG & API POST /api/chat (4)
│   ├── test_tour_retrieval.py          # Kiểm thử truy xuất tour & không bịa dữ liệu (3)
│   ├── test_context_builder.py         # Kiểm thử tạo ngữ cảnh CSDL (2)
│   ├── test_image_upload.py            # Kiểm thử upload ảnh: hợp lệ, sai định dạng, RBAC (5)
│   ├── test_price_consistency.py       # Kiểm thử liên kết giá vé & tên tour giữa các bảng (4)
│   └── test_accounting.py              # Kiểm thử kế toán: duyệt thu, công nợ, chi phí, P&L (6)
│
├── scripts/
│   ├── check_rbac_live.py              # Kiểm tra RBAC trực tiếp trên server đang chạy
│   └── purge_demo_data.py              # Xóa dữ liệu demo, giữ tài khoản & dữ liệu thật
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
   git clone https://github.com/dtc245220010ictu/Tour_AI.git
   cd Tour_AI
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

4. **Khởi tạo cơ sở dữ liệu:**
   Bảng được tự tạo tự động khi chạy app (schema.sql). Hệ thống **không tự nạp dữ liệu demo** theo mặc định — chỉ có dữ liệu thật bạn tạo.
   - *(Tùy chọn)* Nạp dữ liệu mẫu để demo/test:
     ```bash
     python database/seeder.py
     ```
   - *(Tùy chọn)* Xóa dữ liệu demo đã nạp, giữ nguyên tài khoản & dữ liệu thật:
     ```bash
     python scripts/purge_demo_data.py
     ```
   - Biến môi trường `SEED_DEMO_DATA=1` trong `.env` sẽ tự nạp dữ liệu demo khi khởi động app (mặc định `0`).

---

## 4. 🧪 Chạy Kiểm Thử Tự Động (Automated Tests)
Chạy toàn bộ bộ test kiểm tra tính đúng đắn, phòng chống Overbooking và Zero-Hallucination:
```bash
python -m pytest -v
```
**Kết quả mong đợi:** 60/60 tests `PASSED` 100%.
*(Phân bổ theo file: RBAC 20 · Auth 6 · Kế toán 6 · Chống overbooking 5 · Bóc tách câu hỏi 5 · RAG pipeline 4 · Truy xuất tour 3 · Upload ảnh 5 · Liên kết dữ liệu 4 · Context builder 2.)*

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
| **Nhân viên tư vấn (Staff)** | `staff@tourai.vn` | `staff123` | Quản lý tour, điểm đến, lịch khởi hành, khách hàng & đặt chỗ, dùng AI sinh mô tả (không có quyền xóa tour, thống kê, tài chính, phản hồi) |
| **Kế toán (Accountant)** | `accountant@tourai.vn` | `accountant123` | Duyệt thanh toán, theo dõi công nợ, ghi chi phí tour, xem báo cáo P&L, lập phiếu chi hoàn tiền |
| **Hướng dẫn viên (Guide)** | `guide@tourai.vn` | `guide123` | Xem lịch trình dẫn tour được phân công |
| **Khách hàng (Customer)** | `customer@tourai.vn` | `customer123` | Tìm kiếm tour, đặt tour, trò chuyện với Chatbot, hủy đơn, gửi đánh giá |

> ⚡ **Đăng nhập nhanh (Quick Login):** Tại trang **http://127.0.0.1:5000/login** có sẵn khu vực **"Đăng nhập nhanh (Demo)"** — chỉ cần bấm vào vai trò (Quản trị / Nhân viên / **Kế toán** / Hướng dẫn viên / Khách hàng) là đăng nhập ngay, không cần gõ tài khoản & mật khẩu. Tính năng này phục vụ kiểm thử/học tập và có thể tắt bằng biến môi trường `ENABLE_DEMO_QUICK_LOGIN=0`.

> 🧹 **Dữ liệu demo:** Hệ thống mặc định **không tự seed dữ liệu mẫu** (`SEED_DEMO_DATA=0`). Muốn nạp lại dữ liệu demo chạy `python database/seeder.py`; muốn xóa dữ liệu demo mà giữ nguyên 5 tài khoản ở trên và lịch sử chat thật, chạy `python scripts/purge_demo_data.py`.

---

## 7. Các Câu Hỏi Mẫu Thử Nghiệm Chatbot RAG AI
Truy cập trang Chatbot tại **http://127.0.0.1:5000/chat** và thử nghiệm:
- *"Có tour Hạ Long nào dưới 4 triệu không?"* &rarr; Gợi ý Tour Hạ Long 3.200.000 VNĐ kèm thẻ tour.
- *"Tôi có khoảng 5 triệu, muốn đi biển 3-4 ngày thì có tour nào?"* &rarr; Gợi ý Tour Phú Quốc và Đà Nẵng còn chỗ.
- *"Tour Sa Pa leo núi Fansipan còn chỗ không?"* &rarr; Báo số chỗ còn của tour Sa Pa.
- *"Có tour Đà Lạt nào dưới 100 nghìn không?"* &rarr; **Kiểm tra Zero Hallucination**: Chatbot thông báo lịch sự không có tour nào giá dưới 100k, tuyệt đối không bịa tour giả!

---

## 8. 💼 Phân Hệ Kế Toán & Tài Chính (Accounting Module)

Phân hệ dành riêng cho vai trò **Kế toán (Accountant)** và **Admin**, được bảo vệ bằng decorator `@roles_required("ADMIN", "ACCOUNTANT")`.

**Truy cập:** đăng nhập bằng `accountant@tourai.vn` / `accountant123`, sau đó chọn menu **"💼 Kế toán"** trên navbar hoặc truy cập trực tiếp **http://127.0.0.1:5000/accounting/dashboard**.

### Các màn hình chức năng
| Route | Phương thức | Chức năng |
|---|---|---|
| `/accounting/dashboard` | GET | Dashboard tài chính: Tổng thực thu, Tổng thực chi, Tồn quỹ ròng, Công nợ phải thu và danh sách việc cần xử lý |
| `/accounting/transactions` | GET | Sổ quỹ thu & đối soát giao dịch chuyển khoản từ khách hàng |
| `/accounting/transactions/<id>/verify` | POST | Kế toán xác nhận tiền đã vào tài khoản ngân hàng (duyệt giao dịch) |
| `/accounting/debts` | GET | Quản lý công nợ khách hàng; form ghi nhận thu nợ nhiều đợt |
| `/accounting/expenses` | GET, POST | Kê chi phí vận hành tour & form thêm khoản chi gắn với Lịch khởi hành |
| `/accounting/tours-pnl` | GET | Báo cáo hiệu quả kinh doanh & lãi/lỗ (P&L) theo từng đoàn tour |
| `/accounting/refunds` | GET, POST | Quản lý và lập phiếu chi hoàn tiền cho booking đã hủy |

### Quy tắc nghiệp vụ chính
- **Công nợ** = `Tổng tiền tour − Tổng tiền đã thanh toán thành công`.
- **P&L một đoàn tour** = `Doanh thu thực nhận − Tổng chi phí vận hành`; **Tỷ suất lợi nhuận (Margin %)** = `Lợi nhuận / Doanh thu × 100`.
- **Sổ quỹ ròng** = `Tổng thực thu − (Tổng chi phí vận hành + Tổng hoàn tiền)`.
- **Chính sách hoàn tiền hủy tour:**
  - Hủy trước ≥ 7 ngày so với ngày khởi hành: hoàn **90%** số tiền khách đã thanh toán.
  - Hủy từ 3–6 ngày: hoàn **50%**.
  - Hủy dưới 3 ngày: **0%** (không hoàn).
- Mọi thao tác ghi nhận tiền đều lưu `verified_by` (kế toán duyệt) và `verified_at` (thời điểm duyệt).

### Cấu trúc dữ liệu liên quan
- Bảng **`tour_expenses`**: lưu chi phí theo `schedule_id` với `category` ∈ {HOTEL, TRANSPORT, MEAL, TICKETS, GUIDE_FEE, OTHER}.
- Bảng **`payments`**: hỗ trợ `payment_type` ∈ {DEPOSIT, FULL, REMAINING, REFUND} cùng các trường xác nhận `verified_by`, `verified_at`.

### Kiểm thử phân hệ kế toán
Các test trong `tests/test_accounting.py` (nằm trong bộ 60 test):
- `test_record_and_verify_payment` — quy trình kế toán duyệt thanh toán chuyển khoản.
- `test_debt_calculation` — tính công nợ khi khách mới đặt cọc một phần.
- `test_tour_expense_and_pnl` — ghi nhận chi phí tour & kiểm tra công thức Lợi nhuận = Doanh thu − Chi phí.
- `test_cancellation_refund_policy_and_processing` — chính sách hoàn tiền theo số ngày trước khởi hành.
- `test_cashflow_summary_metrics` — sổ quỹ thu/chi.
- `test_unauthorized_access` — CUSTOMER/GUIDE bị chặn khỏi các route `/accounting/*`.

---

## 9. Liên Kết Repository
- GitHub: **https://github.com/dtc245220010ictu/Tour_AI**
- Repository cũ (đổi tên): https://github.com/dtc245220010ictu/He_thong_QL_tour_co_tich_hop_AI