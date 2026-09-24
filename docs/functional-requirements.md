# 3. Yêu cầu chức năng

## 3.1. Chức năng quản lý

1. Đăng nhập và phân quyền quản lý, nhân viên tư vấn, kế toán.
2. Quản lý tour, điểm đến, lịch trình, giá tour.
3. Quản lý lịch khởi hành và số chỗ.
4. Quản lý khách hàng và đặt chỗ.
5. Theo dõi thanh toán, đặt cọc, hủy tour.
6. Quản lý hướng dẫn viên và phân công tour.
7. Thu thập phản hồi sau tour.
8. Thống kê doanh thu, tour bán chạy, tỷ lệ lấp đầy.

## 3.2. Phân quyền bắt buộc

Hệ thống xác định **đúng năm (05) vai trò** sau, không phát sinh thêm bất kỳ vai trò nào khác: **Quản trị viên (Admin), Nhân viên tư vấn, Kế toán, Khách hàng, Hướng dẫn viên**.

Nguyên tắc kiểm soát truy cập:

* Hệ thống áp dụng nguyên tắc **chỉ cho phép những thao tác được cấp quyền**; mọi thao tác không được cấp quyền đều bị từ chối và được ghi nhận là **"Không có quyền"**.
* Mỗi vai trò chỉ được thao tác trong đúng phạm vi quy định tại mục này; việc mở rộng phạm vi phải do Quản trị viên thực hiện thông qua phân quyền tài khoản.
* **Trợ lý AI là chức năng dùng chung cho cả 05 vai trò.** Việc sử dụng AI **không đồng nghĩa với việc người dùng được cấp thêm bất kỳ quyền quản lý dữ liệu nào** của hệ thống; phân quyền dữ liệu luôn được xác định riêng theo mục này.

### 3.2.1. Quản trị viên (Admin)

* Có **toàn quyền trên hệ thống**.
* Được xem, thêm, sửa, xóa và xử lý **tất cả** các chức năng hiện có tại mục 3.1.
* Được quản lý tài khoản và phân quyền người dùng.
* Được sử dụng Trợ lý AI.

### 3.2.2. Nhân viên tư vấn

**Chỉ được quản lý các chức năng:**

* Tour.
* Điểm đến.
* Lịch khởi hành.
* Khách hàng.

**Không có quyền** tham gia hoặc quản lý các chức năng còn lại, bao gồm:

* Thanh toán.
* Đặt cọc.
* Hoàn tiền.
* Hủy tiền/hủy tour về mặt tài chính.
* Quản lý hướng dẫn viên.
* Phân công hướng dẫn viên.
* Thống kê.
* Báo cáo tài chính.
* Các chức năng quản trị khác.

Nhân viên tư vấn **được sử dụng Trợ lý AI** (không đi kèm quyền quản lý dữ liệu nào khác).

### 3.2.3. Kế toán

**Chỉ được:**

* Quản lý thanh toán.
* Xử lý hoàn tiền.
* Xử lý các khoản tiền liên quan đến hủy tour.
* Xem thống kê.
* Xem và lập báo cáo tài chính.
* Xem thông tin tour.
* Xem thông tin điểm đến.

**Không có quyền** thêm, sửa, xóa hoặc quản lý các chức năng khác ngoài phạm vi trên.

Kế toán **được sử dụng Trợ lý AI** (không đi kèm quyền quản lý dữ liệu nào khác).

### 3.2.4. Khách hàng

**Chỉ được:**

* Xem tour.
* Đặt tour.
* Xem các tour mà chính mình đã đặt.
* Xem lịch khởi hành.
* Xem hướng dẫn viên.
* Đánh giá/phản hồi sau tour.
* Sử dụng Trợ lý AI.

**Không có quyền** xem, chỉnh sửa hoặc quản lý dữ liệu của khách hàng khác và **không có quyền** truy cập các chức năng quản trị.

### 3.2.5. Hướng dẫn viên

**Chỉ được xem:**

* Tour.
* Điểm đến.
* Lịch khởi hành.
* Bảng phân công nhiệm vụ của chính mình.
* Bảng phân công nhiệm vụ của các hướng dẫn viên đồng nghiệp.

**Không có quyền** thêm, sửa hoặc xóa dữ liệu và **không có quyền** quản lý các chức năng khác.

Hướng dẫn viên **được sử dụng Trợ lý AI** (không đi kèm quyền quản lý dữ liệu nào khác).

### 3.2.6. Quy định chung về Trợ lý AI

1. Cả **05 vai trò** (Admin, Nhân viên tư vấn, Kế toán, Khách hàng, Hướng dẫn viên) đều **Có quyền sử dụng** Trợ lý AI.
2. Trợ lý AI là chức năng dùng chung; **sử dụng AI không cấp thêm cho người dùng bất kỳ quyền xem, thêm, sửa, xóa hay xử lý dữ liệu nào** ngoài phạm vi đã quy định tại mục 3.2.1–3.2.5.
3. Kết quả từ Trợ lý AI không làm thay đổi trạng thái hay dữ liệu của hệ thống; mọi thao tác quản lý dữ liệu vẫn phải qua kiểm tra phân quyền tương ứng.

## 3.3. Bảng ma trận phân quyền

**Chú giải:** mỗi ô liệt kê đầy đủ các quyền được cấp theo thứ tự **Xem → Thêm → Sửa → Xóa → Xử lý**; phần sau dấu gạch nối liệt kê rõ các quyền **không** được cấp, ghi là **"Không có quyền"**.

| Chức năng | Admin | Nhân viên tư vấn | Kế toán | Khách hàng | Hướng dẫn viên |
| --- | --- | --- | --- | --- | --- |
| 1. Đăng nhập và phân quyền quản lý, nhân viên tư vấn, kế toán | Xem, Thêm, Sửa, Xóa, Xử lý (quản lý tài khoản và phân quyền người dùng) | Đăng nhập: Có quyền — Xem, Thêm, Sửa, Xóa, Xử lý tài khoản/phân quyền: **Không có quyền** | Đăng nhập: Có quyền — Xem, Thêm, Sửa, Xóa, Xử lý tài khoản/phân quyền: **Không có quyền** | Đăng nhập: Có quyền — Xem, Thêm, Sửa, Xóa, Xử lý tài khoản/phân quyền: **Không có quyền** | Đăng nhập: Có quyền — Xem, Thêm, Sửa, Xóa, Xử lý tài khoản/phân quyền: **Không có quyền** |
| 2. Quản lý tour, điểm đến, lịch trình, giá tour | Xem, Thêm, Sửa, Xóa, Xử lý | Xem, Thêm, Sửa, Xử lý — Xóa: **Không có quyền** | Xem (thông tin tour, điểm đến) — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** | Xem — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** | Xem — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** |
| 3. Quản lý lịch khởi hành và số chỗ | Xem, Thêm, Sửa, Xóa, Xử lý | Xem, Thêm, Sửa, Xử lý — Xóa: **Không có quyền** | **Không có quyền** | Xem — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** | Xem — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** |
| 4. Quản lý khách hàng và đặt chỗ | Xem, Thêm, Sửa, Xóa, Xử lý | Xem, Thêm, Sửa, Xử lý (khách hàng và tiếp nhận đặt chỗ, không gồm các bước tài chính) — Xóa: **Không có quyền** | **Không có quyền** | Xem (các tour mà chính mình đã đặt), Thêm (đặt tour) — Sửa, Xóa, Xử lý: **Không có quyền** | **Không có quyền** |
| 5. Theo dõi thanh toán, đặt cọc, hủy tour | Xem, Thêm, Sửa, Xóa, Xử lý | **Không có quyền** | Xem, Thêm, Sửa, Xử lý (quản lý thanh toán, hoàn tiền, các khoản tiền liên quan hủy tour) — Xóa: **Không có quyền** | **Không có quyền** | **Không có quyền** |
| 6. Quản lý hướng dẫn viên và phân công tour | Xem, Thêm, Sửa, Xóa, Xử lý | **Không có quyền** | **Không có quyền** | Xem (hướng dẫn viên) — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** | Xem (bảng phân công của chính mình và của đồng nghiệp) — Thêm, Sửa, Xóa, Xử lý: **Không có quyền** |
| 7. Thu thập phản hồi sau tour | Xem, Thêm, Sửa, Xóa, Xử lý | **Không có quyền** | **Không có quyền** | Thêm (gửi đánh giá/phản hồi của chính mình sau tour) — Xem, Sửa, Xóa, Xử lý: **Không có quyền** | **Không có quyền** |
| 8. Thống kê doanh thu, tour bán chạy, tỷ lệ lấp đầy | Xem, Thêm, Sửa, Xóa, Xử lý | **Không có quyền** | Xem, Xử lý (lập báo cáo tài chính) — Thêm, Sửa, Xóa: **Không có quyền** | **Không có quyền** | **Không có quyền** |
| Trợ lý AI | **Có quyền sử dụng** | **Có quyền sử dụng** | **Có quyền sử dụng** | **Có quyền sử dụng** | **Có quyền sử dụng** |

**Ghi chú đối với bảng ma trận:**

1. Chức năng Trợ lý AI là chức năng dùng chung; cả 5 vai trò đều **Có quyền sử dụng**, nhưng quyền này **không đi kèm bất kỳ quyền quản lý dữ liệu nào khác**.
2. Chữ "quản lý" trong phạm vi của Nhân viên tư vấn và Kế toán được hiểu theo đúng danh sách quyền đã liệt kê tại mục 3.2.2 và 3.2.3; mọi thao tác ngoài danh sách đó đều là **Không có quyền**.
3. Mọi vai trò đăng nhập bằng tài khoản của chính mình (chức năng 1); chỉ Quản trị viên được quản lý tài khoản và phân quyền người dùng.
4. Nhân viên tư vấn không tham gia các bước tài chính trong nghiệp vụ đặt chỗ (thanh toán, đặt cọc, hoàn tiền, hủy tour về mặt tài chính).
5. Khách hàng chỉ thao tác trên dữ liệu thuộc chính mình; Hướng dẫn viên chỉ thực hiện quyền xem theo danh sách tại mục 3.2.5.
6. **Giải thích về self-service của Khách hàng:** Việc khách hàng tự thanh toán và tự hủy được thực hiện **chỉ trên đơn đặt chỗ của chính mình**, được xem là một phần của quyền "Đặt tour" (chức năng 4) và "Xem các tour mà chính mình đã đặt"; khách hàng tuyệt đối không được can thiệp vào thanh toán/hủy của đơn hàng khác. Các thao tác tài chính trên đơn của khách hàng khác thuộc trách nhiệm của Kế toán và Quản trị viên theo chức năng 5.

