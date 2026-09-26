# Báo Cáo Kết Quả Kiểm Thử (Automated Test Report) - TourAI

Tài liệu này ghi nhận kết quả thực thi bộ kiểm thử tự động toàn diện cho hệ thống **TourAI (Đề tài 17)** theo tiêu chuẩn `testing` skill.

---

## 1. Tóm tắt kết quả kiểm thử (Executive Summary)

- **Thời điểm thực thi:** 26/09/2026
- **Test Framework:** `pytest 9.1.1`
- **Môi trường:** Python 3.14 (Windows)
- **Tổng số ca kiểm thử:** **103/103 PASSED**
- **Tỷ lệ thành công:** **100.0%**
- **Thời gian thực thi:** 3.54 giây
- **Tình trạng:** **PASSED - READY FOR PRODUCTION**

```text
103 tests collected
....................................................................................................
103 passed in 3.54s
```

---

## 2. Chi tiết các module kiểm thử

| STT | Tên Test File | Số ca test | Kết quả | Trọng tâm kiểm thử |
|---|---|---|---|---|
| 1 | `test_accounting.py` | 6 | 6/6 PASS | Đối soát thanh toán, công nợ, chi phí tour, P&L, hoàn tiền hủy tour, RBAC |
| 2 | `test_ai_content_service.py` | 9 | 9/9 PASS | AI sinh mô tả/lịch trình có fallback cấu trúc, retry và validation output |
| 3 | `test_auth.py` | 6 | 6/6 PASS | Mật khẩu băm an toàn, đăng ký, đăng nhập và quick-login theo cấu hình |
| 4 | `test_booking_capacity.py` | 5 | 5/5 PASS | Trừ số chỗ nguyên tử, chặn overbooking, hoàn chỗ và guardrails hủy đơn |
| 5 | `test_context_builder.py` | 2 | 2/2 PASS | Định dạng context ngắn gọn, thông báo rỗng chuẩn mực |
| 6 | `test_grounded_answer_builder.py` | 4 | 4/4 PASS | Câu trả lời chỉ dùng tour/giá/ngày đi có trong dữ liệu retrieve |
| 7 | `test_image_upload.py` | 6 | 6/6 PASS | Upload/paste ảnh hợp lệ, chặn file sai, RBAC và ô ảnh form Sửa tour |
| 8 | `test_price_consistency.py` | 5 | 5/5 PASS | Giá tour–lịch, tổng tiền booking và số chỗ tự tính khi sửa lịch |
| 9 | `test_question_analyzer.py` | 17 | 17/17 PASS | Ngân sách, thời lượng/range, điểm đến, sở thích, regression "khoảng 5 triệu" & nhận diện yêu cầu tóm tắt phản hồi |
| 10 | `test_rag_pipeline.py` | 15 | 15/15 PASS | API chat, zero-hallucination, alternatives, câu hỏi mơ hồ & phân nhánh tóm tắt phản hồi (ADMIN) |
| 11 | `test_rbac.py` | 22 | 22/22 PASS | Ma trận phân quyền Admin/Staff/Accountant/Guide/Customer; nút Sửa & form sửa tour |
| 12 | `test_tour_retrieval.py` | 5 | 5/5 PASS | Parameterized SQL, lọc tour còn chỗ và alternatives |

---

## 3. Đánh giá tính tuân thủ các quy tắc cốt lõi

### 3.1 Quy tắc Phòng Chống Đặt Vượt Chỗ (Overbooking Prevention)
- Khi lịch khởi hành có `available_seats = 15`, khách đặt 3 chỗ -> `available_seats` giảm còn đúng 12 chỗ.
- Khách đặt vượt quá số chỗ còn lại -> Hệ thống ném ngoại lệ `OverbookingError` và rollback giao dịch CSDL ngay lập tức.
- Khi đơn đặt chỗ bị hủy -> Số chỗ được cộng trả chính xác về lịch trình tương ứng.
- Khi sửa lịch khởi hành, số chỗ còn lại được tính lại từ booking chưa hủy; payload client không thể ghi đè số ghế đã giữ và không thể giảm tổng ghế thấp hơn số đã giữ.
- **Đánh giá: ĐẠT 100%.**

### 3.2 Quy tắc Không Bịa Đặt Dữ Liệu (Zero Hallucination Policy)
- Khi khách hỏi tour với mức giá không tưởng (ví dụ: "Dưới 100 nghìn"), Tour Retriever trả về danh sách rỗng `[]`.
- Context Builder sinh thông báo rỗng.
- Chatbot API trả về thông báo lịch sự rằng không tìm thấy tour phù hợp, tuyệt đối không bịa ra tour hay mức giá giả.
- Các câu hỏi mơ hồ chỉ nhận tour đang mở bán/còn chỗ; câu "Tầm 5 triệu thì đi đâu?" chỉ trả tour không vượt ngân sách đã bóc tách.
- **Đánh giá: ĐẠT 100%.**

### 3.3 Phân Hệ Kế Toán & Tài Chính (Accounting Module)
- **Đối soát thanh toán:** Kế toán xác nhận giao dịch chuyển khoản PENDING → SUCCESS, đơn tour tự động CONFIRMED. Xác nhận lại giao dịch đã duyệt bị từ chối đúng.
- **Công nợ khách hàng:** Tính đúng `Debt = Total Amount - Paid Amount`. Thanh toán vượt quá nợ còn lại bị từ chối.
- **Chi phí vận hành:** Validate hạng mục chi phí, số tiền > 0, tiêu đề không rỗng, schedule tồn tại. Ghi nhận thành công.
- **Báo cáo P&L:** Tính đúng `Gross Profit = Revenue - Expenses`, `Margin % = (Gross Profit / Revenue) × 100`.
- **Hoàn tiền hủy tour:** Áp dụng chính sách 3 mốc (90% / 50% / 0%). Hoàn vượt tiền đã trả bị từ chối.
- **Sổ quỹ dòng tiền:** Tổng hợp đúng `Net Cash = Total Inflow - Total Outflow`.
- **RBAC:** Anonymous → redirect login. CUSTOMER/GUIDE → redirect denied. ACCOUNTANT/ADMIN → 200 OK.
- **Đánh giá: ĐẠT 100%.**

### 3.4 Phân Nhánh Tổng Hợp Phản Hồi Khách Hàng Trên Trợ Lý AI (ADMIN)
- Câu hỏi dạng *"Tóm tắt phản hồi khách hàng"* (động từ tóm tắt + danh từ phản hồi) được nhận diện và **không** bị trả lời bằng nội dung tư vấn/giới thiệu tour.
- `ADMIN` nhận **Báo cáo tổng hợp phản hồi** dựng từ dữ liệu thật trong bảng `feedbacks`: số lượng phản hồi, điểm trung bình sao và 3 mục phân tích (Khen ngợi / Cần cải thiện / Đề xuất hành động); trường `tours` trả về rỗng.
- Người dùng không phải `ADMIN` chỉ nhận thông báo lịch sự rằng chức năng dành cho Quản trị viên — không rò rỉ nội dung phản hồi và không bị trả lời lạc hướng bằng giới thiệu tour.
- Khi Gemini không khả dụng, báo cáo dùng bản tổng hợp luật theo thang điểm sao — hệ thống không bao giờ trả về câu trả lời rỗng hoặc thông tin bịa đặt.
- **Đánh giá: ĐẠT 100%.**
