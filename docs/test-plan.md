# Kế Hoạch Kiểm Thử Phần Mềm (Software Test Plan) - TourAI

Tài liệu này đặc tả kế hoạch kiểm thử tự động và thủ công cho dự án **TourAI (Đề tài 17)** theo tiêu chuẩn `testing` skill.

---

## 1. Mục tiêu kiểm thử
1. Đảm bảo toàn bộ các yêu cầu chức năng (FR-001 đến FR-025) và yêu cầu phi chức năng (NFR-001 đến NFR-008) được xác minh chính xác.
2. Kiểm thử nghiêm ngặt cơ chế **Zero-Overbooking**: ngăn chặn tuyệt đối tình trạng đặt vượt quá số chỗ trống khả dụng khi có nhiều yêu cầu đặt chỗ.
3. Kiểm thử nguyên tắc **Zero-Hallucination**: bảo đảm Chatbot RAG chỉ tư vấn các tour thực tế có trong CSDL, không bao giờ tự bịa tour hoặc giá tiền ảo khi người dùng đưa ra các yêu cầu không tưởng.
4. Kiểm thử tính an toàn bảo mật: phòng chống SQL Injection trong câu truy vấn của Tour Retriever, bảo vệ Secrets và xử lý lỗi người dùng thân thiện.

---

## 2. Phạm vi kiểm thử (Scope of Testing)

### 2.1 Kiểm thử Đơn vị (Unit Tests)
- `tests/test_auth.py`:
  - Đăng ký tài khoản thành công, mật khẩu được băm an toàn (`generate_password_hash`).
  - Đăng nhập xác thực chính xác mật khẩu, từ chối mật khẩu sai.
  - Từ chối đăng ký với email trùng lặp.
- `tests/test_question_analyzer.py`:
  - Bóc tách điểm đến chính xác từ câu hỏi có dấu và không dấu ("ha long", "Hạ Long").
  - Chuẩn hóa mức giá tối đa / tối thiểu từ nhiều định dạng tiếng Việt: "dưới 4 triệu", "5tr", "100 nghìn", "3 đến 5 triệu".
  - Bóc tách thời lượng chuyến đi ("3 ngày", "2 ngày 1 đêm").
  - Nhận diện sở thích đặc thù ("biển", "núi", "săn mây") và ánh xạ điểm đến tương ứng.
  - Phân tích yêu cầu sắp xếp ("giá rẻ nhất" -> `price_asc`).
- `tests/test_tour_retrieval.py`:
  - Truy xuất tour theo điểm đến và mức giá tối đa bằng câu lệnh SQL có tham số (`?`).
  - Lọc bỏ các tour đã hết chỗ (`available_seats = 0`) hoặc đang bị vô hiệu hóa (`is_active = 0`).
  - Trả về danh sách rỗng (`[]`) khi ngân sách yêu cầu thấp hơn tất cả các tour hiện có (Zero Hallucination).
  - Đề xuất tour thay thế gần nhất khi không có tour thỏa mãn hoàn toàn.
- `tests/test_context_builder.py`:
  - Định dạng thông tin tour thành văn bản ngắn gọn, trung thực, kèm số chỗ còn và giá chuẩn VNĐ.
  - Xuất thông báo rõ ràng khi danh sách tour rỗng.
- `tests/test_booking_capacity.py`:
  - Đặt tour thành công và trừ chính xác số chỗ khả dụng trong CSDL.
  - Ngăn chặn Overbooking: ném lỗi `OverbookingError` khi đặt số chỗ lớn hơn `available_seats`.
  - Hủy đơn đặt tour và tự động hoàn trả số chỗ về lịch trình.
- `tests/test_price_consistency.py`:
  - Đồng bộ giá tour và giá lịch khởi hành.
  - Khi sửa lịch khởi hành đã có booking, tính lại `available_seats` từ booking `PENDING`/`CONFIRMED`/`COMPLETED`; chặn giảm `total_seats` thấp hơn số ghế đã giữ.

### 2.2 Kiểm thử Tích hợp (Integration Tests)
- `tests/test_rag_pipeline.py`:
  - Kiểm thử toàn trình `RAGService.answer_question()` từ câu hỏi đến phản hồi và thẻ tour.
  - Endpoint `POST /api/chat`: trả mã HTTP 200, phản hồi JSON đầy đủ gồm `answer` và `tours`.
  - Kiểm tra tính hợp lệ dữ liệu đầu vào: câu hỏi rỗng trả về mã lỗi HTTP 400.
  - Kịch bản Zero-Hallucination: khi hỏi tour giá dưới 100k, chatbot trả lời lịch sự không có tour, không bịa thông tin.
  - Kịch bản yêu cầu mơ hồ: "Tư vấn cho tôi đi du lịch" và "Có tour gì hay không?" chỉ trả các tour thực tế còn chỗ; "Tầm 5 triệu thì đi đâu?" chỉ trả tour có giá không vượt 5.000.000 VNĐ.

### 2.3 Kiểm thử Phân quyền & Luồng Quản trị Tour (RBAC & Admin Flow Tests)
- `tests/test_rbac.py`:
  - Ma trận phân quyền 5 vai trò (ADMIN, STAFF, ACCOUNTANT, GUIDE, CUSTOMER) trên các route quản trị, kế toán, phản hồi và AI.
  - Trang **Quản lý sản phẩm tour** hiển thị nút **Sửa** cho ADMIN và STAFF; nút **Xóa** chỉ hiển thị với ADMIN.
  - STAFF mở được form **Sửa Thông Tin Tour** từ danh sách và lưu thành công thay đổi (tên, thời lượng, giá) vào CSDL.

### 2.4 Kiểm thử Upload Ảnh & Bảo Toàn Ảnh Trong Form Sửa (Image Upload Tests)
- `tests/test_image_upload.py`:
  - Upload ảnh hợp lệ qua `POST /admin/upload-image` -> trả URL `/static/uploads/...` và file thực sự tồn tại trong thư mục upload.
  - Chặn file sai định dạng (`script.exe`) kèm thông báo lỗi; yêu cầu đăng nhập và chặn CUSTOMER tải ảnh.
  - Tạo tour kèm file ảnh -> `image_url` lưu đường dẫn nội bộ `/static/uploads/...`.
  - Form **Sửa tour** giữ nguyên ảnh upload nội bộ: ô ảnh là `type="text"` (không dùng `type="url"` — đường dẫn tương đối sẽ bị HTML5 chặn submit, khiến nhân viên bị bắt nhập lại URL) và bấm **Lưu thay đổi** không làm mất ảnh cũ.

---

## 3. Môi trường & Công cụ kiểm thử
- **Ngôn ngữ:** Python 3.14
- **Test Framework:** `pytest 9.1+`
- **Môi trường CSDL Test:** SQLite isolated test database (`database/test_tour_ai.db`)
- **HTTP Client:** Flask Test Client
- **Lệnh thực thi:** `python -m pytest -v`

