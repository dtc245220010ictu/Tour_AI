# Hướng Dẫn Sử Dụng Hệ Thống (User Guide) - TourAI

Tài liệu này cung cấp hướng dẫn thao tác chi tiết dành cho Khách hàng (Customer) và Nhân viên/Quản trị viên (Staff/Admin) của hệ thống **TourAI (Đề tài 17)**.

---

## Thanh điều hướng chung

- Mọi người dùng có thể mở **Trang chủ**, **Khám phá Tour** và **Trợ lý AI**.
- Khi đã đăng nhập, nhấn **Không gian làm việc** để quay lại các chức năng đúng vai trò sau khi xem các trang chung. Riêng Khách hàng, nút này hiển thị là **Tour của tôi**.

---

## PHẦN I. HƯỚNG DẪN DÀNH CHO KHÁCH HÀNG

### 1. Khám Phá & Tìm Kiếm Tour Du Lịch
1. Truy cập trang chủ **Trang chủ** hoặc mục **Khám phá Tour**.
2. Sử dụng thanh tìm kiếm để lọc tour theo:
   - **Từ khóa:** Nhập tên tour, danh lam thắng cảnh hoặc địa phương.
   - **Điểm đến:** Chọn tỉnh/thành phố (Hạ Long, Đà Nẵng, Phú Quốc, Sa Pa, Đà Lạt, Hà Giang...).
   - **Mức giá:** Chọn ngân sách tối đa (Dưới 3 triệu, dưới 4 triệu, dưới 6 triệu...).
   - **Thời lượng:** 2 ngày, 3 ngày hoặc từ 4 ngày trở lên.
3. Nhấn **Lọc kết quả** để xem các tour thỏa mãn.

### 2. Tư Vấn Thông Minh Bằng Chatbot AI
1. Nhấn vào mục **🤖 Trợ lý AI** trên thanh điều hướng.
2. Bạn có thể bấm vào các gợi ý có sẵn hoặc tự nhập câu hỏi tự nhiên bằng tiếng Việt vào khung chat ở dưới cùng:
   - *"Có tour Hạ Long nào dưới 4 triệu không?"*
   - *"Tôi có 5 triệu, muốn đi biển 3-4 ngày thì có tour nào?"*
   - *"Tour Sa Pa leo núi Fansipan cuối tuần còn chỗ không?"*
3. Trợ lý AI sẽ:
   - Phân tích yêu cầu và truy xuất dữ liệu tour thực tế còn chỗ trong cơ sở dữ liệu.
   - Trả lời tư vấn nhiệt tình, nêu rõ giá tiền, thời lượng và ngày khởi hành.
   - Hiển thị trực tiếp **Thẻ Tour (Product Cards)** ngay bên dưới câu trả lời.
4. Bấm nút **"Xem chi tiết & Đặt"** trên thẻ tour để chuyển ngay đến trang chi tiết chuyến đi.

> 💡 **Lưu ý:** Chức năng *"Tóm tắt phản hồi khách hàng"* chỉ dành cho tài khoản **Quản trị viên (ADMIN)**. Khi khách hàng hỏi, trợ lý sẽ nhắc nhở lịch sự rằng chức năng dành cho Quản trị viên và tiếp tục hỗ trợ tư vấn tour.

### 3. Đặt Chỗ Tour & Giữ Ghế (Booking)
1. Tại trang chi tiết tour, cuộn xuống mục **📅 Lịch Khởi Hành & Chỗ Còn Trống**.
2. Chọn ngày khởi hành mong muốn (chú ý số chỗ còn lại) và nhấn **Đặt tour**.
3. Điền thông tin người đại diện (Họ tên, số điện thoại, email) và chọn số lượng khách (Người lớn, trẻ em).
4. Hệ thống sẽ tự động tính toán tổng số tiền cần thanh toán.
5. Nhấn **Xác nhận Đặt chỗ**:
   - Nếu số chỗ còn đủ: Hệ thống tạo mã đặt chỗ duy nhất (ví dụ: `BK-20261015-8899`) và lập tức trừ số chỗ tương ứng để giữ chỗ cho bạn.
   - Nếu số chỗ không đủ: Hệ thống sẽ hiển thị thông báo lỗi hết chỗ rõ ràng và ngăn chặn việc đặt quá số chỗ (Overbooking).

### 4. Quản Lý Đơn & Hủy Tour
1. Nhấn **🎒 Tour của tôi** trên thanh menu để xem danh sách các chuyến đi đã đặt.
2. Khách hàng có thể nhấn **Chi tiết** để xem lại biên nhận hoặc bấm **Hủy tour** khi có việc đột xuất.
3. Bạn được **tự hủy trực tiếp** các đơn ở trạng thái **Chờ thanh toán** hoặc **Đã xác nhận** mà không cần chờ nhân viên tư vấn phê duyệt. Đơn đã hoàn thành hoặc đã hủy trước đó sẽ không thể hủy thêm lần nữa.
4. Khi bạn nhấn Hủy tour, hệ thống sẽ tự động giải phóng và cộng trả lại số chỗ trống vào lịch trình để khách hàng khác có thể đặt.
5. Nếu đơn đã thanh toán, hệ thống tạo **phiếu báo hoàn tiền** ở trạng thái chờ duyệt. Mức 90% (hủy trước ≥ 7 ngày), 50% (3–6 ngày) hoặc 0% (dưới 3 ngày) chỉ là **gợi ý** cho Kế toán/Admin; số tiền hoàn cuối cùng được phê duyệt và hiển thị trong *Tour của tôi*.

---

## PHẦN II. HƯỚNG DẪN DÀNH CHO NHÂN VIÊN & QUẢN TRỊ VIÊN

### 1. Bảng Điều Khiển Báo Cáo (Admin Dashboard)
1. Với môi trường đã nạp demo bằng `python database/seeder.py`, đăng nhập bằng tài khoản quản trị (`admin@tourai.vn` / `admin123`) hoặc nhân viên (`staff@tourai.vn` / `staff123`). Ở môi trường không seed, dùng tài khoản do quản trị viên tạo.
2. Nhấn vào mục **📊 Quản trị** trên thanh menu:
   - Theo dõi 4 chỉ số cốt lõi: Tổng doanh thu thực thu, Tổng đơn đặt, Số lượng tour mở bán, Số khách hàng đăng ký.
   - Xem bảng xếp hạng **Top Tour Bán Chạy Nhất**.
   - Xem biểu đồ thanh đo **Tỷ Lệ Lấp Đầy Chỗ (Occupancy Rate)** theo từng chuyến khởi hành để quyết định mở thêm chuyến hoặc giảm giá kích cầu.

### 2. Quản Lý Tour & Sử Dụng AI Sinh Nội Dung Tự Động
1. Truy cập mục **Quản lý Tour**.
2. Để thêm tour mới nhanh chóng:
   - Nhập Tên tour và chọn Điểm đến.
   - Nhấn nút màu tím: **✨ AI Sinh Mô Tả & Lịch Trình Tự Động**.
   - Hệ thống sẽ tự động tạo ra một đoạn văn giới thiệu chuẩn marketing du lịch hấp dẫn và phân bổ lịch trình chi tiết từ Ngày 1 đến ngày cuối cùng.
   - Nhân viên có thể chỉnh sửa lại theo ý muốn và nhấn **Lưu Tour Mới**.
3. Để **sửa một tour đã có**:
   - Tại bảng **Danh Sách Tour Hiện Có**, bấm nút **Sửa** ở cột **Thao tác** (ADMIN và STAFF đều sử dụng được).
   - Form **✏️ Sửa Thông Tin Tour** mở ra với đầy đủ thông tin hiện tại: tên, điểm đến, thời lượng, giá, phương tiện, ảnh, mô tả, lịch trình chi tiết và trạng thái hiển thị.
   - Ô **Ảnh đại diện** hiển thị sẵn ảnh hiện tại. Muốn đổi ảnh thì chọn file mới hoặc dán ảnh (Ctrl+V); nếu giữ nguyên thì không cần nhập lại URL — ảnh cũ vẫn được giữ khi bấm **💾 Lưu thay đổi**.
   - Nếu đổi giá tour, giữ tích **"Đồng bộ giá lịch khởi hành theo giá tour mới"** để mọi đợt khởi hành được cập nhật: giá người lớn = giá tour, giá trẻ em = 70%.
   - Bấm **💾 Lưu thay đổi**; hệ thống báo "Đã cập nhật tour thành công!" và danh sách tour hiển thị thông tin mới.
4. Nút **Xóa** (xóa mềm — tour bị ẩn khỏi trang bán thay vì xóa vĩnh viễn) chỉ hiển thị với tài khoản **ADMIN**.

### 3. Mở Đợt Khởi Hành Mới & Kiểm Soát Chỗ
1. Truy cập mục **Lịch Khởi Hành**.
2. Chọn Tour, ngày khởi hành, ngày kết thúc, giá vé người lớn, giá vé trẻ em và tổng số chỗ (ví dụ: 20 chỗ).
3. Nhấn **Lưu Lịch Khởi Hành** để mở bán trên trang web.
4. Khi sửa một lịch đã có booking, chỉ cập nhật tổng số chỗ, ngày đi/về, giá và trạng thái. Trường **Số chỗ còn lại** là chỉ đọc: hệ thống tự tính bằng tổng số chỗ trừ số khách của các booking chưa hủy.
5. Không thể giảm tổng số chỗ thấp hơn số chỗ đã giữ; hệ thống sẽ báo lỗi và giữ nguyên dữ liệu nếu thao tác không hợp lệ.
6. ADMIN hoặc STAFF có thể **Tạm hoãn** một lịch khởi hành nhưng phải nhập lý do. Lịch `POSTPONED` không nhận booking mới và lý do hoãn hiển thị cho khách; thao tác **Khôi phục** sẽ trả lịch về `OPEN` hoặc `FULL` theo số chỗ còn lại.

### 4. Phân Tích & Tóm Tắt Đánh Giá Bằng AI (Chỉ dành cho Quản trị viên)
1. Truy cập mục **Đánh Giá AI** (yêu cầu quyền Quản trị viên - ADMIN).
2. Xem toàn bộ các nhận xét và chấm điểm sao của khách hàng sau các chuyến đi.
3. Nhấn nút: **🤖 AI Phân Tích & Tóm Tắt Toàn Bộ Phản Hồi**:
   - Trợ lý AI sẽ đọc qua toàn bộ các đánh giá và xuất bản **Báo Cáo Chất Lượng Dịch Vụ**, chỉ rõ:
     - Các điểm khách hàng hài lòng nhất (Hướng dẫn viên, đồ ăn, cảnh quan...).
     - Các hạn chế cần khắc phục (xe cộ, thời gian nghỉ ngơi...).
     - Đề xuất cải tiến hành động cụ thể cho ban quản lý.
4. **Hỏi trực tiếp Trợ lý AI:** Ngoài trang Đánh Giá AI, bạn có thể vào mục **🤖 Trợ lý AI** và gõ *"Tóm tắt phản hồi khách hàng"* (hoặc bấm chip **📊 Tóm tắt phản hồi khách hàng** chỉ hiển thị với tài khoản ADMIN):
   - Trợ lý nhận diện đúng yêu cầu và trả ngay **Báo cáo tổng hợp phản hồi** kèm số lượng phản hồi và điểm trung bình sao — thay vì trả lời tư vấn tour.
   - Khách hàng (không phải ADMIN) khi hỏi sẽ nhận thông báo lịch sự rằng chức năng dành cho Quản trị viên.

---

## PHẦN III. HƯỚNG DẪN DÀNH CHO HƯỚNG DẪN VIÊN

1. Đăng nhập bằng tài khoản Hướng dẫn viên và mở **Không gian làm việc → Đoàn được phân công** để xem lịch dẫn đoàn và tra cứu tour. Các màn hình này chỉ cho phép xem.
2. Mở **Không gian làm việc → Khách trong đoàn → Danh sách khách** để xem khách còn hiệu lực của tất cả đoàn đã được phân công hướng dẫn viên, gồm thông tin liên hệ, số lượng khách, lịch đi và ghi chú.
3. Danh sách khách không có nút thêm, sửa, xóa hay cập nhật trạng thái đơn. Nếu cần thay đổi booking, liên hệ Nhân viên tư vấn hoặc Quản trị viên.
4. Mọi vai trò, gồm Hướng dẫn viên, đều có thể dùng **Trợ lý AI** từ thanh điều hướng chung; trợ lý không cấp thêm quyền quản lý dữ liệu.

---

## PHẦN IV. HƯỚNG DẪN DÀNH CHO KẾ TOÁN (ACCOUNTANT / ADMIN)

Với môi trường demo, đăng nhập bằng tài khoản kế toán (`accountant@tourai.vn` / `accountant123`) hoặc quản trị viên (`admin@tourai.vn` / `admin123`); ở môi trường không seed, dùng tài khoản được cấp. Sau đó mở **Không gian làm việc → Tài chính**.

### 1. Dashboard Tài Chính Kế Toán
1. Truy cập **Kế toán → Bảng điều khiển**.
2. Theo dõi 4 chỉ số tài chính chính:
   - **Tổng Thực Thu (Tiền Vào):** Tổng các khoản thanh toán thành công từ khách hàng.
   - **Tổng Thực Chi (Tiền Ra):** Bao gồm chi phí vận hành tour và hoàn tiền hủy tour.
   - **Tồn Quỹ Ròng (Net Cash):** Số dư tiền mặt & ngân hàng hiện có.
   - **Công Nợ Phải Thu:** Tổng tiền khách hàng còn nợ chưa thanh toán đủ.
3. Xem cảnh báo giao dịch chuyển khoản chờ duyệt và đơn hủy tour cần lập phiếu chi.
4. Xem tóm tắt hiệu quả lợi nhuận (P&L) các đợt khởi hành gần nhất.

### 2. Đối Soát & Duyệt Thanh Toán Chuyển Khoản
1. Truy cập **Kế toán → Phiếu Thu & Đối Soát**.
2. Danh sách hiển thị các giao dịch thanh toán (Đang chờ / Thành công).
3. Khi khách hàng chuyển khoản ngân hàng, trạng thái là `PENDING`. Kế toán kiểm tra sao kê ngân hàng, nếu đúng thì nhấn nút **Duyệt tiền vào** để xác nhận.
4. Sau khi duyệt, đơn đặt tour của khách tự động chuyển sang trạng thái `CONFIRMED`.

### 3. Quản Lý Công Nợ Khách Hàng
1. Truy cập **Kế toán → Công Nợ**.
2. Hệ thống tự động tính toán: `Công nợ = Tổng tiền đơn tour - Tổng tiền đã thanh toán`.
3. Bảng hiển thị: Mã đơn, Tên khách, Tour & Ngày đi, Đã nộp, Còn nợ, Trạng thái (Đặt cọc một phần / Chưa thanh toán).
4. Nhấn **Thu nợ** để mở form lập phiếu thu cho từng đợt thanh toán còn lại.

### 4. Quản Lý Chi Phí Vận Hành Đoàn Tour
1. Truy cập **Kế toán → Chi Phí Tour**.
2. Chọn Lịch khởi hành đoàn tour và ghi nhận từng khoản chi theo 6 hạng mục:
   - 🚌 Xe vận chuyển / Vé máy bay
   - 🏨 Phòng khách sạn / Lưu trú
   - 🍽️ Ăn uống / Nhà hàng
   - 🎟️ Vé thắng cảnh / Cáp treo
   - 👨‍💼 Thù lao Hướng dẫn viên
   - 📦 Chi phí phát sinh khác
3. Nhập số tiền, tên nhà cung cấp, số hóa đơn, ngày lập phiếu và ghi chú.
4. Có thể lọc chi phí theo từng đợt khởi hành để kiểm soát ngân sách chặt chẽ.

### 5. Báo Cáo Lợi Nhuận Từng Đoàn Tour (P&L Report)
1. Truy cập **Kế toán → Báo Cáo P&L**.
2. Xem bảng lãi lỗ cho từng chuyến đi:
   - **Doanh thu:** Tổng tiền khách hàng đã thanh toán thành công.
   - **Chi phí vận hành:** Tổng các khoản chi đã ghi nhận (có phân loại cơ cấu chi phí).
   - **Lợi nhuận gộp:** = Doanh thu - Chi phí.
   - **Tỷ suất lợi nhuận (Margin %):** = (Lợi nhuận gộp / Doanh thu) × 100.
3. Biên lợi nhuận được đánh dấu màu: 🟢 ≥ 20% (Tốt), 🟡 > 0% (Trung bình), 🔴 ≤ 0% (Lỗ).
4. Có thể lọc theo chuyến đi cụ thể hoặc xem tổng hợp tất cả.

### 6. Quản Lý Hoàn Tiền Khi Hủy Tour
1. Truy cập **Kế toán → Hoàn Tiền Hủy**.
2. Hệ thống hiển thị mức **gợi ý** hoàn tiền theo 3 mốc thời gian:
   - Hủy trước ≥ 7 ngày trước khởi hành → Hoàn **90%** tiền đã nộp.
   - Hủy từ 3 đến 6 ngày → Hoàn **50%**.
   - Hủy dưới 3 ngày → **Không hoàn tiền (0%)**.
3. Kế toán/Admin xem phiếu `PENDING`, số tiền khách yêu cầu, mức gợi ý và lý do hủy; sau đó chọn **Duyệt** hoặc **Từ chối**.
4. Khi duyệt, có thể điều chỉnh số tiền hoàn thực tế nhưng không vượt số tiền khách đã thanh toán; hệ thống tạo giao dịch `REFUND`. Khi từ chối, phải nhập lý do để khách theo dõi.

