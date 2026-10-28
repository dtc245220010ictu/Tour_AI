# Phân Tích Điểm Chưa Rõ, Giả Định & Rủi Ro Yêu Cầu (Requirements Issues)

Tài liệu này ghi nhận các điểm mơ hồ (ambiguities), giả định (assumptions), và ranh giới hệ thống phát hiện trong quá trình phân tích yêu cầu phần mềm cho Đề tài 17.

---

## 1. Các điểm chưa rõ trong tài liệu ban đầu (Ambiguities)
1. **Chính sách giá cho Trẻ em (Child Pricing):**
   - *Vấn đề:* Đề tài nêu giá tour nhưng chưa chỉ rõ tỷ lệ tính giá cho trẻ em so với người lớn.
   - *Cách xử lý:* Giả định trẻ em tính bằng 70% giá vé người lớn (hoặc cấu hình trường riêng `child_price` trong bảng giá lịch trình).
2. **Quy tắc hoàn tiền khi hủy tour (Cancellation Refund Policy):**
   - *Vấn đề:* Chưa có quy định hủy trước bao nhiêu ngày thì được hoàn bao nhiêu phần trăm.
   - *Cách xử lý:* Hiển thị quy tắc gợi ý: Hủy trước ngày khởi hành >= 7 ngày 90%; từ 3-6 ngày 50%; dưới 3 ngày 0%. Kế toán/Admin duyệt hoặc từ chối phiếu báo hoàn và quyết định số tiền cuối cùng trong giới hạn số tiền đã trả.
3. **Cơ chế xác nhận thanh toán trực tuyến:**
   - *Vấn đề:* Yêu cầu theo dõi thanh toán nhưng không bắt buộc tích hợp cổng thanh toán trực tiếp của ngân hàng thực tế (VNPAY/Momo Sandbox).
   - *Cách xử lý:* Hỗ trợ mô phỏng thanh toán (Simulated Checkout) và cập nhật thanh toán chuyển khoản/tiền mặt qua giao diện Kế toán và Khách hàng.

---

## 2. Các giả định chính (Assumptions)
- **Giả định 1 (Đơn vị tiền tệ):** Toàn bộ giá tour, giao dịch thanh toán và thống kê sử dụng đơn vị Việt Nam Đồng (VNĐ).
- **Giả định 2 (Kiểm soát chỗ - Concurrency):** Khi khách hàng tạo booking, hệ thống giữ chỗ ngay bằng kiểm tra điều kiện `available_seats >= requested_seats` và cập nhật nguyên tử trong cùng transaction để bảo đảm không bị race condition. Booking `PENDING`, `CONFIRMED`, `COMPLETED` giữ chỗ; booking `CANCELLED` hoàn chỗ.
- **Giả định 3 (AI Fallback):** Trong trường hợp người dùng chưa cấu hình `GEMINI_API_KEY` hoặc mạng bị gián đoạn, hệ thống phải có cơ chế fallback thông minh (Rule-based Search & Mock Response) để không làm crash hệ thống và vẫn phục vụ được khách hàng.
- **Giả định 4 (Phân quyền):** Người dùng có vai trò `ADMIN` có toàn quyền truy cập các module quản trị; `STAFF` quản lý tour/lịch/điểm đến, xem khách và xử lý trạng thái booking nhưng không quản lý feedback hoặc tài chính; `CUSTOMER` chỉ quản lý booking và feedback của chính mình.
- **Giả định 5 (Lưu trữ):** MySQL 8 là backend bắt buộc. Môi trường test phải dùng database MySQL riêng qua `MYSQL_TEST_DB` (hậu tố `_test`); không dùng SQLite cho runtime hoặc test tích hợp.

---

## 3. Ranh giới hệ thống (System Boundaries)
- **Thuộc phạm vi (In-Scope):**
  - Quản lý Tour, Điểm đến, Lịch trình, Lịch khởi hành.
  - Quản lý Booking, Trừ số chỗ, Hủy tour hoàn chỗ.
  - Phiếu báo hoàn, duyệt/từ chối hoàn tiền, công nợ, chi phí theo lịch và P&L.
  - Quản lý Hướng dẫn viên, Phân công tour.
  - Quản lý Phản hồi khách hàng.
  - Báo cáo thống kê kinh doanh (Doanh thu, tỷ lệ lấp đầy).
  - RAG Chatbot tư vấn tour chuẩn xác theo CSDL, AI sinh mô tả tour, AI tóm tắt phản hồi.
- **Ngoài phạm vi (Out-of-Scope):**
  - Đặt vé máy bay và phòng khách sạn trực tiếp từ hệ thống đối tác thứ 3 (GDS/OTA API).
  - Xuất hóa đơn đỏ điện tử (e-Invoice) kết nối với Tổng cục Thuế.

---

## 4. Biên bản Đánh giá & Phê duyệt (Human Gate 1 Review)
- **Người thẩm định:** Kỹ sư Trưởng / Giảng viên hướng dẫn
- **Trạng thái:** **APPROVED** (Đã phê duyệt)
- **Nội dung kiểm tra:**
  - [x] Danh sách yêu cầu chức năng (FR-001 đến FR-025) có ID đầy đủ, không thiếu sót.
  - [x] Yêu cầu phi chức năng (NFR-001 đến NFR-008) có tiêu chí đo lường rõ ràng.
  - [x] User Stories và Ma trận truy xuất rõ ràng, không có hiện tượng AI Hallucination.
  - [x] Acceptance Criteria có kịch bản Given-When-Then kiểm thử được.
  - [x] Đã phê chuẩn cho bước Thiết kế Kiến trúc (Architecture) và Thiết kế UML (UML Design).

