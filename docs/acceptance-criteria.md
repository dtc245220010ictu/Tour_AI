# Tiêu Chí Chấp Nhận (Acceptance Criteria)

Tài liệu này định nghĩa các tiêu chí chấp nhận cụ thể cho các User Story chính bằng cú pháp Gherkin (`Given - When - Then`).

---

### AC-001 (Đăng ký tài khoản)
- **Given:** Người dùng chưa có tài khoản trên hệ thống và đang ở trang đăng ký.
- **When:** Người dùng điền đầy đủ họ tên, email hợp lệ (chưa tồn tại trong hệ thống), số điện thoại và mật khẩu có ít nhất 6 ký tự, sau đó nhấn "Đăng ký".
- **Then:** Hệ thống tạo tài khoản mới với vai trò mặc định là `Customer`, lưu mật khẩu đã được băm an toàn, chuyển hướng đến trang đăng nhập và hiển thị thông báo thành công.

---

### AC-002 (Đăng nhập xác thực và phân quyền)
- **Given:** Người dùng đã có tài khoản hợp lệ.
- **When:** Người dùng nhập đúng email và mật khẩu rồi nhấn "Đăng nhập".
- **Then:** Hệ thống xác thực danh tính, tạo phiên làm việc (session). Nếu là Admin/Staff thì chuyển đến trang Quản trị, nếu là Customer thì chuyển đến trang chủ hoặc trang cá nhân.
- **When (Thất bại):** Người dùng nhập sai mật khẩu hoặc email không tồn tại.
- **Then:** Hệ thống từ chối đăng nhập và hiển thị thông báo "Email hoặc mật khẩu không chính xác", không tiết lộ cụ thể trường nào bị sai.

---

### AC-003 (Đặt chỗ thành công & Trừ số chỗ trống)
- **Given:** Chuyến đi ngày `20/10/2026` của tour "Khám Phá Hạ Long" đang có `available_seats = 10`.
- **When:** Khách hàng đặt tour cho `2 người lớn` và `1 trẻ em` (tổng 3 chỗ) và hoàn tất form đặt tour.
- **Then:**
  1. Hệ thống tạo bản ghi `booking` mới với trạng thái `PENDING`.
  2. Số chỗ khả dụng của lịch trình được cập nhật giảm chính xác: `available_seats = 10 - 3 = 7`.
  3. Tổng số tiền được tính đúng theo công thức: `2 * adult_price + 1 * child_price`.
  4. Hiển thị trang xác nhận với mã đặt chỗ duy nhất (Booking Code).

---

### AC-004 (Ngăn chặn Overbooking)
- **Given:** Chuyến đi ngày `15/11/2026` chỉ còn `available_seats = 2`.
- **When:** Khách hàng cố gắng đặt chỗ với số lượng `3 người`.
- **Then:**
  1. Hệ thống từ chối tạo đơn đặt chỗ.
  2. Hiển thị thông báo lỗi rõ ràng: "Rất tiếc, chuyến đi này chỉ còn lại 2 chỗ trống. Vui lòng giảm số lượng khách hoặc chọn ngày khởi hành khác."
  3. Giá trị `available_seats` trong CSDL không bị thay đổi.

---

### AC-005 (Hủy tour & Hoàn trả số chỗ)
- **Given:** Đơn đặt chỗ mã `BK-1002` gồm 4 khách cho chuyến đi ngày `01/12/2026` đang ở trạng thái `CONFIRMED`, chuyến đi có `available_seats = 5`.
- **When:** Khách hàng hoặc quản trị viên thực hiện thao tác "Hủy đặt chỗ".
- **Then:**
  1. Trạng thái đơn tour chuyển thành `CANCELLED`.
  2. Số chỗ của chuyến đi được hoàn trả tự động: `available_seats = 5 + 4 = 9`.
  3. Ghi nhận thời điểm hủy và chính sách hoàn tiền tương ứng.

---

### AC-006 (Chatbot AI - Gợi ý đúng dữ liệu trong CSDL)
- **Given:** Cơ sở dữ liệu có các tour biển: "Tour Phú Quốc 3N2Đ" giá 4.500.000 VNĐ (còn chỗ) và "Tour Nha Trang 4N3Đ" giá 6.200.000 VNĐ (còn chỗ).
- **When:** Khách hàng hỏi chatbot: *"Tôi có khoảng 5 triệu, muốn đi biển 3 ngày thì có tour nào không?"*
- **Then:**
  1. Question Analyzer trích xuất điều kiện: `category='biển' hoặc keyword='biển'`, `max_price=5000000`, `duration_days=3`.
  2. Tour Retriever truy vấn CSDL và lấy ra "Tour Phú Quốc 3N2Đ".
  3. Chatbot trả lời giới thiệu Tour Phú Quốc 3N2Đ với đúng mức giá 4.500.000 VNĐ và thông tin còn chỗ.
  4. Phản hồi hiển thị kèm thẻ tour (Product Card) để khách có thể nhấn "Xem chi tiết" và "Đặt ngay".

---

### AC-007 (Chatbot AI - Zero Hallucination khi không có tour phù hợp)
- **Given:** Cơ sở dữ liệu KHÔNG có bất kỳ tour nào đi "Đà Lạt" với mức giá dưới 1.000.000 VNĐ.
- **When:** Khách hàng hỏi: *"Có tour Đà Lạt nào dưới 1 triệu không?"*
- **Then:**
  1. Question Analyzer xác định: `destination='Đà Lạt'`, `max_price=1000000`.
  2. Tour Retriever truy vấn CSDL và trả về danh sách rỗng (`[]`).
  3. Chatbot phản hồi lịch sự bằng tiếng Việt: *"Hiện tại hệ thống chưa có tour Đà Lạt nào có mức giá dưới 1.000.000 VNĐ. Bạn có thể tham khảo các tour Đà Lạt khác có giá từ ... hoặc để lại thông tin để nhân viên tư vấn thêm."*
  4. Chatbot TUYỆT ĐỐI KHÔNG tự bịa ra một tour "Đà Lạt 1 ngày giá 900k" nếu không có trong cơ sở dữ liệu.

---

### AC-008 (AI Sinh mô tả tour & Tóm tắt phản hồi)
- **Given:** Nhân viên nhập các điểm nhấn: "Hạ Long, du thuyền 5 sao, vịnh Bái Tử Long, chèo kayak, hang Sửng Sốt".
- **When:** Nhân viên nhấn nút "AI Sinh mô tả".
- **Then:** Hệ thống gửi prompt tới AI Engine và trả về đoạn văn mô tả tour văn phong hấp dẫn, bố cục rõ ràng, kèm tóm tắt lịch trình theo ngày gợi ý.

