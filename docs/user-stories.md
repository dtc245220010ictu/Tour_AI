# Danh Sách User Stories & Ma Trận Truy Xuất (Traceability Matrix)

## 1. Danh sách User Stories

### Nhóm 1: Xác thực & Quản lý tài khoản
- **US-001 (Đăng ký tài khoản):**
  - *As a* khách hàng mới,
  - *I want to* đăng ký tài khoản với email, số điện thoại và mật khẩu,
  - *so that* tôi có thể đặt tour và theo dõi lịch sử đặt chỗ.
  - *Traceability:* `FR-001`
- **US-002 (Đăng nhập hệ thống):**
  - *As a* người dùng hệ thống (khách hàng hoặc nhân viên),
  - *I want to* đăng nhập với tài khoản của mình,
  - *so that* tôi truy cập được vào các chức năng phù hợp với quyền hạn của mình.
  - *Traceability:* `FR-002`, `FR-003`

### Nhóm 2: Quản lý Tour & Lịch trình
- **US-003 (Quản lý tour):**
  - *As an* nhân viên tư vấn / Quản trị viên,
  - *I want to* thêm mới, cập nhật thông tin tour (tên, giá, điểm đến, lịch trình),
  - *so that* danh sách sản phẩm tour luôn đầy đủ và chính xác trên hệ thống.
  - *Traceability:* `FR-005`, `FR-006`
- **US-004 (AI sinh mô tả tour):**
  - *As an* nhân viên soạn thảo nội dung tour,
  - *I want to* nhờ AI tạo văn phong mô tả tour và tóm tắt lịch trình từ các điểm nhấn chính,
  - *so that* tôi tiết kiệm thời gian viết bài và có nội dung quảng bá hấp dẫn.
  - *Traceability:* `FR-007`

### Nhóm 3: Lịch khởi hành & Kiểm soát chỗ
- **US-005 (Quản lý lịch khởi hành):**
  - *As an* nhân viên điều hành tour,
  - *I want to* tạo các đợt khởi hành với số chỗ giới hạn và giá vé tương ứng,
  - *so that* khách hàng có thể lựa chọn ngày đi cụ thể.
  - *Traceability:* `FR-008`
- **US-006 (Kiểm soát số chỗ trống):**
  - *As an* nhân viên quản lý,
  - *I want* hệ thống tự động khóa/chặn đặt tour khi một lịch khởi hành đã hết chỗ,
  - *so that* không bao giờ xảy ra tình trạng đặt vượt quá năng lực phục vụ (overbooking).
  - *Traceability:* `FR-009`, `FR-010`

### Nhóm 4: Tìm kiếm & Đặt tour
- **US-007 (Tìm kiếm và lọc tour):**
  - *As a* khách hàng,
  - *I want to* tìm kiếm tour theo địa điểm, ngân sách và thời lượng,
  - *so that* tôi nhanh chóng tìm thấy chuyến đi phù hợp với nhu cầu.
  - *Traceability:* `FR-011`
- **US-008 (Đặt tour trực tuyến):**
  - *As a* khách hàng,
  - *I want to* đặt chỗ cho bản thân và người thân trên một chuyến đi cụ thể,
  - *so that* công ty du lịch giữ chỗ và chuẩn bị dịch vụ cho tôi.
  - *Traceability:* `FR-012`, `FR-013`

### Nhóm 5: Thanh toán & Hủy tour
- **US-009 (Xử lý thanh toán):**
  - *As an* kế toán / khách hàng,
  - *I want to* cập nhật trạng thái thanh toán hoặc đặt cọc cho đơn tour,
  - *so that* đơn hàng được xác nhận chính thức.
  - *Traceability:* `FR-015`
- **US-010 (Hủy đơn tour):**
  - *As a* khách hàng hoặc nhân viên,
  - *I want to* hủy đơn đặt tour khi có nhu cầu đột xuất,
  - *so that* chỗ trống được giải phóng cho khách hàng khác và quy trình hoàn cọc được kích hoạt.
  - *Traceability:* `FR-016`

### Nhóm 6: Hướng dẫn viên & Phản hồi
- **US-011 (Phân công hướng dẫn viên):**
  - *As an* người điều hành tour,
  - *I want to* phân công hướng dẫn viên cho các đợt khởi hành,
  - *so that* đoàn tour có nhân sự dẫn dắt chất lượng.
  - *Traceability:* `FR-017`, `FR-018`
- **US-012 (Gửi phản hồi chuyến đi):**
  - *As a* khách hàng sau khi đi tour về,
  - *I want to* chấm sao và gửi nhận xét đánh giá,
  - *so that* chia sẻ trải nghiệm và đóng góp ý kiến nâng cao chất lượng dịch vụ.
  - *Traceability:* `FR-019`
- **US-013 (AI tóm tắt phản hồi):**
  - *As a* quản lý chất lượng dịch vụ,
  - *I want* AI phân tích và tóm tắt nhanh các điểm khen/chê từ toàn bộ nhận xét của khách,
  - *so that* tôi có cái nhìn tổng quan mà không cần đọc thủ công hàng trăm bình luận.
  - *Traceability:* `FR-020`

### Nhóm 7: Báo cáo & Thống kê
- **US-014 (Thống kê kinh doanh):**
  - *As a* giám đốc/quản lý,
  - *I want to* xem biểu đồ doanh thu, top tour đắt khách và tỷ lệ lấp đầy ghế,
  - *so that* tôi ra quyết định kinh doanh và điều chỉnh kế hoạch mở tour.
  - *Traceability:* `FR-021`

### Nhóm 8: Trợ lý AI Tư Vấn Tour (RAG Chatbot)
- **US-015 (Tư vấn bằng ngôn ngữ tự nhiên):**
  - *As a* khách hàng chưa biết đi đâu,
  - *I want to* nhắn tin cho AI Chatbot mô tả mong muốn ("Tôi muốn đi biển 3 ngày, ngân sách dưới 5 triệu"),
  - *so that* AI gợi ý ngay các tour có sẵn phù hợp nhất kèm link xem chi tiết.
  - *Traceability:* `FR-022`, `FR-023`, `FR-024`
- **US-016 (Chính sách Không bịa dữ liệu - Zero Hallucination):**
  - *As a* khách hàng,
  - *I want* AI chỉ giới thiệu những tour thực sự đang có và còn chỗ trong hệ thống,
  - *so that* tôi không bị tư vấn nhầm thông tin ảo hoặc giá không chính xác.
  - *Traceability:* `FR-024`, `FR-025`

---

## 2. Bảng Ma trận Truy xuất (Traceability Matrix)

| User Story ID | Tên User Story | Functional Requirements | Kiểm thử liên quan (Test Case) |
|---|---|---|---|
| `US-001` | Đăng ký tài khoản | FR-001 | TC-AUTH-01 |
| `US-002` | Đăng nhập hệ thống | FR-002, FR-003 | TC-AUTH-02 |
| `US-003` | Quản lý thông tin tour | FR-005, FR-006 | TC-TOUR-01 |
| `US-004` | AI sinh mô tả tour | FR-007 | TC-AI-GEN-01 |
| `US-005` | Quản lý lịch khởi hành | FR-008 | TC-SCHED-01 |
| `US-006` | Kiểm soát overbooking | FR-009, FR-010 | TC-BOOK-02 |
| `US-007` | Tìm kiếm và lọc tour | FR-011 | TC-TOUR-02 |
| `US-008` | Đặt tour trực tuyến | FR-012, FR-013, FR-014 | TC-BOOK-01 |
| `US-009` | Xử lý thanh toán | FR-015 | TC-PAY-01 |
| `US-010` | Hủy đặt chỗ & giải phóng ghế | FR-016 | TC-BOOK-03 |
| `US-011` | Phân công hướng dẫn viên | FR-017, FR-018 | TC-GUIDE-01 |
| `US-012` | Gửi đánh giá tour | FR-019 | TC-FEED-01 |
| `US-013` | AI tóm tắt phản hồi | FR-020 | TC-AI-SUM-01 |
| `US-014` | Báo cáo doanh thu & tỷ lệ lấp đầy | FR-021 | TC-STAT-01 |
| `US-015` | Chatbot tư vấn tour ngôn ngữ tự nhiên | FR-022, FR-023, FR-024 | TC-CHAT-01 |
| `US-016` | AI trung thực, không bịa thông tin | FR-024, FR-025 | TC-CHAT-02 |

