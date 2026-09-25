# Đặc Tả Yêu Cầu Phần Mềm (Software Requirements Specification)

## 1. Các bên liên quan (Stakeholders) & Tác nhân (Actors)
- **Quản trị viên (Admin/Manager):** Quản lý toàn bộ hệ thống, xem báo cáo doanh thu, tỷ lệ lấp đầy, quản trị người dùng và cấu hình.
- **Nhân viên tư vấn (Consultant/Staff):** Quản lý thông tin tour, điểm đến, lịch khởi hành, tiếp nhận và hỗ trợ booking của khách hàng, sử dụng AI sinh mô tả tour.
- **Kế toán (Accountant):** Theo dõi xác nhận thanh toán, tiền đặt cọc, công nợ, quản lý hoàn hủy tour.
- **Hướng dẫn viên (Tour Guide):** Xem lịch trình được phân công, danh sách khách hàng trong đoàn tour.
- **Khách hàng (Customer):** Xem, tìm kiếm, lọc tour, đặt tour, thanh toán, tương tác với AI Chatbot tư vấn, gửi phản hồi sau tour.
- **AI Engine (Gemini / RAG Service):** Hệ thống trí tuệ nhân tạo hỗ trợ tư vấn dựa trên cơ sở dữ liệu tour, sinh nội dung và tóm tắt phản hồi.

---

## 2. Yêu cầu chức năng (Functional Requirements)

### Phân hệ 1: Xác thực & Quản trị người dùng
- **FR-001:** Hệ thống phải cho phép người dùng đăng ký tài khoản khách hàng mới với họ tên, email, số điện thoại và mật khẩu.
- **FR-002:** Hệ thống phải cho phép người dùng đăng nhập an toàn bằng email/tên đăng nhập và mật khẩu, cấp phiên làm việc (session).
- **FR-003:** Hệ thống phải kiểm soát truy cập và phân quyền theo 5 vai trò: Admin, Consultant, Accountant, Guide, Customer.
- **FR-004:** Hệ thống cho phép người dùng quản lý và cập nhật thông tin cá nhân.

### Phân hệ 2: Quản lý Điểm đến & Tour du lịch
- **FR-005:** Nhân viên/Admin có thể xem, thêm mới, cập nhật và xóa mềm điểm đến (Destination).
- **FR-006:** Nhân viên/Admin có thể xem danh sách, thêm mới, sửa và xóa tour du lịch (tên tour, điểm đến, giá, thời lượng, lịch trình ngày).
- **FR-007:** Hệ thống cung cấp công cụ AI hỗ trợ tự động sinh bản mô tả tour hấp dẫn và tóm tắt lịch trình du lịch dựa trên các điểm đến và từ khóa do nhân viên nhập.

### Phân hệ 3: Lịch khởi hành & Kiểm soát chỗ (Schedule & Capacity)
- **FR-008:** Nhân viên/Admin có thể tạo và quản lý các đợt khởi hành cho từng tour (ngày đi, ngày về, tổng số chỗ, giá theo đợt, trạng thái).
- **FR-009:** Hệ thống tự động tính toán và cập nhật số chỗ còn trống (available seats) theo thời gian thực khi có booking mới hoặc khi hủy booking.
- **FR-010:** Hệ thống phải ngăn chặn tình trạng đặt vượt quá số chỗ khả dụng (overbooking).

### Phân hệ 4: Tìm kiếm, Đặt tour & Khách hàng
- **FR-011:** Khách hàng có thể tìm kiếm tour theo từ khóa, lọc theo điểm đến, khoảng giá, số ngày và xem chi tiết tour cùng lịch khởi hành.
- **FR-012:** Khách hàng có thể tạo đơn đặt tour (booking) bằng cách chọn lịch khởi hành còn chỗ, nhập số lượng khách (người lớn, trẻ em) và thông tin liên hệ.
- **FR-013:** Hệ thống tự động tính tổng tiền tour dựa trên số lượng khách và đơn giá của đợt khởi hành.
- **FR-014:** Khách hàng và nhân viên có thể tra cứu lịch sử và trạng thái đơn đặt tour.

### Phân hệ 5: Thanh toán & Quản lý Hủy tour
- **FR-015:** Khách hàng hoặc Kế toán có thể ghi nhận thanh toán (đặt cọc hoặc thanh toán toàn bộ) cho đơn đặt chỗ.
- **FR-016:** Hệ thống hỗ trợ quy trình hủy tour theo chính sách: cập nhật trạng thái hủy, hoàn lại số chỗ trống cho lịch khởi hành và ghi nhận phí hoàn tiền (nếu có).

### Phân hệ 6: Hướng dẫn viên & Phân công
- **FR-017:** Quản trị viên/Nhân viên có thể quản lý danh sách hồ sơ hướng dẫn viên du lịch.
- **FR-018:** Quản trị viên có thể phân công hướng dẫn viên cho đợt khởi hành cụ thể, kiểm tra trùng lặp lịch làm việc.

### Phân hệ 7: Đánh giá & Phản hồi
- **FR-019:** Khách hàng đã hoàn thành tour có thể gửi đánh giá điểm số (1-5 sao) và nhận xét phản hồi chi tiết.
- **FR-020:** Hệ thống cung cấp công cụ AI tóm tắt các phản hồi của khách hàng, tổng hợp ưu điểm và nhược điểm để nâng cao chất lượng tour.

### Phân hệ 8: Báo cáo & Thống kê
- **FR-021:** Hệ thống cung cấp dashboard hiển thị doanh thu theo khoảng thời gian, danh sách tour bán chạy nhất và tỷ lệ lấp đầy chỗ của các đợt khởi hành.

### Phân hệ 9: Trợ lý AI Tư Vấn Tour (RAG Chatbot)
- **FR-022:** Khách hàng có thể tương tác với Chatbot bằng ngôn ngữ tự nhiên tiếng Việt để tìm kiếm và nhận tư vấn tour.
- **FR-023:** Chatbot phân tích câu hỏi người dùng thành các tiêu chí có cấu trúc (điểm đến, ngân sách tối đa, thời lượng, ngày đi, sở thích).
- **FR-024:** Chatbot bắt buộc phải truy vấn dữ liệu từ MySQL/SQLite để lấy các tour còn chỗ phù hợp với tiêu chí của khách.
- **FR-025:** Nếu không tìm thấy tour nào phù hợp trong cơ sở dữ liệu, Chatbot phải thông báo rõ ràng rằng hiện không có tour thỏa mãn thay vì tự bịa ra thông tin giả mạo.

---

## 3. Yêu cầu phi chức năng (Non-Functional Requirements)

- **NFR-001 (Hiệu năng):** Thời gian phản hồi trang web trung bình dưới 1.5 giây đối với các tác vụ CRUD thông thường; thời gian phản hồi của Chatbot AI dưới 4 giây.
- **NFR-002 (Bảo mật - Mật khẩu):** Mật khẩu người dùng phải được băm an toàn bằng thuật toán bcrypt/pbkdf2 trước khi lưu vào CSDL.
- **NFR-003 (Bảo mật - Secrets):** API Key của AI Engine (Gemini API Key) và Secret Key của ứng dụng phải lưu trong biến môi trường (`.env`), tuyệt đối không hardcode trong mã nguồn hoặc client-side JS.
- **NFR-004 (Bảo mật - Injection):** Toàn bộ truy vấn cơ sở dữ liệu phải dùng parameterized query hoặc ORM để triệt tiêu lỗ hổng SQL Injection.
- **NFR-005 (Toàn vẹn dữ liệu):** Ràng buộc tính nhất quán số chỗ trống: `available_seats = total_seats - SUM(num_adults + num_children của booking PENDING, CONFIRMED, COMPLETED)` luôn được bảo đảm bằng giao dịch (database transaction). Booking `PENDING` đã giữ chỗ; booking `CANCELLED` được hoàn chỗ và không được tính vào số ghế đã giữ.
- **NFR-006 (Giao diện & Trải nghiệm):** Giao diện thân thiện, tương thích đa thiết bị (responsive trên mobile, tablet, desktop).
- **NFR-007 (Độ tin cậy của AI):** Cơ chế Zero-Hallucination: Prompt hệ thống của RAG Chatbot nghiêm cấm việc suy đoán hoặc tự tạo tour, giá tiền hay ngày khởi hành không có trong ngữ cảnh CSDL được cấp.
- **NFR-008 (Khả năng mở rộng):** Thiết kế theo mô hình kiến trúc phân lớp (Layered Architecture: Route -> Service -> Repository/Model) giúp dễ dàng tích hợp thêm các dịch vụ thanh toán và mô hình AI khác.

