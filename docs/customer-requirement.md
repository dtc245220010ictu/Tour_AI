# Yêu Cầu Khách Hàng (Customer Requirements) - Đề Tài 17

## 1. Bối cảnh dự án
Công ty du lịch cần một hệ thống thông tin toàn diện để quản lý hoạt động kinh doanh lữ hành, bao gồm: tour du lịch, lịch khởi hành, quản lý khách hàng, đặt chỗ (booking), thanh toán, phân công hướng dẫn viên và tiếp nhận phản hồi sau chuyến đi.
Trong thực tế, khách hàng thường gặp khó khăn khi tìm kiếm tour phù hợp với ngân sách, thời gian và sở thích cá nhân; trong khi nhân viên công ty mất rất nhiều thời gian để soạn thảo mô tả tour, lên lịch trình tóm tắt và tổng hợp đánh giá của du khách.

## 2. Phạm vi yêu cầu chức năng
1. **Quản lý người dùng và phân quyền:**
   - Đăng nhập/đăng xuất an toàn.
   - Phân quyền các vai trò: Quản trị viên/Quản lý (Admin/Manager), Nhân viên tư vấn (Consultant/Staff), Kế toán (Accountant), Hướng dẫn viên (Tour Guide) và Khách hàng (Customer).

2. **Quản lý danh mục tour và điểm đến:**
   - Quản lý điểm đến (Destination): tên điểm đến, vùng miền, mô tả, hình ảnh.
   - Quản lý tour (Tour): tên tour, điểm đến, thời lượng (số ngày đêm), phương tiện, giá tiêu chuẩn, chính sách, lịch trình chi tiết theo ngày.

3. **Quản lý lịch khởi hành và kiểm soát chỗ:**
   - Mỗi tour có nhiều lịch khởi hành (Departure Schedules) với ngày đi, ngày về cụ thể, số chỗ tối đa (total seats) và số chỗ còn lại (available seats).
   - Tự động trừ số chỗ khi đặt chỗ thành công và hoàn lại chỗ khi hủy tour. Không cho phép đặt vượt quá số chỗ còn lại.

4. **Quản lý khách hàng và đặt chỗ (Booking):**
   - Khách hàng xem danh sách tour, tìm kiếm và lọc tour theo điểm đến, giá, thời gian khởi hành.
   - Đặt chỗ tour trực tuyến: nhập thông tin người đặt, số lượng khách (người lớn, trẻ em), chọn lịch khởi hành còn chỗ.
   - Quản lý danh sách đặt chỗ, cập nhật trạng thái: Chờ xác nhận, Đã đặt cọc, Đã thanh toán, Đã hoàn thành, Đã hủy.

5. **Theo dõi thanh toán, đặt cọc và hủy tour:**
   - Ghi nhận thanh toán (tiền mặt, chuyển khoản, cổng trực tuyến), số tiền đặt cọc tối thiểu, số tiền còn lại.
   - Xử lý chính sách hủy tour và hoàn tiền theo quy định.

6. **Quản lý hướng dẫn viên và phân công:**
   - Quản lý hồ sơ hướng dẫn viên: họ tên, số điện thoại, ngôn ngữ, kinh nghiệm.
   - Phân công hướng dẫn viên cho từng đợt khởi hành cụ thể, tránh trùng lịch.

7. **Thu thập và quản lý phản hồi:**
   - Du khách sau khi hoàn thành tour có thể gửi đánh giá sao (1-5 sao) và nhận xét phản hồi về chất lượng dịch vụ, hướng dẫn viên, khách sạn, ẩm thực.

8. **Báo cáo và thống kê:**
   - Thống kê doanh thu theo thời gian, thống kê tour bán chạy nhất, tỷ lệ lấp đầy chỗ (occupancy rate) của các chuyến khởi hành.

9. **Tích hợp trí tuệ nhân tạo (AI Engine):**
   - **AI tư vấn tour (RAG Chatbot):** Tư vấn tour thông minh theo ngôn ngữ tự nhiên dựa trên ngân sách, số ngày, điểm đến/sở thích. Chatbot bắt buộc phải truy vấn dữ liệu tour thực tế còn chỗ từ cơ sở dữ liệu, tuyệt đối không được tự bịa ra thông tin tour, giá tiền hay lịch khởi hành không có thật.
   - **AI sinh mô tả và lịch trình:** Hỗ trợ nhân viên tự động sinh nội dung mô tả tour hấp dẫn và tóm tắt lịch trình du lịch từ các điểm đến chính.
   - **AI tóm tắt và phân tích phản hồi:** Tự động tóm tắt hàng loạt phản hồi của khách hàng sau tour, phân tích điểm khen ngợi và các điểm cần cải thiện.

## 3. Yêu cầu kỹ thuật & Ràng buộc
- Backend: Python Flask.
- Cơ sở dữ liệu: MySQL (hỗ trợ SQLite cho môi trường local/test).
- AI Engine: Google Gemini API (hoặc OpenAI/Claude), có cơ chế bảo vệ API Key an toàn trong biến môi trường `.env`, có fallback khi chưa cấu hình key.
- Giao diện: Web responsive hiện đại, trực quan, thẩm mỹ cao (HTML5, CSS3, JavaScript).

